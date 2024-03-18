import io
import logging
import os
import textwrap
import traceback
from contextlib import redirect_stdout

import discord
import psutil
from dis_command.discommand.ext import cogs, commands

from lana.utils import permissions

logger = logging.getLogger(__name__)
# ??
try:
    from lana.config.config import owners
except ImportError:
    logger.warning("No owners found in config, code in lana.cogs.eval will not work as intended.")


def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:-1])

    # remove `foo`
    return content.strip("` \n")


class EvalCommand(cogs.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, ctxx):
        self.client = ctxx

    @commands.command(name="eval")
    async def eval(self, bot, ctx, code: str):
        """Evaluates a code"""
        if ctx.author.id not in owners or not permissions.is_owner(ctx):
            return await ctx.send("This command is owner only.")

        env = {
            "self": self,
            "client": bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "os": os,
            "ps": psutil,
            "discord": discord,
        }
        env.update(globals())

        body = cleanup_code(code)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
        await ctx.message.add_reaction("\u23F2")
        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            await ctx.message.remove_reaction("\u23F2", bot.user)
            await ctx.message.add_reaction("\u274C")
            value = stdout.getvalue()
            return await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            await ctx.message.remove_reaction("\u23F2", bot.user)
            await ctx.message.add_reaction("\u2705")
            if ret is None:
                if value:
                    await ctx.send(f"```py\n{value}\n```")
            else:
                await ctx.send(f"```py\n{value}{ret}\n```")


def export(bot):
    exports = {"cog": EvalCommand(bot), "name": "EvalCommand"}
    return exports
