# modcheck — scripted mod-functionality validation (pre-playtest)

Owner-designed sitting 2026-09-12 (BENCH). Every ruling below is his; the card
answers are recorded on this date. This is the test BEFORE the playtest: hit each
basic functionality component of a mod once, automatically, and record it. It is
not exhaustive and it is not the playtest.

## Rulings (owner, 2026-09-12)

- **Form** (re-ruled 2026-09-12 after measurement): one Python validation script
  per mod against the shared modcheck bridge library. Driving is deterministic
  Python at bridge speed (~16 ms/call MEASURED, `bridge_latency_bench.py`); the
  LLM never drives step-by-step — it judges the captured evidence afterward.
- **Build-up and tear-down are absolute** (owner, 2026-09-12): at lightning
  speed, clean build-up and tear-down control spurious interactions — pawns
  left to themselves do strange, unpredictable things. Create the state you
  wish to test thoroughly; destroy it completely when the chain ends.
- **Environment**: minimal mechanism list + the mod under test. Playtest stays on
  the full list; cross-mod conflicts are playtest's problem.
- **Evidence**: bridge state read-back AND one screenshot per component. Neither
  alone passes a component.
- **Component list**: the mod's Mod Settings toggles are the FLOOR — every toggle
  has at least one component — and the builder adds components for complex
  functions beyond any toggle (owner: "you'll need more tests than there are
  toggleable options sometimes"). The ceiling is open.
- **Gate**: no playtest offer without a current green run. Re-run after MAJOR
  changes; small tweaks may stay green by recorded builder judgment (`minor`,
  with a one-line why, on the ledger). Undeclared change = stale.
- **Reporting**: immutable `rimflow verify` event per run + an HTML flip-through
  sheet per run.
- **Failure**: auto-file a rimflow finding (screenshot attached) and CONTINUE the
  run to collect every failure.
- **Retrofit**: full wave — every shipped mod gets a validation script, after the pilot
  proves the format.

## 1. The validation script

`validation.py`, in the mod's source folder in the repo. Never deployed —
`deploy_custom_mods.py` must skip it by name. Python, importing ONLY the shared
modcheck library — no direct RimBridge use in a mod's script, because the
library is where the read-back, pause, and teardown discipline lives. *(The
steps-YAML format from earlier the same day is dropped — with no LLM
improvising mid-run, the script itself must express walk-until, poll-until and
conditional read-backs, and YAML asked to do that becomes a bad programming
language. Runtime speed was measured identical either way.)*

**A script captures the ENTIRE setup** (owner, 2026-09-12): it starts from a
cleared test area and spawns everything it needs — never "show someone can fall
in the pit" against whatever the map happens to hold, but "clear all map
contents; spawn a person; cause them to walk over the pit; demonstrate they
fall in". A component whose preconditions came from outside the script is a
lint error.

**Components may CHAIN** (owner, 2026-09-12): components grouped in a chain
share one setup and run sequentially, each continuing from the previous
component's end state — no per-component stand-up/tear-down. (Measured
2026-09-12: per-call latency is ~16 ms, so the saving is in setup work and
game-tick waits, not call count — and a chain is one scenario told in order,
which is also easier to judge.) Tear-down happens at CHAIN end, per §1b. The
pit mod as one chain: clear area → spawn pits + pawn → walk over → falls in →
cannot leave → health decreases under overhead sun → decrease stops when
tended; a second chain: oversize pawn pauses at the pit but is not captured;
a third: climbing and flying animals escape by the same process. When a
component in a chain fails, its finding is filed and the run continues — but
downstream components of that chain whose state is now meaningless record
**UNMEASURED (upstream failed)**, never pass or fail, and the runner moves to
the next chain.

```python
from modcheck import Suite

suite = Suite("RM_PitTraps")

@suite.chain("pit_capture")
def pit_capture(t):                       # t: the chain's test context
    t.clear_area(size=40)                 # setup is the script's job, always
    pits = t.spawn("RM_Pit", count=3, at="line")
    raider = t.spawn_pawn("raider", hostile=True, beyond=pits)

    with t.component("falls_in", toggle="pitsEnabled"):
        t.walk_over(raider, pits)
        t.wait_ticks(600)
        t.expect_in_cell_of(raider, "RM_Pit")
        t.screenshot()

    with t.component("cannot_leave", toggle="pitsEnabled"):
        t.order_to(raider, "map-edge")
        t.wait_ticks(1200)
        t.expect_in_cell_of(raider, "RM_Pit")
        t.screenshot()
    # ... sun damage, tended-stops — same chain, shared state
    # teardown is AUTOMATIC at chain end: the library sweeps every id it spawned

@suite.chain("oversize_pass")             # fresh setup, new chain
def oversize_pass(t):
    t.clear_area(size=40)
    pits = t.spawn("RM_Pit", count=3, at="line")
    with t.component("pauses_not_captured", beyond_toggle=True):
        beast = t.spawn_pawn("RM_OversizeBeast", beyond=pits)
        t.walk_over(beast, pits)
        t.wait_ticks(900)
        t.expect_not_in_cell_of(beast, "RM_Pit")
        t.expect_reached_past(beast, pits)
        t.screenshot()
```

- `toggle=` on a component names a Mod Settings field; `beyond_toggle=True`
  marks behavior no toggle owns. The library cross-checks the mod's settings
  def and REFUSES a mod whose toggle has zero components (floor enforcement).
- The verb vocabulary lives in the LIBRARY and grows there, never in per-mod
  code; `t.bridge_call(tool, args)` is the escape valve, and every mutation
  through it still pays the read-back.
