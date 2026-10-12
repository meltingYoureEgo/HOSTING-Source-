# 🤖 DarkBits Hosting Bot

Production-ready Telegram script hosting platform with mandatory channel verification, owner approval workflow, user management, and 24/7 systemd deployment.

## ✨ Features

- **Force-Join System** — Mandatory channel membership, live API checks, 2 warnings then permanent ban
- **Script Hosting** — Upload `.py` / `.js` / `.zip`, owner approval, auto-install missing deps
- **User Management** — Full panel: All / Active / Banned / Subscribed, ban/unban/remove, view + download files
- **Bot Configuration** — Owner transfer, contact/support username edit, admin management
- **24/7 Deployment** — Systemd service, auto-restart on crash, auto-start on VPS reboot

## 📋 Requirements

- Ubuntu 20.04+ / Debian 11+
- Python 3.10+
- 512 MB RAM minimum
- Telegram bot token from @BotFather
- Bot must be **admin** in force-join channels

## 🚀 Installation

```bash
git clone https://github.com/meltingYoureEgo/HOSTING-Source.git
cd HOSTING-Source

sudo apt update
sudo apt install -y python3 python3-pip python3-venv

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
