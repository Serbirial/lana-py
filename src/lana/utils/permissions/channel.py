import discord


def is_nsfw(ctx):
    """ Checks if a channel is NSFW. """
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.is_nsfw()


