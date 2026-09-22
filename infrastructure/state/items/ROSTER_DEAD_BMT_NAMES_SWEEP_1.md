# ROSTER_DEAD_BMT_NAMES_SWEEP_1 — the 14 dead BMT_ rows nobody can rename safely

## where this came from

`MIASMA_FEVERWOOD_GREENTIDE_BMT_1` fixed three rosters. Generalising its measurement
across all **31** rosters (2026-09-21, BENCH, Mac session) found **32 more** live `BMT_`
rows in 12 rosters. All 32 name a `biomesteam.biomescaverns` def (donor **NOT** in the
active mod list) that we have **already ported** under an `RSW_` name; **0** were
unportable.

**18 of the 32 were already wired** in their biome under the ported name — pure stale
rows, renamed at `b173e699d`, no judgment needed.

**These 14 are the remainder: ported, and wired NOWHERE.** They are deliberately left
under their dead `BMT_` names, because renaming a row is an assertion that the species is
admitted — and for several of these that assertion is false or contested. Renaming first
and asking later would launder a guess into the roster.

## 🔴 Do NOT bulk-wire these to close the count

That is the exact trap the parent item's spec names. At least four of the 14 are unwired
**correctly**, by an existing ruling — evidence below, gathered per species. A sweep that
wires all 14 would re-admit creatures the owner already excluded and put fishing results
on the land.

## the 14, with what is already known about each

`bs` = `race.baseBodySize`, MEASURED off our own port def, not the donor.

| roster | biome | dead name | bs | what the evidence says |
|---|---|---|---|---|
| `the_twilight_sea` | `RUT_TwilightSea` | `BMT_Megakrill` | 0.2 | 🔴 **Leave unwired.** Its own roster law says it: *"still a FISHING RESULT, never a wildAnimals s[pawn]"*. The row belongs in a fishing/`fish` context, not `<wildAnimals>`. |
| `the_lantern_deeps` | `RUT_LanternDeeps` | `BMT_CrystalCrab` | 2.4, predator | 🔴 **Leave unwired — evicted by its own sheet.** `RUT_LanternDeeps.xml`'s header records the Deeps sheet's **hard ban 3** evicting the six crystal-studded residents *by name*, crystal crab among them. The roster row is the stale thing here, not the wiring; it should become an **eviction record**, not an admission. |
| `the_twilight_sea` | `RUT_TwilightSea` | `BMT_MutatingTumorfishAdult` | 1.8, predator | ⚠️ **Probably the wrong roster.** Law says *"RETARGET: the_twilight_deep (schooling/multiples)"* — the twilight **deep** is the sea-FLOOR sheet (`the_twilight_deep.md`), a different thing from the surface. Resolve where it lives before wiring anything. |
| `the_twilight_sea` | `RUT_TwilightSea` | `BMT_MutatingTumorfishFry` | 0.8, predator | ⚠️ Same as above. |
| `the_twilight_sea` | `RUT_TwilightSea` | `BMT_MutatingTumorfishSpawn` | 0.8 | ⚠️ Same as above. |
| `the_grey_sea` | `RUT_GreySea` | `BMT_Polluwog` | 0.1 | ✅ **Wiring looks genuinely owed** — law: *"STAYS Grey Deep — not flagged schooling; cap released so it is a resident (owner ruling 2026-09-…)"*. But note it says Grey **Deep**, and the roster is the Grey **Sea**; settle surface-vs-floor first, same question as the tumorfish. |
| `wasteland` | `RUT_Wasteland` | `BMT_Sacapillar` | 2.4 | ✅ Wiring looks owed — law: *"PLACED: wasteland (homeless disposition sitting, frozen 2026-09-10)"*. A placement ruling exists and nothing acted on it. |
| `the_cracked_lands` | `RUT_CrackedLands` | `BMT_SandPillar` | 0.8 | ✅ Placed by the round2 move mapping (*"cracked land"*), never wired. ⚠️ Wire onto **`RM_FloodedCanyon`**, not `RUT_CrackedLands` — that twin is FROZEN as of `FLOODEDCANYON_RM_MOD_BUILD_1`, and campaign fauna rides a Utinni patch onto the `RM_` def. |
| `nightside_ice` | `RUT_NightsideIce` | `BMT_CaveLemming` | 1.0 | ⚠️ Placed (*"ice sheet, rename"*) but the law also says a **rename/refashion is owed** with a thermal-only sensing line (owner ruling 2026-09-1x). Do the refashion question first; wiring a def that is about to be renamed buys nothing. |
| `the_scarlands` | `RUT_Scarlands` | `BMT_CrystalFairyMole` | 0.86 | ⚠️ Placed here by the round2 mapping (*"Scarlands, oddly"*), and it is ALSO one of the six names in the Deeps' ban 3 — which under the owner's 2026-09-21 cut-scope ruling does **not** reach the Scarlands. So it may legitimately live here. Also note the biome is being renamed to `RM_Warscar` (`SCARLANDS_STANDALONE_MOD_1`). |
| `the_scarlands` | `RUT_Scarlands` | `BMT_MegaphoridLarva` | 0.32 | ✅ Placed (*"scarlands"*), never wired. Same `RM_Warscar` note. |
| `arid_shrubland` | `RUT_AridShrubland` | `BMT_Stoneback` | 0.4 | ⚠️ **One species, three rosters.** Law is *"Anywhere on the dayside where it might be needed"* — a generic dayside filler. It IS already wired in `RUT_Desert`. Decide once whether "anywhere on the dayside" means wire it into all of them or leave it as the Desert's. |
| `the_scarlands` | `RUT_Scarlands` | `BMT_Stoneback` | 0.4 | ⚠️ Same species, same one-time decision. |
| `wasteland` | `RUT_Wasteland` | `BMT_Stoneback` | 0.4 | ⚠️ Same species, same one-time decision. |

