# RIMMANDRAKE_BUILD_PIPELINE_CONTROL_ONE_LINERS_NO_BUILD_PROCESS

## What the card said

<!-- answered 2026-11-18T19:26:34Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** A "void" run is one that died of a system fault, was stopped by us, or that you declare should not count; under the new design it never spends a trial, look or cycle. Each stage also has a spend ceiling (about 25M weighted tokens) that pauses a mod when reached. The tokens a void run burnt are real. Should a void run's spend count toward that stage ceiling?
**Picked:** Does not count (Recommended)
**Its description:** Why: a ceiling should measure what the mod cost on its merits. Buys: no mod is paused by our own faults or stops. Costs: a fault loop could burn tokens unseen by the ceiling; a separate system-fault alarm must catch it. Recommended: it matches your rule that system failures never charge the mod.
**Other options:** Counts in full · Own ceiling for void spend

**Question:** The new one-line command turns work off for everything, one mod, one stage or one item. New launches stop at once in every case. Today, stopping Graffiti's running work took a separate manual kill, while runs that are killed lose whatever they had not yet saved. What should turning something off do, by default, to runs that are already running?
**His words:** Each of these should be specific commands. "Stop work immediately and write where you are." "Stop work at the next easy spot and write where you are." "STOP NOW without write." Defaults for the system are nice, sure... should be Stop work at the next easy spot and write where you are" should be the default always. But we shouldn't rely on defaults. The agent should be precise in its instruction and use the right option. We don't need to prethink this.
**Other options:** Stop one, spare all (Recommended) · Always let them finish · Always stop them · Refuse until told

## spec
Slice 1 ("Core") of `design/specs/2026-11-18-pipeline-control-surface/03-merged.md` section 5: one SQLite control
store (`~/.local/state/rimmandrake/control/control.db`, `RM_CONTROL_DB` for tests), `src/RimMandrake/rimflow/control.py`
and `./pipe`: on/off by scope, show, why, log, void, grant look, and the three stop commands (owner, by card
2026-11-18: `--write-now`, `--at-easy-spot` (default, always named), `--kill`); `launch_unit()` with `admit()` on every
`systemd-run` launch site; reserve-then-settle for the granted coverage look; the ExecCondition re-check; the
system-fault meter. The owner, 2026-11-18 ~10:40 AM PST: "This should be a one-line bash command, ok? Build that
immediately."

## verify
`python3 src/RimMandrake/rimflow/selftest_control.py` (prints PASS selftest_control; real `rm-probe-` units).

## criteria
Every criterion in the builder's brief: both pause-race orderings, one look for two callers, duplicate settle/void,
unreadable/corrupt/locked store, crash before/after start, two clones, void never moves a stage, `on all` keeps his
hold, --kill kills a TERM-ignoring unit and child within 1 s, the stop order reaches a running stub agent, every
`systemd-run` site routed (mutant watched red), every verb's p95 under 1 s.

## refs
new: src/RimMandrake/rimflow/control.py
new: src/RimMandrake/rimflow/selftest_control.py
file: src/RimMandrake/rimflow/detached_helper.py
