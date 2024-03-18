from sanic.blueprints import Blueprint
from sanic.response import json

# from config import config

blueprint = Blueprint("API", url_prefix="/api")

# NOTE: Currently done endpoints: logging, welcoming, autorole, prefix

table_data = {  # Contains queries to populate tables based on their name
    "logging": "INSERT INTO logging (guild, enabled) VALUES (?,0)",
    "welcome": "INSERT INTO welcome (guild, enabled) VALUES (?,0)",
    "panic": "INSERT INTO panic (guild, enabled) VALUES (?,0)",
    "antialt": "INSERT INTO antialt (guild, enabled) VALUES (?,0)",
    "premium_points": "INSERT INTO premium_points (user_id, points) VALUES (?,0)",
    "strict_mod_actions": "INSERT INTO strict_mod_actions (guild, enabled, premium) VALUES (?,0,0)",
}


async def populate_table(db, table, *args):
    db.execute(table_data[table], *args)


@blueprint.get("/health", strict_slashes=True)
async def health(request):
    return json({"status": "healthy"})


@blueprint.post("/prefix/<guild:int>/add", strict_slashes=True)
async def prefix_add(request, guild):
    _json = request.json
    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})

    limit = request.app.ctx.db.query("SELECT prefix FROM prefixes WHERE guild = ?", guild)  # FIXME: figure out a way to make COUNT() work
    if limit != None and len(limit) >= request.app.ctx.prefix_limit:
        return json({"op": "limit"})

    check = request.app.ctx.db.query_row("SELECT prefix FROM prefixes WHERE guild = ? AND prefix = ?", guild, _json["op"])

    if not check:
        request.app.ctx.db.execute("INSERT INTO prefixes (guild, prefix) VALUES (?,?)", guild, _json["op"])
    elif check != None:
        return json({"op": "clash"})  # the prefix clashes with a current one.

    return json({"op": True})


@blueprint.post("/prefix/<guild:int>/remove", strict_slashes=True)
async def prefix_remove(request, guild):
    _json = request.json

    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})

    request.app.ctx.db.execute("DELETE FROM prefixes WHERE guild = ? AND prefix = ?", guild, _json["op"])

    return json({"op": True})


#########################################################


@blueprint.post("/antialt/<guild:int>/toggle", strict_slashes=True)
async def antialt_toggle(request, guild):
    check = request.app.ctx.db.query_row("SELECT enabled FROM antialt WHERE guild = ?", guild)
    if check == None:
        await populate_table(request.app.ctx.db, "antialt", guild)
        return json({"op": 2})  # 2 is code for 'populated', aka first run.
    elif check == 0:
        request.app.ctx.db.execute("UPDATE antialt SET enabled = 1 WHERE guild=?", guild)
    elif check == 1:
        request.app.ctx.db.execute("UPDATE antialt SET enabled = 0 WHERE guild=?", guild)
    return json({"op": check})  # Return the toggled state from before.


@blueprint.post("/antialt/<guild:int>/days", strict_slashes=True)
async def antialt_days(request, guild):
    _json = request.json

    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})

    try:
        days = int(_json["op"])
    except:
        return json({"op": -1})  # -1 is code for a general conversion error.

    request.app.ctx.db.execute("UPDATE antialt SET age_threshold = ? WHERE guild=?", guild, days)
    return json({"op": True})


##########################################################


@blueprint.post("/panic/<guild:int>/toggle", strict_slashes=True)
async def panic_toggle(request, guild):
    _json = request.json

    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})

    check = request.app.ctx.db.query_row("SELECT enabled FROM panic WHERE guild = ?", guild)
    if check == None:
        await populate_table(request.app.ctx.db, "panic", guild)
        return json({"op": 2})  # 2 is code for 'populated', aka first run.
    elif check == 0:
        request.app.ctx.db.execute("UPDATE panic SET enabled = 1 WHERE guild=?", guild)
    elif check == 1:
        request.app.ctx.db.execute("UPDATE panic SET enabled = 0 WHERE guild=?", guild)

    return json({"op": check})  # Return the toggled state from before.


@blueprint.post("/panic/<guild:int>/message_limit", strict_slashes=True)
async def panic_message_limit(request, guild):
    _json = request.json

    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})
    if not type(_json["op"]) == int:
        return json({"op": "not_integer"})
    if _json["op"] > 1000:
        return json({"op": "too_big"})
    check = request.app.ctx.db.query_row("SELECT enabled FROM panic WHERE guild = ?", guild)
    if check == None:
        await populate_table(request.app.ctx.db, "panic", guild)
        return json({"op": 2})  # 2 is code for 'populated', aka first run.
    request.app.ctx.db.execute("UPDATE panic SET message_limit = ? WHERE guild = ?", _json["op"], guild)

    return json({"op": True})  # Return the toggled state from before.


