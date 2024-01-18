import redis

RDB = redis.Redis(
    host='127.0.0.1',
    port=6379,
    decode_responses=True)

def get_guild_events(guild: int) -> int:
    """Gets the event count for a guild (How many events have happened since last cleared).

    Args:
        guild (int): Guild ID.

    Returns:
        int: The number of events that have happend.
    """    
    return RDB.get(f"lana:events:{guild}") or 0

def add_guild_event(guild: int) -> int:
    """Adds event to guild counter.

    Args:
        guild (int): Guild ID.

    Returns:
        int: The new count of events.
    """    
    key = f"lana:events:{guild}"
    current = RDB.get(key)
    if current == None:
        RDB.set(key, 1, 15)
        return 1
    current = int(current) + 1
    RDB.set(key, current, keepttl=True)
    return current



def add_moderator_action(member: int) -> int:
    """Adds to moderation action count.

    Args:
        member (int): The moderator who has done an action.

    Returns:
        int: The new count.
    """
    key = f"lana:actions:{member}"
    current = RDB.get(key)
    if current == None:
        RDB.set(key, 1, 60)
        return 1
    current = int(current) + 1
    RDB.set(key, current, keepttl=False)
    return current

def get_moderator_action(member: int) -> int:
    """Gets a moderators current actions.

    Args:
        member (int): The moderator who has done an action.

    Returns:
        int: The count of actions the moderator has done in their time limit.
    """
    return RDB.get(f"lana:actions:{member}") or 0