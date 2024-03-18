import asyncio
import re
import subprocess
from asyncio import sleep
from copy import copy
from os import system

from context import Context
from dis_command.discommand.ext import cogs, commands, events
from discord import Member
from exceptions import ArgConvertError

from lana.utils import permissions
from lana.utils.embed import Embed

# from config.config import owners


class Owner(cogs.Cog):
    def __init__(self, bot):
        self.client = bot
        self._GIT_PULL_REGEX = re.compile(r"\s*(?P<filename>.+?)\s*\|\s*[0-9]+\s*[+-]+")

    async def run_process(self, command):
        try:
            process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await process.communicate()
        except NotImplementedError:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await self.client.loop.run_in_executor(None, process.communicate)

        return [output.decode() for output in result]

    @commands.command(aliases=["lt"])
    async def lagtest(self, bot, ctx, how_many: int):
        if ctx.author.id not in bot.config.owners or not permissions.is_owner(ctx):
            return await ctx.send("This command is owner only.")
        how_many = await bot.converter.integer(ctx, how_many)

    @commands.command(aliases=["su", "sudo"])
    async def impersonate(self, bot, ctx, who: Member, content: str):
        if ctx.author.id not in bot.config.owners or not permissions.is_owner(ctx):
            return await ctx.send("This command is owner only.")
        member = await bot.converter.member(ctx, who)

        new_message = copy(ctx.message)
        new_message.author = member
        new_message.content = f"{ctx.prefix[0]}{content}"

        command, _context = events.process_message(bot, ctx.prefix, new_message, context=Context)
        if command and _context:
            await ctx.send(f"Running {command.name} as {member.display_name}")
            return await command.invoke(bot, _context)
        else:
            return await ctx.send(f"Command was not found.\nForged content: `{new_message.content}`")

    @commands.command()
    async def update(self, bot, ctx, to_reload: bool = False):
        if ctx.author.id not in bot.config.owners or not permissions.is_owner(ctx):
            return await ctx.send("This command is owner only.")
        try:
            to_reload = await bot.converter.boolean(to_reload)
        except ArgConvertError:
            pass
        await ctx.send("Stashing and pulling from github...")
        system("git stash")
        system("git pull")
        if to_reload:
            await ctx.send("Reloading bot...")
            bot.all_commands["reload"].invoke(bot, ctx)  # FIXME: make not hardcode

    @commands.command(aliases=["rel"])
    async def reload(self, bot, ctx):
        """No-Downtime reloading of configs, cogs, commands, and events entirely."""
        if ctx.author.id not in bot.config.owners or not permissions.is_owner(ctx):
            return await ctx.send("This command is owner only.")

        embed = Embed(ctx.channel, title="Starting reload...")
        await embed.send()

        await ctx.send("Waiting 6 seconds for any running tasks/commands to finish...", delete_after=6)
        await sleep(6)

        await embed.add_to_description("[0] Unloading cogs/events...")
        await bot.cog_manager.unload_cogs()

        await ctx.send("Waiting 6 seconds for any running tasks/commands to finish...", delete_after=6)
        await sleep(6)

        await embed.add_to_description("[1] Reloading config data...")
        try:
            from config import config

            bot.config = config.BotConfig()
        except:
            await embed.add_to_description("[1E] Error loading config, shutting down...")
            await ctx.message.add_reaction("\u274C")
            await bot.logout()

        await embed.add_to_description("[1.5] Syncing guilds to database...")
        await bot.syncer(bot.db, bot)

        await embed.add_to_description("[2] Reloading discommand and cogs/events...")
        cached_paths = copy(bot.cog_manager.cached_paths)
        try:
            from dis_command.discommand.ext.cog_manager import CogManager
            from dis_command.discommand.ext.event_manager import EventManager

            bot.cog_manager = CogManager(bot)
            bot.event_manager = EventManager(bot)
            for path in cached_paths:
                await bot.cog_manager.load_cogs(path, update_commands=False)
        except Exception as e:
            await embed.add_to_description("[2E] Error reloading discommand, shutting down...")
            await ctx.message.add_reaction("\u274C")
            await ctx.send(e)
            await bot.logout()
        await embed.add_to_description("[2.5] Loaded cogs/events from cached paths...")

        await embed.add_to_description("[3] Updating internal command list...")
        bot.cog_manager.update_all_commands()
        await embed.set_title("Reload finished.")
        return await ctx.send("Bot has reloaded!", delete_after=12)


def export(bot):
    exports = {"cog": Owner(bot), "name": "Owner"}
    return exports
