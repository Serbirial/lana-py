# Just a check #
from os.path import isfile
if not isfile("config/token.txt"):
	print("Please make a file called `token.txt` containing the bots token in the `config` folder.")
	exit(0)
# # # # # # # #

# Discord #

import discord

from dis_command.discommand.entry.inject import inject_into_bot
from dis_command.discommand.ext.cog_manager import CogManager
from dis_command.discommand.ext.event_manager import EventManager

from dis_command.discommand.ext import (
	task,
	converter
)

from discord import AutoShardedClient


# Non-discord #

import psutil
import datetime
import asyncio

# Config #

from config import config

# Utils #

from utils import db
from utils import redis
from utils import embed

# PRIVATE ANTILOCK #
try:
	from private import antilock
except:
	antilock = None


intent = discord.Intents.all()

DEFAULT_PREFIX = "lana."

async def sync_db(db_obj, bot_obj):
	#schema = open("config/schema.sql", "r")
	#db_obj.execute(schema.read())
	#schema.close()

	check = db_obj.query("SELECT * FROM owners")
	if check == None or len(check) == 0:
		owner_id = input("No owner IDs found in database, please paste your discord accounts ID > ")
		try:
			owner_id = int(owner_id)
		except:
			print("Failed to convert to integer, please make sure it only contains numbers, exiting...")
			exit(0)
		db_obj.execute("INSERT INTO owners (id, level) VALUES (?,?)", owner_id, "0")

	print("Running pre-ready DB population...")
	data = db_obj.query("SELECT id FROM guilds")
	gids = [x.id for x in bot_obj.guilds]
	for guild in data:
		if guild not in gids:
			db_obj.execute("DELETE FROM guilds WHERE id = ?", guild)
	for guild in bot_obj.guilds:
		if guild.id not in data:
			db_obj.execute("INSERT INTO guilds (id) VALUES (?)", guild.id)
	del gids, data
	print("DB Sync'd")
class LanaAR(AutoShardedClient):
	def __init__(self, db: db.DB, **attrs):
		super().__init__(
			#shard_ids=[0, 1],
			#shard_count=1,
			case_insensitive=True,
			max_messages=10000,
			fetch_offline_members=True,
			assume_unsync_clock=True,
			intents=intent)

		self.syncer = sync_db
		self.converter: converter = converter
		self.cog_manager: CogManager = None
		self.event_manager: EventManager = None

		self.process:   psutil.Process = psutil.Process()

		self.color: int = self.get_color # Get bot colors

		self.db:     db.DB = db
		self.redis:  redis.Redis = redis.RDB
		self.config: config.BotConfig = config.BotConfig()

		# Data filled in on_ready
		self.first_run:   bool    = False
		self.loaded_cogs: bool  = False
		self.avatar_data: bytes = None

		print("Done __INIT__, waiting for ON_READY")

		# DONT TOUCH
		self._at_limit:       list = []
		self._at_panic_limit: list = []


	async def timed_remove_from_hardlimit(self, guild: int) -> None:
		"""Sleeps 12 seconds and removed guild from the hardlimit that stops accepting events, Allowing for the bot to accept events once again from that guild.

		Args:
			guild (int): The guild ID.
		"""        
		await asyncio.sleep(25)
		self._at_limit.remove(guild)

	async def timed_remove_from_panic(self, guild: int) -> None:
		"""Removes a guild from the panic, allowing the bot to stop muting people who send messages.

		Args:
			guild (int): The guild ID.
		"""        
		await asyncio.sleep(8)
		self._at_panic_limit.remove(guild)


	async def get_color(self) -> int:
		return None

	async def init_extensions(self, path='cogs/'):
		"""Loads bot extensions

		Args:
			path (str, optional): Path to extensions. Defaults to 'cogs/'.
		"""		
		await self.cog_manager.load_cogs(path, False)
		# If it errors let it kill the entire bot
		# that way it does not break and be a potential security risk

	async def init_events(self, path='cogs/events/') -> None:
		"""Loads bot events.

		Args:
			path (str, optional): Path to event files. Defaults to 'cogs/events/'.
		"""		
		await self.cog_manager.load_cogs(path, False)
		# If it errors let it kill the entire bot
		# that way it does not break and be a potential security risk

	async def load_cogs_and_events(self):
		"""Starts the process of loading all the cogs and events.
		"""		
		await self.init_extensions()
		await self.init_events()

		try:
			await self.init_extensions("private/cogs/")
			await self.init_events("private/cogs/events/")
		except FileNotFoundError:
			pass

	async def download_avatar_data(self):
		print("Downloading avatar data...")
		self.avatar_data = await self.user.display_avatar.read()
		print("Downloaded.")

	def dispatch(self, event: str, *args: tuple) -> None:
		if event == "ready":
			return task.run_in_background(self.on_ready())
		
		elif event == "message":
			# FIXME: check for args incase it could error.
			message = args[0]
			if not hasattr(message, "guild") or message.guild == None: # DMs not allowed
				return
			if message.guild.id in self._at_limit:
				return
			if antilock and antilock.overloaded(self, message): # This is private code, you will have to implement this yourself.
				return

		self.event_manager.dispatcher(event, *args if args else ())
		return super().dispatch(event, *args if args else ())

	async def on_ready(self):
		'''Bot startup, sets uptime.'''
		await self.wait_until_ready()
		# Set the error channel.
		self.error_channel = self.get_channel(self.config.error_channel)
		# Sync the DB
		await sync_db(self.db, self)

		if not self.avatar_data:
			task.run_in_background(self.download_avatar_data())
		if not self.loaded_cogs:
			print("Loadings cogs and events...")
			self.loaded_cogs = True
			await self.load_cogs_and_events()
			print("Loaded cogs and events.")
			print("Updating bots internal command list...")
			self.cog_manager.update_all_commands()
			print("Command list ready.")
		else:
			print("Bot reconnected.")
			return
		if not hasattr(self, 'uptime'):  # Track Uptime
			self.uptime = datetime.datetime.utcnow()
		
		try:
			await self.change_presence(status=discord.Status.online, activity=discord.Game(f"with {len(list(self.get_all_members()))} foxes | lana help"))
		except ConnectionResetError:
			print("ConnectionResetError while changing status.")

		e = await embed.build_embed("Bot connected to discord.")
		e.add_field(name="Guilds", value=len(self.guilds))
		e.add_field(name="Users", value=len(self.users))
		e.add_field(name="Shards", value=len(self.shards))
		try:
			await self.get_channel(self.config.output_channel).send(content="<@!309025661031415809>", embed=e)
		except Exception as e:
			print(f"Error while sending startup message: {e}")

	def on_shutdown(self, *args):
		self.db.pool.close()
		exit(0)


	async def get_prefix(self, message: discord.Message) -> list | str:
		"""Gets the guilds prefix, or if there isnt one, gets the default one.

		Args:
			message (discord.Message): Message from the on_message handler.

		Returns:
			list | str: List of prefixes or a single prefix
		"""
		prefixes = [DEFAULT_PREFIX] # TODO: sort prefixes while adding to mariadb instead of relying on intensive sorting every new message.
		try:
			prefix = self.db.query('SELECT prefix FROM prefixes WHERE guild = ?', message.guild.id)
			if prefix != None:
				prefixes.extend(prefix)
		except:
			pass
		finally:
			return prefixes

if __name__ == "__main__":
	lana = LanaAR(db.DB(db.mariadb_pool(0)))
	try:
		lana.panel = db.DB(db.mariadb_pool(1, "private/config/private_db.json"))
	except FileNotFoundError:
		pass
	inject_into_bot(lana)
	lana.run(lana.config.token)