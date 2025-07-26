from discord.ext import tasks, commands

class searchCog(commands.Cog):
    def __init__(self):
        self.search.start()
    def cog_unload(self):
        self.search.cancel()

    @tasks.loop(seconds=60*5)
    def search(self) -> None:
        search = A03.Search(**self.searchParams) #type: ignore
        search.update()
        print(search.total_results)
        decoder = json.decoder.JSONDecoder()
        while True:
            t1 = time.time()
            dataFile = decoder.decode(open('data.json').read())
            totalworks = dataFile['total']
            startingWorks = dataFile['total']
            while totalWorks < search.total_results:
                for result in search.results:
                    if result.id not in dataFile['ids']:
                        self.sendwork(result.id)
                        dataFile['ids'].append(result.id)
                        totalWorks += 1
                print(totalWorks)
                search.page + 1
                search.update()
            dataFile['total'] = totalworks
            with open('data.json', 'w') as file:
                jsonData = json.JSONEncoder().encode(dataFile)
                file.write(jsonData)
            print(f'''Updated Data File in {round(time.time() - t1, 1)} Seconds
                      Increased works from {startingWorks} to {totalWorks}''')