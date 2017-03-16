from discord.ext.commands import Bot
import requests
import json
import re

ENDPOINT = "https://enhanced-ow-api.herokuapp.com/"

my_bot = Bot(command_prefix = "!")

@my_bot.event
async def on_ready():
    print("Client logged in")

@my_bot.command()
async def h():
    return await my_bot.say("Hi! I'm a bot here to provide useful Overwatch information! " \
                           "Below are some helpful commands and examples on how to use them.\n\n" \
                           "!stats [battletag] [platform] [mode] [hero]\n" \
                           "\t- Displays all stats for specififc hero.\n" \
                           "\t- Usage:\n\t\t!stats HughMungus-0420 pc comp McCree\n" \
                           "\t\t!stats HanzoMain69 xbox qp Bastion\n\n" \
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
async def stats(battletag, system, mode, hero):
    """
        Return the stats for requested hero assuming the user has already !login.
        usage:
            !stats john-0420 pc qp Hanzo
            !stats HughMungus xbox comp Hanzo
            !stats MarcellusWallace psn Hanzo
    """
    
    if mode not in ["qp", "comp"]:
        return await my_bot.say("Oops! Please specify qp or comp.")
    elif mode == "qp":
        mode = "quickplay"
    elif mode == "comp":
        mode = "competetive"
    
    need_verify = False
    if system == "xbox":
        platform = "xbl"
    elif system == "ps4":
        platform = "psn"
    elif system == "pc":
        need_verify = True
        platform = "pc/us/"
    else:
        return await my_bot.say("Incorrect platform input." \
                                "Choose any of 'xbox', 'ps4', or 'pc'.")
        
    if need_verify:
        ok_status = verify_battletag(battletag)
        if ok_status == None:
            return await my_bot.say("Oops! Your battle tag was not in the format of 'btag-0000'.")

    url = ENDPOINT + battletag + "/" + mode + "/" + platform
    print("pinging " + url)
    resp = requests.get(url)
    obj = json.loads(resp.text)
    for cat in obj[hero]:
        await my_bot.say(cat + "\n" + str(json.dumps(obj[hero][cat], indent = 4)).replace("{", "").replace("}", "") + "\n")

def verify_battletag(btag):
    return re.match("\w+-\d{4}", btag)

with open("info.txt") as f:
    token = f.read()

my_bot.run(token)