import AO3
import json
import time
import sendWork
import discord
import search

class Bot(discord.Client):
    def setInfo(self, searchParams: dict[str, str | bool | int], updateTime: float, channelIDs: list[int]) -> None:
        '''
        Args:
            searchParams (dict[str, str]): 
            updateTime (float): The time between two different requests in hours
            channelIDs (list[int]): The list of channel IDs to send messages to
        '''
        self.searchParams = searchParams
        self.updateTime = updateTime
        self.channelIDs = channelIDs

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        #threading.Thread(target=self.search).start()
        search.searchCog()
    
    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        print('Recieved Message')
        if message.content.startswith('$setChannel'):
            with open('data.json') as file:
                data = json.JSONDecoder().decode(file.read())
            data['channelIDs'].append(message.channel.id)
            with open('data.json', 'w') as file:
                file.write(json.JSONEncoder().encode(data))

            await message.channel.send(f'Added channel {message.channel.name} to update list') #type: ignore
        
        if message.content.startswith('$removeChannel'):
            with open('data.json') as file:
                data = json.JSONDecoder().decode(file.read())
            try:
                data['channelIDs'].remove(message.channel.id)
                await message.channel.send(f'Removed channel {message.channel.name} from update list') #type: ignore
            except ValueError:
                await message.channel.send(f'Failed to remove channel {message.channel.name} from update list') #type: ignore
            with open('data.json', 'w') as file:
                file.write(json.JSONEncoder().encode(data))
    
    def sendWork(self, workID):
        for channelID in self.channelIDs:
            channel = self.get_channel(channelID)
            message = await channel.send(f'https://archiveofourown.org/works/{workID}')