from sanic.blueprints import Blueprint
from sanic.response import json, text
from sanic.response import redirect

import secrets

blueprint = Blueprint("Dashboard", url_prefix="/dash")

def generate_user_secret(request, user_id: int):
	db = request.app.ctx.db
	secret = secrets.token_urlsafe(64)
	db.execute("INSERT INTO oauth_identification (user_id, access_token) VALUES (?,?)", user_id, secret)
	return secret

def save_refresh_token(request, user_id: int, refresh_token: str):
	db = request.app.ctx.db
	db.execute("INSERT INTO oauth_refresh (refresh_token, user_id) VALUES (?,?) ON DUPLICATE KEY UPDATE refresh_token = ?", refresh_token, user_id, refresh_token)
	return True


def get_user_from_secret(request, secret: str):
	db = request.app.ctx.db
	_id = db.query_row("SELECT user_id FROM oauth_identification WHERE access_token = ?", secret)
	return _id

def get_refresh_token(request, user_id: int):
	db = request.app.ctx.db
	token = db.query_row("SELECT refresh_token FROM oauth_refresh WHERE user_id = ?", user_id)
	return token


@blueprint.route('/')
async def dash_home(request):
	secret = request.cookies.get("secret")

	user_id = get_user_from_secret(request, secret)
	if user_id != None:
		refresh_token = get_refresh_token(request, user_id)
	else:
		return redirect("http://localhost:8080/dash/login")

	access = request.ctx.oauth.refresh_token(refresh_token) # Generate the new access token

	# Save the new refresh token 
	if save_refresh_token(request, user_id, access.refresh_token) == True:
		pass
	else:
		return text("Something went wrong saving new refresh key")

	identity = access.fetch_identify()

	guilds = access.fetch_guilds()
	bot_guilds = request.app.ctx.db.query("SELECT id FROM guilds")

	_guilds = []

	accepted_perms = [8, 32]

	for guild in guilds:
		if int(guild['id']) in bot_guilds:
			print(dir(guild))
			print(guild['permissions'])
			print(int(guild['permissions']))
			if guild['owner']:
				_guilds.append({"id": guild['id'], "icon_url": f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png"})
			elif int(guild['permissions']) in accepted_perms:
				print("Added")
				_guilds.append({"id": guild['id'], "icon_url": f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png"})

	name = identity['username']
	return await request.ctx.render("dashboard.html", context={"guild_count": len(bot_guilds), "guilds": _guilds, "username": name})

@blueprint.route('/view/<guild_id:int>')
async def dash_guild(request, guild_id: int):
	secret = request.cookies.get("secret")

	user_id = get_user_from_secret(request, secret)
	if user_id != None:
		refresh_token = get_refresh_token(request, user_id)
	else:
		return redirect("http://localhost:8080/dash/login")

	access = request.ctx.oauth.refresh_token(refresh_token) # Generate the new access token

	# Save the new refresh token 
	if save_refresh_token(request, user_id, access.refresh_token) == True:
		pass
	else:
		return text("Something went wrong saving new refresh key")

	bot_guilds = request.app.ctx.db.query("SELECT id FROM guilds")
	if guild_id not in bot_guilds:
		return text("Bot not in guild.")
	del bot_guilds
	
	guilds = access.fetch_guilds()

	guild = None
	for _guild in guilds:
		if int(_guild['id']) == guild_id:
			if int(_guild['permissions']) in [8, 32] or _guild['owner']:
				guild = _guild
			else:
				return text("Not a server admin.")
	if not guild:
		return text("Guild not found.")
	

	
	return await request.ctx.render("settings.html", context={"guild": guild})


@blueprint.route('/login')
def dash_login(request):
	return redirect(request.ctx.oauth.generate_uri(scope=["identify", "connections", "guilds"]))

@blueprint.route("/callback")
def gen_oauth2(request):
	code = request.args.get("code")

	try:
		access = request.ctx.oauth.exchange_code(code)
	except:
		redirect("http://localhost:8080/dash/login")

	identify = access.fetch_identify()

	secret = request.app.ctx.db.query_row("SELECT access_token FROM oauth_identification WHERE user_id = ?", identify['id'])
	if secret == None:
		secret = generate_user_secret(request, identify['id'])
	
	if save_refresh_token(request, identify['id'], access.refresh_token) == True:
		pass
	else:
		return text("Error while saving refresh token")

	print(f"User {identify['id']} with refresh token {access.refresh_token} and secret {secret}")
	
	response = redirect("http://localhost:8080/dash/")
	response.add_cookie(
        "secret",
        secret,
		path="*",
        httponly=True
    )

	return response