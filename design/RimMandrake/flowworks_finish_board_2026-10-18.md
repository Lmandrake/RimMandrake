# FlowWorks finish board (BENCH, written 2026-10-18)

Owner, 2026-10-18: *"please handoff at this time and set notes to prepare for finishing FlowWorks in Bench. We will be
force advancing it as quickly as possible to get that mod finished."* Also: biome art is accepted as-is and never blocks
(`design/RimMandrake/standing_rulings.md` "Biome art never blocks").

The one page the next BENCH session opens to drive FlowWorks to finished beside FOUNDRY. Every number is tagged
MEASURED (read from the ledger, git or a command this session) or ESTIMATED (a judgement). Ledger state was read from
`rimflow show` at origin/main `30e52696d2` on 2026-10-18; nothing was run that writes `ModsConfig.xml`.

## 0. Read this first: the ledger lags the code

MEASURED: the depth rebuild is mostly BUILT AND LIVE-PROVEN, but its items still read `proposed`/`doing`. FOUNDRY's
notes (day 2 to day 5, `Transient/fw_scenes/live*`) carry the proof; nobody filed `implemented`/`verify`/`close`.
Examples: `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES` (P3) note "ProofLevelSurface bar worst gap 0.0001 m" yet state
`proposed`; `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE` (P8) live readout recorded, state `proposed`;
`LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP` (P11) and `FISH_ROLL_MEND_PONDS_BORN_BARREN` (P13) built, state `proposed`.
Step 1 of the critical path is therefore a ledger truth pass, not code. Do not rebuild what exists
(CLAUDE.md: search before filing).

## 1. What "finished" means for FlowWorks

Finished = `FLOWWORKS_NORTHSTAR_SHIP_1` (kind trial, FOUNDRY, `proposed`) acceptance AND the epic's done condition:

| # | condition | source | state (MEASURED unless marked) |
|---|---|---|---|
| F1 | `code_review_status.py check` over tracked FlowWorks `.cs`: 0 DIRTY | SHIP_1 | **45 DIRTY of 195-ish tracked `.cs`**; 116 DIRTY of 506 `.cs/.xml/.py`. (Was 195/195 CLEAN on 2026-10-15; the rebuild dirtied them.) |
| F2 | Mod Settings superb, all-off component digs dry channels | SHIP_1 | `all_off_still_digs` chain exists (2026-10-05); settings grew since (157 toggles, 2026-10-18 harness commit); re-audit owed |
| F3 | Art for every visual bar | SHIP_1 | 97 of 100 def texture refs borrowed vanilla/foreign art (2026-10-05, may be stale; UNMEASURED today). See owner question Q2 |
| F4 | `deploy_custom_mods.py --mod FlowWorks` in sync, DLL `.srchash` matches | SHIP_1 | not checked (push guard enforces `.srchash`); live runs used DLL `1e2dec39d`-era builds |
| F5 | `FLOWWORKS_DOOR_FAMILY_1` and `PIT_SUPERDEEP_COLLAPSE_1` closed or parked by his word | SHIP_1 | DOOR_FAMILY `done`; SUPERDEEP `doing` (bridge) |
| F6 | GREEN-MINIMAL: `modcheck status FlowWorks` GREEN on the `flowworks` tier + his sheet review | `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` (`proposed`) | v2 live 74P/0F on 2026-10-05; since then v2 61/0/0 on DLL `6699957b8` (2026-10-18). `modcheck floor --all`: FlowWorks **DRAFT**, 0 bars validated |
| F7 | GREEN-FULL: GREEN on the full list after a cold load, list restored byte-identical | `FLOWWORKS_NORTHSTAR_GREEN_FULL_1` (`built`, A1/A2 owed) | cold load ~25 min on the 639-mod list (BENCH note 2026-10-13); no short check exists |
| F8 | North-star bars VALIDATED by him (hash-bound; any edit reverts to DRAFT) | `design/validation_walks/RimMandrake/FlowWorks.md` `## north star` | state DRAFT, `validated-hash:` empty. Bars still saying "four depths"/notches: `fill_tier_legible`, `depth_and_fill_jointly_legible`, `pit_depth_ladder_legible`, `pawn_height_ladder_legible`; new `still_water_one_surface_height` (R9) is written in the file |
| F9 | Epic `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` done: every child closed and he has looked at the staged save and art | the epic | children listed in section 2 |

