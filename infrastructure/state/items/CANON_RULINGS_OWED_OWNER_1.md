## spec
_not recorded in the source queue_

## verify
_not recorded in the source queue_

## criteria
_not recorded in the source queue_

## notes
**Imported from `queue/HUMAN.md`. Its `state:` read, verbatim:**

ready

**filed:** BUILD, 2026-08-20, after W0–W3 of the upgrade runbook

**Nothing here blocks the build.** `infrastructure/state/canon.yml` now holds one traceable
value for every contested number, and `check_canon.py` reports **0 contradictions across all
119 design docs**. These are the questions measurement could not settle, filed with the
evidence so each is a yes/no, not an essay.

### ⭐ The one that is worth a look, not a ruling

`./src/RimMandrake/Utils/show.sh TRANSIENT_refmatch_globes.html` — Ash'karr as **three
orthographic globes** (day face, terminator, night cap) beside the two tidal-lock reference
photographs, all at the same size. This has never been rendered before; every previous view
was equirectangular, while the binding reference is a globe. **`refmatch.py` cannot be built
until you have looked**, because its five defect thresholds are calibrated against those
photographs, not chosen.

### 🔴 THREE ARE ANSWERED — 2026-08-20, in session

| ruled | outcome |
|---|---|
| **`Lake`** | ✅ **KEEP.** Confirmed, not provisional. |
| **The two cut-then-painted biomes** | ✅ **THE PAINTER WINS.** `AB_GelatinousSuperorganism` (96 tiles) and `ZBiome_Grasslands` (233) stay exactly as painted; **both cuts are REVERSED.** Written into all five docs that said otherwise. |
| **The Deepwater Compact** | ✅ **AUTHOR THE ROSTER.** Filed as `DEEPWATER_CAST_ROSTER_1` in `queue/DECIDE.md` with spec, verify and criteria. |
| **The habitable ring** | ⏸️ **Abstained, deliberately.** 34–57 and 40–57 both keep standing; canon holds 34–57 as provisional and the question stays open. |

⭐ **And the follow-up is already done rather than pending.** Rather than wait for a third
cut-versus-painted case to surface by hand, the whole cut list was diffed against the painted
biome census: of the **24 biomes on the map, exactly two** were ever cut-flagged — the two above.
**There is no third case.** `canon.yml > cut_vs_painted`.

### The seven, as filed

| # | question | the evidence | canon holds |
|---|---|---|---|
| 1 | **Habitable ring: 34–57° of arc, or 40–57°?** | 34–57 is what the code that **sited The Setdown** used, and arc 56.9 is called "the outer edge" — which only reads true against 34–57. 40–57 appears with real tile counts (2,477, of which 1,791 land) in the file whose banner points at dead measurements | 34–57, **provisionally**. ~700 tiles at stake |
| 2 | **`Lake` — confirm it stays** | Not a preference: **The Scald**, one of exactly three ruled seas, is painted `Lake` for all 312 of its tiles. Cutting the def deletes a named sea | keep |
| 3 | **`AB_GelatinousSuperorganism`** | Cut 2026-08-04, **painted on 96 tiles 2026-08-18**. The palette was never told | open |
| 4 | **`ZBiome_Grasslands`** | Same shape, found the same day: REMOVE on 2026-08-14, **painted on 233 tiles**. ⚠️ Two of these in one day says the cut list and the painter have never been diffed as a pair — worth doing once rather than finding a third by hand | open |
| 5 | **Pirate faction defName** | `meta.json` says `AM_EnemyPirate`; the painter and the settlements CSV both say `Pirate`, with 4 settlements. One of them is not a def the game can resolve, and that is a load error, not a cosmetic difference. ⚠️ CHECK's to settle — it needs the save read against the live def set | open |
| 6 | **The Deepwater Compact has no cast roster** | Eleven `INHABITED_CAST_*.md` files against twelve dossiers. It is not a marginal faction — its faith is **the Balance**, the water politics every other faction reacts to | open |
| 7 | **A 701-line doc's subject biome is on the cut list** (`SAVANNA_PREMISE_RESOLVE_1`) | Either the doc is dead or the cut is | open |

### 🔴 One thing was already wrong and is now fixed — you should know it existed

`setup_checklist.md` §2 still told you to author **"The Articles of Passage"**, memes
**Nomad + Tunneler**. What shipped is **"The Salvation"** on `AM_Structure_Scavenger` ·
`Trader` · `VME_Scrapper` · `VME_Trader` · `VME_Nomad`. **An ideoligion is fixed at world
creation**, so working that line live would have baked the wrong religion in permanently.
Corrected in place with the shipped values beside it. The in-fiction name *"Keepers of the
Second Hand"* survived — it is in the shipped `<ideoDescription>` verbatim.

⚠️ **Still genuinely open there:** `ideoligion/APPROVED.md:119-120` recommends **dropping
`VME_Nomad`** for `Nomadic_Preferred`, and `JawaTribes.xml` still carries `VME_Nomad`. That
recommendation has never been ruled on.
