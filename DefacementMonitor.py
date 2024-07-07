from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_apscheduler import APScheduler
import requests
from bs4 import BeautifulSoup
import hashlib
import os
import json
import difflib
from selenium import webdriver
from PIL import Image, ImageChops
import io
from datetime import datetime
from time import sleep

app = Flask(__name__)
app.secret_key = 'supersecretkey'
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Global variables
PUSHOVER_USER_KEY = ''
PUSHOVER_API_TOKEN = ''
urls = []
custom_message = ''
ignore_patterns = []
change_threshold = 0.05
previous_hashes = {}
previous_contents = {}
previous_screenshots = {}
last_checks = {}
config_file = 'config.json'
last_checks_file = 'last_checks.json'

def send_pushover_notification(message):
    if custom_message:
        message = f"{custom_message}\n\n{message}"
    payload = {
        'token': PUSHOVER_API_TOKEN,
        'user': PUSHOVER_USER_KEY,
        'message': message
    }
    response = requests.post('https://api.pushover.net/1/messages.json', data=payload)
    return response

def get_page_content(url):
    response = requests.get(url)
    return response.text

def get_page_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def get_detailed_changes(old_content, new_content):
    differ = difflib.Differ()
    diff = list(differ.compare(old_content.splitlines(), new_content.splitlines()))
    return "\n".join(diff)

def take_screenshot(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    screenshot = driver.get_screenshot_as_png()
    driver.quit()
    return Image.open(io.BytesIO(screenshot))

def compare_screenshots(old_screenshot, new_screenshot):
    diff = ImageChops.difference(old_screenshot, new_screenshot)
    return diff.getbbox() is not None

def is_significant_change(old_content, new_content):
    for pattern in ignore_patterns:
        if pattern in old_content or pattern in new_content:
            return False
    diff_ratio = difflib.SequenceMatcher(None, old_content, new_content).ratio()
    return (1 - diff_ratio) > change_threshold

def load_last_checks():
    global last_checks
    if os.path.exists(last_checks_file):
        with open(last_checks_file, 'r') as f:
            last_checks = json.load(f)
    else:
        last_checks = {}

def save_last_checks():
    with open(last_checks_file, 'w') as f:
        json.dump(last_checks, f)

def check_for_changes():
    for url in urls:
        new_content = get_page_content(url)
        new_hash = get_page_hash(new_content)
        new_screenshot = take_screenshot(url)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_checks[url] = current_time
        save_last_checks()
        
        report_filename = f"reports/report_{url.replace('://', '_').replace('/', '_')}.txt"
        
        if url not in previous_hashes:
            previous_hashes[url] = new_hash
            previous_contents[url] = new_content
            previous_screenshots[url] = new_screenshot
            new_screenshot.save(f"screenshots/initial_{url.replace('://', '_').replace('/', '_')}.png")
            
            with open(report_filename, "w") as f:
                f.write(f"Initial check for {url} at {current_time}\n")
                f.write("No previous content to compare.\n\n")
            
            continue
        
        with open(report_filename, "a") as f:  # Changed to append mode
            f.write(f"\nCheck performed for {url} at {current_time}\n")
            
            if new_hash != previous_hashes[url] and is_significant_change(previous_contents[url], new_content):
                changes = get_detailed_changes(previous_contents[url], new_content)
                f.write("Changes detected:\n")
                f.write(changes)
                f.write("\n")
                
                if compare_screenshots(previous_screenshots[url], new_screenshot):
                    screenshot_filename = f"screenshots/changed_{url.replace('://', '_').replace('/', '_')}.png"
                    new_screenshot.save(screenshot_filename)
                    send_pushover_notification(f"Changes detected on {url}. Report: {report_filename}, Screenshot: {screenshot_filename}")
                else:
                    send_pushover_notification(f"Changes detected on {url}. Report: {report_filename}")
            else:
                f.write("No significant changes detected.\n\n")
        
        previous_hashes[url] = new_hash
        previous_contents[url] = new_content
        previous_screenshots[url] = new_screenshot

def load_config():
    global PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN, urls, custom_message, ignore_patterns, change_threshold
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)
            PUSHOVER_USER_KEY = config.get('user_key', '')
            PUSHOVER_API_TOKEN = config.get('api_token', '')
            urls = config.get('urls', [])
            custom_message = config.get('custom_message', '')
            ignore_patterns = config.get('ignore_patterns', [])
            change_threshold = config.get('change_threshold', 0.05)