- Every `expect_*` is a bridge READ compared against a stated value. Every
  write that HAS an independent read-back channel pays it, enforced at runtime
  — the ~40 silent-success bridge calls are the reason this system exists. A
  write with NO such channel is not refused but lands in evidence marked
  **UNVERIFIED** (owner ruling 2026-09-12): a component containing one can
  only report **PASS(UNVERIFIED n)**, never a clean PASS.

## 1b. Build-up and tear-down are the test (owner, 2026-09-12)

Owner, verbatim: *"if we really do have python using the bridge at lightning
speed clean build up and tear down is absolutely crucial to control spurious
interactions. Pawns left to themselves do all sorts of strange unpredictable
things. We must create the state we wish to test thoroughly."*

- A chain CREATES every element of the state it tests — cleared area, things,
  pawns, weather and time where they matter. A precondition from outside the
  script is refused, not warned about.
- A chain ENDS by destroying everything it made: the library tracks every id
  it spawned and sweeps them at chain end — and on abort — then re-reads the
  area and asserts it is empty. A chain that leaks a pawn poisons every later
  chain in ways no assertion anticipates.
- TIME STAYS PAUSED except inside an explicit `wait_ticks`/`play_for`. The
  library re-pauses at every component boundary and VERIFIES the pause
  (ticksGame read twice) — unattended ticks between steps are exactly the
  spurious interactions the ruling names.
- Hostiles spawn inside the cleared test area, never near anything else, and
  never outlive their chain.

## 2. The runner and the library

`src/RimMandrake/Utils/modcheck/` (dev tooling — exempt from the three-tier
naming scheme). Entry: `modcheck run <mod> [<mod>...]`.

The library is substantially an EXTRACTION, not a new build (census 2026-09-12):
`rimbench/core.py`'s `Session.mutate()` already enforces success≠change
read-backs; `load_session.py` is the gated ordered-step prior art; the
plan-JSON replay idiom (sea-landmark cleanup, `apply_floor_plan.py`) is the
deterministic-drive idiom. Add what nothing owns yet: reconnect-with-
post-condition-polling after a timeout (the poisoned-socket trap, today handled
by only two polling scripts), spawn-tracking teardown (§1b), pause verification,
and automatic evidence capture.

**The LLM never drives.** The script runs deterministically (~16 ms/call
MEASURED at 593 mods, `bridge_latency_bench.py`, 2026-09-12); it captures an
evidence bundle — raw read-backs + screenshots per component — and one model
pass at the end judges outcomes against each component's stated expectation.

**Two run modes** (owner addendum, 2026-09-12):

- **Smoke mode** (the default): a full checkout of a mod simply to re-smoke-test
  it after a change. Checkpoints are NO-OPS; the run is as fast as the bridge
  allows; evidence is per-component only.
- **Debug mode** (`--debug`): for INITIAL checkout of a mod, or when a bug is
  known. A script may declare `t.checkpoint("name")` at sensing points inside a
  complex chain — in debug mode each one dumps the full local state (things and
  pawns in the test area, positions, relevant hediffs/fields, ticksGame) plus a
  screenshot into the evidence bundle, so a failure can be localised between
  two checkpoints instead of autopsied from the end state. `--debug` also
  implies `--halt-on-fail`: stop at the first red component with the area left
  intact for live inspection. Checkpoints are free to sprinkle — they cost
  nothing outside debug mode.

Per session: capture current ModsConfig (the existing `modlist_swap.py`
discipline), swap to MINIMAL + the mods under test, restart to a quicktest map
(~90 s), take the bridge lock (`rimflow bridge take`), run each mod's components
in order, release, restore the FULL list. Multiple mods batch into one swap
session. FOUNDRY owns runs; never during an owner session; one bridge driver.

Per component: execute steps; read back after every write; screenshot at the
declared moment (bridge screenshot; `system_screenshot.py` is the fallback when
the bridge one returns success-and-nothing). A failed expect files a rimflow
finding on the mod's item naming the component, with the screenshot path — and
the run CONTINUES.

## 3. The record

- `rimflow verify` per run: `<mod> N/N components`, pass/fail each, immutable.
  This is the durable truth.
- One HTML sheet per run in `Transient/modcheck/<MOD>_<UTC>.html`: component /
  expected / observed / screenshot. Transient shelf life (~14 days) is fine —
  the ledger outlives it; a finding copies what it needs into its own item.

## 4. Gate and staleness

`infrastructure/state/modcheck_status.json`, owned by the runner's CLI, never
hand-edited — the CODE_REVIEW_STATUS pattern: per mod, last green run id and the
content hash of the mod's files at run time.

- Hash mismatch → provisionally STALE.
- `modcheck declare <mod> minor --why "<one line>"` (a ledger note) re-greens it
  at the new hash. Anything not declared minor is major.
- **A minor declaration is only valid for a trivial change without gameplay
  effect** (owner, 2026-09-12): text/description strings, or a very slight
  parameter adjustment. The declare command prints the mod's diff `--stat` at
  declare time and records it with the note, so the claim is checkable against
  what actually changed — a C#, patch, or def-structure change declared minor
  is a wrong declaration, and whoever spots it flips the mod stale.
- The playtest offer path checks GREEN. No green, no playtest.

## 5. Rollout

1. `MOD_VALIDATION_RUNNER_1` — runner, step vocabulary v1, floor enforcement,
   status registry, verify + HTML report, deploy-tool skip rule.
2. `MOD_VALIDATION_PIT_PILOT_1` — the pit mod end-to-end: validation.py written from
   its settings toggles + beyond-toggle components (falls-in, climb-out vs not,
   and the rest of its defined functionality), run green, sheet reviewed by the
   owner once to ratify the report format.
3. `MOD_VALIDATION_RETROFIT_1` — every shipped mod gets a validation script. Filed now,
   starts only after the pilot ratifies the format.
