## spec
The biome flora rosters (`BIOME_FLORA_ROSTERS_1`) are deployed and the 2026-08-23 22:49Z load proved them
**parsed**: `BiomeDef` still 80, zero errors naming `BiomeFlora_Ashkarr`, all 604 plants and all 24 biomes
resolving in the matching 581-mod capture. **What no offline reading can tell us is whether it LOOKS right.**

Generate a map in each of three biomes chosen because each tests a different failure:

- **`Desert`** — the dayside family, and the biome most likely to be seen first.
- **`HorrorWastes`** — the one roster that was substantially *rewritten*: it lost `Plant_Agave`, its entire
  shipped roster, as a desert succulent standing on ground at −49 °C, and gained `HorrorWeb` from its own mod.
- **`AB_MycoticJungle`** — the mycoid belt, the family furthest from anything vanilla ships.

## verify
A map in each. Report **what species are actually present**, not a screenshot alone.

## criteria
- [ ] Each map's plants come from that biome's assigned family and no other.
- [ ] `HorrorWastes` shows `HorrorWeb` and shows no `Plant_Agave`.
- [ ] Nothing renders magenta or missing-texture.

## Watch out
🔴 **Judge by the ROSTER the biome holds, not by how much has sprouted — this is the whole trap.** 642 of 669
plants stop at `minGrowthTemperature` 0.0 °C and half this planet is below that, so a perfectly correct roster
can still read as bare ground. **Bare is not a failure of this patch.** If a map looks empty, read the biome's
`wildPlants` rather than concluding the roster is wrong; the temperature half is
`NORMALIZE_TEMPERATURE_TOLERANCES_1`, a different item, filed for BUILD.

⚠️ **`ExtremeDesert` (density 0.008) and `Wasteland` (0.0099) will read bare at ANY roster** — together 22.6%
of the planet. They are deliberately not on this list. `BARE_BIOMES_NEED_DENSITY_1` carries that question and
DECIDE's recommendation; do not "fix" a density here.

⚠️ **Every plant is FUEL.** `design/Jawa/worldbuilding/hydrology_and_fire_ecology.md` R-H3 makes plant growth
the fuel for a savanna that burns forever. If a biome reads *lusher* than expected, that is a fire-ecology
observation worth reporting, not just an aesthetic one.

⛔ **No `MayRequire` guards these patches, deliberately** — the dump's `packageId` names the mod that last
*retextured* a def, not the one defining it, so a `MayRequire` built from it would skip Core biomes. If a
roster appears not to have applied, the cause is the `PatchOperationConditional`, not a missing mod gate.
