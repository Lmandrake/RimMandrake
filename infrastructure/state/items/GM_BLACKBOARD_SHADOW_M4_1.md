# GM_BLACKBOARD_SHADOW_M4_1 — the external blackboard, in shadow mode

Filed by FOUNDRY, 2026-09-13. Two queue items — `KYBER_TRADE_PLOT_1`
(BLOCKED: "Heat/Hutt-Interest GM blackboard (M4) unbuilt — cannot meet
verify's sale-raises-heat clause without inventing parallel infra") and
`CATHEDRAL_REGARD_BLACKBOARD_1` ("Depends on: GM blackboard M4... live in
shadow mode") — both name this milestone as a hard prerequisite, but no
queue item existed to build it. This item is that build.

## spec

`design/Jawa/build_plan.md` §4, milestone M4 (verbatim):

> The external blackboard: Imperial Heat + the orbital-detection timer + the
> dark-tile pause, as a Python state machine driven by polled reads. Runs in
> **shadow mode** for a whole playthrough of the thin slice — logs what it
> *would* fire, fires nothing. Then flip injection on a throwaway save, then
> for real. This is the instrument-autonomy staging ramp from
> `first_live_access.md`.
>
> **Exit:** a shadow log we can read and believe, before anything is live.

Read `design/Jawa/worldbuilding/enrichment_agents.md` §4 (the read → propose
→ human-approve → write-with-V&V → re-verify loop M0 already established —
this state machine is a consumer of that pattern, not a new one) and §7.1
("the headline unknown") for the reload-survival answer M0 already settled
— reuse it, don't re-answer it.

This item builds the STATE MACHINE and its SHADOW-MODE run only — polled
reads over the bridge, an Imperial Heat number, an orbital-detection timer,
a dark-tile-pause flag, logging what each WOULD fire without firing it. It
does NOT build: the live injection flip (a separate, later step per M4's own
"then flip... then for real" sequencing), `CATHEDRAL_REGARD_BLACKBOARD_1`'s
Regard counter/stage machine (a *consumer* of this blackboard, its own
item), or anything from `KYBER_TRADE_PLOT_1`'s own quest content (already
built, per that item's own note — only the blackboard was missing).

## verify

- The state machine runs against a live game session (polled bridge reads,
  per M0's primitive verbs) for a meaningful stretch of play and produces a
  shadow log of would-be Heat/timer/pause events.
- Nothing it does writes to the save, fires an incident, sends a letter, or
  otherwise mutates game state — shadow mode means read-only, by construction,
  not by discipline.
- The shadow log is legible enough that a human (or `CATHEDRAL_REGARD_BLACKBOARD_1`'s
  own later build) could believe and act on it.

## criteria

A shadow-mode run against a real live session produces a Heat number, an
orbital-detection timer state, and a dark-tile-pause flag that track sensible
inputs (kyber/mindstone sales, faction-13 goodwill, Cathedral-ground
presence — cross-check exact inputs against `design/Jawa/kyber_trade_plot_spec.md`
§2/§3 and `design/Jawa/cathedral_concealment_arc_spec.md`'s "The law" section,
which both this item and its two dependents must respect: knowledge gate,
bans 1/2/3/6, rationed patience, Oracle laws, no Force, no worldgen), logged
without firing anything. Live injection ("then flip... for real") is
explicitly NOT this item's exit bar — that is M4's own later half, owed to
a follow-up once the shadow log is trusted.

## built (BENCH, 2026-09-13)

**`src/RimMandrake/Utils/gm_blackboard_shadow.py`** — the state machine. Flat
single-file script, matching this repo's Python-tooling convention
(`src/RimMandrake/Utils/` is all flat scripts, no subpackage). Polls the live
bridge, computes four numbers in-process, writes one JSONL record per poll,
fires nothing.

- **Read-only by construction**: a `safe_call()` gate refuses any tool name
  not in a fixed `ALLOWED_TOOLS` allowlist (`rimworld/get_game_info`,
  `jawa/map_info`, `jawa/list_factions`, `jawa/list_things`, `jawa/get_defs`,
  plus `rimworld/step_game_ticks` for time-advance — which the rimbridge
  skill's capability-matrix confirms "advances it without unpausing, no raid
  risk"). No `fire_incident`, `send_letter`, `save_game`, `execute_debug_action`
  or any `set_*`/spawn/destroy call exists anywhere in the file — not
  omitted by discipline, refused by code if ever added carelessly.
- **Inputs tracked, per poll**: `jawa/list_things` count of
  `Force_KyberCrystal` + `RUT_Mindstone` (the kyber family — mindstone not
  yet absorbed into `RUT_` names per kyber spec §1, so it polls defensively
  and will start contributing the moment it resolves, no code change); Hutt
  Cartel (`RUT_Jawa_HuttCartel`) goodwill via `jawa/list_factions`; Cathedral/
  faction-13 (`Mechanoid`, "the Forgotten Arsenal") goodwill + hostile flag,
  same call; current map's biome (`jawa/map_info`) checked against a v1
  dark-biome set (`Glowforest`, `BMT_CrystalCaverns`, `BMT_EarthenDepths`,
  `BMT_FungalForest` — all confirmed resolvable on the live 2026-09-13 mod
  list via `get_defs`) for the dark-tile pause.
- **Four tracked numbers**: Heat (sublinear bump on a kyber-family count
  *decrease* between polls, per kyber spec §3's "scale sublinearly"; slow
  decay absent sales), Hutt Interest (linear bump on the same delta, per
  kyber spec §4's "fed by kyber sales to any buyer"), Cathedral Regard (loses
  on any kyber-family sale + on high Heat near Cathedral ground, gains on
  low/falling Heat near Cathedral ground, per cathedral spec §2's up/down
  table; drifts toward zero absent signal — a shadow-mode-only choice, not a
  copy of the satiation vector's no-drift ruling, which is a different
  number), and the orbital-detection timer (ticks down, faster at high Heat,
  **paused** on a dark tile — `build_plan.md`'s "dark-tile pause" — logs a
  `would_fire` event and resets when it hits zero, never actually fires
  anything).
- **Known, documented gap**: Cathedral-ground presence has no authored
  tile/landmark id anywhere in the corpus yet (checked `the_rust_cathedral.md`
  and `worldbuilding/`) — the script uses a best-effort label/biome-string
  heuristic and logs its own confidence (`cathedral_ground_confidence`)
  rather than pretending certainty. Real geolocation is future build work,
  not this item's exit bar.
- **Reload-survival**: sidestepped, not re-derived. All state lives in this
  process's own JSONL log, never written into the save — per
  `enrichment_agents.md` §4's read-only-consumer framing, there is nothing
  here for a reload to lose.

## shadow-log evidence (real live session, 2026-09-13)

Bridge taken (`rimflow bridge take`), driven against the owner's actual live
campaign (tile 17007, "Zeddo's Salvage Yard", `RUT_ExtremeDesert`,
`ticksGame` 126808 at start). Two runs, 35 polls total, ticks 126808 →
144307 (~17.5k ticks, ~7 in-game hours), every poll a genuine bridge read —
`step_game_ticks` used to advance time paused (no unpause, no raid risk);
zero incidents fired, zero letters sent, zero saves written, verified by
reading the script's own call log (every call name is in `ALLOWED_TOOLS`).

- `infrastructure/state/facts/gm_blackboard_shadow_log_2026-09-13.jsonl` —
  15 polls at default GM-tuning constants. Current campaign genuinely holds
  zero kyber/mindstone right now, so Heat/Hutt Interest/Cathedral Regard sat
  at 0 throughout — a correct real reading (`countMatched: 0` of 7848 things
  scanned, `isCompleteList: true`), not a tool failure. `dark_tile: false`
  throughout (real desert biome). Orbital timer drained cleanly at the
  low-Heat rate (59800 → 57000), no fire in this window.
- `infrastructure/state/facts/gm_blackboard_shadow_log_2026-09-13_demo_orbital.jsonl` —
  20 polls with `--orbital-timer-start 800` (down from the 60000 default) to
  observe the would-fire → log → reset → continue cycle inside a short run,
  against the same real ticks/reads. **5 would-fire events logged, 0 fired**:
  `orbit` ran 600→400→200→[fire, reset to 800]→600→… four full cycles.
  Sample record (poll 4): `{"orbital_timer_after": 800, "would_fire":
  [{"type": "orbital_detection", "detail": "orbital-detection timer reached
  zero -- SHADOW MODE: logged only, nothing fired, no incident queued."}]}`.
  The tuning constant is a documented placeholder (kyber spec §3: "exact
  constants are M4 GM-layer tuning"), lowered only for this demo run via a
  new `--orbital-timer-start` CLI flag — the mechanism exercised is real,
  the threshold is deliberately cheap to reach.
- The kyber/Heat/Hutt-Interest pathway was **not** exercised by a live
  triggering event in this window, because the campaign genuinely has no
  kyber trade activity right now (verified zero, not assumed). The formula
  path (`_sale_heat`, sublinear scaling) is code-reviewable and structurally
  correct but unconfirmed against a real sale in this run — the honest
  limitation to flag for whoever next touches this, rather than staging a
  fake sale (which would require a write, against this item's own charter).

Bridge released (`rimflow bridge release`) after the runs.

## status: left in `doing`

Live injection ("then flip... for real") is explicitly out of scope per this
item's own spec — a separate, later step. Closing this item now would read
as "shadow mode done, ready to flip," which isn't earned yet: the orbital-
timer pathway is proven live end-to-end, but the kyber/Heat/Hutt-Interest
pathway has only been proven structurally, not against a real live sale
event. Left `doing` rather than closed so the next session (or a future
`rimflow next`) picks this up to either (a) watch for a real kyber sale in
the live campaign and confirm the Heat/Hutt pathway against it, or (b) judge
the structural proof sufficient and flip to live injection on a throwaway
save per M4's own sequencing. `KYBER_TRADE_PLOT_1` and
`CATHEDRAL_REGARD_BLACKBOARD_1` can now unblock on the *shape* of this
blackboard (the state machine exists, the inputs are named, the log format
is legible) even while this item itself stays open on the live-sale proof.
