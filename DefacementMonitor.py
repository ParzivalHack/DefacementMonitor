from flask import Flask, render_template, request, redirect, url_for, flash
from flask_apscheduler import APScheduler
import requests
from bs4 import BeautifulSoup
import hashlib
import os
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Global variables for Pushover
PUSHOVER_USER_KEY = ''
PUSHOVER_API_TOKEN = ''
url = ''
hash_file = 'page_hash.txt'
config_file = 'config.json'

# Function to send notifications via Pushover
def send_pushover_notification(message):
    payload = {
        'token': PUSHOVER_API_TOKEN,
        'user': PUSHOVER_USER_KEY,
        'message': message
    }
    response = requests.post('https://api.pushover.net/1/messages.json', data=payload)
    return response

# Function to get the hash of the page content
def get_page_hash(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    page_content = soup.get_text()
    return hashlib.sha256(page_content.encode('utf-8')).hexdigest()

# Function to check for changes
def check_for_changes():
    global previous_hash
    current_hash = get_page_hash(url)

    if current_hash != previous_hash:
        send_pushover_notification(f'⚠️ALERT: The content of the page {url} has changed! Possible Defacement Detected!')
        with open(hash_file, 'w') as file:
            file.write(current_hash)
        previous_hash = current_hash

# Load configuration if it exists
def load_config():
    global PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)
            PUSHOVER_USER_KEY = config.get('user_key', '')
            PUSHOVER_API_TOKEN = config.get('api_token', '')

@app.route('/', methods=['GET', 'POST'])
def index():
    global url, PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN

    if request.method == 'POST':
        url = request.form['url']
        PUSHOVER_USER_KEY = request.form['user_key']
        PUSHOVER_API_TOKEN = request.form['api_token']
        save_config = 'save_config' in request.form

        if save_config:
            with open(config_file, 'w') as file:
                json.dump({'user_key': PUSHOVER_USER_KEY, 'api_token': PUSHOVER_API_TOKEN}, file)
            flash('Configuration saved!', 'success')
        else:
            flash('Configuration updated but not saved!', 'info')

    return render_template('index.html', user_key=PUSHOVER_USER_KEY, api_token=PUSHOVER_API_TOKEN, url=url)

@app.route('/start', methods=['POST'])
def start_monitoring():
    scheduler.add_job(id='MonitorJob', func=check_for_changes, trigger='interval', minutes=10)
    flash('Monitoring started!', 'success')
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_monitoring():
    scheduler.remove_job('MonitorJob')
    flash('Monitoring stopped!', 'warning')
    return redirect(url_for('index'))

@app.route('/test', methods=['POST'])
def send_test_notification():
    title = request.form.get('title', 'Test Notification')
    message = request.form.get('message', 'This is a test notification.')
    response = send_pushover_notification(f"{title}\n\n{message}")
    if response.status_code == 200:
        flash('Test notification sent successfully!', 'success')
    else:
        flash(f'Error sending test notification: {response.text}', 'danger')
    return redirect(url_for('index'))

# Work in progress...
#@app.route('/account_info', methods=['GET'])
#def account_info():
#    response = requests.post('https://api.pushover.net/1/users/validate.json', data={
#        'token': PUSHOVER_API_TOKEN,
#        'user': PUSHOVER_USER_KEY
#    })
#    account_data = response.json()
#
#    response = requests.post('https://api.pushover.net/1/devices.json', data={
#        'token': PUSHOVER_API_TOKEN,
#        'user': PUSHOVER_USER_KEY
#    })
#    devices_data = response.json()
#
#    return render_template('account_info.html', account_data=account_data, devices_data=devices_data)

if __name__ == '__main__':
    load_config()
    app.run(debug=True)