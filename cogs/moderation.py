import unidecode
import discord 

from dis_command.discommand.ext import cogs
from dis_command.discommand.ext import commands

from utils import permissions, default
from utils.predefiner import PredefinedActions


from exceptions import CantReachAPI

class Moderation(cogs.Cog):
	""" Various commands for moderators. """
	def __init__(self, bot):
		self.client = bot

	@commands.command()
	async def kick(self, bot, ctx, member: discord.Member, reason: str = None):
		""" Kicks a user from the current server. """
		await permissions.check_permissions(ctx, kick_members=True)
		member = await bot.converter.member(ctx, member)

		await ctx.guild.kick(member, reason=default.responsible(ctx.author, reason))
		await ctx.send(default.actionmessage("kicked"))

	@commands.command(aliases=["nick"])
	async def nickname(self, bot, ctx, member: discord.Member, name: str = None):
		""" Nicknames a user from the current server. """
		await permissions.check_permissions(ctx, manage_nicknames=True)
		member = await bot.converter.member(ctx, member)
		
		await member.edit(nick=name, reason=default.responsible(ctx.author, "Changed by nickname command."))
		message = f"Reset `{member.name}`s nickname" if not name else f"Changed `{member.name}`s nickname to **{name}**"
		await ctx.send(message)

	@commands.command()
	async def mute(self, bot, ctx, member: discord.Member, reason: str = None):
		""" Mutes a user from the current server. """
		await permissions.check_permissions(ctx, manage_roles=True)
		member = await bot.converter.member(ctx, member)

		mute_role = None
		for role in ctx.guild.roles:
			if role.name.lower() == "muted":
				mute_role = role

		predefined = PredefinedActions(mute_role) # mute_role will be the data passed down when looking for collection triggers
		predefined.make_collection(
			mute_role, # pass yet again to be used when looking for action triggers
			mute_role.name if mute_role else None  # If this is None then role was not found and it will look for an action with the trigger None. 
		).add_action(
			trigger=mute_role if mute_role else 0, # Set the trigger to the role name if found, otherwise default to 0 to make inaccessible (mute_role cannot ever return 0). 
			action=[
				member.add_roles(mute_role, reason=default.responsible(ctx.author, reason)),
				ctx.send(default.actionmessage("muted"))
				]
		).add_action(
			trigger=None, # Set the trigger to None, which means this action will be triggered if `mute_role` is unchanged (None). 
			action=ctx.send("Are you sure you've made a role called **muted**?"))

		await predefined.run()

	@commands.command()
	async def unmute(self, bot, ctx, member: discord.Member, reason: str = None):
		""" Mutes a user from the current server. """
		await permissions.check_permissions(ctx, manage_roles=True)
		member = await bot.converter.member(ctx, member)

		mute_role = None
		for role in ctx.guild.roles:
			if role.name.lower() == "muted":
				mute_role = role
		if not mute_role:
			return await ctx.send("Are you sure you've made a role called **Muted**?S")
		await member.remove_roles(mute_role, reason=default.responsible(ctx.author, reason))
		await ctx.send(default.actionmessage("unmuted"))

	@commands.command()
	async def ban(self, bot, ctx, member: discord.Member = None, reason: str = None):
		""" Bans a user from the current server. """
		await permissions.check_permissions(ctx, ban_members=True)
		if member is None:
			return await ctx.send("You need to mention the person to ban.")
		member = await bot.converter.member(ctx, member)

		await ctx.guild.ban(member, reason=default.responsible(ctx.author, reason))
		await ctx.send(default.actionmessage("banned"))

	@commands.command()
	async def massban(self, bot, ctx, reason, members: int):
		""" Mass bans multiple members from the server. [IDS ONLY]"""
		await permissions.check_permissions(ctx, ban_members=True)
		
		for member_id in members:
			try:
				await ctx.guild.ban(discord.Object(id=int(member_id)), reason=default.responsible(ctx.author, reason))
			except ValueError:
				return await ctx.send("There was in invalid ID. Could not convert to integer, make sure all the IDs only have numbers in them.")
		await ctx.send(default.actionmessage("massbanned", mass=True))

	@commands.command()
	async def unban(self, bot, ctx, member: int, reason: str = None):
		""" Unbans a user from the current server. """
		await permissions.check_permissions(ctx, ban_members=True)
		member = await bot.converter.integer(ctx, member)
		
		if member is None:
			return await ctx.send("You need to give the ID of the person to unban.")
		member = await bot.converter.integer(ctx, member)

		await ctx.guild.unban(discord.Object(id=member), reason=default.responsible(ctx.author, reason))
		await ctx.send(default.actionmessage("unbanned"))

	@commands.group()
	async def role(self, bot, ctx):
		"""Roles commands"""
		await ctx.show_help(self)

	@role.command(name='add')
	async def addrole(self, bot, ctx, member: discord.Member, rolename: str, reason: str = None):
		""" Add a role to someone else. """
		await permissions.check_permissions(ctx, manage_roles=True)
		member = await bot.converter.member(ctx, member)

		role = discord.utils.find(lambda m: rolename.lower(
		) in m.name.lower(), ctx.message.guild.roles)
		if not role:
			return await ctx.send('That role does not exist.')
		await member.add_roles(role, reason=default.responsible(ctx.author, reason))
		await ctx.send(f'Added: `{role.name}`')

	@role.command(name='massadd')
	async def massaddrole(self, bot, ctx, rolename: str, reason: str = None):
		''' Mass add roles to everyone. '''
		await permissions.check_permissions(ctx, manage_roles=True)

		role = discord.utils.find(lambda m: rolename.lower(
		) in m.name.lower(), ctx.message.guild.roles)
		if not role:
			return await ctx.send('That role does not exist.')
		for member in ctx.message.guild.members:
			try:
				await member.add_roles(role, reason=default.responsible(ctx.author, reason))
			except:
				await ctx.send(f"I don't have the perms to add that role to {member.name}.")
		await ctx.send("Done.")

	@role.command(name='remove')
	async def removerole(self, bot, ctx, member: discord.Member, rolename: str, reason: str = None):
		""" Remove a role from someone else. """
		await permissions.check_permissions(ctx, manage_roles=True)
		member = await bot.converter.member(ctx, member)
		if reason == None:
			reason 
		
		role = discord.utils.find(lambda m: rolename.lower(
		) in m.name.lower(), ctx.message.guild.roles)
		if not role:
			return await ctx.send('That role does not exist.')
		await member.remove_roles(role, reason=default.responsible(ctx.author, reason))
		await ctx.send(f'Removed: `{role.name}`')

	@commands.command()
	async def decancer(self, bot, ctx, member : discord.Member):
		""" Strips a user of all ascii if you have the permissions, or if you dont; sends the stripped version."""
		member = await bot.converter.member(ctx, member)
		
		if ctx.me.permissions_in(ctx.channel).manage_nicknames and ctx.author.permissions_in(ctx.channel).manage_nicknames:
			cancer = member.display_name
			decancer = unidecode.unidecode_expect_nonascii(cancer)
			if len(decancer) > 32:
				decancer = decancer[0:32-3] + "..."
			try:
				await member.edit(nick=decancer)
				await ctx.send(f"Changed {member.name}'s nickname from `{cancer}` to `{decancer}`.")
			except discord.Forbidden:
				await ctx.send("I dont have the correct permissions to do this, make sure i have `Manage Nicknames` or that my role is higher than the member's highest role")
		else:
			cancer = member.display_name
			decancer = unidecode.unidecode_expect_nonascii(cancer)
			await ctx.send(f'The decancered version of `{cancer}` is `{decancer}`.')

def export(bot):
	exports = {
		"cog": Moderation(bot),
		"name": "Moderation"
	}
	return exports