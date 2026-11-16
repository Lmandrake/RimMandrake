# GimmeSomeSlack human review

Sheet: `keysheet.html` (open it) / `KEYSHEET.md`. Review map savegame: `GSS_OWNER_LOOK_20261116.rws` in the game's Saves folder (kept until the owner says delete). Rebuild the map with `python.exe src/RimMandrake/GimmeSomeSlack/human_review.py --build --fresh-map` from the repo root, then `save_review_map.py`.
Saved 2026-11-16 06:11.

`GSS_OWNER_LOOK_20261116.rws` also holds an extra station X in the free area (cords into all four wall faces with a 4-way junction inside a room; a T, a plus and an L corner; a run under a door, one through an open gap, an in-wall run ending inside the wall), built by `review/extra_station_x.py` (run after `--build`); it is not in `human_review.py` and not on the key sheet. The earlier walk saves `RM_gss_walk_20261015.rws` and `RM_gss_walk_20261015b.rws` (31 stations, hose-free) are still in the Saves folder.
