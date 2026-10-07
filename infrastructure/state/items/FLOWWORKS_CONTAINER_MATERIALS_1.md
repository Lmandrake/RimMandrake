# FLOWWORKS_CONTAINER_MATERIALS_1 — bottles and barrels are made from a material the player picks

Filed by BENCH, 2026-10-06, on the owner's typed ruling (23:28), answering what to do
about the glass-bottle render that contradicted his patchwork-metal brief (386d51170):

> "Player can set what kinds of bottles they use (leather, glass(any stone), metal)
> depending on what they have in abundance and what crafting stations they have.
> Barrels are like this too: wooden, metal, plasteel"

## spec

Vanilla-native: the bottle and barrel families are **stuffable** (one def per state,
material carried as `Stuff`), and each material is its own RecipeDef at the stations
that material belongs to, so what a colony can make follows its benches:

| container | material (stuff) | recipe | stations |
|---|---|---|---|
| bottle | leather (Leathery) | `RM_Make_Bottle_Leather` | crafting spot, hand/electric tailoring bench |
| bottle | glass, from any stone block (Stony) | `RM_Make_Bottle_Glass` | stonecutter's table, electric smelter |
| bottle | metal (Metallic) | `RM_Make_Bottle_Metal` | fueled/electric smithy, machining table |
| barrel | wood (Woody) | `RM_Make_Barrel_Wood` | crafting spot |
| barrel | metal (Metallic, not plasteel) | `RM_Make_Barrel_Metal` | fueled/electric smithy |
| barrel | plasteel | `RM_Make_Barrel_Plasteel` | machining table, fabrication bench |

The material survives the whole chain (empty -> filled -> dirty -> washed, pour into a
tank, revert): every C# site that swaps a container's def carries the source thing's
Stuff (`RM_LiquidBottleUtility.MakeContainer`). Colour comes from the stuff tint, so the
art must be a neutral greyscale silhouette per container.

| bucket | wood (Woody) | `RM_Make_Bucket_Wood` | crafting spot |
| bucket | metal (Metallic, not plasteel) | `RM_Make_Bucket_Metal` | fueled/electric smithy |
| bucket | leather (Leathery) | `RM_Make_Bucket_Leather` | crafting spot, hand/electric tailoring bench |

## rulings 2026-10-06 23:45 (decision taken by question card)

1. Buckets get player-chosen materials too: wood, metal, leather.
2. Material changes what a container can hold, capacity included: leather cannot hold hot/boiling
   liquids or acid (fill refused with a readable reason); glass and metal can; plasteel barrels hold more.
3. Any stone-made bottle is named "glass" (the stone only tints it).
4. The contained LIQUID's colour shows on a filled container; an empty one shows its material colour.


## material rules (ruling 2, built)

Data: `RM_ContainerMaterialsExtension` on RM_BottleItemBase / RM_BucketItemBase / RM_BarrelItemBase
(`Defs/LiquidTypes/ThingDefs/RM_LiquidBottles_Base.xml`); logic: `Source/LiquidTypes/RM_ContainerMaterialMath.cs`
(Verse-free, selftested against the shipped XML) and `RM_ContainerMaterials.cs`.

| container | material | units (base x factor) | hot | acid |
|---|---|---|---|---|
| bottle (1) | leather / glass / metal | 1 / 1 / 1 (a 1-unit bottle only moves at factor >= 1.5) | refuse / ok / ok | refuse / ok / refuse |
| bucket (5) | wood / metal / leather | 5 / 6 / 4 | ok / ok / refuse | refuse / refuse / refuse |
| barrel (25) | wood / metal / plasteel | 25 / 30 / 40 | ok | refuse / refuse / refuse (provisional) |

Hot = `LiquidDef.hot` (boiling water; generator row flag). Acid = corrodes apparel, AcidBurn damage, or pH <= 4
(acid water; reaction liquor and red slime have no bottled form). Enforced in the terrain fill search (skips refused
liquids, `JobFailReason` names why), the tank drain search (same), and both fill JobDrivers (message, container kept).
Capacity scales every tank pour/draw (`RM_ContainerMaterials.UnitsIn`). Drinking is unchanged: nutrition is per def.
Wooden buckets and barrels refuse acid but hold hot liquids (decision taken by question card 2026-10-07 00:04);
same refusal path and reason text as leather ("A wooden container can't hold acid water: the acid eats through it.").
Metal refuses acid too; only glass holds it. Owner typed in chat 2026-10-07 (relayed by the coordinator):
"Actually even metal can't do acid." Hot liquids: only leather refuses. Plasteel refusing acid is PROVISIONAL,
the safe default while he decides: one flag, `holdsAcid` on the Plasteel row of RM_BarrelItemBase.

## naming and tint (rulings 3 and 4, built)

`RM_CompContainerMaterial` on all three ItemBases. Naming: a stone container's label rebuilds vanilla's
"ThingMadeOfStuffLabel" with the word "glass", so "granite empty bottle" reads "glass empty bottle" and
"granite bottled fresh water" reads "glass bottled fresh water" (bill/recipe preview labels are vanilla's and still
name the stone; the recipe is already called "make glass bottles"). Tint: one Graphic; `ForceColor` returns the
contained liquid's `LiquidDef.color` (generator table `LIQUID_CONTAINER_COLORS`) on a filled container and nothing on
an empty/dirty one, so vanilla's stuff colour (the material) shows there. Safe to cache because every chain step makes
a new Thing. Both colours multiply the art, so the greyscale regens are what make either read cleanly.

## art

Greyscale, stuff-tintable regen jobs for RM_Bottle and RM_Barrel (not the held glass
render). See the progress log Transient/flowworks_container_materials_progress_2026-10-06.md.

Queued 2026-10-06: `fwart_RM_Bottle_Stuffable_v1`, `fwart_RM_Barrel_Stuffable_v1`, `fwart_RM_Bucket_Stuffable_v1` (greyscale,
owner_note = his words). Until they install, the coloured patchwork-metal art is
multiplied by the stuff colour and reads muddy.

## state

Rulings 1-4 built offline 2026-10-07, never loaded (no game this pass). Earlier: built offline: stuffCategories on the bottle and barrel
ItemBases, `Defs/LiquidTypes/RecipeDefs/RM_ContainerRecipes.xml` (6 recipes),
`RM_LiquidBottleUtility.MakeContainer` at all 6 def-swap sites, DLL rebuilt.

## watch out

- `src/RimMandrake/FlowWorks/review_map.py` spawns RM_BottleEmpty/RM_BarrelEmpty through
  `rimworld/spawn_thing` with no stuff; if that tool does not pick a default stuff the
  vanilla "made from stuff but no stuff" error fires there. Check on the next review-map run.
- Existing saves holding unstuffed bottles/barrels load with null Stuff on a now-stuffed
  def; vanilla assigns default stuff with a one-time error. Map state is disposable, so
  accepted.
- First live load: confirm the 6 recipes appear at their benches and a steel bottle stays
  steel through fill -> drink -> wash.
