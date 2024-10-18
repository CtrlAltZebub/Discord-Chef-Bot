from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
import asyncio

# Load environment variables from the .env file
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SPOONACULAR_API = os.getenv('SPOONACULAR_API')

# Create the bot object
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        # Sync the slash commands with Discord
        await bot.tree.sync()
        print("Slash commands synced!")
    except Exception as e:
        print(f"Error syncing commands:{e}")

# Bot Commands here
async def load_extensions():
    extensions = [
        'cogs.random_recipe',
        'cogs.recipe_search',
        'cogs.ingredient_info',
        'cogs.meal_plan',
    ]
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"Loaded {ext} successfully")
        except Exception as e:
            print(f"{ext} failed to load: {e}")

# Handling invalid commands
@bot.event
async def on_command_error(ctx, error):
    # Check if the error is because of an unknown command
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Oops! I don't recognise that command. Type '.help' for more information.")
    else:
    # Handling any other errors
        await ctx.send("Something went wrong.")

async def run_bot():
    await load_extensions()
    await bot.start(DISCORD_TOKEN)

asyncio.run(run_bot())
