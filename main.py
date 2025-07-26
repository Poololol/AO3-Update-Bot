import AO3
import json
import time
import discord
from bot import Bot
from keys import token

searchParams = {'characters': 'Neuro-sama (Virtual Streamer)'}

with open('data.json') as file:
    data = json.JSONDecoder().decode(file.read())


intents = discord.Intents.default()
intents.message_content = True

bot = Bot(intents=intents)
bot.setInfo(searchParams, 1/30, data['channels'])
bot.run(token)