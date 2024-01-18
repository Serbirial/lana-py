from functools import wraps
from aiohttp import (
	ClientSession,
	ClientConnectorError,
	ClientResponse
)
from typing import Self, Coroutine
from exceptions import CantReachAPI

async def cancel_unused_actions(connection_instance):
	if len(connection_instance._actions) > 0:
		for collec in connection_instance._actions.values():
			for coro in collec.values():
				coro.close()
	if connection_instance.default_action:
		connection_instance.default_action.close()

class JsonError(Exception):
	pass

async def process_json(
    response: ClientResponse, require: bool = True
) -> ClientResponse | Exception:
    """For use when expecting JSON data to be sent back from API, errors if no JSON was received."""
    data = await response.json()
    if data == None and require:
        raise JsonError("Expected JSON data back from API.")
    return data

class Response:
	def __new__(cls, raw: ClientResponse, json: dict = {}) -> None:
		new_cls = super().__new__(cls)

		new_cls.__raw = raw
		new_cls.json = json
		new_cls.status = raw.status
		new_cls.headers = raw.headers
		new_cls.encoding = raw.get_encoding()

		return new_cls

	def expect_json_key(self, key: str, return_found = False) -> Self | JsonError:
		"""Expects the responses JSON to contain a given key

		Args:
			key (str): The key expected to exist in the JSON supplied by the API.

		Raises:
			JsonError: Key was not found or differs.

		Returns:
			Self | JsonError: Loops back to Response instance allowing for chaining. Errors if nothing was found.
		"""		
		if key not in self.json.keys():
			raise JsonError("Expected JSON key differs from returned JSON key.")
		if return_found:
			return self.json[key]
		return self # Allow for chaining

	def expect_json_keys(self, keys: list | set) -> Self | JsonError:
		"""Expects the responses JSON to contain a given key

		Args:
			keys (list | set): The keys expected to exist in the JSON supplied by the API.

		Raises:
			JsonError: Keys were not found or differ.

		Returns:
			Self | JsonError: Loops back to Response instance allowing for. Errors if nothing was found.
		"""		
		to_check = self.json.keys()
		for key in keys:
			if key not in to_check:
				raise JsonError("Expected JSON key data differs from returned key schema.")
		return self # Allow for chaining

	def expect_possible_json_values(self, key, possible_values: list, return_found: bool = False, *, loose: bool = False) -> Self | str | JsonError:
		"""UNUSED"""
		to_check = self.json.keys()
		if key not in to_check:
			raise JsonError("The provided key to check was not in the JSON.")
		
		temp = self.json[key]
		for value in possible_values:
			if loose:
				if value.lower() == temp.lower():
					if not return_found:
						return Self
					return temp
			else:
				if value == temp:
					if not return_found:
						return Self
					return temp

	def expect_json_value(self, key: str, expected_value: str | int, return_found: bool = False, *, loose: bool = False) -> Self | str| JsonError:
		"""Expects the responses JSON to contain a given key + value combination.

		Args:
			key (str): The key expected to exist in the JSON supplied by the API.
			expected_value (str | int): The value expected to exist under the supplied key.
			loose (bool, optional): If True, lowers the given/expected key/value to lowercase. Defaults to False.
			
		Raises:
			JsonError: Keys were not found or differ.

		Returns:
			Self | JsonError: Loops back to Response instance allowing for chaining. Errors if nothing was found.
		"""	
		if key not in self.json.keys():
			raise JsonError("Expected JSON key missing while expecting value.")
		if loose:
			if self.json[key].lower() != expected_value.lower():
				raise JsonError("Expected JSON values differs from returned values.")
		else:
			if self.json[key] != expected_value:
				raise JsonError("Expected JSON values differs from returned values.")
		if not return_found:
			return self
		return self.json[key]

async def find_response_action(actions, json):
	if len(actions) == 0:
		return -1
	else:
		for possible_value in actions.keys():
			if possible_value in json:
				to_exec = actions[possible_value][json[possible_value]]
				#if not inspect.iscoroutinefunction(to_exec):
				#	raise Exception("Expected action not a coroutine (do_actions middleman).")
				return to_exec


def catch_api_err(func) -> Response | CantReachAPI | Exception:
	"""Catch and throw the correct error if the API is down or erroring, instead of being jank. Also does QOL stuff."""
	@wraps(func)
	async def wrapper(self, **kwargs):
		try:
			ret = await func(self, **kwargs)
			await self.cleanup() # So you dont have to close the connection manually
			return ret
		except ClientConnectorError: # API is down or not responding at all.
			await cancel_unused_actions(self)
			await self.cleanup()
			raise CantReachAPI()
		except JsonError as e:
			await cancel_unused_actions(self)
			await self.cleanup()
			raise e
	return wrapper