Plan for the depth work: `design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md` (P1-P14, rulings R1-R13, risks).
ESTIMATED total at filing was 26 to 48 agent-days; most of P3-P8, P11-P13 has since landed (MEASURED by commits
`4231348aa7`..`c66716301d`), so what remains is P14, live proofs, review, his looks and the SHIP stamp.

## 2. Open FlowWorks-related ledger items

Columns: ID · state · needs · seat · what remains · blocks / blocked-by. Seat = ledger owner (`for=`). "built" claims are
from FOUNDRY notes; `proposed` means the ledger, not the code (section 0). Sweep: 72 candidate IDs by family prefix
(MEASURED), ~170 by keyword (most are other mods: Sump, Scald, GSS, Graffiti, Bacta; excluded).

### (a) Blocking ship: 22 items

| ID | state | needs | seat | remaining | edges |
|---|---|---|---|---|---|
| `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (epic, P10) | proposed | offline/bridge/owner | FOUNDRY | integration walk, staged save, redrawn S5, his look | blocked by all children |
| `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES` (P3) | proposed (built) | offline | FOUNDRY | file implemented+verify; open MOD findings: pump to canal stalls after one notch, spill vanishes with no filth, S5.e sheet destroyed | blocks P10 |
| `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` (P4) | doing (built) | offline | FOUNDRY | settings UI / mouseover by eye UNMEASURED; close | with P3 |
| `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE` (P8) | proposed (built) | offline | FOUNDRY | his wording look (V8 kept by card 10-18); sea reading UNMEASURED | P10 |
| `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT` (P5) | built | bridge | FOUNDRY | A2 dig-to-depth walk, A3 save reload, A4 art (his look) | **must not ship before P2 passes** |
| `DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT` (P6) | built | bridge | FOUNDRY | rides P5's walk | P5 |
| `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` (P2) | proposed | bridge | FOUNDRY | mask-swap row UNMEASURED; owed `raider_never_crosses_ramped_moat`, `hauler_fetches_ramped_floor`, `save_reload_pockets_identical`; modcheck record | gates shipping P5 |
| `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` | doing | offline | BENCH | A1/A2 live climb rows (P2 discharges) | P2 |
| `PIT_SUPERDEEP_COLLAPSE_1` | doing | bridge | FOUNDRY | live proofs; P12 barrier verdict per site; named in SHIP_1 | SHIP_1 |
| `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` (P14) | doing | offline | BENCH | **NOT BUILT** (no commit mentions it, MEASURED): one-water terrain ladder, wet dug squares on base layer, thin water in situ, ice and flood rows | blocks P10, P13 dug-water fish rows |
| `LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP` (P11) | proposed (built) | offline | FOUNDRY | live: only the mountainous lake got 0.5-10 m floors, flat/hill lakes 0.5-1 m; roughness table owed to him; his look | P10 |
| `FISH_ROLL_MEND_PONDS_BORN_BARREN` (P13) | proposed (built) | offline | FOUNDRY | fish rows UNMEASURED (needs a `ProofWaterBody` read surface); reed grace path not exercised | P14 for dug water |
| `WATER_SCENES_PROVE_AFTER_THE_CREEP_FIX` (P1) | proposed | deploy | FOUNDRY | live reruns done (partial, day 5: 22 MATCH/8 DIFFERS earlier; S5 level rows MATCH); `modcheck record` never run (walk JSON has no mod_hash) | see (d) |
| `VERY_SHALLOW_WATER_RESKIN_HE_SEES_FIRST` + `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST` (P9, 2) | proposed | offline then owner | FOUNDRY | 3 under-25 cm candidates + canal/wall/deep-tint mocks exist; his look (in game for thin water) | P10 |
| `SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING` | proposed | bridge | FOUNDRY | regression at `ea44bf7957`: salt bottle gives no hydration; sprinkler T22 FAIL + 3 UNMEASURED | blocks GREEN |
| `THIRST_ROWS_DIAGNOSE_SLIME_SITS_STILL` | proposed | bridge | FOUNDRY | thirst_live T27/T15/T16 fail twice (pawn only wanders) | blocks GREEN |
| `VALIDATION_V2_RECONCILE_AFTER_THE_BIG_DIG` | proposed | bridge | FOUNDRY | day 4/5: 61/0/0 on fresh and calm v2 maps; reconcile the 24 earlier failures in writing | GREEN |
| `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` | proposed | bridge | FOUNDRY | final minimal-tier run + modcheck record + his sheet review | after the above |
| `FLOWWORKS_NORTHSTAR_GREEN_FULL_1` | built | bridge | FOUNDRY | A1/A2: full-list cold load run | after GREEN_MINIMAL |
| `FLOWWORKS_NORTHSTAR_SHIP_1` | proposed | offline | FOUNDRY | F1-F5 above | last |
| `FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING` | proposed | owner | BENCH | rewrite bar prose to metres first (any edit reverts DRAFT), then his sitting; offer narrowed limitless bar (R13) | F8 |
### (b) Needed but not blocking: 19 items (live proofs owed on built work, owner looks, polish)

| ID | state | needs | seat | remaining |
|---|---|---|---|---|
| `WATER_SCENES_S5_JUDGE_THIRD_DRAFT` | proposed | owner | BENCH | he approves S5 redrawn with level numbers (after P10 re-seal) |
| `DEPTH_DEFAULTS_ASK_ELEVEN_VETOES` | proposed | owner | BENCH | mostly answered, see section 4; narrow to the leftovers |
| `DEPTH_QUESTIONS_ASK_RAIDERS_FIRST` | proposed | owner | BENCH | mostly answered; Q11 left, see section 4 |
| `FALL_DAMAGE_BUILD_DEEP_DROPS_KILL`, `FALL_GUARDRAILS_BUILD_REAL_OBJECT`, `PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER`, `PIT_ALERT_BUILD_RED_MEANS_HELP` | validated | bridge | FOUNDRY | one live batch (4 items, built 10-18, commits `95fe5d2a26`, `e4917fd137`, `84737505c5`, `46c14c59f0`) |
| `BEACH_RING_RETIRE_DRAINED_MEANS_DRY` | validated | bridge | FOUNDRY | live dry-means-dry row |
| `RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP` | proposed | bridge | FOUNDRY | owner 10-18: go around, breach, jump packs, ladders pre-built, sieges unchanged. Real build; depends on P2 raid result |
| `PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS` | proposed | offline | FOUNDRY | two ladders, carryable ladder, climbing gear; pairs with `FLOWWORKS_LADDER_RAISE_LOWER_1` (validated, owner look OWED) |
| `HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE` | proposed | bridge | FOUNDRY | S3 pond loses 6.98 levels vs canal gains 6.00; hose routing prefers bare ground |
| `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD`, `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` | validated | bridge | BENCH | A2 pipe-look survives blueprint to building (~5 min check); A5/A6 colonists-clean SITE-UNMEASURED |
| `SPRINKLER_HEADS_BUILD_PUMP_REQUIRED` | doing | offline | BENCH | stage all four nozzle looks spraying for a joint walk (his rule: in situ only) |
| `THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY` | doing | offline | BENCH | built offline, not deployed; live T1-T7, T9, T10, caravan readout, code review owed |
| `TANK_TALL_BUILD_TWICE_THE_DRINK` | doing | offline | BENCH | art installed 10-15; live proof of tall tanks |
| `FLOWWORKS_PLAYTEST_CAMPAIGN_1`, `FLOWWORKS_REVIEW_LOOKS_ROUND_1` | proposed | offline | BENCH | stale-looking campaign items; read before acting, probably (d) |
| `RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED` | built | bridge | FOUNDRY | 11 river toggle proofs + 10 river-walk lines; Rivers walk is DRAFT |

(IDs counted individually; DEFAULTS, RAIDERS_Q and PLAYTEST/REVIEW_LOOKS also appear in (d).)
### (c) Can be cut or deferred (propose, do not decide): 26 items

| ID | state | why defer | edges |
|---|---|---|---|
| `SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT`, `_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS`, `_GRATE_BUILD_LET_THE_FIRE_UP`, `_UNDERPASS_BUILD_MIND_YOUR_HEAD`, `_WATERS_BUILD_MAY_BACKTRACK`, `_JETTY_BUILD_WALK_THE_PLANK`, `_ART_RESKIN_HE_SEES_FIRST` (7) | proposed | New feature family filed 10-19 00:52 from `flowworks_bridges_design_2026-10-17.md`; none is in SHIP_1 acceptance; large (7 builds, art his look) | R8 amendment allows walk-under |
| `TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT` | proposed | wet foxhole cover; new feature, not in SHIP_1 | after RAIDERS_TRENCH |
| `BIG_CREATURES_DESIGN_WALLS_AND_SLOTS` | proposed | design pass done (`design/RimMandrake/big_creatures_walls_and_slots_2026-10-18.md`, 349 lines, six owner questions in its section 8); build is a new feature | not blocking |
| `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` | proposed | colonists now dig to 8 m (20 m max); consolidation doc already asks "drop it?" | |
| `FLOWWORKS_QUARRY_DIGGING_1` | validated | design pass only; quarry/sluice build not required to ship | |
| `CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES`, `RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS`, `RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS` | proposed | review aids, not features | art is secondary per owner 10-18 |
| `CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES` | proposed | cosmetic, from a relayed observation, never measured; owner said "work out appearance matching later" (10-18) | |
| `FLOWWORKS_HOSE_FIX_PAUSE_REMESH_EVERY_FRAME`, `FLOWWORKS_CONVERTER_FIX_CAP_EATS_CHANGE`, `FLOWWORKS_PITCOVER_FIX_BURNS_PAWN_UNHARMED`, `FLOWWORKS_PITFALL_FIX_HISTORY_NOT_SAVED`, `HOSE_LAY_POLISH_CENTRE_VS_MOUTH` | proposed | small code-review finds; cheap offline wins; fold into the F1 review wave rather than defer | F1 |
| `PROPANE_CANAL_WIRE_STILL_NO_FLUID`, `GSS_TOGGLES_FIX_OFF_MEANS_OFF`, `SARLACC_PIT_WIDEN_THE_BIG_ONES` | proposed | other mods' items that touch FlowWorks; not FlowWorks ship | |
| `FLOOD_STATION_REWIRE_DRY_CANAL_STAYS_DRY`, `THIRST_DESIGN_SLIME_IS_THE_LAST_RESORT`, `SAND_SHOVEL_DIAGNOSE_DIGS_UNDER_WALLS` | proposed | verify passed 10-17 (flood); design/diagnose items outside the SHIP_1 list | |

(26 IDs counted individually, 7 of them suspension rows; the five small code-review fixes are really "do cheaply in the F1 wave".)

### (d) Dead or duplicate: list for closing, with proof: 6 items

| ID | proof | proposal |
|---|---|---|
| `WATER_SCENES_PROVE_AFTER_THE_CREEP_FIX` (P1) | its own note 10-17 20:55: reran on the P3+P4 DLL; day 5 `run_S5_stdout.txt` rows MATCH; the creep-fix DLL it names is replaced by the solver | close with sha, keep the missing modcheck record as a note on the epic |
| `PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE`, `DEEP_WATER_BUILD_SWIM_OR_SINK`, `WATER_NATURAL_DECIDE_ONE_SURFACE`, `HOSE_LEFTOVER_FIX_NO_VANISHING_LITRES`, `LAKE_GROUNDWATER_REFILL_BUILD_WETNESS_CUT` | MEASURED: already `done` in the ledger; listed so nobody reopens them | no action |
| `DEPTH_DEFAULTS_ASK_ELEVEN_VETOES`, `DEPTH_QUESTIONS_ASK_RAIDERS_FIRST` | MEASURED: epic notes 10-18 15:17-16:52 record owner card answers to V1, V3, V4, V5, V8, D4, Q7, Q12, Q2 | close after posting the 2-3 leftover questions as one card (section 4) |
| `FLOWWORKS_PLAYTEST_CAMPAIGN_1`, `FLOWWORKS_REVIEW_LOOKS_ROUND_1` | ESTIMATED stale (2026-10-06 era, pre-rebuild); not read in depth | read, then drop if superseded |
| `FLOWWORKS_BUILD_PROGRAM_1`, `LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS` | MEASURED: already `superseded` | no action |

Counts of open items per group (MEASURED by hand-count of the rows above): (a) 22 · (b) 19 · (c) 26 · (d) 3 to close
(P1, the two card items) plus 2 stale candidates, the rest already closed.

## 3. Proposed split (a proposal, not a ruling)

**FOUNDRY keeps** (it holds the bridge for "FlowWorks depth acceptance" and has uncommitted work: 26 non-art/non-transient
paths in `/home/mandrake/rm/foundry` plus its ledger shard, MEASURED; the Alpha Biomes retirement is in that tree):
P2 mask-swap proofs and the raid rows; P10 integration walk and the staged savegame; the live rows for the 4 built
10-18 pit rules; regression diagnosis (`SALT_BOTTLE_DIAGNOSE...`, `THIRST_ROWS_DIAGNOSE...`); `RAIDERS_TRENCH_BUILD...`;
C# fixes in `src/RimMandrake/FlowWorks/Source/` (it owns those files; BENCH does not edit them while the bridge is held).

**BENCH takes** (files FOUNDRY is not touching):
1. The ledger truth pass (section 0), by `rimflow` only, explicit-path ledger commit.
2. P14 `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` is BENCH's item. It edits FlowWorks C# that P3 also touches: first
   `rimflow note` FOUNDRY and agree the file split (`RM_FlowKernel.cs`, excavation component) before any edit.
3. The F1 code-review wave (45 DIRTY `.cs`): review-only files first, no collision while FOUNDRY is mid-edit; fix-commits by explicit path.
4. Owner sittings: art/in-situ (thin water, sprinkler nozzles, ladders raised/lowered, S5 third draft, lake floor variety),
   bar re-validation, the cards in section 4. Offline prep so each sitting is one trip.
5. The cheap live checks that need no depth code: `HOSE_RULINGS` A2 (~5 min), `TANK_TALL`, `THIRST_BUILD_OWN_BOTTLES`
   live rows, `FLOWWORKS_LADDER_RAISE_LOWER_1`, when BENCH holds the bridge (`rimflow bridge who`: FREE at write time).
6. Rewrite the four "four depths"/notch bars in `FlowWorks.md` to metres in ONE edit, just before his sitting.

Bridge: `rimflow bridge take --for "<what>"` first, release on stop; no flyer live tests without him; `modcheck run` rewrites `ModsConfig.xml`.

## 4. Owner decisions: still open (checked 2026-10-18, MEASURED against epic notes)

| item | status |
|---|---|
| `DEPTH_DEFAULTS_ASK_ELEVEN_VETOES` | **Mostly answered.** Answered by card: V1 keep curve, V3 fall by metres (deep falls can kill), V4 spikes relative, V5 shooting, V6 pit room 3.0 m scaled, V8 readout wording, D4 delete `sourceBudgetMultiplier`, shallow drowning default-on. **Not recorded as answered:** V2 (drowning when water covers the head) beyond "drown slowly", V7 (picture bands, rides his art look), D3 (one burn rate; built as default). |
| `DEPTH_QUESTIONS_ASK_RAIDERS_FIRST` | **Mostly answered.** Q7 raiders (go around, breach, jump packs, ladders, sieges unchanged), Q12 red alert, Q2 swim (R12) answered. **Open:** Q11 who goes down to tend and rescue. Q6 became `BIG_CREATURES_DESIGN_WALLS_AND_SLOTS`. Q9 plants on dug ground is not in this rebuild. |
| `FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING` | **Open.** Hash-bound section DRAFT. |
| `WATER_SCENES_S5_JUDGE_THIRD_DRAFT` | **Open**, waits on P10 re-seal. |
| `BIG_CREATURES_DESIGN_WALLS_AND_SLOTS` six questions | **Open** (design doc section 8); not needed to finish. Defer to after ship. |

Cards to put to him (plain words; one recommended each). Use the `question-card` skill layout when sending.

**Q1. What does "finished" include?**
- A. Water, pits, thirst, hoses, sprinklers and rivers as they are, plus the rebuild. Bridges, trench cover, big creatures wait for the next version. *Buys:* a ship in days to weeks. *Costs:* the seven suspension-bridge builds and trench cover you filed last night are not in this release. **(recommended)**
- B. Everything filed, including the suspension bridges. *Buys:* nothing left out. *Costs:* ESTIMATED 25 to 40 more agent-days (7 builds + art with his look).
- C. A plus trench cover and the raider-trench build only. *Buys:* the fight-from-a-trench story is whole. *Costs:* ESTIMATED 5 to 8 more agent-days.

**Q2. May FlowWorks ship with its borrowed art (97 of 100 textures borrowed from vanilla or other mods, as of 2026-10-05)?**
- A. Yes, accept it as-is and review later, like the biomes (your 2026-10-18 ruling). *Buys:* no art wait. *Costs:* the ship acceptance line "art for every visual bar" is waived. **(recommended)**
- B. Only the new depth art (thin water, wall faces, deep tints) must be made and seen by you first. *Buys:* the rebuild looks right. *Costs:* one art sitting (ESTIMATED 1 to 2 agent-days + your look).
- C. All FlowWorks art replaced. *Costs:* ESTIMATED weeks.

**Q3. Who goes down into a pit to tend or rescue someone (Q11)?**
- A. Any colonist who can climb back out; if nobody can, a ladder job is queued first. *Buys:* no one gets stuck rescuing. **(recommended)**
- B. Only colonists at or above a climbing skill; others wait for a ladder. *Costs:* slower rescues.
- C. Nobody; prisoners in pits are fed by drop-in only. *Costs:* kills rescue play.

**Q4. Leftovers of the old vetoes card (V2 drowning over the head, V7 picture bands, D3 one burn rate): keep the built defaults?**
- A. Keep all three; you judge V7 in the art sitting. *Buys:* closes the card. **(recommended)**
- B. Tell me which to change.

## 5. Critical path (ordered, at most 12 steps; every figure ESTIMATED, in agent-hours; 1 agent-day = 8 h)

| # | step | seat | needs | agent-h |
|---|---|---|---|---|
| 1 | Ledger truth pass: file implemented/verify/close for P3, P4, P5, P6, P8, P11, P13, P1 and the two card items, citing each commit and live note | BENCH | offline | 2 to 3 |
| 2 | Send Q1-Q4 cards (one batch) so scope is fixed before building | BENCH | owner | 1 |
| 3 | P14 build: one water ladder, wet dug squares on the base layer, save migration, selftests (coordinate files with FOUNDRY) | BENCH | offline | 20 to 28 |
| 4 | Regression diagnosis: salt bottle, thirst rows, sprinkler T22 (suspects `26a47408f7`, `ea44bf7957`) | FOUNDRY | bridge | 4 to 8 |
| 5 | P2 leftovers: mask-swap under churn, ramped-moat raid, hauler, reload pockets; raid result decides RAIDERS_TRENCH scope | FOUNDRY | bridge | 6 to 10 |
| 6 | F1 code-review wave over 45 DIRTY `.cs` (plus cheap fixes from (c)) | BENCH (+ review agents) | offline | 10 to 16 |
| 7 | Live batch for built 10-18 work (falls, guardrails, pit room, alert, beach ring) and P14 rows (ice, flood, thin water in situ, dug-pond fish) | FOUNDRY/BENCH | bridge | 6 to 9 |
| 8 | P10 integration: deploy, full walk, redraw S5 with level numbers, stage the savegame, write modcheck records | FOUNDRY | deploy + bridge | 8 to 12 |
| 9 | Owner sitting 1: thin water in situ, S5 third draft, lake floors and roughness table, sprinklers, ladders (prep 3 h; his time ESTIMATED 45 to 90 min) | BENCH | owner | 3 to 4 |
| 10 | Rewrite bars to metres in one edit, narrowed limitless bar, then owner sitting 2 re-validates the section | BENCH | owner | 2 to 3 |
| 11 | GREEN-MINIMAL run + his sheet, then GREEN-FULL after a ~25 min cold load (list saved and restored byte-identical) | FOUNDRY/BENCH | bridge | 5 to 7 |
| 12 | SHIP_1 stamp: settings audit, `deploy_custom_mods.py --mod FlowWorks` sync, `.srchash`, close DOOR_FAMILY/SUPERDEEP, close epic | BENCH | offline | 3 to 5 |

ESTIMATED total: about 70 to 105 agent-hours (9 to 13 agent-days) if Q1 answers A and parallel seats overlap steps
3-6; it is dominated by P14 (step 3) and review (step 6). Steps 3, 4, 5 and 6 run in parallel; 7 follows 3 and 5; 8 follows 3 to 7.
Options B and C in Q1 add to this. The earlier plan total (26 to 48 agent-days, 2026-10-17) is superseded by this.

## 6. Traps
- MEASURED: `modcheck floor --all` takes over 2 minutes; run it in the background. Its FlowWorks row says "no bar" while
  the file has bars: UNMEASURED which is right; ask `modcheck` before quoting a bar count.
- Deep water is swimmable (R12): any moat or trench item that assumed a water barrier needs its verdict (P12 recorded them).
- Alpha Biomes retirement lives in FOUNDRY's uncommitted tree; do not touch or commit it from BENCH.
