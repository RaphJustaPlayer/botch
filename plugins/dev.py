import discord
from discord.ext import commands
import json
import traceback

stfu_error_cog = False


def victoire(posteur, winner, score):
    embed = discord.Embed(
        title="Victoire",
        description=f"{posteur.name}#{posteur.discriminator} \u2192 {winner.name}#{winner.discriminator}",
        color=discord.Colour.green()
    )
    embed.add_field(name="Nombre de victoires :", value=f"{score} \u2192 {score}")
    embed.set_footer(text=f"Winner ID:{winner.id} • Ex-posteur ID: {posteur.id}")
    return embed


def kop1(posteur, kop1):
    embed = discord.Embed(
        title="Kop1",
        description=f"{posteur.name}#{posteur.discriminator} \u2192 {kop1.name}#{kop1.discriminator}",
        color=discord.Colour.green()
    )
    embed.set_footer(text=f"Kop1 ID:{kop1.id} • Ex-posteur ID: {posteur.id}")
    return embed


class Dev(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.file = "dev"
        self.log_channel = {True: 752932896683196536, False: 752561016839209055}
        self.professionel = 0

    @commands.Cog.listener()
    async def on_ready(self):
        for emoji in self.bot.emojis:
            if 'professionnel' == emoji.name:
                self.professionel = emoji

    @commands.command()
    async def reload(self, ctx, param=None):
        if ctx.author.id != 354188969472163840:
            return
        await ctx.message.delete()
        cogs = []
        if param is None:
            for cog in self.bot.cogs:
                cogs.append(cog)
            for cog in cogs:
                self.bot.reload_extension("plugins." + cog.lower())
            await ctx.send(f"All cogs reloaded")
        elif param.capitalize() in self.bot.cogs:
            self.bot.reload_extension("plugins." + param.lower())
            await ctx.send(f"{param} reloaded")
        elif param.lower() == "sb":
            self.bot.reload_extension("plugins.starbotch")
            await ctx.send(f"{param} reloaded")
        else:
            await ctx.send(f"{param} is an invalid cog")

    @commands.command()
    async def mp(self, ctx, *, pakage):
        if ctx.author.id != 354188969472163840: return
        pakage = pakage.split(" ")
        user = await self.bot.fetch_user(int(pakage[0]))
        del pakage[0]
        pakage = " ".join(pakage)
        await user.send(pakage)

    """@commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not stfu_error_cog:
            if isinstance(error, commands.errors.MissingAnyRole):
                await ctx.send("C'est des commandes de {} pas pour la plèbe".format(self.professionel))
            elif isinstance(error, commands.errors.CommandNotFound):
                pass
            elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
                await ctx.send(f"Argument manquant obligatoire`{error.param}`")
            elif isinstance(error, discord.ext.commands.errors.BadArgument):
                await ctx.send(f"Mauvais argument `{', '.join(error.args)}`")
            else:
                if self.bot.user.id != 762723841498677258:
                    channel = await self.bot.fetch_channel(732296566299426939)
                else:
                    channel = await self.bot.fetch_channel(752932896683196536)
                tr = traceback.format_exception(type(error), error, error.__traceback__)
                await channel.send(f"{error}\n```py\n{' '.join(tr)}```")
        else:
            if self.bot.user.id != 762723841498677258:
                channel = await self.bot.fetch_channel(732296566299426939)
            else:
                channel = await self.bot.fetch_channel(752932896683196536)
            tr = traceback.format_exception(type(error), error, error.__traceback__)
            await channel.send(f"{error}\n```py\n{' '.join(tr)}```")"""

    @commands.command(name="stfupls")
    async def stfupls(self, ctx):
        global stfu_error_cog
        if stfu_error_cog: stfu_error_cog = False
        else: stfu_error_cog = True
        await ctx.send(f"stfu_error_cog set to `{stfu_error_cog}`")

    @commands.command(name='data')
    async def dt(self, ctx):
        if ctx.author.id != 354188969472163840:
            return
        text = "```json\n"
        text += json.dumps(self.bot.DBA.showall(), indent=2) + '```'
        await ctx.send(text)

    @commands.command(name='test')
    async def test(self, ctx):
        if ctx.author.id != 354188969472163840:
            return


def setup(bot):
    bot.add_cog(Dev(bot))
