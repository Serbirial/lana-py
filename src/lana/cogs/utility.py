import discord
from dis_command.discommand.ext import cogs, commands

from lana.utils import checks, permissions

# from aiohttp.client_exceptions import ClientConnectorError


# from exceptions import CantReachAPI


class Utility(cogs.Cog):
    """Various commands that can be very handy."""

    def __init__(self, bot):
        self.client = bot

    @commands.command(aliases=["pruneestimate"])
    async def estimatepruned(self, bot, ctx, days: int = 7):
        """Will tell you now many members would be pruned in X days, defaults to 7 days."""
        days = await bot.converter.integer(ctx, days)

        if days > 30:
            return await ctx.send("Number of days should be below 30.")
        try:
            pruned = await ctx.guild.estimate_pruned_members(days=days)
            msg = f"If you pruned for {days} days it would kick {pruned} members"
            if days == 1:
                msg = msg.replace("days", "day")
            if pruned == 1:
                msg = msg.replace("members", "member")
            await ctx.send(msg)
        except discord.Forbidden:
            await ctx.send("Failed due to lack of permissions. I need to be able to access the prune feature to estimate it.")

    @commands.command(aliases=["stealemoji"])
    async def emojisteal(self, bot, ctx, emoji: discord.PartialEmoji):
        """Steals an emoji"""
        if checks.strict_actions(ctx):
            checks.is_known_mod(ctx, ctx.author.id)
        await permissions.check_permissions(ctx, bot.config.owners, manage_server=True)
        emoji = await bot.converter.emoji(ctx, emoji)

        prompt = await ctx.prompt(
            message="Are you sure? this will steal that emoji with the same exact name, you have 10 seconds to confirm or deny.",
            delete_after=True,
            embed=True,
            author_id=ctx.author.id,
            timeout=10,
        )
        if prompt:
            msg = await ctx.send("Confirmed.")
            async with ctx.channel.typing():
                emj_bytes = await emoji.read()
                try:
                    await ctx.guild.create_custom_emoji(name=emoji.name, image=emj_bytes)
                except discord.Forbidden:
                    await msg.delete()
                    return await ctx.send("I do not have permissions to manage emojis.")
            await msg.edit(content="Done.")
        elif not prompt:
            return await ctx.send("Aborting.")

    @commands.command(aliases=["bc"])
    async def botclear(self, bot, ctx, limit: int = 50):
        """Clears the given number of messages from bots, defaults to 50"""
        await permissions.check_permissions(ctx, bot.config.owners, manage_messages=True)

        if limit > 500:
            return await ctx.send("Please choose a number lower than 500.")
        conf = await ctx.prompt(
            f"Are you sure? this will clear the last {limit} messages of bots, you have 10 seconds to confirm or deny.",
            delete_after=True,
            embed=True,
            author_id=ctx.author.id,
            timeout=10,
        )
        if conf:
            try:
                msg = await ctx.send(f"Trying to purge {limit} messages.")
                await ctx.message.delete()
                await msg.delete()
                async for message in ctx.channel.history(limit=limit):
                    if message.author.bot:
                        await message.delete()
                await ctx.send("Done", delete_after=5)
            except Exception as e:
                await ctx.send(e)
        else:
            return await ctx.send("Aborted.")

    @commands.command()
    async def purge(self, bot, ctx, limit: int = None):
        """Purges last 500~ ammount of messages."""
        await permissions.check_permissions(ctx, bot.config.owners, manage_messages=True)

        if not limit:
            await ctx.send("You didnt give a limit")
        if limit > 500:
            return await ctx.send(
                "The limit on purgable messages is set to 500 due to lag with logging. (if you have it on, and are constantly purging, consider turning logs off before doing so, `(prefix)log false`)"
            )
        msg = await ctx.send(f"Trying to purge {limit} messages.")
        await ctx.message.delete()
        await msg.delete()
        await ctx.channel.purge(limit=limit, bulk=True)
        await ctx.send("Done", delete_after=3)

    @commands.command()
    async def botperms(self, bot, ctx, limit: int = None):
        """Shows the current bot permissions."""
        print(ctx.channel.permissions_for(ctx.guild.me))


def export(bot):
    exports = {"cog": Utility(bot), "name": "Utility"}
    return exports
