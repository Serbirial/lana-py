from __future__ import annotations
from typing import Any, Optional, Union

from dis_command.discommand.ext import cogs
from dis_command.discommand.ext import commands

from discord.ext import menus
from utils.permissions import user
import discord
import inspect
import itertools

from utils.paginator import RoboPages
from context import Context



class SelectionDropdown(discord.ui.Select):
    def __init__(self, parent_view, cogs):

        # Set the options that will be presented inside the SelectionDropdown
        self.parent = parent_view
        options = []
        for cog in cogs:
            options.append(discord.SelectOption(label=cog, description=cog))

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the SelectionDropdown options. We defined this above
        super().__init__(placeholder='Choose a Cog.', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        self.parent.current_cog = self.values[0]
        await interaction.response.edit_message(embed=self.parent.build_embed())

class PaginatedHelpCommand(discord.ui.View):
    def __init__(self, *, context, bot, timeout=180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.context = context
        self.help_pages = self.paginate()
        self.current_cog = "Settings" # FIXME
        self.index = 0
        
    def build_embed(self):
        embed = discord.Embed(title=self.current_cog)
        description = ""
        for name, desc in self.help_pages[self.current_cog].items():
            if 'desc' not in desc: # Subcommand
                temp = ""
                for sname, sdesc in desc.items():
                    temp += f"\n{sname}: {sdesc}"
                embed.add_field(name=name, value=temp)
            else:
                description += f"\n{name}:  {desc['desc']}"
        embed.description = description
        return embed
        
        
    @discord.ui.button(label="Next",style=discord.ButtonStyle.gray)
    async def next_button(self, button:discord.ui.Button, interaction:discord.Interaction):
        self.index += 1
        await interaction.response.edit_message(embed=self.build_embed())

    @discord.ui.button(label="Back",style=discord.ButtonStyle.gray)
    async def back_button(self, button:discord.ui.Button, interaction:discord.Interaction):
        self.index -= 1
        await interaction.response.edit_message(embed=self.build_embed())

    def paginate(self) -> dict:
        fields = {}
        for cog_name, data in self.bot.help[0].items(): # regular commands
            if cog_name not in fields:
                fields[cog_name] = {}

            for com_name, desc in data.items():
                fields[cog_name][com_name] = desc


        # Sub commands
        for cog_name, data in self.bot.help[1].items():
            if cog_name not in fields:
                fields[cog_name] = {}

            for parent_name, sub_data in data.items():
                if parent_name not in fields[cog_name]:
                    fields[cog_name][parent_name] = {}
                for com_name, desc in sub_data.items():
                    fields[cog_name][parent_name][com_name] = desc
        self.add_item(SelectionDropdown(self, fields.keys()))
        return fields


class BasicHelp:
    def __init__(self, data) -> None:
        self.embed =  discord.Embed()
        self.pages = self.paginate(data)

    def paginate(self, help_data: dict[str, object]) -> dict:
        pages = {}

        # Regular commands first
        for cog_name, data in help_data[0].items():
            if cog_name not in pages:
                pages[cog_name] = []

            for com_name, desc in data.items():
                pages[cog_name].append((com_name, desc['desc']))


        # Sub commands
        for cog_name, data in help_data[1].items():
            if cog_name not in pages:
                pages[cog_name] = []

            for parent_name, sub_data in data.items():
                for com_name, desc in sub_data.items():
                    pages[cog_name].append((parent_name, com_name, desc))

        return self.format_pages(pages)
    
    def format_pages(self, data: dict) -> discord.Embed:
        for category, data in data.items():
            built = ""
            sub = {}
            for command in data:
                if len(command)==2: # Name + Help
                    built += f"\n`{command[0]}: {command[1]}`"

                elif len(command)==3: # Parent + Subcommand + Subcommand Help
                    if command[0] not in sub:
                        sub[command[0]] = {}
                    sub[command[0]][command[1]] = command[2]
            for parent, subdata in sub.items():
                built += f"```{parent}:\n"
                for subname, subdesc in subdata.items():
                    built += f"  {subname}: {subdesc}\n"
                built += "```"
            self.embed.add_field(name=category, value=built, inline=False)
        return self.embed


class Help(cogs.Cog):
    """Help Cog"""

    def __init__(self, bot):
        self.client = bot

    @commands.command()
    async def basichelp(self, bot, ctx):
        """Sends all commands in a basic format"""
        _help = BasicHelp(bot.help)
        return await ctx.send(embed=_help.embed)

    @commands.command()
    async def help(self, bot, ctx, command: str = None):
        """Sends the help menu."""
        if command:
            if command in bot.all_commands:
                command = bot.all_commands[command]
                if type(command) == commands.CommandGroup:
                    embed = discord.Embed(title=command.name, description=command.description)
                    for subcommand in command.commands.values():
                        embed.add_field(name=subcommand.name, value=subcommand.description)
                    return await ctx.send(embed=embed)
                embed = discord.Embed(title=command.name, description=command.description)
                args = inspect.getfullargspec(command.callback)
                del args.args[:3]
                if len(args.args)>=1:
                    _temp = ""
                    for arg in args.args:
                        _temp += f"\n{arg} ({args.annotations[arg]})"
                    embed.add_field(name=f"Command arguments:", value=_temp)
                return await ctx.send(embed=embed)
        _view = PaginatedHelpCommand(bot=bot, context=ctx)
        await ctx.send(view=_view, embed=_view.build_embed())

    @commands.command()
    async def join(self, bot, ctx):
        """Joins a server."""
        perms = discord.Permissions()
        perms.read_messages = True
        perms.external_emojis = True
        perms.send_messages = True
        perms.manage_roles = True
        perms.manage_channels = True
        perms.ban_members = True
        perms.kick_members = True
        perms.manage_messages = True
        perms.embed_links = True
        perms.read_message_history = True
        perms.attach_files = True
        perms.add_reactions = True
        await ctx.send(f'<{discord.utils.oauth_url(bot.user.id, permissions=perms)}>')

def export(bot):
    exports = {
        "cog": Help(bot),
        "name": "Help"
    }
    return exports