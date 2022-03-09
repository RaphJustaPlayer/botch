import discord
from discord.ext import commands
from discord.utils import get
from package import dictionairy
from package import protected_channels
import re
from main import BOTCH
import time
import package
import random

star_react = {}


def embed_have_content(message, author, have_content):
    if have_content:
        if message.content[0] == ">": txt = "\n"+message.content
        else: txt = message.content

        embed = discord.Embed(
            title=f"Message __***INCROYABLE !***__",
            description=f"« {txt} »\n\n[Vers le message]({message.jump_url})",
            color=discord.Colour.gold()
        )
    else:
        embed = discord.Embed(
            title=f"Message __***INCROYABLE !***__",
            description=f"[Vers le message]({message.jump_url})",
            color=discord.Colour.gold()
        )

    embed.set_footer(text=f"Author ID:{author.id} • Message ID:{message.id}")
    embed.set_author(name=f'{author.display_name}', icon_url=author.avatar_url)
    return embed


def starembed(message, author):
    have_content = False
    for l in message.content:
        if l != " " or l != '\n':
            have_content = True
    if 'http' in message.content:
        have_content = False

    embed = embed_have_content(message, author, have_content)

    try:
        embed.set_image(url=message.attachments[0].url)
    except:
        try:
            embed.set_image(url=re.search("(?P<url>https?://[^\s]+)", message.content).group("url"))
        except:
            pass
        pass
    return embed


async def sbload(bot, starbotch_channel):
    sb_channel = await bot.fetch_channel(starbotch_channel[bot.user.id == 762723841498677258])
    final = {}
    async for msg in sb_channel.history():
        try:
            raw = msg.embeds[0].description
            raw = raw.split('(https://discord.com/channels/')
            raw = raw[1][:-1].split('/')
            msgid = raw[2]
            test = msg.content.split('**')
            if len(test) == 3:
                final[(int(msgid), int(raw[1]))] = int(test[1])
        except:
            pass

    final = dictionairy(final)
    final.reverse()
    sbclean = {}
    db = bot.DBA.showallsb()

    for payload, stars in final:
        if payload[0] in db:
            msgdb = bot.DBA.showsb(payload[0])
            bot.DBA.updatesb(payload[0], stars, msgdb[0])
            sbclean[payload[0]] = (msgdb[0], stars)
        else:
            msg_channel = await bot.fetch_channel(payload[1])
            try:
                msg = await msg_channel.fetch_message(payload[0])
                bot.DBA.updatesb(msg.id, stars, msg.jump_url)
                sbclean[msg.id] = (msg.jump_url, stars)
            except discord.NotFound:
                pass
    return sbclean


