import discord
from discord import app_commands
from discord.ext import commands
import json
import shlex

# ─────────────────────────────────────────────────────────────
# Load configuration
# ─────────────────────────────────────────────────────────────
with open("config.json") as f:
    TOKEN = json.load(f)["token"]

# ─────────────────────────────────────────────────────────────
# In-memory storage
# channel_id -> { list_name -> [items] }
# ─────────────────────────────────────────────────────────────
lists: dict[int, dict[str, list[str]]] = {}

# ─────────────────────────────────────────────────────────────
# Bot setup
# ─────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def get_channel_lists(channel_id: int) -> dict[str, list[str]]:
    return lists.setdefault(channel_id, {})

def resolve_list(channel_id: int, list_name: str | None):
    channel_lists = get_channel_lists(channel_id)

    if list_name:
        if list_name not in channel_lists:
            return None, f"❌ List `{list_name}` does not exist."
        return list_name, None

    if len(channel_lists) == 0:
        return None, "❌ No lists exist in this channel."
    if len(channel_lists) > 1:
        return None, "⚠️ Multiple lists exist. Please specify one."

    return next(iter(channel_lists)), None

def format_list(name: str, items: list[str]) -> str:
    if not items:
        return f"### {name}\n*(empty)*"
    body = "\n".join(f"- {item}" for item in items)
    return f"### {name}\n{body}"

# ─────────────────────────────────────────────────────────────
# Events
# ─────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# ─────────────────────────────────────────────────────────────
# /create
# ─────────────────────────────────────────────────────────────
@bot.tree.command(name="create", description="Create a new list")
@app_commands.describe(name="List name", items="Items (use quotes for spaces)")
async def create(interaction: discord.Interaction, name: str, items: str | None = None):
    channel_lists = get_channel_lists(interaction.channel_id)

    if name in channel_lists:
        await interaction.response.send_message("❌ List already exists.", ephemeral=True)
        return

    parsed_items = shlex.split(items) if items else []
    channel_lists[name] = parsed_items

    await interaction.response.send_message(
        f"✅ List created\n{format_list(name, parsed_items)}"
    )

# ─────────────────────────────────────────────────────────────
# /add
# ─────────────────────────────────────────────────────────────
@bot.tree.command(name="add", description="Add items to a list")
@app_commands.describe(items="Items to add", list_name="Optional list name")
async def add(interaction: discord.Interaction, items: str, list_name: str | None = None):
    channel_id = interaction.channel_id
    resolved, error = resolve_list(channel_id, list_name)
    if error:
        await interaction.response.send_message(error, ephemeral=True)
        return

    parsed_items = shlex.split(items)
    lists[channel_id][resolved].extend(parsed_items)

    await interaction.response.send_message(
        f"➕ Items added\n{format_list(resolved, lists[channel_id][resolved])}"
    )

# ─────────────────────────────────────────────────────────────
# /remove and /rm
# ─────────────────────────────────────────────────────────────
async def remove_impl(interaction: discord.Interaction, items: str, list_name: str | None):
    channel_id = interaction.channel_id
    resolved, error = resolve_list(channel_id, list_name)
    if error:
        await interaction.response.send_message(error, ephemeral=True)
        return

    parsed_items = shlex.split(items)
    current = lists[channel_id][resolved]

    for item in parsed_items:
        if item in current:
            current.remove(item)

    await interaction.response.send_message(
        f"➖ Items removed\n{format_list(resolved, current)}"
    )


@bot.tree.command(name="remove", description="Remove items from a list")
@app_commands.describe(items="Items to remove", list_name="Optional list name")
async def remove(interaction: discord.Interaction, items: str, list_name: str | None = None):
    await remove_impl(interaction, items, list_name)

@bot.tree.command(name="rm", description="Alias for /remove")
@app_commands.describe(items="Items to remove", list_name="Optional list name")
async def rm(interaction: discord.Interaction, items: str, list_name: str | None = None):
    await remove_impl(interaction, items, list_name)



# ─────────────────────────────────────────────────────────────
# /delete
# ─────────────────────────────────────────────────────────────
@bot.tree.command(name="delete", description="Delete a list")
@app_commands.describe(name="List name")
async def delete(interaction: discord.Interaction, name: str):
    channel_lists = get_channel_lists(interaction.channel_id)

    if name not in channel_lists:
        await interaction.response.send_message("❌ List does not exist.", ephemeral=True)
        return

    await interaction.response.send_message(
        f"⚠️ Type `confirm` to delete `{name}`",
        ephemeral=True
    )

    def check(msg):
        return (
            msg.author == interaction.user
            and msg.channel == interaction.channel
            and msg.content.lower() == "confirm"
        )

    try:
        await bot.wait_for("message", timeout=20, check=check)
    except:
        await interaction.followup.send("❌ Delete cancelled.", ephemeral=True)
        return

    del channel_lists[name]
    await interaction.followup.send(f"🗑️ `{name}` deleted.")

# ─────────────────────────────────────────────────────────────
# /view
# ─────────────────────────────────────────────────────────────
@bot.tree.command(name="view", description="View a list")
@app_commands.describe(list_name="Optional list name")
async def view(interaction: discord.Interaction, list_name: str | None = None):
    channel_id = interaction.channel_id
    resolved, error = resolve_list(channel_id, list_name)
    if error:
        await interaction.response.send_message(error, ephemeral=True)
        return

    await interaction.response.send_message(
        format_list(resolved, lists[channel_id][resolved])
    )

# ─────────────────────────────────────────────────────────────
# /show and /ls
# ─────────────────────────────────────────────────────────────
@bot.tree.command(name="show", description="Show all lists")
async def show(interaction: discord.Interaction):
    channel_lists = get_channel_lists(interaction.channel_id)
    if not channel_lists:
        await interaction.response.send_message("📭 No lists exist.")
        return

    names = "\n".join(f"- {name}" for name in channel_lists)
    await interaction.response.send_message(f"📋 **Lists:**\n{names}")
'''
bot.tree.add_command(app_commands.Command(
    name="ls",
    description="Alias for /show",
    callback=show
))
'''
# ─────────────────────────────────────────────────────────────
bot.run(TOKEN)
