# Live art look — Modern tanks, Modern FA fire reel, portable ladder (BENCH helper, 2026-10-22)

## Status
- DONE. Bridge taken (BENCH) and released at the end; game left up, paused, on RM_fw_walkthrough_20261022d.

## Selftest + deploy
- `selftest_flowworks_stock.py` GREEN (run_selftests 1/1 PASS); the C# SelfTest's HoseJointChecks assertion that needs
  ok == total == 256 reel feeds passed (hose: 380/380 assertions).
- Game closed (taskkill, PID 11220), `./game --why "deploy FlowWorks art" down`; `deploy_custom_mods.py --mod FlowWorks`
  plan = 9 files (DLL + srchash, six Modern reel PNGs, Tank/Modern/RM_LiquidTank.png), `--apply` -> VERIFIED in sync.
- ModsConfig = tier fw_gss_sitting (14 mods, md5 2fca0dd9 = the swap marker's tier_md5, marker kept). Relaunched via
  Steam, save c loaded (tick 130095), Player.log 178 lines, 0 error/exception lines.

## Staging (new things -> saved as RM_fw_walkthrough_20261022d; c and b untouched, md5 862d2c85 / fe741af8)
- Map C, open grass at x 100-160, z 198-226 (north of C13, outside every plot). Plants/items/filth cleared there.
- Four tanks (jawa/build_batch, look set with CompTankLook.SetLook -> Modern; thing_graphic reads Tank/Modern/<def>):
  RM_LiquidTank (116,202), RM_LiquidTankTall (116,208), RM_UniversalCargoTank (116,214), RM_UniversalCargoTankXTall
  (116,220); a Modern reel at (104,z) rot E each, hose laid to (115,z) -> free end coupled to the tank's west port.
- FA reels (HoseProbe place, Modern): stored (134,210) rot E; laid west (132,204)->(120,204); laid north (140,204)->(140,214);
  laid south (126,222)->(126,211).
- Portable ladders: C12's 3 m pit (65..67, 16..18): the staged west one (65,17) + three added: N (66,18), E (67,17), S (66,16).
- My error, fixed: a destroy_batch (Building) to clear limestone at (144..153, 211..215) also took a laid reel at (154,210);
  it was re-staged at (132,204). The first tank lays (target = the tank's own square) failed the joint check (finding 1)
  and were re-laid to the square in front of the port.

## Captures (Transient/pile_2026-10-22/live_art_look/*.png, all looked at)
| # | subject | file | verdict |
|---|---|---|---|
| 1 | Modern short white leg tank + hose | t1_short.png | PASS: reads as a white poly leg tank, ~1.7 x 1 cell in its 2x2; coupler face on the end bulkhead fitting, no gap, nothing clipped |
| 2 | Modern tall green poly + hose | t2_tall.png | FLAG: recognisable green poly tank, size fine; coupler sits ~0.3 cell west of the drawn wall and a bare hose stub runs on into the plain wall (no drawn fitting there; the port is the footprint edge, the art is narrower) -> finding 2 |
| 3 | Modern IBC cargo + hose | t3_ibc.png | FLAG: clearly an IBC (cage, pallet, valve); same 0.3-cell coupler-off-frame stub -> finding 2 |
| 4 | Modern extra-tall white poly + hose | t4_xtall.png | FLAG: clearly a tall white poly tank with level band; same stub -> finding 2 |
| 5 | Modern FA fire reel stored (E) | r1_stored.png | PASS: red drum wound with red hose, handwheel valve, pedestal; hard-edged box shadow larger than the reel -> finding 3 |
| 6 | Modern FA fire reel laid west | r2_west.png, r2_west_nozzle.png | PASS: empty red drum, coupler on the nozzle, no gap |
| 7 | Modern FA fire reel laid north | r3_north.png, r3_north_nozzle.png | PASS: coupler on the nozzle; box shadow (finding 3) |
| 8 | Modern FA fire reel laid south | r4_south.png, r4_south_nozzle.png | PASS: valve up, nozzle down, coupler on it; box shadow (finding 3) |
| 9-12 | portable ladder on N / E / S / W walls | l_all.png | PASS: N stands up the wall with its top above the rim; E and W upright on the wall line (they overhang the rim line by a few px, reads as leaning on it); S shows only the top stub above the near lip (the agreed convention). The W/E foot shadow from the owner's 02:08 note is not visible at this zoom |
- Not judged (not the subject): the colonist Roberson in the ladder pit draws at full size over the pit's south rim.
  Dark ground blotches beside tanks 1-2 were there before anything was built (probe_site.png) and read plain
  GrasslandSoil: not the tanks.

## Joint check (`northstar/joint_check.py --all-maps`)
- Before staging: PASS (map 0: 24 joints / 18 reels; map 48: 2 / 2).
- After the first tank lays: FAIL, 4 x free_on_port gap 0.207 (ends ON the tanks) -> finding 1.
- After the re-lay: PASS (map 0: 35 joints / 26 reels, 0 gaps, 0 unmeasured; map 48: 2 / 2). joints_after.json.

## Phone image
- look.png (1590 x 1302): nine labelled tiles; looked at.

## Findings (filed)
1. MOD `HOSE_TANK_LAY_FIX_ENDS_ON_LID`: laying a hose to a tank's own square is accepted and leaves the free end lying on
   the tank, 0.207 cell from its port (joint check FAIL free_on_port); should snap to the port or refuse.
2. MOD `MODERN_TANK_PORT_REDRAW_COUPLER_FLOATS`: Modern tall / IBC / XTall art is narrower than the 2x2 footprint and has no
   fitting at the port, so the coupler sits ~0.3 cell off the wall with bare hose into plain wall (short tank is right).
3. MOD `MODERN_REEL_SHADOW_FIX_BOX_TOO_BIG`: the Modern FA reel draws a hard-edged square shadow much larger than its
   slim pedestal art (stored, north, south).
4. HARNESS `CELL_RECT_SHOT_FIX_COLONIST_BAR_PHOTOBOMBS`: jawa/clear_ui + rimworld/screenshot_cell_rect still show the
   colonist bar across the top of tall captures (r4_south.png, probe_site.png).
