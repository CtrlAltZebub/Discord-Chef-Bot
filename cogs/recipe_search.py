from discord.ext import commands
from discord import app_commands
import discord
import requests
import os

SPOONACULAR_API = os.getenv('SPOONACULAR_API')
header = {
    "Content-Type": "application/json",
    "x-api-key": f"{SPOONACULAR_API}"
}
CHANNEL_ID = os.getenv('CHANNEL_ID')

class RecipeSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    This command allows the user to search for recipes with multiple filters.
    The user can input:
    - meal type (e.g. breakfast, lunch, dinner)
    - cuisine (e.g. Italian, Mexican)
    - ingredients (e.g. pasta, eggs)
    - allergies (e.g. nuts, lactose)
    - diet (e.g. vegetarian, vegan)
    - time (how long it takes to cook the meal)
    - number of recipes between 1-100 (e.g. 7)
    Example usage: !recipe_search meal_type=breakfast cuisine=Italian ingredients=eggs,pasta
    """
    # Slash commands for recipe search with custom filters.
    @app_commands.command(name='recipe', description="Search for a recipe with custom filters")
    @app_commands.describe(
        meal="Type of meal (Eg main course, breakfast etc. For a full list please view the '.help' command)",
        cuisine="Type of cuisine (Eg Italian, Asian)",
        diet="Type of diet (Eg Vegetarian, Gluten Free, Paleo)",
        allergies="Any allergies you have",
        ingredients="Are there any particular ingredients you want to use?",
        number="How many meals do you want to find?"
    )
    async def recipe_search(
            self,
            interaction: discord.Interaction,
            meal: str = None,
            cuisine: str = None,
            diet: str = None,
            allergies: str = None,
            ingredients: str = None,
            number: int = 1
    ):
            # Get the recipe IDs
            recipe_ids, error = self.get_recipe_id(meal, cuisine, diet, allergies, ingredients, number)
            if error:
                await interaction.response.send_message(f"Error: {error}")
                return # Stop execution if there was an error

            # Build the message to send back
            message = "Here are your search results: \n\n"

            # Check if recipe_ids is empty
            if not recipe_ids:
                await interaction.response.send_message("No recipes found with these filters")
                return

            await interaction.response.send_message(message)
            # Get the recipe info using the IDs
            for recipe_id in recipe_ids:
                recipe_info, error = self.get_recipe_info(recipe_id)
                if error:
                    await interaction.followup.send(f"Error: {error}")
                    return
                message = self.format_message(recipe_info)
                # Send the formatted recipe message
                await interaction.followup.send(message)

    @staticmethod
    def get_recipe_id(
            meal: str = None,
            cuisine: str = None,
            diet: str = None,
            allergies: str = None,
            ingredients: str = None,
            number: int = 1
    ):
        # Make an API call to get the recipe id
        try:
            url = "https://api.spoonacular.com/recipes/complexSearch"
            query_params = {
                "type": meal or "main course",  # Default to main course / dinner recipes
                "cuisine": cuisine,
                "diet": diet,
                "intolerances": allergies,
                "includeIngredients": ingredients,
                "number": min(number, 100)  # Default to 1 result
            }
            recipe_ids = []

            # Build the URL request with all the parameters
            id_response = requests.get(url, headers=header, params=query_params)
            id_response.raise_for_status()  # Raise an exception for HTTP errors
            data = id_response.json()

            # Check if results exist
            if not data['results']:
                return None, f"Couldn't find any recipes matching this search."

            # Put the recipe ID's into a list and return it
            for recipe in data['results']:
                recipe_ids.append(recipe['id'])
            return recipe_ids, None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching recipe ID: {e}")
            return None, "There was an issue retrieving the recipe ID."

    @staticmethod
    def get_recipe_info(recipe_id):
        # Make the API call to get the recipe info:
        try:
            info_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
            info_response = requests.get(info_url, headers=header)
            info_response.raise_for_status() # Raise an exception for HTTP errors
            recipe_info = info_response.json()
            return recipe_info, None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching ingredient info {e}")
            return None, "There was an issue retrieving the recipe info."

    @staticmethod
    def format_message(recipe_info):
        # Build the message with the recipe's information
        message = (
            f"**{recipe_info['title']}**\n"
            f"{recipe_info.get('image', 'No image available')}\n"
            f"Serves: {recipe_info.get('servings', 'N/A')}, "
            f"Cook time: {recipe_info.get('readyInMinutes', 'N/A')} mins,\n"
            f"{recipe_info.get('sourceUrl', 'No link available')}\n\n"
        )

        return message


async def setup(bot):
    await bot.add_cog(RecipeSearch(bot))
