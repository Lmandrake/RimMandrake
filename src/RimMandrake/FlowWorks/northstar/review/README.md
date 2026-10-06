# FlowWorks feature review sheet

`FlowWorks_review.html` — every FlowWorks feature (45, in 8 sections), built or not, in plain designer sentences, one
status each: **Works in game** (a mapped live-test row PASSed for every part), **Built, not yet seen**, **Partly built**,
**Not built**. Derived from the 139-row capability table in `../../human_review.py` (code probes + the newest
`../validation_v2_result_*.json` + the rimflow ledger); nothing is typed. Top panel: sections x status, what the owner
is asked, what remains to build (grouped by what it waits on, from the ledger). Technical evidence sits behind each
feature's closed "details" toggle. `FlowWorks_status_board.html` is the same content as a plain printable document.

- Regenerate: `python3 src/RimMandrake/FlowWorks/human_review.py`. Serve: `serve_sheet.py --sheet FlowWorks_review.html --decisions FlowWorks_review.decisions.json` from this folder.
- Selftest: `python3 src/RimMandrake/FlowWorks/northstar/selftest_human_review.py`.
- `FlowWorks_review.decisions.json` is the owner's once it exists: the generator writes it only when absent.
- `shots/` = downscaled 2026-10-05 live-run screenshots, the Quarry reference (ruling 33) and the two unpicked ladder drawings.
- Lives under `northstar/` so it does not move modcheck's mod hash; held from deploy in `src/DEPLOY_HOLD.txt`.
- Presentation rules: `design/RimMandrake/northstar_densification_lessons.md`, "Review sheet presentation rules".

## Returning to the review map (keeper save)

Keeper: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\RM_fw_review_20261006.rws`
(built 2026-10-06 from the GREEN run; 34 visuals + 51 gallery stations; older keepers `RM_fw_review_20261005*.rws` stay).
It only loads cleanly on the **flowworks tier**, so the mod list comes first:

1. `python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks --apply`, then launch RimWorld through Steam.
2. In the main menu use Load game and pick `RM_fw_review_20261006` (or bridge `rimworld/load_game_ready`).
3. Labels are process memory and are gone after a load: `python.exe src/RimMandrake/FlowWorks/review_map.py --labels`.
4. Walk it: `review_map.py --goto S0|V|M|F|<station>`. Key: `map/KEYSHEET.md`.
5. Finished: `python3 src/RimMandrake/Utils/modset_builder.py --restore` with the game closed.

A save carries the map as it was built; if FlowWorks code or defs changed since, rebuild with `review_map.py --build --fresh-map` and `--save` a new keeper rather than trusting the old one.
