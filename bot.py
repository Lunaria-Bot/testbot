import os
import json
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

# ========================
# Data Persistence
# ========================
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "botdata.json")

def ensure_data_dir():
    """Ensure the data folder exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_data():
    """Load bot data from JSON file."""
    ensure_data_dir()
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"cooldowns": {}, "settings": {}}

def save_data(data):
    """Save bot data to JSON file."""
    ensure_data_dir()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ========================
# Discord Bot Setup
# ========================
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# Events
# ========================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"📜 Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# ========================
# Slash Commands
# ========================
@bot.tree.command(name="settings", description="Update your DM preferences")
@app_commands.describe(dm_enabled="Enable or disable DM notifications (true/false)")
async def settings(interaction: discord.Interaction, dm_enabled: bool):
    """Allow a user to toggle DM notifications on/off."""
    user_id = str(interaction.user.id)
    if "settings" not in data:
        data["settings"] = {}

    data["settings"][user_id] = {"dm_enabled": dm_enabled}
    save_data(data)

    await interaction.response.send_message(
        f"✅ DM notifications {'enabled' if dm_enabled else 'disabled'}",
        ephemeral=True
    )

@bot.tree.command(name="reload", description="Reloads the bot's commands (Admin only)")
async def reload(interaction: discord.Interaction):
    """Allow admins to reload commands without restarting the bot."""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.",
            ephemeral=True
        )
        return

    try:
        synced = await bot.tree.sync()
        await interaction.response.send_message(
            f"✅ Commands reloaded successfully ({len(synced)} synced).",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Reload failed: {e}",
            ephemeral=True
        )

# ========================
# Start Bot
# ========================
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN environment variable not set!")

    bot.run(token)
