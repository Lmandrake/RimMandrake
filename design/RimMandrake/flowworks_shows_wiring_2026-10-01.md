# FlowWorks `shows=` wiring — 2026-10-01

Measured offline against `origin/main` at `4b3786455`. No bridge use, no `modcheck validate`,
no `--owner-said`. No code was changed: the wiring this pass was briefed to add already exists.

## Goal

Make the north-star visual floor bind something, starting with FlowWorks (VALIDATED, STALE).
The brief rested on "`shows=` appears in 0 of 54 mod validation.py files (MEASURED 2026-09-17)".
**That figure is out of date.** Re-measured today: `shows=` appears in **3 of 35** mod
`validation.py` files (`src/RimMandrake/*/validation.py`), and FlowWorks is one of them.
FlowWorks was wired at `84f3788da` (`FLOWWORKS_NORTHSTAR_WIRE_1`), and `d83c40a9f` added to it.

## Mapping

`src/RimMandrake/FlowWorks/validation.py` claims every id in the VALIDATED `## north star`
section of `design/validation_walks/RimMandrake/FlowWorks.md`:

- walk state VALIDATED; recorded hash == current hash (the section was not edited)
- must-show ids: **38**, uncovered **0**
- cannot-show ids: **5**, unclaimed **0** (each `never_*` id is claimed by a component that
  photographs the defect it rejects)
- orphan `shows=` ids (claimed but absent from the checklist): **0**
- Mod Settings toggle floor: 27 toggles, uncovered **0**

The mapping is one component per bar or small bar group, plot by plot (A dug channel, B fill
tiers, C limitless canal, C2/T tar, D limited pond, E fire, F slime, H depth ladder, G pit).
`(change)` bars end on a before|after diptych so the single-frame judge sees both states.

## Uncovered lines (findings)

**No must-show line lacks a component.** The real gap is that some claims cannot pass. Four
components claim six bars and raise `BLOCKED` unconditionally, because the feature is unbuilt.
They are claimed on purpose, so the bar FAILS rather than goes untested:

| component | bars | blocked on |
|---|---|---|
| `two_fluids_side_by_side` | `fill_fluid_distinct` | per-body fluid (ActiveFluid is one FluidDef per map) |
| `pit_cover_invisible` | `pit_covered_invisible`, `pit_covered_seam_at_max_zoom` | superdeep terrain-mimic cover |
| `sluice_state_look` | `sluice_gate_state_legible` | `FLOWWORKS_DOOR_FAMILY_1` |
| `spikes_look` | `spikes_read_distinct` | per-cell spikes |

The suite's own docstring also expects these bars to come back NO from the judge until art or
mechanics land: `tar_fill_front_lags_water` (no viscosity), plus the depth draw offset bars.
That is the bar doing its job, not a coverage hole. `canal_same_liquid_look` has no state
predicate (it is screenshot-only), so it is decided by the judge alone.

## Floor verdict

`python3 -m modcheck.cli floor --all`:
`FlowWorks  VALIDATED  bars 38  covered 38  uncovered 0  bar met`.
`runner.refusal(runner.visual_floor(suite, ns))` returns `''`, so a run would **not** be
REFUSED on the visual floor. Footer: Graffiti 8/8 and Pyrelands 19/19 are also met.

`modcheck status` still reads `FlowWorks STALE [stored: GREEN]`, and `doctor` raises
`STATUS_DISAGREEMENT`. STALE means the mod's content hash changed since the last recorded run.
It is a status-registry fact, not a coverage fact. Only `modcheck run FlowWorks` clears it, and
that needs the bridge, so the baseline run (`FLOWWORKS_NORTHSTAR_BASELINE_RUN_1`) is the next step.

## Sanity probe

The all-clear was suspect until the floor showed it could fail. These probes ran on in-memory
copies of the component list, and no file was edited:

- I removed every claim of `ladder_state_legible`. The refusal was `validated must-show lines
  no component claims: ladder_state_legible`.
- I removed every claim of `pit_reads_as_hole`. `uncovered_shows` returned `['pit_reads_as_hole']`.
- I added an unclaimed line `zz_unclaimed_probe` to the bar. It came back uncovered.
- I added an orphan claim `zz_orphan`. The refusal was ``` `shows=` ids absent from the
  validated checklist: zz_orphan ```.

So the gate can refuse in both directions, and the clean verdict is real.

## Selftests

`python3 src/RimMandrake/Utils/run_selftests.py` on the unmodified worktree:
**94/104 passed** (2 skipped, 1 unmeasured, 9 failed). None of the failures is from this pass,
which changed no code. Three of them touch north-star tooling:

- `modcheck/selftest_walklint.py`: `live repo: 0 walklint FAIL findings (got 3)`. One of the
  three is `SUBJECT_MISMATCH` on `design/validation_walks/RimUtinni/LanternDeeps.md`.
- `northstar_driver/selftest.py` and `selftest_judge.py`: `mock: unknown tool
  jawa/pawn_force_incapacitate`. A recent Northstar commit calls a tool that the mock
  transport (`northstar_driver/transport.py`) does not implement.

The other six are BlueDesert, label_collision_check, one_path_seam, sound_paths, sun_heat and
Bacta mock.

## Doc rot found

`CLAUDE.md` ("North-star validation state") says "`shows=` appears in 0 of 54 mod
`validation.py` files … the north-star system cannot GREEN anything". Both claims are false
today: the count is 3 of 35, and FlowWorks, Graffiti and Pyrelands meet their visual floors.
