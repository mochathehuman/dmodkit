import discord
from discord.ext import commands
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

atexit.register(lambda: logger.flush()) # flush logs prior to stop

class Modkit:
    def __init__(self, bot, *, config=None):
        self.bot = bot
        self.warns = {}
        self.sniped = {}
        self.config = config or {}
        self.log_channel_id = self.config.get("log_channel_id")

    def kick(self):
        @self.bot.command()
        @commands.has_permissions(kick_members=True)
        async def kick(ctx, member: discord.Member, *, reason=None):
            await member.kick(reason=reason)
            await ctx.send(f'Kicked {member.mention} | Reason: {reason or "None"}')

    def ban(self):
        @self.bot.command()
        @commands.has_permissions(ban_members=True)
        async def ban(ctx, member: discord.Member, *, reason=None):
            await member.ban(reason=reason)
            await ctx.send(f'Banned {member.mention} | Reason: {reason or "None"}')

    def warn(self):
        @self.bot.command()
        async def warn(ctx, member: discord.Member, *, reason=None):
            self.warns.setdefault(member.id, []).append(reason or "No reason")
            await ctx.send(f'Warned {member.mention} | Reason: {reason or "No reason"}')
            with open("warnings.log", "a") as f:
                f.write(f"{ctx.guild.name} | {ctx.author} warned {member} | Reason: {reason or 'No reason'}\n")

        @self.bot.command()
        async def warnings(ctx, member: discord.Member):
            w = self.warns.get(member.id, [])
            msg = "\n".join([f"{i+1}. {r}" for i, r in enumerate(w)]) or "No warnings"
            await ctx.send(f'{member.mention} has {len(w)} warning(s):\n{msg}')

    def mute(self):
        @self.bot.command()
        @commands.has_permissions(moderate_members=True)
        async def mute(ctx, member: discord.Member, minutes: int = 5):
            until = discord.utils.utcnow() + timedelta(minutes=minutes)
            await member.timeout(until, reason=f"Muted by {ctx.author}")
            await ctx.send(f'{member.mention} muted for {minutes} minute(s).')

        @self.bot.command()
        @commands.has_permissions(moderate_members=True)
        async def unmute(ctx, member: discord.Member):
            await member.timeout(None)
            await ctx.send(f'{member.mention} unmuted.')

    def purge(self):
        @self.bot.command()
        @commands.has_permissions(manage_messages=True)
        async def purge(ctx, limit: int = 10):
            deleted = await ctx.channel.purge(limit=limit)
            await ctx.send(f'Deleted {len(deleted)} messages.', delete_after=3)

    def slowmode(self):
        @self.bot.command()
        @commands.has_permissions(manage_channels=True)
        async def slowmode(ctx, seconds: int = 0):
            await ctx.channel.edit(slowmode_delay=seconds)
            await ctx.send(f'Slowmode set to {seconds} seconds.')

    def lock(self):
        @self.bot.command()
        @commands.has_permissions(manage_channels=True)
        async def lock(ctx):
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
            await ctx.send("Channel locked.")

        @self.bot.command()
        @commands.has_permissions(manage_channels=True)
        async def unlock(ctx):
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
            await ctx.send("Channel unlocked.")

    def nick(self):
        @self.bot.command()
        @commands.has_permissions(manage_nicknames=True)
        async def nick(ctx, member: discord.Member, *, nickname=None):
            await member.edit(nick=nickname)
            await ctx.send(f'Nickname set for {member.mention}.')

    def strike(self):
        @self.bot.command()
        async def strike(ctx, member: discord.Member, *, reason=None):
            self.warns.setdefault(member.id, []).append(reason or "No reason")
            count = len(self.warns[member.id])
            await ctx.send(f'Strike {count} for {member.mention} | Reason: {reason or "No reason"}')
            if count >= 3:
                await member.kick(reason="3 strikes rule")
                await ctx.send(f'{member.mention} kicked after 3 strikes.')

    def snipe(self):
        @self.bot.event
        async def on_message_delete(message):
            self.sniped[message.channel.id] = (message.content, message.author)

        @self.bot.command()
        async def snipe(ctx):
            msg = self.sniped.get(ctx.channel.id)
            if msg:
                await ctx.send(f'Last deleted: "{msg[0]}" (by {msg[1]})')
            else:
                await ctx.send('Nothing to snipe.')

    def modlog(self):
        @self.bot.event
        async def on_command(ctx):
            msg = f"{ctx.author} used '{ctx.command}' in #{ctx.channel} (guild: {ctx.guild})"
            logger.log(msg, level=LogLevel.INFO, tag="COMMAND")

        @self.bot.event
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