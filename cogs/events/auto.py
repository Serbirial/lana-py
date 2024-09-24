import discord
import context
import traceback

from bot import sync_db

from dis_command.discommand.ext import cogs
from asyncio import sleep

from utils import db

class AutoEvents(cogs.Cog):
	def __init__(self, client):
		self.client = client

	async def update_status(self):
		"""Updates the bots status every 1200 seconds
		"""		
		# Update the status
		while True:
			try:
				await self.change_presence(status=discord.Status.online, activity=discord.Game(f"with {len(list(self.get_all_members()))} foxes | lana help"))
			except ConnectionResetError:
				self.__print("ConnectionResetError while changing status.")	
				continue
			await sleep(1200)


	async def sync_database(self):
		"""Sync's the Databases Guilds table from the main instance of the bot.
		"""		
		# Sync the database
		if self.client._is_main_instance:
			while True:
				try:
					await sync_db(self.client.db, [self.client.guilds + self.client._total_guilds])
				except Exception as e:
					self.__print(f"Error while syncing guilds to database: {e}.")	
					continue
				await sleep(1200*2)


	async def sync_guilds(self):
		"""Sync's the Guilds to the main instance of the bot for use in sync'ing the database
		"""		
		# Sync the guilds to the main bot instance to be added to the database
		if not self.client._is_main_instance:
			while True:
				try:
					await self.ipc.sync_guilds(self.client.db, self.client.guilds)
				except Exception as e:
					await self.ipc.error(str(e))
					continue
				await sleep(1200)


def export(bot):
	events = AutoEvents(bot)
	exports = {
		"cog": events,
		"name": "Auto Events"
	}
	return exports