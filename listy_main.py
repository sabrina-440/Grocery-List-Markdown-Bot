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
#TODO: change name from list to shopping-list

import discord
from discord import app_commands
from discord.ext import commands
import json
import asyncio
import re

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

TOKEN = config['token']

#TODO: use markdown (.md) files for storage instead for Obsidian integration
lists = []
content = {}

intents = discord.Intents.default()
intents.presences = True
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
activity = discord.Game(name="~keeper of the lists~")
client = commands.Bot(command_prefix='/', intents=intents)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}')
    try:
        # Sync the command tree
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# Define a slash command with input fields
@client.tree.command(name="create", description="create a new list")
@app_commands.describe(list_name="The name of the list to add", items="comma seperated items to add to current list")
async def greet(interaction: discord.Interaction, list_name: str, items: str):
    await interaction.response.send_message(f"List Created, {list_name}: '\n{items}'") 
    #TODO: make items list like - item1\n - item2\n etc...)




client.run(TOKEN)

