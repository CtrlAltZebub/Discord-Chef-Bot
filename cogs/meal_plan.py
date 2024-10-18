from discord.ext import commands
from discord import app_commands
import discord
from recipe_search import RecipeSearch
import random
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
        self.recipe = RecipeSearch

    """
    Due to how the spoonacular API is set up, this command will simulate the same effect
    as the meal plan API by making a recipe_search call for each desired meal.
    For example, a user might want to make a weekly meal plan. By default this command will
    make 21 (7 * 3) API calls based on the users input, a meal for breakfast, lunch and dinner
    for each day of the week. If the user only wants to create a meal plan for breakfast and dinner,
    or only for dinner, then 14 (7 * 2) or 7 (7 * 1) will be called.
    
    This command can be scaled by asking how many days/weeks the user wants the meal plan for. 
    """
    # Slash commands for recipe search with custom filters.
    @app_commands.command(name='plan', description="Create a meal plan")
    @app_commands.describe(
        weeks = "How many weeks do you want to make a meal plan for?",
        days = "How many days do you want to make a meal plan for?",
        meals = "Which meals do you want to create a plan for?",
        diet = "Type of diet you're creating a plan for",
        allergies = "Any allergies or intolerances you have"
    )
    async def meal_plan(
            self,
            interaction: discord.Interaction,
            weeks: int = 1, # Default to 1 week
            days: int = 0, # Default to 0 days
            meals: str = "breakfast, lunch, dinner", # Default to 3 meals per day
            diet: str = None, # Default to no specific diet
            allergies: str = None # Default to no allergies or intolerances
    ):
        # Get time frame from user. Convert weeks into days
        # Allow for varying amounts of time by adding the Days (default 0) to weeks
        plan_length = days + (weeks * 7)

        # Split the meals string into a list
        # Spoonacular doesn't take "lunch" as a meal type, so randomly replace it with "salad" or "side dish"
        meal_types = meals.split(", ")

        # Map user inputs to Spoonacular API meal types
        meal_map = {
            "breakfast": "breakfast",
            "lunch": ["side dish", "salad"],
            "dinner": "main course",
        }

        # Build the meal plan
        message = f"Here is your meal plan for {plan_length} days:\n\n"
        # Loop through each day and each meal to gather recipes
        for day in range(plan_length):
            message += f"**Day {day}:**\n"
            # For each meal, use recipe_search to get a recipe
            for meal in meal_types:
                # Alternate salad / side dish options
                if meal == "lunch":
                    meal_type = random.choice(meal_map[meal])
                else:
                    meal_type = meal_map.get(meal, meal)

                # Call the recipe search for the meal
                recipe_info, error = await self.meal_recipe_search(
                    meal=meal_type,
                    diet=diet,
                    allergies=allergies
                )
                if recipe_info:
                    # Format and send the meal plan
                    message += RecipeSearch.format_message(recipe_info)
                    message += f"\n\n"
            # Send each day's meal plan separately to reduce message size
            await interaction.response.send_message(message)


    async def meal_recipe_search(
            self,
            meal,
            diet=None,
            allergies=None,
            ingredients=None
    ):
        """
        Helper function to search for a recipe for a specific meal using the recipe_search function
        """
        try:
            # Call the recipe_search function from the RecipeSearch class to get the recipe id
            recipe_ids, error = await self.recipe.get_recipe_id(
                meal=meal,
                diet=diet,
                allergies=allergies,
                ingredients=ingredients,
                number=1
            )
            if error:
                return None, error

            # Get detailed recipe info
            recipe_id = recipe_ids[0]
            recipe_info, error = await self.recipe.get_recipe_info(recipe_id)
            if error:
                return None, error

            # Format and return the recipe information
            return RecipeSearch.format_message(recipe_info), None
        except Exception as e:
            print(f"Error searching for recipe: {e}")
            return None, "An error occurred while searching for a recipe"


async def setup(bot):
    await bot.add_cog(MealPlan(bot))
