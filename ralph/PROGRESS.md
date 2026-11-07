# Graffiti: where the last pass got to

`ralph/DONE.md` claims done, with its gaps. If it comes back, start there.

## How it works now
- `Source/Kernel/RM_GraffitiKernel.cs` holds the wall plane (`FacePoly`, `MarkPieces`); `Source/WallPlane.cs` prints it. `art_source/wallgeom.py` and `wallsim.py` are the offline twin: judge geometry and art there first, on the real atlases.
- Art: `art_source/manifest.py gen` generates what's missing into `ralph_graffiti/gen3`, `bake.py` writes `Textures/`, `patch_defs.py` writes sizes and pigmenting into the defs, `gallery_sim.py <dir> <prefix>` shows it all at play zoom.
- `stage_colony.py`: `new`, `colony`, `call Ladder|Sweep|Gallery|Spree 3|Who|Count`, `run <ticks>`, `shot <name> x,z,w,h [ppc]`. Noon is tick 15000 + 60000k. Max 33 cells wide at 64 px.

## Traps that cost time
- The game gate matches the install path, even for a read-only decompile. Don't dodge it. Decompiled source is in `D:\ClaudeWork\rimmandrake\decomp\rw16\all`, atlases in `D:\Luke\dev\RimMandrake\observed\inventory\bundle_textures`.
- Paused shots drew pawns at stale spots: the tweener only moves with frames. `Settle` resets it, and `shot` calls it.
- Vanilla's naming dialog pops up over long advances. `shot` closes it.
- Weathering is a tight trade. A streak floor of 0.42 with patches at wear*0.5 looked great on the bench and went nearly invisible in dim rooms. Check marks in the colony, not just the sim.
- `rimworld/load_game_ready` returns before the map is usable. The next call can see no map.
- The service shell needs the PATH and `RIMFLOW_SEAT=BENCH` exports. `/tmp/gr/cycle.sh` was my stop-deploy-launch script and won't survive a reboot; `live_session.py` does the same plus the suite.

## Next, best first
1. Run `judge_cli.py` on the suite result (not run).
2. Test natural rock and modded walls in game, and the full list.
3. If paint still reads clean close up: more streak in fills, without losing play zoom.
4. Try the honest gap: −8 to −5 aren't ranked by looks.
The game is still up on `graffiti_solo`; the owner's mod list has not been restored.
