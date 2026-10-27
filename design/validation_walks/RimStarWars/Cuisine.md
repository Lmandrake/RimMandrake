# Cuisine — validation walk
subject: src/RimStarWars/Cuisine  (packageId: mandrake.rsw.cuisine)
deps: none declared (all DLC assumed; Fish category needs no MayRequire).
list: minimal
status-hint: one campfire-roasted "roast on a stick" item (meat, fish or plant, named from its first ingredient; owner card 2026-10-26) plus the raw RSW_Skewer resource and its crafting recipe — Wave 1 of the high-cuisine build ladder, absorbed from badoaks.meatonastick(.expansion) per STICK_FOOD_INGEST_1.

## must be true
- RSW_Skewer (ParentName ResourceBase) and the ONE stick-meal ThingDef RSW_RoastOnAStick (ParentName MealCookedIngredientless) resolve as real ThingDefs.
- RSW_CraftSkewers (recipeUsers: CraftingSpot) turns 1 Woody-stuff ingredient into 10 RSW_Skewer.
- RSW_CookRoastOnAStick (0.5 nutrition of MeatRaw/Fish/PlantFoodRaw + 1 skewer -> 1) and RSW_CookRoastOnAStick4 (2.0 + 4 skewers -> 4), recipeUsers Campfire, requiredGiverWorkType BasicWorker, done through WorkGiverDef RSW_DoBillsRoastCampfire (any colonist, not only cooks; vanilla food-poisoning odds kept).
- Roasting a stick relabels the resulting item "Roasted <first ingredient>" via CompProperties_NameGen/NameGenComp, overriding the raw defName label.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.cuisine" and no XML error naming ThingDefs_Cuisine.xml, or RecipeDefs_Cuisine.xml   # load-time
2. [D] jawa/get_defs {defs: "ThingDef/RSW_Skewer;ThingDef/RSW_RoastOnAStick"} → RSW_Skewer statBases.MarketValue = 0.12
3. [D] jawa/get_def {defType: "RecipeDef", defName: "RSW_CraftSkewers"} → products.RSW_Skewer = 10, ingredients[0].count = 1, recipeUsers contains CraftingSpot
4. [D] jawa/get_def {defType: "RecipeDef", defName: "RSW_CookRoastOnAStick"} → recipeUsers contains Campfire, ingredientValueGetterClass = IngredientValueGetter_ExcludeSkewer, products.RSW_RoastOnAStick = 1
5. [B] rimworld/spawn_thing {defName: "RSW_Skewer", x, z, stackCount: 10} then jawa/list_things {defName: "RSW_Skewer"} → a stack of 10 exists at the target cell
X. [S] (human pass) roast one at a campfire and confirm the label reads "Roasted <ingredient>" (NameGenComp); then repeat with a colonist whose Cooking is disabled — they must be able to take the bill (BasicWorker)

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
(not yet dictated)

### must show

**Food on a stick**
- [ ] `cuisine_sticks_read_as_skewers` — the roast on a stick (`RSW_RoastOnAStick`)
      in a stockpile reads as food on a skewer.
- [ ] `cuisine_skewer_reads_as_sticks` — `RSW_Skewer` reads as a bundle of bare
      sticks. (guess)
- [ ] `cuisine_cooked_at_campfire` — a colonist cooking a stick meal is seen at a
      campfire.

### cannot show

- [ ] `cuisine_never_vanilla_meal_art` — a stick meal drawn as a vanilla meal
      plate. (guess)
