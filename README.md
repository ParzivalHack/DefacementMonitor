# Defacement Monitor

![Defacement Monitor Logo](https://github.com/ParzivalHack/DefacementMonitor/assets/82817793/af07c4f2-045f-46d9-a5b7-5e1c88ac09de)

## 🔍 Overview

Defacement Monitor is a powerful, easy-to-use web application that helps you keep track of changes to your websites. Using the Pushover notification service, it alerts you instantly when your monitored web pages are modified, providing an extra layer of security against website defacement and unauthorized changes.

## 🌟 Features

- **Real-time Monitoring**: Regularly checks your specified URLs for changes.
- **Instant Notifications**: Sends alerts directly to your device via Pushover when changes are detected.
- **User-friendly Interface**: Simple web interface for easy configuration and management.
- **Flexible Configuration**: Set custom monitoring configurations and save them for convenience automatically.
- **Test Notifications**: Send test alerts to ensure your Pushover setup is working correctly.
- **Start/Stop Controls**: Easily activate or deactivate monitoring as needed.

## 🚀 How It Works

1. **Setup**: Enter your Pushover User Key and API Token, along with the URL you want to monitor.
2. **Monitoring**: The application periodically checks the specified URL for changes.
3. **Detection**: If a change is detected, the content's hash is updated and stored.
4. **Notification**: An instant alert is sent to your devices via Pushover.

## 🛠 Installation

1. Clone this repository:
```git clone https://github.com/yourusername/defacement-monitor.git```
3. Navigate to the project directory:
```cd DefacementMonitor```
4. Install the required dependencies:
```pip install -r requirements.txt```

## 🏃‍♂️ Usage

1. Run the Flask web application:
* Linux:
```python DefacementMonitor.py```
* Windows:
Download and double-click on the RunWindows.bat (or just right-click execute on the file)
2. Open your web browser and go to `http://127.0.0.1:5000` (localhost:5000).
3. Enter your Pushover User Key and API Token and the URL you want to monitor.
4. Click "Save" & "Start Monitoring" to begin.
5. If you need help with the setup, you can click on the blue "?" at the top right corner of the page to get the initial instructions on hwo to get started :)

## ⚠️ Alert Example
![Alert Example](https://github.com/ParzivalHack/DefacementMonitor/assets/82817793/c9e2bd4c-d7a1-4ff4-a551-af214464bfd7)


## 📋 Requirements

- Python 3.6+ is suggested (Python 3.0 is mandatory)
- Flask
- Flask-APScheduler
- Requests
- BeautifulSoup4
- A free Pushover account

## 🔨 To-Do (soon)

1. Allow users to set custom time intervals for checking the website (right now is defaulted to 10 mins).
2. Allow to monitor multiple websites at once.

## 🔒 Security Note

Always ensure you're using this tool on websites you own or have permission to monitor. Unauthorized monitoring of websites may be illegal in some jurisdictions. User discretion is advised. The creator of this tool takes no responsibility in unauthorized monitoring activities or any potential damage related to its use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://github.com/ParzivalHack/DefacementMonitor/issues).

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Contact

Feel free to connect with me :) 
[Linkedin](https://www.linkedin.com/in/tommaso-bona-20b76b232/)
[Email](mailto:tommasobona04@gmail.com)
