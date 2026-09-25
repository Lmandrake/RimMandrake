# The Rot — RM_TheRot franchise-free cast proposal (2026-09-24)

DESIGN PROPOSAL for the owner to rule on at a bench sitting. Nothing here is applied.
Sources: `the_rot.md` (frozen sheet) · `rot_flora_fauna_names.md` · `rosters/the_rot.json` ·
`THEROT_RM_MOD_BUILD_1` (§3 split facts) · `RSW_BiomesTeamPort_Races.xml` (labels/bodies read
from the defs) · the two noncanon naming docs (style rules + Appendix C register).

## Framing

**The 12-row partition (ruled today by card).** Of the 20 `wildAnimals` rows in the Rot's def,
12 are SW-tier rows. Per the races file header (*"biomesteam.biomescaverns / biomescore /
biomespollutedlands port … Renamed BMT_ → RSW_ throughout"*) and the item's §3:

- **10 MIGRATE to `RM_`** — Biomes! Team inventions, not Star Wars IP (Q11a: the tier line is
  IP, not flavour): `RSW_PustuleHornet`, `RSW_ColonyPustuleHornet`, `RSW_PustuleHornetSpawned`,
  `RSW_PustuleHornetQueen`, `RSW_ColonyPustuleHornetQueen`, `RSW_SmogMoth`, `RSW_Thrumbungus`,
  `RSW_Yooka`, `RSW_FungalWeevil`, `RSW_FungalMantis`. All 10 live in
  `RSW_BiomesTeamPort_Races.xml`.
- **2 stay Utinni-side** — genuinely Star Wars: `Snoruuk` (donor def,
  `mlie.starwarsanimalcollection` — Q11 unambiguous) and `RSW_ShiroTrap` (canon:
  `design/RimStarWars/canon_references/shiro` exists; ported in MLIE Wave C, not in the
  BiomesTeamPort file). Both ride `UtinniPatches/Patches/WildAnimals_TheRot.xml`.

**What the free def holds after migration:** 8 `AA_` Alpha Animals rows inline (Q9 —
rennok/agaripawn, gromma/agaripod, durrok/wildpawn, mullgoth/wildpod, vorrugath/mycoid
colossus, chittik/swarmling, plus `AA_AngelMoth` and `AA_AnimaColossus`) + the 10 migrated
`RM_` creatures = **18 fauna rows**, and **all 30 wildPlants** (17 `RUT_`→`RM_` + 13 `AB_`
inline; the item measured **zero** SW plant names, confirmed — nothing to note per plant).
Only 2 of 20 fauna rows leave, and both their niches are covered inside the free set
(floor-ambush by the skerrith's dormant-ambush guardian band; generic mid-grazer by the
brogg and rennok). **No genuine niche hole opens** — see New creatures below.

**Names.** Two of the 10 already carry owner-applied, law-clean coined labels (grellik,
skerrith — `ROT_FLORA_FAUNA_VERDICTS_1`, live in the def today): KEEP. The other 8 carry
English compounds ("pustule hornet", "smog moth") or donor names ("thrumbungus", "yooka")
and are RECOINED. Where Appendix C already holds a batch-2 draft I reuse it (illoth,
brullith); I diverge from two drafts for cause, stated on the row and flagged for the owner
(zillok → canon Zillo Beast four-letter collision; yurrok → in-biome sound-collision with
the turrok shelf). No goo/gel-bodied creature exists among the 10 (each body read from the
def), so the Slime monosyllable law binds nothing here.

## Migration table

Commonalities are the roster's; bodySize read from the races file. "Goo?" = slime/goo/gel
body per the def's own body + description (Slime law trigger).

| current RSW_ defName | current label | Goo? | verdict | proposed RM_ defName + label | syl | rationale |
|---|---|---|---|---|---|---|
| `RSW_PustuleHornet` (0.5, bs 0.32) | pustule hornet | no (chitin wasp) | RECOIN | `RM_Thozzik` — **thozzik** | 2 | English compound. Batch-2 draft *zillok* opens "zill-" = canon **Zillo** Beast — rule 2/four-letter-stem violation, swapped per that doc's own swap practice |
| `RSW_ColonyPustuleHornet` (0.5, bs 0.32) | pustule hornet | no | RECOIN | `RM_ThozzikColony` — **thozzik** | 2 | Same species, hive-loyal variety; shares the label as the donor did |
| `RSW_PustuleHornetSpawned` (0.2, bs 0.32) | pustule hornet | no | RECOIN | `RM_ThozzikSpawned` — **thozzik** | 2 | Queen-spawned form, same label |
| `RSW_PustuleHornetQueen` (0.3, bs 1) | pustule queen | no | RECOIN | `RM_ThozzikQueen` — **thozzik queen** | 2+1 | Variant shape (rule 4): plain English stage word on the coined stem |
| `RSW_ColonyPustuleHornetQueen` (0.2, bs 1) | pustule queen | no | RECOIN | `RM_ThozzikColonyQueen` — **thozzik queen** | 2+1 | As above |
| `RSW_SmogMoth` (0.5, bs 0.77) | smog moth | no (moth) | RECOIN | `RM_Illoth` — **illoth** | 2 | English compound. Batch-2 draft reused unchanged — no collision found (opening "illo-" unique planet-wide) |
| `RSW_Thrumbungus` (0.5, bs 4) | thrumbungus | no (fungal amalgam biped, hide — not gel) | RECOIN | `RM_Brullith` — **brullith** | 2 | Donor name (and reads thrumbo+fungus). Batch-2 draft reused; "brul-" distinct from brellik/brommok/brossak |
| `RSW_Yooka` (0.5, bs 2.1) | yooka | no (hunchbacked mammal) | RECOIN | `RM_Brogg` — **brogg** | 1 | Donor's coinage → recoin per this sitting's ruling. Batch-2 offer *yurrok* is one letter off the Rot's own **turrok shelf** (same biome — real confusion) and the set has zero monosyllables against today's syllable-variety ruling; brogg fixes both |
| `RSW_FungalWeevil` (0.4, bs 0.5) | grellik | no (beetle carrying fungus) | KEEP | `RM_Grellik` — **grellik** | 2 | Already owner-applied coined name, law-clean; defName follows the label at migration |
| `RSW_FungalMantis` (0.15, bs 2.0) | skerrith | no (chitin mantis, fungal carapace) | KEEP | `RM_Skerrith` — **skerrith** | 2 | Already owner-applied coined name, law-clean |

Stays Utinni-side, unchanged here: `Snoruuk` (0.5) and `RSW_ShiroTrap` (0.5) — patch rows in
`WildAnimals_TheRot.xml`, `MayRequire` per row.

## New creatures

**None proposed.** After migration the free set is 18 rows with the pyramid intact —
small/vermin: chittik, grellik, thozzik ×3 + 2 queens, illoth, mollith (angel moth) ·
mid: rennok, durrok, brogg · large: gromma, mullgoth, brullith · giant: vorrugath,
kerrugoth (anima colossus) · guardian-ambush: skerrith. The two exiled rows leave no hole:
the shiro trap's floor-ambush niche is held by the skerrith (roster band "guardian",
dormant-ambush), and the snoruuk was a plain 0.5-commonality import with no distinct band.
Ban 2 (hybrid-or-out) also makes casual invention here expensive — a new resident must be a
fungus/animal hybrid — and 18 rows already exceeds every neighbouring biome's fauna count.
The mod is rich enough to stand alone without minting.