## spec

Work species-by-species, in this order, because the first two shrink the list without any
judgment call:

1. **`BMT_Megakrill` and `BMT_CrystalCrab`** — do NOT wire. Move each row out of `fauna`
   into that roster's `evictions` array with a `reason` citing the ruling that excludes it
   (its own "fishing result" law; the Deeps' ban 3). This is bookkeeping, not a decision.
2. **Settle surface-vs-floor once** for the sea species (`Polluwog`, the three
   `MutatingTumorfish`): does a sea-FLOOR sheet (`the_twilight_deep.md`,
   `the_grey_deep.md`) have a def of its own to wire onto, or do floor residents ride the
   surface biome? One answer resolves four rows. ⚠️ Those four biomes are also merging into
   ONE mod, `mandrake.rm.terminalbiomes` (§7 Q1 ruling), so the answer interacts with
   `TERMINALBIOMES_RM_MOD_BUILD_1`.
3. **`BMT_Stoneback` × 3** — one ruling, not three: does "anywhere on the dayside" wire it
   into the Arid Shrubland, Scarlands and Wasteland, or does it stay the Desert's alone?
4. **The four straightforward placements** (`Sacapillar`, `SandPillar`, `MegaphoridLarva`,
   `CrystalFairyMole`) — rename the row and wire at the roster's own commonality, checking
   `ECOSYSTEM_PYRAMID_LAW_1` before each (compute the biome's small-weighted share the way
   `MIASMA_FEVERWOOD_GREENTIDE_BMT_1` did; `Sacapillar` at bs 2.4 into the Wasteland is the
   one most likely to matter). ⛔ `SandPillar` goes onto `RM_FloodedCanyon` via a Utinni
   patch, never the frozen `RUT_CrackedLands`.
5. **`BMT_CaveLemming`** — resolve the owed rename/refashion first, then wire under the
   new name.

## verify

Zero `BMT_` names remain in any of the 31 roster JSONs' `fauna` arrays. Every row either
resolves to an `RSW_` name that is wired in the biome it names, or sits in that roster's
`evictions` with a reason citing a real ruling. `validate_patch.py` clean on every edited
XML. No biome newly fails `ECOSYSTEM_PYRAMID_LAW_1`'s proposed 60% small-weighted floor as
a result of the wiring.

## criteria

Every species each roster admits can actually appear in the shipped game, and every species
it excludes says why and on whose ruling — with no row silently renamed into an admission
nobody made.

## 🔴 NOT measurable on the Mac laptop

Whether each `RSW_` port resolves against the **live** active mod list was not checked here:
`measure` is not executable on this machine (`permission denied`) and there is no local def
dump. Existence in `src/` was verified by parsing the XML. A Desktop pass should confirm
resolution before wiring.

## Noted, not a defect

94 distinct `BMT_` defNames are still targeted by xpath across 12 of our patch files (42 in
`Doctrine/Patches/MegafaunaYield.xml`) while that donor is inactive — but those ops are
wrapped in `PatchOperationConditional` (931 of them in that file), so they are inert by
design, not silently broken. Cleanup at most, and only alongside other work in those files.
