from discord.ext.commands import Bot
import requests
import json

ENDPOINT = "https://enhanced-ow-api.herokuapp.com/"
BTAG = "(null)"
G_BTAG = "boludo00-1183" 

my_bot = Bot(command_prefix = "!")


@my_bot.event
async def on_ready():
    print("Client logged in")

@my_bot.command()
async def hello(*args):
    return await my_bot.say("hello, world")

@my_bot.command()
async def h():
    return await my_bot.say("Available commands:\n\n" \
                            "!login battle-tag (ex: !login john-1234)\n" \
                            "!stats hero (Only works if you've logged in. ex: !stats Tracer) \n\n" \
                            "Available heros:\n" \
                            "Reaper\n" 
                            "Tracer\n" \
                            "Mercy\n" \
                            "Hanzo\n" \
                            "Torbjörn\n" \
                            "Reinhardt\n" \
                            "Pharah\n" \
                            "Winston\n" \
                            "Widowmaker\n" \
                            "Bastion\n" \
                            "Symmetra\n" \
                            "Zenyatta\n" \
                            "Genji\n" \
                            "Roadhog\n" \
                            "McCree\n" \
                            "Junkrat\n" \
                            "Zarya\n" \
                            "Soldier: 76\n" \
                            "Lúcio\n" \
                            "D.Va\n" \
                            "Mei\n" \
                            "Sombra\n" \
                            "Ana\n" \
                            )

@my_bot.command()
async def login(battletag):
    global BTAG
    BTAG = battletag
    return await my_bot.say("Logged in with: " + battletag)

@my_bot.command()
async def show():
    return await my_bot.say("You are currently signed in with: " + BTAG)

@my_bot.command()
async def stats(hero):
    """
        Return the stats for requested hero assuming the user has already !login.
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