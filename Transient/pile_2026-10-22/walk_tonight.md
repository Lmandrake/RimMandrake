# FlowWorks live walk — tonight, 2026-10-22 (BENCH with the owner)

Save **RM_fw_walkthrough_20261022b** (map C: 10 scenarios + DB drawbridge row; map R: C1 + C11). Clock: map C 16:00,
map R 09:42 (the two tiles are ~6.3 h apart in longitude: at the usual 10:00 on map C, map R is in the dark at 03:42). Old save RM_fw_walkthrough_20261022 is kept. Stops JSON (camera driver): `Transient/pile_2026-10-22/walk_tonight.json`. **11 stops, 27 decisions, ~44 min.** Every stop is one of HIS judgments; everything an agent proved is in the skip list.

## REBUILD (~16:30, after the belt frees the game) — commands in order, BENCH seat clone `/home/mandrake/rm/bench`

1. **Bridge**: `rimflow bridge take --for "walkthrough rebuild 20261022b"` (bare `rimflow bridge who` first; the belt releases).
2. **HEAD**: `git fetch origin && git log --oneline -1 origin/main` must include 7517bbf820 (map R builder + DB row),
   444af8cdea + be9b0277f3 (sign truth), c1e83fe38d (C3 turned reels), fixer B's C4/C10 lays and
   the day's FlowWorks DLL (+ .srchash). Bring the seat clone to it with `./publish`/`git pull --rebase origin main` (no
   --autostash; a DLL conflict = stop).
3. **Game down for the deploy** (a DLL cannot be written while RimWorld runs): close RimWorld by PID
   (`tasklist.exe /FI "IMAGENAME eq RimWorldWin64.exe"` -> `taskkill.exe /PID <pid>`), then
   `./game --why "deploy HEAD for the walkthrough rebuild" down`.
4. **Deploy**: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks` (plan: read it; no `-` line, nothing
   from another seat) then the same with `--apply` (expect VERIFIED in sync). ModsConfig is NOT touched: tier fw_gss_sitting
   (14 mods, swap-active marker) stays.
5. **Launch via Steam**: `powershell.exe Start-Process 'steam://rungameid/294100'`; `./game --why "walkthrough rebuild launch" loading`;
   wait for the bridge token (~2 min on the small list) and the main menu; `./game --why "main menu reached" up`.
6. **Map C** (fresh quicktest game, ~7 min incl. the 2 h soak):
   `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --build --fresh-map | tr -d '\r'`
   -> expect `LIVE build: 10/10 scenarios as staged; soak: ...`. Soak movers so far: C2 (moat, fixer B fixed), C7, C12 —
   a mover is a NOTE for the walk, not a stop. The DB row builds here (any `station DB ...` note = a REFUSED proof call: read it).
   `--build --fresh-map` deletes the stale review/scenarios/map_r_placed.json.
7. **Map R** (a SECOND map in the same game; map C and its colonists stay):
   `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --river --build --fresh-map | tr -d '\r'`
   -> expect `LIVE map R (tile T, map M; map C = K): C1 at (x, z) OK; C11 8 of 8 stations; N of N sign books`.
   UNTESTED LIVE (written offline today): if it prints `map R NOT founded`, retry once; if C1 FAILs, read
   `Transient/fw_scenarios_river_verify.json` notes. Exit 2 = no river tile qualified (record it; walk map C only, skip stops 8-11).
8. **Verify signs + labels**: `... --river --labels` (map R labels), `... --river --goto C1`, then
   `python3 src/RimMandrake/Utils/system_screenshot.py Transient/pile_2026-10-22/rebuild_mapR.bmp`; then
   `... --labels` (switches back to map C) and `... --goto DB`, screenshot `rebuild_DB.bmp`, `... --goto C3`, screenshot
   `rebuild_C3.bmp` (turned reels at x 39-47, z 13). Sign counts: each build line prints `N of N sign books` — N must equal.
   Spot-read one sign: `jawa/review_sign action=list prefix="SIGN C12"` must say the colonist WALKS the planks.
9. **Save** (map C current, clock pinned to 10:00, paused; old save untouched — `free_save_name` refuses an existing name):
   `python3 src/RimMandrake/Utils/save_guard.py run --current-slot none -- python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --save --name RM_fw_walkthrough_20261022b`
   -> expect `save RM_fw_walkthrough_20261022b: ok=True`. Keysheet regenerates (review/scenarios/KEYSHEET.md, keysheet.html).
10. **Commit + push** (explicit paths): `git add src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json`, then
    `git commit src/RimMandrake/FlowWorks/northstar/review/scenarios/{map_r_placed.json,KEYSHEET.md,keysheet.html} -F -`, `./publish`.
11. **Keep the bridge** for the walk: `rimflow bridge take --for "owner walkthrough 20261022b"`. Refresh the skip list below
    from `Transient/pile_2026-10-22/belt.md` (rows proven after 09:10).

## The walk

Camera: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --goto <ID> | tr -d '\r'` (map C) or `... --river --goto C1|C11|R1..R8` (map R; switches maps itself; map-C gotos switch back). Close-ups: the `frame` of each view in the JSON (absolute cells; map R views are C1 plot-local `frame_rel` + c1.origin from map_r_placed.json). One card per stop, the questions below as its rows.

