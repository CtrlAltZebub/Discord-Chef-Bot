from discord.ext import commands
import requests
import os

SPOONACULAR_API = os.getenv('SPOONACULAR_API')
header = {
    "Content-Type": "application/json",
    "x-api-key": f"{SPOONACULAR_API}"
}
CHANNEL_ID = os.getenv('CHANNEL_ID')

class RandomRecipe(commands.Cog):
    # Initialise the class
    def __init__(self, bot):
        self.bot = bot

    """
    This command will use the spoonacular api search for a random recipe.
    It will then grab the recipe and send it in a specific channel (#food).
    Error Handling will help deal with any request errors  
    """
    @commands.command(name='recipe')
    async def random_recipe(self, ctx):
        try:
            # URL and header for the random recipe
            url = "https://api.spoonacular.com/recipes/random"
            response = requests.get(url, headers=header)
            response.raise_for_status()
            data = response.json()
            # Get the first item in the response.json data
            recipe = data['recipes'][0]
            # Reply to the command with a formatted message
            # Include recipe name, total time and recipe link
            await ctx.send(
                f"Here's a random recipe: {recipe['title']}\n"
                f"{recipe['image']}\n"
                f"{recipe['servings']}, {recipe['preparationMinutes']}, {recipe['cookingMinutes']}\n"
                f"{recipe['sourceUrl']}")
        except requests.exceptions.RequestException as e:
            await ctx.send()
            print(f"Error: {e}")


def setup(bot):
    bot.add_cog(RandomRecipe(bot))
