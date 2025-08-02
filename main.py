import json
import discord
import asyncio
from typing import Literal
from bot import Bot
from keys import token

def convertParams(searchParams: dict[str, list[str]]) -> dict[str, str | int | bool]:
    return {'characters': ','.join(searchParams['characters']), 'fandoms': ','.join(searchParams['fandoms'])}

def saveParams(searchParams: list[dict[str, list[str]]]):
    with open('data.json') as file:
        data = json.JSONDecoder().decode(file.read())
    data['searchParams'] = searchParams
    with open('data.json', 'w') as file:
        file.write(json.JSONEncoder().encode(data))

def searchEmpty(searchParams: list[dict[str, list[str]]]) -> bool:
    tot = 0
    for i in range(len(searchParams)):
        tot += searchParams[i]['characters'] == [] and searchParams[i]['fandoms'] == []
    return tot == len(searchParams)

def setBotInfo():
    saveParams(searchParams)
    bot.setInfo([convertParams(searchParams[i]) for i in range(len(searchParams))], updateTime, data['channelIDs'])

with open('data.json') as file:
    data = json.JSONDecoder().decode(file.read())

intents = discord.Intents.default()
intents.message_content = True
searchParams: list[dict[str, list[str]]] = data['searchParams']
updateTime: float = data['interval']

bot = Bot(command_prefix='$', intents=intents)
setBotInfo()

tree = bot.tree
@tree.command(name="addchannel", description="Adds current channel to the update list")
async def addChannel(interaction: discord.Interaction):
    with open('data.json') as file:
        data = json.JSONDecoder().decode(file.read())
    if interaction.channel.id not in data['channelIDs']: #type: ignore
        data['channelIDs'].append(interaction.channel.id) #type: ignore
        await interaction.response.send_message(f'Added channel "{interaction.channel.name}" to update list') #type: ignore
    else:
        await interaction.response.send_message(f'Channel "{interaction.channel.name}" is already in update list') #type: ignore
    with open('data.json', 'w') as file:
        file.write(json.JSONEncoder().encode(data))

@tree.command(name="removechannel", description="Removes current channel from the update list")
async def removeChannel(interaction: discord.Interaction):
    with open('data.json') as file:
        data = json.JSONDecoder().decode(file.read())
    try:
        data['channelIDs'].remove(interaction.channel.id) #type: ignore
        await interaction.channel.send(f'Removed channel "{interaction.channel.name}" from update list') #type: ignore
    except ValueError:
        await interaction.channel.send(f'Failed to remove channel "{interaction.channel.name}" from update list') #type: ignore
    with open('data.json', 'w') as file:
        file.write(json.JSONEncoder().encode(data))

@tree.command(name="addtag", description="Adds a tag to the search")
@discord.app_commands.describe(tagtype="The type of tag to add e.g. Character, Fandom", searchgroup='The search group to add the tag to', tag="The tag to add")
async def addTag(interaction: discord.Interaction, tagtype: Literal['characters', 'fandoms', 'tags', 'relationships'], tag: str, searchgroup: int = 1):
    try: 
        if tag not in searchParams[searchgroup - 1][tagtype]:
            searchParams[searchgroup - 1][tagtype].append(tag)
            await interaction.response.send_message(f'Added "{tag}" to search parameters for group {searchgroup}')
            setBotInfo()
        else:
            await interaction.response.send_message(f'"{tag}" is already in search parameters')
    except IndexError:
        await interaction.response.send_message(f'Group {searchgroup} does not exist')

@tree.command(name="removetag", description="Removes a tag from the search")
@discord.app_commands.describe(tagtype="The type of tag to remove e.g. Character, Fandom", searchgroup='The search group to add the tag to', tag="The tag to remove")
async def removeTag(interaction: discord.Interaction, tagtype: Literal['characters', 'fandoms', 'tags', 'relationships'], tag: str, searchgroup: int = 1):
    try:
        searchParams[searchgroup - 1][tagtype].remove(tag)
        await interaction.response.send_message(f'Removed "{tag}" from search parameters for group {searchgroup}')
        setBotInfo()
    except (ValueError, IndexError) as e:
        if e.__class__ == IndexError:
            await interaction.response.send_message(f'Group {searchgroup} does not exist')
        elif e.__class__ == ValueError: 
            await interaction.response.send_message(f'"{tag}" was not in search parameters')

