
def in_guild(db, guild_id: int) -> bool:
    return guild_id in db.execute("SELECT id ")