from discord.ext import commands
import package
import discord


class Vocal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = {True: 752932746053025865, False: 625330528588922882}
        self.file = "vocal"

    @commands.group(name="vocal")
    async def _vocal_core(self, ctx):
        await ctx.message.delete()
        package.is_admin(ctx.author.roles)
        if ctx.invoked_subcommand is None:
            package.is_admin(ctx.author.roles)
            embed = discord.Embed(
                title="Help vocal",
                color=discord.Colour.from_rgb(255, 0, 21)
            )
            embed.add_field(name="`?vocal status`",
                            value="Affiche le status des channel vocaux", inline=False)
            embed.add_field(name="`?vocal ban <id/@cible>`",
                            value="Ban quelqu'un des channels vocaux", inline=False)
            embed.add_field(name="`?vocal unban <id/@cible>`",
                            value="J'ai besoin de m'expliquer ?", inline=False)
            await ctx.send(embed=embed)

    @_vocal_core.command(name="status")
    async def _vocal_status(self, ctx):
        members = 0
        embed = discord.Embed(title="Vocal status",
                              color=discord.Colour.from_rgb(255, 0, 21))
        for channel in ctx.guild.voice_channels:
            embed.add_field(name=channel.name, value=f"{len(channel.members)} personne{'s' if len(channel.members) > 1 else ''} connecté{'s' if len(channel.members) > 1 else ''}", inline=False)
            members += len(channel.members)
        embed.description = f"{members} personne{'s' if len(channel.members) > 1 else ''} connecté{'s' if len(channel.members) > 1 else ''} sur {len(ctx.guild.voice_channels)} channels vocaux"
        await ctx.send(embed=embed)

    @_vocal_core.command(name="ban")
    async def _vocal_ban(self, ctx, member_id):
        try: member = ctx.guild.fetch_member(int(member_id))
        except:
            try: member = ctx.message.mentions[0]
            except: return await ctx.send("Vous devez mentionner ou donner l'id du membre à ban")

        await member.move_to(await self.bot.fetch_channel(702436185162776586))

        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(member, connect=False)

        await ctx.send(f"{member.mention} est banni de toute les channel vocaux... nothing personal kid")

    @_vocal_core.command(name="unban")
    async def _vocal_unban(self, ctx, member_id):
        try: member = ctx.guild.fetch_member(int(member_id))
        except:
            try: member = ctx.message.mentions[0]
            except: return await ctx.send("Vous devez mentionner ou donner l'id du membre à déban")

        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(member, connect=True)

        await ctx.send(f"{member.mention} est débanni de toute les channel vocaux... t'as plus interet à faire le con")


def setup(bot):
    bot.add_cog(Vocal(bot))
