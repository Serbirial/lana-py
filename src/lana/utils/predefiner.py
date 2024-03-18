# This is a utility that assists with anything to do with pre-defined actions based on expected data
from inspect import isawaitable

from typing import (
	Self,
	Coroutine,
	Any
)
from functools import wraps

from dataclasses import (
	dataclass,
	field
)

async def default_coro() -> None:
	return "This is the default action message. The default actions have not been set"

def __close(self):
	if len(self.collection) > 0:
		for collec in self.collection.values():
			values = collec.actions
			for coro in values.values():
				if type(coro) == list: # list of coros
					for nested_coro in coro:
						nested_coro.close()
				else:
					coro.close()
		if self.default_action:
			self.default_action.close()
		if self.error_action:
			self.error_action.close()

def cleanly_close(func) -> Any | Exception:
	"""Catch any thrown errors and cleanup before raising the error again."""
	@wraps(func)
	async def wrapper(self, **kwargs):
		if not hasattr(self, "collection"):
			raise Exception("clean close wrapper used outside of PredefinedActions")
		try:
			ret = await func(self, **kwargs)

			__close(self)

			return ret
		except Exception as e:
			__close(self)
			if self.error_action:
				return await self.error_action
			raise e
	return wrapper



@dataclass
class ActionCollection:
	callback: Coroutine = None # optional nested way to get data
	actions: dict = field(default_factory=dict) 


	def add_action(self, trigger: Any, action: Coroutine) -> Self:
		"""Adds an action to be executed based on the found trigger.

		Args:
			trigger (Any): _description_
			action (Coroutine): _description_

		Returns:
			Self: _description_
		"""
		self.actions[trigger] = action
		return self

	async def _invoke(self, fallback: Any):
		if isawaitable(self.callback):
			ret = await self.callback
		else:
			ret = fallback
		if ret in self.actions:
			new_ret = self.actions[ret]
			if type(new_ret) == list: # list of coros to execute instead of a single coro.
				last_ret = None
				for coro in new_ret:
					last_ret = await coro
				return last_ret

			return await self.actions[ret]

class PredefinedActions:
	def __init__(
			self,
			to_exec: Coroutine = None,
			default_action: Coroutine = None,
			error_action: Coroutine = None
		) -> Self:
		self.coro = to_exec

		self.default_action: Coroutine = default_action
		self.error_action: Coroutine = error_action

		self.collection: dict[Any, ActionCollection] = {}  # A map of triggers and their actions.

	@cleanly_close
	async def run(self):
		"""Runs the given coroutine for found data then finds the correct trigger and execute it."""
		if isawaitable(self.coro):
			resp = await self.coro
		else:
			resp = self.coro
		if resp in self.collection:
			ret = await self.collection[resp]._invoke(resp)
			return ret
		else:
			if self.default_action:
				return await self.default_action

	def make_collection(self, trigger: Any, to_exec: Coroutine = None, ret_base: bool = False) -> ActionCollection | Self:
		"""Makes a collection object that is executed when the trigger is found, returns the collection object, or optionally the base instance. (disabled by default).

		Args:
			trigger (Any): the trigger needed to select and execute this collection.
			to_exec (Coroutine, optional): Makes the collection execute a function to check for data, for nested use.
			ret_base (bool, optional): Controls if the return is the collection instance or the base instance. Defaults to True.

		Returns:
			ActionCollection: The created collection of actions under the given trigger.
			Self: The base instance.
		"""
		collection = ActionCollection(to_exec)
		self.collection[trigger] = collection
		if ret_base:
			return self
		return collection

	def set_default_action(self, coro: Coroutine) -> Self:
		self.set_default_action = coro
		return self
