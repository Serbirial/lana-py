import time
from datetime import datetime
import discord

import os
import platform
import psutil

from utils.predefiner import PredefinedActions

from dis_command.discommand.ext import cogs
from dis_command.discommand.ext import commands

from aiohttp.client_exceptions import ClientConnectorError
from asyncio.exceptions import TimeoutError 
from aiohttp import ClientTimeout

from exceptions import CantReachAPI

api_timeout = ClientTimeout(
	total=3, # total timeout (time consists connection establishment for a new connection or waiting for a free connection from a pool if pool connection limits are exceeded) default value is 5 minutes, set to `None` or `0` for unlimited timeout
	sock_connect=4, # Maximal number of seconds for connecting to a peer for a new connection, not given from a pool. See also connect.
	sock_read=5 # Maximal number of seconds for reading a portion of data from a peer
)

async def ping_api(ctx) -> int:
	connection = await ctx.create_api_connection()
	try:
		start = time.monotonic()
		async with connection.get(ctx.bot.config.api_url, timeout=api_timeout) as response:
			response_time = time.monotonic() - start
			await connection.close()
			return round(response_time * 500)
	except ClientConnectorError:
		await connection.close()
		raise CantReachAPI()
	except TimeoutError: 
		await connection.close()
		raise CantReachAPI

