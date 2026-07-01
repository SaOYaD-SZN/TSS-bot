# ✨ ᏖᏕᏕ — Your All-in-One Cutie Discord Bot 🎀

<p align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3VhNjN0NW9mNWQwM3Q5dWx6eWV1djRlY3NkMGVhNml5Y2F2azV4YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ICOgUNjpvO0PC/giphy.gif" width="220" alt="cute anime gif" />
</p>

<p align="center">
  <b>Aesthetic • Powerful • Self-Hosted • Free</b><br/>
  Built with <b>discord.py 2.7.1</b> + SQLite 💫
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-ffb6c1?style=for-the-badge&logo=python&logoColor=white">
  <img alt="discord.py" src="https://img.shields.io/badge/discord.py-2.7.1-cba6f7?style=for-the-badge&logo=discord&logoColor=white">
  <img alt="Database" src="https://img.shields.io/badge/Database-SQLite-f9e2af?style=for-the-badge&logo=sqlite&logoColor=black">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-a6e3a1?style=for-the-badge">
</p>

---

## 🌸 Overview

**ᏖᏕᏕ** is a cute but capable Discord bot designed for modern communities — moderation, leveling, economy, study tools, tickets, utility, and fun commands in one elegant package.

✅ **100% free & self-hosted**  
✅ **No paid database or external backend**  
✅ **Hybrid commands** (`/slash`, `!prefix`, `@mention`)  
✅ **Anime/cutie aesthetic + professional structure**

---

## 🧸 Feature Menu

| Category | Commands |
|---|---|
| 🔨 **Moderation** | `kick`, `ban`, `unban`, `timeout`, `untimeout`, `warn`, `warnings`, `clearwarnings`, `purge`, `lock`, `unlock`, `slowmode`, `setnick`, `addrole`, `removerole` |
| 🪙 **Leveling & Economy** | `rank`, `leaderboard`, `balance`, `daily`, `work`, `pay`, `shop`, `additem`, `removeitem`, `buy`, `inventory`, `addcoins` (+ passive XP/coins from chatting) |
| 🌸 **Fun & Games** | `8ball`, `coinflip`, `roll`, `rps`, `ship`, `compliment`, `meme`, `joke`, `hug`, `pat`, `cuddle`, `poke`, `trivia`, `guess` |
| 💌 **Utility** | `ping`, `userinfo`, `serverinfo`, `avatar`, `botinfo`, `poll`, `remindme`, `afk`, `timestamp`, `suggest` |
| 🎫 **Welcome & Tickets** | `setwelcome`, `setleave`, `testwelcome`, `ticketsetup`, `ticketpanel`, `addtoticket`, `closeticket` (+ automatic join/leave messages) |
| 📚 **Study** | `pomodoro`, `studytimer`, `studytip`, `checkin`, `streak`, `todo`, `todolist`, `tododone`, `tododelete` |
| 💫 **Help** | One polished `/help` command with dropdown categories |

> All commands work as **slash + prefix + mention hybrid commands**.

---

## ⚡ Quick Start

### 1) Create your Discord app
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) → **New Application**
2. Open **Bot** tab → **Reset Token** → copy your token
3. Enable **Privileged Gateway Intents**:
   - Server Members Intent
   - Message Content Intent
4. Open **OAuth2 → URL Generator**:
   - Scopes: `bot` + `applications.commands`
   - Required perms: Manage Roles, Manage Channels, Kick/Ban/Moderate Members, Manage Messages, Manage Nicknames, View/Send Messages, Embed Links, Read Message History, Add Reactions, Use Application Commands
5. Invite bot using generated URL

---

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3) Configure token

Rename `.env.example` → `.env` and set:

```env
DISCORD_TOKEN=your_bot_token_here
```

---

### 4) Run bot

```bash
python main.py
```

If terminal shows:

`ᏖᏕᏕ is online as ...`

you’re live ✨

---

## 🏗️ Project Structure

```text
tss-bot/
├── main.py               # entry point — loads all cogs
├── config.py             # colors, emojis, bot name theme
├── database.py           # SQLite schema + data access
├── requirements.txt
├── .env.example
└── cogs/
    ├── moderation.py
    ├── leveling_economy.py
    ├── fun.py
    ├── utility.py
    ├── welcome_tickets.py
    ├── study.py
    └── help.py
```

---

## 💾 Data & Reliability

- SQLite DB (`tss.db`) auto-creates beside `main.py`
- Keep `tss.db` persistent on your host to preserve economy, levels, and warnings
- Public APIs used for fun commands are free and key-less  
  (`meme-api.com`, `icanhazdadjoke.com`, `nekos.best`, `opentdb.com`)
- If an API is down, bot returns graceful fallback messages (no crash)

---

## 🎨 Customization

You can easily retheme your bot in `config.py`:

- Embed colors
- Emojis/icons
- Bot name styling
- Footer text aesthetic

Admins can expand economy items directly in Discord using `/additem` (no code edits needed).

---

## 🌟 Hosting Notes

Since you already host bots:

- Upload this full folder
- Start command: `python main.py`
- Set env var: `DISCORD_TOKEN=...` in host dashboard

Done. Cute bot online. Professional workflow. Zero paid stack. 💗

---

## 🩷 Credits

Made with love, pastel vibes, and too much coffee ☕🌸  
If you use this, consider starring the repo and sharing your themed version!

<p align="center">
  <img src="https://media.giphy.com/media/3oriO0OEd9QIDdllqo/giphy.gif" width="180" alt="anime wave gif"/>
</p>
