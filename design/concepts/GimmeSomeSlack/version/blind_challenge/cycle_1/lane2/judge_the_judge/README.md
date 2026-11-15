# Judge the judge (GSS 0.1.0 blind cycle 1, lane 2 follow-up, 2026-11-15)

- `feasibility_sweep.py` (`--step 15`: `feasibility_step15.txt`): one cord meeting slack 1.4x, a cell of stray (chord > 4) and the bend bar at once
  exists for every chord 2..12 x heading_A x heading_B x fitted/plug cell (2704 of 2704); every chord-3+ cell has two shapes 0.1 apart (the 22 that
  do not are chord 2, exempt by the owner's card). The four criteria are sound.
- `refusals.json`: two judge checks repaired in `../../lane1/BlindLane1.cs` (L1_CORD_EXCURSION's chain read, L1_NO_REPEAT's verdict), the
  `no_hose_in_gss` wording for the neutral fixer, and the two loop definitions for cycle 2.
- `Diag.cs`, `diag.py`: the sweep harness (lane 1's scene maker, thousands of seeded scenes, failures by lay and end kind);
  `python3 diag.py all 1000 --base [--src <GimmeSomeSlack dir>]` from the repo root. `sweep_base_2000.txt`: the base kernel over 2000 scenes.
