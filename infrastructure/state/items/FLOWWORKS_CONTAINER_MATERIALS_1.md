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

Buckets are NOT in the ruling and stay unstuffed until he says.

## open questions for the owner

- Buckets: same treatment (and which materials)?
- Should materials differ in behaviour (leather leaks or can't hold boiling/acid,
  plasteel holds more)? Today only vanilla stuff stats differ (hit points,
  flammability, beauty).
- A stone bottle's label reads "granite empty bottle" (vanilla stuff naming), not
  "glass bottle". OK, or should "glass" be its own material made from stone?
- The planned per-liquid tint of the container art conflicts with the stuff tint;
  material tint wins for now.

## art

Greyscale, stuff-tintable regen jobs for RM_Bottle and RM_Barrel (not the held glass
render). See the progress log Transient/flowworks_container_materials_progress_2026-10-06.md.

Queued 2026-10-06: `fwart_RM_Bottle_Stuffable_v1`, `fwart_RM_Barrel_Stuffable_v1` (greyscale,
owner_note = his words). Until they install, the coloured patchwork-metal art is
multiplied by the stuff colour and reads muddy.

## state

Built offline, never loaded (no game this pass): stuffCategories on the bottle and barrel
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
