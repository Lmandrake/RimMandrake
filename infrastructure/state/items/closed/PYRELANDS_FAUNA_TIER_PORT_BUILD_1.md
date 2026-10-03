# PYRELANDS_FAUNA_TIER_PORT_BUILD_1

Spec: `design/Jawa/worldbuilding/biomes/pyrelands_bedazzle_review_2026-10-01.md` §1 (finding 1) and §4 row 0. Ruled by `design/RimMandrake/biome_mod_architecture.md` §7 Q11a/Q12; owner turn 1 (card): animals and heat together.

1. Port the eight invented residents (`RUT_FireHawk`, `RUT_FurnaceBeast`, `RUT_Flamefang`, `RUT_Sytheclaw`, `RUT_Barbslinger` with its tail gun, `RUT_FireWasp` with its eggs, `RUT_Ashwallow`, `RUT_Emberscythe`) to `RM_` race and kind defs in `mandrake.rm.pyrelands`, wired inline in `RM_Pyrelands`'s `<wildAnimals>` at today's commonalities, replacing the 13 vanilla placeholder rows. Carry labels, descriptions, art, flight stats and flip-book frames, and comps.
2. Repoint every reader: `PyrelandsMechanicsDefOf` (both mods), the ember carry, the thermal cycle, bed-down ignition, warmth aura, burrowing, the furnace herd seeder, `Patch_FurnaceBeastHeatImmunity`, `RUT_FurnaceHide` sources, the north-star suite's def names.
3. Shrink `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml` to an `Add` of the seven canon `RSW_` rows (no longer a Replace).

Not here: `RUT_Sytheclaw`'s rows in the Greentide and the Contagion twin are those biomes' sitting rows, not evictions (they repoint to the `RM_` def or keep it, per their sittings). This item goes first: `PYRELANDS_ULLAI_GIANT_BUILD_1` and `PYRELANDS_HEAT_KIND_BUILD_1` wire against the `RM_` names.

🔴 **North-star re-measure:** `PYRELANDS_NORTHSTAR_TRIAL_1` must re-measure after row 0 (the animal move) lands: it changes the cast the trial's census reads. Sequence with `PYRELANDS_SHIP_READINESS_1`.

## verify
- Free tier alone (no UtinniPatches): `RM_Pyrelands` spawns the eight; a fire-hawk carries embers; a furnace-beast cycles.
- No `RUT_` row of these eight left anywhere targeting `RM_Pyrelands`; selftests pass.
