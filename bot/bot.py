from pathlib import Path

from decouple import config

import discord
from discord.ext import commands


class MusicBot(commands.Bot):
    def __init__(self):
        self._cogs = [p.stem for p in Path(".").glob("./bot/cogs/*.py")]
        super().__init__(
            command_prefix=self.prefix,
            case_insensitive=True,
            intents=discord.Intents.all()
        )

    def setup(self):
        print("Running setup...")
        for cog in self._cogs:
            self.load_extension(f"bot.cogs.{cog}")
            print(f"Loaded `{cog}` cog.")
        print("Setup completed.")

    def run(self):
        self.setup()
        TOKEN = config('TOKEN')
        print("Running bot...")

        super().run(TOKEN, reconnect=True)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)

    # Error handling
    async def on_error(self, err, *args, **kwargs):
        raise

    async def on_command_error(self, ctx, exc):
        raise getattr(exc, "original", exc)

    # some events with prints
    async def prefix(self, bot, msg):
        return commands.when_mentioned_or("/")(bot, msg)

    async def on_ready(self):
        self.client_id = (await self.application_info()).id
        print("Bot ready.")

    async def on_connection(self):
        print(f"Connected to Discord Latency:{self.latency *1000:,.0f}ms.")

    async def on_resumed(self):
        print("Bot resumed.")

    async def on_disconnect(self):
        print("Bot dicsonnected.")

    async def shutdown(self):
        print("Closing discord connection...")
        await super().close()

    async def close(self):
        print("Closing on keyboard interrupt")
        await self.shutdown()
