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

## Acceptance proofs (GPT §5 table) — planned

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
