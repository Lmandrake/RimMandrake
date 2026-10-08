# SHIPVERMIN_FREE_TIER_BEASTS_1: build report (FOUNDRY, 2026-10-07)

Status: BUILT offline, uncommitted. Static checks pass and the DLL builds. Nothing has been verified live.

## 1. swbestiary references in ShipVermin (before)

| where | reference | class |
|---|---|---|
| About.xml modDependencies + loadAfter | `mandrake.rsw.swbestiary` | dependency |
| Patches/RSW_Mynock_ShipVermin.xml | breeder comp + pressure/seek/gnaw extensions onto `RSW_Mynock` | mechanic |
| RM_ShipVerminMod.cs NestSpeciesRoster | `RSW_Mynock`, `RSW_Scavrat`, `RSW_WompRat`, `RSW_Zhakka` (+ donor `Mynock`/`Scavrat`/`WompRat`/`VFEI2_Fuelmite`) | roster row |
| RM_ShipVerminMod.cs settings | `spawnMynock/Scavrat/WompRat/Fuelmite` and labels "Mynock", "Womp rat", "Zhakka (fuelmite)" | text + roster |
| RM_Alert_ShipVermin.cs | "Mynocks aboard: {0}" plus the explanation | text |
| RM_CompProperties_VerminNest.cs | comment pointing at the RSW_Mynock patch | text |
| validation.py | PATCHED_DEF `RSW_Mynock`, mynock chains | test |
| About.xml description | mynock/SWBestiary prose | text |

`spawnRat` was a dead setting: it was not in the roster and had no UI control. The static check was already FAILING on it before this change. It is removed now. Scribe ignores unknown keys.

## 2. Free-tier beasts (invented, `RM_`, one slot each, stats copied from the canon creature in that slot)

The census read creature descriptions in src/RimMandrake. No unused ship-vermin creature exists: every candidate already has a biome home. So four are new.

- **RM_Skivvik** (slot of RSW_Mynock): a vacuum-proof flat hull leech. It drifts to powered hulls, breeds, and gnaws lights, conduits and laid floor. It carries the breeder and the pressure/seek/gnaw extensions inline, with the same numbers (soft cap 3, hard cap 12, tag ShipVermin).
- **RM_Rattagh** (slot of RSW_Scavrat): a sociable, toxin-proof, bristle-backed pest rodent that lives in wreck voids and ship crawlspaces.
- **RM_Gorrud** (slot of RSW_WompRat): a nocturnal, long-jawed predatory rodent of cargo holds and wrecks.
- **RM_Fethrik** (slot of RSW_Zhakka): a shelled fuel mite that sprays a cone of chemfuel that does not ignite (`RM_FethrikFuelSpew`).

Departures forced by the tier line: RSW leather, meat, body, name generator and sounds are swapped for the nearest vanilla ones. The free beasts have no `wildBiomes` (they arrive by nest and breeding). RM_Fethrik drops no leather because RSW_InsectChitin has no vanilla twin.

New C# (RM-tier copies, since an RM mod cannot name an RSW type):
- `RM_CompInnateAbility`, gated by the new setting `fuelSpewEnabled`.
- `RM_CompAbilityEffect_FuelSpew`.
- `RM_ShipVerminCanonSwapExtension`.

## 3. Canon rows moved

`src/RimStarWars/SWBestiary/Patches/ShipVermin/RSW_ShipVermin_CanonCast.xml` is guarded by `PatchOperationFindMod` on the name "RimMandrake: Ship Vermin". FindMod matches the mod NAME only (`ModLister.HasActiveModWithName`, checked in RimSage). ShipVermin is standalone, not part of the Biomes composition, so no composed name is needed. The patch does two things:
1. Adds the hull-leech mechanics to RSW_Mynock, moved unchanged from the old ShipVermin patch. validation.py checks that the numbers match RM_Skivvik's.
2. Adds `RM_ShipVerminCanonSwapExtension` to RM_Skivvik→RSW_Mynock, RM_Rattagh→RSW_Scavrat, RM_Gorrud→RSW_WompRat and RM_Fethrik→RSW_Zhakka.

`ShipVerminSettings.Resolve` then spawns the canon kind in that slot, and the slot's checkbox still governs it. The checkbox label shows whichever creature fills the slot. Free defs stay loaded but are replaced in the nest pick. The RUT FallWrecks `speciesWeights` that name RSW_ kinds still respect the slot toggles.

## 4. Files changed

