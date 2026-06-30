"""
ᏖᏕᏕ — welcome & tickets cog.
Welcome/leave messages are simple text templates supporting {member} and {guild}.
Tickets use a persistent button panel; opening a ticket creates a private channel.
"""

import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from config import COLORS, EMOJI, FOOTER_TEXT


def wt_embed(title, description, color=COLORS["tickets"]):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=FOOTER_TEXT)
    return embed


def render_template(template: str, member: discord.Member) -> str:
    return (template or "Welcome {member} to {guild}! 🎀").replace(
        "{member}", member.mention
    ).replace("{guild}", member.guild.name)


class TicketPanelView(discord.ui.View):
    """Persistent view: the 'Open Ticket' button posted by /ticketpanel."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="tss:open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot = interaction.client
        cfg = await bot.db.get_ticket_config(interaction.guild.id)
        if not cfg or not cfg["support_role_id"]:
            await interaction.response.send_message(
                embed=wt_embed(f"{EMOJI['cross']} Not configured", "Tickets aren't set up yet. Ask an admin to run `/ticketsetup`.", COLORS["error"]),
                ephemeral=True,
            )
            return

        guild = interaction.guild
        category = guild.get_channel(cfg["category_id"]) if cfg["category_id"] else None
        support_role = guild.get_role(cfg["support_role_id"])

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}"[:90],
            category=category,
            overwrites=overwrites,
            reason=f"Ticket opened by {interaction.user}",
        )
        await bot.db.create_ticket(channel.id, guild.id, interaction.user.id)

        embed = wt_embed(
            f"{EMOJI['ticket']} Ticket opened",
            f"Hi {interaction.user.mention}! Support will be with you shortly.\n"
            f"Use the button below to close this ticket when you're done.",
        )
        await channel.send(content=support_role.mention if support_role else None, embed=embed, view=CloseTicketView())
        await interaction.response.send_message(
            embed=wt_embed(f"{EMOJI['sparkle']} Ticket created", f"Your ticket: {channel.mention}"),
            ephemeral=True,
        )


class CloseTicketView(discord.ui.View):
    """Persistent view: the 'Close Ticket' button inside a ticket channel."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="tss:close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot = interaction.client
        await bot.db.close_ticket(interaction.channel.id)
        await interaction.response.send_message(embed=wt_embed(f"{EMOJI['lock']} Closing...", "This ticket will close in 5 seconds."))
        await asyncio.sleep(5)
        await interaction.channel.delete(reason="Ticket closed")


