import typing as t

import discord
import wavelink
from discord.ext import commands


class Player(wavelink.Player):
    def __init__(self, dj: discord.Member):
        self.dj = dj


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.wavelink = wavelink.Client(bot=bot) #its not working with current wavelink version i guess/
        self.bot.loop.create_task(self.start_nodes())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                pass  # disconnect bot

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node):
        print(f"Wavelink node `{node.identifier}` ready")

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Music commands are not avaible in DMs.")
            return False
        return True

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        await wavelink.NodePool.create_node(
            bot=self.bot,
            host='127.0.0.1',
            port=2333,
            password='youshallnotpass')

    @commands.command(name="connect", aliases=["join"])
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        try:
            channel = channel or ctx.author.voice.channel
        except AttributeError:
            return await ctx.send('No voice channel to connect to. Please either provide one or join one.')

        player = Player(dj=ctx.author)
        vc: Player = await channel.connect(cls=player)

        return vc


def setup(bot):
    bot.add_cog(Music(bot))
