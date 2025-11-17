import AO3
import json
import time
import discord
import asyncio
import inputimeout
from ServerInfo import ServerInfo
from keys import authorID

class Bot(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options) -> None:
        '''Always call `Bot.setInfo()` before `Bot.run()`'''
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)
        self.searchNum = 0
        self.logLevel = 0
        with open('data.json', 'r') as f:
            self.serverInfos = [ServerInfo.fromJSON(si, guildID) for guildID, si in json.JSONDecoder().decode(f.read()).items()]

    def log(self ,message: str, guildID: int | None = None) -> None:
        if self.logLevel > 0:
            if guildID:
                print(f'{time.strftime("%H:%M:%S", time.localtime())} - {guildID} - {message}')
            else:
                print(f'{time.strftime("%H:%M:%S", time.localtime())} - {message}')

    def setInfo(self, searchParams: list[dict[str, str | bool | int]], updateTime: float, channelIDs: list[int], autoStart: bool | None = None, delete: bool | None = None) -> None:
        '''
        Args:
            searchParams (dict[str, str]): Search Parameters.
            updateTime (float): The time between two different requests in hours.
            channelIDs (list[int]): The list of channel IDs to send messages to.
            autoStart (bool | None = None): Whether to automatically restart the bot after a disconnect. If set to None will not change the value.
            delete (bool | None = None): Whether to delete previously sent links. If set to None will not change the value. 
        '''
        #self.searchParams = searchParams
        #self.updateTime = updateTime
        #self.channelIDs = channelIDs
        #self.bg_task: list[asyncio.Task | None] = [None] * len(self.guilds)
        #if delete is not None:
            #self.delete = delete
        if autoStart is not None:
            self.autoStart = autoStart
        #self.nextUpdateTime = 0

    async def on_ready(self):
        self.log(f'Logged in as {self.user} (ID: {self.user.id})') #type: ignore
        await self.tree.sync()
        self.log(f'Ready!')
        if self.autoStart:
            s = 'y'
        else:
            try: 
                s = inputimeout.inputimeout(prompt='Start? (y/n) ', timeout=10)
            except inputimeout.TimeoutOccurred:
                s = 'n'
        if s.lower().strip() == 'y':
            self.startSearches()
            #self.log(f'Started!')
        else:
            self.log(f'Not Started!')

    def startSearches(self, send: bool = True):
        for serverInfo in self.serverInfos:
            if serverInfo.task is None or time.time() > serverInfo.nextUpdateTime:
                serverInfo.task = self.loop.create_task(self.search(serverInfo, send), name=f'Search-{serverInfo.guildID}-{serverInfo.searchNum}')
                serverInfo.searchNum += 1
            #self.log(f'Search Already Started!')

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        #self.log(f'Recieved message: {message.content}')
        if message.author.id == authorID:
            if message.content.startswith('$reload'):
                self.log(f'Reloading')
                #self.tree.copy_global_to(guild=message.guild) #type: ignore
                self.log(await self.tree.sync(guild=message.guild)) #type: ignore
                self.log([com.name for com in self.tree.get_commands()]) #type: ignore
                #self.log(message.guild.id)
                await message.channel.send('Reloaded!')

    async def search(self, serverInfo: ServerInfo, send: bool):
        await self.wait_until_ready()
        
        decoder = json.decoder.JSONDecoder()
        encoder = json.encoder.JSONEncoder()
        
        while not self.is_closed():
            try:
                if serverInfo.delete:
                    for channelID in serverInfo.channelIDs:
                        channel = self.get_channel(channelID)
                        async for message in channel.history(limit=10): #type: ignore
                            if message.author == self.user:
                                await message.delete()
                                self.log(f'Message Deleted!', serverInfo.guildID)
            except:
                pass

            self.log(f'Search Starting!', serverInfo.guildID)
            t1 = time.time()
            dataFile = decoder.decode(open('data.json').read())
            totalWorks = dataFile[serverInfo.guildID]['total']
            startingWorks = dataFile[serverInfo.guildID]['total']

            for searchParam in serverInfo.searchParams:
                search = AO3.Search(**searchParam, sort_column=AO3.search.DATE_POSTED) #type: ignore
                search.update()
                self.log(f'Total Works: {search.total_results}, Pages: {search.pages}', serverInfo.guildID)

                while search.page <= search.pages:
                    newWorks = 0
                    for result in search.results:
                        if result.id not in dataFile['ids'] and (serverInfo.explicit or (result.rating != 'Explicit')):
                            if send:
                                await self.sendWork(serverInfo, result.id)
                                await asyncio.sleep(4)
                            dataFile['ids'].append(result.id)
                            newWorks += 1
                            totalWorks += 1
                    self.log(f'Works Loaded: {totalWorks}, Page: {search.page}', serverInfo.guildID)
                    if send and newWorks == 0:
                        break
                    search.page += 1
                    search.update()

                dataFile['total'] = totalWorks
                with open('data.json', 'w') as file:
                    jsonData = encoder.encode(dataFile)
                    file.write(jsonData)

            self.log(f'''Updated Data File in {round(time.time() - t1, 1)} Seconds
                           Increased works from {startingWorks} to {totalWorks}''', serverInfo.guildID)
            if not send:
                break
            serverInfo.nextUpdateTime = time.time() + serverInfo.updateTime * 60 * 60
            self.log(f'Next search time: {time.strftime('%H:%M:%S', time.localtime(serverInfo.nextUpdateTime))}', serverInfo.guildID)
            await asyncio.sleep(serverInfo.updateTime * 60 * 60)

    async def sendWork(self, serverInfo: ServerInfo, workID: int):
        self.log(f'Sending work: {workID}', serverInfo.guildID)
        if serverInfo.channelIDs == []:
            with open('data.json') as file:
                serverInfo.channelIDs = json.JSONDecoder().decode(file.read())[serverInfo.guildID]['channelIDs']
        if serverInfo.channelIDs == []:
            self.log('Channel List is empty', serverInfo.guildID)
        for channelID in serverInfo.channelIDs:
            channel = self.get_channel(channelID)
            self.log(f'Sending work {workID} to channel "{self.get_channel(channelID).name}"', serverInfo.guildID) #type: ignore
            message = await channel.send(f'https://archiveofourown.org/works/{workID}') #type: ignore
            #self.log(f'Sent to {workID} channel "{self.get_channel(channelID).name}"') #type: ignore