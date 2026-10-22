# FlowWorks completion plan (BENCH, 2026-10-21)

Planning helper output for the owner's order of 2026-10-21: *"Push Flowworks all the way to completion. I can review
question cards as per the skill. I can review art sheets. Whatever you need. In game walks live."* Read-only pass:
no source, ledger, bridge or game touched. Everything below is MEASURED 2026-10-21 unless marked otherwise.

## Definition of complete

Taken from the repo, not invented. FlowWorks (`mandrake.rm.flowworks`) is complete when **all five** of these hold:

1. **North star VALIDATED at the current hash.** `design/validation_walks/RimMandrake/FlowWorks.md` `## north star`
   reads `state: DRAFT`, `validated-hash:` empty (MEASURED). It now holds **73 must-show + 8 cannot-show bars**,
   16 accepted at the 2026-10-20 sitting (`design/RimMandrake/flowworks_bars_answers_2026-10-20.md`) plus R9
   `still_water_one_surface_height` and four reworded bars (`FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING`). Only the
   owner validates. One proposal is still outside the section: `hose_and_pipe_girth_sensible` (judged at an
   in-game look, `HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME`).
2. **`modcheck floor --all` reads `bar met` for FlowWorks** (GimmeSomeSlack already does: VALIDATED 9/9). Today's
   row (copy dated 2026-10-21 20:27): `FlowWorks … DRAFT 0 0 0 UNMEASURED no bar`. That requires:
   - a live `validation_v2_result_*.json` at the **current** mod hash. Newest is 20261017T212648, 61/61 PASS, at
     an older hash, so it no longer counts;
   - a live `proof_hose_*.json` at the current hash (newest is 2026-10-11);
   - every bar claimed by a row that actually runs. `validation.py` `EXTENSION_ONLY_BARS` lists **21 bars claimed
     only by extension chains**; 16 of them, the 2026-10-20 bars, are claimed only by UNMEASURED components. That
     list is the owed promotion work.
