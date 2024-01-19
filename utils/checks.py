from discord import (
	Client,
	AutoShardedClient
)
from exceptions import (
	CommandCheckError,
	PremiumCheckError
)

async def message_in_cache(client: Client | AutoShardedClient, mid: int):
		if any(mid == x.id for x in client.cached_messages[:100]):
			return True
		else:
			return False


def strict_mod_actions(ctx):
	ret = ctx.bot.db.query_row("SELECT enabled FROM strict_mod_actions WHERE guild = ?", ctx.guild.id)
	if ret == None or ret == 0:
		return False
	elif ret == 1:
		return True

def is_known_mod(ctx, userid: int):
	ret = ctx.bot.db.query_row("SELECT user_id FROM guild_mods WHERE guild = ? AND user_id = ?", ctx.guild.id, userid)
	if ret == None:
		return False
	elif ret == userid:
		return True
	
def is_known_admin(ctx, userid: int):
	ret = ctx.bot.db.query_row("SELECT user_id FROM guild_admins WHERE guild = ? AND user_id = ?", ctx.guild.id, userid)
	if ret == None:
		return False
	elif ret == userid:
		return True