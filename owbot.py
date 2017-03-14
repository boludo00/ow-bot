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
    resp_text = resp.text
    print("character cout  of response: " + str(len(resp_text)))
    obj = json.loads(resp.text)
    print("Stats for " + hero)
    for hero_sub in obj[hero]:
        print(hero_sub+":\n")
        # await my_bot.say(hero_sub+":\n")
        sub_obj = obj[hero][hero_sub]
        for value in sub_obj:
            print(value + " -> " + sub_obj[value])
            # await my_bot.say(value + ": " + sub_obj[value])

    # return await my_bot.say(json.dumps(obj[hero]["Hero Specific"], indent = 4))
    for cat in obj[hero]:
        await my_bot.say(cat + "\n" + str(json.dumps(obj[hero][cat], indent = 4)).replace("{", "").replace("}", "") + "\n")

@my_bot.command()
async def test():
    url = "http://enhanced-ow-api.herokuapp.com/boludo00/quickplay/xbl/"
    resp = requests.get(url)
    print(resp.json()["Mei"]["Assists"])
    await my_bot.say("Your stats: ")
    await my_bot.say(resp.json()["Mei"]["Assists"])
    


my_bot.run("MjkxMDM4MzA2MDYwNDY4MjI0.C6jqSQ.FGHkHtGg8CPRu4W1Os-EbUq48pA")