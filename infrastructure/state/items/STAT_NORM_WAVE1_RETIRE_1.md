# STAT_NORM_WAVE1_RETIRE_1

Owner, verbatim (2026-09-09), after reviewing `STAT_NORMALIZATION_AUDIT_1`'s
census: "retire wave 1 items. We don't need those. The animal plant rework will
work on the rest later when we revisit."

## spec

Retire these 13 mods, per `STAT_NORMALIZATION_AUDIT_1`'s Wave 1 (measured
zero-content, zero/near-zero save presence — see
`design/Jawa/mods/stat_normalization_audit_2026-09-09.md` §4 and the
save-cross-reference table in §3 for the exact numbers this claim rests on):

- `fluxilis.germanquality`
- `zylle.moredangerousgame`
- `farhanfair.warcaskettweakspatch`
- `aelanna.fistnerf`
- `mosi.rebalancedancientjunk`
- `farxmai2.vanilladeconstructablevehicles`
- `coldcrow.betterkibble`
- `doomdrvk.unlimitednuzzles`
- `victor.buymore`
- `mlie.harvestwhenbutchering`
- `archie.turrettargetpatch`
- `samael.npcmechsandanimals`
- `mlie.choosebiomecommonality`

**Do NOT add `summersausages2ttv.techlevelenforcement`** — the census flagged
it as a possible 14th candidate but explicitly left it unresolved (it gates
equipment availability, not values — a design question, not a numbers one).
Out of scope for this item.

## 🔴 Do not touch ModsConfig until the full list is confirmed stable

