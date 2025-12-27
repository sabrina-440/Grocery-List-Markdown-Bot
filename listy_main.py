import discord
from discord import app_commands
from discord.ext import commands
import json
import shlex
from pathlib import Path

'''
/create make a new list

/add add item to already existing list, can specifify list. 
if not specified it will look for other lists in thread/channel. 
if no lists in thread then report error, if multiple ask to specify
can add multiple items seperated by space or use quotes if items have spaces
prints out list after modification is done


/remove -remove item from list. all rules of add apply to remove

/delete specify list name to delete, asks for confirmation before doing so

/view view list specified or thread/channel default existing

/show show all current lists

/ls show all list names and items
'''

cmds_info = '''
NOTE spaces between items, use quotes "two words" to specify multi word items!!

/create make a new list (can add items)

/add add item to already existing list, can specify list or will look into thread/channel

/remove remove item from list, can specify or will look into thread/channel

/delete delete an entire list, specify name of list, must confirm to avoid mistakes

/show show all current lists

/view show items on a list

/ls show all list names and items

/help display avaliable cmds
'''

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────
with open("config.json") as f:
    TOKEN = json.load(f)["token"]

DATA_DIR = Path("lists")
DATA_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────
# Markdown storage helpers
# ─────────────────────────────────────────────────────────────
def channel_file(channel_id: int) -> Path:
    return DATA_DIR / f"channel_{channel_id}.md"

def load_lists(channel_id: int) -> dict[str, list[str]]:
    path = channel_file(channel_id)
    if not path.exists():
        return {}

    lists: dict[str, list[str]] = {}
    current = None

    for line in path.read_text().splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            lists[current] = []
        elif line.startswith("- ") and current:
            lists[current].append(line[2:].strip())

    return lists

def save_lists(channel_id: int, lists: dict[str, list[str]]):
    path = channel_file(channel_id)
    lines = []

    for name, items in lists.items():
        lines.append(f"## {name}")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    path.write_text("\n".join(lines).rstrip() + "\n")

# ─────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────
def resolve_list(channel_id: int, list_name: str | None):
    lists = load_lists(channel_id)

    if list_name:
        if list_name not in lists:
            return None, None, f"❌ List `{list_name}` does not exist."
        return list_name, lists, None

    if not lists:
        return None, None, "❌ No lists exist in this channel."
    if len(lists) > 1:
        return None, None, "⚠️ Multiple lists exist. Please specify one."

    name = next(iter(lists))
    return name, lists, None

def format_list(name: str, items: list[str]) -> str:
    if not items:
        return f"### {name}\n*(empty)*"
    return "### " + name + "\n" + "\n".join(f"- {i}" for i in items)

# ─────────────────────────────────────────────────────────────
# Bot setup
# ─────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


# ─────────────────────────────────────────────────────────────
# /help
# ─────────────────────────────────────────────────────────────
@bot.tree.command(name="help", description="show all possible commands from listy")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(cmds_info, ephemeral=True)

# ─────────────────────────────────────────────────────────────
# /create
# ─────────────────────────────────────────────────────────────
@bot.tree.command(name="create", description="Create a new list")
@app_commands.describe(name="List name", items="Items (use quotes for spaces)")
async def create(interaction: discord.Interaction, name: str, items: str | None = None):
    lists = load_lists(interaction.channel_id)

    if name in lists:
        await interaction.response.send_message("❌ List already exists.", ephemeral=True)
        return

    lists[name] = shlex.split(items) if items else []
    save_lists(interaction.channel_id, lists)

    await interaction.response.send_message(
        f"✅ List created\n{format_list(name, lists[name])}"
    )

# ─────────────────────────────────────────────────────────────
# /add
# ─────────────────────────────────────────────────────────────
@bot.tree.command(name="add", description="Add items to a list")
@app_commands.describe(items="Items to add", list_name="Optional list name")
async def add(interaction: discord.Interaction, items: str, list_name: str | None = None):
    name, lists, error = resolve_list(interaction.channel_id, list_name)
    if error:
        await interaction.response.send_message(error, ephemeral=True)
        return

    lists[name].extend(shlex.split(items))
    save_lists(interaction.channel_id, lists)

    await interaction.response.send_message(
        f"➕ Items added\n{format_list(name, lists[name])}"
    )

# ─────────────────────────────────────────────────────────────
# /remove + /rm
# ─────────────────────────────────────────────────────────────
async def remove_impl(interaction, items, list_name):
    name, lists, error = resolve_list(interaction.channel_id, list_name)
    if error:
        await interaction.response.send_message(error, ephemeral=True)
        return

    for item in shlex.split(items):
        if item in lists[name]:
            lists[name].remove(item)

    save_lists(interaction.channel_id, lists)
    await interaction.response.send_message(
        f"➖ Items removed\n{format_list(name, lists[name])}"
    )

@bot.tree.command(name="remove", description="Remove items from a list")
async def remove(interaction: discord.Interaction, items: str, list_name: str | None = None):
    await remove_impl(interaction, items, list_name)
'''
@bot.tree.command(name="rm", description="Alias for /remove")
async def rm(interaction: discord.Interaction, items: str, list_name: str | None = None):
    await remove_impl(interaction, items, list_name)
'''
# ─────────────────────────────────────────────────────────────
# /delete
# ─────────────────────────────────────────────────────────────
@bot.tree.command(name="delete", description="Delete a list")
async def delete(interaction: discord.Interaction, name: str):
    lists = load_lists(interaction.channel_id)

    if name not in lists:
        await interaction.response.send_message("❌ List does not exist.", ephemeral=True)
        return

    del lists[name]
    save_lists(interaction.channel_id, lists)

    await interaction.response.send_message(f"🗑️ `{name}` deleted.")

# ─────────────────────────────────────────────────────────────
# /view
# ─────────────────────────────────────────────────────────────
@bot.tree.command(name="view", description="View a list")
async def view(interaction: discord.Interaction, list_name: str | None = None):
    name, lists, error = resolve_list(interaction.channel_id, list_name)
    if error:
        await interaction.response.send_message(error, ephemeral=True)
        return

    await interaction.response.send_message(format_list(name, lists[name]))

# ─────────────────────────────────────────────────────────────
# /show
# ─────────────────────────────────────────────────────────────
@bot.tree.command(name="show", description="Show all lists")
async def show(interaction: discord.Interaction):
    lists = load_lists(interaction.channel_id)
    if not lists:
        await interaction.response.send_message("📭 No lists exist.")
        return

    await interaction.response.send_message(
        "📋 **Lists:**\n" + "\n".join(f"- {n}" for n in lists)
    )

# ─────────────────────────────────────────────────────────────
# /ls
# ─────────────────────────────────────────────────────────────

@bot.tree.command(name="ls", description="detailed show all lists and items on list")
async def show(interaction: discord.Interaction):
    lists = load_lists(interaction.channel_id)
    if not lists:
        await interaction.response.send_message("📭 No lists exist.")
        return
    response = ""
    for l in lists:
        response+= format_list(l, lists[l]) +'\n'
    await interaction.response.send_message(response)

# ─────────────────────────────────────────────────────────────
bot.run(TOKEN)
