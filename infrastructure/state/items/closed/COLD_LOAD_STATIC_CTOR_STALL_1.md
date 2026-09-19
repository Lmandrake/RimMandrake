# COLD_LOAD_STATIC_CTOR_STALL_1 — cold load hangs at the same checkpoint, even on a known-good mod list

Surfaced 2026-09-02 trying to enable+live-verify `WEATHER_SUITE_SLICE_1`
(`mandrake.rsw.weathersuite` + `mandrake.rut.weathersuite`, 594 mods).

## spec

Two consecutive restarts both hung indefinitely at the exact same point in
`Player.log`: the last line either run ever wrote is `Finished transpiling
1409 methods - <timestamp>`, immediately followed by silence — no further
log output, ever, in either run.

- **Run 1** (594 mods, WeatherSuite pair newly enabled): launched via Steam,
  hung. Waited ~70 minutes past "Finished transpiling" with zero new log
  lines. `Get-Process RimWorldWin64` showed `Responding: True` throughout and
  CPU climbing steadily (~800-900 CPU-seconds per 10 wall-clock minutes,
  consistent with 1-2 threads actively busy). `rimworld/get_game_info` via
  the bridge answered in 7-15ms the whole time (`"status": "no_game"`) — the
  Unity main thread was NOT starved/frozen, it was actively ticking and
  servicing bridge calls, just never reaching "Playing" or logging anything
  from whatever it was doing.
- **Isolation test**: killed run 1, reverted `ModsConfig.xml` to the
  pre-WeatherSuite 592-mod list (the SAME list that loaded cleanly multiple
  times earlier this session — see tonight's other closed items:
  `PAWN_FLAVOR_STAGELESS_ADD_FAIL_1`, `SONIC_WEAPONS_EXPANSION_1`, etc., all
  cold-load-verified clean on 592-593 mods within normal (~25-35 min) time).
  Relaunched. **Same stall reproduced**: hung at the identical
  "Finished transpiling 1409 methods" checkpoint, this time CPU growth
  slowed to near-zero within ~15 minutes of reaching it (an even stronger
  stall signal than run 1). Killed after ~15 minutes past the checkpoint.

**This means the stall is not attributable to `mandrake.rsw.weathersuite`/
`mandrake.rut.weathersuite` specifically** — the identical mod list that
worked fine several times tonight failed the same way immediately
afterward, with nothing in the repo, `Mods/` folder, or `ModsConfig.xml`
changed between the last known-good load and this one (WeatherSuite's own
`ModsConfig` entries were removed before the second attempt).

**What's different, circumstantially, between "worked earlier tonight" and
"now"**: several `Stop-Process -Force` kills on `RimWorldWin64` happened in
the hours before this stall (this session's own restart cycles, plus at
least one earlier "recovered from incompatible mods" auto-reset incident on
`FORSAKEN_CRAGS_PREDATORS_BUILD_1`'s pass). No other `RimWorldWin64` or
duplicate `steamwebhelper` processes were found lingering
(`Get-Process | Where-Object ProcessName -match 'RimWorld|steam'` showed
exactly one `RimWorldWin64` and the normal Steam process tree). Not
confirmed as the cause — a real hypothesis, not a finding.

**Third run, per this item's own `## verify` (don't conclude from 2 data
points alone)**: relaunched a THIRD time on the same untouched 592-mod list,
no changes of any kind between attempts. **Reproduced again, same
checkpoint** — "Finished transpiling 1409 methods" at 11:29:25 PM, ~20
minutes with zero further log growth before being killed. 3/3 consecutive
launches now stall at the identical point. This is no longer a single
fluke sample — it is the environment's current, repeatable behavior.
`ModsConfig.xml` was NOT auto-reset by this stall (still reads 592 after
the kill) — unlike the earlier `animalType`/incompatible-mods incidents
tonight, this failure mode does not trigger RimWorld's own recovery dialog;
it is a silent hang, not an exception.

Evidence preserved, do not delete:
- `Player-stuck-weathersuite.log` (run 1, 594 mods)
- `Player-stuck-baseline-592.log` (run 2, 592 mods, isolation test)
- `Player-stuck-baseline-592-attempt2.log` (run 3, 592 mods, third confirmation)
- all three under `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\`

`ModsConfig.xml` (live) and `ModsConfig.FULL.LATEST.xml` (repo) are both
currently restored to the confirmed-592 pre-WeatherSuite state. The game is
DOWN (all three attempts killed) as of this note. **Not attempting a fourth
restart solo** — three identical reproductions is enough to stop guessing;
further diagnosis likely needs something outside what a bridge/log-reading
seat can see (machine-level state: disk space, a pending Windows/Steam
update holding a lock, thermal throttling, a stuck driver).

## verify

- Determine what actually happens at/after "Finished transpiling 1409
  methods" in RimWorld's own startup sequence (this is the point just
  before the `StaticConstructorOnStartup` reflection pass fires across
  every active mod assembly, per the `rimworld-load-round` skill's own
  citation of `GenTypes.AllTypesWithAttribute`) — confirm against decompiled
  source, don't assume.
- Try a THIRD launch (fresh, no other changes) before assuming this is
  permanent — the isolation test's own baseline reproduction could itself
  be an environmental fluke (a single bad sample), not a fully proven
  pattern. Two data points at the same checkpoint is suggestive, not
  certain.
- If it reproduces a third time on the known-good list: consider a full
  machine-level check (disk space, a pending Windows/Steam update holding a
  lock, thermal throttling, a stuck GPU driver) before touching mods again.
- If it does NOT reproduce a third time: this may have been transient
  (resource contention from something else running on the machine), and
  `WEATHER_SUITE_SLICE_1` can retry its own restart once this item is closed
  or the pattern is otherwise explained.

## criteria

A cold load reaches "JawaBench ready" again on the known-good 592-mod list,
proving the environment itself is healthy, before any further mod-list
change is attempted. Root cause named if found; if genuinely unresolvable
from available evidence, say so plainly rather than guessing.
