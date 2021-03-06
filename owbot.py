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
import plotly.plotly as py
import plotly.graph_objs as go
from functools import partial

# authenticate with plotly
py.sign_in("boludo00", "caCJFQ3nYafwrCXikwVv")

test_token = "MjkxMDM4MzA2MDYwNDY4MjI0.C-lPqw.7pngM2sKkkXeYXKfXRjhSfLEga8"
# BOT_TOKEN = os.environ['BOT_TOKEN']
ENDPOINT = "https://enhanced-ow-api.herokuapp.com/"
FIREBASE = "https://brilliant-torch-8374.firebaseio.com/"

config = {
    "apiKey": "AIzaSyCBqo72uWGeOKEEBbjg4gzHhvtFHJqtj8k",
    "authDomain": "brilliant-torch-8374.firebaseapp.com",
    "databaseURL": "https://brilliant-torch-8374.firebaseio.com/",
    "storageBucket": "brilliant-torch-8374.appspot.com",
    "messagingSenderId": "251897490818"
}


firebase = pyrebase.initialize_app(config)
db = firebase.database()


my_bot = Bot(command_prefix = "!")

def file_reader(filename):
    with open(filename + ".txt") as f:
        msg = f.read()
    return my_bot.say(msg)

def graph_avg_dmg(data, user):
    hero_to_avgs = list()

    for hero in data:
        if hero == "ALL HEROES":
            continue
        if "Average" in data[hero]:
            if "Damage Done - Average" in data[hero]["Average"]:
                avg_dmg = eval(data[hero]["Average"]["Damage Done - Average"].replace(",", ""))
                hero_to_avgs.append((hero, avg_dmg))

    hero_to_avgs = sorted(hero_to_avgs, key=lambda x: x[1], reverse=True)
    trace = go.Bar(x=list(zip(*hero_to_avgs))[0], y=list(zip(*hero_to_avgs))[1])
    layout = go.Layout(title=user + " Average Damage (quickplay)", xaxis=dict(tickangle=45))
    data = [trace]

    fig = go.Figure(data=data, layout=layout)
    return fig

def bubble_graph_avg_dmg(data, user, mode):
    hero_to_avgs = list()

    with open("data/colormap.json") as f:
        colors = json.load(f)

    if mode == "c":
        mode = "competitive"
    elif mode == "q":
        return graph_avg_dmg(data, user)
        
    for hero in data:
        if hero == "ALL HEROES":
            continue
        # print(hero)
        # print(json.dumps(data[hero], indent=4))
        if "Combat" in data[hero]:
            if "All Damage Done" in data[hero]["Combat"]:
                if "Game" in data[hero]:
                    all_dmg = eval(data[hero]["Combat"]["All Damage Done"].replace(",", ""))
                    played = eval(data[hero]["Game"]["Games Played"])
                    print(hero)
                    print(all_dmg)
                    print(played)
                    if played == 0:
                        avg_dmg = 0
                    else:
                        avg_dmg = float(all_dmg) / played
                    hero_to_avgs.append((hero, avg_dmg, played, colors[hero]))

    hero_to_avgs = sorted(hero_to_avgs, key=lambda x: x[1], reverse=True)
    layout = go.Layout(title=user + " Average Damage (" + mode + ")", xaxis=dict(tickangle=45))    
    trace0 = go.Scatter(
    x=list(zip(*hero_to_avgs))[0],
    y=list(zip(*hero_to_avgs))[1],
    mode='markers',
    marker=dict(
        size=list(zip(*hero_to_avgs))[2],
        sizeref = .8,
        color=list(zip(*hero_to_avgs))[3]
        )
    )
    data = [trace0]
    
    fig = go.Figure(data=data, layout=layout)
    return fig


