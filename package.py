import requests
import discord
from bs4 import BeautifulSoup
import codecs
import os
import time
import re
from discord import Embed, Colour
import discord.ext.commands.errors as er
from YTB_request import YtbRequests
import json


standard_embed_color = discord.Colour.from_rgb(255, 0, 21)


def localtime():
    return time.strftime("%Y-%m-%d %Hh-%Mm-%Ss")


def generate_quote():
    film = ""
    character = []
    citation = ""
    number = ""
    r = requests.get('https://www.kaakook.fr/random')
    soup = BeautifulSoup(r.text, 'lxml')
    a = soup.find_all('a')

    for raw in a:
        raw = str(raw)
        if "/film" in raw and "/films" not in raw:
            raw = raw.split('>')
            film = raw[1][:-3]
        elif '/perso' in raw and '/persos' not in raw:
            raw = raw.split('>')
            character.append(raw[1][:-3])
        elif '/citation' in raw and 'svg' not in raw:
            raw = raw.split('>', 1)
            citation = raw[1][:-4]
            if "<br/>" in citation:
                citation = citation.replace('<br/>', '\n')
            if '<b>' in citation:
                citation = citation.replace('<b>', '**')
                citation = citation.replace('</b>', '**')
            if '<i>' in citation:
                citation = citation.replace('<i>', '*')
                citation = citation.replace('</i>', '*')
            raw = raw[0].split("-")
            number = raw[1][:-1]

    if len(character) == 0:
        return citation, film, None, number
    else:
        return citation, film, character, number


def dictionairy(leaders):  # Fonction qui permet de trier un dictionnaire en prenant les valeur par ordre croissant.
    # J'ai péta ça sur stack overflow je sais pas comment sa marche mais sa marche
    # Note that it will sort in lexicographical order
    # For mathematical way, change it to float
    return (sorted(leaders.items(), key=
    lambda kv: (kv[1], kv[0])))


def log(fonction, *args, **kwargs):
    with codecs.open(f'{os.getcwd()}\\logs', "a", 'utf-8') as f:
        f.write(f"[{localtime()}] - {fonction} was called by `{args[0]}` with `{kwargs}`\n")


def downloader(url):
    r = requests.get(url, stream=True, headers={
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
    })
    suffix = url.split('.')
    with open(f"report.{suffix[len(suffix)-1]}", 'wb') as f:
        f.write(r.content)
    return f"report.{suffix[len(suffix)-1]}"


class CustomEmbeds:
    def __init__(self):
        pass

    @staticmethod
    def victoire(posteur, winner, score):
        embed = Embed(
            title="Victoire",
            description=f"{posteur.name}#{posteur.discriminator} \u2192 {winner.name}#{winner.discriminator}",
            color=Colour.green()
        )
        embed.add_field(name="Nombre de victoires :", value=f"{score} \u2192 {score + 1}")
        embed.set_footer(text=f"Winner ID:{winner.id} • Ex-posteur ID: {posteur.id}")
        return embed

    @staticmethod
    def kop1(posteur, kop1):
        embed = Embed(
            title="Kop1",
            description=f"{posteur.name}#{posteur.discriminator} \u2192 {kop1.name}#{kop1.discriminator}",
            color=Colour.green()
        )
        embed.set_footer(text=f"Kop1 ID:{kop1.id} • Ex-posteur ID: {posteur.id}")
        return embed

    @staticmethod
    def message_edit(before, after):
        embed = discord.Embed(
            timestamp=after.created_at,
            description=f"<@!{before.author.id}>**'s message was edited in** <#{before.channel.id}>.",
            colour=discord.Colour(0x00FF00)
        )
        embed.set_author(name=f'{before.author.name}#{before.author.discriminator}',
                         icon_url=before.author.avatar_url_as(static_format='jpg'))
        embed.set_footer(text=f"Author ID:{before.author.id} • Message ID: {before.id}")
        embed.add_field(name='Before:', value=before.content, inline=False)
        embed.add_field(name="After:", value=after.content, inline=False)
        return embed

    @staticmethod
    def message_delete(message):
        embed = discord.Embed(
            timestamp=message.created_at,
            description=f"<@!{message.author.id}>**'s message was deleted in** <#{message.channel.id}>.",
            colour=discord.Colour.red()
        )
        embed.set_author(name=f'{message.author.name}#{message.author.discriminator}',
                         icon_url=message.author.avatar_url_as(static_format='jpg'))
        embed.set_footer(text=f"Author ID:{message.author.id} • Message ID: {message.id}")
        embed.add_field(name="Content :", value=message.content)
        return embed

    @staticmethod
    def ytbEmbed(url = 'https://www.youtube.com/user/BOTCHvideos'):
        content = YtbRequests.SearchInYtbChannel(url)
        print(content)
        youtube = discord.Embed(  # Définition de l'embed
            title = content[1],  # Définition du titre de l'embed
            url = url,
            # Définition de l'url du titre de l'embed
            colour = discord.Colour.red(),  # Définition de la couleur de l'embed
            description = "Chaîne communautaire basée sur le plaisir et le fun !")

        youtube.set_thumbnail(
            url = 'https://images-ext-1.discordapp.net/external/37ywkK_fY6AtHDSW64zdpxf-81XtfGymZbawgr5ln7A/%3Fsize%3D1024/https/cdn.discordapp.com/icons/625330528588922882/a_f5e4ccb80c000491a40c3e8764e270d2.gif')

        youtube.add_field(name = "Subscriber count :",
                          value = content[2])  # Ajout du compteur d'abonnés WIP

        youtube.add_field(name = "Last video :", value = content[3])
        return youtube


def bettermonths(number):
    months = {
        1: 'Janvier',
        2: 'Février',
        3: 'Mars',
        4: 'Avril',
        5: 'Mai',
        6: 'Juin',
        7: 'Juillet',
        8: 'Aout',
        9: 'Septembre',
        10: 'Octobre',
        11: 'Novembre',
        12: 'Décembre'
    }
    return months[number]


def is_admin(roles):
    admin = False
    admin_roles = [625332148265549844, 636302581949530122, 625333008542597122, 637277665182744636,
                   777247006954750023, 753273974623830078]
    for r in [role.id for role in roles]:
        if r in admin_roles:
            admin = True
    if not admin:
        raise er.MissingAnyRole('admin')


def in_protected_channel(cid):
    with open('config.json') as f:
        conf = json.load(f)

    if cid in conf['protected_channels']:
        return True
    else:
        return False


def is_bot(ID):
    if ID in [762723841498677258, 777166173149986826]:
        return True
    return False


def protected_channels():
    with open(r'config.json', 'r') as f:
        conf = json.load(f)
    return conf['protected_channels']


def count_lines_code(values):
    """Count the number of lines for the whole project"""
    count = 0
    with open('main.py', 'r', encoding="utf8") as file:
        for line in file.read().split("\n"):
            count += 1
    with open('package.py', 'r', encoding="utf8") as file:
        for line in file.read().split("\n"):
            count += 1
    with open('DataBaseAccess.py', 'r', encoding="utf8") as file:
        for line in file.read().split("\n"):
            count += 1

    for filename in [f"{os.getcwd()}/plugins/{x.file}.py" for x in values]:
        print(filename)
        try:
            with open(filename, 'r', encoding="utf8") as file:
                for line in file.read().split("\n"):
                    count += 1
        except Exception as e:
            print(e)
    return count


def reversed_dict(init_dict):
    list_keys = []
    for k in init_dict.keys(): list_keys.append(k)

    rev_dict = {}
    for i in reversed(list_keys): rev_dict[i] = init_dict[i]
    return rev_dict
