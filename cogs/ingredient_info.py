from discord.ext import commands
import requests
import os

SPOONACULAR_API = os.getenv('SPOONACULAR_API')
header = {
    "Content-Type": "application/json",
    "x-api-key": f"{SPOONACULAR_API}"
}
CHANNEL_ID = os.getenv('CHANNEL_ID')

class IngredientInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    This command takes a user input,
    then makes an API call to the spoonacular db for information on a particular ingredient.
    Error handling will let the user know if they made a mistake in their search
    and if there was a problem during the request.
    
    This command will need to make 2 API calls, first to get the ingredient id,
    and then to get the relevant information to give to the user.
    """
    @commands.command(name='ingredient')
    async def ingredient_info(self, ctx, *, ingredient_name=None):
        # Check for a user error
        if not ingredient_name:
            await ctx.send("Please provide the name of an ingredient to search for.")
            return

        # Get the ingredient ID
        ingredient_id, error = self.get_ingredient_id(ingredient_name)
        if error:
            await ctx.send(f"Error: {error}")

        # Get the ingredient info using the ID
        ingredient_info, error = self.get_ingredient_info(ingredient_id)
        if error:
            await ctx.send(f"Error: {error}")

        # Format and send the response
        message = self.format_message(ingredient_info)
        await ctx.send(message)


    @staticmethod
    def get_ingredient_id(ingredient_name):
        # Make an API call to get the ingredient id
        try:
            id_url = "https://api.spoonacular.com/food/ingredients/search"
            id_params = {
                "query": ingredient_name,
                "addChildren": False,
                "metaInformation": True,
            }
            id_response = requests.get(id_url, headers=header, params=id_params)
            id_response.raise_for_status() # Raise an exception for HTTP errors
            data = id_response.json()
            # Check if results exist
            if not data['results']:
                return None, f"Couldn't find any ingredients matching '{ingredient_name}'"

            # Return the ingredient ID
            ingredient_id = data['results'][0]['id']
            return ingredient_id, None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching ingredient ID: {e}")
            return None, "There was an issue retrieving the ingredient ID."


    @staticmethod
    def get_ingredient_info(ingredient_id):
        # Make the API call to get the ingredient info
        try:
            info_url = f"https://api.spoonacular.com/food/ingredients/{ingredient_id}/information"
            info_params = {
                "amount": 1
            }
            info_response = requests.get(info_url, headers=header, params=info_params)
            info_response.raise_for_status() # Raise an exception for HTTP errors
            ingredient_info = info_response.json()
            return ingredient_info, None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching ingredient info: {e}")
            return None, "There was an issue retrieving the ingredient info."


    @staticmethod
    def format_message(ingredient_info):
        # Build the message with the ingredient's information
        message = (
            f"**Ingredient:** {ingredient_info['amount']} {ingredient_info['name']}\n"
        )
        for nutrient in ingredient_info['nutrition']['nutrients']:
            message += (
                f"{nutrient['name']}: {nutrient['amount']}{nutrient['unit']}"
            )

        return message


def setup(bot):
    bot.add_cog(IngredientInfo(bot))
