from discord.ext import commands
import requests
import json
import discord


async def get_da_meme():
    r = requests.get("https://meme-api.herokuapp.com/gimme")
    return json.loads(str(r.text))


class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = "memes"

    @commands.command(name='meme')
    async def post_meme(self, ctx):
        package = await get_da_meme()
        embed = discord.Embed(
            title=package["title"],
            color=discord.Colour.from_rgb(255, 0, 21)
        )
        embed.set_image(url=package["url"])
        embed.set_author(name=package["author"], url=package["postLink"])
        embed.set_footer(text=f"{package['ups']} upvotes")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Memes(bot))