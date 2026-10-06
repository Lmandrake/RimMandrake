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
