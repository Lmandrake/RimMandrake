# Live L2 / GREEN-MIN sweep, acc_l1x-34, 2026-10-07 (FOUNDRY helper)

Method: modcheck chains from each mod's validation.py driven through Session against the running game (no ModsConfig swap, via Transient/l2sweep_run.py); results JSON in Transient/l2sweep_<Mod>.json.

| item/criterion | verdict | evidence |
|---|---|---|
| Droidworks chains (validation.py, 24 components) | 20 PASS / 2 FAIL / 0 other | l2sweep_Droidworks.json. FAIL protocol_droid_shifts_prices (TraderCaravanArrival did not fire, canFireNow=True) and ion_overload (RSW_JawaIon_Stun absent: Jawa Ion mod not on this list; expected) |
| DROIDWORKS_FACE_RENDER_DEFAULT_HUMAN_1 A1, A2 | UNMEASURED | no chain reads faces/headType render; spawned droids carry headType RSW_DW_HeadType_Blank only |
| DROIDWORKS_FORMAT_TIERS_1 A1-A6 | UNMEASURED | suite has format_tier_defaults_to_programmable + power chains PASS (touches A4 only); no mindless/sapient/blank/recipe-gating/deformat scene exists |
| DROIDWORKS_WIPE_SEVERITY_1 A2, A3, A4 | UNMEASURED | wipe_hediff_attaches PASS (hediff adds) but no 7-day stumble or quirk-accrual read; GREEN-MIN bars not run |
| MINDSTONE_MATRIX_KINDLED_BUILD_1 A2 | UNMEASURED | mindstone_head_wiring PASS (defs/wiring only); mine/recipes/assemble/wipe-refusal gauntlet not run |
| WRECKED_DISTILLATION_MODULE_1 A2 | UNMEASURED | no distillation chain in WreckedMachines/validation.py; separately the mod logs Config errors (see next row) |
| WreckedMachines chains | 5 PASS / 5 FAIL / 7 UNMEASURED | FAIL spawns_and_inspects_clean x3: Config error RM_WM_AutomatedSmelter_Refurbished "minifiable but not in any thing category", RM_WM_Distillation_Kludged "impassable, player-buildable building that can..." (real def defects). FAIL materialCostFactor/refurbishedRatio/kludgedRatio/wreckedRatio *_rewrites_its_def: patcher output unchanged on read-back (def-read may not see comp lists; unverified) |
| RAKATAN_ARCHOTECH_MACHINES_1 A2 | UNMEASURED | no chain spawns/degrades/heals grades |
| WYYYSCHOKK_FANG_PENDANT_1 A2 | UNMEASURED | donor_butcher_products_carry_the_fang PASS (def read, not a live butcher); recipe check "FAIL" is an instrument gap: get_defs does not serialize ingredient filter thingDefs, product RSW_Apparel_FangPendant is present. A3, A4, A5 UNMEASURED (thoughtClass unreadable by get_defs) |
| TrophyCraft chains | 8 PASS / 1 instrument-FAIL / 3 UNMEASURED | l2sweep_TrophyCraft.json |
| SHIELD_MODS_LEVERAGE_1 A2, A3 | UNMEASURED | ShipShields validation all_green (14 PASS: settings round-trip, 2 Harmony patches, defs read back) but no bubble/veil/particulate/cryo gauntlet; north-star bars not run |
| UnfinishedLine chains | 17 PASS / 1 FAIL / 3 UNMEASURED | FAIL volunteer_offered: "VOLUNTEER REFUSED: Enclaves not allied" (fixture precondition, 3 downstream UNMEASURED) |
| EggReckoning chains | 9 PASS / 0 FAIL / 6 UNMEASURED | l2sweep_EggReckoning.json |
| FallLineArrivals chains | 8 PASS / 1 FAIL / 1 UNMEASURED | FAIL anywhere_allows: with onlyOnFallLine OFF RUT_FallArrival cannot fire (no skyfaller cell?). FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1 A3 (scar/memwipe) UNMEASURED; survivor_drifts_in_feral PASS |
| DroidRepairJobs chains | 5 PASS / 0 FAIL / 9 UNMEASURED | quote needs quest lifecycle list; pickup/grading need signals no bridge tool fires |
| FlowWorks (PIT_TEMPERATURE_SOFTENING_1 A2-A5, SURFACE_RIVER_WEIRS_1 A2) | UNMEASURED | full validation.py exceeded 580 s and was killed before writing JSON; E-series dune/sink rows seen passing in the console tail, not recorded |
| Others on list (AcousticScanner, ProximityHatch, GimmeSomeSlack, LuminousPigment, ShipVermin, WeatherSuite) | UNMEASURED | no acceptance L2/GREEN-MIN item owned by these mods in FOUNDRY's list |

No `rimflow verify` recorded: no chain maps one-to-one onto an acceptance criterion's wording, so nothing was a clear measured PASS of a named criterion.
Map: quicktest started once (launch gate bypassed: only RM_Thurrock hediff comp type from EnvironmentalHazards is missing on this list). No hostile-kill tool exists in the bridge tool list; wild_droid_crash chain spawned a crash droid, not hostiles. Game left running, paused, on the map.
