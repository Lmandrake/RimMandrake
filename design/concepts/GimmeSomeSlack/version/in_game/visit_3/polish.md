# GimmeSomeSlack in-game visit 3: polish (a record; nobody fixes these)

- human_review.py's region clear leaves quicktest map features in place: a SteamGeyser steams over station 5's cords on GSS_011_VISIT3_WALK_20261121.rws (strange S_V3_ST05_GEYSER_STEAM).
- visit_rows.py `--final` writes UNMEASURED rows for scenes the visit never ran; a later visit copy should limit it to the checks the change touches (S_V3_FINAL_FLAG_WROTE_UNRUN_SCENES).