def graph_win_rate(data, user):
    heros = []
    games_won_vs_lost = []

    for hero in data.keys():
        if hero == "ALL HEROES":
            continue
        if "Game" in data[hero]:
            print(hero)
            if "Games Won" in data[hero]["Game"]:
                heros.append(hero)
                num_won = eval(data[hero]["Game"]["Games Won"])
                num_played = eval(data[hero]["Game"]["Games Played"])

                games_won_vs_lost.append((hero, num_won, num_played, num_played-num_won))

    games_won_vs_lost = sorted(games_won_vs_lost, key=lambda x: x[2], reverse=True)
    heros = list(zip(*games_won_vs_lost))[0]
    won = list(zip(*games_won_vs_lost))[1]
    total_played = list(zip(*games_won_vs_lost))[2]
    lost = list(zip(*games_won_vs_lost))[3]
    print(games_won_vs_lost)
    trace1 = go.Bar(
        x=heros,
        y=won,
        name='Games Won'
    )
    trace2 = go.Bar(
        x=heros,
        y=lost,
        name='Games Lost'
    )

    data = [trace1, trace2]
    layout = go.Layout(
        title="Win rate for " + user + " (current season)",
        barmode='stack',
        xaxis=dict(tickangle=45),
        annotations=[
            dict(x=xi,y=yi,
                text=str("{0:.2f}".format(float(yi)/zi)) if zi > 0 else 0,
                xanchor='center',
                yanchor='bottom',
                showarrow=False,
            ) for xi, yi, zi in zip(heros, won, total_played)]
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


def make_request(btag, system, mode, server=""):
    print(btag)
    url = ENDPOINT + btag + "/" + mode  + "/" + system + "/" + server
    print("pinging " + url)
    resp = requests.get(url)
    for response in resp.history:
        print(response.url)
    if resp.status_code == 500:
        print("oops")
        return None
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

def elim_min(resp, hero):
    # if hero in resp
    if hero not in resp:
        return -1
    
    # parse string number and handle commas 
    total_elims = eval("".join(resp[hero]["Combat"]["Eliminations"].split(",")))

    time_string = resp[hero]["Game"]["Time Played"]
    
    time = int(re.search("\d+", time_string).group(0))

    if "hour" in time_string:
        min_time = time * 60
    else: 
        min_time = time
    

    return float(total_elims) / min_time

def death_min(resp, hero):
    # if hero in resp:
    if hero not in resp:
        return -1
    total_death = eval(resp[hero]["Deaths"]["Deaths"])
    if "Environmental Deaths" in resp[hero]["Deaths"]:
        total_death += eval(resp[hero]["Deaths"]["Environmental Deaths"])
    time_string = resp[hero]["Game"]["Time Played"]
    
    time = int(re.search("\d+", time_string).group(0))

    if "hour" in time_string:
        min_time = time * 60
    else:
        min_time = time


    return float(total_death) / min_time

def ult_game(resp, hero):
    if hero not in resp:
        return -1
    # get ult name for specific hero
    with open("data/ults.json") as f:
        ult_map = json.load(f)
    ult_name = ult_map[hero]

    if "Ultimates Earned" in resp[hero]["Miscellaneous"]:
        num_ults = eval(resp[hero]["Miscellaneous"]["Ultimates Earned"])
    else:
        return my_bot.say("No Ult data for " + hero)

    if "Hero Specific" in resp[hero]:
        ult_kills = eval(resp[hero]["Hero Specific"][ult_name + " Kills"])
    else:
        return -1

    time_string = resp[hero]["Game"]["Time Played"]
    
    time = int(re.search("\d+", time_string).group(0))

    if "hour" in time_string:
        min_time = time * 60
    else:
        min_time = time

    ults_min = float(ult_kills) / min_time
    return ult_name, round(ults_min, 2)



@my_bot.event
async def on_ready():
    print("Client logged in")

# @my_bot.event(pass_context=True)
# async def on_message(message):
#     # listen for init command
#     await my_bot.process_commands(message)
#     if message.content.startswith('?hello'):
#         args = message.content[7:].split(" ")

@my_bot.command(pass_context=True)
async def update(ctx, btag):
    snowflake = ctx.message.author.id

    db_tag = btag.replace(" ", "%20")

    users = db.child("owbot").get()

    await login_searcher(btag, "quickplay", snowflake, "update")

@my_bot.command(pass_context=True)
async def login(ctx, btag, mode = "quickplay"):

    user_exists = False
    snowflake = ctx.message.author.id

    db_tag = btag.replace(" ", "%20")

    users = db.child("owbot").get()

    for u in users.each():
        if snowflake == u.key():
            user_exists = True

    if not user_exists:
        print("New snowflake detected")
        await login_searcher(btag, mode, snowflake, "set")
    else:
        await my_bot.say("You're already in the system! Please use !update.")

async def login_searcher(btag, mode, snowflake, func):
    left = btag.rfind('-')
    right = len(btag) - 5
    exact = left - right

    systems = {"xbl", "psn"}
    servers = {"us", "eu", "kr"}

    snowflake_entry = db.child("owbot").child(snowflake)

    if exact == 0:
        for server in servers:
            resp = make_request(btag, "pc", mode, server)
            if resp == None:
                print("rekt")
            else:
                entry = dict()
                entry[snowflake] = dict(btag=btag, system="pc", server=server)
                if func == "set":
                    snowflake_entry.set(entry[snowflake])
                else:
                    snowflake_entry.update(entry[snowflake])
                await my_bot.say("Successfully stored battletag")
                break
    else:
        for system in systems:
            resp = make_request(btag, system, mode, server="")
            if resp == None:
                print("rekt")
            else:
                entry = dict()
                entry[snowflake] = dict(btag=btag, system=system, server="")
                if func == "set":
                    snowflake_entry.set(entry[snowflake])
                else:
                    snowflake_entry.update(entry[snowflake])
                if system == "xbl":
                    await my_bot.say("Successfully stored gamertag")
                else:
                    await my_bot.say("Successfully stored psn")
                break

    data_entry = db.child("owbot").child(snowflake).child("btag").get()
    if data_entry.val() != btag:
        await my_bot.say("Please enter a valid login.")

@my_bot.command(pass_context=True)
async def statz(ctx, hero, mode):

    # handle this soldier 76 case differently (this is lazy)
    if hero.lower() == "soldier:76":
        hero = "soldier: 76"

    snowflake = ctx.message.author.id

    users = db.child("owbot").get().val()
    if snowflake in users:
        user_data = users[snowflake]
        resp = get_response(user_data, mode)
        if resp is None:
            return await my_bot.say("Server error, make sure your gamertag is correct!")

        for key in resp:
             if key.lower() == hero.lower():
                 hero = key

        for cat in resp[hero]:
            await my_bot.say("```python\n"+ cat + "\n" + str(json.dumps(resp[hero][cat], indent = 4)).replace("{", "").replace("}", "") +"```\n")

    else:
        print("Couldnt locate Snowflake.")

@my_bot.command(pass_context=True)
async def summary(ctx, hero):
    snowflake = ctx.message.author.id
    users = db.child("owbot").get().val()

    if snowflake in users:
        user_data = get_data(snowflake)
        tag = user_data['btag']
        resp = get_response(user_data, "c")
        if resp is None:
            return await my_bot.say("Server error, double check your gamertag!")
        
        winrate = resp[hero]["Game"]["Win Percentage"] if "Win Percentage" in resp[hero]["Game"] else "0%"
        dpm = round(death_min(resp, hero), 2)
        epm = round(elim_min(resp, hero), 2)
        # u_name, uper_min = ult_game(resp, hero)
        await my_bot.say("**" + hero + "**" + "\n**Elims / min: **" + str(epm) +
                        "\n**Deaths / min: **" + str(dpm) + "\n**Winrate: **" + winrate)


@my_bot.command(pass_context=True)
async def time(ctx, mode):
    snowflake = ctx.message.author.id
    print (snowflake)
    users = db.child("owbot").get().val()

    plt.xkcd()

    if snowflake in users:
        user_data = get_data(snowflake)
        tag = user_data['btag']
        resp = get_response(user_data, mode)
        if resp is None:
            return await my_bot.say("Server error, double check your gamertag!")
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

@my_bot.command(pass_context=True)
async def winrate(ctx):
    snowflake = ctx.message.author.id
    print (snowflake)
    users = db.child("owbot").get().val()
    if snowflake in users:
        user_data = get_data(snowflake)
        tag = user_data['btag']
        resp = get_response(user_data, "c")
        if resp is None:
            return await my_bot.say("Server error, double check your gamertag!")
        fig = graph_win_rate(resp, tag)
        py.image.save_as(fig, filename='win_rate_stacked.png')
        await my_bot.send_file(ctx.message.channel, 'win_rate_stacked.png')
        os.remove('win_rate_stacked.png')

@my_bot.command(pass_context=True)
async def dmg(ctx, mode):
    snowflake = ctx.message.author.id
    print (snowflake + " requesting average damage...")
    users = db.child("owbot").get().val()
    if snowflake in users:
        user_data = get_data(snowflake)
        tag = user_data['btag']
        resp = get_response(user_data, mode)
        if resp is None:
            return await my_bot.say("Server error, double check your gamertag!")
        # fig = graph_avg_dmg(resp, tag, mode)
        fig = bubble_graph_avg_dmg(resp, tag, mode)
        py.image.save_as(fig, filename='avg_damage.png')
        await my_bot.send_file(ctx.message.channel, 'avg_damage.png')
        os.remove('avg_damage.png')



@my_bot.command()
async def h():
    await file_reader("help")

@my_bot.command()
async def commands():
    await file_reader("commands")


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

my_bot.run(test_token)
