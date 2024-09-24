import asyncio
import websockets
from json import loads

def format_event(raw_event_data, delim: str = "\n"): # This code is wacky...
	event_name, event_data = raw_event_data.split(delim)
	return event_name, loads(event_data.replace("\'", "\""))
def format_outgoing_event(name, data):
	return f"{name}\n{data}"

class IPCClient:
	def __init__(self, client, host_addr, host_port) -> None:
		self.client = client
		self.host = host_addr
		self.port = host_port
		self.connection = None

	async def send(self, connection, event_name, event_data: dict = {}):
		"""Send a message through the IPC

		Args:
			connection (websocket_connection): The websocket connection.
			event_name (str): The event name.
			event_data (dict, optional): The event data. Defaults to {}.
		"""		
		await connection.send(format_outgoing_event(event_name, event_data))

	async def recv(self, connection):
		"""Receive data through the IPC

		Args:
			connection (websocket_connection): The websocket connection.

		Returns:
			tuple: Tuple/Json data.
		"""		
		data = await connection.recv()
		return format_event(data)

	async def auth_handshake(self, connection): # FIXME actual auth
		"""The authentication handshake process to verify the connection is actually from another (verified) bot instance.

		Args:
			connection (websocket_connection): The websocket connection.

		Returns:
			str: The verified connections reference.
		
		Closes automatically if not able to verify.
		"""		
		event, data = await self.recv(connection)
		if event == "identify":
			await self.send(connection, "identify", {"ref": self.client.internal_name})
			event, data = await self.recv(connection)
			if event != "done":
				print("CRITICAL: Something went wrong during IPC Client auth.")
			return True

	async def connection_handler(self):
		"""WS Connection handler for IPC.
		"""		
		try:
			async with websockets.connect(self.make_uri()) as connection:
				self.connection = connection 
				if await self.auth_handshake(connection):
					while connection.closed != True:
						event, data = await self.recv(connection)
						pass
		except websockets.exceptions.ConnectionClosedError or websockets.exceptions.ConnectionClosedOK:
			print("CRITICAL: IPC CLIENT CONNECTION WAS CLOSED OR LOST")

	async def start(self):
		"""Starts the IPC client.
		"""		
		await self.connection_handler()

	def make_uri(self) -> str:
		"""Makes the WS URI

		Returns:
			str: The constructed URI.
		"""		
		return f"ws://{self.host}:{self.port}"

	async def notify(self, message):
		"""Notify the Cluster of {message}

		Args:
			message (str): The message to be sent.
		"""		
		await self.send(self.connection, "notify", {"args": message})

	async def sync_guilds(self):
		"""Sync all bot instances and shards with the Cluster to update the Guilds Table in the Database.
		"""		
		await self.send(self.connection, "guild_sync", {"guilds": [x.id for x in self.client.guilds]})

	async def error(self, error):
		"""Notify the Cluster of an error.

		Args:
			error (Exception | str): The exeption or error.
		"""
		await self.send(self.connection, "error", {"error": error if type(error) == str else str(error)})