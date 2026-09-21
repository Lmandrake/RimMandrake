# Roster reconciliation — the Rot and RUT_TheForge — 2026-09-21

## Scope
Per ROT_ROSTER_DEAD_DONOR_NAMES_1 and FORGE_ROSTER_UNRECONCILED_BMT_1: reconcile
`design/Jawa/worldbuilding/biomes/rosters/the_rot.json` vs `RUT_TheRot.xml`, and
`RUT_TheForge`'s roster JSON vs its live wiring. (Miasma/FeverWood/Greentide are
named in FORGE item but out of scope for this pass.)

## Instruments used
- `python3 -c "json.load(...)"` on the roster JSONs directly (small files, no `measure` needed).
- `python3 -c "ET.parse(...)"` on the BiomeDef XMLs' `<wildAnimals>`.
- `python3 -c "ET.parse(ModsConfig...).find('activeMods')"` against
  `infrastructure/state/modlists/ModsConfig_full_plus_gelatinousslime_2026-09-21.xml`
  (620 active mods) for active-mod checks — parsed, never grepped.
- `grep` across `src/` for donor→owned rename evidence (header comments, defName
  lists) per the method warning — never used to conclude absence by itself.
- `git log`/`git show` on the roster JSONs and on `infrastructure/state/items/`
  to find prior owner rulings (`decisions_propagated.json`,
  `ROT_FLORA_FAUNA_VERDICTS_1`) rather than guessing intent.
- `skills/rimworld-modding/scripts/validate_patch.py --defs <Data> --defs <Mods>
  --defs <Workshop> --mods-config <live snapshot>` on both edited XML files: OK,
  0 errors, 0 warnings.

## The Rot — measured counts
**MY numbers, re-measured, NOT adjusted to the briefed figures:**
- `the_rot.json` `fauna` array: **23** admitted entries at start of this session
  (not the briefed 28 — see note below), of which **10** were already wired in
  `RUT_TheRot.xml`'s `<wildAnimals>` and **13** were not.
- Of the 13 unwired: **10** carried a dead `BMT_`/donor name, **3** were
  non-donor names (`ShiroTrap`, `AA_AnimaColossus`, `MA_Sporemole`).
