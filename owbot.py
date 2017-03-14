from discord.ext.commands import Bot
import requests
import json

ENDPOINT = "https://enhanced-ow-api.herokuapp.com/"
BTAG = "(null)  "
G_BTAG = "boludo00-1183" 

my_bot = Bot(command_prefix = "!")


@my_bot.event
async def on_ready():
    print("Client logged in")

@my_bot.command()
async def hello(*args):
    return await my_bot.say("hello, world")

@my_bot.command()
async def login(battletag):
    global BTAG
    BTAG = battletag
    print("to " + BTAG)
    return await my_bot.say("Logged in with: " + battletag)

@my_bot.command()
async def show():
    return await my_bot.say("You are currently signed in with: " + BTAG)

@my_bot.command()
async def stats(hero):
    """
        Return the stats for requested hero.
        usage:
            !stats Hanzo
    """
    url = ENDPOINT + BTAG + "/quickplay/" + "pc/us/"
    print("pinging " + url)
    resp = requests.get(url)
    obj = json.loads(resp.text)
    for cat in obj[hero]:
        await my_bot.say(cat + "\n" + str(json.dumps(obj[hero][cat], indent = 4)).replace("{", "").replace("}", "") + "\n")


my_bot.run("MjkxMDM4MzA2MDYwNDY4MjI0.C6jqSQ.FGHkHtGg8CPRu4W1Os-EbUq48pA")