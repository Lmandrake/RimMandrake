# modcheck — scripted mod-functionality validation (pre-playtest)

Owner-designed sitting 2026-09-12 (BENCH). Every ruling below is his; the card
answers are recorded on this date. This is the test BEFORE the playtest: hit each
basic functionality component of a mod once, automatically, and record it. It is
not exhaustive and it is not the playtest.

## Rulings (owner, 2026-09-12)

- **Form**: one steps file per mod + one shared runner. No per-mod Python.
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
- **Retrofit**: full wave — every shipped mod gets a steps file, after the pilot
  proves the format.

## 1. The steps file

`validation.steps.yaml`, in the mod's source folder in the repo. Never deployed —
`deploy_custom_mods.py` must skip it by name.

**A script captures the ENTIRE setup** (owner, 2026-09-12): it starts from a
cleared test area and spawns everything it needs — never "show someone can fall
in the pit" against whatever the map happens to hold, but "clear all map
contents; spawn a person; cause them to walk over the pit; demonstrate they
fall in". A component whose preconditions came from outside the script is a
lint error.

**Components may CHAIN** (owner, 2026-09-12): the bridge is slow, so components
grouped in a chain share one setup and run sequentially, each continuing from
the previous component's end state — no per-component stand-up/tear-down. The
pit mod as one chain: clear area → spawn pits + pawn → walk over → falls in →
cannot leave → health decreases under overhead sun → decrease stops when
tended; a second chain: oversize pawn pauses at the pit but is not captured;
a third: climbing and flying animals escape by the same process. When a
component in a chain fails, its finding is filed and the run continues — but
downstream components of that chain whose state is now meaningless record
**UNMEASURED (upstream failed)**, never pass or fail, and the runner moves to
the next chain.

```yaml
mod: RM_PitTraps            # folder name as deploy knows it
chains:
  - name: pit_capture
    setup:
      - clear_area: {size: 40}
      - spawn_thing: {def: RM_Pit, count: 3, at: line}
    components:
      - name: falls_in
        toggle: pitsEnabled
        steps:
          - spawn_pawn: {kind: raider, hostile: true, beyond: pits}
          - move_pawn_to: {pawn: last, across: pits}
          - wait_ticks: 600
        expect: [pawn_in_cell_of: {pawn: last, def: RM_Pit}]
        screenshot: after-expect
      - name: cannot_leave      # continues from falls_in's end state
        toggle: pitsEnabled
        steps: [move_pawn_to: {pawn: last, to: map-edge}, wait_ticks: 1200]
        expect: [pawn_in_cell_of: {pawn: last, def: RM_Pit}]
        screenshot: after-expect
      # ... sun damage, tended-stops, in the same chain
  - name: oversize_pass        # fresh setup, new chain
    setup: [clear_area: {size: 40}, spawn_thing: {def: RM_Pit, count: 3, at: line}]
    components:
      - name: pauses_not_captured
        beyond-toggle: true
        steps: [spawn_pawn: {kind: RM_OversizeBeast, beyond: pits}, move_pawn_to: {pawn: last, across: pits}, wait_ticks: 900]
        expect: [pawn_not_in_cell_of: {pawn: last, def: RM_Pit}, pawn_reached: {pawn: last, past: pits}]
        screenshot: after-expect
```

- `toggle:` names a Mod Settings field; `beyond-toggle: true` marks a component
  covering behavior no toggle owns. The runner cross-checks the mod's settings
  def and REFUSES the mod if any toggle has zero components (floor enforcement).
- Step vocabulary starts small and grows in the runner, never in per-mod code:
  `clear_area`, `spawn_thing`, `spawn_pawn`, `move_pawn_to`, `wait_ticks`,
  `set_weather`, `set_setting`, `bridge_call` (generic escape valve: named
  tool + args), `assert` / `expect` read-backs, `screenshot`.
- Every `expect` is a bridge READ compared against a stated value. A write step
  with no subsequent read anywhere in the component is a lint error — the ~40
  silent-success bridge calls are the reason this system exists.

## 2. The runner

`src/RimMandrake/Utils/modcheck/` (dev tooling — exempt from the three-tier
naming scheme). Entry: `modcheck run <mod> [<mod>...]`.

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
2. `MOD_VALIDATION_PIT_PILOT_1` — the pit mod end-to-end: steps file written from
   its settings toggles + beyond-toggle components (falls-in, climb-out vs not,
   and the rest of its defined functionality), run green, sheet reviewed by the
   owner once to ratify the report format.
3. `MOD_VALIDATION_RETROFIT_1` — every shipped mod gets a steps file. Filed now,
   starts only after the pilot ratifies the format.