class Connection(object):
	"""Instance of a connection to an external API.
	Inherit when making an API specific connector."""
	def __init__(self, url: str) -> None:
		self.url: str = url
		self.connection: ClientSession = None
		self.last_resp: Response = None # The most recent response, for caching.

		self.default_action: Coroutine = None
		self._actions = {}

		self.codes: list = None
		self.headers: dict = None

	def expect_status_codes(self, codes: list[int]) -> Self:
		self.codes = codes
		return self

	def predefine_json_actions(self, key: str, possible_values: dict[str, Coroutine]) -> Self:
		"""Define coros to automatically execute at the earliest point if the returned JSON data matches.

		Args:
			key (str): The expected key to put your actions under.
			possible_values (dict of values the expected key could have and coros to execute if found): Keys in this dict will be the values from the API given JSON and values the coro for executing. 

		Returns:
			Self: Loops back to Connection instance for chaining.
		"""		
		if key in self._actions:
			temp = {**possible_values, **self._actions[key]}
			self._actions[key] = temp
		self._actions[key] = possible_values
		return self

	def set_default_action(self, coro: Coroutine) -> Self:
		"""Sets the default action (coro) that will be executed when JSON processing or predefined responses fails.

		Args:
			coro (Coroutine): The coro to be awaited

		Returns:
			Self: Loops back to Connection instance for chaining.
		"""
		self.default_action = coro
		return self

	def set_headers(self, headers: dict) -> Self:
		"""Sets headers for this connection to use.

		Args:
			headers (dict): The headers to be sent along with any requests made with this Connection.

		Returns:
			Self: Loops back to the connections instance for chaining support.
		"""		
		self.headers = headers
		return self


	async def finalize_response(self, resp: ClientResponse, json: dict = None) -> Response:
		"""The final step before returning the fully fleshed out Response object for caching.

		Args:
			resp (ClientResponse): the aiohttp.ClientResponse from an API response.
			json (dict, optional): The processed json sent back from the API response. Defaults to None.

		Returns:
			Response: Fully fleshed out Response object.
		"""
		actual = Response(resp, json)

		self.last_resp = actual

		return actual

	def make_sure_connected(self):
		"""Makes sure there is a aiohttp.ClientSession to use before sending requests.
		"""		
		if not self.connection:
			self.connect()

	@catch_api_err # TODO: make sure this is ordered right to run AFTER the decorator currently above.
	async def post(self, **kwargs) -> Response:
		"""Sends a POST request to the API and processes then returns the response as a Response object.

		Returns:
			Response: The response of the API.
		"""		
		require_json = kwargs.get("require_json", False)
		json = kwargs.get("json", None)
		self.make_sure_connected()
		async with self.connection.post(self.url, json=json) as raw_resp:
			if self.codes and raw_resp.status not in self.codes:
				default = await self.default_action
				await cancel_unused_actions(self)
				return default
			try:
				data = await process_json(raw_resp, require_json)
			except JsonError as e:
				if self.default_action:
					default = await self.default_action
					await cancel_unused_actions(self)
					return default
				raise e
			early_call = await find_response_action(actions=self._actions, json=data)
			if early_call != -1:
				try:
					early = await early_call
					await cancel_unused_actions(self)
					return early
				except:
					default = await self.default_action
					await cancel_unused_actions(self)
					return default
			resp = await self.finalize_response(raw_resp, data)
		await cancel_unused_actions(self)
		return resp

	@catch_api_err # TODO: make sure this is ordered right to run AFTER the decorator currently above.
	async def get(self, **kwargs) -> Response:
		require_json = kwargs.get("require_json", False)
		self.make_sure_connected()
		async with self.connection.get(self.url, **kwargs) as raw_resp:
			json = await process_json(raw_resp, require_json)
			resp = await self.finalize_response(raw_resp, json)
		return resp

	def connect(self) -> ClientSession:
		self.connection = ClientSession()

	async def cleanup(self) -> True:
		if self.connection != None:
			await self.connection.close()

		return True



# For my bot.
class InternalApiConnection(Connection):
	"""Instance of a connection to internal APIs."""
	def __init__(self,
				ctx,
				url: str,
				auth_key: str = None
				) -> None:
		super().__init__(url) # Inherit from Connection

		self.ctx = ctx # Access bot variables
		self.auth_key = auth_key
