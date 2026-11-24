## spec
Pyrelands (Design Version 0.1.0). Rank 8 of the costly-acts study (`design/specs/2026-11-23-costly-test-acts/analysis.md` sections 4 and 9; item RIMMANDRAKE_CENSUS_COSTLY_TEST_ACTS_REPEATED_HE_SAW_SHIP_FLY). Test-harness change only: no mod bar moves. Short chains only; the long "field weeks" chain (rank 2) is NOT filed here.

**Measured (visit 7, ArchSmall, 2026-11-23):** 48 site reloads, 718 s, about 15 s each, one before every check; most checks work on their own pad. About 5 shared site loads for the short chains would do, about 20 loads in all (the long and map-wide chains keep their own); saved about 5 min [guess ~50%]. Also in the study: `plant_census` ran alone (109 s) and again inside `plant_census,scorchfruit_fire_born` (163 s); `grass_cover` ran alone (25 s) and again with `embergrass_regrow`; running each only inside its host chain is the study's rank 12 (about 2.5 min), a small separate saving, not filed here.
Cost named by the study: a chain that leaves fire, weather or a setting spoils the next; each chain's teardown must be read before the next starts, else reload. `fire_incident`, weather and letter chains stay alone.
Build: medium; needs no scene-library part (the chains run in the Northstar driver: `src/RimMandrake/Utils/northstar_driver/`, `src/RimMandrake/Pyrelands/northstar_plan.py`, `northstar_site.py`, `validation.py`; the fixer finds the reload point, the study does not name it).
**What waits on the library (not filed):** rank 2, field weeks (about 36 min; 4 long checks sharing one map over 14.6 game days): needs `s.stage` (pads, terrain, plants), `s.act` (`weather`, `tune`) and `s.read` (fertility probe); only `s.run` is built. [guess ~55%]
Which chain groups keep every verdict: shown by no run (UNMEASURED).

**Recommendation: Polish list** (about 5 min per visit, guess ~50%). The Conductor decides.

## verify
Acceptance test: `bash infrastructure/state/items/RIMMANDRAKE_SHARE_PYRELANDS_SITE_LOAD_BETWEEN_SHORT_CHAINS.acceptance.sh [--day D --from HH:MM --to HH:MM --port P]`
- Reads the bridge telemetry (`E:\telemetry\raw\bridge\<day>.jsonl.gz`) and counts `rimworld/load_game` calls on the visit's port in its window; limit 20 (our own rule, the study's target [guess]). WATCHED FAIL today (2026-11-24) on visit 7: `calls in the window 39718; rimworld/load_game calls 61 (limit 20, our own rule)`, exit 1. The count 61 is this reader's yardstick; the study's 48 counts load acts, so do not compare them. `--selftest` prints SELFTEST OK (6 cases: 48 loads -> red; 12 -> green; no load in a visit with other calls -> green; empty visit -> could not look; other port only -> could not look; unreadable file -> could not look). Watched green.
- Run it on the first Pyrelands visit after the change with that visit's window. UNRUN live: that every chain verdict is the same as before the sharing.

## criteria
- On the first visit after the change the reader exits 0, and every short chain's verdict equals its verdict on visit 7/8 (or the item records which one moved and why).
