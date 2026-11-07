# Graffiti: where the last pass got to

## How to look at it
`src/RimMandrake/Graffiti/stage_colony.py` (under `python.exe`, from the repo root) builds a lived-in base (rooms, corridor, three wall materials, meals), then `call Gallery|Compare|Faces|Spree 3|Who|Count`, `run <ticks>`, `shot <name> x,z,w,h`. Colony rects at play zoom: `106,122,33,15` and `106,112,33,13`. Noon is tick 15000 + 60000k.

## What was wrong, and what changed
- A paint job stood on one cell for 8000 ticks and repainted it every 250, so a spree left 3 to 6 marks. Now each job finishes one mark, with time set by its form, then moves down the wall.
- Marks straddled the wall and floor seam. Now they draw on the wall cell itself. Doors and machines no longer count as walls, and the paint goes when its wall goes.
- Every mark was the same size and dead level, so walls read as sticker rows. Now each has a stable tilt, size and slide, and there are 2-cell and 3-cell marks (wide throw-ups, roll calls, posters, pieces).
- Recreation alone can leave walls bare for a whole day. `JobGiver_IdleTag` now lets an idle hand tag, and a per-room cap stops calm painters burying a bedroom. Sprees ignore the cap.
- Marks could ride off on feet and rain washed them away. Both are off.
- All Vandal art is replaced (it was bright clip-art), and no donor art remains. All 27 meme glyphs and the sigil frames were redone as spray work with no ring-and-slash silhouettes.
- Marks use the `Mote` shader. Cutout clips overspray into sticker edges, Transparent draws nothing at this altitude, post-light glows at night.

## Traps that cost time
- **A `graphicData` block on the abstract `RM_BaseGraffiti` makes every mark invisible, with no error.** Set `shaderType` per def.
- Check new art at 64 px before installing: red-on-red detail merged into a blob that passed at full size.
- **The screenshot tool writes asynchronously.** Reuse a filename and you copy the LAST run's picture. `shot` now uses unique capture names. This faked an "empty hall" for me. Always check colonist names in the picture against `call Who`.
- Colonists draw at their last on-screen spot after `safe_advance` with the camera elsewhere (`Who` shows them moving). I did not fix this: framing the camera and stepping 4 ticks did not help. Don't read pawn positions from a shot. It is a harness view, not seen in the mod's logic.
- The service environment has no Windows PATH and no seat. Export PATH with `/mnt/c/Windows/System32`, PowerShell and `WindowsApps`, and `RIMFLOW_SEAT=BENCH` (the clone's seat, and `live_session.py`'s default). `./game` with that seat writes a CONDUCTOR event into the ledger, so read `tasklist.exe` instead.
- `bridge who` in this clone can show a stale hold. It frees after 45 minutes.
- `jawa/time_set_ticks` refuses on a populated map. Reach noon with `run`.
- `live_session.py` refuses a game past tick 120000: restart, then use `--no-restart --no-quicktest`. After it, run `judge_cli.py <results.json>`.
- Concurrent `codex_image` jobs need their own `--codex-home`, or they harvest each other's images.

## Next
`ralph/DONE.md` claims done; the verdicts and untested gaps are there. If a reviewer sends it back, the open items, best first:
1. Meme glyphs alone still read as emblems. Rougher, less centred art, or two-tone scrawl versions, would help. The owner ruled every meme gets a mark, so they can't just be dropped.
2. Marks lie flat across the crease between wall top and front face. A wall-face mark could be split at the crease and shaded, or sit lower.
3. Never tested: the full mod list, save/load mid-job, balance past day 3.
4. `spree_wall` is sometimes stopped by site surprises (a `Crush` death, a wild Trispike), not by the mod. Clearing wild animals and roofs first would stop that.
