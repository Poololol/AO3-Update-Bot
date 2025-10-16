# Instructions
## Installation
1. Clone the repository
2. Copy dataTemplate.json and rename it to data.json
3. Create a file named keys.py
4. In keys.py type `token = 'YOUR_BOT_TOKEN'` and `authorID = 'YOUR_DISCORD_ID'`
## Usage
1. Run main.py
2. Set the channel the bot will send links to using `/addchannel`
3. Set the tags to search for using `/addtag`
4. To load all current matching works
    * Without sending links use `/load` then `/start` once finished loading
    * With sending links use `/start`
5. To stop the bot use `/stop`
## Search
1. Search tags are split into search groups
2. Tags inside a search group are AND
3. Different search groups are OR
4. Examples:
   * To get the search (Character A AND Character B) OR Character A/Character B you would need 2 search groups, the first with 2 tags: Character A and Character B, the second group with only Character A/Character B
   * To get the search Character A AND (Character B OR Character C) you would need 2 search groups, the first with 2 tags: Character A and Character B, the second also with 2 tags: Character A and Character C
5. Search group indices start at 1

# Discord Command Documentation
## `/addchannel [channel]`
Adds a channel to the list of channels to send links to. If no parameter is specified adds the channel the command was sent in, otherwise adds the specified channel.
## `/addgroup`
Adds an empty search group.
## `/addtag tagtype tag [searchgroup]`
Adds the specified tag to the search. Tagtype is the type of tag to add, options are: characters, fandoms, tags, relationships, and excluded tags. Tag is the tag to add. Searchgroup is the search group number to add the tag to, defaults to 1.
## `/deletegroup searchgroup`
Deletes the specified searchgroup and all the tags it contains.
## `/listchannels`
Lists the names of all of the channels in the list of channels to send links to.
## `/listnumworks [searchgroup]`
Lists the number of works that exist in the specified search group. The searchgroup parameter determines which search groups are looked at, options are: -1, 0, 1 ... n where n is the nnumber of search groups present. Specifying -1 searches through all groups and lists the total number of works loaded at the moment, 0 lists the total number of works loaded, and any other value lists the number of works for the corresponding group, defaults to -1. Will not give an accurate estimate for the total number of matching works. This commad makes api requests and therefore may take a while depending on the number of search groups.
## `/listtags`
Lists all of the tags in the current search parameters.
## `/load`
Loads all matching works into the bot's memory without sending any links, useful for setting up the bot. This commad makes api requests and therefore may take a while depending on the number of matching works.
## `/removechannel [channel]`
Removes a channel from the list of channels to send links to. If no parameter is specified removes the channel the command was sent in, otherwise removes the specified channel.
## `/removetag tagtype tag [searchgroup]`
Removes the specified tag from the search. Tagtype is the type of tag to remove, options are: characters, fandoms, tags, relationships, and excluded tags. Tag is the tag to remove and must be an existing tag. Searchgroup is the search group number to remove the tag from, defaults to 1.
## `/setinterval interval`
Set the interval for the search, in hours. The default is 1 hour.
## `/start`
Starts the bot, will start the bot searching and sending links repeating at the specified interval.
## `/stop`
Stops the bot, stops the bot from searching and sending links.
## `/toggleexplicit`
Toggles the sending of works marked as explicit. Default is to allow sending explicit.

# Command Line Arguments
## `-l, --loglevel LEVEL`
Specifies the level of logging, 0 is no logging, 1 is my log messages, 2 is all logging. Defaults to 1
## `-a, --autostart`
If specified automatically restart the bot after a disconnection, otherwise don't.
## `-m, --deleteafter DELETEAFTER`
Specifies the time in seconds in which to delete responses to commands after. If not specified defaults to never delete responses.
## `-d, --linkdelete`
If specified delete sent links right before the next search, otherwise keep sent links.