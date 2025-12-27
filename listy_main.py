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

TOKEN = "YMTQ1Mzg0NTQzMDA0NjU2MDQyOQ.GAcA9W.vco7OklQuPhVzIWTezj5YUB6rpYDImRhQHpLcc"
#config['token']

#TODO: use markdown (.md) files for storage instead for Obsidian integration
lists = []
content = {}

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
activity = discord.Game(name="~keeper of the lists~")
client = commands.Bot(command_prefix='/', intents=intents)

async def on_ready(self):
    print(f'Logged on as {self.user}')
    try:
        # Sync the command tree
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# Define a slash command with input fields
@client.tree.command(name="greet", description="Greets a user with a custom message")
@app_commands.describe(user_name="The name of the user to greet", message="A custom message to include")
async def greet(interaction: discord.Interaction, user_name: str, message: str):
    await interaction.response.send_message(f"Hello, {user_name}! Bot says: '{message}'")




client.run(TOKEN)