### 1. C3_reels_hoses — map C, ~6 min
- camera: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --goto C3`
  - view reel park + turned reels: frame_cell_rect x=11 z=11 w=38 h=26
  - view o1 hose to Hobb (laid, plump): frame_cell_rect x=16 z=24 w=22 h=24
- setup: none (staged: park reels plump/filling/flat/wound at x13; dropped carry along z13; turned N/E/S at 39-47,13)
- look: hose girth empty vs plump; the EMPTY (flat, dropped) hose's shadow; the four reel looks; the turned reels (north/south are the west art turned)
- **CARD:** Hose girth now (empty and plump)? — Keep / Thinner / Thicker / Plump only: wider · closes: HOSE_GIRTH_TUNE_MUCH_THINNER
- **CARD:** Empty-hose shadow (darker, wider since today)? — Keep / Lighter / Darker still · closes: HOSE_GIRTH_TUNE_MUCH_THINNER
- **CARD:** Turned reels (north/south = west art turned)? — Fine as is / Install the drawn N/S views (phone A-P) / Redraw · closes: REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED, REEL_OUTLET_DECIDE_ALWAYS_GOES_WEST
- **CARD:** Reel looks (four styles) still bizarre / side-on? — Read right now / Still side-on: redraw / Redraw one style · closes: REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON

### 2. C12_planks_ladders — map C, ~5 min
- camera: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --goto C12`
  - view concealed pit + rail ladder: frame_cell_rect x=63 z=30 w=16 h=12
  - view portable ladder / gear / jump pits: frame_cell_rect x=62 z=13 w=24 h=12
- setup: HE pokes: right-click the drafted colonist at 71,33 to 75,35 (across the planks)
- look: the colonist ON the planks (floor height, not sunk); the oubliette rail ladder RAISED; the portable ladder leaning
- **CARD:** A colonist walking the planks reads as? — On the floor (right) / Sunk into the pit / Floating · closes: PIT_COVER_WIDEN_PLANKS_BEAR_BOOTS (closed 41fb948b5e; a 'no' reopens it)
- **CARD:** Rail ladder (raised, on the wall)? — Keep / Hug the wall tighter / Redraw · closes: RAIL_LADDER_REDRAW_CLIMB_NOT_CRAWL
- **CARD:** Portable ladder leaning in the 3 m pit? — Keep / Redraw · closes: PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS (look bar)

### 3. C2_seam_spikes — map C, ~6 min
- camera: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --goto C2`
  - view gatehouse concealed pit (max zoom for the seam): frame_cell_rect x=89 z=77 w=7 h=7
  - view drawbridge raised in the keep wall: frame_cell_rect x=93 z=76 w=12 h=12
- setup: after the seam question HE (god mode) deconstructs one gatehouse plank: the whole cover gives way, spikes show
- look: the seam at max zoom; then the spikes in the 4 m pit; the steel leaf/winch/gate in place
- **CARD:** Concealed pit at max zoom? — Seam right / Too visible / Too hidden · closes: north-star look bar pit_covered_seam_at_max_zoom (C2)
- **CARD:** Pit spikes art? — Keep / Thinner spokes / Redraw to his reference · closes: PIT_SPIKES_REDRAW_SPOKES_NOT_LOGS

### 4. DB_drawbridge_pictures — map C, ~4 min
- camera: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --goto DB`
  - view four drawbridges + two closed gates: frame_cell_rect x=63 z=167 w=36 h=18
