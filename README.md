# Instructions
You will need to [register](https://discord.com/developers/applications) your own bot for this
## Code
1. Copy dataTemplate.json and rename it to data.json
2. Create a file named keys.py
3. In keys.py type `token = 'YOUR_BOT_TOKEN'` and `authorID = 'YOUR_DISCORD_ID'`
## Usage
1. Invite the bot to your server
2. Type `$reload`
3. Set the channel the bot will send links to using `/addchannel`
4. Set the tags to search for using `/addtag`
5. To load all current matching works
    * Without sending links use `/load` then `/start` once finished loading
    * With sending links use `/start`
6. To stop the bot use `/stop`
