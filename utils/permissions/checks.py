from config.config import owners

from exceptions import (
    CommandCheckError,
    PremiumCheckError
)

async def check_permissions(ctx, **perms):
    if ctx.author.id in owners:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    ret = all(
        getattr(resolved, name, None) == value
        for name, value in perms.items())
    if ret != True:
        raise CommandCheckError("Command check did not pass.")



def owner(ctx):
    return ctx.author.id in owners

def is_owner(ctx):
    return owner(ctx)

async def has_premium(ctx, level: int):
    lvl = ctx.bot.db.query_row("SELECT level FROM premium WHERE user_id = ?", ctx.author.id)
    if lvl is None:
        raise PremiumCheckError("Check for premium failed. This command requires premium.")
    if level > lvl:
        raise PremiumCheckError("Premium level not high enough for this command.")
    return lvl >= level