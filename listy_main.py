'''
/create make a new list

/add add item to already existing list, can specifify list. 
if not specified it will look for other lists in thread/channel. 
if no lists in thread then report error, if multiple ask to specify
can add multiple items seperated by space or use quotes if items have spaces
prints out list after modification is done


/remove (or /rm for short) -remove item from list. all rules of add apply to remove

/delete specify list name to delete, asks for confirmation before doing so

/view view list specified or thread/channel default existing

/show (or /ls) show all current lists
'''


import discord
import json
import asyncio
import re

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

TOKEN = config['token']

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        self.lists = []
        self.content = {}

    async def on_ready(self):
        print(f'Logged on as {self.user}')
    
    async def on_message(self, message):
         if message.content.startswith('/create'):
            try:
                response = re.match(r'')
            
            return   



intents = discord.Intents.default()
intents.presences = True
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

activity = discord.Game(name="~keeper of the lists~")
client = MyClient(intents=intents, activity=activity)

client.run(TOKEN)