def save_config():
    config = {
        'user_key': PUSHOVER_USER_KEY,
        'api_token': PUSHOVER_API_TOKEN,
        'urls': urls,
        'custom_message': custom_message,
        'ignore_patterns': ignore_patterns,
        'change_threshold': change_threshold
    }
    with open(config_file, 'w') as file:
        json.dump(config, file)

@app.route('/', methods=['GET', 'POST'])
def index():
    global PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN, urls, custom_message, ignore_patterns, change_threshold
    
    if request.method == 'POST':
        PUSHOVER_USER_KEY = request.form['user_key']
        PUSHOVER_API_TOKEN = request.form['api_token']
        urls = [url.strip() for url in request.form['urls'].split(',')]
        custom_message = request.form['custom_message']
        ignore_patterns = request.form.getlist('ignore_patterns')
        change_threshold = float(request.form['change_threshold']) / 100
        
        if 'save_config' in request.form:
            save_config()
            flash('Configuration saved!', 'success')
        else:
            flash('Configuration updated but not saved!', 'info')
    
    return render_template('index.html', 
                           user_key=PUSHOVER_USER_KEY, 
                           api_token=PUSHOVER_API_TOKEN, 
                           urls=','.join(urls),
                           custom_message=custom_message,
                           ignore_patterns=ignore_patterns,
                           change_threshold=int(change_threshold * 100))

@app.route('/start', methods=['POST'])
def start_monitoring():
    interval = int(request.form['interval'])
    schedule = request.form['schedule']
    
    if schedule:
        scheduler.add_job(id='MonitorJob', func=check_for_changes, trigger='cron', **cron_to_dict(schedule))
    else:
        scheduler.add_job(id='MonitorJob', func=check_for_changes, trigger='interval', minutes=interval)
    
    # Run the job once immediately
    scheduler.add_job(id='ImmediateCheck', func=check_for_changes, trigger='date', run_date=datetime.now())
    
    flash('Monitoring started!', 'success')
    # Add a small delay to allow the first check to complete
    sleep(2)
    return redirect(url_for('dashboard'))

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

@app.route('/dashboard')
def dashboard():
    global urls, last_checks
    job_status = scheduler.get_job('MonitorJob') is not None
    load_last_checks()  # Load the latest last_checks data
    return render_template('dashboard.html', urls=urls, job_status=job_status, last_checks=last_checks)

@app.route('/download_report/<path:url>')
def download_report(url):
    filename = f"report_{url.replace('://', '_').replace('/', '_')}.txt"
    report_path = os.path.join('reports', filename)
    
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    if not os.path.isfile(report_path):
        # Create a report file if it doesn't exist
        with open(report_path, 'w') as f:
            f.write(f"No checks have been performed yet for {url}\n")
            f.write(f"Last known check time: {last_checks.get(url, 'Never')}\n")
            f.write(f"Current monitoring status: {'Active' if scheduler.get_job('MonitorJob') else 'Inactive'}\n")
    
    return send_file(report_path, as_attachment=True)

@app.route('/clear_list')
def clear_list():
    global urls, last_checks
    urls = []
    last_checks = {}
    flash('Monitored URLs and reports have been cleared.', 'success')
    return redirect(url_for('dashboard'))

def cron_to_dict(cron_string):
    minute, hour, day, month, day_of_week = cron_string.split()
    return {
        'minute': minute,
        'hour': hour,
        'day': day,
        'month': month,
        'day_of_week': day_of_week
    }

if __name__ == '__main__':
    load_config()
    load_last_checks()
    if not os.path.exists('reports'):
        os.makedirs('reports')
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')
    app.run(debug=True)
