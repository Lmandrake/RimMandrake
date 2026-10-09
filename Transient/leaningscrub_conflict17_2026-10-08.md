# LeaningScrub: the 17 conflicted pictures (Delete / Keep)

Decision taken by question card 2026-10-08 18:44 (a click, not an owner quote). Nothing deleted.

**STATUS: page built, NOT SERVED.** `block_hand_edited_sheet.py` refuses any `serve_sheet.py` start that does not go through `serve_gated.py`, and `serve_gated.py` needs a biome scaled-review stamp this non-biome page cannot get (`scaled_review_gate.py check` fails req 0/1/2/4/5: no snapshot, no biome). Needs a BENCH/owner decision on the guard (exempt this page, or approve a gated route). URL: none yet.

To serve once allowed (from `/home/mandrake/rm/bench/Transient`): `serve_sheet.py --no-open --sheet leaningscrub_conflict17_2026-10-08.html --decisions leaningscrub_conflict17_2026-10-08.decisions.json`.

- Page: `/home/mandrake/rm/bench/Transient/leaningscrub_conflict17_2026-10-08.html`, images in the `_img` folder beside it; builder `Transient/leaningscrub_conflict17_build.py` (re-run is safe; keeps a saved decisions file).
- Decisions (written by the sidecar on each click): `Transient/leaningscrub_conflict17_2026-10-08.decisions.json`. Prefilled Keep on all 17 (no `at`, so enact ignores them). A Delete click writes `purge:[sha]`.
- 17 = RSW_Eopie 6 (3 live, 3 kept), RSW_Lothcat 2 (live), RSW_Scurrier 6 (3 live male B, 3 kept female A), RSW_Strill 3 (kept); 8 live, re-checked by hash.
- Enactment once he has picked: `python3 src/RimMandrake/Utils/art/art.py enact Transient/leaningscrub_conflict17_2026-10-08.decisions.json --apply`. Caveat: enact never purges a live or kept picture, so every picked Delete is reported as a conflict; those need `art.py purge <sha>` with its release-keep option, citing his pick, after replacements are installed for the 8 live ones.

**Owner 2026-10-08 18:59 (typed): "Pause delete for now."** Nothing deleted; all 17 stay. Contact image: Transient/leaningscrub_conflict17_2026-10-08_contact.png

**Decision taken by question card 2026-10-08 19:05: delete all 17 (supersedes "Pause delete for now"), including the 8 live.** Purged all 17 (card 19:05) -- result: 9 purged (Eopie 4-6, Scurrier female 12-14, Strill 15-17; keeps released). The 8 live (Eopie 1-3, Lothcat 7-8, Scurrier male B 9-11) were REFUSED by the ledger guard ("live in a mod -- install a replacement first"); installed textures untouched, no creature textureless. Purge them after replacements install. Replacements: Lothcat south/north = existing done jobs regen_ls2_canon_lothcat_v1_south/_north (awaiting install); Eopie + Scurrier male filed at priority 0: regen_c17_eopie_v1_{east,south,north}, regen_c17_scurrier_v1_{east,south,north} (builder Transient/biome_art_refresh_2026-10-07/build_conflict17_replacement_jobs.py).
