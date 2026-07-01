"""
ᏖᏕᏕ — help cog.
A single /help command with a dropdown to browse commands by category.
"""

from typing import TypedDict

import discord
from discord.ext import commands

from config import BOT_NAME, COLORS, EMOJI, FOOTER_TEXT


class _CategoryInfo(TypedDict):
    label: str
    color: int
    commands: list[str]


CATEGORIES: dict[str, _CategoryInfo] = {
    "moderation": {
        "label": f"{EMOJI['ban']} Moderation",
        "color": COLORS["moderation"],
        "commands": [
            "kick",
            "ban",
            "unban",
            "timeout",
            "untimeout",
            "warn",
            "warnings",
            "clearwarnings",
            "purge",
            "lock",
            "unlock",
            "slowmode",
            "setnick",
            "addrole",
            "removerole",
        ],
    },
    "economy": {
        "label": f"{EMOJI['coin']} Leveling & Economy",
        "color": COLORS["economy"],
        "commands": [
            "rank",
            "leaderboard",
            "balance",
            "daily",
            "work",
            "pay",
            "shop",
            "buy",
            "inventory",
            "additem",
            "removeitem",
            "addcoins",
        ],
    },
    "fun": {
        "label": f"{EMOJI['flower']} Fun & Games",
        "color": COLORS["fun"],
        "commands": [
            "8ball",
            "coinflip",
            "roll",
            "rps",
            "ship",
            "compliment",
            "meme",
            "joke",
            "hug",
            "pat",
            "cuddle",
            "poke",
            "trivia",
            "guess",
        ],
    },
    "utility": {
        "label": f"{EMOJI['letter']} Utility",
        "color": COLORS["utility"],
        "commands": [
            "ping",
            "userinfo",
            "serverinfo",
            "avatar",
            "botinfo",
            "poll",
            "remindme",
            "afk",
            "timestamp",
            "suggest",
        ],
    },
    "tickets": {
        "label": f"{EMOJI['ticket']} Welcome & Tickets",
        "color": COLORS["tickets"],
        "commands": [
            "setwelcome",
            "setleave",
            "testwelcome",
            "ticketsetup",
            "ticketpanel",
            "addtoticket",
            "closeticket",
        ],
    },
    "study": {
        "label": f"{EMOJI['book']} Study",
        "color": COLORS["study"],
        "commands": [
            "pomodoro",
            "studytimer",
            "studytip",
            "checkin",
            "streak",
            "todo",
            "todolist",
            "tododone",
            "tododelete",
        ],
    },
}


def category_embed(bot, key):
    cat = CATEGORIES[key]
    lines = []
    for name in cat["commands"]:
        cmd = bot.get_command(name)
        desc = cmd.description if cmd and cmd.description else ""
        lines.append(f"**/{name}** — {desc}")
    embed = discord.Embed(
        title=cat["label"], description="\n".join(lines), color=cat["color"]
    )
    embed.set_footer(text=FOOTER_TEXT)
    return embed


class HelpSelect(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label=cat["label"], value=key)
            for key, cat in CATEGORIES.items()
        ]
        super().__init__(placeholder="Choose a category... 🎀", options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = category_embed(self.bot, self.values[0])
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.add_item(HelpSelect(bot))


class Help(commands.Cog):
    """💫 Help — browse everything I can do."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help", description="Browse all commands by category."
    )
    async def help_command(self, ctx):
        total = sum(len(c["commands"]) for c in CATEGORIES.values())
        embed = discord.Embed(
            title=f"{EMOJI['ribbon']} {BOT_NAME} — Help Menu",
            description=(
                f"Hi {ctx.author.mention}! I have **{total}** commands across "
                f"**{len(CATEGORIES)}** categories."
                " Pick one below to see what I can do!"
                f" {EMOJI['sparkle']}"
            ),
            color=COLORS["primary"],
        )
        embed.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=embed, view=HelpView(self.bot))


async def setup(bot):
    await bot.add_cog(Help(bot))
