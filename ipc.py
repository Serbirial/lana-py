import asyncio
import websockets
from json import loads

def format_event(raw_event_data, delim: str = "\n"): # This code is wacky...
	event_name, event_data = raw_event_data.split(delim)
	return event_name, loads(event_data.replace("\'", "\""))

def format_outgoing_event(name, data):
	return f"{name}\n{data}"

def get_args_from_data(data):
	if not "args" in data:
		return ()
	else:
		return data["args"]

class IPCServer:
	def __init__(self, main_client, ip, port) -> None:
		self.client = main_client
		self.ip = ip
		self.port = port
		self.connections = {} # reference : connection
		self.VALID_EVENTS = {
			"identify": None,
			"db_sync": None,
			"notice": None,
			"broadcast": self.broadcast

		}

	def check_if_valid_event(self, event):
		return event in self.VALID_EVENTS

	async def auth_handshake(self, connection): # FIXME actual auth
		await self.send(connection, "identify")

		event, data = await self.recv(connection)

		if event != "identify" or "ref" not in data:
			print("Client didnt identify in first response.")
			return connection.close()
		else:
			if data["ref"] in self.connections:
				print("Client tried to use already-used reference name.")
				return connection.close()
			await self.send(connection, "done")
			return data["ref"]

	async def send(self, connection, event_name, event_data: dict = {}):
		await connection.send(format_outgoing_event(event_name, event_data))

	async def recv(self, connection):
		data = await connection.recv()
		return format_event(data)

	async def broadcast(self, data) -> None:
		""" Send event to all connections"""
		#conns = [x for x in self.connections.values() if x != [self.connections[reference]]]
		websockets.broadcast([x for x in self.connections.values()], data)
		return True

	async def connection_handler(self, connection, reference):
		""" Receive incoming events """
		while connection.closed != True:
			try:
				event, data = await self.recv(connection)
				if not self.check_if_valid_event(event):
					await self.send(connection, "error", {"error": "bad event name"})
					print("bad event name")

				else:
					if self.VALID_EVENTS[event] != None:
						args = get_args_from_data(data)
						print(f"valid event {event} - {data}")
						await self.VALID_EVENTS[event](*args)
						await self.send(connection, "done")

			except websockets.exceptions.ConnectionClosedError or websockets.exceptions.ConnectionClosedOK:
				pass

	async def start(self):
		try:
			print("-----    Starting IPC Server    -----.\n")
			async with websockets.serve(self.handler, self.ip, self.port, compression=None, ping_interval=30, max_size=262144): # Disable compression at cost of network bandwidth
				print("\n-----    Started IPC Server    -----.\n")
				await asyncio.Future()  # run forever
		except:
			self.cleanup_before_exit()

	async def handler(self, connection):
		""" Handles a single connection. """
		print(f">>> Incoming Connection")

		reference = await self.auth_handshake(connection)
		self.connections[reference] = connection
		print(f">>> Accepted Connection ({reference})")

		try:
			asyncio.create_task(self.connection_handler(connection, reference)) # Receive events
			await connection.wait_closed() # Wait until connection closes
		except websockets.exceptions.ConnectionClosedError or websockets.exceptions.ConnectionClosedOK:
			del self.connections[reference]

		del self.connections[reference]
		print(f">>> Closed connection ({reference})\n")
		return

	def cleanup_before_exit(self):
		print("\n----    Exiting IPC server.    -----\n")
		print("Done.")

