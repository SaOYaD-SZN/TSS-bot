# ᏖᏕᏕ — your all-in-one cutie Discord bot 🎀

A free, self-hosted Discord bot built with **discord.py 2.7.1** (the current
stable release as of 2026). Everything runs on a local SQLite database, so
there's no paid database or external service required — just your bot token.

## ✨ What's included

| Category | Commands |
|---|---|
| 🔨 Moderation | kick, ban, unban, timeout, untimeout, warn, warnings, clearwarnings, purge, lock, unlock, slowmode, setnick, addrole, removerole |
| 🪙 Leveling & Economy | rank, leaderboard, balance, daily, work, pay, shop, additem, removeitem, buy, inventory, addcoins (+ passive XP/coins from chatting) |
| 🌸 Fun & Games | 8ball, coinflip, roll, rps, ship, compliment, meme, joke, hug, pat, cuddle, poke, trivia, guess |
| 💌 Utility | ping, userinfo, serverinfo, avatar, botinfo, poll, remindme, afk, timestamp, suggest |
| 🎫 Welcome & Tickets | setwelcome, setleave, testwelcome, ticketsetup, ticketpanel, addtoticket, closeticket (+ automatic join/leave messages) |
| 📚 Study | pomodoro, studytimer, studytip, checkin, streak, todo, todolist, tododone, tododelete |
| 💫 Help | one `/help` command with a dropdown menu for every category |

All commands work as **both** slash commands (`/command`) and prefix
commands (`!command` or `@ᏖᏕᏕ command`) thanks to discord.py's hybrid
commands.

## 1. Create the bot application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) → **New Application**.
2. Open the **Bot** tab → click **Reset Token** → copy the token (you'll paste it into `.env` in step 3).
3. On the same **Bot** tab, scroll to **Privileged Gateway Intents** and turn ON:
   - **Server Members Intent**
   - **Message Content Intent**
4. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot` and `applications.commands`
   - Bot permissions: Manage Roles, Manage Channels, Kick Members, Ban Members,
     Moderate Members, Manage Messages, Manage Nicknames, View Channels,
     Send Messages, Embed Links, Read Message History, Add Reactions,
     Use Application Commands
   - Copy the generated URL and open it to invite the bot to your server.

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

(Uses the latest 2026 releases: discord.py 2.7.1, aiosqlite, aiohttp, python-dotenv.)

## 3. Add your token

Rename `.env.example` to `.env` and paste your token:

```
DISCORD_TOKEN=your_bot_token_here
```

## 4. Run it

```bash
python main.py
```

You should see `ᏖᏕᏕ is online as ...` in your terminal — that's it, your bot
is live! Since you already have hosting set up, just upload this whole
`tss-bot` folder there, set the start command to `python main.py`, and make
sure the `DISCORD_TOKEN` environment variable is set (most hosts let you set
env vars in their dashboard instead of using a `.env` file).

## Project structure

```
tss-bot/
├── main.py              # entry point — loads all cogs
├── config.py             # colours, emojis, bot name (edit to re-theme)
├── database.py           # SQLite schema + all data access
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

## Notes & free-tier tips

- **No paid services used anywhere.** The meme/joke/gif/trivia commands call
  free, key-less public APIs (meme-api.com, icanhazdadjoke.com, nekos.best,
  opentdb.com). If one of them is briefly down, the bot just replies with a
  friendly "couldn't fetch that" message instead of crashing.
- The SQLite file (`tss.db`) is created automatically next to `main.py` the
  first time you run the bot — make sure your host keeps that file persistent
  between restarts (most do), or your levels/economy/warnings will reset.
- Want to re-theme the colours/emojis or add a different bot name in
  embeds/footers? Everything is centralized in `config.py`.
- To add more shop items for the economy system, server admins can run
  `/additem` right inside Discord — no code changes needed.
