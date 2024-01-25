import datetime
from datetime import datetime
from typing import Any
import aiohttp

from discord import Embed as discord_embed

from discord import (
	Webhook,
	Member,
	Message,
	TextChannel
)
from discord.colour import Colour

from discord.errors import Forbidden
from discord.types.embed import EmbedType

class Embed(discord_embed):
	"""Custom embed class for QOL additions."""
	def __init__(
			self,
			channel: TextChannel,
			colour: int | Colour | None = None,
			color: int | Colour | None = None,
			title: Any | None = None,
			type: EmbedType = 'rich',
			url: Any | None = None,
			description: Any | None = None,
			timestamp: datetime | None = None):
		super().__init__(
			colour=colour,
			color=color,
			title=title,
			type=type,
			url=url,
			description=description,
			timestamp=timestamp)
		self.channel = channel
		self.message = None

	async def show(self):
		if not self.message:
			pass
		await self.message.edit(embed=self)

	async def send(self):
		self.message = await self.channel.send(embed=self)

	async def add_to_description(self, to_add: str):
		if not self.description:
			self.description = to_add
		elif self.description:
			self.description += f"\n{to_add}"
		if self.message:
			await self.show()

	async def set_title(self, title):
		self.title = title
		await self.show()

	async def set_desc(self, description):
		self.description = description
		await self.show()

async def build_embed(title: str = None, description: str = None) -> discord_embed:
	"""Builds embed with timestamp and returns it.

	Args:
		title (str, optional): The title used when creating the embed object. Defaults to None.
		description (str, optional): The description used when creating the embed object. Defaults to None.

	Returns:
		Embed: The created embed object.
	"""    
	return discord_embed(title=title, description=description, timestamp=datetime.utcnow())

async def send_webhook_embed(webhook_url, embed):
	"""Sends embed through a webhook.

	Args:
		webhook_url (str): The url used when sending through webhook.
		embed (discord.Embed): The embed to send.
	"""    
	async with aiohttp.ClientSession() as session:
		webhook = Webhook.from_url(url=webhook_url, session=session)
		try:
			await webhook.send(username="Lana", embed=embed)
		except:
			await session.close()
		await session.close()
		

async def add_member_difference_fields(embed: discord_embed, before: Member, after: Member):
	if before.avatar != after.avatar:
		before.set_thumbnail(url=before.avatar.url)
		before.set_author(name=before.display_name, icon_url=before.avatar.url)
		before.add_field(name="User has been edited", value=f"User: {before.mention}", inline=False)
		before.add_field(name="Avatar change", value=f"New is below, old to the right", inline=False)
		before.set_image(url=after.avatar.url)
	elif before.status != after.status:
		embed.add_field(name="User has changed their status", value=f"Before: {before.status}\nAfter: {after.status}", inline=False)
	elif before.roles != after.roles:
		embed.set_author(name=before.display_name, icon_url=before.avatar.url)
		embed.add_field(name="User has been edited", value=f"User: {before.mention}", inline=False)
		if len(before.roles) > len(after.roles):
			rolemsg = f"Removed role(s): {' '.join([x.name for x in before.roles if x not in after.roles])}"
		elif len(before.roles) < len(after.roles):
			rolemsg = f"Added role(s): {' '.join([x.name for x in after.roles if x not in before.roles])}"
		try:
			logs = await before.guild.audit_logs(limit=10)
			tmp = [x for x in logs if x.target == before]
		except Forbidden:
			embed.set_footer(text="Could not view audit logs to see who did this action")
		else:
			embed.set_footer(text=f"Action done by {f'{tmp[0].user.name} ({tmp[0].user.id})' if tmp!=None else '(Cannot get)'}")
		embed.add_field(name="Roles", value=rolemsg, inline=False)
	elif before.name != after.name:
		embed.set_author(name=before.display_name, icon_url=before.avatar.url)
		embed.add_field(name="User has been edited", value=f"User: {before.mention}", inline=False)
		embed.add_field(name="Username", value=f"Before: {before.name}\nAfter: {after.name}", inline=False)
	elif before.display_name != after.display_name:
		embed.set_author(name=before.name, icon_url=before.avatar.url)
		embed.add_field(name="User has been edited", value=f"User: {before.mention}", inline=False)
		embed.add_field(name="Display name", value=f"Before: {before.display_name}\nAfter: {after.display_name}", inline=False)
	elif before.nick != after.nick:
		embed.set_author(name=before.display_name, icon_url=before.avatar.url)
		embed.add_field(name="User has been edited", value=f"User: {before.mention}", inline=False)
		embed.add_field(name="Nickname", value=f"Before: {before.nick}\nAfter: {after.nick}", inline=False)
	elif before.is_timed_out() != after.is_timed_out():
		embed.set_author(name=before.display_name, icon_url=before.avatar.url)
		if after.is_timed_out() == True:
			embed.add_field(name=f"User has been timed out", value=f"User: {before.mention}", inline=False)
		elif after.is_timed_out() == False:
			embed.add_field(name=f"User timeout has been removed", value=f"User: {before.mention}", inline=False)

	else:
		embed.add_field(name="Unrecognized change in member update event", value="Please notify the developers of this, preferribly with a explanation of what changed, or a screenshot of audit logs.")