- M `src/RimMandrake/ShipVermin/About/About.xml`: swbestiary removed from the dependencies and loadAfter, description rewritten. No loadAfter is needed: patches apply after all defs, and types resolve after all assemblies load.
- D `src/RimMandrake/ShipVermin/Patches/RSW_Mynock_ShipVermin.xml`
- A `src/RimMandrake/ShipVermin/Defs/ThingDefs_Races/RM_ShipVermin_Cast.xml`
- A `src/RimMandrake/ShipVermin/Defs/AbilityDefs/RM_ShipVermin_Abilities.xml`
- A `src/RimMandrake/ShipVermin/Source/RM_CompInnateAbility.cs`
- A `src/RimMandrake/ShipVermin/Source/RM_CompAbilityEffect_FuelSpew.cs`
- A `src/RimMandrake/ShipVermin/Source/RM_ShipVerminCanonSwapExtension.cs`
- M `src/RimMandrake/ShipVermin/Source/RM_ShipVerminMod.cs`: slot roster, Resolve, settings
- M `src/RimMandrake/ShipVermin/Source/RM_Alert_ShipVermin.cs`: the alert now reads "Ship vermin aboard"
- M `src/RimMandrake/ShipVermin/Source/RM_CompProperties_VerminNest.cs`: comment only
- M `src/RimMandrake/ShipVermin/Source/RM_ShipVermin.csproj`: 3 Compile Includes added
- M `src/RimMandrake/ShipVermin/validation.py`: free cast; new static checks for franchise-free content, canon patch guard and swaps, and same-tuning
- M `src/RimMandrake/ShipVermin/Assemblies/RimMandrake.ShipVermin.dll` + `.srchash`: rebuilt, uncommitted
- A `src/RimStarWars/SWBestiary/Patches/ShipVermin/RSW_ShipVermin_CanonCast.xml`
- M `src/RimUtinni/UtinniPatches/Patches/WreckVerminNest_ShipChunk.xml`: two stale comment pointers fixed

## 5. Art owed (placeholders are tinted vanilla textures; no PNG added)

- RM_Skivvik (placeholder Sparrow): a flat, wet, rubbery hull leech, sucker-ring mouth, two thin steering flaps, bruise-purple grey, about bat-sized. Needs north/east/south facings. A flight flip-book is optional.
- RM_Rattagh (placeholder Rat): a heavy, bristle-backed, cat-sized rodent with a blunt face, dusty brown, CutoutComplex mask for 5 tints. Needs a dessicated sprite.
- RM_Gorrud (placeholder Boomrat): a dog-sized, long-jawed, lean nocturnal rodent with a dark hide and visible teeth. Needs a dessicated sprite.
- RM_Fethrik (placeholder Megascarab): a large shelled mite with swollen amber fuel sacs under the rear shell and a head claw, rust-orange. Needs a dessicated sprite.
- RM_FethrikFuelSpew ability icon (placeholder UI/Abilities/FireSpew).

## 6. Checks run

- `validation.py` static: PASS (0 findings). It was FAIL (2) before. Sanity-probed: a wrong guard name is caught, 18 mechanics leaves were compared, the roster parses all 4 slots.
- `lint_def_type_refs.py --mod ShipVermin`: the RM→RSW DIRECTION warning is gone and there are 0 REAL findings. `--mod SWBestiary`: 0 REAL findings, and the new reference is classed GUARDED_XML. Full repo: 0 NO_DEPENDENCY pairs.
- `validate_patch.py` (repo plus every install root, 613/614 mods found): 0 errors.
  - The patch's free-kind conditional matched 4 ShipVermin defs, and the RSW_Mynock adds matched.
  - The warnings are the intended add-if-missing shape, plus vanilla texPaths that live inside asset bundles. The texPaths were checked against vanilla PawnKindDefs in RimSage.
- `winbuild.py RM_ShipVermin.csproj`: Build succeeded, 0 warnings, 0 errors.
- `modcheck lint`: 0 FAIL. It gave 1 new WARN: the walk `design/validation_walks/RimMandrake/ShipVermin.md` line 7 cites the deleted patch file.

## 7. Not verifiable offline / owed

- A2 (L1): free list load, no red errors, get_defs on the 4 free kinds. UNMEASURED.
- A3 (L2): with SWBestiary, RSW_Mynock carries the ShipVermin tag and the free kinds carry the swap. UNMEASURED (a patch that matches nothing logs nothing).
- Fuel spew grant on RM_Fethrik, Sparrow-texture rendering on a Bird body, Megascarab texture on BeetleLikeWithClaw: all unseen in game.
- Out of my edit scope, now stale:
  - The walk doc `design/validation_walks/RimMandrake/ShipVermin.md` still describes the RSW_Mynock patch, the old settings names and component ids (`mynock_patch.*`, `only_rat_on_spawns_a_rat`, `patch_target_species_resolves`).
  - The SWBestiary def header comments in `Defs/ShipVermin/ThingDefs_Races/RSW_Mynock.xml` and its PawnKindDef still point at the old ShipVermin patch.
- Duplicate code: SWBestiary's CompInnateAbility/CompAbilityEffect_FuelSpew now have RM twins. SWBestiary could consume the RM copies later; it already depends on rm.biomes but not on ShipVermin.
- Not deployed to the game Mods folder. A4 (owner approves list and art) is open.