##########################################################


@blueprint.post("/log/<guild:int>/toggle", strict_slashes=True)
async def log_toggle(request, guild):
    _json = request.json

    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})

    check = request.app.ctx.db.query_row("SELECT enabled FROM logging WHERE guild = ?", guild)
    if check == None:
        await populate_table(request.app.ctx.db, "logging", guild)
        return json({"op": 2})  # 2 is code for 'populated', aka first run.
    elif check == 0:
        request.app.ctx.db.execute("UPDATE logging SET enabled = 1 WHERE guild=?", guild)
    elif check == 1:
        request.app.ctx.db.execute("UPDATE logging SET enabled = 0 WHERE guild=?", guild)

    return json({"op": check})  # Return the toggled state from before.


@blueprint.post("/log/<guild:int>/channel", strict_slashes=True)
async def log_channel(request, guild):
    _json = request.json

    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})

    check = request.app.ctx.db.query_row("SELECT enabled FROM logging WHERE guild = ?", guild)
    if check == None:
        await populate_table(request.app.ctx.db, "logging", guild)
        return json({"op": 2})  # 2 is code for 'populated', aka first run.

    # FIXME: regex to check if its a legit webhook URL

    request.app.ctx.db.execute("UPDATE logging SET webhook_url = ? WHERE guild = ?", _json["op"], guild)

    return json({"op": True})


################################


@blueprint.post("/welcome/<guild:int>/toggle", strict_slashes=True)
async def welcome_toggle(request, guild):

    check = request.app.ctx.db.query_row("SELECT enabled FROM welcome WHERE guild = ?", guild)
    if check == None:
        await populate_table(request.app.ctx.db, "welcome", guild)
        return json({"op": 2})  # 2 is code for 'populated', aka first run.
    elif check == 0:
        request.app.ctx.db.execute("UPDATE welcome SET enabled = 1 WHERE guild=?", guild)
    elif check == 1:
        request.app.ctx.db.execute("UPDATE welcome SET enabled = 0 WHERE guild=?", guild)

    return json({"op": check})  # Return the toggled state from before.


@blueprint.post("/welcome/<guild:int>/channel", strict_slashes=True)
async def welcome_channel(request, guild):
    _json = request.json

    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})

    check = request.app.ctx.db.query_row("SELECT enabled FROM welcome WHERE guild = ?", guild)
    if check == None:
        await populate_table(request.app.ctx.db, "welcome", guild)
        return json({"op": 2})  # 2 is code for 'populated', aka first run.

    request.app.ctx.db.execute("UPDATE welcome SET channel = ? WHERE guild = ?", _json["op"], guild)

    return json({"op": True})


@blueprint.post("/welcome/<guild:int>/message", strict_slashes=True)  # FIXME: add check
async def welcome_message(request, guild):
    _json = request.json

    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})
    check = request.app.ctx.db.query_row("SELECT enabled FROM welcome WHERE guild = ?", guild)
    if check == None:
        await populate_table(request.app.ctx.db, "welcome", guild)
        return json({"op": 2})  # 2 is code for 'populated', aka first run.

    request.app.ctx.db.execute("UPDATE welcome SET message = ? WHERE guild = ?", _json["op"], guild)

    return json({"op": True})


@blueprint.post("/welcome/<guild:int>/embed", strict_slashes=True)
async def welcome_embed(request, guild):

    check = request.app.ctx.db.query_row("SELECT enabled FROM welcome WHERE guild = ?", guild)
    if check == None:
        await populate_table(request.app.ctx.db, "welcome", guild)
        return json({"op": 2})  # 2 is code for 'populated', aka first run.

    embed = request.app.ctx.db.execute("SELECT embed FROM welcome WHERE guild = ?", guild)
    if embed == 0:
        request.app.ctx.db.execute("UPDATE embed SET enabled = 1 WHERE guild=?", guild)
    elif embed == 1:
        request.app.ctx.db.execute("UPDATE embed SET enabled = 0 WHERE guild=?", guild)

    return json({"op": embed})  # Return the toggled state from before.


##########################################################


@blueprint.post("/autorole/<guild:int>/toggle", strict_slashes=True)
async def autorole_toggle(request, guild):

    check = request.app.ctx.db.execute("SELECT enabled FROM autorole WHERE guild = ?", guild)
    if check == 0:
        request.app.ctx.db.execute("UPDATE autorole SET enabled = 1 WHERE guild=?", guild)
    elif check == 1:
        request.app.ctx.db.execute("UPDATE autorole SET enabled = 0 WHERE guild=?", guild)

    return json({"op": check})  # Return the toggled state from before.


