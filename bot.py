import AO3
import json
import time
import discord
import asyncio
import inputimeout
from keys import authorID

class Bot(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options) -> None:
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)

    def setInfo(self, searchParams: list[dict[str, str | bool | int]], updateTime: float, channelIDs: list[int]) -> None:
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

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})') #type: ignore
        print('------')
        await self.tree.sync()
        print('Ready!')
        try: 
            s = inputimeout.inputimeout(prompt='Start? (y/n) ', timeout=10)
        except inputimeout.TimeoutOccurred:
            s = 'n'
        if s.lower().strip() == 'y':
            self.startSearch()
            print('Started!')
        else:
            print('Not Started!')

    def startSearch(self, send: bool = True, allowExplicit: bool = True):
        self.bg_task = self.loop.create_task(self.search(self.searchParams, send, allowExplicit))

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        #print(f'Recieved message: {message.content}')
        if message.author.id == authorID:
            if message.content.startswith('$reload'):
                print('Reloading')
                #self.tree.copy_global_to(guild=message.guild) #type: ignore
                print(await self.tree.sync(guild=message.guild))
                print([com.name for com in self.tree.get_commands()])
                #print(message.guild.id)
                await message.channel.send('Reloaded!')

    async def search(self, searchParams: list[dict[str, str | bool | int]], send: bool = True, allowExplicit: bool = True):
        await self.wait_until_ready()
        
        decoder = json.decoder.JSONDecoder()
        encoder = json.encoder.JSONEncoder()
        
        while not self.is_closed():
            t1 = time.time()
            dataFile = decoder.decode(open('data.json').read())
            totalWorks = dataFile['total']
            startingWorks = dataFile['total']

            for searchParam in searchParams:
                search = AO3.Search(**searchParam, sort_column=AO3.search.DATE_POSTED) #type: ignore
                search.update()
                print(f'Total Works: {search.total_results}')
                newWorks = []

                while search.page <= search.pages:
                    for result in search.results:
                        if result.id not in dataFile['ids'] and (allowExplicit or (result.rating != 'Explicit')):
                            if send:
                                await self.sendWork(result.id)
                            newWorks.append(result.id)
                            dataFile['ids'].append(result.id)
                            totalWorks += 1
                    print(f'Works Loaded: {totalWorks}')
                    search.page += 1
                    search.update()

                dataFile['total'] = totalWorks
                with open('data.json', 'w') as file:
                    jsonData = encoder.encode(dataFile)
                    file.write(jsonData)
            print(f'''Updated Data File in {round(time.time() - t1, 1)} Seconds
                Increased works from {startingWorks} to {totalWorks}''')
            if not send:
                break
            print(f'Seconds until next search: {self.updateTime * 60 * 60}')
            await asyncio.sleep(self.updateTime * 60 * 60)

    async def sendWork(self, workID: int):
        print(f'Sending work: {workID}')
        if self.channelIDs == []:
            with open('data.json') as file:
                self.channelIDs = json.JSONDecoder().decode(file.read())['channelIDs']
        if self.channelIDs == []:
            print('Channel List is empty')
        for channelID in self.channelIDs:
            channel = self.get_channel(channelID)
            await channel.send(f'https://archiveofourown.org/works/{workID}') #type: ignore
            print(f'Sent to channel "{self.get_channel(channelID).name}"') #type: ignore