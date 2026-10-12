<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=240&section=header&text=DarkBits%20Hosting%20Bot&fontSize=68&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Production-Ready%20Telegram%20Script%20Hosting%20Platform&descAlignY=58&descSize=18" width="100%"/>

<a href="https://t.me/meltingYoureEgo">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=22&duration=2500&pause=600&color=22C55E&center=true&vCenter=true&multiline=true&width=900&height=80&lines=Telegram+Bot+%E2%80%A2+Script+Hosting+%E2%80%A2+Force+Join;Python+%E2%80%A2+Flask+%E2%80%A2+SQLite+%E2%80%A2+Systemd;Owner+Approval+%E2%80%A2+User+Management+%E2%80%A2+24%2F7" alt="Typing SVG" />
</a>

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://ubuntu.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/meltingYoureEgo)
[![Status](https://img.shields.io/badge/Status-Active-22C55E?style=for-the-badge&logo=statuspage&logoColor=white)]()
[![Stars](https://img.shields.io/github/stars/meltingYoureEgo/HOSTING-Source-?style=for-the-badge&logo=github&color=FFD700)](https://github.com/meltingYoureEgo/HOSTING-Source-/stargazers)
[![Forks](https://img.shields.io/github/forks/meltingYoureEgo/HOSTING-Source-?style=for-the-badge&logo=github&color=8B5CF6)](https://github.com/meltingYoureEgo/HOSTING-Source-/network/members)

<br/>

[📖 Overview](#-overview) · [✨ Features](#-features) · [📋 Requirements](#-requirements) · [🚀 Installation](#-installation) · [🔧 Management](#-management-commands) · [📁 Structure](#-project-structure) · [🎯 Commands](#-bot-commands) · [🔒 Force-Join](#-force-join-flow) · [🐛 Troubleshooting](#-troubleshooting)

</div>

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%">

---

<div align="center">

## 📖 Overview

> **DarkBits Hosting Bot** — a production-grade Telegram bot that turns any VPS into a multi-tenant script hosting platform.

> Every user is verified through mandatory channel membership, every upload requires owner approval, and every script runs in an isolated folder under `psutil` supervision.

> Powered by **pyTelegramBotAPI**, **Flask**, **SQLite**, and **systemd** — built for zero-touch uptime.

</div>

<br/>

<table>
<tr>
<td align="center" width="25%">
<img src="https://img.icons8.com/fluency/96/security-shield-green.png" width="48"/>
<br/><b>Force Join</b>
<br/><sub>Mandatory channel gate</sub>
</td>
<td align="center" width="25%">
<img src="https://img.icons8.com/fluency/96/upload.png" width="48"/>
<br/><b>Script Hosting</b>
<br/><sub>Isolated execution</sub>
</td>
<td align="center" width="25%">
<img src="https://img.icons8.com/fluency/96/user-shield.png" width="48"/>
<br/><b>User Mgmt</b>
<br/><sub>Ban · Unban · Manage</sub>
</td>
<td align="center" width="25%">
<img src="https://img.icons8.com/fluency/96/server.png" width="48"/>
<br/><b>24/7 Uptime</b>
<br/><sub>Auto-restart systemd</sub>
</td>
</tr>
</table>

---

<div align="center">

## ✨ Features

</div>

<br/>

<table>
<tr><th align="center" width="30%">Feature</th><th>Description</th></tr>
<tr>
<td align="center">🛡️ <b>Force-Join System</b></td>
<td>

- Mandatory channel membership verification
- Live API checks — no cached bypass
- 2 warnings on channel leave events
- 3rd leave = permanent ban (persisted in SQLite)
- Unban auto-resets warnings
- Owner / Admin bypass

</td>
</tr>
<tr>
<td align="center">📤 <b>Script Hosting</b></td>
<td>

- Upload `.py` · `.js` · `.zip` scripts
- Owner approval required before execution
- Auto-install missing Python dependencies
- Isolated user folders
- Process monitoring via `psutil`

</td>
</tr>
<tr>
<td align="center">👥 <b>User Management</b></td>
<td>

- Full panel with live statistics
- Sections: All · Active · Banned · Subscribed
- Detailed user cards (ID, name, subscription, files)
- Ban / Unban / Remove from panel
- View + download user files

</td>
</tr>
<tr>
<td align="center">⚙️ <b>Bot Configuration</b></td>
<td>

- Persistent settings in SQLite
- Owner transfer with confirmation
- Contact / Support usernames editable in-bot
- Admin management (add / remove / self-leave)

</td>
</tr>
<tr>
<td align="center">🚀 <b>24/7 Deployment</b></td>
<td>

- Systemd service included
- Auto-restart on crash (10s delay)
- Auto-start on VPS reboot
- Flask keep-alive for uptime monitors

</td>
</tr>
</table>

---

<div align="center">

## 📋 Requirements

</div>

<br/>

<table>
<tr><th>Component</th><th>Minimum</th><th>Recommended</th></tr>
<tr><td>🖥️ Operating System</td><td>Ubuntu 20.04 LTS</td><td>Ubuntu 22.04 LTS</td></tr>
<tr><td>🐍 Python</td><td>3.10</td><td>3.11+</td></tr>
<tr><td>🧠 RAM</td><td>512 MB</td><td>1 GB+</td></tr>
<tr><td>💾 Disk</td><td>1 GB</td><td>5 GB+</td></tr>
<tr><td>🤖 Bot Token</td><td colspan="2"><a href="https://t.me/BotFather">@BotFather</a></td></tr>
<tr><td>📢 Channel Admin</td><td colspan="2">Bot must be admin in force-join channels</td></tr>
</table>

---

<div align="center">

## 🚀 Installation

</div>

<br/>

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/meltingYoureEgo/HOSTING-Source-.git
cd HOSTING-Source-
2️⃣ Install System Dependencies
bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
3️⃣ Create Virtual Environment
bash
python3 -m venv venv
source venv/bin/activate
4️⃣ Install Python Dependencies
bash
pip install --upgrade pip
pip install -r requirements.txt
5️⃣ Configure the Bot
Edit HOSTABHI.py:

python
TOKEN           = "YOUR_BOT_TOKEN"
OWNER_ID        = 123456789
ADMIN_ID        = 123456789
YOUR_USERNAME   = 'meltingYoureEgo'
UPDATE_CHANNEL  = 'https://t.me/meltingYoureEgo'
Edit force_join_patch.py:

python
CHANNELS = [
    ("@your_channel_1",  "Channel One"),
    ("@your_channel_2",  "Channel Two"),
]
6️⃣ First Test Run
bash
python3 HOSTABHI.py
Expected output:

text
[CFG] Initialized (3 keys)
[FJ] ✅ bot admin in @your_channel_1
[FJ] ✅ bot admin in @your_channel_2
[UM] User Management installed
Flask Keep-Alive server started.
Press Ctrl+C multiple times to stop.

7️⃣ Setup 24/7 Systemd Service
bash
sudo nano /etc/systemd/system/hostabhi.service
Paste the contents of hostabhi.service (adjust user / paths):

ini
[Unit]
Description=DarkBits Hosting Bot
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/tgposter
ExecStart=/home/YOUR_USERNAME/tgposter/venv/bin/python3 /home/YOUR_USERNAME/tgposter/HOSTABHI.py
Restart=always
RestartSec=10
KillSignal=SIGTERM
TimeoutStopSec=20
StandardOutput=append:/home/YOUR_USERNAME/tgposter/hostabhi.log
StandardError=append:/home/YOUR_USERNAME/tgposter/hostabhi.log
Environment=PORT=8080
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
Enable and start:

bash
sudo systemctl daemon-reload
sudo systemctl enable hostabhi
sudo systemctl start hostabhi
sudo systemctl status hostabhi
<div align="center">
🔧 Management Commands
</div>
Action	Command
🟢 Check Status	sudo systemctl status hostabhi
🔄 Restart Bot	sudo systemctl restart hostabhi
🛑 Stop Bot	sudo systemctl stop hostabhi
▶️ Start Bot	sudo systemctl start hostabhi
📜 Live Logs	sudo journalctl -u hostabhi -f
📄 Last 50 Lines	sudo journalctl -u hostabhi -n 50 --no-pager
🧹 Clear Log File	> /home/USER/tgposter/hostabhi.log
⬆️ Update & Restart	cd ~/tgposter && git pull && sudo systemctl restart hostabhi
<div align="center">
📁 Project Structure
</div>
plaintext
HOSTING-Source-/
│
├── 🐍 HOSTABHI.py              # Main bot entry point
├── 🛡️ force_join_patch.py      # Mandatory channel membership gate
├── 👥 user_manager.py          # User management panel
├── 📤 upload_approval.py       # Owner approval workflow for uploads
├── ⚙️ bot_config.py            # Persistent settings + admin UI
│
├── 📦 requirements.txt         # Python dependencies
├── 🔁 hostabhi.service         # Systemd unit file
├── 🌐 .env.example             # Environment template
├── 🚫 .gitignore               # Git ignore rules
├── 📜 LICENSE                  # MIT License
└── 📖 README.md                # This file
Runtime directories (auto-created, gitignored):

Path	Purpose
inf/	SQLite database & system data
upload_bots/	User-uploaded scripts
clones/ · clones2/	Cloned bot instances
hostabhi.log	Runtime log file
<div align="center">
🎯 Bot Commands
</div>
👤 User Commands
Command	Description
/start	Open main menu
/help	Show all commands
/uploadfile	Upload a script
/checkfiles	View your files
/contactowner	Contact bot owner
/botspeed	Check bot response speed
👑 Owner / Admin Commands
Command	Description
/adminpanel	Open admin panel
/broadcast	Broadcast to all users
/lockbot	Lock / unlock bot
/stats	View statistics
/runningallcode	Start all user scripts
/ban <user_id>	Ban a user
/unban <user_id>	Unban a user
<div align="center">
🔒 Force-Join Flow
</div>
Situation	Action
New user sends /start	Force-join prompt with buttons
User joined + Verify	✅ Access granted
User leaves a channel	⚠️ Warning 1 issued
User rejoins then leaves again	⚠️ Warning 2 (final)
User leaves a 3rd time	🚫 Permanent ban
Owner / Admin	⚡ Bypass
💡 Unbanning via Admin Panel auto-resets warnings so the user starts fresh.

<div align="center">
📄 Source Code
</div>
<details> <summary><b>📦 &nbsp; requirements.txt</b></summary>
txt
pyTelegramBotAPI>=4.20.0
flask>=3.0.0
psutil>=5.9.0
requests>=2.31.0
</details><details> <summary><b>🌐 &nbsp; .env.example</b></summary>
env
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
OWNER_ID=YOUR_TELEGRAM_ID
ADMIN_ID=YOUR_TELEGRAM_ID
YOUR_USERNAME=meltingYoureEgo
UPDATE_CHANNEL=https://t.me/meltingYoureEgo
</details><details> <summary><b>🚫 &nbsp; .gitignore</b></summary>
gitignore
__pycache__/
*.py[cod]
venv/
env/
*.db
*.sqlite
*.sqlite3
inf/
upload_bots/
clones/
clones2/
*.log
.env
.DS_Store
Thumbs.db
*.bak*
*~
</details><details> <summary><b>🔁 &nbsp; hostabhi.service</b></summary>
ini
[Unit]
Description=DarkBits Hosting Bot
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/tgposter
ExecStart=/home/YOUR_USERNAME/tgposter/venv/bin/python3 /home/YOUR_USERNAME/tgposter/HOSTABHI.py
Restart=always
RestartSec=10
KillSignal=SIGTERM
TimeoutStopSec=20
StandardOutput=append:/home/YOUR_USERNAME/tgposter/hostabhi.log
StandardError=append:/home/YOUR_USERNAME/tgposter/hostabhi.log
Environment=PORT=8080
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
</details><details> <summary><b>🐍 &nbsp; HOSTABHI.py &nbsp;<i>(main entry point)</i></b></summary>
File location: repository root
Lines: ~2700
Purpose: Main bot — polling loop, message handlers, file hosting, admin commands, clones, broadcast.

⚠️ Full source is in the repository file. Click the file in the repo tree to view it.

Config block (top of file):

python
TOKEN           = "YOUR_BOT_TOKEN"          # From @BotFather
OWNER_ID        = 123456789                 # Your Telegram user ID
ADMIN_ID        = 123456789                 # Admin ID (can be same)
YOUR_USERNAME   = 'meltingYoureEgo'         # Without @
UPDATE_CHANNEL  = 'https://t.me/meltingYoureEgo'
Setup order (bottom of file):

python
# ─── FORCE JOIN GATE ───
try:
    from force_join_patch import install_fj
    _admin_ids = {ADMIN_ID, OWNER_ID}
    install_fj(bot, OWNER_ID, _admin_ids, owner_username=YOUR_USERNAME)
except Exception as _fj_e:
    print(f"[FORCE-JOIN] ❌ Failed: {_fj_e}")

# ─── BOT CONFIG (persistent settings) ───
try:
    import bot_config as _bc
    _bc.init_config({...})
    _bc.register_handlers(bot, lambda uid: uid == OWNER_ID)
except Exception as _cfg_e:
    print(f"[CFG] ❌ Failed: {_cfg_e}")

# ─── UPLOAD APPROVAL GATE ───
try:
    import upload_approval
    upload_approval.register_handlers(bot, OWNER_ID)
except Exception as _ap_e:
    print(f"[APPROVAL] Failed: {_ap_e}")

# ─── USER MANAGEMENT PANEL ───
try:
    import user_manager
    user_manager.register(bot, lambda uid: uid == OWNER_ID or uid in admin_ids or uid == ADMIN_ID)
except Exception as _um_e:
    print(f"[UM] ❌ Failed: {_um_e}")
</details><details> <summary><b>🛡️ &nbsp; force_join_patch.py</b></summary>
Purpose: Mandatory channel membership gate — 2 warnings + 3rd = permanent ban.
Install via: install_fj(bot, owner_id, admin_ids, owner_username=None)

Key structures:

python
CHANNELS = [
    ("@meltingYoureEgo",  "Melting Ego"),
    ("@meltingYoureEgoo", "Melting Egoo"),
]
Behaviour:

Fresh check on every /start

Warnings tracked per-user in memory + banned list in SQLite

Unban auto-detects DB and resets warnings

</details><details> <summary><b>👥 &nbsp; user_manager.py</b></summary>
Purpose: Full user administration panel.
Install via: user_manager.register(bot, is_admin_fn)

Menus: All Users · Active · Banned · Subscribed · Statistics · Search

User actions: Ban · Unban · Remove · View Files · Subscription

File actions: View details · Download to chat

</details><details> <summary><b>📤 &nbsp; upload_approval.py</b></summary>
Purpose: Owner approval workflow before script execution.
Install via: upload_approval.register_handlers(bot, owner_id)

Flow:

User uploads file → saved to upload_bots/{user_id}/

Owner receives approval request with Approve / Reject buttons

On Approve → script runs, user notified

On Reject → file deleted, user notified

</details><details> <summary><b>⚙️ &nbsp; bot_config.py</b></summary>
Purpose: Persistent settings + admin UI.
Install via: bot_config.init_config(defaults) + bot_config.register_handlers(bot, is_owner_fn)

Settings managed:

owner_id — transferable

contact_username — editable

support_username — editable

Admin list — add / remove / self-leave

Storage: bot_settings table in inf/bot_data.db

</details>
<div align="center">
🐛 Troubleshooting
</div>
<details> <summary><b>🔴 Bot is not responding</b></summary>
bash
sudo systemctl status hostabhi
sudo journalctl -u hostabhi -n 50 --no-pager
Check for Traceback or Error lines.

</details><details> <summary><b>⚔️ 409 Conflict — terminated by other getUpdates request</b></summary>
Duplicate bot process running:

bash
pkill -9 -f HOSTABHI.py
sleep 2
sudo systemctl restart hostabhi
</details><details> <summary><b>🚪 Force-join not working</b></summary>
Ensure the bot is administrator in every required channel:

Open channel → Administrators → Add bot

Enable Post Messages permission

</details><details> <summary><b>📦 Missing Python module in uploaded script</b></summary>
The bot auto-installs. Manual:

bash
cd ~/tgposter
source venv/bin/activate
pip install MODULE_NAME
sudo systemctl restart hostabhi
</details><details> <summary><b>♻️ Bot keeps restarting every 10 seconds</b></summary>
Something is crashing at startup:

bash
sudo journalctl -u hostabhi -n 100 --no-pager | grep -A 20 "Traceback"
</details><details> <summary><b>🔑 Authentication failed when pushing to GitHub</b></summary>
GitHub no longer accepts passwords. Create a Personal Access Token:

Go to https://github.com/settings/tokens

Generate new token (classic)

Note: HOSTING

Expiration: No expiration

Scope: repo (full)

Generate token → copy

Use the token as the password when prompted.

</details>
<div align="center">
🧪 Testing
</div>
bash
# 1. Check service is active
sudo systemctl is-active hostabhi

# 2. Check service is enabled (auto-start on boot)
sudo systemctl is-enabled hostabhi

# 3. Kill the process — systemd should restart it
sudo pkill -f HOSTABHI.py
sleep 12
sudo systemctl status hostabhi
Expected: active (running) — auto-recovery worked.

<div align="center">
🔐 Security Notes
</div>
🔒 Never commit real tokens to this repository

<ul>
<li>🌐 Use environment variables for production: <code>BOT_TOKEN</code>, <code>OWNER_ID</code></li>
<li>🕵️ Keep the repository private if you can't remove hardcoded values</li>
<li>💾 Regular backup of <code>inf/bot_data.db</code> is recommended</li>
<li>🔄 Rotate tokens every 90 days</li>
<li>🛡️ Only run this bot on a trusted VPS</li>
</ul>

<br />

---

<h2>📊 Repository Stats</h2>

<div align="center">

<img src="https://github-readme-stats.vercel.app/api?username=meltingYoureEgo&show_icons=true&theme=tokyonight&hide_border=true&bg_color=0D1117&title_color=22C55E&icon_color=22C55E&text_color=c9d1d9" height="180" />
<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=meltingYoureEgo&layout=compact&theme=tokyonight&hide_border=true&bg_color=0D1117&title_color=22C55E&text_color=c9d1d9" height="180" />

<br /><br />

<img src="https://github-readme-streak-stats.herokuapp.com/?user=meltingYoureEgo&theme=tokyonight&hide_border=true&background=0D1117&ring=22C55E&fire=22C55E&currStreakLabel=22C55E" width="48%" />

<br /><br />

<img src="https://github-profile-trophy.vercel.app/?username=meltingYoureEgo&theme=tokyonight&no-frame=true&no-bg=true&column=7&margin-w=10" width="90%" />

</div>

<br />

---

<h2>📝 License</h2>

<div align="center">

<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge&logo=opensourceinitiative&logoColor=white" /></a>

<br /><br />

<p>This project is licensed under the <b>MIT License</b> — see the <a href="LICENSE">LICENSE</a> file for details.</p>

</div>

<br />

---

<h2>👤 Author</h2>

<div align="center">

<img src="https://avatars.githubusercontent.com/meltingYoureEgo" width="120" style="border-radius:50%" />

<h3>meltingYoureEgo</h3>

<p><i>Software Developer · Cybersecurity Enthusiast · Security Researcher</i></p>

<a href="https://github.com/meltingYoureEgo"><img src="https://img.shields.io/badge/GitHub-@meltingYoureEgo-181717?style=for-the-badge&logo=github&logoColor=white" /></a>
<a href="https://t.me/meltingYoureEgo"><img src="https://img.shields.io/badge/Telegram-@meltingYoureEgo-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" /></a>

</div>

<br />

---

<h2>⭐ Support</h2>

<div align="center">

<p>If this project helped you, please consider giving it a <b>star</b>.</p>

<p>It means a lot and helps others find this project.</p>

<br />

<a href="https://github.com/meltingYoureEgo/HOSTING-Source-/stargazers"><img src="https://img.shields.io/badge/Star_this_repo-FFD700?style=for-the-badge" /></a>
<a href="https://github.com/meltingYoureEgo/HOSTING-Source-/fork"><img src="https://img.shields.io/badge/Fork_this_repo-8B5CF6?style=for-the-badge" /></a>

</div>

<br />

<img src="https://user-images.githubusercontent.com/74038190/212284115-f47cd8ff-2ffb-4b04-b5bf-4d1c14c0247f.gif" width="100%" />

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=140&section=footer&text=Made%20with%20%E2%9D%A4%EF%B8%8F%20by%20meltingYoureEgo&fontSize=22&fontColor=ffffff&animation=twinkling&fontAlignY=70" width="100%" />

<b>Built with ❤️ using pyTelegramBotAPI · Flask · SQLite · Systemd</b>

</div>
