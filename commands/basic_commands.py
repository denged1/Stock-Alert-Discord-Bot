
from discord.ext import commands


################ Commands  ################
class BasicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='hello', help='Replies with a greeting')
    async def hello(self, ctx):
        await ctx.send('Lebron has entered the court')


    @commands.command(name='setchannel', help='Sets the current channel for daily alerts')
    @commands.has_permissions(administrator=True)
    async def setchannel(self, ctx):
        """Registers the current channel as the one for daily alerts."""
        with open("channels.txt", "a") as f:
            f.write(f"{ctx.guild.id},{ctx.channel.id}\n")
        await ctx.send("This channel has been set for daily alerts!")

    @commands.command(name='removechannel', help='Removes the current channel from daily alerts')
    @commands.has_permissions(administrator=True)
    async def removechannel(self, ctx):
        """Removes the current channel from the daily alerts list."""
        lines = []
        with open("channels.txt", "r") as f:
            lines = f.readlines()
        with open("channels.txt", "w") as f:
            for line in lines:
                if line.strip() != f"{ctx.guild.id},{ctx.channel.id}":
                    f.write(line)
        await ctx.send("This channel has been removed from daily alerts!")

    @commands.command(name='fud', help='self explanatory')
    async def fud(self, ctx):
        await ctx.send("Okay okay okay, I need the price to go up. I can't take this anymore. Every day, I'm checking the price and it's dipping. Every day, I check the price - bad price. I can't take this anymore, man. I have overinvested - by a lot. It is what it is. I need the price to go up. Can devs do something?")

async def setup(bot: commands.Bot):
    await bot.add_cog(BasicCommands(bot))
