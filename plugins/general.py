import discord
from discord.ext import commands
import asyncio
import time
from platform import system as system_name
from subprocess import call as system_call
import package
import requests
from bs4 import BeautifulSoup
import json
from YTB_request import YtbRequests
import random


async def ping_adress(ctx, ip):
    packages = 30
    wait = 0.3
    try:
        try:
            m = await ctx.send(f"Pinging {ip}...")
        except:
            m = None
        t1 = time.time()
        param = '-n' if system_name().lower() == 'windows' else '-c'
        command = ['ping', param, str(packages), '-i', str(wait), ip]
        result = system_call(command) == 0
    except Exception as e:
        await ctx.send("`Error:` {}".format(e))
        return
    if result:
        t = (time.time() - t1 - wait * (packages - 1)) / packages * 1000
        await ctx.send("Pong ! (average of {}ms per 64 byte, sent at {})".format(round(t, 2), ip))
    else:
        await ctx.send("Unable to ping this adress")
    if m is not None:
        await m.delete()


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.file = "general"
        self.codelines = package.count_lines_code(self.bot.cogs.values())

    @commands.command(name="ping", enabled=True)
    async def rep(self, ctx, ip=None):
        """Get bot latency
        You can also use this command to ping any other server"""
        if ip is None:
            m = await ctx.send("Ping...")
            t = (m.created_at - ctx.message.created_at).total_seconds()
            await m.edit(content=":ping_pong:  Pong !\nBot ping: {}ms\nDiscord ping: {}ms".format(round(t * 1000),
                                                                                                  round(
                                                                                                      self.bot.latency * 1000)))
            await ctx.message.delete()
        else:
            asyncio.run_coroutine_threadsafe(
                ping_adress(ctx, ip), asyncio.get_event_loop())

    @commands.command(name='citafion', enabled=True)
    async def citation(self, ctx):
        """Give a quote
                Extract and post a random quote from Kaakook"""
        await ctx.message.delete()
        citation, film, characters, number = package.generate_quote()
        if characters is None:
            title = "Citation"
        elif len(characters) == 1:
            title = f"Citation de {characters[0]}"
        else:
            title = 'Citation de'
            for n in range(len(characters) - 1):
                title += f" {characters[n]},"
            title = f'{title[:-1]} et de {characters[len(characters) - 1]}'
        embed = discord.Embed(
            title=title,
            description=f'« {citation} »',
            url=f'https://www.kaakook.fr/citation-{number}',
            color=discord.Colour.orange()
        )
        embed.set_author(name="Par Kaakook")
        embed.set_footer(text=f"Citation en provenance de {film}")
        await ctx.send(embed=embed)

    @commands.command(name="tipeee", enabled=True)
    async def tipeee(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(
            title="Soutenez la chaine BOTCH !",
            description="Si vous voulez soutenir BOTCH, n'hésitez pas a donner une pièce a ces ~~claudos~~ créateurs d'exception !",
            url="https://fr.tipeee.com/botch-1",
            color=discord.Colour.from_rgb(255, 0, 21)
        )
        embed.set_image(
            url="https://images-ext-2.discordapp.net/external/2lioRnN_4idYGz32ClIBqRfsCm86hE8BIhZ5f8EyNhc/https/api.tipeee.com/cache/20160621203507/media/1200/630/zoom/1072276/75e230d641ed5c46108178a1334b5603399396a5.jpeg")
        await ctx.send(embed=embed)

    @commands.command(name="bstats", enabled=True)
    async def bstats(self, ctx):
        await ctx.send(f'There are {self.codelines} lines in the whole code')

    @commands.command(name='todo', enabled=True)
    async def todo(self, ctx):
        await ctx.message.delete()
        with open("ongoingtask.md", 'r', encoding="utf-8") as file:
            text = file.read().split('\n')
        final = ""

        taskpercent = 0
        ttpercent = 0

        done = 0
        undone = 0
        for t in text:
            if ('[ ]' in t and "  " in t) or ('[ ]' in t and " ..." not in t):
                undone += 1
                if '$' in t:
                    oui = False
                    if '$' in t: oui = True
                    text = t.replace('$', ' ')
                    if oui: text += '%'
                    final += text + '\n'

                    t = t.split('$')
                    ttpercent += int(t[1])
                    taskpercent += 1
                else:
                    final += t + '\n'
            elif ('[x]' in t and "  " in t) or ('[x]' in t and " ..." not in t):
                done += 1
                oui = False
                if '$' in t: oui = True
                text = t.replace('$', ' ')
                if oui: text += '%'
                final += text + '\n'
            else:
                final += t + '\n'
        final += f'{round((done * 100 + ttpercent) / (done + undone))}% : {done}/{done + undone} task done.'
        final = final.replace('`', '')
        final = "```md\n" + final
        final += '```'
        await ctx.send(final)

    @commands.command(pass_context=True, name='info')
    async def info(self, ctx):
        if self.bot.user.id != 762723841498677258:
            for emoji in self.bot.emojis:
                if emoji.id == 777146313846292481:
                    boris = emoji
        else:
            for emoji in self.bot.emojis:
                if emoji.id == 754335412633337887:
                    boris = emoji

        await ctx.message.delete()
        embed = discord.Embed(
            title=ctx.guild.name,
            url="https://discord.gg/G38Ge7y",
            color=discord.Colour.from_rgb(255, 0, 21)
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)
        if ctx.guild.banner_url != '':
            embed.set_image(url=ctx.guild.banner_url)
        embed.add_field(name='Un serveur possédant :',
                        value=f'{len(ctx.guild.voice_channels)} channels vocaux ainsi que\n{len(ctx.guild.text_channels)} channels textuels !',
                        inline=True)
        embed.add_field(name='Une communauté de :',
                        value=f"{str(ctx.guild.member_count)} membres avec un total de\n{len(ctx.guild.roles)} roles !",
                        inline=True)
        embed.add_field(name="Un bot de :",
                        value=f'{self.codelines} lignes de code en provenance de notre développeur professionnel bénévol <@!354188969472163840>',
                        inline=False)

        id_list = []
        score_dict = {}
        sb = self.bot.DBA.showallsb()
        for n, name in enumerate(sb):
            id_list.append(name)
            score_dict[n] = sb[name][1]

        sorted_keys = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
        score_dict = []
        for i in sorted_keys:
            temp = i[0], i[1]
            score_dict.append(temp)
        embed.add_field(name="Avec un starbotch d'enfer :",
                        value=f"{len(id_list)} messages ÉNORMES dont [LE meilleurs de tous]({sb[id_list[score_dict[0][0]]][0]}) avec {str(score_dict[0][1])}⭐ !")

        embed.add_field(name='Et tout ceci protégé par :',
                        value=f"La puissance psychique de la voix off et la force spirituelle du Saint et Glorieux {boris} depuis le {ctx.guild.created_at.day} {package.bettermonths(ctx.guild.created_at.month)} de l'an {ctx.guild.created_at.year}",
                        inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='help')
    async def help(self, ctx, param=None):
        await ctx.message.delete()

        if param is None:
            embed = discord.Embed(
                title="Help",
                color=discord.Colour.from_rgb(255, 0, 21),
                description="Hey !"
                            f"\nC'est moi le B-B-BOT(CH) magnifique robot codé pour servir le Saint et Glorieux <:boris:777146313846292481> et la mystérieuse voix off."
                            f"\nJe vous offres une panoplie de commandes pour vous accompagnez dans vos incroyables péripécies dans ce monde fabuleux qu'est le serveur ***BOTCH***")
            embed.add_field(name="`?help`",
                            value=f"Affiche un message d'aide général.", inline=False)
            embed.add_field(name="`?sdlm`",
                            value=f"Affiche un message d'aide sur le jeu <#707639957484732466>.", inline=False)
            embed.add_field(name="`?admin`",
                            value=f"Affiche un message d'aide sur les commandes admin.", inline=False)
            embed.add_field(name="`?tipeee`",
                            value="Permet de ~~donner l'aumone au saint Boris~~ soutenir vos créateurs préférés !",
                            inline=False)
            embed.add_field(name="`?ping`",
                            value="Test les latences du BOT(CH) et de l'API de discord", inline=False)
            embed.add_field(name="`?citafion`",
                            value="Exprime le savoir absolue des plus grands penseurs du genre humain", inline=False)
            embed.add_field(name='`?info`',
                            value='Affiche les stats du serveur', inline=False)
            embed.add_field(name='`?botch`',
                            value='Expose la suprématie de BOTCH sur le youtube game', inline=False)
            embed.add_field(name="`?sb` ou `?starbotch`",
                            value="Affiche un message d'aide sur les commandes du starbotch")
        else:
            raise commands.errors.BadArgument(param)

        await ctx.send(embed=embed)

    @commands.command(name='botch')
    async def botch(self, ctx):
        await ctx.message.delete()
        await ctx.send("La commande `?botch` est actuellement complètement pt. Je la répare soon donc avant 2025")

    @commands.command(name='youtube')
    # Pour le moment on ne peux voir que notre chaine mais pk pas le faire avec d'autre chaine ytb dans le futur
    async def youtube(self, ctx):
        await ctx.message.delete()  # Suprime le message de la commande
        await ctx.send(embed=package.CustomEmbeds.ytbEmbed())  # Envoit l'embed

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.bot.test: return await self.bot.process_commands(message)
        if "@everyone" in message.content:
            guild = message.guild
            member = await guild.fetch_member(message.author.id)
            roles = member.roles
            verif = False
            for r in [role for role in roles]:
                for n in r.permissions:
                    if n[0] == 'mention_everyone' and n[1]: verif = True
            if not verif:
                messages_pagentil = ["Wesh t'as cru t'étais qui pour everyone comme ça ?",
                                     "T'es un malade dans ta tête ?",
                                     "Ty va pas bien pitiot ?!",
                                     "Complètement fada !",
                                     "https://tenor.com/view/t-ban-ban-bigflo-oli-bigflo-et-oli-gif-17515232",
                                     "Yévététué !",
                                     "Comme l'a dis Aristote : \n> oui",
                                     "Hey, t'es pas influenceur avec 10M d'abonnées là"]
                for _ in range(len(messages_pagentil)):
                    message_pagentil = random.choice(messages_pagentil)
                    messages_pagentil.remove(message_pagentil)
                    await message.author.send(message_pagentil)

        msg = message.clean_content.split(":")
        counter = 0
        for r in msg:
            r = r.split("boris")
            if len(r) == 2:
                counter += 1
        if counter != 0:
            boris_temple = await self.bot.fetch_channel(638035798540943370)

            try:
                counter_message = await boris_temple.fetch_message(813812044356255796)
                embed = counter_message.embeds[0]
                desclist = embed.description.split('`')
                counter = int(desclist[1]) + counter

                embed = discord.Embed(
                    title="The boris counter",
                    description=f"Un total de `{counter}` émojis de type <:boris:777146313846292481> ont été utilisés",
                    color=discord.Colour.from_rgb(255, 0, 21)
                )

                await counter_message.edit(embed=embed)

                paliers = []
                for n in range(1000):
                    paliers.append(n * 1000)
                if counter in paliers:
                    await boris_temple.send(
                        f"{counter} émojis de type <:boris:777146313846292481> ont été utilisés !\n***__FÉLICITATION !!!__***")
            except:
                pass

    @commands.command(name="suntzu")
    async def suntzu(self, ctx):
        await ctx.message.delete()
        citations = ["“L’art de la guerre, c’est de soumettre l’ennemi sans combat.”",
                     "“Le bon général a gagné la bataille avant de l’engager.”",
                     "“Celui qui excelle à résoudre les difficultés les résout avant qu’elles ne surgissent. Celui qui excelle à vaincre ses ennemis triomphe avant que les menaces de ceux-ci ne se concrétisent.”",
                     "“Connais l’adversaire et surtout connais toi toi-même et tu seras invincible.”",
                     "“L'invincibilité se trouve dans la défense et la possibilité de victoire dans l'attaque.”",
                     "“Celui qui n'a pas d'objectifs ne risque pas de les atteindre.”",
                     "“C'est lorsqu'on est environné de tous les dangers qu'il n'en faut redouter aucun.”",
                     "“La guerre est une affaire d'une importance vitale pour l'État.”",
                     "“Connais ton adversaire, connais-toi, et tu ne mettras pas ta victoire en danger.”",
                     "“Connais le ciel et connais la terre, et ta victoire sera totale.”",
                     "“Si tu ne connais ni ton adversaire ni toi-même, à chaque bataille tu seras vaincu.”",
                     "“Faire cent batailles et gagner cent victoires n'est pas la meilleure conduite”",
                     "“Parvenir à battre son adversaire sans l'avoir affronté est la meilleure conduite.”",
                     "“Tout art de la guerre repose sur la duperie.”",
                     "“Il faut feindre la faiblesse, afin que l'ennemi se perde dans l'arrogance.”",
                     "“Attaque ton ennemi quand il n'est pas préparé, apparais quand tu n'es pas attendu.”",
                     "“Si ton ennemi te semble colérique, cherche à l'irriter encore davantage.”",
                     "“Il n'existe pas d'exemple d'un nation qui aurait tiré profit d'une longue guerre.”",
                     "“Ce que les anciens appellent un grand guerrier est celui qui gagne, mais qui excelle aussi dans l'art de gagner facilement.”",
                     "“Le guerrier victorieux remporte la bataille, puis part en guerre. Le guerrier vaincu part en guerre, puis cherche à remporter la bataille.”",
                     "“Un grand dirigeant commande par l'exemple et non par la force.”",
                     "“Si ses ordres ne sont pas clairs et distincts, alors le général est à blâmer.”",
                     "“Traite tes soldats comme tu traiterais ton fils bien-aimé.”",
                     "“La rapidité est l'essence même de la guerre.”"]
        embed = discord.Embed(
            title="Sun Tzu il a dit:",
            color=discord.Colour.green(),
            description=random.choice(citations)
        )
        embed.set_footer(text="L'Art de la Guerre",
                         icon_url="https://m.media-amazon.com/images/I/51jLZ3XYGFL._SL500_.jpg")
        await ctx.send(embed=embed)

    @commands.command(name="itsShrektime")
    async def itsShrektime(self, ctx):
        package.is_admin(ctx.author.roles)  # Vérifie que le mec qui l'utilise soit admin
        names = {}
        async for member in ctx.guild.fetch_members(limit=None):  # Initialise un loop a travers TOUT les membres
            names[int(
                member.id)] = member.nick if member.nick is not None else member.name  # Créer un dict tel que {'id_du_membre': 'nickname_du_membre'}

            try:
                await member.edit(nick="Shrek")  # Le rename Shrek ptdr
            except Exception as e:
                print(e)

        with open('lastnames.txt', 'w') as outfile:
            json.dump(names, outfile)  # Sauvegarde les anciens nicknames

        await ctx.send("Somebody once told me the world is gonna roll me...")

    @commands.command(name="Shrektimeisfinish")
    async def Shrektimeisfinish(self, ctx):
        package.is_admin(ctx.author.roles)  # Vérifie que le mec qui l'utilise soit admin
        with open('lastnames.txt') as json_file:
            names = json.load(json_file)  # Récupère le dict avec les ids corespondant aux nicknames

        async for member in ctx.guild.fetch_members(limit=None):  # Initialise un loop a travers TOUT les membres
            try:
                await member.edit(nick=names[str(member.id)])  # Rename tout le monde avec les anciens nicknames
            except Exception as e:
                print(e)


def setup(bot):
    bot.add_cog(General(bot))