- setup: none (timber lowered, timber raised, steel lowered, steel raised + winch powered; gates WoodLog and Steel, closed)
- look: each leaf/winch/gate draws its MATERIAL picture (443912e4df); closed timber gate = the picture he never picked
- ⚠ seat saw (preview 16:00): the TIMBER RAISED leaf (no winch, abs 72..76,174) draws NOTHING although ProofLeaf reads it
  raised 3/3 — only the steel raised leaf shows its upright edge. Filed TIMBER_LEAF_DIAGNOSE_UP_AND_INVISIBLE; tell him
  before the timber card (judge the timber LOWERED deck and the gates; the raised timber picture is a bug, not a look).
- **CARD:** Timber drawbridge pictures? — Keep / Redraw leaf / Redraw winch / Redraw both · closes: DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS ('Drawbriges need to be looked at in game')
- **CARD:** Steel drawbridge pictures? — Keep / Redraw leaf / Redraw winch / Redraw both · closes: DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS
- **CARD:** Closed gates (timber/Scrapper closed renders exist, never picked)? — Install the A renders / Keep what shows / Redraw · closes: BRIDGE_ART_REDRAW_CABINETS_GROW_SADDLES

### 5. C5_riser_girth — map C, ~4 min
- camera: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --goto C5`
  - view tank bay + pump: frame_cell_rect x=112 z=24 w=26 h=24
- setup: none
- look: pipes rising onto each tank's flange; pipe girth (half since 10-22); chemfuel/propane/water colours
- **CARD:** Pipe rising onto the tank flange? — Right / Riser too tall / Enter lower / centre · closes: PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID
- **CARD:** Pipe girth (half)? — Keep / Thinner / Thicker · closes: PIPE_GIRTH_TUNE_HALF_AS_THICK
- **CARD:** Liquid colours in hoses/canals? — All distinct / Chemfuel ~ propane / Water too dark · closes: (look bar liquid_colours; a 'no' files a tune item)

### 6. C7_ponds_level_wells — map C, ~5 min
- camera: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --goto C7`
  - view two ponds + hose net + bleed wells + ground tanks: frame_cell_rect x=12 z=124 w=26 h=16
  - view tower + garden hose: frame_cell_rect x=12 z=140 w=30 h=12
- premise (corrected 2026-10-22 evening): tanks in plain Store mode do NOT level with each other — **"Storage fill stays
  pump-only"** (GSS ruling 3, spec of PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL). Levelling is between liquid BODIES joined
  by a pipe/open hose. The three ground tanks stand apart as a size look only.
- staged: two dug ponds 2 m deep west of the plot (HIGH full at abs 13..16,134..137; LOW at 1 notch, abs 13..16,126..129),
  two Modern reels on one pipe, a hose onto each pond's lip; HIGH end Outflow, LOW end **Capped** (nothing moves).
- setup: HE opens it — select the LOW pond's reel (abs 24,127), Free end -> Outflow (or seat:
  `python.exe Transient/pile_2026-10-22/walk_c7_probe.py water "role:23,127;Outflow" water`); unpause at speed 3 for
  ~2.5 in-game hours (6,000 ticks; 10,000 dL move per 250-tick cycle); re-read with `... walk_c7_probe.py water`.
- look: the full pond falling, the low one rising in decilitre steps to one level; both reels read "Levelling: flowing"
  then "level"; the hoses plump while flowing; the bleed wells read as wells (not taps); the tall tower
- known UX wrinkle (seat saw it live): while levelling flows the Outflow end still reads "Nothing drains here: needs a pump
  or a tank set to Dump", and the HIGH end flips from "beside deep water" to "lying free". A 'confusing' from him files it.
- **CARD:** Two ponds joined by a hose finding one level, no pump: speed? — Right / Too fast / Too slow · closes: PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL (A4 look), WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES
- **CARD:** Bleed well art? — Reads as a well / Reads as a tap: redraw · closes: BLEED_WELL_STRINGS_RENAME_TAP_RETIRED (strings done; art call)

