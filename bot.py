import discord
from discord.ext import commands
import random
import datetime

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

# 1. Setup Bot Intents and Instance
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Custom cute prefix: '🌸' or 't!'
bot = commands.Bot(command_prefix="t!", intents=intents, help_command=None)

# Aesthetic Hex Color Codes for Embeds
PASTEL_PINK = 0xFFB6C1
PASTEL_PURPLE = 0xE6E6FA
PASTEL_BLUE = 0xAEC6CF

# 2. Bot Ready Event
@bot.event
async def on_ready():
    print(f"✨ {bot.user.name} is now online and sparkling! ✨")
    # Setting an aesthetic custom status for 2026
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="☁️ 𝓘𝓷 𝓪 𝓹𝓪𝓼𝓽𝓮𝓵 𝓭𝓻𝓮𝓪𝓶 | t!help"
        )
    )

# 3. All-In-One Command Suite

# --- CATEGORY: UTILITY & HELP ---
@bot.command()
async def help(ctx):
    """🌸 Displays the aesthetic menu of all available commands."""
    embed = discord.Color.from_rgb(255, 182, 193)  # Soft pink
    embed = discord.Embed(
        title="─── ※ ᏖᏕᏕ 𝓜𝓮𝓷𝓾 ※ ───",
        description="𝖧𝖾𝗅𝗅𝗈, 𝖽𝖺𝗋𝗅𝗂𝗇𝗀! 𝖧𝖾𝗋𝖾 𝗂𝗌 𝖾𝗏𝖾𝗋𝗒𝗍𝗁𝗂𝗇𝗀 𝖨 𝖼𝖺𝗇 𝖽𝗈 𝖿𝗈𝗋 𝗒𝗈𝗎: ✨",
        color=PASTEL_PINK
    )
    embed.add_field(
        name="🎀 𝖴𝗍𝗂𝗅𝗂𝗍𝗐", 
        value="`t!help` - 𝖲𝗁𝗈𝗐𝗌 𝗍𝗁𝗂𝗌 𝖼𝗎𝗍𝖾 𝗆𝖾𝗇𝗎\n`t!ping` - 𝖢𝗁𝖾𝖼𝗄 𝗆𝗒 𝗁𝖾𝖺𝗋𝗍𝖻𝖾𝖺𝗍\n`t!userinfo` - 𝖲𝗉𝗒 𝗈𝗇 𝖺 𝗆𝖾𝗆 Slate", 
        inline=False
    )
    embed.add_field(
        name="🧸 𝖥𝗎𝗇 &  Get", 
        value="`t!8ball <question>` - 𝖳𝗁𝖾 𝗆𝖺𝗀𝗂𝖼 𝖼𝗋𝗒𝗌𝗍𝖺𝗅 𝖻𝖺𝗅𝗅\n`t!compliment <user>` - 𝖲𝗉𝗋𝖾𝖺𝖽 𝗌𝗈𝗆𝖾 𝗅𝗈𝗏𝖾\n`t!choose <or/options>` - 𝖫𝖾𝗍 𝗆𝖾 𝗉𝗂𝖼𝗄 𝖿𝗈𝗋 𝗒𝗈𝗎", 
        inline=False
    )
    embed.add_field(
        name="🧼 𝖬𝗈𝖽𝖾𝗋𝖺𝗍𝗂𝗈𝗇", 
        value="`t!purge <amount>` - 𝖢𝗅𝖾𝖺𝗇 𝗎𝗉 𝗆𝖾𝗌𝗌𝗒 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌\n`t!kick <user>` - 𝖦𝖾𝗇𝗍𝗅𝗒 𝗌𝖾𝗇𝖽 𝗌𝗈𝗆𝖾𝗈𝗇𝖾 𝖺𝗐𝖺𝗒\n`t!ban <user>` - 𝖡𝖺𝗇𝗂𝗌𝗁 𝖻𝖺𝖽 𝗏𝗂𝖻𝖾𝗌 𝖿𝗈𝗋𝖾𝗏𝖾𝗋", 
        inline=False
    )
    embed.set_footer(text="ᏖᏕᏕ 𝖡𝗈𝗍 2026 • Made with 🤍")
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    """☁️ Check response delay."""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        description=f"🌙 **𝖯𝗈𝗇𝗀!** 𝖬𝗒 𝗁𝖾𝖺𝗋𝗍 𝗂𝗌 𝖻𝖾𝖺𝗍𝗂𝗇𝗀 𝖺𝗍 `{latency}ms`",
        color=PASTEL_BLUE
    )
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    """🪞 View profiles layout."""
    member = member or ctx.author
    embed = discord.Embed(title=f"🌸 {member.name}'s Profile", color=PASTEL_PURPLE)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🎀 Account Created", value=member.created_at.strftime("%b %d, %Y"), inline=True)
    embed.add_field(name="☁️ Joined Server", value=member.joined_at.strftime("%b %d, %Y"), inline=True)
    embed.add_field(name="🪄 Top Role", value=member.top_role.mention, inline=False)
    await ctx.send(embed=embed)


