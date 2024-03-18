from discord import AutoShardedClient, Client

from lana.exceptions import StrictActionCheckError


async def message_in_cache(client: Client | AutoShardedClient, mid: int):
    if any(mid == x.id for x in client.cached_messages[:100]):
        return True
    else:
        return False


def strict_actions(ctx):
    ret = ctx.bot.db.query_row("SELECT enabled FROM strict_mod_actions WHERE guild = ?", ctx.guild.id)
    if ret == None or ret == 0:
        return False
    elif ret == 1:
        return True


def strict_actions_premium(ctx):
    if ctx.bot.db.query_row("SELECT enabled FROM strict_mod_actions WHERE guild = ?", ctx.guild.id) == 1:
        ret = ctx.bot.db.query_row("SELECT premium FROM strict_mod_actions WHERE guild = ?", ctx.guild.id)
        if ret == None or ret == 0:
            return False
        elif ret == 1:
            return True


def is_known_admin(ctx, userid: int):
    ret = ctx.bot.db.query_row("SELECT user_id FROM guild_admins WHERE guild = ? AND user_id = ?", ctx.guild.id, userid)
    if ret == None:
        raise StrictActionCheckError("User tried to do admin action without being in known list of admins")
    elif ret == userid:
        return True


def is_known_mod(ctx, userid: int):
    ret = ctx.bot.db.query_row("SELECT user_id FROM guild_mods WHERE guild = ? AND user_id = ?", ctx.guild.id, userid)
    if ret == None:
        try:  # Admins can do moderation commands even if they are only in the mod list.
            if is_known_admin(ctx, userid) == True:
                return True
        except StrictActionCheckError:
            raise StrictActionCheckError("User tried to do moderation action without being in known list of moderators")
    elif ret == userid:
        return True
