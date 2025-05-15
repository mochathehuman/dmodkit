import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from loggingutil import LogFile, LogLevel
import atexit

logger = LogFile(
    filename="modkit.log",
    verbose=True,
    mode="text",
    include_timestamp=True,
    compress=False
)

atexit.register(lambda: logger.flush())

class Modkit:
    def __init__(self, client: discord.Client, tree: app_commands.CommandTree, *, config=None):
        self.client = client
        self.tree = tree
        self.warns = {}
        self.sniped = {}
        self.config = config or {}
        self.log_channel_id = self.config.get("log_channel_id")

    def kick(self):
        @self.tree.command(name="kick", description="Kick a member")
        @app_commands.checks.has_permissions(kick_members=True)
        async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
            await member.kick(reason=reason)
            await interaction.response.send_message(f'Kicked {member.mention} | Reason: {reason}')

    def ban(self):
        @self.tree.command(name="ban", description="Ban a member")
        @app_commands.checks.has_permissions(ban_members=True)
        async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
            await member.ban(reason=reason)
            await interaction.response.send_message(f'Banned {member.mention} | Reason: {reason}')

    def warn(self):
        @self.tree.command(name="warn", description="Warn a member")
        async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
            self.warns.setdefault(member.id, []).append(reason)
            await interaction.response.send_message(f'Warned {member.mention} | Reason: {reason}')
            with open("warnings.log", "a") as f:
                f.write(f"{interaction.guild.name} | {interaction.user} warned {member} | Reason: {reason}\n")

        @self.tree.command(name="warnings", description="Check a member's warnings")
        async def warnings(interaction: discord.Interaction, member: discord.Member):
            w = self.warns.get(member.id, [])
            msg = "\n".join([f"{i+1}. {r}" for i, r in enumerate(w)]) or "No warnings"
            await interaction.response.send_message(f'{member.mention} has {len(w)} warning(s):\n{msg}')

    def mute(self):
        @self.tree.command(name="mute", description="Mute a member")
        @app_commands.checks.has_permissions(moderate_members=True)
        async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int = 5):
            until = discord.utils.utcnow() + timedelta(minutes=minutes)
            await member.timeout(until, reason=f"Muted by {interaction.user}")
            await interaction.response.send_message(f'{member.mention} muted for {minutes} minute(s).')

        @self.tree.command(name="unmute", description="Unmute a member")
        @app_commands.checks.has_permissions(moderate_members=True)
        async def unmute(interaction: discord.Interaction, member: discord.Member):
            await member.timeout(None)
            await interaction.response.send_message(f'{member.mention} unmuted.')

    def purge(self):
        @self.tree.command(name="purge", description="Purge messages")
        @app_commands.checks.has_permissions(manage_messages=True)
        async def purge(interaction: discord.Interaction, limit: int = 10):
            deleted = await interaction.channel.purge(limit=limit)
            await interaction.response.send_message(f'Deleted {len(deleted)} messages.', ephemeral=True)

    def slowmode(self):
        @self.tree.command(name="slowmode", description="Set slowmode delay")
        @app_commands.checks.has_permissions(manage_channels=True)
        async def slowmode(interaction: discord.Interaction, seconds: int = 0):
            await interaction.channel.edit(slowmode_delay=seconds)
            await interaction.response.send_message(f'Slowmode set to {seconds} seconds.')

    def lock(self):
        @self.tree.command(name="lock", description="Lock the channel")
        @app_commands.checks.has_permissions(manage_channels=True)
        async def lock(interaction: discord.Interaction):
            await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
            await interaction.response.send_message("Channel locked.")

        @self.tree.command(name="unlock", description="Unlock the channel")
        @app_commands.checks.has_permissions(manage_channels=True)
        async def unlock(interaction: discord.Interaction):
            await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
            await interaction.response.send_message("Channel unlocked.")

    def nick(self):
        @self.tree.command(name="nick", description="Change nickname")
        @app_commands.checks.has_permissions(manage_nicknames=True)
        async def nick(interaction: discord.Interaction, member: discord.Member, nickname: str = None):
            await member.edit(nick=nickname)
            await interaction.response.send_message(f'Nickname set for {member.mention}.')

    def strike(self):
        @self.tree.command(name="strike", description="Give a strike")
        async def strike(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
            self.warns.setdefault(member.id, []).append(reason)
            count = len(self.warns[member.id])
            await interaction.response.send_message(f'Strike {count} for {member.mention} | Reason: {reason}')
            if count >= 3:
                await member.kick(reason="3 strikes rule")
                await interaction.followup.send(f'{member.mention} kicked after 3 strikes.')

    def snipe(self):
        @self.client.event
        async def on_message_delete(message):
            self.sniped[message.channel.id] = (message.content, message.author)

        @self.tree.command(name="snipe", description="Show last deleted message")
        async def snipe(interaction: discord.Interaction):
            msg = self.sniped.get(interaction.channel.id)
            if msg:
                await interaction.response.send_message(f'Last deleted: "{msg[0]}" (by {msg[1]})')
            else:
                await interaction.response.send_message('Nothing to snipe.')

    def modlog(self):
        @self.client.event
        async def on_command(ctx):
            msg = f"{ctx.author} used '{ctx.command}' in #{ctx.channel} (guild: {ctx.guild})"
            logger.log(msg, level=LogLevel.INFO, tag="COMMAND")

        @self.client.event
        async def on_command_error(ctx, error):
            msg = f"Error from '{ctx.command}' by {ctx.author}: {str(error)}"
            logger.log_exception(error, tag="CMD_ERROR")

    def load_all(self):
        self.kick()
        self.ban()
        self.warn()
        self.mute()
        self.purge()
        self.slowmode()
        self.lock()
        self.nick()
        self.strike()
        self.snipe()
        if self.log_channel_id:
            self.modlog()