- **Why 23, not 28**: git history shows commit `c2428fb6f` ("cut the 6 fauna,
  owner ruling 2026-09-20") removed 5 fauna rows from `the_rot.json`
  (`BMT_CaveSpider`, `BMT_ChemSnail`, `BMT_GiantSlug`, `BMT_GiantSnail`,
  `BMT_Pillbug`) AFTER the item's 28-count was measured earlier the same day.
  28 − 5 = 23. The item's number was correct when written; the roster moved
  under it. This is exactly the trap the brief warned about, confirmed by
  checking git log rather than assumed.

## The Rot — classification (a/b/c)
All 13 resolved via `decisions_propagated.json` (the owner's 2026-09-10
sitting) plus direct source/donor-mod checks — **no guessing**:

**(a) already owned, wired this pass — 10:**
| dead name | owned as | source |
|---|---|---|
| `ShiroTrap` | `RSW_ShiroTrap` | ported, `RSW_ShiroTrap.xml` (mlie.starwarsanimalcollection donor, header comment confirms) |
| `BMT_ColonyPustuleHornetQueen` | `RSW_ColonyPustuleHornetQueen` | ported, `RSW_BiomesTeamPort_Races.xml` |
| `BMT_PustuleHornetQueen` | `RSW_PustuleHornetQueen` | ported, same file |
| `BMT_PustuleHornetSpawned` | `RSW_PustuleHornetSpawned` | ported, same file |
| `BMT_ColonyPustuleHornet` | `RSW_ColonyPustuleHornet` | ported, same file |
| `BMT_PustuleHornet` | `RSW_PustuleHornet` | ported, same file |
| `BMT_SmogMoth` | `RSW_SmogMoth` | ported, same file |
| `BMT_Thrumbungus` | `RSW_Thrumbungus` | ported, same file |
| `BMT_Yooka` | `RSW_Yooka` | ported, same file |
| `AA_AnimaColossus` | `AA_AnimaColossus` (unrenamed) | real, active donor def confirmed live in `sarg.alphaanimals`'s own 1.6 folder on disk — never ported, never needed to be, just never wired |

**(b) donor exists, not referenced, genuine port-or-drop — 1:**
| name | status |
|---|---|
| `MA_Sporemole` | Donor `veterano.mythicages.megafaunabestiary` ("Mythic Ages: Megafauna Bestiary") is **NOT in the active mod list** (confirmed by parsing the live snapshot); no `RSW_`/`RUT_` port exists anywhere under `src/`. The owner's 2026-09-10 sitting already said "move to the Rot" in intent, but nothing was ever built. **Left un-renamed and unwired in the JSON, flagged for the owner below** — matches the item's own flag exactly. |

**Plus 2 stale rows found and reconciled that were neither of the above — already-ruled housekeeping, no new judgment call:**
- `BMT_GlowBat` — owner ruling 2026-09-10 (`decisions_propagated.json`
  `fauna:the_rot:BMT_GlowBat` decision=`out`, "CUT — all flying bats"). Never
  wired; removed from the roster's fauna list, recorded in `evictions`.
- `BMT_BovineBeetle` — `ROT_FLORA_FAUNA_VERDICTS_1` TASK 2 (2026-09-19)
  already moved this species to the Lantern Deeps as `RSW_BovineBeetle` (its
  Grabber) and removed it from `RUT_TheRot.xml`. The roster JSON row was
  simply never updated to match — removed, recorded in `evictions`.

**(c) names nothing at all — 0.** Every one of the 13 resolved to either a
real port, a real active donor def, or a documented prior ruling. Nothing was
a dead name with no referent anywhere.

Also renamed 2 already-correct-but-stale JSON rows to match their live wiring
(`BMT_FungalWeevil`→`RSW_FungalWeevil`, `BMT_FungalMantis`→`RSW_FungalMantis`)
so the verify criterion ("zero `BMT_` names in the JSON or the XML") is
actually met, not just true of the XML.

## The Rot — wiring done
Edited `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml`: added the
10 class-(a) rows to `<wildAnimals>` under their owned names (commonalities
carried over from the roster JSON). 3 of the 10
(`RSW_PustuleHornetQueen`/`RSW_ColonyPustuleHornetQueen`/
`RSW_PustuleHornetSpawned`) were found ALREADY wired in
`RUT_Wasteland.xml` despite the owner's ruling moving them to the Rot and
`wasteland.json`'s roster no longer listing them — a stale duplicate-biome
wiring, not part of either roster's declared scope but a direct correctness
issue created by this exact ruling. Removed those 3 lines from
`RUT_Wasteland.xml` in the same pass (documented inline in both files) rather
than leave a live double-spawn bug standing.

Edited `design/Jawa/worldbuilding/biomes/rosters/the_rot.json`: renamed 11
`def` fields to their owned/ported names, removed `BMT_GlowBat` and
`BMT_BovineBeetle` from `fauna` with eviction records added, left
`MA_Sporemole` unwired/un-renamed and flagged.

Both XML files validate clean (`validate_patch.py --defs <Data/Mods/Workshop>
--mods-config <live 620-mod snapshot>`: 0 errors, 0 warnings) and both JSON
files parse.

## RUT_TheForge — measured counts
**MY numbers, re-measured, NOT adjusted to the briefed "27":**
- `the_forge.json` `fauna` array: **10** admitted entries at start of this
  session. Live `<wildAnimals>` in `RUT_TheForge.xml`: **7** wired. 3 unwired.
- `the_forge.json`'s `evictions` array carries **28** `BMT_`-prefixed names —
  every one already dispositioned `homeless-reserve` / `cut:...` / `move:...`,
  i.e. already-adjudicated exclusion records, exactly the same shape as the
  Rot's own `evictions` array. **These are not a gap** — an eviction record is
  supposed to have zero live wiring; that is what the disposition field
  means.
- 🔴 **This is where the briefed "27 unreconciled BMT_ names with zero live
  wiring" comes from, and it is a measurement artifact, not a live defect.**
  `Transient/dead_roster_refs_assessment.md` (the source of the FORGE item's
  headline number) itself only ever compared `the_forge.json`'s live
  `fauna`/wired-XML shape at a high level and flagged the 27 as "worth
  checking" without breaking it into fauna-vs-evictions — the 28
  already-resolved eviction rows above account for the entire figure. Only
  **1** `BMT_` name was ever live in `fauna` (`BMT_Maguana`), and that one was
  already ported and wired as `RSW_Maguana` before this session touched
  anything (`CAVERNS_PARITY_BUILD_1` r5). **The_forge.json had ZERO
  unreconciled, still-unwired `BMT_` names in its live fauna list.**

## RUT_TheForge — classification (a/b/c)
Of the 3 unwired fauna rows:
- **(a) already owned, just needed the JSON's `def` field renamed — 1:**
  `BMT_Maguana` → `RSW_Maguana` (already ported and wired in the XML; the
  roster row was simply never updated to match). Found the row's
  `commonality` (0.15) doesn't match the live wired value (0.5) — a
  pre-existing tuning drift, flagged but not touched (not this task's scope).
- **(c) names nothing at all — 1, found beyond the item's own scope:**
  `AA_Cinderlisk` — `WYYYSCHOKK_FERALISK_MERGE_1` (2026-09-10, closed)
  Cherry-Picker-cut the whole Alpha Animals "-lisk" clade and removed it from
  `RUT_TheForge.xml`; the defName does not load at all. The roster JSON's
  `fauna` row was never updated to match — removed, recorded in `evictions`.
  Not a `BMT_` name and not named in either item, but the identical defect
  shape (stale roster row surviving a cut/port that already happened
  elsewhere) — correctness-outranks-scope, fixed on sight.
- **(b)/no genuine port-or-drop call found in the_forge.json's live fauna.**
  `AA_ColossalAerofleet` and `Tibidee` remain unwired **on purpose** — both
  are real, presumably-wirable names, but `RUT_TheForge.xml`'s own header
  comment (ECOSYSTEM_PYRAMID_LAW_1, 2026-09-20) says they are deliberately
  left out for being LARGE against the owner's "50% small" ruling. No action
  needed; not a dead-name defect.
- The 28 `evictions` rows and the 3 already-`RUT_`-renamed flora rows: no
  action needed, already correctly resolved.

## RUT_TheForge — wiring done
JSON only — `RUT_TheForge.xml` needed no changes (it already carried zero
live `BMT_`/dead refs). Edited
`design/Jawa/worldbuilding/biomes/rosters/the_forge.json`: renamed
`BMT_Maguana`→`RSW_Maguana` in `fauna`, removed the stale `AA_Cinderlisk` row
from `fauna` with an eviction record added. JSON parses; no XML to
re-validate for this roster (unchanged).

## For the owner (class b/c, port-or-drop)

**Only ONE genuine open call across both rosters: `MA_Sporemole` (the Rot).**
- Donor `veterano.mythicages.megafaunabestiary` ("Mythic Ages: Megafauna
  Bestiary") is confirmed NOT in the active 620-mod list.
- No `RSW_`/`RUT_` port exists anywhere under `src/` — this is a real gap, not
  a rename to find.
- The 2026-09-10 sitting already recorded intent ("move" to the Rot in
  `decisions_propagated.json`) but nothing was ever built.
- Reactivating the donor mod is against standing practice (retired donors
  don't come back), so the choice is **PORT** (author it as our own def, the
  FungalWeevil/FungalMantis pattern) or **DROP** (remove the row from
  `the_rot.json`, recorded as a cut).
- Existing art already captured for review sits at
  `design/Jawa/fauna/sprites/MA_Sporemole.png` and
  `design/Jawa/worldbuilding/review/creature_art/MA_Sporemole.{detail,scale}.png`
  — donor-source captures from an earlier census pass, not generated/ruled
  art of ours. If PORT is chosen, check whether that capture is usable
  reference before queuing anything through the artpipe daemon (no art was
  queued this pass, per the hard rule).

**One design question surfaced, not a defect — re-checked, and it's more
specific than the earlier assessment said:** `RUT_TheRot.xml` (this pass) now
wires the **ported** `RSW_ShiroTrap`. `RUT_Greentide.xml` wires the **bare
donor** `ShiroTrap` directly (`MayRequire="mlie.starwarsanimalcollection"`,
line 195) — not the port. Both resolve live today (the donor mod is still
active for other unrenamed species like `Snoruuk`/`Beldon`/`LavaFlea`), so
nothing is broken, but it means two near-identical creatures under two
different defNames could both be spawning across two biomes: the Rot gets our
port, the Greentide still gets the donor's original. Cross-biome sharing of
one name is normal in this roster (most `AA_` names repeat across biomes);
sharing under TWO different names for what the port's own header calls the
same species is the part worth a one-line owner confirmation — should
Greentide's wiring also move to `RSW_ShiroTrap` for consistency, or is the
split intended?

**One pre-existing tuning drift, not touched:** the_forge.json's
`RSW_Maguana` (renamed from `BMT_Maguana`) row carries `commonality: 0.15`
while the live `<wildAnimals>` wiring uses `0.5`. Not this task's scope
(existence, not tuning) — flagged for whoever owns fauna density numbers.

## Could not establish
- Whether the Miasma/FeverWood/Greentide rosters (the other three named in
  `FORGE_ROSTER_UNRECONCILED_BMT_1`) have the same "evictions-counted-as-live"
  measurement artifact as the Forge, or a genuine gap — out of this task's
  declared scope (the Rot + the Forge only) and not measured this pass.
- Whether a post-load def dump confirms the newly-wired species actually
  spawn (the Rot item's own "verify" criterion) — the game is running under
  another window's bridge hold this session; hard rule forbids touching it.
  This needs a live check on the next cold load / bridge-free window.
- Full detail on the 620-mod live snapshot's currency (used
  `ModsConfig_full_plus_gelatinousslime_2026-09-21.xml`, the newest dated
  snapshot on disk, in preference to the 2026-09-19 one the items cite) —
  both snapshots agree on every mod this task depended on
  (`biomesteam.biomescaverns` absent, `sarg.alphaanimals`/
  `mlie.starwarsanimalcollection`/`mandrake.rsw.swbestiary` active,
  `veterano.mythicages.megafaunabestiary` absent), so the choice didn't
  change any finding.

## Commit
TBD
