import discord
from discord.ext import commands
import package
import json


class Broadcast(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.file = "broadcast"
        self.broadcastconfirm = {}  # Sous la forme int(user_id): ('sdlm', message)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Ce on_message est uniquement utilisé pour gérer le broadcast administrateur.
        Il faudrait déplacer toute la sectio de braodcast dans un cogs à part entière plus tard.
        """
        if self.bot.test: return await self.bot.process_commands(message)  # Check si le bot est sous token test
        if message.content == 'confirm':  # Le confirm est utilisé pour le système de broadcast

            if message.author.id in self.broadcastconfirm and self.broadcastconfirm[message.author.id][0] == 'sdlm':
                # Vérifie si la personne qui envoit le confirm est bien celui qui a envoyer le broadcast et si le message est bien enregistré.
                for user_id in self.bot.DBA.showall():  # Récupère l'id de toute les personnes du leaderboard
                    try:
                        user = await self.bot.fetch_user(int(user_id))  # Fetch chaque personne du leaderboard
                        await user.send(self.broadcastconfirm[message.author.id][1])  # Envoit le message de broadcast
                    except:
                        pass  # Juste au cas où le membre a bloquer ses mp
                self.broadcastconfirm.pop(message.author.id, None)  # Retire le message du dict

        elif message.content == 'cancel' and message.author.id in self.broadcastconfirm:
            # Si le broadcaster cancel son message
            self.broadcastconfirm.pop(message.author.id, None)  # Retire le message du dict
            await message.channel.send("Message annulé")  # Feedback

    # START OF BROADCAST GROUP
    @commands.group(name="broadcast", aliases=['bc'])
    async def _broadcast_groupe(self, ctx):
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
    async def _broadcast_annonce(self, ctx):
        if ctx.author.id != 354188969472163840:
            return
        embed = discord.Embed(
            title='***BOTCH NEWS !***',
            description='C drole putain',
            color=discord.Colour.from_rgb(255, 0, 21)
        )
        await ctx.send(embed=embed)

    @_broadcast_groupe.command(name='sdlm')
    async def _broadcast_sdlm(self, ctx, *, message):
        await ctx.send('Le message que vous vous apretez a envoyé est :'
                       f'\n```{message}```'
                       '\n\nTapez `confirm` pour envoyer le message.')
        self.broadcastconfirm[ctx.author.id] = ('sdlm', message)

    @_broadcast_groupe.command(name='example', aliases=["ex"])
    async def _broadcast_sexample(self, ctx):
        example = {"title": "SALUT LES ***B-B-B-BOTCHS*** !!!",
                   "description": "... ÉNORME !",
                   "image": "écrire False si pas utilisé, sinon lien vers l'image",
                   "thumbnail": "écrire False si pas utilisé, sinon lien vers l'image",
                   "color": "rouge botch par défaut et flm de coder les autres couleurs pour le moment"}
        await ctx.send("```json\n{}```".format(json.dumps(example, indent=2, ensure_ascii=False)))
    # END OF BROADCAST GROUP


def setup(bot):
    bot.add_cog(Broadcast(bot))
