from discord.ext.commands import Bot

my_bot = Bot(command_prefix = "!")

@my_bot.event
async def on_ready():
    print("Client logged in")

@my_bot.command()
async def hello(*args):
    return await my_bot.say("hello, world")

my_bot.run("MjkxMDM4MzA2MDYwNDY4MjI0.C6jqSQ.FGHkHtGg8CPRu4W1Os-EbUq48pA")