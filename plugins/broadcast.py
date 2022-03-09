import discord
from discord.ext import commands
import package
import json
import main

def make_broadcast_embed(package):
    embed = discord.Embed(
        title=package['title'],
        description=package['description'],
        color=discord.Colour.from_rgb(255, 0, 21)
    )
    if 'thumbnail' in package:
        embed.set_thumbnail(url=package['thumbnail'])
    if 'image' in package:
        embed.set_image(url=package['image'])
    return embed


class Broadcast(commands.Cog):

    def __init__(self, bot: main.BOTCH):
        self.bot = bot
        self.file = "broadcast"
        self.broadcastconfirm = {}  # Sous la forme int(user_id): ('sdlm', message)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.bot.test: return await self.bot.process_commands(message)  # Check si le bot est sous token test
        if message.content == 'confirm' and message.author.id in self.broadcastconfirm:  # Le confirm est utilisé pour le système de broadcast
            if self.broadcastconfirm[message.author.id][0] == 'sdlm':
                # Vérifie si la personne qui envoit le confirm est bien celui qui a envoyer le broadcast et si le message est bien enregistré.
                cant_send = 0
                for user_id in self.bot.DBA.showall():  # Récupère l'id de toute les personnes du leaderboard
                    try:
                        user = await self.bot.fetch_user(int(user_id))  # Fetch chaque personne du leaderboard
                        await user.send(embed=self.broadcastconfirm[message.author.id][1])  # Envoit le message de broadcast
                    except:
                        cant_send += 1  # Juste au cas où le membre a bloquer ses mp
                self.broadcastconfirm.pop(message.author.id, None)  # Retire le message du dict
                await message.channel.send(f"Message envoyé à {len(self.bot.DBA.showall())-cant_send} membres")
            elif self.broadcastconfirm[message.author.id][0] == 'bnews':
                annonce_channel = await self.bot.fetch_channel(625338153640656907)
                await annonce_channel.send(f"OYEZ OYEZ @everyone, C'EST L'HEURE DES ***B-B-BOTCH NEWS !!!***",
                                           embed=self.broadcastconfirm[message.author.id][1],
                                           allowed_mentions=discord.AllowedMentions(everyone=True))

        elif message.content == 'cancel' and message.author.id in self.broadcastconfirm:
            # Si le broadcaster cancel son message
            self.broadcastconfirm.pop(message.author.id, None)  # Retire le message du dict
            await message.channel.send("Message annulé")  # Feedback

    # START OF BROADCAST GROUP
    @commands.group(name="broadcast", aliases=['bc'])
    async def _broadcast_groupe(self, ctx: discord.ext.commands.Context):
        package.is_admin(ctx.author.roles)
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Help broadcast",
                color=discord.Colour.from_rgb(255, 0, 21)
            )
            embed.add_field(name="`?broadcast sdlm <message>`",
                            value="Envoit un message à tout les participants présents dans la db du <#707639957484732466>",
                            inline=False)
            embed.add_field(name="`?broadcast annonce <message>`",
                            value="Envoit un message dans le <#625338153640656907>", inline=False)
            await ctx.send(embed=embed)

    @_broadcast_groupe.command(name='annonce')
    async def _broadcast_annonce(self, ctx, *, message: str):
        try:
            message = json.loads(message)
        except:
            return await ctx.send("Format du message incorecte")
        embed = make_broadcast_embed(message)
        await ctx.send('Le message que vous vous apretez à envoyer dans <#625338153640656907> est :', embed=embed)
        await ctx.send("Tapez `confirm` pour envoyer le message ou `cancel` pour l'annuler.")
        self.broadcastconfirm[ctx.author.id] = ('bnews', embed)

    @_broadcast_groupe.command(name='sdlm')
    async def _broadcast_sdlm(self, ctx, *, message: str):
        try:
            message = json.loads(message)
        except:
            return await ctx.send("Format du message incorecte")
        embed = make_broadcast_embed(message)
        await ctx.send('Le message que vous vous apretez à envoyer est :', embed=embed)
        await ctx.send("Tapez `confirm` pour envoyer le message ou `cancel` pour l'annuler.")
        self.broadcastconfirm[ctx.author.id] = ('sdlm', embed)

    @_broadcast_groupe.command(name='example', aliases=["ex"])
    async def _broadcast_sexample(self, ctx):
        example = {"title": "SALUT LES ***B-B-B-BOTCHS*** !!!",
                   "description": "... ÉNORME !",
                   "image": "lien vers l'image (supprimer cette ligne si pas utilisée)",
                   "thumbnail": "lien vers l'image (supprimer cette ligne si pas utilisée)"}
        embed = discord.Embed(
            title=example['title'],
            description=example['description'],
            color=discord.Colour.from_rgb(255, 0, 21)
        )

        await ctx.send("Pas obligé de remttre les ` pour rentre le message```json\n{}```Donnera".format(json.dumps(example, indent=2, ensure_ascii=False)), embed=embed)
    # END OF BROADCAST GROUP


def setup(bot):
    bot.add_cog(Broadcast(bot))
