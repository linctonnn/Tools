# WhatsApp Spammer Tool 🔥

A Python-based automation tool for sending multiple WhatsApp messages using Selenium.

![WhatsApp Logo](https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg){: width="100" height="100"}

## 📌 Disclaimer

**This tool is for educational purposes only.** Misuse of this tool may violate WhatsApp's Terms of Service. Use at your own risk.

## 🌟 Features

- Send multiple messages to any WhatsApp contact/group
- Customizable message list
- Adjustable delay between messages
- Simple QR-code based authentication
- Cross-platform support

## ⚙️ Prerequisites

- Python 3.7+
- Chrome/Firefox browser
- WhatsApp Web account

## 🛠️ Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/whatsapp-spammer.git
   cd whatsapp-spammer
   ```

2. Install dependencies:
   ```bash
   pip install selenium webdriver-manager
   ```

## 🚀 Usage

1. Run the script:

   ```bash
   python whatsapp_spammer.py
   ```

2. When prompted, enter:

   - Contact/group name exactly as it appears in WhatsApp
   - Number of messages to send

3. Scan the QR code when WhatsApp Web appears

4. Watch the magic happen! ✨

## ⚡ Customization

Edit the `messages` list in the script to change the message content:

```python
messages = [
    "Custom message 1",
    "Custom message 2",
    # Add more messages here
]
```

Adjust the sending speed by modifying the delay:

```python
time.sleep(0.5)  # Change this value
```

## 🛡️ Safety Tips

1. Don't send more than 10-15 messages per minute
2. Avoid using for spam
3. Test with your own number first
4. Use a secondary WhatsApp account for testing

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

## 📜 License

[MIT](https://choosealicense.com/licenses/mit/)

## **⚠️ Important:** WhatsApp may temporarily ban accounts that send too many messages too quickly. Use responsibly!
