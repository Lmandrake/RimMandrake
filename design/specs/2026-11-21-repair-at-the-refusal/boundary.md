# BOUNDARY: a fault of form is repaired where it is found; the fault loop counts substance only, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/form_fault.py` (the one shared answer), `src/RimMandrake/rimflow/run_void.py`
(`sync_system`: the class of a launch that never started), `src/RimMandrake/rimflow/maturation_dispatch.py` (the
Stage 3 launch fault, `form_repair_gate`, `repair_launch`, `system_fault_stop`), `src/RimMandrake/rimflow/detached_helper.py`
(`FOOTER`) and `src/RimMandrake/rimflow/role_launch.py` (`launch_argv`: the brief line). Item
`RIMMANDRAKE_REPAIR_AT_THE_REFUSAL_NO_STOP_FOR_UNTIED_SHOES`, written 2026-11-21. The ruling:
`design/RimMandrake/standing_rulings.md` §A fault of form is repaired where it is found. Each promise has a check of its
name in `src/RimMandrake/rimflow/selftest_repair_at_refusal.py`. The census of refusal sites: `census.md` beside this
page.

Why: on 2026-11-20 eleven gates refused work for a fault of form. A program caller (the tick) sent the same refused
input again, and `OPS_MATURATION_SYSTEM_FAULT_LOOP` turned three refusals of any kind into a paused mod that waited
for the Conductor's hand. The refusal texts of that night are in the dispatch state
(`/mnt/d/ClaudeWork/rimmandrake/dispatcher/maturation/state.json`, `mods.<Mod>.system_faults`).

## ACCEPTS (the only inputs this is built for)

- **a-refusal-text.** The text of a refusal as a gate printed it or a launch returned it: any string, or None.
- **a-dispatch-state.** The tick's `state.json` shape: `mods.<Mod>` with its books (`steward`, `fixers`,
  `blind_auto`, `ingame_auto`, `launches`, `holder_road_back`, `pilot_launches`), `system_faults`, `cleared` and the new
  `form_repairs` list.
- **a-repair-launch.** The tick's launcher for a repair run: `fx["repair_launch"](mod, brief) -> (ok, text, unit)`, by
  default `maturation_dispatch.repair_launch` (it files an item and launches `detached_helper.py launch` on it).

## DOES NOT SURVIVE (not promised)

- **a-machine-fault-at-launch.** A machine fault that stops a launch (no space, systemd-run) is not told apart from a
  gate's refusal: both are "never started", both owe a repair. The repair run's own launch then meets the same fault,
  and `a-repair-launch-refused-names-the-conductor` hands it on. One principle, no table. A refused pool clone is the
  one exception (`a-pool-refusal-is-a-wait`).
- **a-repair-run-that-lies.** A repair run that ends success and fixed nothing: the next same refusal counts once as
  substance (`a-repair-that-did-not-hold-counts-once`), so at most the loop's limit is spent.

## PROMISES (each one is owed a check of the same name)

- **form-note-repairs-and-continues.** `form_fault.repaired(what, how, event=e)` prints one line that starts
  `NOTE (form, repaired): `, appends `{what, how}` to `e["form_notes"]`, and returns it. Nothing in it exits.
- **form-refusal-names-its-repair.** `form_fault.refusal(what, repair)` returns a text with `REFUSED (form): <what>`
  and `REPAIR: <repair>`; an empty repair raises ValueError (a form refusal with no repair is not allowed);
  `form_fault.repair_of(text)` returns the repair.
- **every-brief-carries-the-repair-line.** `detached_helper.FOOTER` and the message `role_launch.launch_argv` gives
  claude both carry `form_fault.BRIEF_LINE`.
