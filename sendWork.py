import discord



async def sendWork(workID: int, channel: discord.TextChannel) -> discord.Message:
    message = await channel.send(f'https://archiveofourown.org/works/{workID}')
    return message