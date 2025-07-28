import json
import discord
import asyncio
from typing import Literal
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
GUILD = 1081778285136060436
guild = discord.Object(id=GUILD)

bot = Bot(command_prefix='$', intents=intents)
bot.setInfo(convertParams(searchParams), updateTime, data['channelIDs'])

tree = bot.tree
@tree.command(name="addchannel", description="Adds current channel to the update list", guild=guild)
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

@tree.command(name="removechannel", description="Removes current channel from the update list", guild=guild)
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

@tree.command(name="addtag", description="Adds a tag to the search", guild=guild)
@discord.app_commands.describe(tagtype="The type of tag to add e.g. Character, Fandom", tag="The tag to add")
async def addTag(interaction: discord.Interaction, tagtype: Literal['characters', 'fandoms'], tag: str):
    if tag not in searchParams[tagtype]:
        searchParams[tagtype].append(tag)
        await interaction.response.send_message(f'Added "{tag}" to search parameters') #type: ignore
        bot.setInfo(convertParams(searchParams), updateTime, data['channelIDs'])
    else:
        await interaction.response.send_message(f'"{tag}" is already in search parameters') #type: ignore

@tree.command(name="removetag", description="Removes a tag from the search", guild=guild)
@discord.app_commands.describe(tagtype="The type of tag to add e.g. Character, Fandom", tag="The tag to remove")
async def removeTag(interaction: discord.Interaction, tagtype: Literal['characters', 'fandoms'], tag: str):
    try:
        searchParams[tagtype].remove(tag)
        await interaction.response.send_message(f'Removed "{tag}" from search parameters') #type: ignore
        bot.setInfo(convertParams(searchParams), updateTime, data['channelIDs'])
    except ValueError:
        await interaction.response.send_message(f'"{tag}" was not in search parameters') #type: ignore

@tree.command(name="listtags", description="Lists the current tags in the search", guild=guild)
async def listTags(interaction: discord.Interaction):
    if searchParams['characters'] == []:
        await interaction.response.send_message('No tags currently selected')
    else:
        await interaction.response.send_message(f'{'\n'.join(searchParams['characters'])}') #type: ignore

@tree.command(name='setinterval', description='Sets the interval between searches', guild=guild)
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

@tree.command(name='start', description='Start the bot searching', guild=guild)
async def start(interaction: discord.Interaction):
    if searchParams['characters'] == []:
        await interaction.response.send_message('No tags currently selected, search cannot be started')
    else:
        bot.bg_task = bot.loop.create_task(bot.search(bot.searchParams))
        await interaction.response.send_message('Started!')

@tree.command(name='stop', description='Stop the bot searching', guild=guild)
async def stop(interaction: discord.Interaction):
    bot.bg_task.cancel()
    await interaction.response.send_message('Stopped!')
    print('Stopped!')

@tree.command(name='load', description='Load works without sending links. Useful for the first time using the bot', guild=guild)
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