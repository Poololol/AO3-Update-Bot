import AO3
import json
import time
import discord
import asyncio
import inputimeout
from keys import authorID

class Bot(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options) -> None:
        '''Always call `Bot.setInfo()` before `Bot.run()`'''
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)

    def setInfo(self, searchParams: list[dict[str, str | bool | int]], updateTime: float, channelIDs: list[int], autoStart: bool | None = False, delete: bool | None = False) -> None:
        '''
        Args:
            searchParams (dict[str, str]): 
            updateTime (float): The time between two different requests in hours
            channelIDs (list[int]): The list of channel IDs to send messages to
        '''
        self.searchParams = searchParams
        self.updateTime = updateTime
        self.channelIDs = channelIDs
        self.bg_task: asyncio.Task | None = None
        if delete is not None:
            self.delete = delete
        if autoStart is not None:
            self.autoStart = autoStart

    async def on_ready(self):
        print(f'{time.strftime("%H:%M:%S", time.localtime())} - Logged in as {self.user} (ID: {self.user.id})') #type: ignore
        await self.tree.sync()
        print(f'{time.strftime("%H:%M:%S", time.localtime())} - Ready!')
        if self.autoStart:
            s = 'y'
        else:
            try: 
                s = inputimeout.inputimeout(prompt='Start? (y/n) ', timeout=10)
            except inputimeout.TimeoutOccurred:
                s = 'n'
        if s.lower().strip() == 'y':
            with open('data.json') as file:
                data = json.JSONDecoder().decode(file.read())
            if self.startSearch(allowExplicit=data['allowExplicit']) == True:
                print(f'{time.strftime("%H:%M:%S", time.localtime())} - Started!')
        else:
            print(f'{time.strftime("%H:%M:%S", time.localtime())} - Not Started!')

    def startSearch(self, send: bool = True, allowExplicit: bool = True, deleteAfter: int | None = None):
        if self.bg_task is None:
            self.bg_task = self.loop.create_task(self.search(self.searchParams, send, allowExplicit))
            return True
        else:
            print(f'{time.strftime("%H:%M:%S", time.localtime())} - Search Already Started!')
            return False

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        #print(f'Recieved message: {message.content}')
        if message.author.id == authorID:
            if message.content.startswith('$reload'):
                print(f'{time.strftime("%H:%M:%S", time.localtime())} - Reloading')
                #self.tree.copy_global_to(guild=message.guild) #type: ignore
                print(await self.tree.sync(guild=message.guild))
                print([com.name for com in self.tree.get_commands()])
                #print(message.guild.id)
                await message.channel.send('Reloaded!')

    async def search(self, searchParams: list[dict[str, str | bool | int]], send: bool = True, allowExplicit: bool = True, deleteAfter: int | None = None):
        await self.wait_until_ready()
        
        decoder = json.decoder.JSONDecoder()
        encoder = json.encoder.JSONEncoder()
        
        while not self.is_closed():
            if self.delete:
                for channelID in self.channelIDs:
                    channel = self.get_channel(channelID)
                    async for message in channel.history(limit=10): #type: ignore
                        if message.author == self.user:
                            await message.delete()
                            print(f'{time.strftime("%H:%M:%S", time.localtime())} - Message Deleted!')

            print(f'{time.strftime("%H:%M:%S", time.localtime())} - Search Starting!')
            t1 = time.time()
            dataFile = decoder.decode(open('data.json').read())
            totalWorks = dataFile['total']
            startingWorks = dataFile['total']

            for searchParam in searchParams:
                search = AO3.Search(**searchParam, sort_column=AO3.search.DATE_POSTED) #type: ignore
                search.update()
                print(f'Total Works: {search.total_results}, Pages: {search.pages}')

                while search.page <= search.pages:
                    newWorks = 0
                    for result in search.results:
                        if result.id not in dataFile['ids'] and (allowExplicit or (result.rating != 'Explicit')):
                            if send:
                                await self.sendWork(result.id, deleteAfter)
                            dataFile['ids'].append(result.id)
                            newWorks += 1
                            totalWorks += 1
                    print(f'Works Loaded: {totalWorks}, Page: {search.page}')
                    if send and newWorks == 0:
                        break
                    search.page += 1
                    search.update()

                dataFile['total'] = totalWorks
                with open('data.json', 'w') as file:
                    jsonData = encoder.encode(dataFile)
                    file.write(jsonData)
            print(f'''{time.strftime("%H:%M:%S", time.localtime())} - Updated Data File in {round(time.time() - t1, 1)} Seconds
                Increased works from {startingWorks} to {totalWorks}''')
            if not send:
                break
            print(f'{time.strftime("%H:%M:%S", time.localtime())} - Seconds until next search: {self.updateTime * 60 * 60}')
            await asyncio.sleep(self.updateTime * 60 * 60)

    async def sendWork(self, workID: int, deleteAfter: int | None):
        print(f'{time.strftime("%H:%M:%S", time.localtime())} - Sending work: {workID}')
        if self.channelIDs == []:
            with open('data.json') as file:
                self.channelIDs = json.JSONDecoder().decode(file.read())['channelIDs']
        if self.channelIDs == []:
            print('Channel List is empty')
        for channelID in self.channelIDs:
            channel = self.get_channel(channelID)
            print(channel)
            print(f'{time.strftime("%H:%M:%S", time.localtime())} - Sending to channel "{self.get_channel(channelID).name}"') #type: ignore
            message = await channel.send(f'https://archiveofourown.org/works/{workID}', delete_after=deleteAfter) #type: ignore
            print(f'{time.strftime("%H:%M:%S", time.localtime())} - Sent to channel "{self.get_channel(channelID).name}"') #type: ignore