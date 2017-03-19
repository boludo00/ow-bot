import discord
from discord.ext.commands import Bot
import requests
import json
import re
from collections import OrderedDict
from datetime import datetime
import pyrebase

phoney_db = dict()
test_db = dict(a="a",b="b",c="c")

ENDPOINT = "https://enhanced-ow-api.herokuapp.com/"
FIREBASE = "https://brilliant-torch-8374.firebaseio.com/"

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": FIREBASE,
  "storageBucket": "projectId.appspot.com"
}

data = {"name": "Mortimer 'Morty' Smith"}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
# db.child("users").child("Morty").set(data)


my_bot = Bot(command_prefix = "!")

def make_request(btag, system, mode, server=""):
    url = ENDPOINT + btag + "/" + mode  + "/" + system + "/" + server
    print("pinging " + url)
    resp = requests.get(url)
    obj = json.loads(resp.text)
    return obj

def get_data(user):
    users = db.child("owbot").get().val()

    if user in users:
        return users[user]
    else:
        return None

def get_response(data, mode):
    system = data["system"]
    btag = data["btag"]
    server = ""
    if mode == "q":
        mode = "quickplay"
    elif mode == "c":
        mode = "competetive"

    if "server" in data:
        server = data["server"]
        return make_request(btag, system, mode, server=server)
    else:
        return make_request(btag, system, mode)


def convertToHours(obj):
    for hero in obj:
        if obj[hero] >= 3600:
            obj[hero] = str(obj[hero] / 3600) + "h"
        elif obj[hero] < 3600:
            obj[hero] = str(obj[hero] / 60) + "m"
    return obj
    

@my_bot.event
async def on_ready():
    print("Client logged in")

@my_bot.event
async def on_message(message):
    # listen for init command
    await my_bot.process_commands(message)
    if message.content.startswith('?init'):
        args = message.content[6:].split(" ")
        # process args 
        btag = args[0]
        system = args[1]
        server = ""
        if system == "pc":
            server = args[2]

        snowflake = message.author.id
        phoney_db[snowflake] = dict(btag=btag, system=system) 
        if server != "":
            phoney_db[snowflake].update(dict(server=server))
        
        # add this entry to the db
        db.child("owbot").set(phoney_db)

        await my_bot.send_message(message.channel, 'Say hello')
        msg = await my_bot.wait_for_message(author=message.author, content='hello')
        await my_bot.send_message(message.channel, 'Hello.')

@my_bot.command(pass_context=True)
async def statz(ctx, hero, mode):
    snowflake = ctx.message.author.id

    users = db.child("owbot").get().val()
    if snowflake in users:
        user_data = users[snowflake]
        resp = get_response(user_data, mode)
            
        for key in resp:
             if key.lower() == hero.lower():
                 hero = key

        for cat in resp[hero]:
            await my_bot.say(cat + "\n" + str(json.dumps(resp[hero][cat], indent = 4)).replace("{", "").replace("}", "") +"\n")

    else:
        print("Couldnt locate Snowflake.")
    
@my_bot.command(pass_context=True)
async def time(ctx, mode):
    snowflake = ctx.message.author.id
    users = db.child("owbot").get().val()

    if snowflake in users:
        user_data = get_data(snowflake)
        resp = get_response(user_data, mode)
        time_map = dict()
        for hero, hero_data in resp.items():
            if hero == "ALL HEROES":
                continue
            if hero_data["Game"]:
                if hero_data["Game"]["Time Played"]:
                    time_string = hero_data["Game"]["Time Played"]
                    time = int(re.search("\d+", time_string).group(0))

                    if "minute" in time_string:
                        secs_time = time * 60
                    elif "hour" in time_string:
                        secs_time = time * 3600

                    time_map[hero] = secs_time
        time_obj = convertToHours(OrderedDict(sorted(time_map.items(), key=lambda t: t[1], reverse = True)))
        return await my_bot.say(" "+str(json.dumps(time_obj, indent=0).replace("{", "").replace("}", "")))

@my_bot.command()
async def h():
    return await my_bot.say("Hi! I'm a bot here to provide useful Overwatch information!" \
                           "Below are some helpful commands and examples on how to use them.\n\n" \
                           "?init [battletag] [system] [server] (only if system is pc)\n" \
                           "\t - Parameters:\n\t\t- battletag: Either the Xbox live gamertag, PSN " \
                           "username, or PC battletag.\n\t\tPC battletags must include the 4 digits \n" \
                           "following their battletag in the format of 'battletag-0069'.\n\t\t" \
                           "system: The platform belonging to your battletag. Acceptable inputs are: " \
                           "'xbl', 'psn', 'pc'.\n\t\t" \
                           "server (If system = pc): The server belonging to the the battle net account. " \
                           "Acceptable inputs are: 'us' (North America), 'kr' (Korea), 'eu' (Europe). "\
                           "\t- Description:\n\t\tInitialize your battle.net information so I can determine "\
                           "what information to send.\n" \
                           "\t- Usage:\n\t\t?init HanzoGod-0420 pc us\n\t\t" \
                           "?init daddy69 xbl\n" \
                           
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




def verify_battletag(btag):
    return re.match("\w+-\d{4}", btag)

with open("info.txt") as f:
    token = f.read()

my_bot.run(token)