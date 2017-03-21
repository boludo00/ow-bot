import discord
from discord.ext.commands import Bot
import requests
import json
import re
from collections import OrderedDict
from datetime import datetime
import pyrebase
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pylab import *
import os


phoney_db = dict()

BOT_TOKEN = os.environ['BOT_TOKEN']
ENDPOINT = "https://enhanced-ow-api.herokuapp.com/"
FIREBASE = "https://brilliant-torch-8374.firebaseio.com/"

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://brilliant-torch-8374.firebaseio.com/",
  "storageBucket": "gs://brilliant-torch-8374.appspot.com/",
  "serviceAccount": "brilliant-torch-8374-firebase-adminsdk-3nctk-299b7654aa.json"
}


firebase = pyrebase.initialize_app(config)
db = firebase.database()


my_bot = Bot(command_prefix = "!")

def make_request(btag, system, mode, server=""):
    url = ENDPOINT + btag + "/" + mode  + "/" + system + "/" + server
    print("pinging " + url)
    resp = requests.get(url)
    obj = json.loads(resp.text)
    print("Done!")
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

def getHours(obj):
    for hero in obj:
        if obj[hero] >= 3600:
            obj[hero] = obj[hero] / 3600
        elif obj[hero] < 3600:
            obj[hero] = obj[hero] / 60
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
    print (snowflake)
    users = db.child("owbot").get().val()

    if snowflake in users:
        user_data = get_data(snowflake)
        tag = user_data['btag']
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

        time_map = OrderedDict(sorted(time_map.items(), key=lambda t: t[1], reverse = True))

        xs = list(time_map.values())
        xs = [float(x) / 3600 for x in xs]
        ys = np.arange(len(list(time_map.keys())))
        heros = tuple(time_map.keys())


        rcdefaults()
        fig, ax = plt.subplots()
        ax.barh(ys, xs, align='center', color='green')
        ax.set_yticks(ys)
        ax.set_yticklabels(heros)
        ax.invert_yaxis()
        ax.set_xlabel('Hours')
        if mode == 'q':
            disp_mode = 'quickplay'
        elif mode == 'c':
            disp_mode = 'competitive'
        ax.set_title(tag + '\nHours Played (' + disp_mode + ')')
        fig.savefig('f.png')
        await my_bot.send_file(ctx.message.channel, 'f.png')
        os.remove('f.png')

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
@my_bot.command(pass_context=True)
async def plot(ctx):
    y = [2,4,6,8,10,12,14,16,18,20]
    x = np.arange(10)
    fig = plt.figure()
    ax = plt.subplot(111)
    ax.plot(x, y, label='$y = numbers')
    plt.title('Legend inside')
    ax.legend()
    #plt.show()
 
    fig.savefig('plot.png')
    await my_bot.send_file(ctx.message.channel, 'plot.png')
    os.remove('plot.png')


def verify_battletag(btag):
    return re.match("\w+-\d{4}", btag)

my_bot.run(BOT_TOKEN)