# LeaningScrub: the 17 conflicted pictures (Delete / Keep)

Decision taken by question card 2026-10-08 18:44 (a click, not an owner quote). Nothing deleted.

**STATUS: page built, NOT SERVED.** `block_hand_edited_sheet.py` refuses any `serve_sheet.py` start that does not go through `serve_gated.py`, and `serve_gated.py` needs a biome scaled-review stamp this non-biome page cannot get (`scaled_review_gate.py check` fails req 0/1/2/4/5: no snapshot, no biome). Needs a BENCH/owner decision on the guard (exempt this page, or approve a gated route). URL: none yet.

To serve once allowed (from `/home/mandrake/rm/bench/Transient`): `serve_sheet.py --no-open --sheet leaningscrub_conflict17_2026-10-08.html --decisions leaningscrub_conflict17_2026-10-08.decisions.json`.

- Page: `/home/mandrake/rm/bench/Transient/leaningscrub_conflict17_2026-10-08.html`, images in the `_img` folder beside it; builder `Transient/leaningscrub_conflict17_build.py` (re-run is safe; keeps a saved decisions file).
- Decisions (written by the sidecar on each click): `Transient/leaningscrub_conflict17_2026-10-08.decisions.json`. Prefilled Keep on all 17 (no `at`, so enact ignores them). A Delete click writes `purge:[sha]`.
- 17 = RSW_Eopie 6 (3 live, 3 kept), RSW_Lothcat 2 (live), RSW_Scurrier 6 (3 live male B, 3 kept female A), RSW_Strill 3 (kept); 8 live, re-checked by hash.
- Enactment once he has picked: `python3 src/RimMandrake/Utils/art/art.py enact Transient/leaningscrub_conflict17_2026-10-08.decisions.json --apply`. Caveat: enact never purges a live or kept picture, so every picked Delete is reported as a conflict; those need `art.py purge <sha>` with its release-keep option, citing his pick, after replacements are installed for the 8 live ones.
