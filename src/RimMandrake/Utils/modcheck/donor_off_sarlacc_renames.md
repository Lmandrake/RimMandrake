# Phase 0: Sarlacc landmark port, old -> new def names (for step P6, the save edit)

Owner, 2026-10-15, by question card ("What should happen to the donor's Sarlacc landmarks" -> "Port both landmarks").
New defs: `src/RimStarWars/SWBestiary/Defs/DonorPackPort/RSW_DonorPack_Sarlacc.xml` (packageId `mandrake.rsw.swbestiary`).
**No save was edited.** P6 does that.

## The table

| def type | donor (`mlie.starwarsanimalcollection`) | ours |
|---|---|---|
| LandmarkDef | `sw_Sarlacc` | `RSW_Sarlacc` |
| LandmarkDef | `sw_DeadSarlacc` | `RSW_DeadSarlacc` |
| TileMutatorDef | `sw_SarlaccLair` | `RSW_SarlaccLair` |
| TileMutatorDef | `sw_DeadSarlaccCave` | `RSW_DeadSarlaccCave` |
| GenStepDef | `sw_SarlaccPit` | `RSW_GenStep_SarlaccPit` |
| GenStepDef | `sw_DeadSarlaccPit` | `RSW_GenStep_DeadSarlaccPit` |
| ThingDef (building, 9x6 work table) | `SarlaccPit` | `RSW_SarlaccPit` |
| ThingDef (building, 12x9 MapPortal) | `DeadSarlacc` | `RSW_DeadSarlaccHusk` (deliberately not `RSW_DeadSarlacc`, which is the LandmarkDef) |
| ThingDef (blueprint, engine-made) | `Blueprint_Install_SarlaccPit` | `Blueprint_Install_RSW_SarlaccPit` |
| ThingDef (blueprint, engine-made) | `Blueprint_Install_DeadSarlacc` | `Blueprint_Install_RSW_DeadSarlaccHusk` |
| ThingDef (item) | `SarlacciSpore` | `RSW_SarlacciSpore` |
| MapGeneratorDef | `SarlaccCavity` | `RSW_SarlaccCavity` |
| RecipeDef | `FeedCorpse` | `RSW_FeedCorpseToSarlacc` |
| WorkGiverDef | `DoBillsFeedSarlacc` | `RSW_DoBillsFeedSarlacc` |
| RulePackDef | `SWNamerLandmark_Sarlacc` | `RSW_NamerLandmark_Sarlacc` |

## What the canonical save holds (measured 2026-10-15)

`CANONICAL_ASHKARR_START_2026-09-12.rws`, grepped token by token (`Human` as `<def>Human</def>` = 75, so the grep can see):

| token | count | where | P6 action |
|---|---:|---|---|
| `<def>sw_Sarlacc</def>` | 8 | world landmarks (`<li><def>..</def><name>..</name></li>`) | rename to `RSW_Sarlacc` |
| `<def>sw_DeadSarlacc</def>` | 7 | world landmarks | rename to `RSW_DeadSarlacc` |
| `DoBillsFeedSarlacc` | 9 | per-pawn `<Workgiver>` priority rows | rename to `RSW_DoBillsFeedSarlacc` (or let them drop) |
| `SarlacciSpore` | 3 | game-wide def lists / records (`<li>`, `<thingDef>`) beside every other donor ThingDef | rename to `RSW_SarlacciSpore` (or let them drop) |
| `SarlaccPit`, `DeadSarlacc` | 2 each | the same game-wide `<li>` / `<thingDef>` lists | rename per the table |
| `Blueprint_Install_SarlaccPit`, `Blueprint_Install_DeadSarlacc` | 1 each | the same game-wide list | rename per the table |
| `sw_SarlaccLair`, `sw_DeadSarlaccCave`, `SarlaccCavity` | 0 | — | nothing |

No spawned sarlacc building and no pocket map exists in the save (no `<def>SarlaccPit</def>` / `<def>DeadSarlacc</def>` things).
The game-wide list rows are the kind every retired donor ThingDef leaves (`RancorSkull`, `KraytPearl`, ... sit beside them); P6's
generic donor sweep should treat them the same way.

## Tools that now expect the RSW_ names

`ashkarr_landmarks.py` (places `RSW_DeadSarlacc`), `ashkarr_populate.py` (looks for `RSW_Sarlacc`), `landmark_art.py` (spec keys),
`structure_roster_lint.py` (anchor `RSW_SarlaccLair`). Run against the current save they will not find the landmarks until P6
renames them. `worldmap_prefill.py` and `worldmap_effects.py` carry BOTH spellings until P6.
