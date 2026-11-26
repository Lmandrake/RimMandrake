# Validation holding store

Where an owner-reported look defect waits until its mod reaches preflight (Stage 2 of the Maturation Pipeline,
`design/specs/2026-11-13-maturation-pipeline.md`). Nothing here is a test, a gate or a stage; nothing here is wired into one.

## The ruling

Owner, 2026-11-12 ~9:35 PM PST (phone typos fixed, meaning unchanged; on item
`RIMMANDRAKE_PIN_OWNER_LOOK_DEFECTS_AS_NAMED_TESTS` as an `--owner-said` note):

> "Make it a rule to store these items until our validation ladder is fully defined and regenerated. Then we will ingest them properly where and how they belong."

It answers his 9:20 PM PST question whether each defect is being recorded for future testing, and replaces the earlier
rule that a defect closes only with a named check.

Owner, by card 2026-11-14 about 1:40 PM PST, "When should the held look statements go into the mods' tables?":
**"Per mod, as it advances."** A mod's held statements are placed in its table when it reaches preflight, and that
placement counts as the ingest the ruling above waited for (spec §8, decision 12).

## How an entry is added

Every defect he reports in a look is appended here when reported, at the end of the look (the Conductor's Workshop rule).
One file per look or sitting, `owner_look_defects_<date>.md`, one table row per statement. Each row must stand alone for a
reader months from now:
- his words verbatim, with the local (Pacific) date and time;
- the save or capture that shows it (a full path; say if it is not in the repo);
- the build he saw (commit sha or DLL hash; say `not recorded` rather than guess);
- the item that fixed it, if any;
- what a check would assert, and the candidate kind: offline selftest, fast in-game state read, or look only;
- whether a proof hook is needed (and its item), and what tests it today;
- never invent a missing cell: write `not recorded`.

## How an entry leaves

When its mod reaches preflight, each of its statements is placed in the mod's test table
(`design/concepts/<Mod>/version/test_table.json`, `held_statements`): on a bar's test, a scene, a selftest, or a look-only
criterion. That placement is the ingest. The row stays here as the verbatim source: each mod's preflight reads these files
and refuses the mod while any statement of its own is unplaced. A statement that names no advancing mod waits here until
its mod reaches preflight.
Ingest item: `RIMMANDRAKE_INGEST_HELD_LOOK_DEFECTS_WHEN_LADDER_REGENERATED`.

## Contents

| file | what |
|---|---|
| `owner_look_defects_2026-11-12.md` | 48 statements (56 rows) from the 2026-11-12 under-liquid pit looks |
| `owner_look_defects_2026-11-12_explosive_knockback.md` | 2 statements from his Explosive Knockback gap rulings, 2026-11-12 4:05 PM PST |
| `owner_look_defects_2026-11-13.md` | 16 statements from the 2026-11-13 morning look (5 of them approvals) |
| `owner_look_defects_2026-11-13_dig_interface.md` | 2 statements from the 2026-11-13 dig-interface look |
| `owner_look_defects_2026-11-13_evening.md` | 5 statements from the 2026-11-13 evening FlowWorks liquid look |
| `owner_look_defects_2026-11-14.md` | 13 numbered findings and 1 follow-up ruling (22 rows) from the 2026-11-14 pit-fixes look. 5 rows are approvals kept as bars |
| `flowworks_walk_20261120.md` (+ `flowworks_walk_20261120/` pictures) | 32 observations (two parts) from his FlowWorks review-map walk, 2026-11-20 morning: class, known or new, cause; what he settled, what is open, what is filed |
| `gss_walk_20261120.md` (+ `gss_walk_20261120/` pictures) | 16 observations from his Gimme Some Slack 0.1.0 walk, 2026-11-20 (the version passed by his card): class, known or new, cause; the source of the blast soot and crater; the 31 stations and what reads each; what is 0.1.1, what is next version |
| `flowworks_walk_20261125.md` | 20 statements from his FlowWorks 0.1.0 walk, 2026-11-25 evening (not passed): each with its picture, its item and the check it asks; the passes he named; his two orders that are not the mod's |
| `walk_defects_2026-11-14_graffiti.md` | 6 agent findings (not his words) from the Graffiti lived-in walk, 2026-11-14 night: an Ideo save-reference error, a raid tag on natural rock, a standing-mockery daily tax, opinion piling up over weeks, two text/picture mismatches, a harness counter |
| `src/RimMandrake/FlowWorks/northstar/owner_look_regressions.py` (+ `selftest_owner_look_regressions.py`) | built early, awaiting ingest: in-game state reads for the rows above; wired into nothing. Its selftest runs only because the nightly sweep discovers every `selftest*.py`, so it does not rot |
| `src/RimMandrake/Utils/selftest_screenshot_mode_restored.py` | built early, awaiting ingest: harness guard for the "cannot select or screenshot" defect |
| enforcement `RIMMANDRAKE_REFUSE_OWNER_DEFECT_CLOSE_WITHOUT_REGRESSION` | held, blocked on the ladder |