- **a-launch-that-never-started-is-form.** A book entry that never started (any refusal text, a machine's
  `LAUNCH FAILED`, a transient fault that outlasted its retries, or none) adds 0 system faults and owes one repair.
  A wait (`maturation_autonomy.wait_refusal`: the drain, a held bridge, control's `./pipe` stop) owes none. There is
  no table of refusal kinds.
- **a-repair-launch-refused-names-the-conductor.** A repair run whose launch is refused `REPAIR_LAUNCH_MOST` times
  leaves the row `repairing` with a `need` line naming the Conductor, and counts no fault.
- **the-launch-refusals-count-no-fault.** Cases 1 to 6 of the night (the drain, the game-folder visit check, the
  visit name, the ignored lock file, the 66-character name, the card paste), each replayed as a never-started book
  entry through `run_void.sync_system`, add 0 system faults, leave the mod off `system_fault`, and each form case
  owes one repair (`form_repairs`). The drain owes none (it is a wait). Red on the base: each counted 1.
- **a-dead-run-still-counts-one.** A run whose record shows it killed adds 1 system fault, as before.
- **form-refusal-is-repaired-not-resent.** A tick on a mod that owes a repair launches the mod's own work nothing,
  starts one repair run with the refusal as its brief, and the mod's row reads `repairing: <what>`. While that run is
  live, the next tick starts no second one and still reads `repairing:`. When it ends, the next tick launches the
  mod's own work again.
- **a-repair-that-did-not-hold-counts-once.** The same refusal (same fingerprint) after a finished repair run adds
  1 system fault, with the cause "the repair of <what> did not hold".
- **the-trip-starts-a-repair.** At the fault limit the row reads `system_fault` and the tick starts one repair run
  with the faults' causes as its brief and says so in the row; when that run ends, the next tick clears the count by
  itself (a `cleared` entry naming the run). A second trip after a repair run of its own names the Conductor
  (`needs_conductor`) and starts no third repair: two repairs that did not hold mean the fix is unknown.

- **a-tick-with-stand-ins-launches-nothing-real.** A tick given fixtures (`fx` not empty) and no `repair_launch`
  starts no repair run; only the live tick (no fixtures) uses the real `repair_launch`.

- **a-refused-repair-launch-reuses-its-filed-item.** A repair launch that filed its item and then failed (a publish,
  a launch) is retried on that same item, never a new one (2026-11-21 02:08 PST: GimmeSomeSlack's first repair launch
  left `..._RUN_FOUR` filed and unused).

- **repairing-is-a-named-wait-never-paused.** A row that reads `repairing` is class `wait`, its `waits_on` the repair,
  never `paused` (no pause alarm, no stall).

- **a-pool-refusal-is-a-wait.** `scratch_clone.pool_admit`'s refusal (`POOL REFUSED: pool full` or `pool at <N> GB`)
  is a wait refusal (`AUT.wait_refusal`; `form_fault.fault_class` gives `wait`). It ends when a run returns its clone,
  which the next launch reuses without the count or GB check. The pool's own alarm, `disk.pool_breach`, owns a pool
  that never frees. Pyrelands, 2026-11-22: its certificate rerun and that rerun's form repair were refused a clone 4
  times, and the repair's third refusal named the Conductor.
- **a-pool-refused-repair-launch-spends-no-try.** A repair launch refused a pool clone records `launch_failed` and adds
  no repair try, so it never names the Conductor. The next tick launches it again.
- **an-owed-pool-refusal-owes-no-repair.** An owed form record whose text is a wait refusal is set to state `wait`
  (neither open nor done). It starts no repair run, and the mod's own act goes on in the same tick.
- **a-pool-refused-cert-rerun-starts-again.** A certificate rerun whose own result error is a wait refusal is started
  again on the same build key. It spends no try (`cert_rerun.tries` is unchanged) and owes no repair.
- **a-raced-cert-rerun-publish-starts-again.** When the certificate rerun's publish stops on a replay conflict in the
  mod's own `test_table.json` alone, the worker drops its stamp commit (`git reset --hard origin/main`: the clone has one
  owner and the table is derived) and writes `race: true`. The tick then starts the rerun again on the newer table. It
  spends no try and owes no repair. A result written before this rule has no `race` field, and the tick reads it by
  that same conflict text. A conflict in any other file drops nothing and stays a form refusal. Pyrelands, 2026-11-22
  4:19 PM PST: a testq-blocks commit landed during the rerun's 449 s.

## LIMITS

- **One open repair per mod.** Danger: two repair runs editing the same pipeline path at once. Evidence: tonight's
  case 2 and case 3 sat on the same in-game launch path within an hour.
- **One automatic repair per trip, two trips.** Danger: a repair loop that spends on a fault nobody can fix. Evidence:
  the ExplosiveKnockback coverage judge's nine refusals in three hours (~90M tokens against a 4M cap,
  `refusal_contract.py`'s header).
