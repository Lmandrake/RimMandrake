## spec
Owner, live 2026-09-10, watching the colony map: "There are also 'Rose of
Rebirth' all over the map... We want to control that plant tightly."

`RotR_RoseOfRebirth` (mod: Romance On The Rim, `telardo.romanceontherim`,
`.../workshop/content/294100/2654432921/1.6/ModCompat/Anomaly/Defs/Artifact/
ThingDefs/RoseOfRebirth.xml`) — 476 instances counted on the live Ash'karr
colony map (`jawa/list_things`, group=Plant, 2026-09-10).

Its own def rules out the two ordinary spread routes:
- `plant.wildClusterWeight = 0` — cannot wild-spread like a normal plant.
- `plant.sowTags Inherit="False"` (empty) — cannot be sown via an ordinary
  colonist grow zone.
The only two XML spawn paths in the mod: the ThingDef itself, and a
`GenStep_ScatterThings` used ONLY by the special "Riot Roses" quest/temp site
(`RiotRoses.xml`, `countPer10kCellsRange 2~3` — nowhere near 476 on a normal
map). So the real spawn route is compiled C# — `thingClass
RomanceOnTheRim.RoseOfRebirth`, or `CompProperties_PlantableByWidowed` on
`RotR_RoseOfRebirthSeed` (tied to a widowed pawn planting one near a lover's
grave) — likely re-triggering far more than the "one per widowed pawn, once"
the flavor text implies. Needs a decompile of `RomanceOnTheRim.dll`
(`ilprobe`/`ilspycmd`, per `read-the-mechanism-before-filing-the-fix`) to find
the actual trigger before proposing a fix.

## verify
PROVE: read the decompiled `RomanceOnTheRim.RoseOfRebirth` Tick/spawn logic
(or `CompProperties_PlantableByWidowed`'s planting job) and name the exact
condition that re-fires.
EXPECT: either a missing "already has one" gate, or a MapComponent/incident
looping over graves/widowed pawns without a per-pawn cooldown.
LIES: a clean read of the seed-planting comp alone would miss a separate
Harmony patch elsewhere in the assembly doing the actual mass placement —
check the whole assembly's references to `RotR_RoseOfRebirth`, not just the
comp that plants it.

## NOT yet decided
Whether "control tightly" means: cap total live count via a periodic
Harmony-free sweep, patch the C# trigger condition (mod update, fragile
across Romance On The Rim updates), or just fix the current map by hand once
(deferred — owner: "we'll repair savegames later"). Needs an owner call once
the mechanism is known.
