# Test-state monitor + run governor — first build (GPT §5)

Item: `TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO`. Basis: GPT review
`design/RimMandrake/test_control/test_control_review_gpt_20261013.md` §5, bound by the owner's rulings in
`design/RimMandrake/debug_process.md` § "Test disturbances" (corrected anomaly with no damage may PASS; damage to
the test restarts the row, never FAIL; every threat is logged and gets a test-environment item; long runs only
when clearly worth it; protected colonists only on rows labelled not about health/needs/damage/death).

## Reused, not rebuilt

| piece | where | used for |
|---|---|---|
| TPS record's ordered bounded writer | `JawaBenchTpsWriter.Enqueue` | every monitor row (kind `vitals`), same JSONL files telemetry already ingests |
| TPS sampler's Root.Update finalizer | `JawaBenchTpsSampler.RootFinalizer` | the W250 wall-time pass (runs while paused) |
| event recorder's `Pawn.Kill` postfix | `JawaBenchEventRecorder.KillPostfix` | death tombstones that survive corpse removal |
| incident journal + origin recorder | `JawaBenchAwareness*.cs`, `jawa/incident_journal` | threat attribution stays there; the monitor watches effects |
| hook installer, meters, switches | `JawaBenchTpsInstall`, `JawaBenchAwarenessCore.Meter` | per-source cost + off switch |
| tool families | `JawaBenchSafetyCore.CampaignDenied` | `jawa/safe_advance` is test-only; `jawa/vitals` reads stay available |
| verdict vocabulary | `modcheck/contract.py` CLEAN / DISRUPTED / INDETERMINATE | the governor's validity |
| clock gate | `modcheck/clockgate.py` | session/row budgets; the governor's advance goes through it |
| telemetry stack | `telemetry/ingest.py`, `analysis.py` → `alerts.json` → RimPulse | series + four alarms |

## Added

**C# (companion)**
- `JawaBenchVitalsCore.cs` — pure (unit-tested in `AwarenessSelfTest`): clock ledger (processed ticks vs
  `TicksGame`, discontinuity kinds), latch, advance policy, stop rules, rollups, row formatting.
- `JawaBenchVitals.cs` — the Verse half. `TickManager.DoSingleTick` prefix+postfix installed at first arm
  (counts processed ticks, catches reassignment between ticks; T60 pawn sample every 60 *processed* ticks).
  W250 pass from the TPS frame finalizer: pause/speed, clock-while-paused, window stack with ages, new letters
  (incl. `LetterDefOf.GameEnded`), `GameEnder.gameEnding`, heartbeat. Tombstones from the Kill postfix.
- `JawaBenchVitalsTools.cs` — `jawa/vitals` (arm / disarm / status / sample / events / clear; arm takes
  critical actor ids, specimen ids, `timeException`, `protected` label) and `jawa/safe_advance` (refuses
  over-budget on a populated map without a time exception; steps ≤60-tick chunks per frame with a frame budget;
  stops on a latched death / downed critical / colonist hostile / new hostile / threat structure / modal /
  colony loss / starving critical / clock discontinuity; cancellable).
- `jawa/time_set_ticks` gate: refused on a map with a spawned free colonist unless `timeException=true`
  (with a reason); every accepted call is a declared discontinuity in the ledger.

Channels (each its own switch in `vitals_settings.json`, its own meter): `pawns`, `threats`, `clock`, `ui`,
`subjects`, `heartbeat`. Every row: session, game epoch, map id, ticksGame, ticksAbs, utc, mono, seq.
A source that is off or unread reports `UNMEASURED`, never 0.

**Python**
- `modcheck/governor.py` — `RowContract` (about-tags, required actors, specimens, tick budget, time exception,
  protection; protection refused when the row is about health/needs/damage/death) and `RowGovernor`
  (PRECHECK → ARMED → EXECUTING → CHECKING → COMPLETE | LATCHED). Disturbance → outcome:
  damage to the test (critical actor downed/dead/hurt, specimen gone, colony loss, fire in scope) → `RESTART`;
  anomaly corrected with no damage → `PASS_ALLOWED` (validity CLEAN with note); coverage lost → INDETERMINATE.
  Every threat is logged and yields a ready-to-file `rimflow file TESTENV_..._HARDEN_...` line.
  `run_row(fn, max_restarts)` drives restarts. `governed_advance()` calls `jawa/safe_advance`.
- `telemetry/ingest.py` — `vitals` rows → `rm_game_pawns_{alive,downed,dead,hostile,bleeding,mental,min_health}`
  by bounded class, `rm_game_threat_structures`, `rm_game_modal_age_s`, `rm_game_clock_disc_total`,
  `rm_game_vitals_latched`; latches become events.
- `telemetry/analysis.py` — alarms: alive colonists 0, a colonist hostile, hostiles on a test map, modal stuck.

## Acceptance proofs (GPT §5 table) — planned (results below)

