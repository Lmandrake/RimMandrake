# GSS Ralph: where the last pass got to

Pass 2 had the game until Graffiti came back mid-diagnosis. HEAD's DLL is the one deployed when I stopped; Graffiti may have replaced the mod list since, so redeploy and re-apply the `gimmesomeslack` tier first.

## What I saw, playing it
`northstar/colony_scene.py` builds a real little colony in all four looks: walled house, shed, solar field, a yard of dense conduit, a cut, masts with one span down, a second run in another look. `--hard` adds a mountain room, a run wholly inside a wall, and a corridor. Shots are `c*`, `d1_*`, `h2_*`, `g1_*` under `shots/`. The owner's look holds up: I would show `d1_*_house` and `d1_*_yard` today.

Fixed because only a real colony showed them:
- **In-wall runs drew nothing.** A machine wired to conduit inside a wall had no cord, so `conduit_reads_invisible` was false for one of the commonest layouts. Now one cord comes out of the nearest wall or rock face (`CordGraph.FaceFor`); hidden conduit still draws none. Rows M1e/M1f passed live.
- **Cords folded into spikes and barbs.** They read as loose stick-like ends in piles. `CordShape.Unfold` rounds a fold locally. My first detector also rounded the approved heap coils and I saw it in the shot: a fold now needs two straight arms. Coils are back. Probe `kinks`, row M2c. It passed in the last run on 1 fold in 9 strands (a lead hard against a machine). The bar is max(1, strands/20).
- **S8 was red from pass 1's styled-winner fix.** HARNESS: its mast auto-linked to a styled run. S8 now stands alone; S8b (passed) pins the join.

## Open: the one thing to chase first
`AERIAL_block` stopped on GovernorStop, "downed (health 1)", in the last two full runs (`/tmp/gss/proof3.log`, `proof4.log`; /tmp may be gone), after M15f in the latest and after R3 in the one before. Runs 1 and 2 passed the block, on 136 and 134 rows' worth of run. The colonist was Ellison at 108,183, inside the aerial site. **Cause unknown.** I was reading their hediffs when the gate shut. Runs 3 and 4 are the first with M1e/M1f, which stage walls at X0-70, Z0+12 and Z0+24, so check that site against where the colonists get moved. Then shock (M15e/f restring crossing a live wire) and temperature or hunger. Rows after the stop never ran, so **those two runs do not count as a pass**: no 0-FAIL result exists on HEAD and nothing is recorded with modcheck. `proof_all_*.json` from this pass are untracked on purpose.

## Next, with the game
1. Deploy (`--apply`), tier, launch via `steam.exe -applaunch 294100`, `python.exe -u .../proof_all.py --live`. Run the downed colonist to ground, then get a clean run and record it.
2. `colony_scene.py --build --fresh-map --hard --shots <new tag> --frames house,yard,cut,fallen,ring,rock,pair`. Pick DONE.md's shots. `fallen`'s default frame is weak: use `--rect 56,4,14,16`.
3. `downed_span_lies_on_ground` is my least sure line: a mid-span cut draws three nearly straight wires from the crossarm to a spark and can read as still up at play zoom. It follows his B11/B21 rulings (one cable, no wiggle), so I left it. Look at a killed mast before giving a verdict.
4. `shapetable` on the colony against a shot: does the 0.3 bar match the eye? No read of it on a colony yet.
5. Never_taut has no number on a colony. Consider a probe over `LaidPiece.LaidRatio` for cords of 3+ cells. By eye nothing long is taut.
6. Restore at the end with the game down: `modset_builder.py --restore` (the owner's 316-mod list; backup in `deployed/config/`).

## Scenes (`scenes.json`, 23): not built as named entry points
Rows and `colony_scene.py` / `gravship_scene.py` cover much of what they ask, but most of their debug-flag controls (wall-face rule off, rebuild skipped, draw suppressed) do not exist. Decide per scene and say so in DONE.md. Do not claim them as built. `sc_gravship` is now real apart from its planted control.

## Items
- SWITCHES: all four switches now have on/off rows. `gravship_scene.py on|off` flew real ships: on keeps the aboard span up; off takes it down; the ground link goes either way; cords land with the ship (`g1_on`, `g1_off`). Its A2 (0 FAIL proof) is still owed.
- Seen live this pass, rows green in runs 1-2: RESTRING_FIX/PROVE (M15f), SWAY_PROVE (M22a/b), BATCHED_LINK (S12e), STYLED_WINNER (S8/S8b). Rows ran in those runs on earlier DLLs.
- Not re-read live this pass, offline only: COLOUR_SEED, FRESH_BUILD, MULTILINK, POWER_THEFT. STRIP_LED: dark strips read by B6b, repaint race itself unseen. WATER_STUB: the matrix passes on this list; the item's FlowWorks-list case not run.
- Fixed offline, complete: FUZZ_ONLY, CORD_AUDIT, RECOLOR. Ruled out: CORD_ADAPTER (approved art).
- For the Conductor, in `infrastructure/state/`: drop `--allow-red O6_review_round1` from SWITCHES and WATER_STUB live_proofs; RESTRING_PROVE's A2 names M15f; the SWITCHES proof can name `gravship_scene.py`.

## Noted, left alone
- The artfit probe reads 39 faults on the colony. The ones I traced are junctions under a building (hidden) and leads to a machine one cell away, which look fine in `c3d`. Not all 39 traced. It may want to skip hidden junctions.
- A battery-to-machine cord with no conduit draws the Mod Settings default; the settings file reads Modern (`ExtensionCord`) while the shipped default is Scrapper. I did not establish who set it: the owner or a past proof. Check before shots of a default-look scene.
- The ledger files and `ModsConfig.before-*` in the tree are dirty from the bridge, `./game` and modset commands. Not committed.