class Information(cogs.Cog):
	""" Various commands that control the configuration of the bot and its workings."""

	def __init__(self, bot):
		self.client = bot

	@commands.command()
	async def baninfo(self, bot, ctx, user_id: int):
		''' Gets a members ban info, user must be an id. '''
		user_id = await bot.converter.integer(ctx, user_id)
		ban = ctx.guild.fetch_ban(user_id)
		if not ban:
			return await ctx.send(f"No ban info found for id `{user_id}`")
		embed = discord.Embed(title=f"Ban info for {ban.user.display_name}")
		embed.add_field(name="User", value=f"{ban.user.display_name} ({ban.user.id})")
		embed.add_field(name="Reason", value=f"{ban.reason if ban.reason else 'No reason provided.'}")
		return await ctx.send(embed=embed)

	@commands.command()
	async def stats(self, bot, ctx):
		''' Gives you the bot statistics. '''
		cpu = f'{round(bot.process.cpu_percent() / psutil.cpu_count(), 1)}% ({psutil.cpu_count()} core/s)'
		used = round(psutil.virtual_memory()[3] / 1024**2)
		total = round(psutil.virtual_memory().total / 1024**2)
		ram = f'Lana: {round(bot.process.memory_full_info().rss / 1024**2)}MB\nGlobal usage: {used}MB/{total}MB ({total-used}MB free)'
		pythoninfo = f"Using python `{platform.python_version()}`"
		if os.name == "posix":
			data = platform.freedesktop_os_release()
			distro = f"Running on {data['NAME']}"
		else:
			distro = "Running on some windows machine..."
		delta = datetime.utcnow() - bot.uptime
		hours, remainder = divmod(int(delta.total_seconds()), 3600)
		minutes, seconds = divmod(remainder, 60)
		days, hours = divmod(hours, 24)
		if days:
			uptime = '{d} days, {h} hours, {m} minutes, and {s} seconds'
		else:
			uptime = '{h} hours, {m} minutes, and {s} seconds'

		embed = discord.Embed(description="Bot stats")
		embed.add_field(name="RAM", value=ram, inline=False)
		embed.add_field(name="CPU", value=cpu, inline=False)
		embed.add_field(name="OS", value=distro, inline=True)
		embed.add_field(name="Python", value=pythoninfo, inline=True)
		embed.add_field(name="Guilds:Users", value=f'{len(bot.guilds)}:{len(bot.users)}', inline=False)
		embed.add_field(name="Uptime", value=f"I have been running for {uptime.format(d=days, h=hours, m=minutes, s=seconds)}", inline=False)
		await ctx.send(embed=embed)

	@commands.command()
	async def ping(self, bot, ctx):
		""" Sends the bots ping """
		before = time.monotonic()
		message = await ctx.send("Hold on...")
		ping = (time.monotonic() - before) * 500
		await message.edit(content="A bit more...")  # first ping
		time.monotonic()
		ping2 = (time.monotonic() - before) * 500
		await message.edit(content="Almost there...")  # second ping
		shard = ""
		for i in bot.latencies:
			if i[0] == ctx.guild.shard_id:
				shard += f"Shard {i[0]}: `{round(i[1] * 500)}` ms\n"
			else:
				shard += f"Shard {i[0]}: `{round(i[1] * 500)}` ms\n"
		try:
			api_ping = f"{await ping_api(ctx)}ms"
		except CantReachAPI:
			api_ping = "Down."
		embed = discord.Embed(colour=0xFFFFFF, description=f"""
Round trip ping: {int(ping)}ms - {int(ping2)}ms
This shards heartbeat ping: {round(bot.latency * 500)}ms
API's ping: {api_ping}
		""")
		#embed.add_field(name="Shard ping", value=shard)
		#embed.set_footer(text=f'This guild is on shard {ctx.guild.shard_id}')
		await message.edit(content=None, embed=embed)

	@commands.command(aliases=['server', 'si', 'svi'])
	async def serverinfo(self, bot, ctx, server_id: int = None):
		'''See information about the server.'''
		server = bot.get_guild(server_id) or ctx.guild
		total_users = len(server.members)
		online = len(
			[m for m in server.members if m.status != discord.Status.offline])
		offline = len(
			[m for m in server.members if m.status == discord.Status.offline])
		text_channels = len(
			[x for x in server.channels if isinstance(x, discord.TextChannel)])
		voice_channels = len(
			[x for x in server.channels if isinstance(x, discord.VoiceChannel)])
		categories = len(server.channels) - text_channels - voice_channels
		passed = (ctx.message.created_at - server.created_at).days
		created_at = "Since {}. That's over {} days ago!".format(
			server.created_at.strftime("%d %b %Y %H:%M"), passed)

		data = discord.Embed(description=created_at, colour=0xFFFFFF)
		data.add_field(name="Users", value="Online:{}\nOffline:{}\nTotal:{}".format(online, offline, total_users))
		data.add_field(name="Text Channels", value=text_channels)
		data.add_field(name="Voice Channels", value=voice_channels)
		data.add_field(name="Categories", value=categories)
		data.add_field(name="Roles", value=len(server.roles))
		data.add_field(name="Owner", value=str(server.owner))
		data.set_footer(text="Server ID: " + str(server.id))
		data.set_author(name=server.name, icon_url=None or server.icon)
		data.set_thumbnail(url=None or server.icon)

		await ctx.send(embed=data)

	@commands.command(aliases=['ui', 'user'])
	async def userinfo(self, bot, ctx, member: discord.Member = None):
		'''Get information about a member of a server'''
		if not member:
			user = ctx.author
		elif member:
			user = await bot.converter.member(ctx, member)

		server = ctx.guild
		avi = user.avatar.url
		roles = sorted(user.roles, key=lambda c: c.position)

		for role in roles:
			if str(role.color) != "#000000":
				color = role.color
		if 'color' not in locals():
			color = 0

		rolenames = []
		for role in roles:
			if len(''.join(rolenames)) > 20:
				rolenames = ["...Too many roles to list"]
				break
			elif role != "@everyone":
				rolenames.append(role.name)
		time = ctx.message.created_at
		desc = '{0} is chilling in {1} mode.'.format(user.name, user.status)
		member_number = sorted(
			server.members, key=lambda m: m.joined_at).index(user) + 1

		if user.activity is None:
			playing = f'{user.name} is not playing anything, or it is not a Rich Presence'

		elif user.activity.type == discord.ActivityType.listening and user.activity.name == "Spotify":
			artists = ', '.join([x for x in user.activity.artists])
			playing = f'{user.name} is listening to spotify!\nArtists: {artists}\nAlbum: {user.activity.album}\nTrack: [HERE](https://open.spotify.com/track/{user.activity.track_id}) '
		else:
			playing = f'{user.name} is on `{user.activity.name}`'

		em = discord.Embed(colour=color,description=desc,timestamp=time)
		em.add_field(name='Playing', value=playing, inline=True)
		em.add_field(name='Nick', value=user.nick, inline=True)
		em.add_field(name='Member No.', value=str(member_number), inline=True)
		em.add_field(name='Account Created', value="{} thats over {} days ago".format(user.created_at.__format__('%A, %d. %B %Y'), (ctx.message.created_at - user.created_at).days))
		em.add_field(name='Join Date', value=user.joined_at.__format__('%A, %d. %B %Y'))
		em.add_field(name='Roles', value=", ".join(rolenames), inline=False)
		em.set_footer(text=f'User ID: {user.id}')
		em.set_thumbnail(url=avi)
		em.set_author(name=user,icon_url=avi)

		await ctx.send(embed=em)

def export(bot):
	exports = {
		"cog": Information(bot),
		"name": "Information"
	}
	return exports