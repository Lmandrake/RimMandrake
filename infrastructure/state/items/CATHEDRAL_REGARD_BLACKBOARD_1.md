
<!-- Split from the 2026-09-12 build decomposition; standing constraints: arc spec section 'The law' (knowledge gate, bans 1/2/3/6, rationed patience, Oracle laws, no Force, no worldgen) bind this item. -->


## spec
Python, GM external blackboard alongside Imperial Heat and Hutt Interest
(kyber spec §2/§3, build_plan.md §2/M4 pattern). Builds:
- **Regard counter** — never a save stat, never a UI gauge (arc §0). Inputs per
  arc §2: manners (polls kit §1 band history via bridge), Assailant-register
  mission completions (story flags), Heat low/falling while on Cathedral ground
  (reads the Heat number it already shares a blackboard with), zero-mindstone-
  sales standing credit, §4 restore choice (mirrors origin-canon §4 pricing,
  adds nothing), misdirection-quest success (item 5). Losses: Heat brought
  near, every mindstone/kyber sale, sacrilege mirrored from faction-13 goodwill
  deltas (one act, two ledgers — the blackboard polls goodwill, no double
  machinery), anomaly sales **by volume not buyer** (A5: running sales-volume
  counter over bolt-shed curiosities + eel-catch). Never-movers: bulk salvage,
  provoked-Sentinel fights, anything unknowable.
- **Stage machine** — WARY/TOLERATED/VOUCHED/REVEALED = f(Regard, faction-13
  goodwill, story flags) per arc §1; knowledge one-way, standing two-way;
  REVEALED entered only by item 7's beat.
- **Exposure pressure** — the §6.1 number (fed by Heat-near-Cathedral, sales
  volume, pursuit events resolving on Cathedral ground); go-dark demotion to
  WARY posture at threshold. The completion chain is item 8's, this item owns
  only the number and the dark flip.
- Consequence outputs fire through the existing bridge/CQF injection lane
  (kyber §2); this item publishes stage + dark-flag for items 2–8 to consume.

## verify
Arc §8 seed 1, in shadow mode: each §2 input moves Regard in the stated
direction; bulk salvage and provoked-Sentinel kills move nothing; a crafting
consumption moves no sale counter (kyber §2 sold-vs-crafted caveat); no input
writes any save stat; demotion 2→1→0-posture works; REVEALED unreachable from
Regard alone.

## criteria
Counter, stages, exposure pressure live in shadow mode with logged would-be
consequences; thresholds/rates in one tunable table (GM tuning owns numbers);
dark flip demotes posture without erasing history.

**Depends on:** GM blackboard M4 (kyber build_plan §2) live in shadow mode;
faction-13 goodwill readable over the bridge (kit §1 ledger is vanilla — no
kit C# strictly required to start). **Waited on by:** items 2–8 (all).
**Seat/needs:** FOUNDRY; offline Python + bridge for polling tests; game-up
only for end-to-end shadow runs. Not row-3.

## built (FOUNDRY, 2026-09-13)

**Extended `src/RimMandrake/Utils/gm_blackboard_shadow.py` in place** (not a
sibling script) — `GM_BLACKBOARD_SHADOW_M4_1`'s own file, same process/poll,
same `safe_call()`/`ALLOWED_TOOLS` read-only gate. Chosen over a sibling
reading M4's JSONL log because Regard's Heat-near-Cathedral input needs the
exact same Heat float M4 already computes per poll in the same tick window —
a log-tailing sibling would either duplicate the Heat formula (drift risk) or
lag a full poll behind it. M4's own Heat/Hutt Interest logic is untouched;
everything below is additive, clearly bounded in its own comment blocks.

- **Read-only extended, not loosened**: added exactly one tool to
  `ALLOWED_TOOLS` — `jawa/trade_price_probe`, read-only "in effect" per its
  own header (opens a headless TradeSession, reads prices, closes it again
  before returning — refuses rather than clobbers a live trade dialog). Used
  only as corroborating evidence (`trader_pawn_present_this_poll`) for
  whether a trade partner was on-map when a kyber/anomaly count dropped.
  `jawa/trade_price_probe`'s sibling `jawa/trade_execute` (which can actually
  move goods) was deliberately NOT added — checked and confirmed absent from
  `ALLOWED_TOOLS`.
