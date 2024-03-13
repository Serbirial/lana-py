from dis_command.discommand.ext import cogs
from dis_command.discommand.ext import commands
from dis_command.discommand.ext.events import inject_events
from dis_command.discommand.ext import slash

from utils import redis
from utils import permissions
from utils.predefiner import PredefinedActions

from random import choice

from config.config import owners

class Test(cogs.Cog):
	""" Various commands that control the configuration of the bot and its workings."""

	def __init__(self, bot):
		pass

	@commands.command()
	async def predtest(self, bot, ctx):
		first_prompt  = ctx.prompt(message="Are you sure about this action?", delete_after=False, embed=True)
		second_prompt = ctx.prompt(message="Are you really sure?", delete_after=False, embed=True)
		default = ctx.send("Then you should be sure")

		predefined = PredefinedActions(to_exec=first_prompt, default_action=default).set_default_action(default)

		predefined.make_collection(
			trigger=True,
			to_exec=second_prompt
		).add_action(
			True,
			ctx.send("But are you really sure?")
		).add_action(
			False,
			ctx.send("Then you should be extra sure.")
		)

		await predefined.run()

	@commands.command("test", xpr=[0.5,1])
	async def test(self, bot, ctx):
		await ctx.send(self.xpr)

	@commands.command("test2")
	async def test2(self, bot, ctx):
		res = redis.get_guild_events(ctx.guild.id)
		await ctx.send(res)

	@commands.command("simevent")
	async def simulate_event(self, bot, ctx, event_name: str, event_data: str):
		if ctx.author.id not in owners or not permissions.is_owner(ctx):
			return await ctx.send("This command is owner only.") 
		try:
			data = []
			for string in event_data.split(" "):
				if ":" in string:
					k,v = string.split(":")
					if k == "guild":
						data.append(bot.get_guild(int(v)))
					elif k == "member":
						data.append(bot.get_member(int(v)))
					elif k == "channel":
						data.append(ctx.guild.get_channel(int(v)))
		except:
			return await ctx.send("Error while loading event data")
		
		bot.event_manager.dispatcher(event_name, *tuple(data))

def export(bot):
	exports = {
		"cog": Test(bot),
		"name": "Testing"
	}
	return exports