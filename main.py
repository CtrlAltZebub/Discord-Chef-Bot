from dotenv import load_dotenv
import os
import discord
from discord.ext import commands

# Load environment variables from the .env file
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SPOONACULAR_API = os.getenv('SPOONACULAR_API')

# Create the bot object
bot = commands.Bot(command_prefix=':', intents=discord.Intents.default())

# Handling invalid commands
@bot.event
async def on_command_error(ctx, error):
    # Check if the error is because of an unknown command
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Oops! I don't recognise that command. Type ':help' for more information.")
    else:
    # Handling any other errors
        await ctx.send("Something went wrong.")

# Help command
@bot.command(name='help')
async def custom_help(ctx):
    help_message = (

    )
    await ctx.send(help_message)

# Bot Commands here
bot.load_extension('cogs.random_recipe') # Gets a random recipe
bot.load_extension('recipe_search') # Searches for a recipe based on given filters
bot.load_extension('ingredient_info') # Searches for information on a specific ingredient

bot.run(os.getenv('DISCORD_TOKEN'))
