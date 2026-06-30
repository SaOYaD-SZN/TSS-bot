"""
ᏖᏕᏕ — main entry point.
Run with:  python main.py
Requires a .env file with DISCORD_TOKEN=your_bot_token_here
"""

import os
import asyncio
import logging
import time
from pathlib import Path

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from config import BOT_NAME, COLORS, FOOTER_TEXT, EMOJI
from database import Database

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
log = logging.getLogger(BOT_NAME)

INTENTS = discord.Intents.default()
INTENTS.members = True          # needed for welcome/leave + moderation
INTENTS.message_content = True  # needed for prefix commands + XP gain


class TssBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=INTENTS,
            help_command=None,
        )
        self.db = Database()

    async def setup_hook(self):
        await self.db.connect()
        cogs_dir = Path(__file__).parent / "cogs"
        for filename in os.listdir(cogs_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                log.info(f"Loaded cog: {filename}")
        self.reminder_loop.start()
        await self.tree.sync()

    async def close(self):
        await self.db.close()
        await super().close()

    @tasks.loop(seconds=20)
    async def reminder_loop(self):
        now = int(time.time())
        due = await self.db.due_reminders(now)
        for r in due:
            channel = self.get_channel(r["channel_id"])
            user = self.get_user(r["user_id"])
            mention = user.mention if user else f"<@{r['user_id']}>"
            embed = discord.Embed(
                title=f"{EMOJI['clock']} Reminder!",
                description=r["message"] or "(no message)",
                color=COLORS["primary"],
            )
            embed.set_footer(text=FOOTER_TEXT)
            try:
                if channel:
                    await channel.send(content=mention, embed=embed)
                elif user:
                    await user.send(embed=embed)
            except discord.HTTPException:
                pass
            await self.db.delete_reminder(r["id"])


bot = TssBot()


@bot.event
async def on_ready():
    log.info(f"{BOT_NAME} is online as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="over the server ✨")
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=_error_embed("You don't have permission to do that."))
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=_error_embed("You're missing a required argument! Check the help command."))
        return
    log.exception("Unhandled command error", exc_info=error)
    await ctx.send(embed=_error_embed("Something went a little wrong. Try again in a moment!"))


def _error_embed(text: str) -> discord.Embed:
    embed = discord.Embed(
        title=f"{EMOJI['cross']} Oops!",
        description=text,
        color=COLORS["error"],
    )
    embed.set_footer(text=FOOTER_TEXT)
    return embed


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit(
            "No DISCORD_TOKEN found. Create a .env file (see .env.example) "
            "and put your bot token in it."
        )
    asyncio.run(bot.start(TOKEN))
