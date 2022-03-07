from discord.ext import tasks, commands
import discord
import datetime
import os
from shutil import copyfile
import package
import collections
from random import choice


class Loops(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.file = "loops"

        self.file_code = Loops.curent_file_number()+1
        self.looped_backup.start()

    @staticmethod
    def do_backup(code):
        path = os.getcwd()
        now = datetime.datetime.now()
        backup_name = f"{path}/bakcups/[{code}] {now.date()} {now.hour}h{now.minute}.db"
        copyfile(f"{path}/data/database.db", backup_name)
        return backup_name
    
    @staticmethod
    def curent_file_number():
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

        keys = []
        for key in files.keys():
            keys.append(key)
        return int(keys[0])

    @tasks.loop(hours=12)
    async def looped_backup(self):
        Loops.do_backup(self.file_code)
        self.file_code += 1

    @tasks.loop(minutes=10)
    async def t_moche_lyolia(self):
        botch = await self.bot.fetch_guild(625330528588922882)
        tmoche = discord.utils.get(botch.roles, id=949262343236366356)
        colors = [discord.Color.dark_magenta(),
                  discord.Color.dark_gold(),
                  discord.Color.blurple(),
                  discord.Color.dark_purple()]
        await tmoche.edit(colour=choice(colors))

    @commands.group(name='loops')
    async def _loops_group(self, ctx):
        await ctx.message.delete()
        package.is_admin(ctx.author.roles)
        if ctx.invoked_subcommand is None:
            await ctx.send("`?loops reload`\n`?loops dobackup`")

    @_loops_group.command(name="reload")
    async def loops_reload(self, ctx):
        path = os.getcwd() + '/bakcups'
        file_list = []
        for r, d, f in os.walk(path):
            file_list = f
        file_list.sort()
        await ctx.send(file_list)

    @_loops_group.command(name="dobackup")
    async def doabackupcauseineedit(self, ctx):
        backup_name = Loops.do_backup(self.file_code)
        self.file_code += 1
        await ctx.send(backup_name)


def setup(bot):
    bot.add_cog(Loops(bot))
