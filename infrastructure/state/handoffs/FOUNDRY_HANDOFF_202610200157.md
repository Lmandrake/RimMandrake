# FOUNDRY_HANDOFF_202610200157 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610191447`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

Option D is the owner's chosen path (card 2026-10-19): retire mods through validated candidate lists on scratch maps, keep the authoritative world untouched, and remake the world ONCE as a DEVELOPMENT world (may be repainted later) when the written checklist in `design/RimMandrake/world_remake_2026-10-19/06_remake_runbook.md` passes. Read `PLAN.md` there first; 01-07 are its evidence. The irreversible faction pass must not be spent until the gates pass, and no rehearsal may be a redraft-to-test (2026-08-21 ruling) without his word.

## What the owner should see

- Wave 1 ran: 39 mods retired, live list now 498 (was 536), clean cold load, `RESULTS.md` in `Transient/live_testing_2026-10-19f/`. The game was left UP on `RM_TestSite_calm_v1_AREAFIX2`, paused.
- `07_deeper_drops.md` proposes DEV 117 / TEST 205 / AUTHORING 225 / SHIP 329 profiles; 157 mods leave every profile. NOT yet ruled on.
- Rhossak: his binding mechanic had NO spec in our files, only the 2026-10-09 sheet descriptions; the defaults I took (thornwood only, 10 cells, 3 awake within 4 cells for 24 h, 10-day cooldown, galled drops 40 meat per 2 days) need his eye.
- Eight vanilla roster rows were cut on his card; Forge now has 4 plants (RM) and 4 animals (RUT); ticket `FORGE_SNAILHOLE_FILL_EMPTY_SHELL_LEFT_BEHIND` needs a new creature.
- 04 scope-cuts section 7 has 9 questions for him; the weather descope covered only SENSING, the Ashkarr weather mod is on.
- His 'Umbra is total darkness' vs the sheet 'starlit and curtain-lit' for RUT_FuelSnows tiles: ask which he wants.

## What is half-done, and where it stops

