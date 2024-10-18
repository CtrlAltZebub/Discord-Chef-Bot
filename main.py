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
    await bot.load_extension('cogs.random_recipe') # Gets a random recipe
    await bot.load_extension('cogs.recipe_search') # Searches for a recipe based on given filters
    await bot.load_extension('cogs.ingredient_info') # Searches for information on a specific ingredient
    await bot.load_extension('cogs.meal_plan') # Creates a meal plan for a user based on the recipe_search command

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
