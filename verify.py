import discord
import time
from discord.ext import commands
from importlib import reload
import os.path
import json
import urllib.request
from modules import checks
import requests

import modules.constants as c


class Verify(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(checks.channel_check_verify)
    async def verify(self, ctx):
        """Checks if a user has a verified email
        It compares it to a blacklist database to determine if the user is trustworthy.

        If the user hasn't been submitted for validation, a link will be provided so that the validation can take place.
        This happens through Discord Oauth2.

        Args:

            None

        Returns:

            True: If the user is determined to be trustworthy. The user will then automatically receive the verified role.

            False: If the user is not determined to be trustworthy. The user will then NOT receive the role.
        """
        embed = discord.Embed(color=0x0C8B18)
        self.ctx = ctx
        role = discord.utils.get(ctx.guild.roles, name=c.verified)
        guild = ctx.message.guild
        author = str(ctx.author)
        embed.title = f"{ctx.author.name}"
        if role in ctx.author.roles:
            embed.description = f"🇵🇹 Já estás verificado\n🇺🇸 You are already verified"
            return await ctx.send(embed=embed)
        if os.path.exists(c.detailfile):
            for line in open(c.detailfile, 'r'):
                data = json.loads(line)
                if data["Discord"] == author:
                    await ctx.author.add_roles(role)
                    embed.description = f"🇵🇹 Verificação completa!\n🇺🇸 Verification complete!"
                    return await ctx.send(embed=embed)

            embed.description = f"🇵🇹 Por favor verifique-se [aqui](https://discordapp.com/oauth2/authorize?response_type=code&client_id=517177680375054336&redirect_uri=http%3A%2F%2F46.101.184.126%3A5000%2Fcallback&scope=identify+email+connections+guilds) e volte a correr o comando `!verify`\n🇺🇸 Please complete the verification [here](https://discordapp.com/oauth2/authorize?response_type=code&client_id=517177680375054336&redirect_uri=http%3A%2F%2F46.101.184.126%3A5000%2Fcallback&scope=identify+email+connections+guilds) and run the `!verify` command again"
            return await ctx.send(embed=embed)
        else:
            await ctx.send("Error, file not exist")
            return "Error, file"

    @commands.command()
    @commands.check(checks.search_check)
    async def set_verified_role(self, ctx, newrole):
        try:
            checkrole = discord.utils.get(ctx.guild.roles, name=str(newrole))
            with open("constants.json", "r") as f:
                data = json.load(f)
            data['verified'] = newrole
            with open("constants.json", "w") as f:
                json.dump(data, f)
            reload(checks)
            c.verified = newrole
            return await ctx.send(f"New verified role set: {newrole}")
        except Exception as err:
            print(err)
            return await ctx.send("No role exists with that name.")

    @commands.command()
    @commands.check(checks.search_check)
    async def set_verify_channel(self, ctx, verifychannel):
        try:
            checkchannel = discord.utils.get(
                ctx.guild.channels, name=str(verifychannel))
            with open("constants.json", "r") as f:
                data = json.load(f)
            data['channel_verify'] = verifychannel
            with open("constants.json", "w") as f:
                json.dump(data, f)
            reload(checks)
            c.channel_verify = verifychannel
            return await ctx.send(f"New verified channel set: {verifychannel}")
        except Exception as err:
            print(err)
            return await ctx.send("No channel exists with that name.")

    @commands.command()
    @commands.check(checks.search_check)
    async def purge(self, ctx, limit: int = 99):
        limit = limit+1

        def check_msg(msg):
            return True
        deleted = await ctx.channel.purge(limit=limit, check=check_msg)
        msg = await ctx.send(f"Deleted Messages: {limit}")
        time.sleep(2)
        await msg.delete()

    @commands.command()
    @commands.check(checks.search_check)
    async def countrole(self, ctx, role):
        count = 0
        role = discord.utils.get(ctx.guild.roles, name=c.verified)
        for member in ctx.guild.members:
            for rol in member.roles:
                if role.id == rol.id:
                    count += 1

        await ctx.send(count)


def setup(bot):
    "reload"
    reload(checks)
    bot.add_cog(Verify(bot))
