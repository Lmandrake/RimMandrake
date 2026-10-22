# line_joins install (BENCH art helper) — progress
Owner 2026-10-21 ~23:20 PDT: "Just accept the art and go on. ... all four art styles could be chosen together. Bad sheet design, but just accept and move on."
- [ ] read sheet + decisions + review spec
- [ ] record acceptance via sheet tooling
- [ ] install via art ledger
- [ ] drawOffset (sprinklers) / drawSize (reels)
- [ ] facings
- [ ] follow-up item (camera angle)
- [ ] art_sheet.py take-all-looks fix + selftest
- [ ] audit, commit, push
- 23:xx read done. Root cause: sheet put every look's render in ONE lane (the def's base texPath; graphic_of = Scrapper path
  for all tank/sprinkler columns) -> one pick per row AND enact would have installed every look onto the Scrapper file.
  Fix in art_sheet.py: look_lane_target() — a render filed for a sibling look's live texPath gets that look's own lane.
- picks: sprinkler Scrapper = lj2 (foot ~y140 near centre, dome 59 px = spec 51-61) over lj (dome 85 px, foot y~185).
- reel geometry: HoseMath.ReelDrawSize 2.8 + ReelIntakeGeometry.cs are generated from art at 2.8 -> C# owed (follow-up item), not done here.
- [x] sheet rebuilt (--sheet-only, gate PASS v1): every look its own lane (37 sets). Acceptance recorded by NEW
      `decisions_v2.py <dec> --accept-looks "<his words>" --prefer RM_SprinklerHead=F` (18 lane picks; stale one-lane assigns kept under assignSuperseded).
- [x] enact --apply --no-deploy: 18 rulings ingested, tap installed; 17 refused over earlier owner-kept installs ->
      art.py install --owner-said (his words) x17: all installed.
- [x] XML: sprinkler drawOffset z per look (Scrapper 0.04, Industrial 0.2, Modern 0.18, Futuristic 0.14; was 0.31);
      reel drawSize 2.8 -> 2.15 ALL looks (one value: validation_style_hose R0 + C# assume one; art 1.4-1.9 cells), shadow (1.23,0.35,1.04). R0 PASS.
- [x] facings: every installed piece is Graphic_Single (reel Graphic_HoseReel, non-rotatable; tap rotatable but single) -> none missing.
- [x] item REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON (FOUNDRY): reels+tap side-on redraw + reel hose geometry C# regen.
- [x] selftest_sheet_look_lanes.py 13/13; related sheet/enact selftests 9/9 GREEN.
- audit (art.py status, fresh): all 18 texPaths LIVE = picked sha, PROTECTED. NOTE RM_LiquidTap.png is also RM_VentGasTap's body.
- the bridge-art helper's commit 4e049d8bdb already carried my art-ledger install events (shared shard).
## Owed (not done here): deploy FlowWorks (Textures + Defs); live look at 1 cell = 80-100 px: sprinkler foot on a mid-run pipe (4 looks), reel + hose nozzle (geometry still old -> gap expected), tank outlet on pipe, pump ports, tap.
