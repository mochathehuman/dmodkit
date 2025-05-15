# dmodkit

**dmodkit** is a lightweight, plug-and-play Discord moderation toolkit for bots using `discord.py`. It's built for speed, simplicity, and zero bloat.

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

> **Note:** This project requires the following packages:
>
> - [`discord.py`](https://pypi.org/project/discord.py/) (v2.0.0 or higher)
> - [`loggingutil`](https://github.com/mochathehuman/loggingutil) (exactly `v1.2.2`)
>
> Install them using:
>
> pip install discord.py loggingutil==1.2.2

## Quickstart

Install:
`pip install dmodkit`

Example:
```py
from discord.ext import commands
from dmodkit.core import Modkit

bot = commands.Bot(command_prefix="!")

mod = Modkit(bot, config={
    "log_channel_id": 123456789012345678  # optional
})
mod.load_all()

bot.run("YOUR_BOT_TOKEN")
```

## Logs

- Warnings: `warnings.log`
- All commands: `modkit.log`
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