| case | how | where |
|---|---|---|
| 600,000-tick request on populated map refused | `safe_advance ticks=600000` | live, quicktest |
| direct clock reassignment detected, row cannot be CLEAN | `time_set_ticks timeException=true` → ledger discontinuity → governor not CLEAN | live |
| `time_set_ticks` refused on populated map without exception | call without the flag | live |
| death retained after corpse removal | kill pawn, destroy corpse, read tombstone | live |
| dormant/hostile structure detected without hostile pawns | spawn a hostile turret | live (cheap); mech cluster deferred |
| raid during a long step interrupts | arm a delayed raid, `safe_advance` 30,000 | live |
| worker downed during wait → DISRUPTED / RESTART, no FAIL | incapacitate critical actor mid-advance | live + offline |
| modal appears while paused | open a dialog while paused, W250 sees it with age | live |
| colony-loss letter detected | kill all colonists, step past the 400-tick countdown | live |
| coverage expiry / read failure prevents CLEAN | TTL expiry, failed status | offline |
| expected transition accepted, extra flagged | contract expectations | offline |
| map transfer distinguished from death | — | deferred (needs gravship/caravan fixture) |

Cost: each channel's meter is read from `jawa/vitals status`; an unexercised hook is reported UNMEASURED.
The 23-mod tier and full-list overhead comparison is deferred to a separate measured run.

## Results — live, 2026-10-13 (minimal list + GSS, quicktest maps)

Script `src/RimMandrake/bridgetools/prove_vitals_governor.py`; evidence `Transient/vitals_governor_proof_20261013/`.
15/15 cases PASS on the final DLL:

| case | result |
|---|---|
| 600,000-tick advance on a populated map | refused before any tick (tick 1 -> 1) |
| clock reassignment without a time exception | refused on a populated map |
| declared reassignment (2,500 ticks) | ledger: declared discontinuity; governor RESTART without a row exception, PASS with one |
| undeclared jump (fastEcology, one tick = 2,000) | advance stopped after 1 tick by `clock_discontinuity` |
| modal while paused (Dialog_Options) | `modal_stuck` at 30 s wall while paused; closed + corrected -> CLEAN, PASS allowed |
| mech cluster landing | 13 hostile structures (3 turrets, 2 spawners, 5 dormant) latched; advance stopped at 240 ticks by `threat_structure` |
| raid during a 25,000-tick advance | stopped locally at ~1,000-1,500 ticks by `hostile_arrival`; `TESTENV_HOSTILES_HARDEN_KNOCK_FIRST` line printed |
| worker downed mid-advance | stopped by `downed` (critical); governor DISRUPTED -> RESTART, criterion FAIL not scored |
| death, corpse destroyed | death trigger + tombstone retained |
| specimen destroyed | `specimen_lost`; governor RESTART instead of a false FAIL |
| colony loss | `alive colonists 0` + `GameEnder countdown started`; injected GameEnded letter latched while paused |

Found by the proofs and fixed: a reassignment before the first wall pass was missed (clock base now set at arm);
hostile ancient WALLS latched thousands of rows (threat = turret/spawner/dormant/condition-causer/non-humanlike faction;
baseline coalesced to one row); a game-over countdown started and was cancelled (Man in Black) between two wall passes
(letters + GameEnder now also read every T60 sample); a once-a-minute alarm missed the transient colony loss (RimPulse
now also alarms on latched `colony_loss` / `colonist_hostile` triggers). Telemetry ingested live: `rm_game_pawns_*`
series and `vitals_trigger` events present; `vitals:hostiles` amber fired during the raid/cluster rows.

Measured cost (quicktest map, ~14-80 pawns, one session): pawns sample mean 184-251 µs per 60 processed ticks
(max 5-8 ms first sample); threats mean 38 µs; clock hook ~1 µs per tick; ui pass ~25 µs per 250 ms.
`subjects` and `heartbeat` UNMEASURED until exercised in a session that reports them.

## Wired (WATCH_WAIT_WIRE_SMALL_STEPS, dbdfef28f7)

`clockgate.advance_chunk` is the one tick mover: `jawa/safe_advance` when the companion has it (else the legacy
`rimworld/step_game_ticks`), raising `clockgate.GovernorStop` (a surprise abort: UNMEASURED, never FAIL) when the latch
stops it. `clockgate.step` (so `Watch.wait`), `Suite.wait_ticks`, `validation_core` `ticks()` and every Pyrelands `_wait`
go through it. Live 2026-10-13c: a Pyrelands row ran on safe_advance only; a critical colonist at Food 0 stopped a
2,000-tick step after 60 ticks and the governor judged RESTART / DISRUPTED (`Transient/bench_live_20261013c/`).

## Deferred

- Map transfer vs death (needs a gravship/caravan fixture); hook-skip / observer-throw / reload rows of GPT's table.
- Overhead A/B on the 23-mod tier and the full list (armed vs off), as GPT §5 asks.
- Callers of `jawa/time_set_ticks` on populated maps (northstar_driver/site.py, scenes/scenelib.py, mod scripts via
  bridge_call) are now refused until they declare a time exception or prepare the time before pawns exist.
