import discord

from config.config import prefix_limit

from dis_command.discommand.ext import cogs
from dis_command.discommand.ext import commands

from utils.embed import Embed
from utils import (
	permissions,
	api,
	checks
)


class Config(cogs.Cog):
	""" Various commands that control the configuration of the bot and its workings."""

	def __init__(self, bot):
		pass

	@commands.group("prefix")
	async def prefix(self, bot, ctx):
		''' Command group that configures the prefixes. '''
		await ctx.show_help(self)

	@prefix.command("add", name="add")
	async def prefixadd(self, bot, ctx, prefix: str):
		''' Add a new prefix. '''
		await permissions.check_permissions(ctx, manage_roles=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"
		actions = {
			"clash": ctx.send("Given prefix clashes with already existing prefix."),
			"limit": ctx.send(f"This guild is at the prefix limit ({prefix_limit})"),
			True:    ctx.send(f"Prefix `{prefix.strip()}` has been added")
		}

		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200])
		connection.set_default_action(ctx.send("The API sent back an un-expected response."))

		await connection.post(require_json=True, json={"op": prefix.strip()})

	@prefix.command("remove", name="remove")
	async def prefixremove(self, bot, ctx, prefix: str):
		''' Remove a custom prefix. '''
		await permissions.check_permissions(ctx, manage_roles=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"
		
		connection = api.InternalApiConnection(ctx, URI).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		resp = (await connection.post(require_json=True, json={"op": prefix.strip()})).expect_json_key("op").expect_json_value("op", True, True)
		if resp == True: # NOTE: should never be anything except true, because it SHOULD error before it has the chance to reach the
			await ctx.send(f"Prefix `{prefix.strip()}` has been removed.")


	@commands.group("modlist")
	async def modlist(self, bot, ctx):
		''' Command group that configures the known moderators. '''
		await ctx.show_help(self)

	@modlist.command("add", name="add")
	async def modadd(self, bot, ctx, member: discord.Member):
		''' Add a new mod. '''
		await permissions.check_permissions(ctx, manage_server=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"
		member = await bot.converter.member(ctx, member)

		actions = {
			"clash": ctx.send("User is already in the mod list."),
			"limit": ctx.send(f"This guild is at the moderator limit (NOTSETYOUSHOULDNTSEETHIS)"),
			True:    ctx.send(f"Moderator `{member.display_name}` has been added")
		}

		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200])
		connection.set_default_action(ctx.send("The API sent back an un-expected response."))

		await connection.post(require_json=True, json={"op": member.id})

	@modlist.command("remove", name="remove")
	async def modremove(self, bot, ctx, member: discord.Member):
		''' Remove a mod from the list. '''
		await permissions.check_permissions(ctx, manage_server=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"
		member = await bot.converter.member(ctx, member)

		connection = api.InternalApiConnection(ctx, URI).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		resp = (await connection.post(require_json=True, json={"op": member.id})).expect_json_key("op").expect_json_value("op", True, True)
		if resp == True: # NOTE: should never be anything except true, because it SHOULD error before it has the chance to reach the
			await ctx.send(f"Mod `{member.display_name}` has been removed from the list.")

	@modlist.command("get", name="list")
	async def listmods(self, bot, ctx):
		''' Lists the current known moderators in the list. '''
		await permissions.check_permissions(ctx, manage_server=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"

		connection = api.InternalApiConnection(ctx, URI).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		resp = (await connection.post(require_json=True, json={"op": None})).expect_json_key("op", True)
		embed = Embed(ctx.channel, title="Currently known moderators.")
		for uid in resp:
			await embed.add_to_description(f"{bot.get_user(uid).mention} ({uid})\n")

		await embed.send()

	@commands.group("adminlist")
	async def adminlist(self, bot, ctx):
		''' Command group that configures the known admins. '''
		await ctx.show_help(self)

	@adminlist.command("add", name="add")
	async def adminadd(self, bot, ctx, member: discord.Member):
		''' Add a new admin. '''
		await permissions.check_permissions(ctx, manage_server=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"
		member = await bot.converter.member(ctx, member)

		actions = {
			"clash": ctx.send("User is already in the admin list."),
			"limit": ctx.send(f"This guild is at the admin limit (NOTSETYOUSHOULDNTSEETHIS)"),
			True:    ctx.send(f"Admin `{member.display_name}` has been added.")
		}

		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200])
		connection.set_default_action(ctx.send("The API sent back an un-expected response."))

		await connection.post(require_json=True, json={"op": member.id})

	@adminlist.command("remove", name="remove")
	async def adminremove(self, bot, ctx, member: discord.Member):
		''' Remove an admin from the list. '''
		await permissions.check_permissions(ctx, manage_server=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"
		member = await bot.converter.member(ctx, member)

		connection = api.InternalApiConnection(ctx, URI).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		resp = (await connection.post(require_json=True, json={"op": member.id})).expect_json_key("op").expect_json_value("op", True, True)
		if resp == True: # NOTE: should never be anything except true, because it SHOULD error before it has the chance to reach the
			await ctx.send(f"Admin `{member.display_name}` has been removed from the list.")

	@adminlist.command("get", name="list")
	async def listadmins(self, bot, ctx):
		''' Lists the current known admins in the list. '''
		await permissions.check_permissions(ctx, manage_server=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"

		connection = api.InternalApiConnection(ctx, URI).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		resp = (await connection.post(require_json=True, json={"op": None})).expect_json_key("op", True)
		embed = Embed(ctx.channel, title="Currently known admins.")
		for uid in resp:
			await embed.add_to_description(f"{bot.get_user(uid).mention} ({uid})\n")

		await embed.send()
	@commands.group("panic")
	async def panic(self, bot, ctx):
		''' Command group that configures the panic feature. '''
		await ctx.show_help(self)
	
	@panic.command("toggle", name="toggle")
	async def panictoggle(self, bot, ctx):
		''' Toggle panic on/off. '''
		await permissions.check_permissions(ctx, manage_roles=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"

		actions = {
			0: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} has been enabled."),
			1: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} has been disabled."),
			2: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} config has been populated, please run any commands again.")}
	
		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		await connection.post(require_json=True, json={"op": None})

	@panic.command("message_limit", name="mlimit")
	async def panicmessage(self, bot, ctx, limit: int = None):
		''' Change the message limit per 5 seconds until the bot panics and starts muting people. '''
		await permissions.check_permissions(ctx, manage_roles=True)
		limit = await bot.converter.integer(limit) or None
		if limit == None:
			current = bot.db.query_row("SELECT message_limit FROM panic WHERE guild = ?", ctx.guild.id)
			if not current:
				return await ctx.send("There is no limit currently, please run the toggle command to initialize the panic config.")
			else:
				return await ctx.send(f"Your current message limit (per 5 seconds) is: `{current}`")
		if limit >= 1000:
			return await ctx.send("Sorry, you need to choose a number smaller than 1000.")
		
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"

		connection = api.InternalApiConnection(ctx, URI).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		(await connection.post(require_json=True, json={"op": limit})).expect_json_key("op").expect_json_value("op", True)

		await ctx.send(f"{ctx.command.parent.endpoint.capitalize()} message limit has been set to {limit}.")



	@commands.group("log")
	async def log(self, bot, ctx):
		''' Command group that configures the logging. '''
		await ctx.show_help(self)
	
	@log.command("toggle", name="toggle")
	async def logtoggle(self, bot, ctx):
		''' Toggle logging on/off. '''
		await permissions.check_permissions(ctx, manage_roles=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"
		
		actions = {
			0: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} has been enabled."),
			1: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} has been disabled."),
			2: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} config has been populated, please run any commands again.")}
		
		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		await connection.post(require_json=True, json={"op": None})

	@log.command("channel", name="channel")
	async def logchannel(self, bot, ctx, channel: discord.abc.GuildChannel):
		''' Change the channel logs go to. '''
		await permissions.check_permissions(ctx, manage_roles=True)
		channel = await bot.converter.channel(ctx, channel)
		if channel.permissions_for(ctx.guild.me).manage_webhooks == False:
			return await ctx.send("I do not have permissions to manage webhooks in that channel.")
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"
		
		actions = {
			True: ctx.send(f"Channel has been set to {channel.mention}"),
			2: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} config has been populated, please run any commands again.")}
		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))

		await ctx.send("Creating webhook...")
		async with ctx.channel.typing():
			webhook = await channel.create_webhook(name=bot.user.name, avatar=bot.avatar_data)
			await connection.post(require_json=True, json={"op": webhook.url})

	@commands.group("welcome")
	async def welcome(self, bot, ctx):
		''' Command group that configures the auto-welcome. '''
		await ctx.show_help(self)
	
	@welcome.command("toggle", name="toggle")
	async def welcometoggle(self, bot, ctx):
		''' Toggle auto-welcome on/off. '''
		await permissions.check_permissions(ctx, manage_roles=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"

		actions = {
			0: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} has been enabled."),
			1: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} has been disabled."),
			2: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} config has been populated, please run any commands again.")}
		
		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		await connection.post(require_json=True, json={"op": None})

	@welcome.command("embed", name="embed")
	async def welcomeembed(self, bot, ctx):
		''' Toggle if the join message is an embed or not. '''
		await permissions.check_permissions(ctx, manage_roles=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"

		actions = {
			0: ctx.send(f"{self.endpoint.capitalize()} has been enabled."),
			1: ctx.send(f"{self.endpoint.capitalize()} has been disabled."),
			2: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} config has been populated, please run any commands again.")}
		
		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		await connection.post(require_json=True, json={"op": None})

	@welcome.command("channel", name="channel")
	async def welcomechannel(self, bot, ctx, channel: discord.abc.GuildChannel):
		''' Change the channel join messages go to. '''
		await permissions.check_permissions(ctx, manage_roles=True)
		channel = await bot.converter.channel(ctx, channel)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"

		actions = {
			True: ctx.send(f"Channel has been set to {channel.mention}"),
			2: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} config has been populated, please run any commands again.")}
		
		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		await connection.post(require_json=True, json={"op": None})


	@welcome.command("message", name="message")
	async def welcomemessage(self, bot, ctx, message: str = None):
		''' Change the content of the join message. '''
		await permissions.check_permissions(ctx, manage_roles=True)
		if not message: # Go back to the default message
			message = "Welcome {{user}}!"
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"

		actions = {
			True: ctx.send(f"Message has been set to:\n```{message}```"),
			2:    ctx.send(f"{ctx.command.parent.endpoint.capitalize()} config has been populated, please run any commands again.")}
		
		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		await connection.post(require_json=True, json={"op": None})

	@commands.group("antialt")
	async def antialt(self, bot, ctx):
		''' Command group that configures anti-alt. '''
		await ctx.show_help(self)
	
	@antialt.command("toggle", name="toggle")
	async def antialttoggle(self, bot, ctx):
		''' Toggle anti-alt on/off. '''
		await permissions.check_permissions(ctx, manage_roles=True)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"

		actions = {
			0: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} has been enabled."),
			1: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} has been disabled."),
			2: ctx.send(f"{ctx.command.parent.endpoint.capitalize()} config has been populated, please run any commands again.")}
		
		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		await connection.post(require_json=True, json={"op": None})

	@antialt.command("days", name="days")
	async def antialtdays(self, bot, ctx, time_in_days: int):
		''' Change the account age (in days) it takes to trigger the anti-alt. '''
		await permissions.check_permissions(ctx, manage_roles=True)
		days = await bot.converter.integer(time_in_days)
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"

		actions = {
			-1:   ctx.send("Error while converting to integer."),
			True: ctx.send(f"Time has been set to {days}.")
		}
		
		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		await connection.post(require_json=True, json={"op": days})

	@commands.group("strictmodactions", name="strictmodactions")
	async def modonlyactions(self, bot, ctx):
		''' Configures the mod-only actions system. '''
		await ctx.show_help(self)

	@modonlyactions.command("toggle", name="toggle")	
	async def modonlyactionstoggle(self, bot, ctx):
		''' Toggle strict moderation actions on/off. (mod/admin commands must be done by users in the modlist or adminlist) '''
		await permissions.check_permissions(ctx, manage_server=True)
		if ctx.author.id != ctx.guild.owner.id:
			return await ctx.send("This command can only be ran by the Guilds OWNER.")
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"

		actions = {
			0: ctx.send(f"{ctx.command.endpoint.capitalize()} has been enabled."),
			1: ctx.send(f"{ctx.command.endpoint.capitalize()} has been disabled."),
			2: ctx.send(f"{ctx.command.endpoint.capitalize()} config has been populated, please run any commands again.")}
	
		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		await connection.post(require_json=True, json={"op": None})

	@modonlyactions.command("premium", name="premium")
	async def modonlyactionspremium(self, bot, ctx):
		''' Toggle premium strict moderation actions on/off. (mod/admin actions must be done by users in the modlist or adminlist, through the entire server, or they will be stripped of their roles/perms) '''
		await permissions.check_permissions(ctx, manage_server=True)
		if ctx.author.id != ctx.guild.owner.id:
			return await ctx.send("This command can only be ran by the Guilds OWNER.")
		URI = f"{bot.config.api_url}/{ctx.command.parent.endpoint}/{ctx.guild.id}/{self.endpoint}"

		actions = {
			0: ctx.send(f"{self.endpoint.capitalize()} has been enabled."),
			1: ctx.send(f"{self.endpoint.capitalize()} has been disabled."),
			2: ctx.send(f"{ctx.command.endpoint.capitalize()} config has been populated, please run any commands again.")}
	
		connection = api.InternalApiConnection(ctx, URI).predefine_json_actions("op", actions).expect_status_codes([200]).set_default_action(ctx.send("The API sent back an un-expected response."))
		await connection.post(require_json=True, json={"op": None})

# TODO: AUTOROLE, REACTIONROLE


def export(bot):
	exports = {
		"cog": Config(bot),
		"name": "Settings"
	}
	return exports