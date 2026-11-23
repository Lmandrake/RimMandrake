# GimmeSomeSlack in-game visit 3: polish (a record; nobody fixes these)

- human_review.py's region clear leaves quicktest map features in place: a SteamGeyser steams over station 5's cords on GSS_011_VISIT3_WALK_20261121.rws (strange S_V3_ST05_GEYSER_STEAM).
- visit_rows.py `--final` writes UNMEASURED rows for scenes the visit never ran; a later visit copy should limit it to the checks the change touches (S_V3_FINAL_FLAG_WROTE_UNRUN_SCENES).
- 2026-11-22 rerun: proof_all offline gate O3 slice row "all-keys-changed re-lay" is a single timed attempt (cold build beside it takes best of 3); after the Unkink step it reads 23-26 ms against a 30 ms bound and read 32.1 ms once at load average 5-8. Not a defect of the mod; one flaky red per few gates.
