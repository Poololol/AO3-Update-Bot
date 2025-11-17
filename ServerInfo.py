import asyncio

class ServerInfo:
    def __init__(self, searchParams: list[dict[str, str | bool | int]], updateTime: float, channelIDs: list[int], allowExplicit: bool, guildID: int, delete: bool | None = None) -> None:
        self.searchParams = searchParams
        self.updateTime = updateTime
        self.nextUpdateTime = 0.
        self.channelIDs = channelIDs
        self.explicit = allowExplicit
        self.task: asyncio.Task | None = None
        self.searchNum = 0
        self.guildID = guildID
        if delete is not None:
            self.delete = delete

    @staticmethod
    def fromJSON(json: dict, guildID: int) -> 'ServerInfo':
        return ServerInfo(json['searchParams'], json['interval'], json['channelIDs'], json['allowExplicit'], guildID, delete=json['deleteLinks'])