import discord

from utils.permissions.checks import check_permissions

from context import Context

has_permissions = check_permissions # lol



def can_send(ctx: Context):
    """ Checks if channel is sendable. """
    return isinstance(ctx.channel,
                      discord.DMChannel) or ctx.channel.permissions_for(
                          ctx.guild.me).send_messages


def can_embed(ctx: Context):
    """ Check if bot can embed. """
    return isinstance(ctx.channel,
                      discord.DMChannel) or ctx.channel.permissions_for(
                          ctx.guild.me).embed_links


def can_upload(ctx: Context):
    """ Check if bot can upload. """
    return isinstance(ctx.channel,
                      discord.DMChannel) or ctx.channel.permissions_for(
                          ctx.guild.me).attach_files


def can_react(ctx: Context):
    """ Check if bot can react. """
    return isinstance(ctx.channel,
                      discord.DMChannel) or ctx.channel.permissions_for(
                          ctx.guild.me).add_reactions