class Starbotch(commands.Cog):

    def __init__(self, bot: BOTCH):
        self.bot = bot
        self.protected_channels = protected_channels()
        self.starbotch_channel = {True: 752932896683196536, False: 777986876552118292}
        self.guild = {True: 752932746053025865, False: 625330528588922882}
        self.file = "starbotch"
        self.starbotch = {}
        self.sb_lb = None

    @commands.Cog.listener()
    async def on_ready(self):
        if self.bot.user.id == 762723841498677258:
            self.starbotch = None
        else:
            self.starbotch = await sbload(self.bot, self.starbotch_channel)
            self.sb_lb = await self.sb_leaderboard()
            print('Starbotch loaded !')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name != "⭐":
            return
        if payload.channel_id in self.protected_channels:
            return

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = get(message.reactions, emoji=payload.emoji.name)

        if message.id in star_react:  # Check si quelqu'un spam pas les étoiles
            if star_react[message.id] >= 3:
                return

        if reaction and reaction.count >= 7:
            sb_channel = await self.bot.fetch_channel(self.starbotch_channel[self.bot.user.id == 762723841498677258])
            guild = await self.bot.fetch_guild(self.guild[self.bot.user.id == 762723841498677258])
            author = await guild.fetch_member(message.author.id)

            async for m in sb_channel.history():
                if len(m.embeds) != 0:
                    raw = m.embeds[0].footer.text
                    try:
                        raw = raw.split(':')
                        if message.id == int(raw[2]):
                            return await m.edit(content=f'⭐**{reaction.count}** dans {channel.mention}',
                                                embed=starembed(message, author))
                    except:
                        pass

            have_content = False
            for l in message.content:
                if l != " ": have_content = True

            embed = embed_have_content(message, author, have_content)
            try:
                embed.set_image(url=message.attachments[0].url)
            except:
                pass

            return await sb_channel.send(content=f'⭐**{reaction.count}** dans {channel.mention}', embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.emoji.name != "⭐":
            return
        if payload.channel_id in self.protected_channels:
            return

        if self.bot.user.id == 762723841498677258:
            sb_channel = await self.bot.fetch_channel(self.starbotch_channel[True])
            guild = await self.bot.fetch_guild(752932746053025865)
        else:
            sb_channel = await self.bot.fetch_channel(self.starbotch_channel[False])
            guild = await self.bot.fetch_guild(625330528588922882)

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        author = await guild.fetch_member(message.author.id)
        reaction = get(message.reactions, emoji=payload.emoji.name)

        async for m in sb_channel.history():
            if len(m.embeds) != 0:
                raw = m.embeds[0].footer.text
                try:
                    raw = raw.split(':')
                    if message.id == int(raw[2]):
                        if reaction and reaction.count < 7:
                            if message.id in star_react:
                                star_react[message.id] += 1
                            else:
                                star_react[message.id] = 1

                            return await m.delete()
                        else:
                            return await m.edit(content=f'⭐**{reaction.count}** dans {channel.mention}',
                                                embed=starembed(message, author))
                except:
                    pass

    @commands.group(name='starbotch', aliases=["sb"])
    async def _starbotch_group(self, ctx):
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Starbotch help",
                color=discord.Color.gold()
            )
            embed.add_field(name="`?sb leaderboard` ou `?sb lb`",
                            value="Affiche le leaderboard du starbotch",
                            inline=False)
            embed.add_field(name="`?sb random` ou `?sb rd`",
                            value="Envoit un message du starbotch pris de façon farpaitement aléatoire.",
                            inline=False)

            admin = False
            admin_roles = [625332148265549844, 636302581949530122, 625333008542597122, 637277665182744636,
                           777247006954750023, 753273974623830078]
            for r in [role.id for role in ctx.author.roles]:
                if r in admin_roles:
                    admin = True
            if admin:
                embed.add_field(name='<:professionnel:777146313845506048> `?sb reload`',
                                value='Reload le leaderboard du starbotch',
                                inline=False)
            await ctx.send(embed=embed)

    async def sb_leaderboard(self):
        id_list = []
        score_dict = {}
        sb = self.bot.DBA.showallsb()
        for n, name in enumerate(sb):
            id_list.append(name)
            score_dict[n] = sb[name][1]

        sorted_keys = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
        score_list = []
        for i in sorted_keys:
            temp = i[0], i[1]
            score_list.append(temp)

        guild: discord.Guild = await self.bot.fetch_guild(self.guild[self.bot.test])

        embed = discord.Embed(
            title=" Starbotch leaderbaord",
            description="Yénenpoploudérire",
            color=discord.Color.gold()
        )
        for n in range(10):
            jump_url = sb[id_list[score_list[n][0]]][0]
            raw = jump_url.split("/")  # ['https:', '', 'discord.com', 'channels', '625330528588922882', '723202829665173615', '723202831531901020']
            channel: discord.TextChannel = await self.bot.fetch_channel(int(raw[5]))
            sb_message: discord.Message = await channel.fetch_message(id_list[score_list[n][0]])
            try:
                member = await guild.fetch_member(sb_message.author.id)
                name: str = member.nick if member.nick is not None else member.name
            except discord.NotFound:
                name: str = sb_message.author.mention
            embed.add_field(name=f"Top {str(n + 1)}",
                            value=f"Par {name.capitalize()} [avec {sb[id_list[score_list[n][0]]][1]}⭐]({sb[id_list[score_list[n][0]]][0]})",
                            inline=False)
        return embed

    @_starbotch_group.command(name='leaderboard', aliases=['lb'])
    async def _starbotch_leaderboard(self, ctx):
        await ctx.send(embed=self.sb_lb)

    @_starbotch_group.command(name='reload')
    async def _starbotch_reload(self, ctx):
        package.is_admin(ctx.author.roles)
        await ctx.send('Reloading the leaderboard ...')
        await ctx.channel.trigger_typing()
        counter = time.time()
        self.sb_lb = await self.sb_leaderboard()
        await ctx.send(content="Leaderboard reloaded in {}s !".format(round(time.time() - counter, 1)))

    @_starbotch_group.command(name='random', aliases=['rd'])
    async def _starbotch_random(self, ctx):
        sb = self.bot.DBA.showallsb()
        keys = list(sb.keys())
        jump_url, stars = sb[random.choice(keys)]
        raw = jump_url.split('/')
        channel = await self.bot.fetch_channel(int(raw[5]))
        message = await channel.fetch_message(int(raw[6]))
        embed = starembed(message, message.author)
        return await ctx.send(content=f'⭐**{stars}** dans {channel.mention}', embed=embed)


def setup(bot):
    bot.add_cog(Starbotch(bot))
