# modr

**modr** is a lightweight, plug-and-play Discord moderation toolkit for bots using `discord.py`. It's built for speed, simplicity, and zero bloat.

## Features

- Kick / Ban
- Warns & Strikes (with auto-kick on 3 strikes)
- Mute (with timeout) / Unmute
- Message Purge
- Channel Lock / Unlock
- Slowmode Control
- Nickname Changes
- Snipe (recover last deleted message)
- Logs all commands via [loggingutil](https://github.com/mochathehuman/loggingutil)
- Warning history saved to `warnings.log`

## Quickstart

Install:
`pip install discord.py`
`pip install loggingutil==1.2.2`

Example:
```py
from discord.ext import commands
from modr.core import Modr

bot = commands.Bot(command_prefix="!")

mod = Modr(bot, config={
    "log_channel_id": 123456789012345678  # optional
})
mod.load_all()

bot.run("YOUR_BOT_TOKEN")
```
## Logs

- Warnings: `warnings.log`
- All commands: `modr.log` (uses loggingutil)
- Log rotation, compression, and buffer control supported

## Planned

- Slash command support
- Context menu moderation
- AutoMod keyword filters
- Persistent user notes

## Permissions

Make sure your bot has the following:
- Kick Members
- Ban Members
- Manage Messages
- Manage Nicknames
- Moderate Members