3. **`FLOWWORKS_NORTHSTAR_SHIP_1` acceptance** (plan `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §5):
   - code review 0 DIRTY. MEASURED today: **97 DIRTY / 422 CLEAN** over tracked .cs/.xml/.py outside
     northstar/, selftests and Tools/. That is 63 .cs (Hose 10, Superdeep 10, Machinery 9, Pits+Drawbridge 7,
     SelfTest 17, …), 14 .xml and 20 .py;
   - Mod Settings superb;
   - FlowWorks' own art for every visual bar, with nothing left on `TrapSpikeArmed`;
   - deploy in sync;
   - `PIT_SUPERDEEP_COLLAPSE_1` closed.
4. **The owner signs off the 1.0.0 release candidate.** `src/RimMandrake/FlowWorks/CHANGELOG.md` says *"Still not
   signed off by the owner (review walk in progress)"*, and the packaged DLL hash line must match.
5. **Every open in-scope ledger item is closed or dropped** (census below). A `built` item still owes its
   live/verify run, and a `validated` item still owes its close.

GSS enters only through (a) `PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES`, where the GSS power-lines master switch hides
FlowWorks pipe poles; (b) the line-width / girth spec shared by cords, hoses and pipes
(`LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED`, `POWER_CORD_*`); and (c) `hose_drawn_under_overhead_span`.

## Census

**Method.** Merged ledger via `model.replay(model.read())`, 929 open items at 2026-10-21 ~21:00 PDT. FlowWorks scope =
open items whose ID or title names FlowWorks or a FlowWorks mechanism (canal, pit, ladder, hose, pipe, pump, tank,
sluice, trench, suspension, liquid, pond, river works), or whose prose names FlowWorks at least twice. Biome-sprint
items that only *use* FlowWorks were dropped by hand: Cauldron, Crackedlands, Forge, Scald, Sump, Vault, Warscar,
Glow tank, Hutt pit, Taken-by-land, worldmap tags, world paths, river steam, Stillsand ledger, liquid industry,
thirst chain, Vexxith, glass. **Excluded per brief:** `DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS` and
`DRAWBRIDGE_RAID_DIAGNOSE_LOITERING_AT_MOAT` (helper on them now).

**In scope: 109 open items** (MEASURED by script). By state: built 41 · proposed 29 · validated 22 · doing 17
(14 of the doing items sit on the OWNER seat). The 63 built + validated items split three ways (MEASURED):
- **43** owe at least one live (L2/L3) row;
- **17** owe only an L1 selftest record. Packet K0 below, no game needed;
- **3** owe only the owner or a GREEN tier: FLOWWORKS_LADDER_RAISE_LOWER_1 (L4), NORTHSTAR_GREEN_FULL_1,
  NORTHSTAR_TRIAL_1.

`L1` = offline selftest recorded with `rimflow verify`; `L2` = a live row; `L4` = the owner's look.

### A. Built, waiting on a live row (L2): the bulk of the work. Each needs one live run plus `rimflow verify`.
| item | outstanding | proof that carries it |
|---|---|---|
| SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS | A1-A8 L2 | `northstar/suspension_bridge_proof.py` |
| SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD | A1-A7,A9 L2; A8 L4 | suspension_bridge_proof |
| SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP | A1-A4 L2 | suspension_bridge_proof |
| SUSPENSION_JETTY_BUILD_WALK_THE_PLANK | A1-A3 L2 | suspension_bridge_proof |
| SUSPENSION_WATERS_BUILD_MAY_BACKTRACK | A1-A4 L2 | suspension_bridge_proof (river site) |
| SUSPENSION_LIVE_DIAGNOSE_FIRST_REAL_RUN | A1-A2 L2 | suspension_bridge_proof (rerun after fixes) |
| SUSPENSION_ART_RESKIN_HE_SEES_FIRST | A1 L1, A3 L2, A2 L4 | art check + owner sheet |
| UNDERPASS_REACH_VERIFY_WALK_UNDER_FOR_REAL (proposed) | live row | suspension_bridge_proof / climb_proof |
| RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP | A2-A7 L2 | `northstar/raid_trench_proof.py` |
| TITAN_TRENCHES_WIRE_MIND_THE_GAP | A1-A5 L2 | raid_trench_proof (titan row) |
| TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP | A2-A3 L2 | climb_proof |
| TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT (validated) | A3-A4 L2 | `trench_cover_proof.py` |
| PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH (proposed) | save/reload pockets FAILED twice | climb_proof + raid_trench_proof |
| PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS (validated) | A4 L2 (verify FAIL B4_access_rescue), A5 L4 | live_session B4 |
| WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS | A2-A5 L1 | selftests only |
| FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT | A4 L2 | climb_proof |
| FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE | A4 L2 | climb_proof / lines_proof |
| PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO | A2 L2 | trench_cover_proof / v2 P-rows |
| FLOWWORKS_PITCOVER_FIX_BURNS_PAWN_UNHARMED (proposed; offline fix landed) | live | v2 P-rows |
| FLOWWORKS_PITFALL_FIX_HISTORY_NOT_SAVED (proposed; fixed 34d0e4db72) | save round trip live | climb_proof save/reload |
| PIT_LIP_FIX_BOAR_HANGS_OUT · PIT_LIP_OCCLUDES_OUTSIDE_1 | L1/L2 | owner_review_stage (visual) |
| FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE | A4 L2 | proof_hose / lines_proof |
| PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE | A2 L1 | selftest |
| PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL | A3 L1, A4-A5 L2 | lines_proof / pond_pump |
| PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE (validated) | A1-A3 L1, A7-A10 L2 | lines_proof (7/9 today) |
| POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS (validated) | A1-A2 L1 | selftest (GSS side) |
| PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES | A2-A3 L1 | GSS SwitchFlipChecks |
| HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD (validated) | A2,A5 L2 (A5 FAIL), A4 L4 | proof_hose |
| HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE (fix 86e8a90bfe) · HOSE_LAY_POLISH_CENTRE_VS_MOUTH (F2 only) | live | proof_hose |
| SPRINKLER_HEADS_BUILD_PUMP_REQUIRED (doing, verify partial) | rest of rows | `sprinkler_live.py` |
| THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY (doing, partial) · SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING (A1-A2 L3) · THIRST_RULES_BUILD_SALT_OFF_THE_MENU (OWNER doing) | live | `thirst_live.py` |
| FLOWWORKS_CONTAINER_MATERIALS_1 (validated) | A2 L2, A3 L4 | bottle chain (~10 min) |
| LIQUID_LEDGER_BUILD_NO_UNIT_LOST (validated) | A4-A7 L2, A9 L4 | live_session (L5 was HARNESS) |
| POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD (validated) | A5,A7 (FAIL),A8 L2 | live_session B4 reservoir |
| WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES | A2 L2 | `level_water.py` / level_surface_bar |
| LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP · FISH_ROLL_MEND_PONDS_BORN_BARREN | A2 L2 each | `deep_lake_proof.py` |
| FLOW_ORDER_EXTERNAL_INPUT_1 | A3 L1, A4 L2 (re-run after P3 solver) | v2 / extension |
| LIQUID_LOOK_MATERIAL_OWNERSHIP_1 | A1 L2 (~5 min toggle x3) | extension chain |
| MISSION_TANK_GOAL_REWIRE_TO_DEST | A2 L1 | mission chain |
| EXCAVATION_LEGACY_MIGRATION_FLAG_1 | A1-A2 L2 | save-load chain |
| FLOWWORKS_QUARRY_DIGGING_1 (validated) | A3-A5 L2 | dig_finds chain |
| RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED | A1-A6 L2, A7 L4 | `extension_proof.py --chains` river toggles |
| FLOWWORKS_CHECKOUT_SCOPE_1 | A2 L2 | one full extension run after a v2 GREEN |
| 5 GPT-P mends, validated, A2 L2 each: FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO, HEAT_BUDGET_PREFIX_MEND_LATE_CELLS_STARVE, NATURAL_HEAT_CACHE_PROVE_STALE_DAYS, STATION_REACH_CENTRE_RETHINK_FOOTPRINT, TAR_COOLING_GLASS_MEND_ENGINE_CELLS | live call-site rows | v2 / extension |
| 3 GPT-P fixes, built, A1 L1 only: FLOWWORKS_CONVERTER_FIX_BLOCKED_STARVES_REST, FLOWWORKS_REACTOR_FIX_STUCK_ENDS_SHIFT, FLOWWORKS_RIVERCOLOR_FIX_DICT_SELF_ENUM | selftest record | offline |
| PIT_ALERT_BUILD_RED_MEANS_HELP · PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER (validated) | A1 L1 each | selftest record |
| PIT_TEMPERATURE_SOFTENING_1 (validated) | A2-A4 L2, A5 GREEN-MIN, A6 L4 | v2 + owner |
| SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST | A2-A3 L1; *"GSS finish → Done after one live pass"* (card 2026-10-20) | settings live pass |
| TESTENV_FLOODS/HIVES/MEGAPEDE/TRIALSITE (4, built, A1 L1) | selftest record | offline |

### B. Built in git, but the ledger still says `doing` (OWNER seat, filed at the 2026-10-16 station walk)
The build note is in the ledger in every case. These owe a live check and an `implemented` event, not code.
SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR (0cdbb186fc) · TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH (19e8ab2abb + CompTankLook) ·
FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS (b696fdb9a2) · FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES (5123b02d8a,
81a6554fbd) · SLIME_CROSSING_BUILD_SLIPPERY_SLOPE (0dcef50bcd) · LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS (2f36d28bc9,
24e78bfd4e) · HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY (815142f404, 52b4167026; sheet up) · DIG_ROCK_TUNE_STONE_FIGHTS_BACK
(kept, rides on the dig cost curve) · PIT_LADDER_REDRAW_HUNG_ON_THE_WALL (art candidates 3a7f1aa9ca, sheet) ·
PIT_SPIKES_SHRINK_HALF_A_MAN (sheet 04bff67a92, v6 recommended) · TAR_LOOK_TUNE_THICK_AND_SLOW (needs game-up, tuned
with him) · GSS_CORD_SILENCE_PHANTOM_SPARK · FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS.

### C. Needs the owner (card, sheet or walk)
FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING (re-validate the hash) · HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME +
LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED (the in-game width look; spec ruled in
`design/RimMandrake/flowworks_line_widths_2026-10-20.md`) · INSITU_ART_JUDGE_SAVES_KEPT_WARM · WATER_SCENES_S5_JUDGE_THIRD_DRAFT ·
RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS · WATER_DEPTH_RESKIN_HE_LOOKS_FIRST · CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES ·
RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS · CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED (D2-D7 open,
`design/RimMandrake/canal_overflow_flooding_2026-10-21.md` §5) · DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL (re-scope) ·
PIT_TRAVEL_TAGS_VET_LORE_FIRST_GUESS (blocked on purpose until the animal pass, so not on tonight's path) ·
GUARDRAIL_ART_RESKIN_BORROWED_FENCE (cosmetic, needs his permission) · every L4 criterion above.

### D. Unbuilt FlowWorks work (proposed)
CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES · PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS · WET_FOXHOLE_BUILD_COLD_FEET_SHAKY_AIM ·
FLOOD_STATION_REWIRE_DRY_CANAL_STAYS_DRY · CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED (after D2-D7) ·
FLOWWORKS_REVIEW_LOOKS_ROUND_1 (items 2, 3, 5 and 7-11 built offline, live owed) · JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS.

### E. Umbrellas: close last, no work of their own
FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG (epic) · PIT_SUPERDEEP_COLLAPSE_1. 13 of 15 children are done; the other two,
PIT_TEMPERATURE_SOFTENING_1 and EXCAVATION_WALL_ART_1, are validated. Its verify lines are MEASURED today: no
TrapSpikeArmed in FlowWorks Defs, and `Pits.md` is gone. All that is left is "north star VALIDATED on his word".
FOUNDRY took a lease on it today. · FLOWWORKS_NORTHSTAR_TRIAL_1 · FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1 ·
FLOWWORKS_NORTHSTAR_GREEN_FULL_1 (a cold load of the full list, ~25 min) · FLOWWORKS_NORTHSTAR_SHIP_1. SHIP's scope
was set by card on 2026-10-18 (*"what counts as finished → everything filed"*). · FLOWWORKS_PLAYTEST_CAMPAIGN_1 ·
FLOWWORKS_VISUAL_PRINCIPLES_1 (A2 L2, A3, A4 L4) · EXCAVATION_WALL_ART_1 (A3-A5 L3/L4).

## Dead items

None closed here; that needs a ledger write, and this pass was barred from making any. Each row cites its proof.
"Close-ready" means the work is done and only the ledger lags.

| item | verdict | proof |
|---|---|---|
| `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` | **premise dead.** Drop it or re-scope it by card (card Q4) | Ledger note 2026-10-17: *"its premise 'digging deeper than 4' is gone; colonists dig to 8 m by default, 2-20 m setting"*. `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT` is **done** (MEASURED). |
| `FLOWWORKS_LADDER_RAISE_LOWER_1` | **overtaken.** Supersede by `PIT_LADDER_REDRAW_HUNG_ON_THE_WALL` | Mechanics PASS (v2 P4/P4b; playtest 2026-10-11). The only thing left, A2 (L4, *"owner confirms ladder art"*), is the art that PIT_LADDER_REDRAW's sheet replaces (3a7f1aa9ca), together with the rail ladder `FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE`. |
| `HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME` | **duplicate.** Fold into `LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED` | Both items are the same in-game width look beside a colonist. LINE_WIDTH holds the ruled spec (*"pipe 30 cm; hose half the pipe; cord = GSS wire"*, by card) and covers cord too. |
| `PIT_LIP_OCCLUDES_OUTSIDE_1` | **close-ready** once the live re-shot is recorded with `rimflow verify` | Ledger 2026-10-07: *"Fixed a100d8e2e … Re-shot … live: upper half shows inside the pit, lower half behind the lip, no rectangle"*. Later work on the same quad: PIT_LIP_FIX_BOAR_HANGS_OUT (88a14262f3). |
| `PIT_SUPERDEEP_COLLAPSE_1` | **close-ready the moment the owner validates the north star** | Umbrella: 13 of 15 children done and 2 validated (MEASURED). Its verify lines also MEASURED today: no `TrapSpikeArmed` in FlowWorks Defs, and `design/validation_walks/RimMandrake/Pits.md` is absent. The one line left is *"north star … VALIDATED on his word"*. |
| 7 OWNER-seat `doing` items in Census §B: SLUICE_GATE_REWIRE, TANK_LOOKS_WIRE, FLOW_SOURCE_SINK, FLOW_CONTROLS, SLIME_CROSSING, LIQUID_CONTAINERS_REDRAW, HOSE_JOINTS_REDESIGN | **not dead; the state is wrong** | Each ledger note says "Built <sha> … live check owed", and each sha is in `git log`. They need `implemented` plus one live row, not more building. |
| `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` | **not dead, only stale** | It went GREEN twice: 74P/0F on 2026-10-05, and 61/61 in `validation_v2_result_20261017T212648.json`. Both runs were at older mod hashes, so it needs a re-run at the current hash, not a fix. |

Checked and **not** dead: `FLOWWORKS_PLAYTEST_CAMPAIGN_1` and `FLOWWORKS_REVIEW_LOOKS_ROUND_1`. A truth pass on
2026-10-18 says neither is superseded. `HOSE_LAY_POLISH_CENTRE_VS_MOUTH` is narrowed to F2 but still live.

## Packets

Each packet is ~30-90 min for one helper. Tags: OFFLINE-CODE (names the `Source/` files it may edit, so that two
helpers never edit or build FlowWorks at once) · LIVE (needs the bridge; names the proof) · OWNER-CARD · OWNER-SHEET ·
OWNER-WALK.

🔴 **Build lock:** one FlowWorks DLL build at a time. The drawbridge pair helper is in
`Source/Pits/Drawbridge/*` and may touch `Superdeep/RM_PocketGrid*.cs` (the winch reach). Any packet that touches
those waits for it.

🔴 **Bridge lock:** one LIVE packet or walk at a time (`rimflow bridge take`). Walks need the bridge free of the
drawbridge helper.

### Owner packets (he is present now)

**C1 — OWNER-CARD: re-validate the FlowWorks north star** (`FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING`).
Question: *"FlowWorks' north star now has 81 bars: the 16 you accepted on 10-20, the new 'still water is one flat
surface' bar, and four bars reworded for metres. Validate the section as it stands?"*
- **Validate now:** the hash is recorded, and PIT_SUPERDEEP_COLLAPSE_1 can close.
- **Show me the changed bars first:** a one-page diff of 21 bars, then the same card.
- **Hold:** wait until the pipe/hose girth look is done.

`hose_and_pipe_girth_sensible` stays a proposal either way. This is the gate on completion criterion 1, and a
validation is his alone.

**C2 — OWNER-CARD: reachability sees walls and depth together?** Source:
`Transient/pile_2026-10-21/relativeveto_options.md` (draft ruling line at its end). Question: *"A colonist can be told
a place is reachable when a wall plus a trench actually cuts it off, so jobs get offered and then fail in a loop. How
should we fix it?"*
- **(d)+(a), recommended:** a second, wall-aware map used only for the "can I get there" check. Trapping, rooms and
  ladders stay depth-only. The winch path check stays.
- **(a) only:** patch each of our own jobs one at a time. Cheap, but the bug class stays open.
- **(b):** make pits themselves wall-aware, as the old design literally says. A wall could then trap pawns.
- **Leave it for now.**

**C3 — OWNER-CARD: canal overflow, D2-D7** (`CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED`; D1 is already answered as
"spill"). Source: `design/RimMandrake/canal_overflow_flooding_2026-10-21.md` §5. One card, six questions, each with
the doc's recommendation first:
- **D2 — what may overflow?** Pumps, rain on a brim-full canal, driver floods and kits. Options: all three
  (recommended) / pumps only / none.
- **D3 — crops under a spill:** drown after 12 h of sheet-deep water (recommended) / drown at once (vanilla) /
  never.
- **D4 — doors:** block water (recommended) / leak slowly underneath.
- **D5 — may a fuel spill spread and burn?** Yes, with its own setting (recommended) / never.
- **D6 — soak-in, evaporation and "joined the lake"** count as disclosed exits in the no-unit-lost ledger: accept /
  refuse.
- **D7 — shipped default** once validated: on / off.

Plus a check on Pillar 2: *"the sheet moves on the engine pulse, not per tick. Is that inside 'no per-tick fluid
sim'?"* Options: yes / no.

Plus a scheduling question: *"Must overflow be in 1.0, or may it follow in 1.1?"* Options: in 1.0 / 1.1. It is the
longest unbuilt branch.

**C4 — OWNER-CARD: three small rulings.**
- (i) `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL`. Its premise is gone now that colonists dig to 8 m. Options: drop it /
  machines and droids dig like colonists, nothing deeper / a machine may dig past the colonist cap.
- (ii) `GUARDRAIL_ART_RESKIN_BORROWED_FENCE`. The pit guardrail wears vanilla fence art, and a cosmetic change needs
  his permission. Options: yes, make our own guardrail art (goes to the art pipeline) / keep the fence.
- (iii) *"Does FlowWorks finish only after a GREEN run on your full 639-mod list (one ~25 min cold load), or is the
  minimal test list enough?"* `FLOWWORKS_NORTHSTAR_GREEN_FULL_1`'s acceptance says full. Options: full list / minimal
  is enough.

The two housekeeping moves (ladder raise/lower superseded, girth items merged) need no card. They are
correctness edits any seat makes (K0).

**S1 — OWNER-SHEET: art sheets that already exist.** One sitting, served via `serve_gated.py`.
- `Transient/biome_ffar/liquid_connections_sheet_2026-10-16.html` (HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY: pumps,
  flanges, saddles × 4 looks + 9 join mocks). ⚠️ Its decisions file holds `A` on all 21 rows with empty notes. Treat
  that as possible prefill until he confirms it.
- `Transient/biome_ffar/pit_ladder_hung_sheet_2026-10-16.html` (PIT_LADDER_REDRAW_HUNG_ON_THE_WALL: hung + stowed).
  Its decisions file also holds all `A`, with the same caveat.

Spikes need no sheet: he picked `B` on 2026-10-16, and they were redrawn top-down at 41cc8b8dcd. That is judged on
walk W1. Per memory, *visuals are reviewed in game*, so S1 is only for picks among candidates. Every
look-at-it-placed judgement goes to a walk.

**S2 — OWNER-SHEET (must be built first): suspension bridge four looks + liquid containers four styles.**
- `SUSPENSION_ART_RESKIN_HE_SEES_FIRST` A2 (L4): 63 textures, installed d0b53e8c49.
- `LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS`: 24 PNGs, installed 2f36d28bc9.

Build with `art_sheet.py` (true scale beside a human; rimworld-review-sheets skill), about 30 min of agent work
before he looks. Also `WATER_SCENES_S5_JUDGE_THIRD_DRAFT`: approve scene S5
(`design/RimMandrake/vv_methods/water_scenes_for_approval_2026-10-16.md`). It is a doc, not art, and fits the same
sitting.

**W1 — OWNER-WALK: the staged review map** (`northstar/owner_review_stage.py`, already built: ladders inside the dug
squares, spikes dry and wet, sluice and grate gates in all four facings plus held open, water ladder, sprinklers,
hoses/girth). Prep: `--dry-run`, then LIVE on a disposable Playing map and save ONE named savegame (memory: options
he must look at ship as a savegame). He judges:
- the rail and hung ladders (`FLOWWORKS_RAIL_LADDER_*`, PIT_LADDER_REDRAW)
- spikes half-a-man (PIT_SPIKES_SHRINK_HALF_A_MAN)
- sluice turning like a door (SLUICE_GATE_REWIRE)
- sprinkler heads in 4 looks (SPRINKLER_HEADS, INSITU_ART_JUDGE)
- pit lip on a lying boar and a muffalo (PIT_LIP_*)
- pump with 4 side ports, pipes to the centre (FLOWWORKS_PUMP_PORTS, PIPE_ENDS)

These cover the L4 criteria of about 8 items. Add the titanoslime stage-1/5 staging INSITU_ART asked for only if it
is cheap.

**W2 — OWNER-WALK: lines beside a colonist** (`LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED` + `HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME`).
Stage with `owner_review_stage.py --only hoses`, plus a GSS cord and pole on the same map. He judges:
- pipe 30 cm / hose half / cord = GSS wire, beside a colonist;
- pipe-pole sag (PIPE_POLES A7-A10 look);
- a hose under an overhead GSS span (`hose_drawn_under_overhead_span`).

This decides the proposal `hose_and_pipe_girth_sensible` (accept as a bar or not).

**W3 — OWNER-WALK: water and depth.** He judges:
- the depth ladder past 2 m: deeper wall faces, pawn sink by drop, floor tint (`WATER_DEPTH_RESKIN_HE_LOOKS_FIRST`,
  his look first);
- swimming at 2 m+;
- one flat surface per body;
- canal-vs-lake two blues (`CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES`, so he sees the defect before we fix it);
- weir and river works (`RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS`);
- the tar look, tuned live with him (`TAR_LOOK_TUNE_THICK_AND_SLOW`, the bridge tools `liquid_look_get/set`);
- slime crossing (SLIME_CROSSING).

Sites: `water_scenes_walk.py` and `river_scenes_walk.py`.

**W4 — OWNER-WALK: bridges and trenches.** Suspension bridge, underpass, grate over fire, jetty, river span, all in
the four looks in game, plus trench cover and raiders at a trench. Do this **after** L2/L3 below are green, so he is
shown working mechanics. It covers SUSPENSION_UNDERPASS A8 L4, PIT_ACCESS A5 L4 and FLOWWORKS_VISUAL_PRINCIPLES A4.

**W5 — OWNER-WALK + sign-off: the release walk.** Do this last. The 1.0.0 CHANGELOG says *"not signed off by the
owner (review walk in progress)"*. He walks the finished mod on the full list and says ship. Closes
FLOWWORKS_NORTHSTAR_SHIP_1 and _TRIAL_1.

### Live agent packets (bridge, one at a time)

**L1 — LIVE: the core floor at the current hash.** Run `northstar/validation_v2.py --live --fresh-map` (flowworks
tier) and `northstar/proof_hose.py`, then `modcheck record FlowWorks --result <json> --tier flowworks`. This makes
the floor row MEASURED again. The last v2 run was 61/61 at an old hash, so expect green. It is a prerequisite of
GREEN_MINIMAL. Run it first after the bridge frees.

**L2 — LIVE: `suspension_bridge_proof.py` full run.** Records L2 for the 7 SUSPENSION_* items and
UNDERPASS_REACH_VERIFY. Read failures with the live-debugging-proof-harness skill (MOD/SITE/HARNESS).

**L3 — LIVE: pits and trenches.** `climb_proof.py` + `raid_trench_proof.py` + `trench_cover_proof.py`. Covers:
- RAIDERS_TRENCH A2-A7 · TITAN_TRENCHES A1-A5 · TRENCH_CROSSING A2-A3 · TRENCH_COVER A3-A4;
- PIT_CLIMB_PROVE. Its save/reload pockets FAILED twice, which is a probable MOD finding, so file one if it repeats;
- FLOWWORKS_PIT_TRAVEL A4 · RAIL_LADDER A4 · PIT_ACCESS A4 (verify FAIL B4_access_rescue);
- FLOWWORKS_PITFALL_FIX save round trip · FLOWWORKS_PITCOVER_FIX · PIT_COVER_DECONSTRUCT A2.

May split into L3a (climb + save) and L3b (raids).

**L4 — LIVE: lines and hoses.** `lines_proof.py` + `proof_hose.py` rows. Covers:
- PUMP_PORTS A4 · PIPE_LEVELLING A4-A5 · PIPE_POLES A7-A10;
- HOSE_RULINGS A2 and A5 (A5 FAILED 2026-10-18; diagnose first) · HOSE_PATHING (fix 86e8a90bfe) · HOSE_LAY F2.

**L5 — LIVE: water, thirst, sprinklers.** `thirst_live.py`, `sprinkler_live.py`, `level_water.py`, `deep_lake_proof.py`
and the bottle chain. Covers:
- THIRST_BUILD_OWN_BOTTLES · SALT_BOTTLE · THIRST_RULES · SPRINKLER_HEADS · CONTAINER_MATERIALS A2;
- LIQUID_LEDGER A4-A7;
- POND_DEPTH A5/A7/A8 (A7 FAILED);
- WATER_LEVEL A2 · LAKE_FLOORS A2 · FISH_ROLL A2 (its earlier FAIL was HARNESS).

**L6 — LIVE: extension chains.** `northstar/extension_proof.py --live --chains` covering:
- the river toggles (RIVER_TOGGLE_PROOFS A1-A6);
- liquid looks toggled ×3 (LIQUID_LOOK_MATERIAL);
- the mission chain (MISSION_TANK) · dig_finds (QUARRY A3-A5) · legacy save-load (EXCAVATION_LEGACY);
- FLOW_ORDER A4 after the P3 solver;
- the 5 GPT-P call-site rows (FLUID_PALETTE, HEAT_BUDGET, NATURAL_HEAT, STATION_REACH, TAR_COOLING);
- one full extension run right after an L1 GREEN (FLOWWORKS_CHECKOUT_SCOPE A2).

**L7 — LIVE: state reads for the OWNER-seat built items.** Covers SLUICE rotation, FLOW_SOURCE_SINK
(`RM_MapControls.PlaceSource/PlaceSink` static_call), FLOW_CONTROLS (six controls), TANK_LOOKS (Choose style gizmo on
a built tank) and DIG_ROCK (rock chunks from a canal dug through rock). Gives each its live row so `implemented` +
`verify` can be written. ~45 min. Run it before W1 where the two overlap.

**L8 — LIVE: settings pass.** SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST A2-A3 (master greying + Reset-all; by card,
*"GSS finish → Done after one live pass"*) plus the all-off component SHIP_1 asks for: everything off and the mod
still digs dry channels.

**L9 — LIVE: GREEN on the full list.** One cold load (~25 min) with the full list saved first, because
`modcheck run` rewrites ModsConfig. Gated on C4(iii), and done last before W5.

### Offline agent packets

**K0 — OFFLINE, ledger only, no source edits: record the 17 L1-only items.**
- Run each item's named selftest (`run_selftests.py --only …`) and `rimflow verify … --result pass`. The 17 are:
  CONVERTER, REACTOR, RIVERCOLOR fixes, MISSION_TANK, PIPE_ENDS, PIPE_POLE_SWITCH, PIT_ALERT, PIT_ROOM,
  POWER_CORD A1-A2, PUMP_ART, SETTINGS_KIT A2-A3, SUSPENSION_BASE A1-A2, the 4 TESTENV_*, and WALL_SCALING A2-A5.
- Then the dead-item housekeeping:
  - `supersede FLOWWORKS_LADDER_RAISE_LOWER_1 --by PIT_LADDER_REDRAW_HUNG_ON_THE_WALL`;
  - fold HOSE_PIPE_WALK into LINE_WIDTH;
  - `implemented` on the 7 OWNER-seat built items, with their shas from Census §B.

Commit the BENCH shard by explicit path.

**K1 — OFFLINE-CODE: build the reach veto, option (d)**, after C2 says yes **and** the drawbridge helper is done.
- Edits `Source/Superdeep/RM_PocketGrid.cs`, `RM_PocketGridMath.cs`, `RM_CliffMask.cs` (incremental postfix), the
  reach postfixes in `RM_SuperdeepTrap.cs`, and a new `SelfTest/` check.
- First step, as the memo says: measure the rebuild time on 250².
- Live row: `drawbridge_proof.py --only LOWER_ONLY_FROM_WINCH` + the moat-and-wall CanReach=A* row.

**K2 — OFFLINE-CODE: code review to 0 DIRTY** (97 DIRTY today). Split by folder so no two reviewers share a file; a
finding becomes a fix in that folder only.
- K2a `Source/Hose/*` (10)
- K2b `Source/Machinery/*` + `Defs/Machinery` (11)
- K2c `Source/Superdeep/*` (10). **After K1.**
- K2d `Source/Pits/*` + `Suspension/` + `RiverColors/` + `Swimming/` + root `.cs`:
  - Flood_FlowWorks.cs, RM_LakeFloorMath.cs, RM_LevellingMath.cs, RM_PitFillEffects.cs, RM_PromotionProofs.cs,
    RimMandrakeFlowWorksMod.cs, DefOf (≈14);
  - **Drawbridge/ only after the drawbridge helper is done**;
  - Flood_FlowWorks.cs only after the K4 decision.
- K2e `Source/SelfTest/*` (17)
- K2f `Defs/Canals` + `Patches/Canals` XML (7+)
- K2g .py tooling (20, incl. `validation.py`, `human_review.py`, `art_source/*`)

Check reachability before reviewing (memory: check a file is still reachable first).

**K3 — OFFLINE-CODE (Python only, no .cs): promote the 21 EXTENSION_ONLY_BARS into rows that run.**
- Files: `src/RimMandrake/FlowWorks/validation.py` (`ROW_SHOWS`, `EXTENSION_ONLY_BARS`),
  `northstar/validation_v2.py`, `northstar/extensions.py`, `northstar/manifest.py`.
- Bind each 2026-10-20 bar to the proof that already measures it: climb_proof, suspension_bridge_proof,
  trench_cover_proof, proof_hose, deep_lake_proof, swim selftests.
- `selftest_extensions.py` asserts the list. Without this, the floor cannot read `bar met` even when every proof is
  green.
- Can run in parallel with anything; it touches no `.cs`.

**K4 — OFFLINE-CODE: canal overflow Stage 0** (offline kernel, no game), after C3.
- Edits `Source/Flood_FlowWorks.cs`, `RM_LevelSolve.cs`, `FluidDef.cs` + new kernel/SelfTest files. ⚠️ It owns
  Flood_FlowWorks.cs while it runs.
- Stages 1-3 (engine layer, effects, settings) are 3 more packets; Stage 4 is a joint live acceptance (a W-packet).
- Biggest single block of unbuilt work, and the item is `needs=owner` until C3 is answered.

**K5 — OFFLINE-CODE: small unbuilt items**, one helper each, files to be found by grep at start:
- `CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES`, after W3 shows him the defect. The liquid look / material code; check
  `LIQUID_LOOK_MATERIAL_OWNERSHIP_1`'s files.
- `WET_FOXHOLE_BUILD_COLD_FEET_SHAKY_AIM` (`Source/Swimming/RM_Swim.cs` + a stat part).
- `PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS` (the dig-finds code from QUARRY).
- `FLOOD_STATION_REWIRE_DRY_CANAL_STAYS_DRY` (game-up; with `FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS`, Baroque
  Biomes side).
- `GUARDRAIL_ART_RESKIN_BORROWED_FENCE`, art pipeline, only if C4(ii) says yes.

**K6 — OFFLINE: package.** After every packet above: rebuild the DLL, update the `.srchash`, refresh the CHANGELOG
1.0.0 hash line, `deploy_custom_mods.py --mod FlowWorks --apply`, and Mod Settings audit notes. Then L9, then W5.

## Order

**Tonight, while he is present** (the cards and sheets need no bridge, so they start now, alongside the drawbridge
helper):
1. **C1 + C2 + C3 + C4** as one question-card sitting (~10 min of his time). C1 is the single most important thing
   for completion.
2. **S1** (the existing sheets), then **S2** once its sheet is built. An agent builds S2 meanwhile, ~30 min.
3. In parallel, no bridge: **K0** (ledger) and **K3** (bar promotion, Python only).
4. Once the drawbridge helper releases the bridge: **L7** (state reads), then **W1** (review map). Then **W2**
   (lines), then **W3** (water + tar tuning). W4 waits for L2/L3.

**Then, by dependency** (bridge-serial for L*, folder-serial for K*):
5. **L1** core floor at the current hash, then **GREEN_MINIMAL** recorded.
6. **L2** suspension, **L3** pits/trenches, **L4** lines/hoses, **L5** water/thirst, **L6** extension chains, **L8**
   settings. Any MOD finding becomes a new item plus a fix packet in the right folder.
7. **K1** reach veto (after C2 and the drawbridge helper), then **K2c** Superdeep review. Run **K2a/b/d/e/f/g** in
   parallel with the live work; one folder per helper, and DLL builds serial.
8. **K4** canal overflow, stages 0-3, after C3. Its joint live acceptance becomes a walk.
9. **K5** small items. **W4** bridges/trenches walk, once L2/L3 are green.
10. **K6** package, **L9** full-list GREEN (per C4(iii)), **W5** release walk and sign-off. Then close the
    umbrellas: PIT_SUPERDEEP_COLLAPSE_1 right after C1, and DEPTH_REBUILD, TRIAL, GREEN_*, SHIP and PLAYTEST last.

**Critical path:** C1 → (L1 + K3) → L2-L6 → K2 → K6 → L9 → W5. Canal overflow (C3 → K4) is the longest branch. If it
must not hold up 1.0, ask him in C3 whether overflow can ship in 1.1. That is his call, so put it on the card as a
seventh option.
