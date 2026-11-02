## spec
found-by: BENCH bridge run (2026-10-23, run 1 driver 4, HEAD 39ec8aac5e deployed, 14-mod fw_gss_sitting).
Class: HARNESS (seen live; the cause in the code is not yet read).

Repro: load RM_fw_walkthrough_20261023e. Run `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --river --goto R1`
(this makes map R, id 51, the current map). Then run `scenarios_map.py --river --build` with no --fresh-map, as run sheet
BRIDGE_RUN_1 row 3.5 says ("map R current").

Result: "C1 at (155, 81) FAIL depth_wrong 1, first_bad ((160,120),(6,2)); C11 0 of 8 stations (unplaced r_current ..
r_placer)". Every station printed "found no free crossing", and the build also printed "swept 1 non-colonist pawn". After
the build, `--river --goto R1` answered "unknown; valid: C1, C11, R1..R0" and `jawa/list_pawns` on map 51 found no
Muffalo. So the in-place build swept the existing stations and the R1 Muffalo, then could not place any station again.
The damage was in memory only: save e was reloaded and its md5 is unchanged (e7fb0659f23a).

Evidence: Transient/bridge_run_1_20261023/s35_build.log, s35_river_verify.json, s35_goto1.log, map_r_placed_before.json.

What it blocks: row 3.5. Map R in save e was built at 06:12, before d356baa2a4 (08:36), the commit that turns the R1
Muffalo west. So RIVER_MUFFALO_FIX_SHOWS_ITS_REAR A1 needs a fresh map R build, and the in-place route cannot give one.
CORD_LOOP_UNTANGLE_LASSOED_A_PIPE A1 (the map R cord at 36,72) is owed for the same reason.

Fix (harness): an in-place `--river --build` must clear the old C11 stations (or skip the stations it finds already
built) before it looks for free crossings. Otherwise it should refuse, and say that --fresh-map is the route. Do not
leave a map that has had its stations swept.