@blueprint.post("/autorole/<guild:int>/role", strict_slashes=True)
async def autorole_role(request, guild):
    _json = request.json

    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})

    # FIXME: check if its an actual role

    request.app.ctx.db.execute("UPDATE autorole SET role = ? WHERE guild = ?", _json["op"], guild)

    return json({"op": True})


##########################################################

# FIXME: the API doesnt do deletion yet.


@blueprint.post("/reactionrole/<guild:int>/<message:int>/<emoji:int>/add", strict_slashes=True)
async def reactionrole_add(request, guild, message, emoji):
    _json = request.json

    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})

    check = request.app.ctx.db.query_row(
        "SELECT enabled FROM reactionrole WHERE guild = ? AND emoji_id = ? AND message_id = ?", guild, emoji, message
    )

    if not check:
        request.app.ctx.db.execute(
            "INSERT INTO reactionrole (guild, message_id, emoji_id, role_id, enabled) VALUES (?, ?, ?, ?, ?)",
            guild,
            message,
            emoji,
            _json["op"],
            1,
        )
        # FIXME: have bot react with emoji.

    elif check:
        return json({"op": "clash"})

    return json({"op": True})  # Return the toggled state from before.


@blueprint.post("/reactionrole/<guild:int>/<message:int>/<emoji:int>/toggle", strict_slashes=True)
async def reactionrole_toggle(request, guild, message, emoji):

    check = request.app.ctx.db.query_row(
        "SELECT enabled FROM reactionrole WHERE guild = ? AND emoji_id = ? AND message_id = ?", guild, emoji, message
    )

    if not check:
        return json({"op": "Void."})  # Doesnt exist.

    elif check == 0:
        request.app.ctx.db.execute(
            "UPDATE reactionrole SET enabled = 1 WHERE guild = ? AND emoji_id = ? AND message_id = ?", guild, emoji, message
        )
    elif check == 1:
        request.app.ctx.db.execute(
            "UPDATE reactionrole SET enabled = 0 WHERE guild = ? AND emoji_id = ? AND message_id = ?", guild, emoji, message
        )

    return json({"op": check})  # Return the toggled state from before.


@blueprint.post("/reactionrole/<guild:int>/<message:int>/<emoji:int>/role", strict_slashes=True)
async def reactionrole_update_role(request, guild, message, emoji):
    _json = request.json

    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})

    # FIXME: check if its an actual role

    request.app.ctx.db.execute(
        "UPDATE reactionrole SET role = ? WHERE guild = ? AND emoji_id = ? AND message_id = ?", _json["op"], guild, emoji, message
    )

    return json({"op": True})


##########################################################


@blueprint.post("/antinuke/<guild:int>/toggle", strict_slashes=True)
async def antinuke_toggle(request, guild):
    check = request.app.ctx.db.query_row("SELECT enabled FROM antinuke WHERE guild = ?", guild)

    if not check:
        return json({"op": "Void."})  # Doesnt exist.

    elif check == 0:
        request.app.ctx.db.execute("UPDATE antinuke SET enabled = 1 WHERE guild = ?", guild)
    elif check == 1:
        request.app.ctx.db.execute("UPDATE antinuke SET enabled = 0 WHERE guild = ?", guild)

    return json({"op": check})  # Return the toggled state from before.


@blueprint.post("/antinuke/<guild:int>/actions", strict_slashes=True)
async def antinuke_actions(request, guild):
    check = request.app.ctx.db.query_row("SELECT enabled FROM antinuke WHERE guild = ?", guild)

    if not check:
        return json({"op": "Void."})  # Doesnt exist.


##########################################################


@blueprint.post("/premium/points/<user:int>", strict_slashes=True)
async def premium_points(request, user):
    check = request.app.ctx.db.query_row("SELECT points FROM premium_points WHERE user_id = ?", user)
    if check == None:
        await populate_table(request.app.ctx.db, "premium_points", user)
        return json({"op": 0})

    return json({"op": int(check)})


@blueprint.post("/premium/points/add/<user:int>", strict_slashes=True)
async def premium_points_add(request, user):
    _json = request.json
    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})
    try:
        points = int(_json["op"])
    except:
        return json({"op": -1})  # -1 is code for a general conversion error.

    check = request.app.ctx.db.query_row("SELECT points FROM premium_points WHERE user_id = ?", user)
    if check == None:
        request.app.ctx.db.execute("INSERT INTO premium_points (user_id, points) VALUES (?,?)", user, points)
    else:
        request.app.ctx.db.execute("UPDATE premium_points SET points = ? WHERE user_id = ?", check + points, user)
    return json({"op": True})


