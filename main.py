import json
import discord
import asyncio
from bot import Bot
from keys import token

def convertParams(searchParams: dict[str, list[str]]) -> dict[str, str | int | bool]:
    with open('data.json') as file:
        data = json.JSONDecoder().decode(file.read())
    data['searchParams'] = searchParams
    with open('data.json', 'w') as file:
        file.write(json.JSONEncoder().encode(data))
    return {'characters': ','.join(searchParams['characters']), 'fandoms': ','.join(searchParams['fandoms'])}

with open('data.json') as file:
    data = json.JSONDecoder().decode(file.read())

intents = discord.Intents.default()
intents.message_content = True
searchParams = data['searchParams']
updateTime = data['interval']

bot = Bot(command_prefix='$', intents=intents)
bot.setInfo(convertParams(searchParams), updateTime, data['channelIDs'])

tree = bot.tree
@tree.command(name="addchannel", description="Adds current channel to the update list")
async def addChannel(interaction: discord.Interaction):
    with open('data.json') as file:
        data = json.JSONDecoder().decode(file.read())
    if interaction.channel.id not in data['channelIDs']:
        data['channelIDs'].append(interaction.channel.id)
        await interaction.response.send_message(f'Added channel "{interaction.channel.name}" to update list')
    else:
        await interaction.response.send_message(f'Channel "{interaction.channel.name}" is already in update list')
    with open('data.json', 'w') as file:
        file.write(json.JSONEncoder().encode(data))

@tree.command(name="removechannel", description="Removes current channel from the update list")
async def removeChannel(interaction: discord.Interaction):
    with open('data.json') as file:
        data = json.JSONDecoder().decode(file.read())
    try:
        data['channelIDs'].remove(interaction.channel.id)
        await interaction.channel.send(f'Removed channel "{interaction.channel.name}" from update list') #type: ignore
    except ValueError:
        await interaction.channel.send(f'Failed to remove channel "{interaction.channel.name}" from update list') #type: ignore
    with open('data.json', 'w') as file:
        file.write(json.JSONEncoder().encode(data))

@tree.command(name="addchartag", description="Adds a character tag to the search")
@discord.app_commands.describe(tag="The character tag")
async def addCharTag(interaction: discord.Interaction, tag: str):
    if tag not in searchParams['characters']:
        searchParams['characters'].append(tag)
        await interaction.response.send_message(f'Added "{tag}" to search parameters') #type: ignore
        bot.setInfo(convertParams(searchParams), updateTime, data['channelIDs'])
    else:
        await interaction.response.send_message(f'"{tag}" is already in search parameters') #type: ignore

@tree.command(name="removechartag", description="Removes a character tag from the search")
@discord.app_commands.describe(tag="The character tag")
async def removeCharTag(interaction: discord.Interaction, tag: str):
    try:
        searchParams['characters'].remove(tag)
        await interaction.response.send_message(f'Removed "{tag}" from search parameters') #type: ignore
        bot.setInfo(convertParams(searchParams), updateTime, data['channelIDs'])
    except ValueError:
        await interaction.response.send_message(f'"{tag}" was not in search parameters') #type: ignore

@tree.command(name="addfandomtag", description="Adds a fandom tag to the search")
@discord.app_commands.describe(tag="The fandom tag")
async def addFandomTag(interaction: discord.Interaction, tag: str):
    if tag not in searchParams['fandoms']:
        searchParams['fandoms'].append(tag)
        await interaction.response.send_message(f'Added "{tag}" to search parameters') #type: ignore
        bot.setInfo(convertParams(searchParams), updateTime, data['channelIDs'])
    else:
        await interaction.response.send_message(f'"{tag}" is already in search parameters') #type: ignore

@tree.command(name="removefandomtag", description="Removes a fandom tag from the search")
@discord.app_commands.describe(tag="The fandom tag")
async def removeFandomTag(interaction: discord.Interaction, tag: str):
    try:
        searchParams['fandoms'].remove(tag)
        await interaction.response.send_message(f'Removed "{tag}" from search parameters') #type: ignore
        bot.setInfo(convertParams(searchParams), updateTime, data['channelIDs'])
    except ValueError:
        await interaction.response.send_message(f'"{tag}" was not in search parameters') #type: ignore

@tree.command(name="listtags", description="Lists the current tags in the search")
async def listTags(interaction: discord.Interaction):
    if searchParams['characters'] == []:
        await interaction.response.send_message('No tags currently selected')
    else:
        await interaction.response.send_message(f'{'\n'.join(searchParams['characters'])}') #type: ignore

@tree.command(name='setinterval', description='Sets the interval between searches')
@discord.app_commands.describe(interval='The time in hours')
async def setInterval(interaction: discord.Interaction, interval: float):
    with open('data.json') as file:
        data = json.JSONDecoder().decode(file.read())
    data['interval'] = interval
    with open('data.json', 'w') as file:
        file.write(json.JSONEncoder().encode(data))
    updateTime = interval
    bot.setInfo(convertParams(searchParams), updateTime, data['channelIDs'])
    await interaction.response.send_message(f'Set interval to {interval} hours ({interval * 60} mins)')

@tree.command(name='start', description='Start the bot searching')
async def start(interaction: discord.Interaction):
    if searchParams['characters'] == []:
        await interaction.response.send_message('No tags currently selected, search cannot be started')
    else:
        bot.bg_task = bot.loop.create_task(bot.search(bot.searchParams))
        await interaction.response.send_message('Started!')

@tree.command(name='stop', description='Stop the bot searching')
async def stop(interaction: discord.Interaction):
    bot.bg_task.cancel()
    await interaction.response.send_message('Stopped!')

@tree.command(name='load', description='Load works without sending links. Useful for the first time using the bot')
async def load(interaction: discord.Interaction):
    if searchParams['characters'] == []:
        await interaction.response.send_message('No tags currently selected, search cannot be started')
    else:
        bot.bg_task = bot.loop.create_task(bot.search(bot.searchParams, False))
        await interaction.response.send_message('Loading...')
        while not bot.bg_task.done():
            await asyncio.sleep(5)
        await interaction.channel.send('Loaded!')

bot.run(token)