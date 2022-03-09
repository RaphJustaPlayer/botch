import discord
from discord.ext import commands
from discord.utils import get
import package
import os
import json
import main


def report_embed(message):  # Génère l'embed de report
    embed = discord.Embed(
        timestamp=message.created_at,
        colour=discord.Colour.red(),
        description=message.content
    )
    embed.set_author(name=f'{message.author.name}#{message.author.discriminator}',
                     icon_url=message.author.avatar_url_as(static_format='jpg'))
    embed.set_footer(text=f"Author ID:{message.author.id} • Message ID: {message.id}")
    if len(message.attachments) != 0: embed.set_image(url=message.attachments[0].url)
    return embed


class Admin(commands.Cog):
    """
    Admin comprend toute les commandes administrateur effectuable avec le BOT(CH) ainsi que qu'autre fonction automatisées

    EVENTS:
        - on_message: utilisé pour confirmer et/ou annuler les actions a choix iréversible tel que les broadcasts et les charge de backup
        - on_raw_reaction_add: utilisé pour le repport de message à la modération en réagissant avec ❗ sous le message

    COMMANDS:
        - post(ctx): renvoit le contenu du message du contexte

        ADMIN CORE:
            - _admin_core(ctx): message d'aide afficher quand `?admin` est invoqué seul. Si pas admin :raise MissingAnyRole
            - _shutdown(ctx): éteind le BOT(CH) (salement parceque j'éteind pas les loops... grosse flemme et sa sert a pas grand chose)
            - _info(ctx): renvoit un embed contenant la desc de la guild,
                                                     le nombre de personne n'ayant meme pas ouvert le serv depuis une semaine,
                                                     le nombre de personnes bannis,
                                                     chanels protégés du ❗ et ⭐

    Grosse flemme de faire le reste, y'aura des comms sur chaque commande
    """
    def __init__(self, bot: main.BOTCH):
        self.bot = bot
        self.file = "admin"
        self.report_channel = {True: 752932896683196536, False: 750634015886803025}

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Check pour le report automatique de message. C'est un bordel inomable et je crois qu'il marche plus.
        """
        if payload.emoji.name != "❗" or package.in_protected_channel(payload.channel_id): return
        # Si c'est pas l'mojis de report ou c'est dans un channel protégé on stop direct ici

        channel = await self.bot.fetch_channel(payload.channel_id)  # Récupère le channel du message
        message = await channel.fetch_message(payload.message_id)  # Récupère le message en lui même
        reaction = get(message.reactions, emoji=payload.emoji.name)  # Récupère les infos sur les réactions du message

        if reaction and reaction.count < 3: return  # Si le nombre de ❗ est inférieur a 3, alors balec

        report_channel = await self.bot.fetch_channel(self.report_channel[self.bot.test])  # Récupère le channel de report en fonction du token

        if reaction and reaction.count == 3:  # Si 3 réactions ❗ sont sur le msg alors il est report
            await channel.send("Message reporté à la modération")  # Feedback user
            await report_channel.send(embed=report_embed(message))  # Feedback modo

        elif reaction and reaction.count == 7:  # Si 7 réactions ❗ sont sur le msg alors il est delete
            await channel.send("Message suprimé du aux nombre élevé de report")  # Feedback user
            await report_channel.send(f"{message.id} a été suprimé due a un nombre élevé de report")
            return await message.delete()  # Supression du message en question

    @commands.command(name='post')
    async def post(self, ctx, *, msg):
        await ctx.message.delete()
        package.is_admin(ctx.author.roles)
        await ctx.send(msg)

    # START OF ADMIN CORE GROUP
    @commands.group(name="admin")
    async def _admin_core(self, ctx):
        await ctx.message.delete()  # Petit cleanup
        package.is_admin(ctx.author.roles)  # Vérifie si l'utilisateur est modo

        if ctx.invoked_subcommand is None:  # Si on a juste ?admin ou alors une subcommande éronée
            package.is_admin(ctx.author.roles)
            embed = discord.Embed(
                title="Help admin",
                color=discord.Colour.from_rgb(255, 0, 21)  # C'est la couleur du BOTCH ça, bien rouge, sah
            )
            # Pas besoin d'expliquer ce qui ce passe en dessous je pense que c'est obvious
            embed.add_field(name="`?admin`",
                            value="Affiche les commandes administrateur relatives au serveur", inline=False)
            embed.add_field(name="`?post <message>`",
                            value="Fait parler BOT(CH) a votre place", inline=False)
            embed.add_field(name="`?admin shutdown`",
                            value="Éteint le <@!777166173149986826>", inline=False)
            embed.add_field(name="`?admin info`",
                            value="Affiche les information administrateur sur le serveur", inline=False)
            embed.add_field(name="`?broadcast`",
                            value="Affiche les commandes administrateur relatives au message de masses", inline=False)
            embed.add_field(name="`?channel`",
                            value="Affiche les commandes administrateur relatives à la gestion individuelle des channels textuels", inline=False)
            embed.add_field(name="`?vocal`",
                            value="Affiche les commandes administrateur relatives au channels vocaux", inline=False)
            await ctx.send(embed=embed)  # Feedback user

    @_admin_core.command(name='shutdown')
    async def _shutdown(self, ctx):
        await ctx.send("Logout :cry:")  # :'c
        await ctx.bot.logout()

    @_admin_core.command(name="info")
    async def _info(self, ctx):
        embed = discord.Embed(
            title=f"{ctx.guild.name} : ADMIN",
            url="https://discord.gg/G38Ge7y",
            description=ctx.guild.description,
            color=discord.Colour.from_rgb(255, 0, 21)
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name='Innactives members count :',
                        value=f"{await ctx.guild.estimate_pruned_members(days=7)}/{ctx.guild.member_count} n'ont pas visité le serveur depuis 7 jours",
                        inline=False)
        embed.add_field(name="Bans count :",
                        value=f'{len(await ctx.guild.bans())} personnes ont été bannies de ce serveur',
                        inline=False)
        with open('config.json') as f:
            conf = json.load(f)

        channels_text = ""
        for c in conf['protected_channels']:
            channels_text += f"\n\t- <#{c}>"
        embed.add_field(name="Protected channels :",
                        value=f'Tout les messages dans les channels de cette liste sont protégés contre le ❗ et ⭐ :{channels_text}',
                        inline=False)

        return await ctx.send(embed=embed)

    @_admin_core.command(name="modifypost")
    async def _modifypost(self, ctx, msg_id, *, new_message):
        msg = await ctx.channel.fetch_message(int(msg_id))
        await msg.edit(content=new_message)

    @_admin_core.command(name="clear")
    async def _clear_messages(self, ctx, cible, nbrmessages=100):
        if "<@" not in cible: return await ctx.send("Aucune cible")
        cible = cible[3:len(cible)-1]
        cible = await ctx.guild.fetch_member(int(cible))
        async for msg in cible.history(limit=nbrmessages):
            await ctx.send(msg)
            await msg.delete()

    @_admin_core.command(name="roles")
    async def _show_roles(self, ctx):
        guild: discord.Guild = None
        for g in self.bot.guilds:
            g: discord.Guild
            if g.id == 625330528588922882:
                guild = g
        roles = guild.roles

        track = 0
        embed = discord.Embed(
            title="Roles status",
            color=discord.Colour.from_rgb(255, 0, 21)
        )
        roleignore = [723202731803672736, 723202665789653102, 636591147589828638, 723196934197608468,
                      754385790682923039, 723521427793510402, 732939404460425236, 735432443930345514, 777247006954750023,
                      717354351705849906, 775767740312977440, 704813192282374174, 636512191046221827, 949262343236366356,
                      720708059525283854, 636557010724454413]
        for role in roles:
            role: discord.Role
            if track == 12:
                await ctx.send(embed=embed)
                embed = discord.Embed(
                    title="Roles status",
                    color=discord.Colour.from_rgb(255, 0, 21)
                )
                track = 0
            elif role.id in roleignore:
                pass
            else:
                embed.add_field(name=f"{role.name if role.id != 625330528588922882 else 'Membres au total'}", value=f"{len(role.members)} personnes ayant ce role")
                track += 1

        if track != 0: await ctx.send(embed=embed)
    # END OF ADMIN CORE GROUP

    # START OF CHANNELS MANAGEMENT GROUP
    @commands.group(name='channel')
    async def channel_management_core(self, ctx):
        await ctx.message.delete()
        package.is_admin(ctx.author.roles)
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Help channel",
                color=discord.Colour.from_rgb(255, 0, 21)
            )
            embed.add_field(name="`?channel block <cible_id> (raison)`",
                            value="La personne ciblée ne peux plus écrire dans ce channel", inline=False)
            embed.add_field(name="`?channel ban <cible_id> (raison)`",
                            value="La personne ciblée ne peux plus ni écrire ni lire dans ce channel", inline=False)
            embed.add_field(name="`?channel clear <cible_id>`",
                            value="Remet les droits de la cible par défaut sur ce channel", inline=False)
            await ctx.send(embed=embed)

    @channel_management_core.command(name='block')
    async def _channel_block(self, ctx, cible_id, *, reason=None):
        try: cible = ctx.message.mentions[0]
        except: cible = await ctx.guild.fetch_member(int(cible_id))
        await ctx.channel.set_permissions(cible, read_messages=True, send_messages=False)
        block_embed = discord.Embed(
            title=f"Block de {cible.name}#{cible.discriminator}",
            description=f"Bloqué dans le channel {ctx.channel.mention}",
            color=discord.Colour.red()
        )
        block_embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                               icon_url=ctx.author.avatar_url_as(static_format='png'))
        block_embed.set_footer(text=f"Moderator ID:{ctx.author.id} • Victime ID:{cible.id}")
        report_channel = await self.bot.fetch_channel(self.report_channel[self.bot.user.id == 762723841498677258])
        block_embed.add_field(name='Raison :', value=reason)
        await report_channel.send(embed=block_embed)
        await cible.send(f"Votre permission d'écrire dans le salon {ctx.channel.name} a été retirée suite à la décision d'un modérateur."
                         f"\n> {reason}")

    @channel_management_core.command(name='ban')
    async def _channel_ban(self, ctx, cible_id, *, reason=None):
        try: cible = ctx.message.mentions[0]
        except: cible = await ctx.guild.fetch_member(int(cible_id))
        await ctx.channel.set_permissions(cible, read_messages=False, send_messages=False)
        block_embed = discord.Embed(
            title=f"Ban de {cible.name}#{cible.discriminator}",
            description=f"Banni du channel {ctx.channel.mention}",
            color=discord.Colour.dark_red()
        )
        block_embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                               icon_url=ctx.author.avatar_url_as(static_format='png'))
        block_embed.set_footer(text=f"Moderator ID:{ctx.author.id} • Victime ID:{cible.id}")
        report_channel = await self.bot.fetch_channel(self.report_channel[self.bot.user.id == 762723841498677258])
        block_embed.add_field(name='Raison :', value=reason)
        await report_channel.send(embed=block_embed)
        await cible.send(f"Votre permission d'accéder à ce salon {ctx.channel.name} a été retirée suite à la décision d'un modérateur."
                         f"\n> {reason}")

    @channel_management_core.command(name='clear')
    async def _channel_clear(self, ctx, cible_id, *, reason=None):
        try: cible = ctx.message.mentions[0]
        except: cible = await ctx.guild.fetch_member(int(cible_id))
        await ctx.channel.set_permissions(cible, read_messages=True, send_messages=True)
        block_embed = discord.Embed(
            title=f"Clear de {cible.name}#{cible.discriminator}",
            description=f"Récupère ses accès à {ctx.channel.mention}",
            color=discord.Colour.green()
        )
        block_embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                               icon_url=ctx.author.avatar_url_as(static_format='png'))
        block_embed.set_footer(text=f"Moderator ID:{ctx.author.id} • Victime ID:{cible.id}")
        report_channel = await self.bot.fetch_channel(self.report_channel[self.bot.user.id == 762723841498677258])
        block_embed.add_field(name='Raison :', value=reason)
        await report_channel.send(embed=block_embed)
        await cible.send(
            f"Votre permission d'écrire dans le salon {ctx.channel.name} a été restaurée."
            f"\n> {reason}")
    # END OF CHANNELS MANAGEMENT GROUP


def setup(bot):
    bot.add_cog(Admin(bot))
