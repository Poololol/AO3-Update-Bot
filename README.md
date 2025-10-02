# Instructions
## Installation
1. Clone the repository
2. Copy dataTemplate.json and rename it to data.json
3. Create a file named keys.py
4. In keys.py type `token = 'YOUR_BOT_TOKEN'` and `authorID = 'YOUR_DISCORD_ID'`
## Usage
1. Invite the bot to your server
2. Type `$reload`
3. Set the channel the bot will send links to using `/addchannel`
4. Set the tags to search for using `/addtag`
5. To load all current matching works
    * Without sending links use `/load` then `/start` once finished loading
    * With sending links use `/start`
6. To stop the bot use `/stop`
## Search
1. Search tags are split into search groups
2. Tags inside a search group are AND
3. Different search groups are OR
4. Examples:
   * To get the search (Character A AND Character B) OR Character A/Character B you would need 2 search groups, the first with 2 tags: Character A and Character B, the second group with only Character A/Character B
   * To get the search Character A AND (Character B OR Character C) you would need 2 search groups, the first with 2 tags: Character A and Character B, the second also with 2 tags: Character A and Character C
