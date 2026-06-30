"""
ᏖᏕᏕ — fun & games cog.
Uses only free, no-API-key services:
  meme-api.com, icanhazdadjoke.com, nekos.best, opentdb.com
"""

import asyncio
import random

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from config import COLORS, EMOJI, FOOTER_TEXT

EIGHTBALL_ANSWERS = [
    "Yes, definitely! 🩷", "It is certain. ✨", "Without a doubt!",
    "Maybe... ask again later 🤔", "I'm not sure about that one.",
    "My answer is no.", "Very doubtful.", "Absolutely not!",
    "Signs point to yes!", "Better not tell you now.",
]

COMPLIMENTS = [
    "you light up every room you walk into {EMOJI}",
    "your kindness makes the world softer {EMOJI}",
    "you're doing better than you think {EMOJI}",
    "your smile could fix anyone's bad day {EMOJI}",
    "you're so much stronger than you realize {EMOJI}",
]


def fun_embed(title, description, color=COLORS["fun"]):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=FOOTER_TEXT)
    return embed


class Fun(commands.Cog):
    """🌸 Fun & Games — memes, jokes, mini games and cute gifs."""

    def __init__(self, bot):
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    # ---------- 8ball ----------
    @commands.hybrid_command(name="8ball", description="Ask the magic 8-ball a question.")
    @app_commands.describe(question="Your question")
    async def eightball(self, ctx, *, question: str):
        embed = fun_embed(f"{EMOJI['star']} The 8-ball says...", random.choice(EIGHTBALL_ANSWERS))
        embed.add_field(name="Question", value=question)
        await ctx.send(embed=embed)

    # ---------- coinflip ----------
    @commands.hybrid_command(name="coinflip", description="Flip a coin.")
    async def coinflip(self, ctx):
        result = random.choice(["Heads", "Tails"])
        await ctx.send(embed=fun_embed(f"{EMOJI['coin']} Coin flip", f"It landed on... **{result}**!"))

    # ---------- dice ----------
    @commands.hybrid_command(name="roll", description="Roll a dice, e.g. 2d6.")
    @app_commands.describe(dice="Format: NdM, e.g. 2d6 (default 1d6)")
    async def roll(self, ctx, dice: str = "1d6"):
        try:
            n, sides = dice.lower().split("d")
            n, sides = int(n), int(sides)
            if not (1 <= n <= 20 and 2 <= sides <= 1000):
                raise ValueError
        except ValueError:
            await ctx.send(embed=fun_embed(f"{EMOJI['cross']} Invalid format", "Use the format NdM, like `2d6`.", COLORS["error"]))
            return
        rolls = [random.randint(1, sides) for _ in range(n)]
        await ctx.send(embed=fun_embed(f"{EMOJI['sparkle']} Dice roll", f"{', '.join(map(str, rolls))} (total: **{sum(rolls)}**)"))

    # ---------- rps ----------
    @commands.hybrid_command(name="rps", description="Play rock, paper, scissors against the bot.")
    @app_commands.describe(choice="rock, paper, or scissors")
    @app_commands.choices(choice=[
        app_commands.Choice(name="rock", value="rock"),
        app_commands.Choice(name="paper", value="paper"),
        app_commands.Choice(name="scissors", value="scissors"),
    ])
    async def rps(self, ctx, choice: str):
        bot_choice = random.choice(["rock", "paper", "scissors"])
        beats = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        if choice == bot_choice:
            outcome = "It's a tie!"
        elif beats[choice] == bot_choice:
            outcome = "You win! 🎉"
        else:
            outcome = "I win this time! 🩷"
        await ctx.send(embed=fun_embed(
            f"{EMOJI['ribbon']} Rock Paper Scissors",
            f"You chose **{choice}**, I chose **{bot_choice}**.\n{outcome}",
        ))

    # ---------- ship ----------
    @commands.hybrid_command(name="ship", description="Calculate compatibility between two members (just for fun!).")
    @app_commands.describe(member1="First member", member2="Second member (defaults to you)")
    async def ship(self, ctx, member1: discord.Member, member2: discord.Member = None):
        member2 = member2 or ctx.author
        seed = (member1.id + member2.id) % 101
        percent = seed
        bar = "🩷" * (percent // 10) + "🤍" * (10 - percent // 10)
        await ctx.send(embed=fun_embed(
            f"{EMOJI['letter']} Ship calculator",
            f"**{member1.display_name}** 💞 **{member2.display_name}**\n\n{bar}\n**{percent}%** compatible!",
        ))

    # ---------- compliment ----------
    @commands.hybrid_command(name="compliment", description="Get a cute compliment.")
    @app_commands.describe(member="Who to compliment (defaults to you)")
    async def compliment(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        text = random.choice(COMPLIMENTS).format(EMOJI=EMOJI["sparkle"])
        await ctx.send(embed=fun_embed(f"{EMOJI['flower']} Aww!", f"{member.mention}, {text}"))

    # ---------- meme ----------
    @commands.hybrid_command(name="meme", description="Get a random meme.")
    async def meme(self, ctx):
        try:
            async with self.session.get("https://meme-api.com/gimme") as resp:
                data = await resp.json()
            embed = fun_embed(data.get("title", "Meme"), "")
            embed.set_image(url=data["url"])
            embed.add_field(name="From", value=f"r/{data.get('subreddit', 'unknown')}")
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send(embed=fun_embed(f"{EMOJI['cross']} Oops", "Couldn't fetch a meme right now, try again soon!", COLORS["error"]))

    # ---------- joke ----------
    @commands.hybrid_command(name="joke", description="Get a random dad joke.")
    async def joke(self, ctx):
        try:
            headers = {"Accept": "application/json"}
            async with self.session.get("https://icanhazdadjoke.com/", headers=headers) as resp:
                data = await resp.json()
            await ctx.send(embed=fun_embed(f"{EMOJI['bear']} Here's a joke!", data["joke"]))
        except Exception:
            await ctx.send(embed=fun_embed(f"{EMOJI['cross']} Oops", "Couldn't fetch a joke right now, try again soon!", COLORS["error"]))

    # ---------- cute gif commands ----------
    async def _send_nekos(self, ctx, endpoint, title, with_target=True, member=None):
        try:
            async with self.session.get(f"https://nekos.best/api/v2/{endpoint}") as resp:
                data = await resp.json()
            result = data["results"][0]
            desc = f"{ctx.author.mention} → {member.mention}" if (with_target and member) else None
            embed = fun_embed(title, desc or "")
            embed.set_image(url=result["url"])
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send(embed=fun_embed(f"{EMOJI['cross']} Oops", "Couldn't fetch that right now, try again soon!", COLORS["error"]))

    @commands.hybrid_command(name="hug", description="Send someone a hug gif.")
    @app_commands.describe(member="Who to hug")
    async def hug(self, ctx, member: discord.Member):
        await self._send_nekos(ctx, "hug", f"{EMOJI['bear']} Hug!", member=member)

    @commands.hybrid_command(name="pat", description="Pat someone.")
    @app_commands.describe(member="Who to pat")
    async def pat(self, ctx, member: discord.Member):
        await self._send_nekos(ctx, "pat", f"{EMOJI['flower']} Pat pat!", member=member)

    @commands.hybrid_command(name="cuddle", description="Cuddle someone.")
    @app_commands.describe(member="Who to cuddle")
    async def cuddle(self, ctx, member: discord.Member):
        await self._send_nekos(ctx, "cuddle", f"{EMOJI['bear']} Cuddles!", member=member)

    @commands.hybrid_command(name="poke", description="Poke someone.")
    @app_commands.describe(member="Who to poke")
    async def poke(self, ctx, member: discord.Member):
        await self._send_nekos(ctx, "poke", f"{EMOJI['sparkle']} Poke!", member=member)

    # ---------- trivia ----------
    @commands.hybrid_command(name="trivia", description="Get a random trivia question.")
    async def trivia(self, ctx):
        try:
            async with self.session.get("https://opentdb.com/api.php?amount=1&type=multiple") as resp:
                data = await resp.json()
            q = data["results"][0]
            import html
            question = html.unescape(q["question"])
            options = [html.unescape(o) for o in q["incorrect_answers"] + [q["correct_answer"]]]
            random.shuffle(options)
            lettered = "\n".join(f"**{chr(65+i)}.** {opt}" for i, opt in enumerate(options))
            answer_letter = chr(65 + options.index(html.unescape(q["correct_answer"])))
            embed = fun_embed(f"{EMOJI['book']} Trivia time!", f"{question}\n\n{lettered}")
            embed.set_footer(text=f"{FOOTER_TEXT} • Answer revealed below in 15s")
            msg = await ctx.send(embed=embed)
            await asyncio.sleep(15)
            embed.add_field(name="Answer", value=f"It was **{answer_letter}**!")
            await msg.edit(embed=embed)
        except Exception:
            await ctx.send(embed=fun_embed(f"{EMOJI['cross']} Oops", "Couldn't fetch trivia right now, try again soon!", COLORS["error"]))

    # ---------- guess the number ----------
    @commands.hybrid_command(name="guess", description="Play a quick guess-the-number game (1-100).")
    async def guess(self, ctx):
        target = random.randint(1, 100)
        await ctx.send(embed=fun_embed(f"{EMOJI['sparkle']} Guess the number!", "I'm thinking of a number between 1 and 100. You have 6 tries — reply in chat!"))

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

        for attempt in range(6):
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=20)
            except Exception:
                await ctx.send(embed=fun_embed(f"{EMOJI['clock']} Time's up", f"The number was **{target}**. Try again sometime!"))
                return
            guess_val = int(msg.content)
            if guess_val == target:
                await ctx.send(embed=fun_embed(f"{EMOJI['star']} You got it!", f"The number was **{target}**! 🎉"))
                return
            hint = "higher 📈" if guess_val < target else "lower 📉"
            await ctx.send(embed=fun_embed("Close!", f"Try {hint}! ({5 - attempt} tries left)"))
        await ctx.send(embed=fun_embed("Out of tries!", f"The number was **{target}**. Better luck next time!"))


async def setup(bot):
    await bot.add_cog(Fun(bot))
