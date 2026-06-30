"""
ᏖᏕᏕ — leveling & economy cog.
XP is earned passively from chatting (cooldown to prevent spam-farming).
Economy is a simple coin system: daily / work / shop / pay.
"""

import random
import time

import discord
from discord import app_commands
from discord.ext import commands

from config import COLORS, EMOJI, FOOTER_TEXT

XP_PER_MESSAGE = (10, 20)
XP_COOLDOWN_SECONDS = 60
DAILY_AMOUNT = 250
WORK_COOLDOWN_SECONDS = 3600
WORK_AMOUNT_RANGE = (50, 200)


def xp_for_level(level: int) -> int:
    return 5 * (level ** 2) + 50 * level + 100


def econ_embed(title, description, color=COLORS["economy"]):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=FOOTER_TEXT)
    return embed


def progress_bar(current, total, length=14):
    filled = min(length, int(length * current / max(total, 1)))
    return "🩷" * filled + "🤍" * (length - filled)


class Leveling(commands.Cog):
    """🪙 Leveling & Economy — chat to earn XP, then spend coins in the shop."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        db = self.bot.db
        row = await db.get_level_row(message.guild.id, message.author.id)
        now = int(time.time())
        if now - row["last_xp_at"] < XP_COOLDOWN_SECONDS:
            return
        gained = random.randint(*XP_PER_MESSAGE)
        new_xp = row["xp"] + gained
        new_level = row["level"]
        needed = xp_for_level(new_level)
        leveled_up = False
        while new_xp >= needed:
            new_xp -= needed
            new_level += 1
            needed = xp_for_level(new_level)
            leveled_up = True
        await db.set_xp_level(message.guild.id, message.author.id, new_xp, new_level, now)
        await db.add_balance(message.guild.id, message.author.id, gained // 2)
        if leveled_up:
            try:
                await message.channel.send(embed=econ_embed(
                    f"{EMOJI['star']} Level up!",
                    f"{message.author.mention} reached **Level {new_level}**! {EMOJI['sparkle']}",
                ))
            except discord.HTTPException:
                pass

    # ---------- rank ----------
    @commands.hybrid_command(name="rank", description="Show your (or someone's) level and XP.")
    @app_commands.describe(member="Whose rank to check")
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        row = await self.bot.db.get_level_row(ctx.guild.id, member.id)
        needed = xp_for_level(row["level"])
        embed = econ_embed(
            f"{EMOJI['star']} {member.display_name}'s rank",
            f"**Level:** {row['level']}\n"
            f"**XP:** {row['xp']} / {needed}\n"
            f"{progress_bar(row['xp'], needed)}",
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    # ---------- leaderboard ----------
    @commands.hybrid_command(name="leaderboard", description="Show the server's top XP earners.")
    async def leaderboard(self, ctx):
        rows = await self.bot.db.leaderboard(ctx.guild.id, limit=10)
        if not rows:
            await ctx.send(embed=econ_embed("Leaderboard", "No one has earned XP yet!"))
            return
        lines = []
        for i, r in enumerate(rows, start=1):
            member = ctx.guild.get_member(r["user_id"])
            name = member.display_name if member else f"<@{r['user_id']}>"
            lines.append(f"**{i}.** {name} — Level {r['level']} ({r['xp']} xp)")
        await ctx.send(embed=econ_embed(f"{EMOJI['star']} Leaderboard", "\n".join(lines)))

    # ---------- balance ----------
    @commands.hybrid_command(name="balance", description="Check your (or someone's) coin balance.")
    @app_commands.describe(member="Whose balance to check")
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        row = await self.bot.db.get_economy_row(ctx.guild.id, member.id)
        await ctx.send(embed=econ_embed(
            f"{EMOJI['coin']} Balance",
            f"**{member.display_name}** has **{row['balance']}** coins.",
        ))

    # ---------- daily ----------
    @commands.hybrid_command(name="daily", description="Claim your daily coins.")
    async def daily(self, ctx):
        row = await self.bot.db.get_economy_row(ctx.guild.id, ctx.author.id)
        now = int(time.time())
        if now - row["last_daily"] < 86400:
            remaining = 86400 - (now - row["last_daily"])
            hours, rem = divmod(remaining, 3600)
            minutes = rem // 60
            await ctx.send(embed=econ_embed(
                f"{EMOJI['clock']} Already claimed",
                f"Come back in **{hours}h {minutes}m** for your next daily!",
                COLORS["error"],
            ))
            return
        await self.bot.db.add_balance(ctx.guild.id, ctx.author.id, DAILY_AMOUNT)
        await self.bot.db.set_last_daily(ctx.guild.id, ctx.author.id, now)
        await ctx.send(embed=econ_embed(
            f"{EMOJI['coin']} Daily claimed!",
            f"You received **{DAILY_AMOUNT}** coins. See you tomorrow! {EMOJI['sparkle']}",
        ))

    # ---------- work ----------
    @commands.hybrid_command(name="work", description="Work to earn some coins.")
    async def work(self, ctx):
        row = await self.bot.db.get_economy_row(ctx.guild.id, ctx.author.id)
        now = int(time.time())
        if now - row["last_work"] < WORK_COOLDOWN_SECONDS:
            remaining = WORK_COOLDOWN_SECONDS - (now - row["last_work"])
            minutes = remaining // 60
            await ctx.send(embed=econ_embed(
                f"{EMOJI['clock']} Still tired",
                f"You can work again in **{minutes}** minute(s).",
                COLORS["error"],
            ))
            return
        earned = random.randint(*WORK_AMOUNT_RANGE)
        jobs = [
            "baked a batch of cookies", "helped at the flower shop",
            "organized a bookshelf", "walked some dogs",
            "ran a lemonade stand", "tutored a classmate",
        ]
        await self.bot.db.add_balance(ctx.guild.id, ctx.author.id, earned)
        await self.bot.db.set_last_work(ctx.guild.id, ctx.author.id, now)
        await ctx.send(embed=econ_embed(
            f"{EMOJI['bear']} Work complete",
            f"You {random.choice(jobs)} and earned **{earned}** coins!",
        ))

    # ---------- pay ----------
    @commands.hybrid_command(name="pay", description="Give some of your coins to another member.")
    @app_commands.describe(member="Who to pay", amount="How many coins")
    async def pay(self, ctx, member: discord.Member, amount: app_commands.Range[int, 1, None]):
        if member.id == ctx.author.id:
            await ctx.send(embed=econ_embed(f"{EMOJI['cross']} Nice try", "You can't pay yourself!", COLORS["error"]))
            return
        row = await self.bot.db.get_economy_row(ctx.guild.id, ctx.author.id)
        if row["balance"] < amount:
            await ctx.send(embed=econ_embed(f"{EMOJI['cross']} Not enough coins", "You don't have enough coins for that.", COLORS["error"]))
            return
        await self.bot.db.add_balance(ctx.guild.id, ctx.author.id, -amount)
        await self.bot.db.add_balance(ctx.guild.id, member.id, amount)
        await ctx.send(embed=econ_embed(f"{EMOJI['coin']} Sent!", f"**{ctx.author.display_name}** sent **{amount}** coins to **{member.display_name}**."))

    # ---------- shop ----------
    @commands.hybrid_command(name="shop", description="View the server shop.")
    async def shop(self, ctx):
        items = await self.bot.db.list_shop_items(ctx.guild.id)
        if not items:
            await ctx.send(embed=econ_embed(f"{EMOJI['shop']} Shop", "The shop is empty right now."))
            return
        lines = [f"**#{i['id']} — {i['name']}** · {i['price']} {EMOJI['coin']}\n{i['description'] or ''}" for i in items]
        await ctx.send(embed=econ_embed(f"{EMOJI['shop']} Shop", "\n\n".join(lines)))

    @commands.hybrid_command(name="additem", description="(Admin) Add an item to the shop.")
    @app_commands.describe(name="Item name", price="Price in coins", description="Item description")
    @commands.has_permissions(manage_guild=True)
    async def additem(self, ctx, name: str, price: app_commands.Range[int, 1, None], description: str = ""):
        await self.bot.db.add_shop_item(ctx.guild.id, name, price, description)
        await ctx.send(embed=econ_embed(f"{EMOJI['sparkle']} Item added", f"**{name}** added to the shop for **{price}** coins."))

    @commands.hybrid_command(name="removeitem", description="(Admin) Remove an item from the shop.")
    @app_commands.describe(item_id="Item ID (from /shop)")
    @commands.has_permissions(manage_guild=True)
    async def removeitem(self, ctx, item_id: int):
        await self.bot.db.remove_shop_item(ctx.guild.id, item_id)
        await ctx.send(embed=econ_embed(f"{EMOJI['sparkle']} Removed", f"Item **#{item_id}** removed from the shop."))

    @commands.hybrid_command(name="buy", description="Buy an item from the shop.")
    @app_commands.describe(item_id="Item ID (from /shop)")
    async def buy(self, ctx, item_id: int):
        item = await self.bot.db.get_shop_item(ctx.guild.id, item_id)
        if item is None:
            await ctx.send(embed=econ_embed(f"{EMOJI['cross']} Not found", "That item doesn't exist.", COLORS["error"]))
            return
        row = await self.bot.db.get_economy_row(ctx.guild.id, ctx.author.id)
        if row["balance"] < item["price"]:
            await ctx.send(embed=econ_embed(f"{EMOJI['cross']} Not enough coins", "You can't afford that yet!", COLORS["error"]))
            return
        await self.bot.db.add_balance(ctx.guild.id, ctx.author.id, -item["price"])
        await self.bot.db.add_inventory(ctx.guild.id, ctx.author.id, item_id, 1)
        await ctx.send(embed=econ_embed(f"{EMOJI['shop']} Purchased!", f"You bought **{item['name']}** for **{item['price']}** coins."))

    @commands.hybrid_command(name="inventory", description="View your purchased items.")
    async def inventory(self, ctx):
        rows = await self.bot.db.get_inventory(ctx.guild.id, ctx.author.id)
        if not rows:
            await ctx.send(embed=econ_embed(f"{EMOJI['shop']} Inventory", "You don't own anything yet."))
            return
        lines = [f"**{r['name']}** x{r['quantity']}" for r in rows]
        await ctx.send(embed=econ_embed(f"{EMOJI['shop']} Your inventory", "\n".join(lines)))

    # ---------- admin xp/coin adjust ----------
    @commands.hybrid_command(name="addcoins", description="(Admin) Give coins to a member.")
    @app_commands.describe(member="Member", amount="Amount of coins")
    @commands.has_permissions(manage_guild=True)
    async def addcoins(self, ctx, member: discord.Member, amount: int):
        await self.bot.db.add_balance(ctx.guild.id, member.id, amount)
        await ctx.send(embed=econ_embed(f"{EMOJI['coin']} Updated", f"Gave **{amount}** coins to **{member.display_name}**."))


async def setup(bot):
    await bot.add_cog(Leveling(bot))