@tree.command(name='addgroup', description='Adds a search group')
async def addGroup(interaction: discord.Interaction):
    with open('dataTemplate.json') as file:
        searchParams.append(json.JSONDecoder().decode(file.read())['searchParams'][0])
    saveParams(searchParams)
    await interaction.response.send_message('Group added!')

@tree.command(name="listtags", description="Lists the current tags in the search")
async def listTags(interaction: discord.Interaction):
    if searchEmpty(searchParams):
        await interaction.response.send_message('No tags currently selected')
    else:
        message = ''
        for i in range(len(searchParams)):
            message += f'Search Group {i+1}:\n'
            tags = sum(list(searchParams[i].values()), [])
            for tag in tags:
                message += f'\t{tag}\n'
        await interaction.response.send_message(message)

@tree.command(name="listchannels", description="Lists the current channels that are being updated")
async def listChannels(interaction: discord.Interaction):
    channelNames: list[str] = []
    for channelID in data['channelIDs']:
        channelNames.append(bot.get_channel(channelID).name) #type: ignore
    message = 'Channels:\n'
    for name in channelNames:
        message += f'\t{name}\n'
    await interaction.response.send_message(message)

@tree.command(name='setinterval', description='Sets the interval between searches')
@discord.app_commands.describe(interval='The time in hours')
async def setInterval(interaction: discord.Interaction, interval: float):
    with open('data.json') as file:
        data = json.JSONDecoder().decode(file.read())
    data['interval'] = interval
    with open('data.json', 'w') as file:
        file.write(json.JSONEncoder().encode(data))
    updateTime = interval
    setBotInfo()
    await interaction.response.send_message(f'Set interval to {interval} hours ({interval * 60} mins)')

@tree.command(name='start', description='Start the bot searching')
async def start(interaction: discord.Interaction):
    if searchEmpty(searchParams):
        await interaction.response.send_message('No tags currently selected, search cannot be started')
    else:
        if bot.bg_task:
            await interaction.response.send_message('Bot is already running!')
        else:
            bot.startSearch()
            await interaction.response.send_message('Started!')
            print('Started!')

@tree.command(name='stop', description='Stop the bot searching')
async def stop(interaction: discord.Interaction):
    if bot.bg_task:
        bot.bg_task.cancel()
        await interaction.response.send_message('Stopped!')
        print('Stopped!')
        bot.bg_task = None
    else:
        await interaction.response.send_message('Bot was not running!')

@tree.command(name='load', description='Load works without sending links. Useful for the first time using the bot')
async def load(interaction: discord.Interaction):
    if searchEmpty(searchParams):
        await interaction.response.send_message('No tags currently selected, search cannot be started')
    else:
        if bot.bg_task is None:
            bot.startSearch(False)
            print('Search Started!')
            try:
                await interaction.response.send_message('Loading... This may take up to 5 minutes depending on how many works need to be loaded')
                while not bot.bg_task.done(): # type: ignore
                    await asyncio.sleep(5)
                await interaction.channel.send('Loaded!') #type: ignore
                bot.bg_task = None
            except asyncio.TimeoutError:
                print('Time out error occured. Trying again')
                await interaction.channel.send('Time out error occured. Trying again') #type: ignore
                bot.bg_task = None
                bot.startSearch(False)
                await interaction.response.send_message('Loading... This may take up to 5 minutes depending on how many works need to be loaded')
                while not bot.bg_task.done(): # type: ignore
                    await asyncio.sleep(5)
                await interaction.channel.send('Loaded!') #type: ignore
                bot.bg_task = None
        else:
            await interaction.response.send_message('Bot is already running!')

bot.run(token)