## Names-checked table

Bar: both naming docs incl. Appendix C, every roster register read this pass, the Rot's own
flora/fauna name set, Lantern Deeps set, four-letter-opening-stem rule, SW canon to my
knowledge (memory only — no web check this pass, so canon column carries UNCERTAIN where not
already ruled).

| name | 4-letter stem | vs naming docs / registers | vs the Rot's own set | vs SW canon |
|---|---|---|---|---|
| thozzik | thoz- | unique (thollum thol-, thoffra thof-, thummorak thum-) | clear | UNCERTAIN — no known match; verify |
| illoth | illo- | unique (ithessa ithe-, ippok ippo-); -lloth ending shared with mollith/brullith is endings, not stems | clear | UNCERTAIN — no known match |
| brullith | brul- | unique; NOTE sound-near brellik (Lantern Deeps) — passes the stem rule, flagged for the ear | clear | UNCERTAIN — no known match |
| brogg | brog- | unique (brommok brom-, brossak bros-, brekkug brek-, brullith brul-, bhoruk bhor-) | clear | UNCERTAIN — no known canon Brogg, but a short name like this deserves the Wookieepedia search pass |
| grellik | grel- | already in register (owner-applied); brellik brel- distinct | clear | already ruled |
| skerrith | sker- | already in register (owner-applied); skorra/skondu/skixxet distinct | clear | already ruled |
| thozzik queen / — variants | — | rule 4 variant shape, no new stem | — | — |

Rejected on check (why the drafts were not reused blindly): **zillok** — "zill-" = canon
Zillo Beast (Clone Wars), one consonant off a famous canon creature; **yurrok** — one letter
off the Rot's own turrok shelf, and "aurr-"/"urr-" neighbours (aurrok, urrixa) crowd it.

## Syllable distribution

Final free-mod fauna set, 14 distinct base names: **1-syllable: 1** (brogg) ·
**2-syllable: 11** (rennok, gromma, chittik, durrok, mullgoth, mollith, thozzik, illoth,
brullith, grellik, skerrith) · **3-syllable: 2** (vorrugath, kerrugoth). Still 2-heavy
against the 2026-09-24 variety ruling (~1/5 · 1/2 · 1/4), but 10 of the 11 two-syllable
names are already owner-ruled/applied and are not re-opened by this proposal; only the four
free coins could move, and one was spent on the monosyllable.

## Rulings — decisions taken by question card, 2026-09-24 (BENCH sitting)

- **Migration table RATIFIED in full**: 10 ports become RM_ defs with the names above —
  thozzik family (zillok swapped over the measured Zillo Beast collision), illoth, brullith,
  grellik, skerrith kept.
- **Yooka → brogg.** yurrok declined (one letter off the turrok shelf); yooka declined.
- **Spore allergy: port our own.** Two RM_ HediffDefs of our own replace the
  `AB_Disease_SporesAllergy` pair so the free mod keeps its signature disease without Alpha
  Biomes — added to `THEROT_RM_MOD_BUILD_1` scope.
- **AA_AnimaColossus: the def wins.** The stale homeless-reserve eviction entry is deleted
  from `the_rot.json` (done same sitting); the wired import row stands.
- All four new coins passed the mechanical gates same sitting: `check_pseudo_sw_name.py` 4/4,
  naming-doc collision zero (illoth/brullith hits are their own batch-2 rows), Wookieepedia
  probe zero real occurrences (brogg's one search hit disproven at page level; instrument
  control-proven). Names are clear to write into defs.
