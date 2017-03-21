import json
import re
from collections import OrderedDict
from datetime import datetime

with open("resp.json") as f:
    data = json.load(f)


def top():
    resp = dict()
    for hero, hero_data in data.iteritems():
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

                resp[hero] = secs_time
    return OrderedDict(sorted(resp.items(), key=lambda t: t[1], reverse = True))

def convertToHours(obj):
    for hero in obj:
        if obj[hero] >= 3600:
            obj[hero] = str(obj[hero] / 3600) + "h"
        elif obj[hero] < 3600:
            obj[hero] = str(obj[hero] / 6) + "m"
    return obj