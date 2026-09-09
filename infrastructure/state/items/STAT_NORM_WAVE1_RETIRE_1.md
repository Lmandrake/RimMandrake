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
