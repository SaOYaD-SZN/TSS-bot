"""
ᏖᏕᏕ — moderation cog.
All commands are hybrid (work as both /slash and !prefix) and require
the matching Discord permission, so only staff can use them.
"""

import datetime as dt

import discord
from discord import app_commands
from discord.ext import commands

from config import COLORS, EMOJI, FOOTER_TEXT


def mod_embed(title, description, color=COLORS["moderation"]):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=FOOTER_TEXT)
    return embed


class Moderation(commands.Cog):
    """🔨 Moderation — keep your server safe and tidy."""

    def __init__(self, bot):
        self.bot = bot

    # ---------- kick ----------
    @commands.hybrid_command(name="kick", description="Kick a member from the server.")
    @app_commands.describe(member="Member to kick", reason="Why are you kicking them?")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await ctx.send(embed=mod_embed(
            f"{EMOJI['ribbon']} Member kicked",
            f"**{member}** has been kicked.\n**Reason:** {reason}",
        ))

    # ---------- ban ----------
    @commands.hybrid_command(name="ban", description="Ban a member from the server.")
    @app_commands.describe(member="Member to ban", reason="Why are you banning them?")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await ctx.send(embed=mod_embed(
            f"{EMOJI['ban']} Member banned",
            f"**{member}** has been banned.\n**Reason:** {reason}",
        ))

    # ---------- unban ----------
    @commands.hybrid_command(name="unban", description="Unban a user by their ID.")
    @app_commands.describe(user_id="The ID of the user to unban")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await ctx.guild.unban(user)
            await ctx.send(embed=mod_embed(f"{EMOJI['sparkle']} Unbanned", f"**{user}** can come back now."))
        except (discord.NotFound, ValueError):
            await ctx.send(embed=mod_embed(f"{EMOJI['cross']} Not found", "Couldn't find that user in the ban list.", COLORS["error"]))

    # ---------- timeout ----------
    @commands.hybrid_command(name="timeout", description="Timeout (mute) a member for a number of minutes.")
    @app_commands.describe(member="Member to timeout", minutes="Duration in minutes", reason="Reason")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason: str = "No reason provided"):
        duration = dt.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        await ctx.send(embed=mod_embed(
            f"{EMOJI['mute']} Timed out",
            f"**{member}** is timed out for **{minutes}** minute(s).\n**Reason:** {reason}",
        ))

    # ---------- remove timeout ----------
    @commands.hybrid_command(name="untimeout", description="Remove a member's timeout.")
    @app_commands.describe(member="Member to remove timeout from")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(embed=mod_embed(f"{EMOJI['sparkle']} Timeout removed", f"**{member}** can talk again."))

    # ---------- warn ----------
    @commands.hybrid_command(name="warn", description="Warn a member (saved permanently).")
    @app_commands.describe(member="Member to warn", reason="Why are you warning them?")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await self.bot.db.add_warning(ctx.guild.id, member.id, ctx.author.id, reason)
        await ctx.send(embed=mod_embed(
            f"{EMOJI['warn']} Warning issued",
            f"**{member}** has been warned.\n**Reason:** {reason}",
        ))
        try:
            await member.send(embed=mod_embed(
                f"{EMOJI['warn']} You were warned",
                f"You received a warning in **{ctx.guild.name}**.\n**Reason:** {reason}",
            ))
        except discord.Forbidden:
            pass

    # ---------- warnings list ----------
    @commands.hybrid_command(name="warnings", description="List a member's warnings.")
    @app_commands.describe(member="Member to check")
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member):
        rows = await self.bot.db.get_warnings(ctx.guild.id, member.id)
        if not rows:
            await ctx.send(embed=mod_embed(f"{EMOJI['sparkle']} Clean record", f"**{member}** has no warnings."))
            return
        lines = [f"**#{r['id']}** — {r['reason']} (by <@{r['moderator_id']}>)" for r in rows]
        await ctx.send(embed=mod_embed(f"{EMOJI['warn']} Warnings for {member}", "\n".join(lines)))

    # ---------- clear warnings ----------
    @commands.hybrid_command(name="clearwarnings", description="Clear all warnings for a member.")
    @app_commands.describe(member="Member to clear warnings for")
    @commands.has_permissions(moderate_members=True)
    async def clearwarnings(self, ctx, member: discord.Member):
        await self.bot.db.clear_warnings(ctx.guild.id, member.id)
        await ctx.send(embed=mod_embed(f"{EMOJI['sparkle']} Cleared", f"All warnings for **{member}** were cleared."))

    # ---------- purge ----------
    @commands.hybrid_command(name="purge", description="Delete a number of recent messages.")
    @app_commands.describe(amount="How many messages to delete (max 100)")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: app_commands.Range[int, 1, 100]):
        await ctx.defer(ephemeral=True)
        deleted = await ctx.channel.purge(limit=amount + (1 if not ctx.interaction else 0))
        msg = f"Deleted **{len(deleted)}** message(s). {EMOJI['sparkle']}"
        if ctx.interaction:
            await ctx.send(embed=mod_embed("Tidied up!", msg), ephemeral=True)
        else:
            await ctx.send(embed=mod_embed("Tidied up!", msg))

    # ---------- lock / unlock ----------
    @commands.hybrid_command(name="lock", description="Lock the current channel (no one can send messages).")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(embed=mod_embed(f"{EMOJI['lock']} Locked", "This channel is now locked."))

    @commands.hybrid_command(name="unlock", description="Unlock the current channel.")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(embed=mod_embed(f"{EMOJI['unlock']} Unlocked", "This channel is now unlocked."))

    # ---------- slowmode ----------
    @commands.hybrid_command(name="slowmode", description="Set slowmode delay (seconds) for this channel. 0 to disable.")
    @app_commands.describe(seconds="Delay in seconds (0-21600)")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: app_commands.Range[int, 0, 21600]):
        await ctx.channel.edit(slowmode_delay=seconds)
        text = "Slowmode disabled." if seconds == 0 else f"Slowmode set to **{seconds}** second(s)."
        await ctx.send(embed=mod_embed(f"{EMOJI['clock']} Slowmode", text))

    # ---------- nickname ----------
    @commands.hybrid_command(name="setnick", description="Change a member's nickname.")
    @app_commands.describe(member="Member", nickname="New nickname (leave empty to reset)")
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def setnick(self, ctx, member: discord.Member, nickname: str = None):
        await member.edit(nick=nickname)
        await ctx.send(embed=mod_embed(f"{EMOJI['sparkle']} Nickname updated", f"**{member}**'s nickname is now **{nickname or member.name}**."))

    # ---------- role add/remove ----------
    @commands.hybrid_command(name="addrole", description="Add a role to a member.")
    @app_commands.describe(member="Member", role="Role to add")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        await ctx.send(embed=mod_embed(f"{EMOJI['sparkle']} Role added", f"Gave **{role.name}** to **{member}**."))

    @commands.hybrid_command(name="removerole", description="Remove a role from a member.")
    @app_commands.describe(member="Member", role="Role to remove")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, role: discord.Role):
        await member.remove_roles(role)
        await ctx.send(embed=mod_embed(f"{EMOJI['sparkle']} Role removed", f"Removed **{role.name}** from **{member}**."))


async def setup(bot):
    await bot.add_cog(Moderation(bot))
