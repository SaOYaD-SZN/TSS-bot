"""
ᏖᏕᏕ — utility cog.
Server/user info, polls, reminders, AFK system, suggestions, etc.
"""

import contextlib
import re
import time
from datetime import UTC, datetime

import discord
from discord import app_commands
from discord.ext import commands

from config import COLORS, EMOJI, FOOTER_TEXT

DURATION_RE = re.compile(r"(\d+)([smhd])")
UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def util_embed(title, description, color=COLORS["utility"]):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=FOOTER_TEXT)
    return embed


def parse_duration(text: str) -> int | None:
    matches = DURATION_RE.findall(text.lower())
    if not matches:
        return None
    return sum(int(amount) * UNIT_SECONDS[unit] for amount, unit in matches)


class Utility(commands.Cog):
    """💌 Utility — handy everyday commands."""

    def __init__(self, bot):
        self.bot = bot

    # ---------- ping ----------
    @commands.hybrid_command(name="ping", description="Check the bot's latency.")
    async def ping(self, ctx):
        await ctx.send(
            embed=util_embed(
                f"{EMOJI['sparkle']} Pong!",
                f"Latency: **{round(self.bot.latency * 1000)}ms**",
            )
        )

    # ---------- userinfo ----------
    @commands.hybrid_command(name="userinfo", description="Show info about a member.")
    @app_commands.describe(member="Member to look up")
    async def userinfo(self, ctx, member: discord.Member | None = None):
        member = member or ctx.author
        embed = util_embed(f"{EMOJI['letter']} {member.display_name}", "")
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Username", value=str(member), inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(
            name="Joined server",
            value=discord.utils.format_dt(member.joined_at, "R")
            if member.joined_at
            else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Account created",
            value=discord.utils.format_dt(member.created_at, "R"),
            inline=True,
        )
        roles = (
            ", ".join(r.mention for r in member.roles if r.name != "@everyone")
            or "None"
        )
        embed.add_field(name="Roles", value=roles, inline=False)
        await ctx.send(embed=embed)

    # ---------- serverinfo ----------
    @commands.hybrid_command(
        name="serverinfo", description="Show info about this server."
    )
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = util_embed(f"{EMOJI['flower']} {guild.name}", "")
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=str(guild.owner), inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(
            name="Created",
            value=discord.utils.format_dt(guild.created_at, "R"),
            inline=True,
        )
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(
            name="Text channels", value=len(guild.text_channels), inline=True
        )
        embed.add_field(
            name="Voice channels", value=len(guild.voice_channels), inline=True
        )
        await ctx.send(embed=embed)

    # ---------- avatar ----------
    @commands.hybrid_command(name="avatar", description="Get a member's avatar.")
    @app_commands.describe(member="Member to look up")
    async def avatar(self, ctx, member: discord.Member | None = None):
        member = member or ctx.author
        embed = util_embed(f"{EMOJI['sparkle']} {member.display_name}'s avatar", "")
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    # ---------- botinfo ----------
    @commands.hybrid_command(name="botinfo", description="Show info about the bot.")
    async def botinfo(self, ctx):
        embed = util_embed(
            f"{EMOJI['ribbon']} About me",
            f"Hi, I'm an all-in-one cutie bot with moderation, leveling, economy, "
            f"fun, utility, welcome/tickets and study tools! {EMOJI['sparkle']}",
        )
        embed.add_field(name="Servers", value=len(self.bot.guilds))
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms")
        await ctx.send(embed=embed)

    # ---------- poll ----------
    @commands.hybrid_command(name="poll", description="Create a quick yes/no poll.")
    @app_commands.describe(question="The poll question")
    async def poll(self, ctx, *, question: str):
        embed = util_embed(f"{EMOJI['sparkle']} Poll", question)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🩷")
        await msg.add_reaction("🤍")

    # ---------- remindme ----------
    @commands.hybrid_command(
        name="remindme", description="Set a reminder, e.g. 1h30m study break."
    )
    @app_commands.describe(
        duration="e.g. 10m, 1h, 1d2h", message="What to remind you about"
    )
    async def remindme(self, ctx, duration: str, *, message: str = "Reminder!"):
        seconds = parse_duration(duration)
        if not seconds or seconds <= 0:
            await ctx.send(
                embed=util_embed(
                    f"{EMOJI['cross']} Invalid duration",
                    "Use a format like `10m`, `1h`, or `1h30m`.",
                    COLORS["error"],
                )
            )
            return
        remind_at = int(time.time()) + seconds
        await self.bot.db.add_reminder(
            ctx.author.id,
            ctx.channel.id,
            ctx.guild.id if ctx.guild else None,
            remind_at,
            message,
        )
        remind_dt = datetime.fromtimestamp(remind_at, tz=UTC)
        await ctx.send(
            embed=util_embed(
                f"{EMOJI['clock']} Reminder set",
                f"I'll remind you here {discord.utils.format_dt(remind_dt, 'R')}:"
                f" *{message}*",
            )
        )

    # ---------- afk ----------
    @commands.hybrid_command(
        name="afk", description="Set yourself as AFK with an optional reason."
    )
    @app_commands.describe(reason="Why are you AFK?")
    async def afk(self, ctx, *, reason: str = "AFK"):
        await self.bot.db.set_afk(
            ctx.author.id, ctx.guild.id if ctx.guild else None, reason
        )
        await ctx.send(
            embed=util_embed(
                f"{EMOJI['bear']} AFK set",
                f"You're now AFK: *{reason}*."
                " I'll let people know if they mention you!",
            )
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        # clear AFK if the (formerly) AFK user talks again
        afk_row = await self.bot.db.get_afk(message.author.id)
        if afk_row:
            await self.bot.db.clear_afk(message.author.id)
            with contextlib.suppress(discord.HTTPException):
                await message.channel.send(
                    embed=util_embed(
                        f"{EMOJI['sparkle']} Welcome back!",
                        f"{message.author.mention}, I removed your AFK status.",
                    ),
                    delete_after=8,
                )
        # notify if an AFK user is mentioned
        for user in message.mentions:
            row = await self.bot.db.get_afk(user.id)
            if row:
                await message.channel.send(
                    embed=util_embed(
                        f"{EMOJI['letter']} They're AFK",
                        f"**{user.display_name}** is AFK: *{row['reason']}*",
                    )
                )

    # ---------- timestamp ----------
    @commands.hybrid_command(
        name="timestamp", description="Get the current Discord timestamp tag."
    )
    async def timestamp(self, ctx):
        now = int(time.time())
        await ctx.send(
            embed=util_embed(
                f"{EMOJI['clock']} Timestamp",
                f"`<t:{now}:F>`"
                f" → {discord.utils.format_dt(discord.utils.utcnow(), 'F')}",
            )
        )

    # ---------- suggest ----------
    @commands.hybrid_command(
        name="suggest",
        description="Send a suggestion to the server (posts in this channel).",
    )
    @app_commands.describe(suggestion="Your suggestion")
    async def suggest(self, ctx, *, suggestion: str):
        embed = util_embed(f"{EMOJI['flower']} New suggestion", suggestion)
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🩷")
        await msg.add_reaction("🤍")


async def setup(bot):
    await bot.add_cog(Utility(bot))
