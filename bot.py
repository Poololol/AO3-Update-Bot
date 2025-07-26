import AO3
import json
import time
import sendWork
import discord
from discord import TextChannel, VoiceChannel, StageChannel, DMChannel, PartialMessageable, GroupChannel, Thread
from typing import Union
import threading

PartialMessageableChannel = Union[TextChannel, VoiceChannel, StageChannel, Thread, DMChannel, PartialMessageable]
MessageableChannel = Union[PartialMessageableChannel, GroupChannel]

class Bot(discord.Client):
    def setInfo(self, searchParams: dict[str, str | bool | int], updateTime: float, channels: list[MessageableChannel]) -> None:
        '''
        Args:
            searchParams (dict[str, str]): 
            updateTime (float): The time between two different requests in hours
        '''
        self.searchParams = searchParams
        self.updateTime = updateTime
        self.channels = channels

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        await self.search()
    
    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        print('Recieved Message')
        if message.content.startswith('$setChannel'):
            with open('data.json') as file:
                data = json.JSONDecoder().decode(file.read())
            #data['channels'].append(message.channel.)
            self.channels.append(message.channel)
            with open('data.json', 'w') as file:
                file.write(json.JSONEncoder().encode(data))

            await message.channel.send(f'Added channel {message.channel.name} to update list') #type: ignore
        
        if message.content.startswith('$removeChannel'):
            with open('data.json') as file:
                data = json.JSONDecoder().decode(file.read())
            try:
                #data['channels'].remove(message.channel)
                self.channels.remove(message.channel)
                await message.channel.send(f'Removed channel {message.channel.name} from update list') #type: ignore
            except ValueError:
                await message.channel.send(f'Failed to remove channel {message.channel.name} from update list') #type: ignore
            with open('data.json', 'w') as file:
                file.write(json.JSONEncoder().encode(data))

    async def search(self) -> None:
        search = AO3.Search(**self.searchParams) #type: ignore
        search.update()
        print(search.total_results)

        decoder = json.decoder.JSONDecoder()
        while True:
            t1 = time.time()
            dataFile = decoder.decode(open('data.json').read())
            totalWorks = dataFile['total']
            startingWorks = dataFile['total']
            while totalWorks < search.total_results:
                for result in search.results:
                    if result.id not in dataFile['ids']:
                        self.sendWork(result.id)
                        dataFile['ids'].append(result.id)
                        totalWorks += 1
                print(totalWorks)
                search.page += 1
                search.update()
            dataFile['total'] = totalWorks
            with open('data.json', 'w') as file:
                jsonData = json.JSONEncoder().encode(dataFile)
                file.write(jsonData)
            print(f'Updated Data File in {round(time.time() - t1, 1)} Seconds\nIncreased works from {startingWorks} to {totalWorks}')
            time.sleep(self.updateTime * 60 * 60)
    
    def sendWork(self, workID):
        for channel in self.channels:
            message = sendWork.sendWork(workID, channel)