##########################################################


@blueprint.post("/modlist/<guild:int>/get", strict_slashes=True)  # TODO: make GET
async def modlist_get(request, guild):
    check = request.app.ctx.db.query("SELECT user_id FROM guild_mods WHERE guild = ?", guild)
    if check == None:
        return json({"op": None})

    return json({"op": check})


@blueprint.post("/modlist/<guild:int>/add", strict_slashes=True)
async def modlist_add(request, guild):
    _json = request.json
    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})
    try:
        mod_id = int(_json["op"])
    except:
        return json({"op": -1})  # -1 is code for a general conversion error.
    check = request.app.ctx.db.query_row("SELECT user_id FROM guild_mods WHERE guild = ? AND user_id = ?", guild, mod_id)
    if check == None:
        request.app.ctx.db.execute("INSERT INTO guild_mods (guild, user_id) VALUES (?,?)", guild, mod_id)
        return json({"op": True})
    else:
        return json({"op": "clash"})


@blueprint.post("/modlist/<guild:int>/remove", strict_slashes=True)
async def modlist_remove(request, guild):
    _json = request.json
    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})
    try:
        mod_id = int(_json["op"])
    except:
        return json({"op": -1})  # -1 is code for a general conversion error.

    request.app.ctx.db.execute("DELETE FROM guild_mods WHERE guild = ? AND user_id = ?", guild, mod_id)

    return json({"op": True})


@blueprint.post("/adminlist/<guild:int>/get", strict_slashes=True)  # TODO: make GET
async def adminlist_get(request, guild):
    check = request.app.ctx.db.query("SELECT user_id FROM guild_admins WHERE guild = ?", guild)
    if check == None:
        return json({"op": None})

    return json({"op": check})


@blueprint.post("/adminlist/<guild:int>/add", strict_slashes=True)
async def adminlist_add(request, guild):
    _json = request.json
    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})
    try:
        admin_id = int(_json["op"])
    except:
        return json({"op": -1})  # -1 is code for a general conversion error.

    check = request.app.ctx.db.query_row("SELECT user_id FROM guild_admins WHERE guild = ? AND user_id = ?", guild, admin_id)
    if check == None:
        request.app.ctx.db.execute("INSERT INTO guild_admins (guild, user_id) VALUES (?,?)", guild, admin_id)
    elif check != None:
        return json({"op": "clash"})

    return json({"op": True})


@blueprint.post("/adminlist/<guild:int>/remove", strict_slashes=True)
async def adminlist_remove(request, guild):
    _json = request.json
    if not _json or not "op" in _json:
        return json({"op": "Missing JSON."})
    try:
        admin_id = int(_json["op"])
    except:
        return json({"op": -1})  # -1 is code for a general conversion error.

    request.app.ctx.db.execute("DELETE FROM guild_admins WHERE guild = ? AND user_id = ?", guild, admin_id)

    return json({"op": True})


##########


@blueprint.post("/strictmodactions/<guild:int>/toggle", strict_slashes=True)
async def strictmodactionstoggle(request, guild):
    check = request.app.ctx.db.query_row("SELECT enabled FROM strict_mod_actions WHERE guild = ?", guild)
    if check == None:
        await populate_table(request.app.ctx.db, "strict_mod_actions", guild)
        return json({"op": 2})  # 2 is code for 'populated', aka first run.
    elif check == 0:
        request.app.ctx.db.execute("UPDATE strict_mod_actions SET enabled = 1 WHERE guild=?", guild)
    elif check == 1:
        request.app.ctx.db.execute("UPDATE strict_mod_actions SET enabled = 0 WHERE guild=?", guild)

    return json({"op": check})  # Return the toggled state from before.


@blueprint.post("/strictmodactions/<guild:int>/premium", strict_slashes=True)
async def strictmodactionspremiumtoggle(request, guild):
    check = request.app.ctx.db.query_row("SELECT premium FROM strict_mod_actions WHERE guild = ?", guild)
    if check == None:
        await populate_table(request.app.ctx.db, "strict_mod_actions", guild)
        return json({"op": 2})  # 2 is code for 'populated', aka first run.
    elif check == 0:
        request.app.ctx.db.execute("UPDATE strict_mod_actions SET premium = 1 WHERE guild=?", guild)
    elif check == 1:
        request.app.ctx.db.execute("UPDATE strict_mod_actions SET premium = 0 WHERE guild=?", guild)

    return json({"op": check})  # Return the toggled state from before.