# --- CATEGORY: FUN & AESTHETIC ---
@bot.command(name="8ball")
async def eightball(ctx, *, question: str):
    """🔮 Aesthetic oracle fortune."""
    responses = [
        "🌸 Yes, absolutely, darling!", "⭐ My stars say yes!", "💭 Ask again when the clouds clear...",
        "🪐 The universe is uncertain.", "🩹 No, sweetie, not today.", "🎐 Highly unlikely."
    ]
    embed = discord.Embed(
        title="🔮 𝖳𝗁𝖾 𝖬𝖺𝗀𝗂𝖼 𝖮𝗋𝖺𝖼𝗅𝖾",
        description=f"**𝖰𝗎𝖾𝗌𝗍𝗂𝗈𝗇:** {question}\n**𝖦𝗎𝗂𝖽𝖺𝗇𝖼𝖾:** {random.choice(responses)}",
        color=PASTEL_PURPLE
    )
    await ctx.send(embed=embed)

@bot.command()
async def compliment(ctx, member: discord.Member):
    """🧸 Send someone a sweet message."""
    compliments = [
        "you radiate pure golden hour energy! ✨", "your kindness is a breath of fresh air. 🍃",
        "the world is so much softer because you are in it. 🧸", "you are doing great, I'm proud of you! 🤍"
    ]
    await ctx.send(f"🌸 {member.mention}, {random.choice(compliments)}")

@bot.command()
async def choose(ctx, *, choices: str):
    """🥞 Make hard decisions easy."""
    options = choices.split(",")
    if len(options) < 2:
        return await ctx.send("🧁 *𝖯𝗅𝖾𝖺𝗌𝖾 𝗀𝗂𝗏𝖾 𝗆𝖾 𝖺𝗍 𝗅𝖾𝖺𝗌𝗍 𝗍𝗐𝗈 𝗈𝗉𝗍𝗂𝗈𝗇𝗌 𝗌𝗉𝗅𝗂𝗍 𝖻𝗒 𝖺 𝖼𝗈𝗆𝗆𝖺!*")
    await ctx.send(f"🍰 𝖨 𝖼𝗁𝗈𝗈𝗌𝖾... **{random.choice(options).strip()}**!")


# --- CATEGORY: MODERATION ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    """🧼 Delete a specific amount of clutter messages."""
    await ctx.channel.purge(limit=amount + 1)
    embed = discord.Embed(description=f"🧹 *𝖲𝗐𝖾𝗉𝗍 𝖺𝗐𝖺𝗒 {amount} 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗂𝗇𝗍𝗈 𝗍𝗁𝖾 clouds!*", color=PASTEL_PINK)
    await ctx.send(embed=embed, delete_after=3)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "𝖭𝗈 𝗋𝖾𝖺𝗌𝗈𝗇 𝗀𝗂𝗏𝖾𝗇."):
    """🩰 Kick a user gracefully."""
    await member.kick(reason=reason)
    embed = discord.Embed(description=f"🍃 *{member.name} 𝗐𝖺𝗌 𝗀𝖾𝗇𝗍𝗅𝗒 remove𝖽. 𝖱𝖾𝖺𝗌𝗈𝗇: {reason}*", color=PASTEL_BLUE)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "𝖭𝗈 𝗋𝖾𝖺𝗌𝗈𝗇 𝗀𝗂𝗏𝖾𝗇."):
    """🔨 Banish bad vibes."""
    await member.ban(reason=reason)
    embed = discord.Embed(description=f"🪐 *{member.name} 𝗐𝖺𝗌 𝖻𝖺𝗇𝗂𝗌𝗁𝖾𝖽 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝗋𝖾𝖺𝗅𝗆. 𝖱𝖾𝖺𝗌𝗈𝗇: {reason}*", color=PASTEL_PINK)
    await ctx.send(embed=embed)


# --- ERROR HANDLING ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🥞 *𝖮𝗈𝗉𝗌! 𝖸𝗈𝗎 𝖽𝗈𝗇'𝗍 𝗁𝖺𝗏𝖾 𝗍𝗁𝖾 𝗆𝖺𝗀𝗂𝖼 𝗉𝗈𝗐𝖾𝗋𝗌 (𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇𝗌) 𝗍𝗈 𝖽𝗈 𝗍𝗁𝖺𝗍.*")

# 4. Run the Bot (Paste your token below)
bot.run(TOKEN)
