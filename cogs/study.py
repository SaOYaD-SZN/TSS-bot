"""
ᏖᏕᏕ — study cog.
Pomodoro-style focus timers, a personal to-do list, and a daily study streak tracker.
"""

import asyncio
import random
import time

import discord
from discord import app_commands
from discord.ext import commands

from config import COLORS, EMOJI, FOOTER_TEXT

STUDY_TIPS = [
    "Try the Pomodoro technique: 25 minutes focused, then a 5 minute break.",
    "Put your phone in another room while you study — out of sight, out of mind!",
    "Teach what you just learned to someone else (even out loud to yourself).",
    "Active recall beats re-reading: quiz yourself instead of just rereading notes.",
    "Studying in short, spaced sessions beats one long cram session.",
    "Stay hydrated — your brain works better with enough water!",
    "Switch up your study location every once in a while to stay alert.",
]


def study_embed(title, description, color=COLORS["study"]):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=FOOTER_TEXT)
    return embed


class Study(commands.Cog):
    """📚 Study — pomodoro timers, streaks, and a personal to-do list."""

    def __init__(self, bot):
        self.bot = bot

    # ---------- pomodoro ----------
    @commands.hybrid_command(
        name="pomodoro",
        description="Start a pomodoro focus timer"
        " (default 25 min focus / 5 min break).",
    )
    @app_commands.describe(
        focus_minutes="Focus duration in minutes",
        break_minutes="Break duration in minutes",
    )
    async def pomodoro(
        self,
        ctx,
        focus_minutes: app_commands.Range[int, 1, 180] = 25,
        break_minutes: app_commands.Range[int, 1, 60] = 5,
    ):
        await ctx.send(
            embed=study_embed(
                f"{EMOJI['book']} Focus time started!",
                f"Focus for **{focus_minutes}** minutes."
                f" I'll let you know when it's break time! {EMOJI['sparkle']}",
            )
        )
        await asyncio.sleep(focus_minutes * 60)
        await ctx.send(
            embed=study_embed(
                f"{EMOJI['clock']} Break time!",
                f"{ctx.author.mention} nice work!"
                f" Take a **{break_minutes}** minute break. {EMOJI['flower']}",
            )
        )
        await asyncio.sleep(break_minutes * 60)
        await ctx.send(
            embed=study_embed(
                f"{EMOJI['sparkle']} Break's over!",
                f"{ctx.author.mention} ready for another round? Run `/pomodoro` again!",
            )
        )

    # ---------- timer ----------
    @commands.hybrid_command(
        name="studytimer",
        description="Set a plain countdown timer, e.g. for a quick study sprint.",
    )
    @app_commands.describe(minutes="Minutes to count down")
    async def studytimer(self, ctx, minutes: app_commands.Range[int, 1, 300]):
        await ctx.send(
            embed=study_embed(
                f"{EMOJI['clock']} Timer started",
                f"I'll ping you in **{minutes}** minute(s)!",
            )
        )
        await asyncio.sleep(minutes * 60)
        await ctx.send(
            embed=study_embed(
                f"{EMOJI['sparkle']} Time's up!",
                f"{ctx.author.mention} your timer is done!",
            )
        )

    # ---------- study tip ----------
    @commands.hybrid_command(name="studytip", description="Get a random study tip.")
    async def studytip(self, ctx):
        await ctx.send(
            embed=study_embed(f"{EMOJI['book']} Study tip", random.choice(STUDY_TIPS))
        )

    # ---------- streaks ----------
    @commands.hybrid_command(
        name="checkin", description="Check in for today to build your study streak."
    )
    async def checkin(self, ctx):
        row = await self.bot.db.get_streak(ctx.author.id)
        now = int(time.time())
        last = row["last_checkin"]
        one_day = 86400
        if now - last < one_day:
            await ctx.send(
                embed=study_embed(
                    f"{EMOJI['cross']} Already checked in",
                    "You've already checked in today — come back tomorrow!",
                    COLORS["error"],
                )
            )
            return
        new_streak = row["current_streak"] + 1 if now - last < 2 * one_day else 1
        longest = max(row["longest_streak"], new_streak)
        await self.bot.db.update_streak(
            ctx.author.id, new_streak, longest, now, row["total_sessions"] + 1
        )
        await ctx.send(
            embed=study_embed(
                f"{EMOJI['star']} Checked in!",
                f"Current streak: **{new_streak}** day(s) 🔥"
                f"\nLongest streak: **{longest}** day(s)"
                f"\nTotal check-ins: **{row['total_sessions'] + 1}**",
            )
        )

    @commands.hybrid_command(
        name="streak", description="View your current study streak."
    )
    async def streak(self, ctx):
        row = await self.bot.db.get_streak(ctx.author.id)
        await ctx.send(
            embed=study_embed(
                f"{EMOJI['star']} Your study streak",
                f"Current: **{row['current_streak']}** day(s) 🔥"
                f"\nLongest: **{row['longest_streak']}** day(s)"
                f"\nTotal check-ins: **{row['total_sessions']}**",
            )
        )

    # ---------- todo list ----------
    @commands.hybrid_command(
        name="todo", description="Add a task to your personal study to-do list."
    )
    @app_commands.describe(task="What do you need to do?")
    async def todo(self, ctx, *, task: str):
        await self.bot.db.add_todo(ctx.author.id, task)
        await ctx.send(
            embed=study_embed(
                f"{EMOJI['check']} Added", f"Added to your to-do list: *{task}*"
            )
        )

    @commands.hybrid_command(
        name="todolist", description="View your personal to-do list."
    )
    async def todolist(self, ctx):
        rows = await self.bot.db.list_todos(ctx.author.id)
        if not rows:
            await ctx.send(
                embed=study_embed(
                    f"{EMOJI['book']} To-do list",
                    "Your list is empty! Add one with `/todo`.",
                )
            )
            return
        lines = []
        for r in rows:
            mark = "✅" if r["done"] else "🩷"
            lines.append(f"{mark} **#{r['id']}** {r['task']}")
        await ctx.send(
            embed=study_embed(f"{EMOJI['book']} Your to-do list", "\n".join(lines))
        )

    @commands.hybrid_command(name="tododone", description="Mark a to-do item as done.")
    @app_commands.describe(todo_id="The ID number from /todolist")
    async def tododone(self, ctx, todo_id: int):
        await self.bot.db.complete_todo(todo_id, ctx.author.id)
        await ctx.send(
            embed=study_embed(
                f"{EMOJI['check']} Nice work!", f"Marked #{todo_id} as done. 🎉"
            )
        )

    @commands.hybrid_command(name="tododelete", description="Delete a to-do item.")
    @app_commands.describe(todo_id="The ID number from /todolist")
    async def tododelete(self, ctx, todo_id: int):
        await self.bot.db.delete_todo(todo_id, ctx.author.id)
        await ctx.send(
            embed=study_embed(
                f"{EMOJI['sparkle']} Removed", f"Deleted #{todo_id} from your list."
            )
        )


async def setup(bot):
    await bot.add_cog(Study(bot))
