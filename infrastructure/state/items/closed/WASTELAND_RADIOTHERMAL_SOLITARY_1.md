# WASTELAND_RADIOTHERMAL_SOLITARY_1 — radiothermal solitary: def built, heat + spacing C# owed

## what

Resolves `COMMISSION_LEDGER_CLEANUP_1` ledger slug
`wasteland:radiothermal-solitary-living-furnace-spacing-law` — wasteland.md
§4: "The radiothermal solitaries — so hot with their own decay they must
dump heat to live: they haunt the cold dark scour and keep distance from
their own kind or cook each other (the spacing law returns, driven by
heat). A warm boulder in the black country means one passed; a tamed one
is a living furnace that heats a shelter all winter and irradiates it the
entire time."

## built

`RUT_Radiothermal` (`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_Radiothermal.xml`)
— a plain interim creature: heavy, ground-hugging quadruped, low MoveSpeed,
high armor/heat armor, `herdAnimal=false`, `wildGroupSize` 1, `roamMtbDays`
widened well past this mod's herd defaults. Wired into `RUT_Wasteland.xml`
wildAnimals at (see the biome file's own comment). No donor found anywhere
in the active mod set that already emits ambient heat as a creature
mechanic (checked cast_assignment.csv/animal_census.csv).

## still owed (this item's remaining scope)

Both halves of the roster's own `mechanic_load` ("NEW C#: heat emission +
spacing") are genuinely new engine work, not guessed at inline:

1. **Heat emission** — "a tamed one heats a shelter all winter." No
   RimSage available from this machine (WSL/Mac) to verify whether the
   vanilla `CompProperties_HeatPusher` (the building-heater comp) attaches
   cleanly to a Pawn ThingDef, so that is NOT assumed — verify on the
   Desktop before either using it or writing a bespoke comp.
2. **Same-species spacing law** — "keep distance from their own kind or
   cook each other." Needs a genuine JobGiver/think-tree insert (avoid own
   species within some radius), no vanilla mechanism does this.

## art

Three facing jobs filed and queued (`rutradiothermal_v1_south/east/north`).

## naming

Working name only — folded into `WASTELAND_SHIPPING_NAMES_1`.
