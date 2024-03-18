from __future__ import annotations

import inspect
from typing import Iterable, Optional
from urllib.parse import urlparse

import aiohttp
import discord

# from discord.ext import commands
from dis_command.discommand.ext import commands, context


class ConfirmationView(discord.ui.View):
    def __init__(self, *, timeout: float, author_id: int, ctx: Context, delete_after: bool) -> None:
        super().__init__(timeout=timeout)
        self.value: Optional[bool] = None
        self.delete_after: bool = delete_after
        self.author_id: int = author_id
        self.ctx: Context = ctx
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id == self.author_id:
            return True
        else:
            await interaction.response.send_message("This confirmation dialog is not for you.", ephemeral=True)
            return False

    async def on_timeout(self) -> None:
        if self.delete_after and self.message:
            await self.message.delete()
        else:
            await self.clear_before_stop()

    async def clear_before_stop(self) -> None:
        await self.message.edit(view=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        await interaction.response.defer()
        if self.delete_after:
            await interaction.delete_original_response()
        else:
            await self.clear_before_stop()
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        await interaction.response.defer()
        if self.delete_after:
            await interaction.delete_original_response()
        else:
            await self.clear_before_stop()
        self.stop()


class Context(context.Context):
    """Custom Context class to provide utility."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def create_api_connection(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession()

    async def entry_to_code(self, entries: Iterable[tuple[str, str]]) -> None:
        width = max(len(a) for a, b in entries)
        output = ["```"]
        for name, entry in entries:
            output.append(f"{name:<{width}}: {entry}")
        output.append("```")
        await self.send("\n".join(output))

    async def indented_entry_to_code(self, entries: Iterable[tuple[str, str]]) -> None:
        width = max(len(a) for a, b in entries)
        output = ["```"]
        for name, entry in entries:
            output.append(f"\u200b{name:>{width}}: {entry}")
        output.append("```")
        await self.send("\n".join(output))

    async def prompt(
        self, message: str, *, timeout: float = 30.0, delete_after: bool = True, author_id: Optional[int] = None, embed: bool = False
    ) -> Optional[bool]:
        """An interactive reaction confirmation dialog.
        Parameters
        -----------
        message: str
            The message to show along with the prompt.
        timeout: float
            How long to wait before returning.
        delete_after: bool
            Whether to delete the confirmation message after we're done.
        author_id: Optional[int]
            The member who should respond to the prompt. Defaults to the author of the
            Context's message.
        Returns
        --------
        Optional[bool]
            ``True`` if explicit confirm,
            ``False`` if explicit deny,
            ``None`` if deny due to timeout
        """

        author_id = author_id or self.author.id
        view = ConfirmationView(
            timeout=timeout,
            delete_after=delete_after,
            ctx=self,
            author_id=author_id,
        )
        if embed:
            embed = discord.Embed(description=message)
            view.message = await self.send(embed=embed, view=view)
        else:
            view.message = await self.send(message, view=view)
        await view.wait()
        return view.value

    async def show_help(self, command: commands.Command | Commands.CommandGroup):
        """Shows the help command for the specified command if given.
        If no command is given, then it'll show help for the current
        command.
        """
        embed = discord.Embed(title=f"{command.name}", description=command.description)
        params = inspect.signature(command.callback).parameters
        for name, arg in params.items():
            if name in ["self", "bot", "ctx"]:
                continue

            if arg.default == inspect._empty:
                embed.add_field(name=name, value="This argument is **Required**")
            else:
                embed.add_field(name=name, value=f"Defaults to: `{arg.default}`")
        if type(command) == commands.CommandGroup:
            for subcommand in command.commands.values():
                embed.add_field(name=subcommand.name, value=subcommand.description)
        return await self.send(embed=embed)

    def delete(self):
        """shortcut"""
        return self.message.delete()

    async def get_ban(self, name_or_id):
        """Helper function to retrieve a banned user"""
        for ban in await self.guild.bans():
            if name_or_id.isdigit():
                if ban.user.id == int(name_or_id):
                    return ban
            if name_or_id.lower() == str(ban.user).lower():
                return ban

    async def purge(self, *args, **kwargs):
        """Shortcut to channel.purge"""
        kwargs.setdefault("bulk", True)
        await self.channel.purge(*args, **kwargs)

    async def _get_message(self, channel, id):
        """Goes through channel history to get a message"""
        async for message in channel.history(limit=2000):
            if message.id == id:
                return message

    async def get_message(self, channel_or_id, id=None):
        """Helper tool to get a message, limits at 2000 messages."""
        if isinstance(channel_or_id, int):
            msg = await self._get_message(channel=self.channel, id=channel_or_id)
        else:
            msg = await self._get_message(channel=channel_or_id, id=id)
        return msg

    @staticmethod
    def is_valid_image_url(url):
        """Checks if a url leads to an image."""
        types = [".png", ".jpg", ".gif", ".bmp", ".webp"]
        parsed = urlparse(url)
        if any(parsed.path.endswith(i) for i in types):
            return url.replace(parsed.query, "size=128")