At the time this item was filed, the live `ModsConfig.xml` held a temporary
~11-mod crash-recovery list (another agent's in-flight work restoring after
tonight's save-compat reboots), NOT the owner's real ~587-590 mod campaign
list. Editing it now would either collide with that restoration or edit the
wrong list entirely.

1. Check `python3 src/RimMandrake/rimflow/cli.py bridge who` and the live
   `ModsConfig.xml`'s `<li>` count before doing anything. If it is not back to
   something in the ~580-600 range, do NOT proceed — leave this item `doing`
   with a note and stop. Do not force or accelerate the restoration; that is
   someone else's in-flight work.
2. Once the full list is confirmed stable (and ideally the game itself
   confirmed UP via `harvest_log.py` succeeding, not just "bridge answers" —
   see tonight's idle-menu-vs-real-load lesson): back up the live
   `ModsConfig.xml` to `infrastructure/state/modlists/` before touching it,
   per this repo's established donor-retirement discipline
   (`WEAPONS_DONOR_RETIREMENT_1`, tonight's `STARWARS_DONOR_SUNSET_1` Wave 4).

## 🔴 Re-verify before executing — do not blindly trust the census numbers

Tonight, two separate donor retirements each passed a thorough dependency
check and still broke the live save. Before removing any of the 13:
1. Re-run a fresh whole-active-mod-list grep for each of the 13 packageIds
   against the NOW-current full list (not the 13:38 snapshot the census used —
   confirm nothing changed in the interim).
2. Re-check the campaign save (`rimworld-savegame` skill, offline) for each of
   the 13 packageIds' own defNames — confirm the census's "0 placed instances"
   finding still holds against the CURRENT save file, not an assumption that
   nothing changed.
3. If any of the 13 turns up a dependent or save reference the census missed,
   pull that one mod out of this wave and proceed with the rest — do not let
   one surprise block the whole wave, and do not guess past a real finding.

## FRESH RE-CHECK RUN (FOUNDRY, 2026-09-09 ~14:45-14:58) — all 13 PASS

Both re-checks this item demands were run from scratch, not read off the census.

**Instrument note**: the live `ModsConfig.xml` still held the **6-mod**
crash-recovery list (mtime 13:50:41, unchanged for 68 min) and
`harvest_log.py` **REFUSED** ("the def dump was written by a 590-mod run but
ModsConfig has 6"), so the checks ran against
`infrastructure/state/modlists/ModsConfig_before_droid_donor_fix_2026-09-09.xml`
(**587 activeMods**) and the live save
`CANONICAL_ASHKARR_2026-09-09.rws` (24,933,845 bytes, `<modIds>` = 590).
All 13 packageIds confirmed **PRESENT** in that 587-list.

### (a) Dependency sweep — 44,197 XML/txt/json files across all 587 active mods

Every active mod's own folder walked (1,333 installed indexed, **0 of 587
active ids unresolved**) and searched for all 13 packageIds in any form —
`modDependencies`, `loadAfter`/`loadBefore`, `forceLoadAfter`,
`incompatibleWith`, `MayRequire`, `PatchOperationFindMod`, plain strings.

**Exactly 2 external references, both in our OWN mods, both mechanically inert:**

| referrer | file | what it is | verdict |
|---|---|---|---|
| `mandrake.rsw.armoury` | `Patches/Warcasket_BuildPathCut.xml` line 113 | `farhanfair.warcaskettweakspatch` appears **only inside an XML comment** — a load-order position table (`485 farhanfair...`). The file's real guard is `PatchOperationFindMod` on VFE Pirates, and every op is additionally `PatchOperationConditional`. Zero mechanical dependency | ✅ inert |
| `mandrake.rut.researchretag` | `About/About.xml` `<forceLoadAfter>` | `<li>coldcrow.betterkibble</li>`. `forceLoadAfter` is an ordering hint, not a dependency — an absent id is ignored by the resolver. Its actual patches on `KibbleDispenser` (`RUT_ResearchRetag.xml` 1867-1893, `RUT_ResearchTabAssign.xml` 241-255) are **all wrapped in `PatchOperationConditional` on the def's existence**, so they become silent no-ops rather than patch failures | ✅ inert |

The other 11 packageIds: **0 external references of any kind.**

### (b) Save cross-reference — CURRENT save, per mod, own defNames only

Each candidate's own `<defName>`s harvested from its non-patch XML (files with
no `PatchOperation`), then counted in the save as placed `<def>NAME</def>`
thing instances and separately as bare reference tokens.

| mod | own defs | placed `<def>` | ref-only | in save `<modIds>` |
|---|---|---|---|---|
| `fluxilis.germanquality` | 0 | **0** | 0 | yes |
| `zylle.moredangerousgame` | 0 | **0** | 0 | yes |
| `farhanfair.warcaskettweakspatch` | 0 | **0** | 0 | yes |
| `aelanna.fistnerf` | 2 | **0** | 0 | yes |
| `mosi.rebalancedancientjunk` | 0 | **0** | 0 | yes |
| `farxmai2.vanilladeconstructablevehicles` | 0 | **0** | 0 | yes |
| `coldcrow.betterkibble` | 4 | **0** | 3 | yes |
| `doomdrvk.unlimitednuzzles` | 0 | **0** | 0 | yes |
| `victor.buymore` | 1 | **0** | 0 | yes |
| `mlie.harvestwhenbutchering` | 0 | **0** | 0 | yes |
| `archie.turrettargetpatch` | 0 | **0** | 0 | yes |
| `samael.npcmechsandanimals` | 0 | **0** | 0 | yes |
| `mlie.choosebiomecommonality` | 0 | **0** | 0 | yes |

**Zero placed instances across all 13.** The only non-zero cell is
`coldcrow.betterkibble`'s `KibbleDispenser`, 3 reference-only tokens, all
inspected in context and all bookkeeping rosters: the finished/available
research-project list, a `<thingDef>` key in the price-history record table,
and a build-designator roster entry. `Blueprint_/Frame_/Techprint_/
_ReplaceStuff` variants sit in the same roster lists. This is exactly the
reference-residue class `STARWARS_DONOR_SUNSET_1` Wave 4 already accepted —
Scribe drops unknown roster entries with a `Could not load reference to`
warning and continues. **No `<def>KibbleDispenser</def>` thing exists on the
map.** (The census recorded 1 ref token; 3 is a token-counting method
difference, not a new finding.)

**Result: nothing pulled. All 13 remain in the wave.**

⚠️ **Follow-on tidy owed, NOT a blocker**: once `coldcrow.betterkibble` is
gone, `ResearchRetag`'s `<li>coldcrow.betterkibble</li>` and its
`KibbleDispenser` operation blocks are dead weight. `build_retag_patches.py`
regenerates that set from the manifest — leave it to the next regeneration
rather than hand-editing a generated artifact mid-wave.

## verify
All 13 `<li>` entries removed from the live `ModsConfig.xml` by exact-tag
match, confirmed absent by re-grep; backup file exists; the fresh dependency +
save re-checks in this item's own text were actually run (not skipped because
the census already did it once).

## criteria
13 mods retired from the live ModsConfig, zero new dependents/save-references
found beyond what the census already characterized as zero. Cold-load proof
is explicitly OWED to the next natural load — do not trigger a dedicated
restart for this alone; today's game has already restarted three times.