class WelcomeTickets(commands.Cog):
    """🎫 Welcome & Tickets — greet new members and run a support desk."""

    def __init__(self, bot):
        self.bot = bot
        bot.add_view(TicketPanelView())
        bot.add_view(CloseTicketView())

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        cfg = await self.bot.db.get_welcome_config(member.guild.id)
        if not cfg or not cfg["welcome_channel_id"]:
            return
        channel = member.guild.get_channel(cfg["welcome_channel_id"])
        if not channel:
            return
        embed = wt_embed(f"{EMOJI['flower']} Welcome!", render_template(cfg["welcome_message"], member))
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(content=member.mention, embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        cfg = await self.bot.db.get_welcome_config(member.guild.id)
        if not cfg or not cfg["leave_channel_id"]:
            return
        channel = member.guild.get_channel(cfg["leave_channel_id"])
        if not channel:
            return
        embed = wt_embed(f"{EMOJI['cross']} Goodbye", render_template(cfg["leave_message"] or "{member} has left {guild}.", member))
        await channel.send(embed=embed)

    # ---------- config commands ----------
    @commands.hybrid_command(name="setwelcome", description="(Admin) Set the welcome channel and message.")
    @app_commands.describe(channel="Channel to post welcomes in", message="Use {member} and {guild} as placeholders")
    @commands.has_permissions(manage_guild=True)
    async def setwelcome(self, ctx, channel: discord.TextChannel, *, message: str = "Welcome {member} to {guild}! 🎀"):
        await self.bot.db.set_welcome(ctx.guild.id, channel.id, message)
        await ctx.send(embed=wt_embed(f"{EMOJI['sparkle']} Saved", f"Welcome messages will be posted in {channel.mention}."))

    @commands.hybrid_command(name="setleave", description="(Admin) Set the leave channel and message.")
    @app_commands.describe(channel="Channel to post leave messages in", message="Use {member} and {guild} as placeholders")
    @commands.has_permissions(manage_guild=True)
    async def setleave(self, ctx, channel: discord.TextChannel, *, message: str = "{member} has left {guild}."):
        await self.bot.db.set_leave(ctx.guild.id, channel.id, message)
        await ctx.send(embed=wt_embed(f"{EMOJI['sparkle']} Saved", f"Leave messages will be posted in {channel.mention}."))

    @commands.hybrid_command(name="testwelcome", description="(Admin) Preview the welcome message.")
    @commands.has_permissions(manage_guild=True)
    async def testwelcome(self, ctx):
        cfg = await self.bot.db.get_welcome_config(ctx.guild.id)
        if not cfg or not cfg["welcome_message"]:
            await ctx.send(embed=wt_embed(f"{EMOJI['cross']} Not set", "Run `/setwelcome` first.", COLORS["error"]))
            return
        await ctx.send(embed=wt_embed(f"{EMOJI['flower']} Preview", render_template(cfg["welcome_message"], ctx.author)))

    # ---------- ticket config ----------
    @commands.hybrid_command(name="ticketsetup", description="(Admin) Configure the ticket system.")
    @app_commands.describe(support_role="Role that can see tickets", category="Category to create ticket channels in", log_channel="Optional log channel")
    @commands.has_permissions(manage_guild=True)
    async def ticketsetup(self, ctx, support_role: discord.Role, category: discord.CategoryChannel = None, log_channel: discord.TextChannel = None):
        await self.bot.db.set_ticket_config(
            ctx.guild.id,
            support_role_id=support_role.id,
            category_id=category.id if category else None,
            log_channel_id=log_channel.id if log_channel else None,
        )
        await ctx.send(embed=wt_embed(f"{EMOJI['sparkle']} Configured", "Ticket system is ready! Use `/ticketpanel` to post the button."))

    @commands.hybrid_command(name="ticketpanel", description="(Admin) Post the 'Open Ticket' button in this channel.")
    @commands.has_permissions(manage_guild=True)
    async def ticketpanel(self, ctx):
        embed = wt_embed(f"{EMOJI['ticket']} Need help?", "Click the button below to open a private support ticket! 🎫")
        await ctx.send(embed=embed, view=TicketPanelView())

    @commands.hybrid_command(name="addtoticket", description="Add a member to the current ticket.")
    @app_commands.describe(member="Member to add")
    async def addtoticket(self, ctx, member: discord.Member):
        ticket = await self.bot.db.get_ticket(ctx.channel.id)
        if not ticket:
            await ctx.send(embed=wt_embed(f"{EMOJI['cross']} Not a ticket", "This isn't a ticket channel.", COLORS["error"]))
            return
        await ctx.channel.set_permissions(member, view_channel=True, send_messages=True)
        await ctx.send(embed=wt_embed(f"{EMOJI['sparkle']} Added", f"{member.mention} can now see this ticket."))

    @commands.hybrid_command(name="closeticket", description="Close the current ticket.")
    async def closeticket(self, ctx):
        ticket = await self.bot.db.get_ticket(ctx.channel.id)
        if not ticket:
            await ctx.send(embed=wt_embed(f"{EMOJI['cross']} Not a ticket", "This isn't a ticket channel.", COLORS["error"]))
            return
        await self.bot.db.close_ticket(ctx.channel.id)
        await ctx.send(embed=wt_embed(f"{EMOJI['lock']} Closing...", "This ticket will close in 5 seconds."))
        await asyncio.sleep(5)
        await ctx.channel.delete(reason="Ticket closed")


async def setup(bot):
    await bot.add_cog(WelcomeTickets(bot))