- **Regard §2 inputs implemented**: kyber/mindstone sale loss and Heat-near
  gain/loss (M4's own, unchanged) plus this item's own additions — zero-sale
  standing credit (distinct from "no loss": every sale-free poll credits a
  small amount), a manners *proxy* (consecutive clean polls — no sale, no
  goodwill drop — standing in for the kit's band history, which **no bridge
  tool exposes**; `RM_MapComponent_BiomeAttitude.currentBand` is a private
  field with no `[Tool]` reading it, checked against every file under
  `src/RimMandrake/bridgetools/JawaBench.BridgeTools/`), sacrilege mirrored
  1:1 from a cathedral (faction 13) goodwill *drop* between polls ("one act,
  two ledgers"), anomaly sales by cumulative volume (`RUT_BoltShedCuriosity`
  + `RUT_CoolantEel`, A5 — a monotonic running total; only crossing the bulk
  threshold moves anything, an occasional sale never does), and one-time
  story-flag beats (Assailant-register mission completions, the §4 restore
  choice, item 5's misdirection-quest success) applied once, not per-poll,
  since they are discrete events, not rates.
- **Stage machine (§1)**: `compute_conduct_posture()` returns WARY(0)/
  TOLERATED(1)/VOUCHED(2) *only* — structurally incapable of returning
  REVEALED(3); REVEALED is a separate `knowledge_revealed` latch set only
  from an explicit `reveal_beat_fired` story flag that no code path in this
  file ever sets on its own (item 7's own future call site). Climb uses the
  §1 floors (regard + manners-proxy streak for TOLERATED; regard + mission
  count for VOUCHED); demotion uses lower hysteresis floors, so Regard loss
  ratchets posture down 2→1→0 on its own.
- **Exposure pressure (§6.1)**: its own accumulator, fed by Heat-near-
  Cathedral, kyber sale volume, and anomaly bulk-crossings (all live-
  observable); pursuit-spine events resolving on Cathedral ground have **no
  live signal** (Act II+ is unbuilt) so that input is a `--pursuit-event-on-
  poll` synthetic demo hook only, always logged as synthetic when used. At
  threshold, a go-dark flip forces posture to WARY and resets the manners-
  streak and exposure pressure — Regard, mission counts, and
  `knowledge_revealed` are untouched (posture-only demotion, history kept).
- **Known, documented gaps (no live signal exists for these; they correctly
  contribute 0/False in a real run)**: manners' true band-history input (kit
  gap, above), Assailant-register mission completions, the §4 restore
  choice, the misdirection-quest success beat (item 5), and any Act II+
  pursuit event — all wired via an optional `--story-flags-file` /
  `--pursuit-event-on-poll` hook for when those items build, never
  fabricated here. The kyber spec's own sold-vs-crafted caveat (a count drop
  could be a sale or a crafting consumption) is **not resolved** — no
  trade-transaction-log tool exists on the bridge (checked
  `JawaBenchTradeExecuteTools.cs`/`JawaBenchTradeProbeTools.cs`: a price
  probe and an execute tool exist, no log) — `trader_pawn_present_this_poll`
  is logged as corroborating evidence only, inherited from M4's own
  documented limitation, not newly solved.

## offline mechanism test (not committed, not live evidence)

Before spending bridge time, a local harness (`FakeRB` feeding scripted
bridge responses, no RimWorld process) exercised every path deterministically:
kyber sale → Regard down; a clean streak → Regard up, stage never reaches
REVEALED; a goodwill drop → sacrilege-mirror Regard loss with no kyber sale
present; a run with no signal at all moves Regard only by the tiny documented
manners/zero-sale trickle (bulk salvage and Sentinel fights have no code path
reading any such signal, confirmed by inspection, so there is nothing to move
mistakenly); anomaly volume below the bulk threshold moves nothing, crossing
it costs Regard and raises exposure; and — the sharpest test — story-flag
beats pushed Regard to 50 and posture legitimately climbed to VOUCHED over
several clean polls, then a forced exposure-pressure overflow produced a
**real VOUCHED→WARY demotion** with Regard and `knowledge_revealed` both
unchanged. All assertions passed.

## shadow-log evidence (real live session, 2026-09-13)

Bridge taken (`rimflow bridge take`), same live campaign M4 left off at
(tile 17007, `ticksGame` 144307 at start of this item's first run — the exact
tick M4's own last run ended on). Bridge released after. Three runs, all
genuine bridge reads/`step_game_ticks` advances, zero incidents fired, zero
letters sent, zero saves written (verified: every tool name called is in
`ALLOWED_TOOLS`, confirmed by reading the run's own printed tool list):

- `infrastructure/state/facts/gm_blackboard_shadow_log_2026-09-13_regard.jsonl`
  — 15 polls, no `--story-flags-file`, default thresholds, ticks 144307 →
  152498. Real live reading: campaign still holds zero kyber/mindstone/
  anomaly items (`countMatched: 0`), no cathedral-ground marker detected
  (`cathedral_ground_confidence: "no-marker-found"`), no goodwill delta. The
  only thing that moved was the tiny manners-proxy/zero-sale trickle (Regard
  0.00 → 0.85 over 15 clean polls) — a correct real reading of "nothing
  happened, but nothing bad happened either," not a tool failure. Stage
  stayed WARY throughout (regard never reached the 15.0 TOLERATED floor).
  Exposure pressure sat at 0.00 throughout (no live input touched it).
- `..._regard_demo_godark.jsonl` — 6 polls, `--exposure-godark-threshold 10
  --pursuit-event-on-poll 3` (both explicit synthetic-demo flags, logged as
  such every time they fire): poll 3 shows `pursuit_event_on_cathedral_ground`
  then `cathedral_go_dark` firing against real ticks/reads, `go_dark_flip_count`
  reaching 1. Posture was already WARY, so this alone only proves the flip
  fires and resets correctly, not a real demotion.
- `..._regard_demo_climb_and_godark.jsonl` — 9 polls, combining
  `--story-flags-file infrastructure/state/facts/cathedral_regard_demo_story_flags.json`
  (`assailant_mission_completions: 5, restore_choice_made: true` — both
  synthetic, since no live mission/quest content exists yet) with
  `--exposure-godark-threshold 10 --pursuit-event-on-poll 8`: poll 1 applies
  the one-time story gain (Regard 0.15 → 50.15); poll 5 the stage machine
  legitimately climbs WARY→VOUCHED against real, live-polled Regard/streak
  values (`compute_conduct_posture` evaluates its chained thresholds once
  per poll, so both the TOLERATED and VOUCHED gates opening on the same poll
  produces a same-poll double climb — worth a tuning note, not a defect);
  poll 8 the synthetic pursuit event crosses the exposure threshold and a
  **real live VOUCHED→WARY demotion** fires (3 would-fire events), while
  Regard keeps climbing through the same poll (50.45 → 50.50) and
  `knowledge_revealed` stays false throughout — "demotes posture without
  erasing history," confirmed against a live session, not just offline.

## verify checklist — confirmed vs. not, and why

- **Each §2 input moves Regard in the stated direction** — CONFIRMED for
  kyber sale loss, Heat-near loss/gain (M4's, unchanged), sacrilege mirror,
  zero-sale credit, manners proxy, anomaly bulk crossing, and the three
  story-flag beats, via the offline harness (deterministic, every direction
  individually asserted) plus the live climb demo for the story-flag beats.
  **NOT independently confirmed against a real live trigering event** for
  manners (no band-history tool exists — proxy only), Assailant missions,
  the §4 restore choice, or misdirection-quest success (items 2/4/5 unbuilt,
  no live source) — same honest-gap shape M4 used for its own unproven
  kyber-sale pathway.
- **Bulk salvage and provoked-Sentinel kills move nothing** — CONFIRMED by
  code inspection (no term in the Regard/exposure computation reads a
  salvage, mining, or combat/kill signal at all — there is nothing to zero
  out because nothing was ever added) and by the live run (15 polls of real
  play activity, no spurious movement).
- **A crafting consumption moves no sale counter** — **NOT confirmable
  live or resolved by this item.** No trade-transaction-log bridge tool
  exists (checked both trade tool files) to distinguish a sale from a
  crafting/consumption drop; `trader_pawn_present_this_poll` was added as
  corroborating evidence but does not gate the count-delta math, so this
  caveat is inherited from M4 unchanged, not newly solved. Flagged honestly
  rather than claimed fixed.
- **No input writes any save stat** — CONFIRMED by construction:
  `ALLOWED_TOOLS` contains only reads plus `step_game_ticks`; no
  `fire_incident`/`send_letter`/`save_game`/`execute_debug_action`/`set_*`/
  `trade_execute` call exists anywhere in the file, and `safe_call()`
  refuses any tool name outside the allowlist before the bridge is asked.
- **Demotion 2→1→0-posture works** — CONFIRMED, both offline (a controlled
  VOUCHED→WARY demotion with asserted Regard/knowledge_revealed invariance)
  and live (`..._regard_demo_climb_and_godark.jsonl` poll 8, real bridge
  session). The intermediate 2→1 step specifically was exercised only
  offline, not live in this session (the live demo went straight 2→0 via
  go-dark, which the spec's own "demotes to WARY posture regardless of
  history" at go-dark explicitly allows — go-dark is not required to step
  through 1).
- **REVEALED unreachable from Regard alone** — CONFIRMED structurally
  (`compute_conduct_posture()`'s return type is 0/1/2 only, by inspection)
  and empirically (every poll across all three live runs and the offline
  harness printed `effective_stage_label` never once reached REVEALED,
  including the run that pushed Regard to 50.55 — well past every posture
  floor).

## status: left in `doing`

Not closing this. The mechanism is built, structurally sound, and proven
live for every input this campaign can currently exercise, but real §2
inputs this arc names — manners' true band-history signal, Assailant
missions, the §4 restore choice, misdirection-quest success, and any Act
II+ pursuit event — have **zero live confirmation**, only offline/synthetic
demonstration, because items 2, 4, 5, and the pursuit spine are unbuilt and
the band-history bridge tool doesn't exist. The sold-vs-crafted ambiguity
inherited from M4 is also still open. Closing now would read as "every §2
input proven," which isn't earned. Left `doing` so whoever builds items 2–8
(or a future session watching for a real kyber/anomaly sale, or adding
`jawa/biome_attitude_get`-style tool for the manners input) can pick this up
to either extend the live proof or judge the structural/offline proof
sufficient and close it.
