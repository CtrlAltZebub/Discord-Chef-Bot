from discord.ext import commands
import requests
import os

SPOONACULAR_API = os.getenv('SPOONACULAR_API')
header = {
    "Content-Type": "application/json",
    "x-api-key": f"{SPOONACULAR_API}"
}
CHANNEL_ID = os.getenv('CHANNEL_ID')

class MealPlan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='meal plan')
    async def mealplan(self, ctx, *, filters=None):
        # Spoonacular meal plan API
        mealplan_url = "https://api.spoonacular.com/mealplanner/generate"

        # Dictionary to map input keywords to API query parameters
        param_map = {
            "time": "timeFrame",
            "diet": "diet",
            "allergies": "exclude",
        }

        # Initialise the query parameters
        query_params = {
            "time": "week", # Default to a weekly meal plan
        }

        if filters:
            # Split input into parts by space and then into key: value pairs
            filter_parts = filters.split()
            for part in filter_parts:
                try:
                    # Split into key and value
                    key, value = part.split('=')
                    if key in param_map:
                        # Use param_map to get the right API parameter
                        query_params[param_map[key]] = value
                except ValueError:
                    await ctx.send(f"Invalid filter format for {part}. Please use the format key=value.")

        # Build the URL request with all the parameters
        response = requests.get(mealplan_url, headers=header, params=query_params)
        response.raise_for_status()
        data = response.json()
        await ctx.send(data)
        # try:
        #     response.raise_for_status() # # Raise an exception for HTTP errors
        #     data = response.json()
        #
        #     # Build the message to send back
        #     # This part of the message is only called once
        #     message = "Here is your meal plan: \n\n"
        #     days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        #     if data['results']:
        #         plan = data['results']
        #         for day in days:
        #             message += (
        #                 f"{day}\n\n"
        #             )
        #             for meal in plan:
        #                 message += (
        #                     f"**{meal['title']}**\n"
        #                     f"{meal.get('image', 'No image available')}\n"
        #                     f"Serves: {meal['servings']}, "
        #                     f"Time: {meal['readyInMinutes']}mins\n"
        #                     f"{meal['sourceUrl']}"
        #             )
        #         # Send the entire message
        #         await ctx.send(message)
        #     else:
        #         await ctx.send("Sorry, I couldn't find any recipes with those filters.")
        # except requests.exceptions.RequestException as e:
        #     await ctx.send("There was an error making your meal plan. Please try again later.")
        #     print(f"Error: {e}")


def setup(bot):
    bot.add_cog(MealPlan(bot))
