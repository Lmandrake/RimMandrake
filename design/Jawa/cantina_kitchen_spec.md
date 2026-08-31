<!-- status: spec — CANTINA_KITCHEN_SPEC_1, BENCH 2026-08-31, green-lit by the owner (tier 2).
     Source register: V2_DREAMS "The Cantina Kitchen — Star Wars food is ANIMAL food"
     (owner, 2026-08-15: "a whole mod of its own, and one of the better ideas on this list").
     v2 content; specced now while Fable holds the pen. -->
# The Cantina Kitchen — Star Wars food is animal food

The register's thesis stands: Star Wars sells an inhabited galaxy through its
menu — tanks of live things behind the bar, eggs shaken into cocktails, a
squealing thing tipped down a throat. RimWorld's food is abstract; this mod
makes it inhabited. The Jawa angle is unchanged and load-bearing: **the
player ENCOUNTERS the cantina kitchen** in Hutt and Deepwater settlements —
a trade good and a moral texture, not a tech tree the clan starts with.

## 1. The spine — the live tank (the one novel mechanic)

`RSW_LiveTank` (building family: aquarium, cage, warm-pit): holds small live
creatures as INGREDIENTS. Mechanism is the pattern measured for the Devourer
this sitting — **despawn + `IThingHolder` inner container** (`ThingOwner`,
deep-saved), the shipped, save-safe way to keep a pawn inside a thing:

- Load job: a hauler brings a small live animal (bodySize cap) to the tank;
  the tank despawns it into its container. Inspect string lists occupants;
  a glass-front graphic overlay shows silhouettes (art, not simulation).
- Freshness IS occupancy: recipes below consume "live X" by pulling from a
  tank in range; no tank, no dish. Occupants tick hunger very slowly
  (abstracted upkeep: the tank consumes small feed per occupant per day) —
  neglect starves the stock, quietly, Zizzik-style.
- The tank never fights back: only bodySize-capped, non-humanlike occupants.
  (Humanlike in a tank is a different mod and a different rating.)

## 2. The menu — recipes repointed, not invented

Per the register: VCE/VBE own the cooking/brewing machinery; we add
ingredients and dishes, not mechanics.

- **Egg lane (VBE):** gorg/kwi eggs from SW Animal Collection species (MIT,
  and its 160 creatures are the solved art problem) → cocktail chain on
  Brewing Expanded's drink shape.
- **Whole-live dishes (VCE):** "squirming bowl," "drowned gorg" — recipes
  whose ingredient is pulled LIVE from a tank; the dish carries a
  `RSW_EatenAlive` thought hook.
- **The faith matrix (the part nobody uses Ideology for):** the same dish
  reads three ways by precept — reverent (Oomo: the family fed from living
  waters, +mood), indifferent (default, small +novelty), horrified
  (a compassion/animal-precept holder, −mood + opinion hit on the server).
  One ThoughtDef family keyed off precepts; no C# beyond the thought worker
  if vanilla's precept-conditional thoughts don't already reach it.

## 3. Where it lives

- **Hutt & Deepwater settlement kitchens** (authored rooms in their
  settlement templates — TILE_STRUCTURE_DESIGNS_1's grammar): tanks stocked,
  dishes on tables, a cook pawn. The player walks in and the galaxy is
  inhabited.
- **Trade:** exotic dishes and LIVE STOCK as trade goods (a caged gorg is
  cargo); Deepwater sells the aquatic lane (depths coupling — shoal grazers
  are tank stock).
- **The clan:** can buy, loot, and eventually build tanks — but no scenario
  start includes one, and Sekki Vosh stays the humble default. Acquiring a
  cantina kitchen is prosperity made visible (and Mob'Unloo pleased).

## 4. Build shape

`mandrake.rsw.cantina` — one comp (`CompLiveTank`, the IThingHolder), the
building family, ~8 RecipeDefs + products, the thought family, loot/trade
lists, settlement-template garnish. Art: tank fronts + dish sprites (sprite
skill; SW Animal Collection silhouettes for tank overlays). No Harmony
expected; the one risk is recipe ingredient-from-container resolution —
if vanilla's ingredient finder won't look inside a container, the fix is a
WorkGiver that ejects-to-spot on demand (still no Harmony).

## verify
Quicktest: build tank, load a live gorg, cook the dish — PROVE the recipe
consumes the occupant and the eater gets the thought; EXPECT the three-way
mood split across three pawns with the three precept states. LIES: the
ingredient may silently resolve from a corpse on the floor instead of the
tank — assert the tank's occupant count dropped.

## criteria
The owner tours a Hutt kitchen on a test map and it reads as the cantina;
the moral texture fires (one pawn delighted, one revolted); nothing of this
is required by any other system.
