# P5 + P6 build log — PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT, DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT (FOUNDRY offline builder, 2026-10-17)

Base: origin/main c0db19331 (P3 7b2fbe7a0, P4/P8 79ac42417). No bridge, no game.
Rulings (owner 2026-10-17, by card): default max colonist dig 8 m, settable 2..20 m; 0.5 m step stays; lakes keep their
own floors; the four 2 m-keyed rules become relative (P7, NOT done here); dig job/work-giver/designator read the grid;
4/7/7/4 square designable and dug; cost curve 3,200 x notch; settings in metres; lowering the cap never shallows.

## Stage (a) — cap sites re-checked at HEAD
- status: DONE. Every §1.3 site re-grepped at c0db19331; line numbers moved (kernel `Superdeep` :150, band loops :1289/:1322,
  sort keys :1827/:1839, gravity score :2038/:2053; map component Deepen :1238, FirstCutDepthAt :541, load repair :566, rain
  :2640). New finds not in §1.3: the load repair clamped D to 4 (would have SHALLOWED every deep cell on load); Deepen/FillIn
  counted `superdeepCellCount` on every cut past 2 m (not just the crossing); the legacy kernel's donor scores went negative
  (never picked) past 2 m and the gravity score `fn*10+dn` collides past 9 notches; validation_v2 S1n/S6 assume the 2 m cap.

## Stage (b) — constants split (PitDepth 4 / MaxDigDepth setting), dig code reads the grid, dig-to-N designator
- status: BUILT (uncommitted at this line). `RM_DigDepthMath` (Verse-free, in SelfTest): PitDepth 4, cap 4..40 default 16,
  MaxDigCeiling 40, WorkToCut. `RM_ExcavationDepth.MaxDepth` DELETED (Superdeep = the pit; MaxDigDepth = setting; MaxDigCeiling).
  Work-giver, designator, dig job read `ExcavatedDepthAt` (terrain only when no engine). `Designator_DigCanalTo` ("Dig to N m",
  float menu of depths with digger-days; re-targets ordered squares); target per cell `RM_digTargets` (scribed; absent = none);
  the job re-adds the designation after a landed cut until the target. Settings `maxDigDepth` (16) + `digCostRisesWithDepth`.
- Oracle differential 3000/3000 in depth, surface, levelset, shipped, pond, exact, exactpond (after the legacy-kernel bucket fix).

## Stage (c) — pocket bands/masks by climb limit, pictures (walls/sink), rain loop, collapse >2 m
- status: BUILT. Pocket grid + cliff masks sized `RM_PitTrapMath.ClimbBands` (K 1..6 = top size band + climber + leaper);
  `ClimbLimit` capped at 6; `RM_PocketGrid.MaxDepth` renamed `BandCount`. Effect: a huge K 4 is now held by a 3 m sheer step
  (was "climbs every step"); `BandText` says "bigger ... 4 levels (2 m)".
- Legacy notch kernel (exact level OFF): surface buckets 0..40 (`DepthCeiling`), taker key, donor scores rescaled
  (x64, sources 1,000,000) — order-preserving for depth <= 4 (oracle 3000/3000 all modes).
- Pit count: Deepen/FillIn count `superdeepCellCount` and notify pit rooms only on the 2 m CROSSING.
- Fall: caller passes 2 m (`RM_PitTrapMath.Superdeep`), not the cap, so falls do not soften (risk 6 of the plan).
- Rain: the per-pulse burst cap is its own constant (4); each square already takes only its own room (rain fills a 7 m pit).
- Pictures NOT changed (cosmetic, his look first, P9): sink capped at 2 m (`RM_PitDrawMath.SinkCapLevels`, renamed from
  MaxDepth), wall faces saturate at a 2 m drop, floors past 2 m all draw `RM_Channel_Superdeep`, AshDepthShade >= 4 same.
  Safe: every array clamps (no index past 2 m). A 7 m core and a 4 m ledge LOOK alike until P9.
- Live harness: validation_v2 phase S runs at the 2 m cap setting (S1n, S6 were 2 m-cap rows; S6 reason text now
  "deepest digging goes"); site_spec SETTINGS +maxDigDepth 16 +digCostRisesWithDepth; review_map_coverage +2 rules;
  validation.TOGGLES_NOT_ON_FLOOR +digCostRisesWithDepth; northstar toggle count 150.

