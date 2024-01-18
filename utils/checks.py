from discord import (
	Client,
	AutoShardedClient
)

async def message_in_cache(client: Client | AutoShardedClient, mid: int):
		if any(mid == x.id for x in client.cached_messages[:100]):
			return True
		else:
			return False
		
