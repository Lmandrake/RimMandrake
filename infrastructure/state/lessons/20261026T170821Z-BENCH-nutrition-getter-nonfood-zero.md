A RecipeDef using vanilla IngredientValueGetter_Nutrition values a non-food ingredient (resin, salt, bitumen) at 0 nutrition, so a bill mixing food with a sealing agent can never gather the agent and never starts. ColdStorage ships IngredientValueGetter_NutritionOrCount (food by nutrition, everything else by count); use it for any food+agent recipe.
home: rimworld-modding
