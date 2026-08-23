
## spec
🔴 **OWNER, 2026-08-23, verbatim:** *"I thought you had distributed the plants per biome for me?
If not, PLEASE do that right now. You, agent Decide, make those calls right now and do it. That
will fix so much… Try to avoid using the same plant across different biome types. It's ok to
draw from Tinctora, Healroot, and other normally player-grown plants as you decorate the
biomes."* Then: *"We can set the appropriate temperatures later, don't worry about that as a
constraint."*

**Done and DEPLOYED 2026-08-23; last extended 10:44.** `design/Jawa/mods/biome_flora.py` holds the rosters and
emits `src/Jawa/Jawa_Patches/Patches/BiomeFlora_Ashkarr.xml` (25 operations — 24 rosters plus the `Wasteland` density raise). The readable
version is `design/Jawa/worldbuilding/biome_flora_rosters.md`.

**8 families · 24 biomes · 604 plants, every one distinct.** ⚠️ **The 134 in the first draft of this item was superseded by three later passes** (`a2292cf1` 134->546, `f9bf9da4` the 84 leftovers, `6c1f16a1` Wasteland density); 604 is what the generator, the doc, the patch and the deployed copy all now say. 4 biomes carry no flora by design
(`Ocean`, `Lake`, `SeaIce`, `IceSheet`). The families are the design: dayside desert ·
contamination · mycoid belt · river jungle · frozen nightside · volcanic · machine and scar ·
alien. **`--check` fails the build if any plant appears in two of them.**

🔑 **Three findings worth keeping:**

1. 🔴 **`wildPlants` is a `LoadDataFromXmlCustom` field — `<li>` destroys the def.** Read from
   `BiomePlantRecord` source, not assumed: the node **NAME** is the plant defName and the node
   **VALUE** is the commonality. This is the same trap that cost 26 BiomeDefs earlier the same
   day, and the only reason it did not repeat is that the source was read before writing XML.
2. ⛔ **No `MayRequire`, deliberately.** The def dump's `packageId` names the mod that last
   **retextured** a def, not the one that defines it — Core's `Desert` reports GRiNDTerra. A
   `MayRequire` built from it would skip Core biomes whenever that mod is absent.
   `PatchOperationConditional` on the same xpath is the correct guard and is sufficient.
3. ⭐ **`HorrorWastes` loses `Plant_Agave`** — a desert succulent on ground at −49 °C, its
   entire shipped roster — and gains `HorrorWeb`, its own mod's plant, which nothing on this
   planet used until now.

## verify
⏳ **Needs a cold load; defs parse only at startup.** The lines and the look are written into
`infrastructure/state/NEXT_RELOAD.md` under *BIOME FLORA*. In order:
`BiomeDef` count still **80** (54 means an `<li>` crept back in) · zero cross-reference errors
naming a plant · zero red errors naming `BiomeFlora_Ashkarr` · then a map in `Desert`,
`HorrorWastes` and `AB_MycoticJungle`.

**Already proven offline:** all 604 defNames exist in the live dump (68,518 defNames, 578
mods); all 24 target biomes carry a `wildPlants` node, so every Conditional matches and every
Replace runs; the deployed copy is byte-identical to the repo.

## criteria
- [x] Every placed biome with flora has an assigned roster.
- [x] No plant crosses a family, enforced by the generator.
- [x] Player-grown flora used as decoration — healroot, tinctoria, psychoid, smokeleaf,
      devilstrand, haygrass, cotton, ambrosia.
- [x] Deployed and verified in sync.
- [x] Confirmed by a cold load — 80 BiomeDefs, zero errors, all 604 plants resolve. ⏳ The LOOK is `BIOME_FLORA_LOOKS_RIGHT_1`, filed for CHECK.

## Watch out
⚠️ **Judge the patch by the ROSTER a biome holds, not by how much has sprouted.** 642 of 669
plants stop at `minGrowthTemperature` 0.0 °C and half this planet is below that, so a correct
roster can still read bare. That is `NORMALIZE_TEMPERATURE_TOLERANCES_1`, filed for BUILD.
⚠️ **`ExtremeDesert` (0.008) and `Wasteland` (0.0099) will read bare at any roster** — 22.6% of
the planet. Density was left at its shipped value on purpose; `BARE_BIOMES_NEED_DENSITY_1`
carries the question and DECIDE's recommendation.
⚠️ **Every plant kept is FUEL.** `hydrology_and_fire_ecology.md` R-H3 makes plant growth the
fuel for a savanna that burns forever, so a roster change is a fire-ecology change.

## HARVEST — the 2026-08-23 22:49Z load, read by DECIDE
✅ **The three offline readings this item asked for all pass**, against the first capture that matches the
live mod list (581 mods, `capturedUtc 2026-08-23T22:49:51Z`, 79,093 defs, 534 types, `orphan=0`):

| reading | wanted | got |
|---|---|---|
| `BiomeDef` count | **80** (54 would mean an `<li>` crept back into `wildPlants`) | **MEASURED 80** |
| red errors naming `BiomeFlora_Ashkarr` | zero | **0 mentions in the whole log** |
| cross-reference errors naming a roster plant | zero | **0 of the 25 in the log** |

Re-proven against the NEW capture rather than the 578-mod one the spec was written on: **all 604 roster
plant defNames resolve, and all 24 target biomes exist** — so every `PatchOperationConditional` matched and
every `Replace` ran. The 25 cross-reference errors in this load are other mods' (16 `Pawn_Melee_Punch_HitBuilding`
sound refs, a `VWE_Tool_Whip` trader entry, and nine `BMT_*` names); ⚠️ **`BMT_BoomSpore` is a plant-shaped
name and is NOT one of ours** — it appears zero times in `biome_flora.py` and zero times in the patch.

⏳ **What is still open is only the LOOK**, filed as `BIOME_FLORA_LOOKS_RIGHT_1` for CHECK: a map in `Desert`,
`HorrorWastes` and `AB_MycoticJungle`. 🔑 **Judge it by the roster the biome HOLDS, not by how much sprouted** —
the Watch out section below is the reason, and it has not changed.
