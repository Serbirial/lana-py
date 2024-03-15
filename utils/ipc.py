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

	async def send(self, connection, event_name, event_data: dict = {}):
		await connection.send(format_outgoing_event(event_name, event_data))

	async def recv(self, connection):
		data = await connection.recv()
		return format_event(data)

	async def auth_handshake(self, connection): # FIXME actual auth
		event, data = await self.recv(connection)
		if event == "identify":
			await self.send(connection, "identify", {"ref": self.client.internal_name})
			event, data = await self.recv(connection)
			if event != "done":
				print("CRITICAL: Something went wrong during IPC Client auth.")

	async def connection_handler(self, connection):
		await self.auth_handshake(connection)
		while connection.closed != True:
			event, data = await self.recv(connection)
			pass # client shouldnt really care about receiving after the auth

	async def start(self):
		await self.connection_handler(self.connection)

	def make_uri(self) -> str:
		return f"ws://{self.host}:{self.port}"
	
	async def init(self):
		try:
			async with websockets.connect(self.make_uri()) as connection:
				self.connection = connection 
				await self.connection_handler(connection)
		except websockets.exceptions.ConnectionClosedError or websockets.exceptions.ConnectionClosedOK:
			print("CRITICAL: IPC CLIENT CONNECTION WAS CLOSED OR LOST")


	async def notify(self, message):
		await self.send(self.connection, "notify", {"args": message})

	async def sync(self):
		await self.send(self.connection, "db_sync", {"args": [x.id for x in self.client.guilds]})