from discord.ext import commands
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
    @commands.command(name='recipe_search')
    async def recipe_search(self, ctx, *, filters=None):
        # Spoonacular complex search URL
        url = "https://api.spoonacular.com/recipes/complexSearch"
        # Dictionary to map input keywords to API query parameters
        param_map = {
            "meal_type": "type",
            "cuisine": "cuisine",
            "ingredient": "includeIngredient",
            "allergies": "intolerances",
            "diet": "diet",
            "time": "maxReadyTime",
            "number": "number",
        }
        if filters:
            # Split input into parts by space and then into key: value pairs
            filter_parts = filters.split()
            for part in filter_parts:
                try:
                    # Split into key and value
                    key, value = part.split(':')
                    if key in param_map:
                        # Use param_map to get the right API parameter
                        header[param_map[key]] = value
                except ValueError:
                    await ctx.send()

        # Build the URL request with all the parameters
        response = requests.get(url, header)

        try:
            response.raise_for_status()
            data = response.json()

            # Build the message to send back
            # This part of the message is only called once
            message = "Here are your search results: \n\n"

            if data['results']:
                recipes = data['results']
                for recipe in recipes:
                    message += (
                        f"**{recipe['title']}**\n"
                        f"{recipe.get('image', 'No image available')}\n"
                        f"{recipe['servings']}, {recipe['preparationMinutes']}, {recipe['cookingMinutes']}\n"
                        f"{recipe['sourceUrl']}"
                    )

                # Send the entire message
                await ctx.send(message)
            else:
                await ctx.send("Sorry, I couldn't find any recipes with those filters.")
        except requests.exceptions.RequestException as e:
            await ctx.send("There was an error fetching recipes. Please try again later.")
            print(f"Error: {e}")


def setup(bot):
    bot.add_cog(RecipeSearch(bot))
