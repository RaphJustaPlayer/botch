from discord.ext import commands
import package
import discord
import asyncio
import time
import os
import datetime
from plugins.loops import Loops
import collections
from shutil import copyfile
import matplotlib.pyplot as plt


async def leaderboard_maker(guild, raw_leaderboard):
    leaderboard = []
    for ID, score in raw_leaderboard:  # fait un top10 des vainqueurs
        try:
            user = await guild.fetch_member(ID)
            leaderboard.append((user.display_name, score))
        except Exception as e:
            print(e, ID)
    return leaderboard


def victoire(posteur, winner, score):
    embed = discord.Embed(
        title="Victoire",
        description=f"{posteur.name}#{posteur.discriminator} \u2192 {winner.name}#{winner.discriminator}",
        color=discord.Colour.green()
    )
    embed.add_field(name="Nombre de victoires :", value=f"{score} \u2192 {score + 1}")
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


class Sdlm(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.file = "sdlm"
        self.main_channel = 707639957484732466
        self.log_channel = {True: 752932896683196536, False: 752561016839209055}
        self.guild = {True: 752932746053025865, False: 625330528588922882}
        self.boris = {True: 754335412633337887, False: 777146313846292481}
        self.leaderboard = []
        self.posteur = bot.DBA.posteur
        self.image = bot.DBA.image
        self.backupconfirm = {}  # Sous la forme 123456789101112: "filename.db"
        self.topgraph_url = self.bot.DBA.topgraph

    async def generate_top_graph(self):
        fig = plt.figure()
        ax: plt.Axes = fig.add_axes([0.1, 0.4, 0.9, 0.6])
        y = []
        names = []
        for name, score in self.leaderboard:
            y.append(score)
            names.append(name)
        ax.bar(names, y)
        plt.ylabel("Score")
        plt.xlabel("Joueurs")
        plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
        ax.spines['bottom'].set_color('#ffffff')
        ax.spines['top'].set_color('#ffffff')
        ax.spines['right'].set_color('#ffffff')
        ax.spines['left'].set_color('#ffffff')
        ax.tick_params(colors='#ffffff')
        ax.xaxis.label.set_color('#ffffff')
        ax.yaxis.label.set_color('#ffffff')
        plt.savefig(f"{os.getcwd()}\\temp\\leaderboard.png", transparent=True)

    async def update_top_graph(self):
        await self.generate_top_graph()
        channel = await self.bot.fetch_channel(752561016839209055)
        message: discord.Message = await channel.send(file=discord.File(f"{os.getcwd()}\\temp\\leaderboard.png"))
        self.topgraph_url = self.bot.DBA.topgraph = message.attachments[0].url

    @commands.Cog.listener()
    async def on_ready(self):
        guild = await self.bot.fetch_guild(self.guild[self.bot.user.id == 762723841498677258])
        self.leaderboard = await leaderboard_maker(guild, self.bot.DBA.leaderboard())

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name not in ["check", "✅"]: return
        if package.in_protected_channel(payload.channel_id): return
        if payload.channel_id != 707639957484732466: return

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if self.posteur != payload.user_id:
            return
        elif self.posteur == message.author.id:
            return await channel.send("T'es un petit marrant toi !")

        guild = await self.bot.fetch_guild(self.guild[self.bot.user.id == 762723841498677258])
        posteur = await guild.fetch_member(self.posteur)

        self.bot.DBA.updatescore(message.author.id, self.bot.DBA.showscore(message.author.id) + 1)
        self.bot.DBA.posteur = self.posteur = message.author.id

        try:
            oldmessage = await channel.fetch_message(self.image)
            await oldmessage.unpin()
        except:
            pass

        self.bot.DBA.image = self.image = 0
        await channel.send("{} __**FÉLICITATIONS !**__".format(message.author.mention))
        logchannel = await self.bot.fetch_channel(self.log_channel[self.bot.user.id == 762723841498677258])
        await logchannel.send(embed=victoire(posteur, message.author, self.bot.DBA.showscore(message.author.id) - 1))
        self.leaderboard = await leaderboard_maker(guild, self.bot.DBA.leaderboard())
        for user_id, _ in self.bot.DBA.leaderboard():
            if user_id == message.author.id: await self.update_top_graph()

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        self.bot.DBA.updatescore(user.id, 0)

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.test: return await self.bot.process_commands(message)
        if message.author.bot:
            if message.type == discord.MessageType.pins_add:
                return await message.delete()
            return
        if message.author.id in self.backupconfirm and message.content == 'confirm':
            path = os.getcwd() + "/bakcups"
            file = self.backupconfirm[message.author.id]
            path_copy = path.replace('bakcups', 'data')
            copyfile(f"{path}/{file}", f"{path_copy}/database.db")
            self.backupconfirm.pop(message.author.id, None)
            await message.channel.send(f"Backup `{file}` chargée !")
        if message.content == 'cancel' and message.author.id in self.backupconfirm:
            self.backupconfirm.pop(message.author.id, None)
            await message.channel.send("Chargement de la backup annulé")

        try:
            if message.content[0] == '?':
                return
        except:
            pass
        if message.channel.id not in [707639957484732466, 732296566299426939, 752932896683196536]:
            return
        elif self.posteur != message.author.id:
            return

        elif message.attachments:
            for pin in await message.channel.pins():
                if pin.author.id == message.author.id:
                    if len(message.content) == 0:
                        pass
                    else:
                        oldpin = await message.channel.fetch_message(pin.id)
                        await oldpin.unpin()

            await message.pin()
            self.image = message.id
            self.bot.DBA.image = message.id
            await asyncio.sleep(0.1)
            async for message in message.channel.history():
                if message.author == self.bot.user:
                    if message.type == discord.MessageType.pins_add:
                        return await message.delete()

    @commands.command(name='leaderboard', aliases=["lb"])
    async def lb(self, ctx):
        if self.topgraph_url == 0: await self.update_top_graph()
        await ctx.message.delete()
        embed = discord.Embed(
            title="Leaderboard :",
            color=discord.Colour.from_rgb(255, 0, 21),
        )
        embed.set_image(url=self.topgraph_url)

        track = 1
        for name, victory in self.leaderboard:  # fait un top10 des vainqueurs
            embed.add_field(name="Top {}".format(track), value="{} avec {} victoires".format(name, victory),
                            inline=False)
            track += 1
        await ctx.send(embed=embed)

    @commands.command(name='score')
    async def score(self, ctx, param=None):
        await ctx.message.delete()
        try:
            try:
                cible = await ctx.guild.fetch_member(int(param))
            except:
                cible = ctx.message.mentions[0]
        except:
            cible = ctx.author

        embed = discord.Embed(
            title="Score de {}".format(cible.display_name),
            colour=cible.color,
            description="Nombre de victoires : {}".format(self.bot.DBA.showscore(cible.id)))
        embed.set_thumbnail(url=cible.avatar_url_as(static_format='png'))

        await ctx.send(embed=embed)

    @commands.command(name='tienskop1')
    async def ti1kop1(self, ctx):
        await ctx.message.delete()
        if ctx.author.id != self.posteur: return await ctx.send("T'es un petit marrant toi !")
        try:
            cible = ctx.message.mentions[0]
        except:
            return await ctx.send("Vous devez ciblez quelqu'un pour passer votre tour.")

        if self.image != 0:
            try:
                oldmessage = await ctx.channel.fetch_message(self.image)
                await oldmessage.unpin()
            except Exception as e:
                print(f"{e}")
        self.bot.DBA.posteur = self.posteur = cible.id
        self.bot.DBA.image = self.image = 0

        await ctx.send("{}, de sa bonté infinie, a donné son tour à {}".format(ctx.author.mention, cible.mention))

    @commands.command(name='posteur')
    async def posteur(self, ctx):
        await ctx.message.delete()
        posteur = await ctx.guild.fetch_member(self.posteur)

        if self.image == 0:
            desc = f"{posteur.mention} n'a pas encore posté d'image..."
        else:
            desc = f"L'image de {posteur.mention} à deviner est :"
        embed = discord.Embed(
            title=f"Le posteur actuel est {posteur.display_name}",
            description=desc,
            color=discord.Colour.from_rgb(255, 0, 21)
        )
        if self.image != 0:
            img = await ctx.channel.fetch_message(self.image)
            imgurl = img.attachments[0].url
            embed.set_image(url=imgurl)
        await ctx.send(embed=embed)

    @commands.group(name='sdlm')
    async def _sdlm_group(self, ctx):
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title=f"Help jeu du screen de la muerte",
                color=discord.Colour.from_rgb(255, 0, 21),
                description="Ce magnifique bot permet le bon fonctionnement du jeu du screen de la muerte !"
                            "\nLe jeu se divise en deux équipes :"
                            f"\n\t- Le posteur : loup solitaire, il doit poster une image que les chercheurs devront "
                            f"trouver. Si une des réponse est juste, il doit réagir au message avec <:check:777176225352384532> ou ✅ pour "
                            f"que le nouvel élu prenne la relève... "
                            "\n\t- Les chercheurs : un groupe d'individus encore mal connus du grand public qui s'efforce "
                            "de faire fonctionner leur hypocampe a la limite du possible humain. Ils doivent trouver ce "
                            "que le posteur veut faire deviner pour lui succéder après.")
            embed.add_field(name="?leaderboard",
                            value="Affiche le leaderboard", inline=False)
            embed.add_field(name="?posteur",
                            value="Affiche le posteur actuel", inline=False)
            embed.add_field(name="?score <cible>",
                            value="Affiche ton score ou celui de la cible (optionnel)", inline=False)
            embed.add_field(name="?tienskop1 (cible)",
                            value="Passe le tour à la cible", inline=False)
            admin = False
            admin_roles = [625332148265549844, 636302581949530122, 625333008542597122, 637277665182744636,
                           777247006954750023, 753273974623830078]
            for r in [role.id for role in ctx.author.roles]:
                if r in admin_roles:
                    admin = True
            if admin:
                embed.add_field(name="<:professionnel:777146313845506048> ?sdlm reload",
                                value="reload la database", inline=False)
                embed.add_field(name="<:professionnel:777146313845506048> ?sdlm posteur <target_id/@target>",
                                value="Passe le posteur actuel pour le nouveau posteur", inline=False)
                embed.add_field(name="<:professionnel:777146313845506048> ?sdlm score <target_id/@target> <score>",
                                value="Change le score d'un joueur", inline=False)
                embed.add_field(name="<:professionnel:777146313845506048> ?sdlm setimg <msg_id>",
                                value="Modifie l'image a chercher", inline=False)
                embed.add_field(name="<:professionnel:777146313845506048> ?sdlm backups",
                                value="Affiche les backups disponible de <#707639957484732466>", inline=False)
                embed.add_field(name="<:professionnel:777146313845506048> ?sdlm load_backup (backup_number)",
                                value="Charge une backup du <#707639957484732466>, si aucun numéro de backup n'est précisé, c'est la plus récente qui sera chargée.",
                                inline=False)
                embed.add_field(name="<:professionnel:777146313845506048> ?sdlm do_backup",
                                value="Créer une backup du <#707639957484732466>",
                                inline=False)
                embed.add_field(name="<:professionnel:777146313845506048> ?sdlm export_backup (backup_number)",
                                value="Exporte une backup du <#707639957484732466>, si aucun numéro de backup n'est précisé, c'est la plus récente qui sera exportée.",
                                inline=False)
            await ctx.send(embed=embed)

    @_sdlm_group.command(name="backups")
    async def _backups_listing(self, ctx):
        path = os.getcwd().replace('plugins', '')
        path += "/bakcups"
        file_list = []
        final = []
        now = datetime.datetime.now()

        for r, d, f in os.walk(path):
            file_list = f

        file_dict = {}
        for f in file_list:
            raw = f.split(" ")
            if len(raw) == 3:
                date = raw[1].split("-")
                hour = raw[2].split("h")
                hour[1] = hour[1][:-3]
                file_dict[int(raw[0][1:-1])] = (date, hour)
        file_dict = collections.OrderedDict(sorted(file_dict.items()))
        file_dict = package.reversed_dict(file_dict)

        for f in file_dict:  # filedict = {n°: ([year, mont, day], [hour, minute]), ...}
            if now.year > int(file_dict[f][0][0]) or now.month > int(file_dict[f][0][1]) + 1 or (
                    now.month > int(file_dict[f][0][1]) and now.day > int(file_dict[f][0][2])):
                os.remove(f"{path}/[{f}] {'-'.join(file_dict[f][0])} {'h'.join(file_dict[f][1])}.db")
            else:
                final.append((f, file_dict[f][0], file_dict[f][1]))

        lists = [final[:(len(final) // 2) + 1 if type(len(final) / 2) == float else len(final) // 2],
                 final[(len(final) // 2):]]
        lists = [lists[0][:(len(lists[0]) // 2) + 1 if type(len(lists[0]) / 2) == float else len(lists[0]) // 2],
                 lists[0][(len(lists[0]) // 2):],
                 lists[1][:(len(lists[1]) // 2) + 1 if type(len(lists[1]) / 2) == float else len(lists[1]) // 2],
                 lists[1][(len(lists[1]) // 2):]]

        track = 1
        for n, splited_list in enumerate(lists):

            embed = discord.Embed(
                title="Backups",
                description="Liste des backups depuis 1 mois" if n == 0 else "",
                color=discord.Colour.from_rgb(255, 0, 21)
            )
            for number, date, hour in splited_list:
                embed.add_field(name=f"[{number}] - {'/'.join(date)}", value=f"{'h'.join(hour)}")
                track += 1
            await ctx.send(embed=embed)

    @_sdlm_group.command(name="do_backup")
    async def _do_backup(self, ctx):
        new_backup = Loops.curent_file_number() + 1
        Loops.do_backup(new_backup)
        await ctx.send(f"Backup n°{new_backup} crée !")

    @_sdlm_group.command(name="load_backup")
    async def _load_backup(self, ctx, backup=""):
        path = os.getcwd() + "/bakcups"
        file_list = []
        for r, d, f in os.walk(path):
            file_list = f
        files = {}
        for f in file_list:
            raw = f.split(" ")
            if len(raw) == 3:
                files[int(raw[0][1:-1])] = f
        files = collections.OrderedDict(sorted(files.items()))
        files = package.reversed_dict(files)

        if backup == "":
            keys = []
            for key in files.keys():
                keys.append(key)
            file = files[keys[0]]
        else:
            try:
                file = files[backup]
            except KeyError as e:
                return await ctx.send(f"`{', '.join(e.args)}` n'est pas une backup valide")

        await ctx.send(f"Vous etes sur le point de charger la sauvegarde `{file}`\nCette action est iréversible, etes vous sur ?\n\nTapez `confirm` pour charger la sauvegarde ou `cancel` pour annuler le chargement.")
        self.backupconfirm[ctx.author.id] = file

    @_sdlm_group.command(name="export_backup")
    async def _export_backup(self, ctx, backup=""):
        path = os.getcwd() + "/bakcups"
        file_list = []
        for r, d, f in os.walk(path):
            file_list = f
        files = {}
        for f in file_list:
            raw = f.split(" ")
            if len(raw) == 3:
                files[int(raw[0][1:-1])] = f
        files = collections.OrderedDict(sorted(files.items()))
        files = package.reversed_dict(files)

        if backup == "":
            keys = []
            for key in files.keys():
                keys.append(key)
            file = files[keys[0]]
        else:
            try:
                file = files[backup]
            except KeyError as e:
                return await ctx.send(f"`{', '.join(e.args)}` n'est pas une backup valide")

        await ctx.send(file=discord.File(f"{os.getcwd()}/bakcups/{file}"))

    @_sdlm_group.command(name='reload')
    async def _reload(self, ctx):
        await ctx.send('Reloading the database ...')
        await ctx.channel.trigger_typing()
        counter = time.time()
        package.is_admin(ctx.author.roles)
        self.image = self.bot.DBA.image
        self.posteur = self.bot.DBA.posteur
        self.leaderboard = await leaderboard_maker(ctx.guild, self.bot.DBA.leaderboard())
        await ctx.send(content="Database reloaded in {}s !".format(round(time.time() - counter, 1)))

    @_sdlm_group.command(name='posteur')
    async def _posteur(self, ctx, cible):
        package.is_admin(ctx.author.roles)
        try:
            posteur = await ctx.guild.fetch_member(int(cible))
        except:
            posteur = ctx.message.mentions[0]

        boris = await ctx.guild.fetch_emoji(self.boris[self.bot.user.id == 762723841498677258])
        try:
            lp = await ctx.guild.fetch_member(self.bot.DBA.posteur)
        except:
            lp = await ctx.guild.fetch_member(762723841498677258)
        embed = discord.Embed(
            title="Changement de posteur !",
            description=f"Après consultation du Saint et Glorieux {boris}, le posteur actuel change !\n\n**{lp.mention} \u2192 {posteur.mention}**",
            color=discord.Colour.from_rgb(255, 0, 21)
        )
        self.posteur = self.bot.DBA.posteur = posteur.id
        self.image = self.bot.DBA.image = 0
        await ctx.send(embed=embed)

    @_sdlm_group.command(name='score')
    async def _score(self, ctx, cible, param):
        try:
            posteur = await ctx.guild.fetch_member(int(cible))
        except:
            posteur = ctx.message.mentions[0]

        init_score = self.bot.DBA.showscore(posteur.id)

        if param == "-1":
            new_score = init_score - 1
        elif param == '+1':
            new_score = init_score + 1
        else:
            new_score = int(param)

        embed = discord.Embed(
            title="Modification du score !",
            description=f"Le score de {posteur.mention} passe de **{str(init_score)}** à **{str(new_score)}**",
            color=discord.Colour.from_rgb(255, 0, 21)
        )
        embed.set_thumbnail(url=posteur.avatar_url_as(static_format='png'))

        self.bot.DBA.updatescore(posteur.id, new_score)
        await ctx.send(embed=embed)
        self.leaderboard = await leaderboard_maker(ctx.guild, self.bot.DBA.leaderboard())

    @_sdlm_group.command(name='setimg')
    async def _set_img(self, ctx, imgid):
        if self.image != 0:
            try:
                oldpin = await ctx.channel.fetch_message(self.image)
                await oldpin.unpin()
            except:
                pass
        try:
            msg = await ctx.channel.fetch_message(int(imgid))
            self.image = self.bot.DBA.image = int(imgid)
            await msg.pin()
        except Exception as e:
            print(e)
            # await ctx.send(f"`{imgid}` is a anvalid ID.")


def setup(bot):
    bot.add_cog(Sdlm(bot))
