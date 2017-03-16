from discord.ext.commands import Bot
import requests
import json

ENDPOINT = "https://enhanced-ow-api.herokuapp.com/"

my_bot = Bot(command_prefix = "!")

@my_bot.event
async def on_ready():
    print("Client logged in")

@my_bot.command()
async def h():
    return await my_bot.say("Hi! I'm a bot here to provide useful Overwatch information! " \
                           "Below are some helpful commands and examples on how to use them.\n\n" \
                           "!stats_comp battletag platform hero\n" \
                           "\t- Displays all competitive stats for specififc hero in the current Season.\n" \
                           "\t- Usage: !stats_comp john-0420 pc McCree\n\n"
                            "!stats_qp battletag platform hero\n" \
                            "\t- Displays all quickplay stats for specific Hero.\n" \
                            "\t- Usage: !stats_qp HanzoMain xbox Hanzo\n\n" \
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
async def stats_comp(battletag, system, hero):
    """
        Return the stats for requested hero assuming the user has already !login.
        usage:
            !stats john-0420 pc Hanzo
            !stats HughMungus xbox Hanzo
            !stats MarcellusWallace ps4 Hanzo
    """
    if system == "xbox":
        platform = "xbl"
    elif system == "ps4":
        platform = "ps4"
    elif system == "pc":
        platform = "pc/us/"
    else:
        return await my_bot.say("Incorrect platform input." \
                                "Choose any of 'xbox', 'ps4', or 'pc'.")
         
    url = ENDPOINT + battletag + "/competetive/" + platform
    print("pinging " + url)
    resp = requests.get(url)
    obj = json.loads(resp.text)
    for cat in obj[hero]:
        await my_bot.say(cat + "\n" + str(json.dumps(obj[hero][cat], indent = 4)).replace("{", "").replace("}", "") + "\n")

@my_bot.command()
async def stats_qp(battletag, system, hero):
    """
        Return the stats for requested hero assuming the user has already !login.
        usage:
            !stats john-0420 pc Hanzo
            !stats HughMungus xbox Hanzo
            !stats MarcellusWallace ps4 Hanzo
    """
    if system == "xbox":
        platform = "xbl"
    elif system == "ps4":
        platform = "ps4"
    elif system == "pc":
        platform = "pc/us/"
    else:
        return await my_bot.say("Incorrect platform input." \
                                "Choose any of 'xbox', 'ps4', or 'pc'.")
         
    url = ENDPOINT + battletag + "/quickplay/" + platform
    print("pinging " + url)
    resp = requests.get(url)
    obj = json.loads(resp.text)
    for cat in obj[hero]:
        await my_bot.say(cat + "\n" + str(json.dumps(obj[hero][cat], indent = 4)).replace("{", "").replace("}", "") + "\n")

with open("info.txt") as f:
    token = f.read()

my_bot.run(token)