- `DONOR_FOUR_RETIRE_JUST_GET_IT_DONE` — A2 passed, A3 partial (MineralsFramework GenStep NRE on every map, another mod's); NEXT: ask the owner whether A3 may pass with that NRE, then do A5 (his unticking and save adoption).
- `WAVE1_MODLIST_RETIRE_37_IN_ONE_LOAD` — validated; owes canonical start-save edit and run-sheet acceptance checks; NEXT: do them at the world sitting, with his word on touching the save.
- `TINKLEGRASS_STALE_UTINNIPATCHES_COPY` — UtinniPatches redeployed after the load, so RM_TinkleGrass error persists until the next game start; NEXT: restart the game once, bundled with the rhossak and Cauldron rows below.
- `RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD` — built, offline checks pass, A1-A7 live rows owed (A5/A6 not yet scripted); NEXT: after deploy, run the Cauldron script's three rhossak rows on RM_TestSite_cauldron_v1_AREAFIX2.
- `CAULDRON_MECHANICS_BUILD_1` — 76 PASS/1 FAIL/6 UNMEASURED; A5 works_refines_condensate FAIL ('Power needed 350 W', maybe harness power setup); NEXT: probe the Filter-Works power setup on the Cauldron site before reading it as a mod bug.
- `CONTAGION_MECHANICS_BUILD_1` — A1 dose row now passes, native_dives is fixture, A6 Coalescence absorb unresolved; NEXT: probe CanReach on the survivors' cells before the arm ends (suspect silent continue in Absorb ~181-195) only if Contagion survives the scope-cut ruling.
- `ASHKARR_WEATHER_INSTALL_THE_SLEEPING_STORMS` — nightside reads UNMEASURED (no sampled tile in the band); NEXT: wait for the owner's weather scope ruling, then close or measure.
- `WORLD_LAYERS_RESCUE_THE_SAVE_HAS_MORE` — filed (the exporter); NEXT: build the save-to-stamp-files exporter per PLAN.md section 5a.
- `FORGE_SNAILHOLE_FILL_EMPTY_SHELL_LEFT_BEHIND` — needs the owner; NEXT: offer him options for the new Forge slow-ground creature.
- `DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO` — pipeline drained, ~147 failures requeue 10 per feeder run, 155 renders shelved as owner-KEPT; NEXT: ask whether his 2026-10-19 accept-all ruling covers the 155 kept pictures, and re-arm both timers if WSL restarted.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — c4fc18105 6c7cee718 e5bebe2d3 still unjudged; NEXT: run rimflow reconcile for them.
- `CONTAGION validation.py` — DIRTY in code review after e9e7c3d03 (only two blocks reviewed); NEXT: review the whole file if Contagion stays.
- The rest of last handoff's pointers (mutators, Direct Sun, scratch-dir move, JawaBench DLL rebuild, temple/lab design) are unchanged; NEXT: pick them up from `FOUNDRY_HANDOFF_202610191447.md`.

## Traps learned

- Random-destination helper copied the first file's letter case and made a case-twin (PaleTree_B vs _b); fixed at `artledger.install()` plus a selftest (filed: infrastructure/state/lessons; see: commit 0cccafd27, fe9972594).
- `companion_profile.json` expires and a load then comes back CAMPAIGN-refused; renew with the same keys (see: Transient/live_testing_2026-10-19c/).
- `measure` cannot count plants/animals on a map; use the bridge mapgen run with a vanilla control (see: 06_remake_runbook.md G13).
- A donor mod's description can be the ONLY spec for an owner mechanic; do not call it 'from another mod' without his word (see: Rhossak item).
- A hook rejects question cards with a header over 12 characters or a question not ending in '?' (see: question-card skill).

## Commits

```
1118c2556 ledger: RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD built (7 live rows owed); code review CLEAN for the rhossak comp+kernel; winbuild mtime lesson
d69358451 Cauldron: rhossak and galled rhossak are our own animals that bind (RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD)
c0295cb13 ledger: eight-row roster cut recorded; FORGE_SNAILHOLE_FILL_EMPTY_SHELL_LEFT_BEHIND filed
03ac7f26a Cut the eight vanilla/DLC roster rows per owner card 2026-10-19 (RM_ and RUT_ twins)
a05f4db52 Donor art: hourly install of 2 finished dregen_ renders (accepted-for-now)
c1cac92b2 ledger: Wave 1 retirement implemented + verified (498 list, CP SHIP 2329); bridge released
e902aaabb live testing 10-19f: Retirement Wave 1 on the 498 list — cold load clean of new classes, calm AREAFIX2 loads, 10k ticks no exceptions
a61632a78 World remake 07: deeper drops (6) and DEV/TEST/AUTHORING/SHIP profiles for all 536
62a43fdd3 World remake 02: drop Wasteland/TheForge from the donor-leaning list (decoupled in 8e87a9649)
3090fd7e0 Ledger sync: donor-decouple notes (REGEN_GAPS_DECIDE_STRAYS_AND_FLYERS, DONOR_DEFS_PORT_TO_OURS_1)
f037c9a37 Wave 1: Lantern Deeps Pyrinth guards accept mandrake.rm.pyrinth; SHIP drops the 140 wave keys; 498 list is FULL.LATEST
8e87a9649 Donor decouple: RM_Wasteland own ground terrains; cut IronScruff rows from RM_TheForge
0bf713753 World remake 05: drop closure (112 SAFE, 12 HOLD), 367-mod candidate profile, exporter item; Umbra and ideo-tool errors deleted
074daa495 World remake: 06 runbook — start-save procedure, gates, rehearsal, rollback, ordered 31
8498d40eb Donor art: hourly install of 11 finished dregen_ renders (accepted-for-now)
82edfaf2e Donor art: hourly install of 7 finished dregen_ renders (accepted-for-now)
38e464c40 Donor art: hourly install of 3 finished dregen_ renders (accepted-for-now)
afa5c02b8 Donor art: hourly install of 5 finished dregen_ renders (accepted-for-now)
825c86d21 Donor art: hourly install of 3 finished dregen_ renders (accepted-for-now)
5352f04eb World remake plan: three options plus D after GPT review; GPT review pinned
... 16 more: git log --oneline 2514de570..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed; all of this session's work is committed.
- Uncommitted, none of it FOUNDRY work from this session: generated or another window's scratch (`Transient/**` decisions/fixtures/fw_scenes, `conversations/2026-10-19-1038-*.md`, `deployed/config/ModsConfig.before-tier-*.xml` backups written by modcheck, `src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261016T192502.json` a stray proof output).
