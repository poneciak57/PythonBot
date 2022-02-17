import asyncio
import datetime as dt
import re
import typing as t
from decouple import config

import bot.engine.exceptions as ex
import bot.engine.queue as queue

import discord
import wavelink
from discord.ext import commands

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue.Queue()

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise ex.AlreadyConnectedToChannel
        if (channel := getattr(ctx.author.voice, "channel", channel)) is None:
            raise ex.NoVoiceChannel

        await super().connect(channel.id)
        return channel

    async def disconnection(self):
        try:
            await self.destroy()
        except KeyError:
            pass

    async def add_tracks(self, ctx, tracks):
        if not tracks:
            raise ex.NoTracksFound

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add(*tracks.tracks)
        elif len(tracks) == 1:
            self.queue.add(tracks[0])
            await ctx.send(f"Added {tracks[0].title} to the queue")
        else:
            if (track := await self.choose_track(ctx, tracks)) is not None:
                self.queue.add(track)
                await ctx.send(f"Added {track.title} to the queue.")

        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def choose_track(self, ctx, tracks):
        def _check(r, u):
            return(
                r.emoji in OPTIONS.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )
        embed = discord.Embed(
            title="Choose a song",
            description=(
                "\n".join(
                    f"**[{i+1}]**{t.title} ({t.length//60000}:{str(t.length%60).zfill(2)})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()

        )
        embed.set_author(name="Query Results")
        embed.set_footer(
            text=f"Invoked by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        msg = await ctx.send(embed=embed)
        for emoji in list(OPTIONS.keys())[:min(len(tracks), len(OPTIONS))]:
            await msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
        else:
            await msg.delete()
            return tracks[OPTIONS[reaction.emoji]]

    def clear_queue(self):
        self.queue.clear()

    async def start_playback(self):
        await self.play(self.queue.first_track)

    async def advance(self):
        try:
            if (track := self.queue.get_next_track()) is not None:
                await self.play(track)
        except ex.QueueIsEmpty:
            pass


class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.get_player(member.guild).disconnection()

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f"Wavelink node `{node.identifier}` ready")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        await payload.player.advance()

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Music commands are not avaible in DMs.")
            return False
        return True

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": config('LAVALINK_PASSWORD'),
                "identifier": "MAIN",
                "region": "europe"
            }
        }
        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj) -> Player:
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    @commands.command(name="connect", aliases=["join"])
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        await ctx.send(f"Connected to {channel.name}.")

    @commands.command(name="disconnect", aliases=["leave"])
    async def disconnect_command(self, ctx):
        player = self.get_player(ctx)
        await player.disconnection()
        await ctx.send("Disconnect.")

    @connect_command.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, ex.AlreadyConnectedToChannel):
            await ctx.send("Already connected to a voice channel.")
        elif isinstance(exc, ex.NoVoiceChannel):
            await ctx.send("No suitable voice channel was found.")
        await self.disconnect_command(ctx)

    @commands.command(name="play")
    async def play_command(self, ctx, *, track: t.Optional[str]):
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if track is None:
            pass
        else:
            track = track.strip("<>")
            if not re.match(URL_REGEX, track):
                track = f"ytsearch:{track}"
            await player.add_tracks(ctx, await self.wavelink.get_tracks(track))

    @commands.command(name="clear")
    async def clear_command(self, ctx):
        player = self.get_player(ctx)
        player.clear_queue()
        await ctx.send("Queue cleared.")

    @commands.command(name="queue", aliases=["ls", "list"])
    async def queue_command(self, ctx, show: t.Optional[int] = 10):
        player = self.get_player(ctx)
        if player.queue.is_empty:
            raise ex.QueueIsEmpty

        embed = discord.Embed(
            title="Queue",
            description=f"Showing up to next {show} tracks.",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Query Results")
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        if upcoming := player.queue.upcoming[:show]:
            embed.add_field(
                name="Next up",
                value="\n".join(f"**[{i+1}]** {upcoming[i].title} ({upcoming[i].length//60000}:{str(upcoming[i].length%60).zfill(2)})" for i in range(
                    len(upcoming)-1, -1, -1)),
                inline=False
            )
        embed.add_field(name="Currently playing",
                        value=player.queue.current_track.title, inline=False)
        await ctx.send(embed=embed)

    @ queue_command.error
    async def queue_command_error(self, ctx, exc):
        print("queue command error")
        if isinstance(exc, ex.QueueIsEmpty):
            await ctx.send("The queue is empty.")

    @ commands.command(name="skip", aliases=["next"])
    async def skip_command(self, ctx):
        player = self.get_player(ctx)
        await player.stop()
        await ctx.send("Skipped current song.")


def setup(bot):
    bot.add_cog(Music(bot))
