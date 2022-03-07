#!/bin/bash/Python-3.9.0 python
# coding=utf-8

try:
    import discord
    import time
    import logging
    import sys
    import json
    import asyncio
    from discord.ext import commands
    import sqlite3
    from DataBaseAccess import DataBaseAccess

    _plugins = ['general', 'dev', 'admin', 'starbotch', 'sdlm', 'loops', "vocal", "memes"]


    class BOTCH(commands.bot.BotBase, discord.Client):
        def __init__(self, test=False):
            super().__init__(command_prefix='?', status=discord.Status.online,
                             activity=discord.Game("servir des bières"), intents=discord.Intents.all())
            self.test = test
            self.DBA = DataBaseAccess(connexion=sqlite3.connect("data/database.db"))
            with open('config.json') as f: self.config = json.load(f)


    def setup_logger():
        # on chope le premier logger
        log = logging.getLogger("raph")
        # on défini un formatteur
        format = logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s", datefmt = "[%d/%m/%Y %H:%M]")
        # ex du format : [08/11/2018 14:46] WARNING RSSCog fetch_rss_flux l.288 : Cannot get the RSS flux because of the following error: (suivi du traceback)

        # log vers un fichier
        file_handler = logging.FileHandler("debug.log")
        # tous les logs de niveau DEBUG et supérieur sont evoyés dans le fichier
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(format)

        # log vers la console
        stream_handler = logging.StreamHandler(sys.stdout)
        # tous les logs de niveau INFO et supérieur sont evoyés dans le fichier
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(format)

        # supposons que tu veuille collecter les erreurs sur ton site d'analyse d'erreurs comme sentry
        # sentry_handler = x
        # sentry_handler.setLevel(logging.ERROR)  # on veut voir que les erreurs et au delà, pas en dessous
        # sentry_handler.setFormatter(format)

        # log.debug("message de debug osef")
        # log.info("message moins osef")
        # log.warn("y'a un problème")
        # log.error("y'a un gros problème")
        # log.critical("y'a un énorme problème")

        log.addHandler(file_handler)
        log.addHandler(stream_handler)
        # log.addHandler(sentry_handler)

        return log


    def main():
        with open('config.json') as f:
            conf = json.load(f)

        if input("Testbot ?\n") == 'y':
            test = True
        else:
            test = False

        client = BOTCH(test=test)
        client.conf = conf
        log = setup_logger()
        log.setLevel(logging.DEBUG)
        log.info("Lancement du bot")

        count = 0
        client.remove_command("help")
        for plugin in _plugins:
            try:
                client.load_extension("plugins." + plugin)
            except:
                log.exception(f'\nFailed to load extension {plugin}')
                count += 1
            if count > 0:
                raise Exception("\n{} modules not loaded".format(count))
        del count

        async def on_ready():
            """Called when the bot is connected to Discord API"""
            print('\nBot connecté')
            print("Nom : " + client.user.name)
            print("ID : " + str(client.user.id))
            if len(client.guilds) < 200:
                serveurs = [x.name for x in client.guilds]
                print(
                    "Connecté sur [" + str(len(client.guilds)) + "] " + ", ".join(serveurs))
            else:
                print("Connecté sur " + str(len(client.guilds)) + " serveurs")
            print(time.strftime("%d/%m  %H:%M:%S"))
            print('------')
            await asyncio.sleep(2)

        client.add_listener(on_ready)

        client.run(conf["token"] if not test else conf["token_test"])


    if __name__ == "__main__":
        main()
except Exception as e:
    print(e)
    x = input()
