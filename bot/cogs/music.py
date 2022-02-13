from distutils import command
from wsgiref.util import request_uri
import discord
import wavelink
from discord.ext import commands


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.wavelink = wavelink.Client(bot=bot) #its not working with current wavelink version i guess
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
            host='123.0.0.1',  # put there http when lavalink hosted i believe
            port=2333,
            https=False,  # change to true when lavalink is hosted i guess
            password='youshallnotpass')

    def get_player(self, obj):
        if isinstance(obj, command.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)


def setup(bot):
    bot.add_cog(Music(bot))
