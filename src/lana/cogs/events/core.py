import traceback

import context
import discord
from dis_command.discommand.ext import cogs, events
from dis_command.discommand.ext.events import process_message
from utils import db

from lana.exceptions import (
    ArgConvertError,
    CantReachAPI,
    CommandCheckError,
    PremiumCheckError,
    StrictActionCheckError,
)


class CoreEvents(cogs.Cog):
    def __init__(self, client):
        self.client = client

    @events.register()
    async def on_command_error(self, ctx, err):
        if isinstance(err, CantReachAPI) or isinstance(err, ConnectionRefusedError):
            return await ctx.send("The bot cannot reach its API right now, so it cannot make changes to configs.")

        elif isinstance(err, discord.Forbidden):
            embed = discord.Embed(description="Not enough perms to execute this command.")
            return await ctx.send(embed=embed)

        elif isinstance(err, StrictActionCheckError):
            embed = discord.Embed(
                description="This server has Strict Moderation Actions on: and you are not in the list of known moderators/admins."
            )
            return await ctx.send(embed=embed)

        elif isinstance(err, ArgConvertError):

            _traceback = traceback.format_tb(err.__traceback__)
            _traceback = "".join(_traceback)
            error = ("```py\n{0}\n```").format(err)
            embed = discord.Embed(title="Error :(", description=f"BadArgument\n{error}", color=0xFFFFFF)
            embed.set_footer(text=f"Lana")
            return await ctx.send(embed=embed)  # u s e r   f r i e n d l y

        elif isinstance(err, discord.errors.Forbidden):
            return await ctx.send(
                "Either you, or i, do not have the permissions to do this, please make sure we both have the relevent permissions for the command."
            )

        elif isinstance(err, CommandCheckError):
            embed = discord.Embed(
                title="No perms?",
                description=f"Seems you tried to use a command that requires either more permissions or owner",
                color=0xFFFFFF,
            )
            return await ctx.send(embed=embed)
        elif isinstance(err, PremiumCheckError):
            return await ctx.send(embed=discord.Embed(description=f"This command is requires premium (or a higher level)"))

        elif isinstance(err, TypeError) and "positional" in str(err):
            print(err)
            await ctx.send("You arent giving required arguments! Here is the help for this command.")
            return await ctx.show_help(ctx.command)

        await ctx.send(
            "You have stumbled upon an uncaught error, the devs have been notified!\nDont panic if one of them joins the server to check out what was going on during/before the error happened."
        )
        if self._is_main_instance:
            await self.error_channel.send(f"New uncaught error in {ctx.guild.name} ({ctx.guild.id}):\n{err}")
        elif not self._is_main_instance and self._parent_instance:
            self._parent_instance.put(f"New uncaught error in {ctx.guild.name} ({ctx.guild.id}):\n{err}")
        raise err

    @events.register()
    async def on_overload_notice(self, guild: discord.Guild, channel: discord.TextChannel):
        return await channel.send(
            "The bot has detected a raid/massive influx of messages, and is temporarily shutting down for this guild.\nPlease enable the `panic` feature to enable a system like this for anti-raid protection."
        )
        # TODO: stuff

    @events.register()
    async def message_edit(self, before, after):
        """Reads edited messages"""
        if before.author.bot:
            return
        prefix = await self.get_prefix(after)
        command, _context = process_message(self, prefix, after, context=context.Context)
        if command and _context:
            await command.invoke(self, _context)

    @events.register()
    async def on_message(self, message: discord.Message):
        """Message handler to process commands.

        Args:
                message (discord.Message): The message to process.
        """
        if message.author.bot:
            return
        prefix = await self.get_prefix(message)
        command, _context = events.process_message(self, prefix, message, context=context.Context)
        if command and _context:
            await command.invoke(self, _context)

    @events.register()
    async def on_shutdown(self, *args):
        self.db.pool.close()
        exit(0)

    @events.register()
    async def on_guild_remove(self, guild):
        self.db.execute("DELETE FROM guilds WHERE id = ?", guild.id)

    @events.register()
    async def on_guild_join(self, guild):
        log = self.get_channel(self.config.output_channel)
        try:
            self.db.execute("INSERT INTO guilds (id) VALUES (?)", guild.id)
        except Exception as e:
            await log.send(f"Error! Failed to add guild to bot database: {e}")
            try:
                await guild.owner.send("Bot was unable to add Guild ID to database, and will leave. Please contact the bot owners.")
            except:
                pass
            await guild.leave()
        members = set(guild.members)
        bots = filter(lambda m: m.bot, members)
        bots = set(bots)
        members = len(members) - len(bots)
        invite_msg = ""
        sketchy_msg = ""
        embed = discord.Embed(description="Hello! my prefix is 'lana.', to get started use 'lana.help'")
        try:
            to_send = sorted(
                [chan for chan in guild.channels if chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)],
                key=lambda x: x.position,
            )[0]
            await to_send.send(embed=embed)
        except Exception as e:
            try:
                await guild.owner.send(embed=embed)
            except Exception as e:
                pass
        try:
            invite_chan = sorted(
                [
                    chan
                    for chan in guild.channels
                    if chan.permissions_for(guild.me).create_instant_invite and isinstance(chan, discord.TextChannel)
                ],
                key=lambda x: x.position,
            )[0]
            invite = await invite_chan.create_invite(reason="Invite for devs")
        except:
            invite_msg += "**Invite Unavailable**"
        else:
            invite_msg += f"[**Guild Invite**]({invite})"
        if len(bots) > members:
            sketchy_msg += "\nBot farm alert <@!309025661031415809> <@320576655620046860>"
        else:
            sketchy_msg += ""

        join = discord.Embed(
            title="Added to Guild",
            description=f"» Name: {guild.name}\n» ID: {guild.id}\n» Members/Bots: `{members}:{len(bots)}`\n» Owner: {guild.owner}{sketchy_msg}\n\n{invite_msg}",
            color=discord.Color.dark_green(),
        )
        join.set_thumbnail(url=guild.icon)
        join.set_footer(text=f"Total Guilds: {len(self.guilds)}")
        await log.send(embed=join)


def export(bot):
    events = CoreEvents(bot)
    exports = {"cog": events, "name": "Core Events"}
    return exports
