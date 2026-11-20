## spec

Road-back item of GimmeSomeSlack in-game visit 2, filed by its steward (RIMMANDRAKE_ROUTE_GIMMESOMESLACK_VISIT_TWO_FAILURES_BACK, 2026-11-20). It takes over RIMMANDRAKE_SPLIT_SLACK_WALK_FAILS_ONLY_BESIDE_REVIEW_STATIONS, which the visit's driver filed with the same evidence; the text below is that item's, with the stage sort added.

Stage sort: GAME ONLY (`--needs game-up`). The cause is unknown until a live experiment: the divergence shows only on the owner's full list (316 mods) on the review map, and the fresh CordBuilder and the live pieces are C# in the running game; no offline harness builds them. Stage-6 check: `sc_walk` (`python.exe src/RimMandrake/GimmeSomeSlack/northstar/gss_playtest_runner.py --recipe full`, full list, on GSS_VISIT2_WALK_20261119.rws). Judge the judge: REAL MISS for cords, soak and save_reload_b (a load rebuilds fresh, and a line was lost). The ui 1/24 line (Industrial->Industrial) may be a check that picks the current look [guess ~55%]; if the fixer shows that, the check's pick is mended to a look other than the current one (the bar keeps its meaning) and re-pinned, never removed.

Visit driver's text:

GimmeSomeSlack visit 2, `sc_walk` (2026-11-19, game a, Archmagi, owner's full list 316 mods, DLL a00e4619…, source
85f388636e). `gss_playtest_runner.py --recipe full` ran on the map that holds the 31 review stations
(`human_review.py --build` on a full-list quicktest, saved first as GSS_VISIT2_WALK_20261119.rws). Result FAIL:

- cords: "connect / disconnect / reconnect: live cords != fresh build" (fresh 171 edges, same 104, missing 67, extra in live 67);
- soak: "blast 0: live cords != fresh";
- ui 1/24: "build PowerConduit: the button opens a look menu and a pick changes the designator's style"
  (detail `PowerConduit_Industrial->PowerConduit_Industrial`; the menu listed Industrial as current);
- save_reload_b: 1 of 7 lines lost after the load (a cord at (130..134, 91) to consumer c53469); its fresh read: 170
  edges, same 79, missing 91, extra 37.

Experiments in the sitting:
- cords+soak again on the same map, `--tick-mode batch` and `--tick-mode speed`: the same FAIL both times. Not frame timing.
- The diverging keys lie on review station 31 (STYLED BLUEPRINTS, cells (71..79,179), a transmitter `m:t53405`) and
  station 5 (MODERN: EVERY COLOUR ENTRY, cells (144..151,26..29)), not on the walk's own site.
- A plain full-list quicktest (no review stations), the same build and list: cords PASS ("live == fresh at every step"),
  soak PASS, save_reload + save_reload_b PASS (7 of 7 lines). ui INVALID there ("no clean 30x16 site").

So a fresh CordBuilder and the live pieces differ on styled blueprints and Modern-colour runs [measured: the diff keys'
cells], and the whole-map compare of cords and soak reads that difference. [guess ~60%] a real divergence that a
player meets: a load rebuilds fresh, and save_reload_b lost a line on that map. [guess ~40%] the fresh build in the
probe lacks the stored-look or colour input that the live build has. The ui fail is unexplained: [guess ~55%] the
check picked the look that was already current.

## verify

Acceptance test: on the owner's full list, load GSS_VISIT2_WALK_20261119.rws (or build the review map), then
`python.exe src/RimMandrake/GimmeSomeSlack/northstar/gss_playtest_runner.py --recipe full` prints `VERDICT PASS`. On
85f388636e it printed FAIL (cords, soak, ui 1/24, save_reload_b) on 2026-11-19 20:45 PST. A first offline test that
fails on the old code: a fresh CordBuilder over a styled-blueprint run and over the Modern-colour runs equals the
incremental build.

## criteria

- A fresh build equals the live build on every review station, station 5 and station 31 included.
- After a save and a load on that map, every cord line is the same.
- The ui conduit-look check picks a look other than the current one, and the designator takes it.

## refs

file: src/RimMandrake/GimmeSomeSlack/northstar/gss_playtest_runner.py
file: src/RimMandrake/GimmeSomeSlack/human_review.py
file: src/RimMandrake/GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs
