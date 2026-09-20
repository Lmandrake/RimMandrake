# DESERT_PORT_DUPLICATE_DEFS_1 — working notes (2026-09-20)

## 1. Independent measurement — CONFIRMS the item
166 Defs/*.xml parsed, keyed on (element tag, defName):
- 2001 def elements, 1635 unique (defType, defName)
- **349 duplicated keys**, 366 extra copies (some keys appear 3x)
- **0 duplicate keys without a DesertPort file involved**
- ThingDef 154 / SoundDef 114 / PawnKindDef 65 / BodyDef 16 — exact match to the item.

## 2. Classification (canonical-XML diff, whitespace-normalised)
- IDENTICAL: 222 (SoundDef 114, ThingDef 51, PawnKindDef 46, BodyDef 11)
- DIFFERS:   127 (ThingDef 103, PawnKindDef 19, BodyDef 5)
- Every duplicated key has >=1 non-DesertPort copy. No key is DesertPort-only.

## 3. Known-exception check
`RSW_Ferroclaw`, `RSW_Voltmaw`, `RSW_Cindermite` (PORTED_BEAST_MECHANICS_REBUILD_1)
are **NOT duplicated** — they live only in Defs/DesertPort/RSW_DesertPortMechanics.xml
and RSW_DesertPortMisc_Races.xml. That trap does not bite. Nothing of theirs is touched.

## 4. Merges performed (auditable list)
PENDING

## 5. BodyDef reference check
PENDING

## 6. Final verification
PENDING

## 4. Decision policy (settled after diffing all 137 differing copies)
Survivor = the PRE-EXISTING def, in every one of the 349 cases. Evidence:
- 27 DP copies use `ParentName="SWanimals_RawMeatBase"` — that abstract does not exist
  under `src/`; the survivor's `RSW_SWanimals_RawMeatBase` does. DP would drop the def.
- 224 differing reference values resolve on the OLD side and NOT on the DP side
  (`RSW_Claws`, `SW_Spur`, `FrilledGorg`, `BanthaHorn`, `AteMudhornEgg`, `WoolNerf`,
  `RSW_GizkaBody`/`RSW_MassiffBody`/`RSW_FlyingAvianBody` — all absent).
- DP dropped `ADogSaidBody="LegsTail"` on 60 race defs; the survivor keeps it.
- 4 DP egg descriptions are copy-paste wrong ("A fertilized gutkurr egg" on the
  *unfertilized* def; "A fertilized kinrath egg" on the krykna egg).
- RSW_Bantha's DP copy duplicates its own `horns` tool `<li>`.
Only 29 differing reference values resolve on the DP side and not the old side.

## 5. Per-file deletion plan (366 elements)
RSW_DesertPortA_Bodies.xml   21 ->  5   (16 BodyDefs removed)
RSW_DesertPortA_Items.xml    56 ->  0   (file deleted)
RSW_DesertPortA_Races.xml    68 ->  0   (file deleted)
RSW_DesertPortA_Sounds.xml  114 ->  0   (file deleted)
RSW_DesertPortB_Eggs.xml     24 ->  0   (file deleted)
RSW_DesertPortB_Materials.xml 26 -> 0   (file deleted)
RSW_DesertPortB_Races.xml    60 ->  0   (file deleted)
RSW_DesertPortMisc_Races.xml 32 -> 30   (2 removed: RSW_Stoneback pair)

## 6. MERGED (not deleted) — the auditable list, 36 edits, commit 31a31e46a
### Sound references, 20 edits on 5 creatures
`RSW_Massiff`, `RSW_Urusai`, `RSW_WompRat`, `RSW_Worrt`, `RSW_Wraid` —
adult `lifeStageAges` `soundWounded/soundDeath/soundCall/soundAngry`
`Pawn_<Creature>_*` -> `RSW_Pawn_<Creature>_*`.
These are NOT vanilla sounds; the bare names exist only inside the donor
`mlie.starwarsanimalcollection`, so they die when it is retired. Each of the
five file headers already CLAIMS the RSW_ set is "wired"/"already absorbed" —
it was not. The DesertPort copy was right and the merge makes the file true to
its own header.

### wildBiomes, 16 edits on 13 creatures
`RSW_Anooba` AridShrubland .16 · `RSW_Bantha` AridShrubland .5 + Desert .5 ·
`RSW_Bolotaur` Desert .01 · `RSW_Cannok` AridShrubland .16 · `RSW_Clodhopper`
Desert .04 · `RSW_Convor` AridShrubland .04 · `RSW_Corinathoth` AridShrubland .4 ·
`RSW_Eopie` AridShrubland .8 + Desert .2 · `RSW_Iriaz` AridShrubland 1.0 +
Desert .04 · `RSW_Mudhorn` AridShrubland .8 · `RSW_Nuna` AridShrubland .4 +
Desert .01 · `RSW_Porg` AridShrubland .04 · `RSW_Vulptex` AridShrubland .08.
Additive only — no existing biome weight was changed. This is the desert port's
substantive contribution and the judgement call in this pass: it changes wild
spawn weights on the planet. Reverting it is 16 line deletions.

## 7. Three merges tried and DELIBERATELY REVERTED
- `specificMeatDef Cameloid_Meat -> RSW_Cameloid_Meat` on `RSW_Eopie`,
  `RSW_Falumpaset`, `RSW_Jamel`. **`Cameloid_Meat` is vanilla Core** and each
  file header states the reuse is deliberate ("no new resource needed"). My
  src/-only resolver gave a false "unresolved" — corrected before commit.
- `soundDeath Pawn_Gullipud_Death -> RSW_...` on `RSW_Pufferpig`. Header:
  sounds are "NOT a Mlie custom sound set, left bare (no sound port needed)".
  Vanilla, deliberate, and the other three are vanilla too.
- `Pawn_Squirrel_Call x4 -> RSW_Pawn_Mynock_*` on `RSW_Mynock`. `RSW_Mynock` is
  our OWN owner-ruled species def (SHIP_VERMIN_MOD_1). Vanilla squirrel calls
  resolve fine, so this is a design upgrade, not a dedup fix. **Recommended as
  follow-up**, not taken here.

## 8. DP content deliberately NOT merged (no silent drops)
- Donor texPaths (`swanimals/...`) — the survivors carry our own bound paths.
- `RSW_Mynock`'s whole DP copy: a different creature. Donor stats, 11-biome
  wildBiomes, `RSW_MynockBody`/`SWAnimalNamerMale` (both absent), and 1.6
  native flight (`MaxFlightTime` 30, `FlightCooldown` 10, `canFlyIntoMap`,
  `flyingAnimationFramePathPrefix swanimals/Mynock/Mynock_Flying_` x4 frames).
  🔑 Those flight frames DO NOT EXIST on disk — `Textures/swanimals/Mynock/` is
  absent — so wiring flight from the DP copy would have given a flyer with no
  art. The flight rule ("if it flies in the fiction, it flies in the game") is
  owed on the ship-vermin mynock as a separate, art-first item.
- `RSW_Bantha`'s DP copy duplicated its own `horns` tool `<li>` — a defect.
- Assorted DP drawSize/combatPower/ecoSystemWeight changes on already-authored
  defs: design changes on FOUNDRY-owned content, not dedup.

## 9. Orphans this leaves behind (flagged, NOT actioned — naming, not dedup)
`Defs/DesertPort/RSW_DesertPortA_BodyParts.xml` defines un-prefixed
`SWClaws`/`SWTailAttackTool`/`SWHornAttackTool`/`SWLeftHoof`/`SWRightHoof`/
`SWLeftArmClawAttackTool`/`SWRightArmClawAttackTool`; only the deleted DP copies
referenced them. `RSW_DesertPortB_Bodies.xml`'s 18 `RSW_Body_*` BodyDefs and
`RSW_DesertPortA_Bodies.xml`'s surviving `Bogwing`/`Dewback`/`FlyingAvian`/
`Reek`/`RSW_Mynock` are likewise now unreferenced. Harmless (defined, unused),
but they are un-prefixed donor names inside a shipping mod.

## 10. Final verification
- `(defType, defName)` across all 160 Defs/*.xml: **0 duplicates**.
  1635 unique defs before, **1635 after** — not one defName left the mod.
- 0 of the 349 previously-duplicated names is now absent from `src/`.
- BodyDefs: 100 ThingDefs resolve to an in-mod BodyDef; **0** tools whose
  `RSW_` `linkedBodyPartsGroup` is missing from the BodyDef they point at.
- 0 dangling `RSW_` refs in body / hatcherPawn / eggFertilizedDef /
  eggUnfertilizedDef / useMeatFrom / specificMeatDef / woolDef / abilities /
  specialTrainables / canCrossBreedWith / butcherBodyPart / PawnKindDef.race.
- `validate_patch.py src/RimStarWars/SWBestiary/Defs`:
  **0 `defined more than once`**; 78 errors, ALL of them missing-art
  (77 PawnKindDef `texPath`, 1 AbilityDef `iconPath`) — pre-existing, different
  problem. 0 errors of any other class.
- `run_selftests.py`: **64/64 passed**, 2 skipped, 0 failed.