## Stage (d) — P6 dig cost, settings text, tests
- status: DONE. Curve kept (3,200 x notch, `RM_DigDepthMath.WorkToCut`); setting "Each half-metre deeper costs more" (off =
  flat 12,800 a notch past 2 m, V1's other option); settings text in metres with digger-days computed from the code.
- MEASURED (vanilla JobDriver_AffectFloor does 1.7 work a tick x MiningSpeed, RimSage): one 7 m square 336,000 work =
  3.29 digger-days; the 4/7/7/4 square 2,726,400 = 26.73 digger-days (feasibility's 5.5 / 45 assumed 1 work a tick);
  flat option 1,638,400 = 16.06 digger-days. 8 m square 435,200 = 4.27 days.

## P7 hit-list (every absolute-2 m rule seen; P7 must handle) — none cemented anew by P5
- Spikes: `Superdeep/RM_Spikes.cs:50` `depth >= 4` (+ `PlaceWorker_SpikesOnSuperdeep`); V4.
- Shooting: `RM_Patch_SuperdeepShooting.cs:94-95` `IsSuperdeepExcavation` (ruling 23); V5.
- Drowning: `RM_PitFillEffects.cs:71` + `RM_FillEffectMath.DrowningPerCheck` ("never shallower than D=4"; rate = fill/depth,
  so 2 m of water in a 7 m pit drowns at 4/14 of the brim rate); V2.
- Falls: `RM_SuperdeepTrap.OnDescent` `FallDropScale(d, Superdeep)` (every fall past 2 m = the 2 m fall); V3.
- Rooms: `RM_PitRooms.cs:65,:67,:221,:271,:566,:615,:631` `IsSuperdeepRaw`; V6.
- Exposure: `RM_PitExposure.cs:33,:240`. Fire: `RM_LiquidFire.cs:506,:552,:846`.
- OFF-branch absolute trap (relative climb off): `RM_SuperdeepTrap.cs` (:88..:963), `RM_PitPathing.cs:71,:102,:128,:520`,
  `RM_PitTrapMath.IsPitDescent/StepBlocked`; `DryStepBaseCost` prices any drop INTO >= 2 m as a free fall (ledge 4 m -> core
  7 m included).
- Route cost: `RM_PitStepCost.cs:136` (wet pit planning cost = a pit's). Pit cover: `Building_PitCover.cs:283` placeworker.
- Labels: `RM_ExcavationDepth.LabelOf` "pit" from 2 m; `RM_Patch`/proof text `lipSuperdeep` (`RM_NorthstarProofs.cs:530`).
- Pictures (P9, not P7): `RM_PitDrawMath.SinkCapLevels`, `RM_WallFaceMath` arrays, `AshDepthShade`.

## Tests
- SelfTest 506/506 (+6 `DeepDig_*`: cap 2/8/20 + never shallows; no dig code reads terrain; cost numbers; the 4/7/7/4
  square digs by 16 orders/152 cuts, holds 152,000 L, brim-full one body gap < 1 cm, 56,000 L settles ring 1 m / core 4 m,
  under the ledge the ring stays dry; legacy notch kernel past 2 m conserves; pockets by band K 1..6, ladders/ramps by delta,
  pit rules past 2 m, fall not softened, pit counted at the crossing).
- Oracle differential 3000/3000 x 7 modes (depth, surface, levelset, shipped, pond, exact, exactpond).
- vv_shipped_matrix --skip-ep: SHIPPED kernel_fuzz 0/10000, fills_from_limitless 0/10000, surface_random 0/1000, seq_* 0,
  hose 0/2798, trail 0/1500; control 194/2000; VERDICT FAIL only on BENCH's AUTHORED `Thirst_slime_last_resort_ruled` (known);
  OFF_edgeSinksEnabled kernel_fuzz 142/2000 (known harness red). Forced-flag suite runs fail the two DeepDig cases that pin
  exact level on/off (as the other authored-flag cases do; not a verdict input).
- Python: selftest_flowworks_northstar only the known RM_ThirstSettings red (toggle count 150); selftest_extensions only the
  known thirst-toggle red; selftest_human_review only the known `still_water_one_surface_height` red; review_map,
  settings_registry, level_water, call_sites, looks_round, conservation, climb_proof, deep_lake_proof, fw_walks PASS.