### 7. C4_depth_read — map C, ~3 min
- camera: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --goto C4`
  - view quarry benches + sump: frame_cell_rect x=14 z=64 w=36 h=36
- setup: none
- look: D1/D2/D3 benches + 3 m sump readable at a glance; wet-wall band; the hose climbing the ramps (fixer B's lay)
- **CARD:** Depth reads at a glance? — Yes / Walls need more shade / Water needs more depth tint · closes: WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED
- **CARD:** Hose up the ramps? — Reads right / Ugly: rework · closes: (C4 hose lay, fixer B; no item)

### 8. switch_to_R — map R, ~1 min
- camera: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --river --labels; python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --river --goto C1`
- setup: seat: re-pin map R labels (the save's sidecar carries map C's only)
- look: -

### 9. C1_terraces — map R, ~6 min
- camera: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --river --goto C1`
  - view sprinkler rows (plot-local 36..46, 10..32): C1-local [36, 10, 11, 23]
  - view pole span over the dry ditch (plot-local 30..40, 34..40): C1-local [30, 33, 12, 8]
  - view terraces + river bank (plot-local 0..30, 20..41): C1-local [0, 20, 31, 22]
- setup: HE opens S1 (terrace 1's tail) and unpauses ~1 in-game hour; frame_rel = plot-local, add c1.origin from review/scenarios/map_r_placed.json
- look: the four sprinkler looks spraying; the pipe span sagging between poles; terrace 2's front; river vs canal blue
- **CARD:** Sprinkler heads (four looks)? — Keep all / Redraw one look / Redraw all · closes: SPRINKLER_HEADS_BUILD_PUMP_REQUIRED
- **CARD:** Pipe span on poles reads as? — A pipe on poles / A power line: redraw / Sag wrong · closes: PIPE_POLE_REDRAW_NOT_A_POWER_LINE, PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE
- **CARD:** Canal front speed along terrace 2? — Right / Too fast / Too slow · closes: (feel; a tune item if not right)
- **CARD:** River blue vs canal blue? — One water / Canal too dark / River too light · closes: CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES

### 10. C11_creek — map R, ~5 min
- camera: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --river --goto C11`
  - view R2 ford: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --river --goto R2`
  - view R3 weir: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --river --goto R3`
  - view R7 ferry rope: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --river --goto R7`
- setup: HE unpauses ~30 s at R2: the control colonist in the water is carried, the one on the stones is not
- look: ford stones read as stones; the weir; the rope above the water; the push of the current
- **CARD:** Weir art? — Keep / Redraw · closes: RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS
- **CARD:** Current push on a wader? — Right / Too strong / Too weak · closes: (feel; RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED rows)
- **CARD:** Ford stones and ferry rope? — Both read right / Stones read as dry ground / Rope sits in the water · closes: (look bars river_ford, river_works_looks)

### 11. overflow_on_terrace — map R, ~5 min (overflow stages 1-3 ARE in tonight's DLL)
- camera: `python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --river --goto C1`
  - view terrace 1 brim (plot-local 0..28, 31..36): C1-local [0, 30, 29, 7]
- setup: overflow ships OFF (master switch, global Mod Setting, not per map) and stays OFF for stops 1-10. Turn it ON only
  here, on map R: dev menu "RMFlowWorks / Canal overflow: switch on/off (test)" (message says ON), or seat:
  `python.exe Transient/pile_2026-10-22/walk_c7_probe.py 'call:jawa/mod_settings_field:{"typeName":"RimMandrake.FlowWorks.Sheet.RM_SheetSettings","action":"set","field":"sheetOverflowEnabled","value":"True"}'`.
  ⚠ REHEARSED 16:30: "S1 shut with the pump on" does NOT spill — nothing feeds terrace 1 above its brim (the bank pump
  fills the sprinkler tank; S0 held open for an in-game hour: sheet ledger in=0). So the seat makes the spill:
  `python.exe Transient/pile_2026-10-22/walk_c7_probe.py 'call:jawa/static_call:{"type":"RimMandrake.FlowWorks.Sheet.RM_SheetProofs","method":"ProofSheetSpill","args":"175,117;40000;Pump"}' ticks:250`
  (the production Offer path; 40,000 dL accepted, 250 ticks later 29 wet squares: 22 sheet + 7 film, max 1,699 dL),
  then HE looks and unpauses to watch it spread/soak. Rehearsal capture: walk_preview/zz_overflow_rehearsal2.png.
- **TURN IT OFF AFTER** (it is saved in Mod Settings, so it outlives the save): the same dev action again (message says OFF),
  or the seat command with `"value":"False"`, then read back (`"action":"get"` -> "False"). Do not save the game with it ON.
- known open: OVERFLOW_DIAGNOSE_FIRST_WET_RUN (rain spill, return-to-pit, ledger rows FAIL in the proof) — the look is still his.
- look: the spill sheet on the field
- **CARD:** Overflow sheet on the ground? — Right / Too blue / too thin / Spreads wrong · closes: CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED

## Proven today by agents — SKIP on the walk (source: belt.md 08:48-14:44 + walk driver 15:17-, 2026-10-22)
- Reel turns 4 ways: rot 0-3 read back, straight lays, build-preview exit line, old reels load West (state) — only the LOOK is his (stop 1).
- Pipe riser onto the tank flange: PASS by capture — only the look is his (stop 5).
- Empty-hose shadow alpha/width (0.80/0.85, 1.35/1.5): state PASS — the look is his (stop 1).
- Planked squares path + walk, open squares refused (PIT_COVER_WIDEN_PLANKS_BEAR_BOOTS, closed 41fb948b5e).
- Drill + bleed well refused on an empty survey; tank allowed (DRILL_PLACEMENT_ENFORCE_NO_DRY_HOLES, closed). Bleed well label + settings search 'bleed' PASS (BLEED_WELL_STRINGS_RENAME_TAP_RETIRED closed).
- lines_proof 11/11 (pipe poles A7-A10, cords, pit covers; LADDER_HOSE_DIAGNOSE_RETRACTS_ON_A_WHIM fixed 0ab8470911, closed).
- drawbridge_proof 12/12 (twice, incl. on ee9fa61fbc) — mechanics done; only PICTURES are his (stops 3-4).
- suspension_bridge_proof 26 PASS / 8 UNMEASURED (posts, grate, underpass A1-A7, jetty A1-A3 incl. 'Jump into pit', lake + sea waters); trench_cover 6 PASS + blast/cast A3/A4; raid_trench breach, ladder, siege, jump-pack rows (RAIDERS_TRENCH A2, A4-A7); trench crossing A2/A3.
- climb_proof 15 PASS; depth_rebuild_proofs 17 PASS (swim/sink, pit depth); validation_v2 62/62 on ee9fa61fbc.
- Pit access: rail ladder lowered from above, pit travel fly/jump/float, rescue ladder (pit_rescue_live 3/3), quarry find, cover deconstruct drops the rider — all DONE.
- Thirst 20 PASS (salt bottle fixed), sprinkler T22 + 8 rows, pond_pump, B2/B4/B5/B6/B7 live-session rows (fish roll, ice freeze/thaw, flood canal kept, settings dialog rows).
- REACH residual soak 0; wall-reach rebuilds tenfold fewer (WALL_REACH_TUNE_REBUILDS_TENFOLD A2/A3); station reach A2.
- FLOW_ORDER_EXTERNAL_INPUT_1 DONE: 6400-square network wets end to end off one inland source at 7.5 ms/pulse (his input: raise the 6000 cap?).
- Deep-lake refill restores the exact shape on c8eb3b2c83 (walk driver 15:50; DRAWDOWN item noted).
- Hose levelling between two ponds: 10,000 dL per 250-tick cycle, reels read "Levelling: flowing" (walk driver, fresh map) — only the SPEED feel is his (stop 6).
- Do NOT walk: C6 tar, C8 lock, C9 trench (raid branch), C10 basin — no his-eye question open there tonight; their signs stand for a later sitting.
- Still open (not walk stops; fixers): CAUSEWAY fill (rerun on a calm site owed), overflow first wet run, suspension buttons still showing, railing stuff=null, settings search misses checkbox labels, glow tank dry beside the sea, spill L5 narrowed.

## Not on the walk, needs him elsewhere
- Phone collections already sent: joint fittings A-N, pipe atlas A-D + pumps E-G, reel N/S A-P (answer by card; stop 1 shows the stand-in).
