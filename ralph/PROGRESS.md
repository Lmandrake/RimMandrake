# GSS Ralph: where the last pass got to

**Game: a deploy needs game A down too (A's FlowWorks list loads this DLL), and FlowWorks took A at 18:44 (its pass 3), so `steve.sh deploy` was REFUSED all pass. This pass ends with `ralph/NEED_GAME_A` + `ralph/NEED_GAME`. Conductor, 7:32 PM: B goes back to Graffiti after this pass; the loop waits for whichever game frees first and `ralph/GAME` switches on its own (GAME_SWITCH in events.log). On a fresh pass: read `ralph/GAME`, run `ralph/steve.sh tier`, then `up`, before driving it.**

Pass 13. Retired on the context gate. **Deployed on B: an early build of the drop change (bump shape, not what is committed).** Committed DLL: 4db43c2df4 (drop as a slow-curving ground cord), built from a clean worktree (since removed) holding only that change. Self-tests 1169/1169 there.

## Owner, 7:07 PM today (relayed): changes the taut-cord bar
"I do agree that cords take slowly curving paths rather than straight lines often: what they avoid are sharp curves unless they must. It is worth an algorithm retune to grant more penalty for tight curves that permit long straight runs in exchange for slowly curving loops as the preferred option. Also including random braiding would help a lot. Look at inline cord piles if needed for inspiration."
So `never_taut_straight_cord` fails on SHARP curves where nothing forces them (hairpins, tight U/V/W fingers, a plateau's corners against a wall), not on long gentle sweeps. Braiding (cords twisting round each other where they run together) is the lever for Modern's heap (a net of straight strokes). He suggests looking at real photos of cord piles first (a GPT consult can describe some).

## Done this pass
- **Spark on the writhing tip, re-checked on pass 12's DLL** (pass 12 touched LayFallen): `p13m_floor_sheet.png`, `p13m_wire_sheet.png` (+ `.gif`), Modern played colony after a blast: spark in 12/12 frames each, mean 0.15 cell from the tip the probe reads, spark travel 0.28/0.41 against tip travel 0.30/0.37. The owner had certified it by eye in pass 11; still holds.
- **Lamp-mast drop is a ground cord, not a taut arc** (`AerialMath.LayDrop` + `LooseRun`, `RM_MapComponent_Aerial.DropMeshes`): hangs straight down from the insulator (a J), touches down a cell or so from the foot (to one side when the device is up-screen, so the ground run doesn't lie over its own hang), then lies to the device as a loose cord in slow wide curves (1.4-2.9x the ground it covers, no loop round its own end, dead-straight stretches bowed, a lazy arc for a short run). Ground part draws under pawns and buildings like a floor cord; a walkability signature re-lays it when a wall goes up. A wall between mast and device (vanilla wires indoors lamps to masts outside) keeps the old hanging drop. Self-test rows in `AerialSelfTest.Drops` with a can-fail. Seen in game only as the first (bump) version: `p13b_Modern_drop.png`, `p13b_drop3.png`, `p13b_drop_crop.png` (before: `p13acut_Modern_drop.png`). The committed slow-curve version is NOT seen in game yet. Prototype + renders: `/mnt/d/ClaudeWork/rimmandrake/gss_drop/` (`snake.py`, `s9.png` is the committed shape).

## Round loops instead of hairpins: built, NOT committed (one self-test row red)
A builder subagent, redirected to the owner's 7:07 note, wrote `RoundExcursions` (GSS-only flag in `_Shared/SlackGeometry/CordLayer.cs`, on at `CordBuilder.cs:126`): excursions laid as wide round lobes, each capped by the room left after the lobes already on that stretch and kept away from the cord's ends, bends under 0.8 cell eased with the lost length regrown without pushing into a wall. BowStraights was dropped (it added tight bends). Lab, four ba worlds: open-floor tight bends 347 -> 219, straight runs > 2.5 cells 36 -> 37, doors matrix unchanged (every through_* still 2). Renders (left HEAD, right new; they predate its last three tweaks): `/mnt/d/ClaudeWork/rimmandrake/gss_straight/fin_fut.png` (hairpins -> round U), `fin_ind.png` (kitchen W -> wide loop), `fin_mod.png` (V -> broad S). New self-test row "slack hop on open floor" (tight bends 117 -> 24 over 48 hops of 3-6 cells; fails with the flag off).
**Red: `nodal: 1/2 dead ends not visibly limp`.** The short dead-end edge at (14,13) used to carry under 1.0 cell of cord, below the audit's cutoff, so it was never checked; now it keeps 3.1-3.5 cells and one tip curls 47 degrees against the 50 degree bar. Two fixes were tried and reverted (each broke `downed`, `whip`, `graph worker`). The change is still in the working tree (`CordLayer.cs`, `CordBuilder.cs`, `SelfTest/CordShapeChecks.cs`) and saved as `ralph/wip_round_excursions.patch`; the committed DLLs are the drop build without it. Builder notes: `/mnt/d/ClaudeWork/rimmandrake/gss_straight/PROGRESS.md`, log `final_selftest.log`. Not fixed by it: fingers on hops of 2 cells or less, heap joins, end fittings, knot necks.

## Do next
1. Finish round loops: make the `nodal` row pass (give a dead end's own tip its limp curl back after the regrow, or keep a short dead-end edge's old slack), re-run the lab (`gss_straight` tools) and renders, commit with both DLLs (FlowWorks' DLL bytes change because it compiles CordLayer.cs; it never sets the flag).
2. When a game is free (`tier`, `up` first): `deploy`, shoot the drop in four looks (`python.exe ralph/live/p12_look.py TAG --frames drop,span`) and the colony tiles (`--tiles`, `--frames dense`). Judge at play zoom against the owner's 7:07 note.
3. **Several cords meeting at one bed** (judge p12: Futuristic and Modern bedroom 3, `ba_new_Futuristic_t00.png`): two cords' slack wanders under the bed, so the bed looks plugged in twice. Pass 9 re-lays a cord that strays under a *powered* machine (`CordShape.MachineStrays`, used in `CordBuilder.SprawlOnce` and `Bowed`); extend it to furniture drawn over cords (beds, tables, shelves: buildings that are passable, not doors/conduit/machines), excluding cells the route itself crosses. Needs a furniture list in `CordWorld` (shared, GSS-only use), filled in `CordWorldAdapter`, read by `LabWorld`. For the lab: `ralph/live/furniture_dump.py` lists every artificial building per played save, but `load_game_ready` returns before the map exists and its wait loop hung (killed); use `lived_in.Run`'s map-ready wait instead.
4. **Eighth cause** (QUESTIONS.md): `CordPlanner.FindPath` only tries the dive A* (through a wall at `DiveCost` 12 per barrier cell) when no walking route exists, so a lamp wired by vanilla through a wall gets a 12-cell walk round and out a door. Fix: with dive on (GSS only), take the dive when the walk is much longer than the dive (e.g. compare costs, or run the dive A* directly, which already prefers open floor); check the doors matrix.
5. **Braiding** for heaps and parallel runs (owner 7:07). Modern's heap first. Look at real cord-pile photos first.
6. Full proof once (`proof_all.py --live`), not recorded. Broaden call: pass 12 made one and acted on it; another is due before DONE if this pass's counts as stale.

## Steve this pass
Fault window open (`bad_cpus=[3,14]` at start). No dead game, no dropped ssh, no reboot. One deploy + restart of game B (bridge up in 22 s). One remote script hung waiting for a map and had to be killed (my script, not weather).

## North star, judged hard (on what is deployed or seen)
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true
- cord_meets_wall_at_its_face: true
- dense_grid_reads_as_tangle: false (Modern's heap is a net of straight strokes; braiding owed)
- break_live_and_dead_ends_differ: true (`p13m_*_sheet.png`)
- overhead_span_above_everything: true
- downed_span_lies_on_ground: true (`p13acut_Modern_cutspan.png`)
- four_styles_distinguishable: true
- one_run_one_style: true
- never_taut_straight_cord: false (judged on the owner's 7:07 terms: hairpins/festoons in the Futuristic workshop and the W in the Industrial kitchen are tight bends nothing forces; round loops are built but uncommitted and unseen in game; the lamp drop is fixed in code but unseen)
- never_cord_across_impassable: true
