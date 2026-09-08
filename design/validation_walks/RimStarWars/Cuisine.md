# Cuisine — validation walk
subject: src/RimStarWars/Cuisine  (packageId: mandrake.rsw.cuisine)
deps: none declared. RSW_FishOnAStick / RSW_CookFishOnAStick carry MayRequireAnyOf="Ludeon.RimWorld.Odyssey,vanillaexpanded.vcef" (optional — absence is not an error)
list: minimal
status-hint: campfire-cooked "on a stick" food line (meat/veg/fungus/fruit/blend/fish) plus the raw RSW_Skewer resource and its crafting recipe — Wave 1 of the high-cuisine build ladder, absorbed from badoaks.meatonastick(.expansion) per STICK_FOOD_INGEST_1.

## must be true
- RSW_Skewer (ParentName ResourceBase) and the 7 stick-meal ThingDefs (RSW_MeatOnAStick, RSW_VegOnAStick, RSW_FungusOnAStick, RSW_LittleMeatOnAStick, RSW_BlendOnAStick, RSW_FishOnAStick, RSW_FruitOnAStick) plus RSW_CookedSkewer all resolve as real ThingDefs (ParentName MealCookedIngredientless).
- RSW_CraftSkewers (recipeUsers: CraftingSpot) turns 1 Woody-stuff ingredient into 10 RSW_Skewer.
- Each stick-meal RecipeDef (e.g. RSW_CookMeatOnAStick, recipeUsers: Campfire) consumes RSW_Skewer alongside its named raw-food category and yields the matching ThingDef.
- Eating RSW_CookedSkewer applies ThoughtDef RSW_AteEmptySkewer: baseMoodEffect -6, durationDays 1.
- Cooking any stick meal relabels the resulting item "Roasted <first ingredient>" via CompProperties_NameGen/NameGenComp, overriding the raw defName label.
- RSW_FishOnAStick and RSW_CookFishOnAStick exist only when Ludeon.RimWorld.Odyssey or vanillaexpanded.vcef is active — legitimately absent otherwise, not a Config error.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.cuisine" and no XML error naming ThingDefs_Cuisine.xml, RecipeDefs_Cuisine.xml or ThoughtDefs_Cuisine.xml   # load-time
2. [D] jawa/get_defs {defs: "ThingDef/RSW_Skewer;ThingDef/RSW_MeatOnAStick;ThingDef/RSW_CookedSkewer;ThoughtDef/RSW_AteEmptySkewer"} → RSW_Skewer statBases.MarketValue = 0.12; RSW_CookedSkewer.ingestible.tasteThought = RSW_AteEmptySkewer; RSW_AteEmptySkewer.stages[0].baseMoodEffect = -6
3. [D] jawa/get_def {defType: "RecipeDef", defName: "RSW_CraftSkewers"} → products.RSW_Skewer = 10, ingredients[0].count = 1, recipeUsers contains CraftingSpot
4. [D] jawa/get_def {defType: "RecipeDef", defName: "RSW_CookMeatOnAStick"} → recipeUsers contains Campfire, ingredientValueGetterClass = IngredientValueGetter_Nutrition, products.RSW_MeatOnAStick = 1
5. [B] rimworld/spawn_thing {defName: "RSW_Skewer", x, z, stackCount: 10} then jawa/list_things {defName: "RSW_Skewer"} → a stack of 10 exists at the target cell
6. [B] rimworld/spawn_thing {defName: "RSW_CookedSkewer", x, z} then jawa/list_things {defName: "RSW_CookedSkewer"} → it exists on the map
X. [S] (human pass) cook meat-on-a-stick at a campfire and confirm the item's in-game label reads "Roasted <ingredient>" (NameGenComp), then eat an empty RSW_CookedSkewer and confirm the mood thought bubble fires
