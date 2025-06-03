# WiPhi 🔓📶 – WiFi Phishing Access Point Tool

WiPhi is an educational tool designed to simulate a rogue WiFi Access Point (AP) that mimics legitimate networks in order to demonstrate how phishing attacks can occur in insecure environments. When a user connects to this fake AP, they are served a fake login page, and any credentials they enter are captured and logged.

---

## ⚠️ WARNING!

> **This tool is intended for educational and ethical penetration testing purposes ONLY.**

Using WiPhi on unauthorized networks or devices is **illegal and unethical**. The purpose of this tool is to:
- Raise awareness about WiFi-based social engineering attacks.
- Help ethical hackers test captive portal vulnerabilities in controlled lab environments.
- Educate users about the importance of avoiding public, unsecured WiFi.

**You are fully responsible for any misuse of this tool. The developer is not liable for any consequences arising from its misuse!**

---

## 🛠 Features

- Launches a rogue WiFi Access Point with custom SSID and optional WPA2/WPA3 password.
- Captive portal phishing page served via Flask backend.
- Auto-redirects OS captive portal detection to phishing page.
- Captures and logs credentials submitted by the victim.
- Clean shutdown and environment restoration.

---

## 🧰 Requirements

- Linux machine (Kali Linux recommended, **will not work in Windows**)
- **Root privileges** (must be run with `sudo`)
- Wireless card that supports **AP (Access Point) mode**
- Python 3
- Dependencies:
  - `Flask`
  - `waitress`
  - `hostapd`
  - `dnsmasq`

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Ensure `hostapd` and `dnsmasq` are installed:
```bash
sudo apt install hostapd dnsmasq
```

---

## 🧠 How It Works

1. **WiPhi (`wiphi.py`)** sets up a fake Access Point using:
   - `hostapd`: to broadcast the WiFi signal.
   - `dnsmasq`: for DHCP and DNS redirection.

2. Network redirection forces connected devices to see a login page.

3. A Flask server (`server.py`) serves:
   - `index.html` (login page)
   - `redirect.html` (fake success page after login)

4. User credentials submitted via the login form are stored in `credentials.txt`.

5. All connections and disconnections are logged with MAC addresses.

6. Graceful shutdown restores original network settings and stops processes.

---

## 🚀 Usage

Run as root:

```bash
sudo python3 wiphi.py --ssid "Free Airport WiFi" --inter wlan0 --ch 6 --password "free1234" --mh 30
```

### Options:

| Option       | Description                                      | Default           |
|--------------|--------------------------------------------------|-------------------|
| `--ssid`     | SSID shown to victim                             | "WiPhi Tool"      |
| `--inter`    | WiFi interface name (e.g., `wlan0`)              | "wlan0"           |
| `--ch`       | Channel to broadcast                             | 5                 |
| `--password` | WPA2/WPA3 passphrase (optional)                  | None              |
| `--mh`       | Max allowed connected clients                    | 20                |

🛑 To stop the tool, press `Ctrl + C` and it will cleanly shut everything down.

---

## 📁 Folder Structure

```
.
├── wiphi.py               # Main script that starts AP and phishing system
├── server.py             # Flask server for captive portal
├── web/
│   ├── index.html        # Login page shown to victims
│   └── redirect.html     # Redirect page after submission
├── configs/
│   ├── hostapd.conf      # Auto-generated hostapd config
│   └── dnsmasq.conf      # Auto-generated dnsmasq config
└── credentials.txt       # Captured credentials are stored here
```

---
## ⚠️ Known Issues / Limitations

- Debugged and tested using Android Phones only.
- Not compatible with Windows OS.
- Won't work without root permissions.
- Requires a WiFi adapter that supports **Access Point mode** (`iw list` to verify).
- Modern devices with HSTS/HTTPS-first may flag the phishing page or not show it properly unless forced HTTP is used.

---
## 🙏 Ethical Reminder

Use WiPhi only in:
- Legal environments (labs, your own devices/networks)
- Penetration testing scenarios with **explicit permission**
- Training and awareness demonstrations

This project is a **learning aid**, not a hacking tool. Let's build a safer digital world by understanding how attackers work.


---

## 📄 License

This project is released under the [MIT License](LICENSE).
Do whatever you want, but be legal and ethical!

---
