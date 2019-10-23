from dotenv import load_dotenv
from discord.ext import commands
from importlib import reload as rreload
import modules.constants
import urllib.request
import modules.constants as c
import discord
import os
import sys
import random
import traceback
import threading
import requests
from functools import partial
import os.path
from modules import checks
import json
from flask import Flask, g, session, redirect, request, url_for, jsonify, render_template, Response
from requests_oauthlib import OAuth2Session

AUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']

OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']

OAUTH2_REDIRECT_URI = f'{discordapp}.com/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


app = Flask(__name__)
run_flag = True
app.debug = False
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'false'


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None, sv=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


@app.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord_s = make_session()
    token = discord_s.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token
    return redirect(url_for('.me'))


@app.route('/me')
def me():
    discord_s = make_session(token=session.get('oauth2_token'))
    verified = c._internal_API.checkEmail(discord_s.get(
        API_BASE_URL + '/users/@me').json()['verified'])
    if verified:
        redirect(c.redirect_complete)
        return "Verification SUCCESS"
    return "Verification Failed"


load_dotenv()
#token = os.getenv('DISCORD_TOKEN')
token = c.token
bot = commands.Bot(command_prefix=c.prefix)
extensions = ['cogs.verify']


@bot.command()
@commands.check(checks.search_check)
async def load(ctx, extension):
    try:
        bot.load_extension(extension)
        print(f"Loaded: {extension}")
        return await ctx.send(f"Module loaded: {extension}")
    except Exception as err:
        print(f"{extension} Cannot be loaded.\n[{err}]")
    return await ctx.send(f"{extension} Cannot be loaded.\n[{err}]")


@bot.command()
@commands.check(checks.search_check)
async def unload(ctx, extension):
    try:
        bot.unload_extension(extension)
        print(f"Unloaded: {extension}")
        return await ctx.send(f"Module unloaded: {extension}")
    except Exception as err:
        print(f"{extension} Cannot be unloaded.\n[{err}]")
    return await ctx.send(f"{extension} Cannot be unloaded.\n[{err}]")


@bot.command()
@commands.check(checks.search_check)
async def reload(ctx, extension):
    try:
        bot.reload_extension(extension)
        print(f"Reloaded: {extension}")
        return await ctx.send(f"Module reloaded: {extension}")
    except Exception as err:
        print(f"{extension} Cannot be Reloaded.\n[{err}]")
        return await ctx.send(f"{extension} Cannot be reloaded.\n[{err}]")


@bot.command()
@commands.check(checks.search_check)
async def set_prefix(ctx, newprefix):
    rreload(checks)
    with open("constants.json", "r") as f:
        data = json.load(f)
    data['prefix'] = newprefix
    with open("constants.json", "w") as f:
        json.dump(data, f)
    bot.command_prefix = newprefix
    return print(f"Prefix Set: {newprefix}")


@bot.command()
@commands.check(checks.search_check)
async def logout(ctx):
    rreload(checks)
    await ctx.bot.logout()
if __name__ == '__main__':
    partial_run = partial(app.run, host='0.0.0.0', debug=False,
                          threaded=True, use_reloader=False)
    t = threading.Thread(target=partial_run)
    t.daemon = True
    t.start()
    for extension in extensions:
        try:
            bot.load_extension(extension)
            print(f"Loaded: {extension}")
        except Exception as err:
            print(f"{extension} Cannot be Loaded.\n[{err}]")
    bot.run(token)
