# WB-game-creatures-20261126-184717 (home game:creatures), state

Done. 1 member, nothing left for a restart.

| ticket | class | outcome | commits |
|---|---|---|---|
| `VANILLA_BEAST_LEAKS_EXCISE_ESCAPEES_AT_LARGE` | keep | fixed, closed | ccb968c4a9, 39d7c817d0, dda1a9edc7 |

- Step A: kept (the leaks were still true on the 2026-11-12 dump, and more than the ticket listed).
- Step B: shaped, 2 parts (offline selftest; the SHIP key).
- Step C: strike patch, SHIP cut of IncidentDef/VEE_CaravanAnimalsWanderIn, RM_CathedralStrays source fix, census fix
  with page `design/specs/2026-11-26-vanilla-beast-route-leaks/boundary.md`. One fresh read (GPT, code_review.md); its
  2 findings were fixed test first.
- Untested: the live read. `python3 src/RimMandrake/Utils/selftest_vanilla_beast_cut.py --dump` on the first def dump
  captured after ccb968c4a9 reads the dump raw. That dump needs the full list (UtinniPatches with VEE and VLE).
