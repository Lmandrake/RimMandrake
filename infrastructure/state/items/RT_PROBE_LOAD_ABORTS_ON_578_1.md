## spec
🔴 **`rt_probe.rws` DOES NOT FINISH LOADING on the 578-mod set.** Read out of the
live stack, in order:
  `CrossRefHandler.ResolveAllCrossReferences()`
  → POSTFIX `com.rimworld.mod.factioncontrol` →
    `FactionControl.CrossRefHandler_ResolveAllCrossReferences.Postfix()`
  → `List.Enumerator.MoveNextRare()` — the shape of a collection modified
    while it is being enumerated
  → `GameAndMapInitExceptionHandlers.ErrorWhileLoadingGame`
  → `GenScene.GoToMainMenu` → `Game.Dispose` → `Map.Dispose`
  → `MapDrawer.Dispose` → **NullReferenceException**
⇒ the load aborts, the engine tries to bail to the main menu, and **the bail
itself throws**, leaving a half-disposed game that still reports
`status: game_loaded` and still answers the bridge.
📌 That zombie state is why `Outputs` (233) and `Settings` (184) enumerate fine
while `Actions` throws, and why `Vehicle-Framework`'s ColonistBar patch then
spams `KeyNotFoundException: key '0'` every OnGUI.
⚠️ It loaded FINE last night on 577. The set changed by exactly one mod
(`mandrake.inhabited`) — but do not conclude Inhabited is the culprit from that
alone. FactionControl is the thing that actually threw, and the save also carries
~250 scratch pawns and `Could not find think node with key ...` on dozens of them.

## verify
next load, do NOT load `rt_probe`. Load `WORLDMAP_gen_sub7b` (the MLP-7 geometry
the CSVs are named for) and grep the log for `ErrorWhileLoadingGame` BEFORE
trusting anything. If it aborts too, the fault is the mod set, not the save.

## criteria
a load with ZERO `ErrorWhileLoadingGame`, and `list_debug_action_children("Actions")`
returning its 642 children. 🔴 That second check is the cheap canary for this whole
class of failure and costs one call — run it FIRST on every future load.

## notes
**from:** CHECK, 2026-08-20, live. Found only because `list_debug_action_children("Actions")`
threw — everything else about the session looked healthy.

**consequence:** 🔑 **Everything today ran on a corpse.** The tool results remain real evidence that
the TOOLS work — 21,872 tiles at 100%, 72 settlements created, 23 regions assigned,
817 mutators cleared — but the GAME STATE is not trustworthy and must not be saved.
The owner independently ruled "scratch, don't save" before this was known, which
turns out to be the right call for a second reason.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

🔵 IN PROGRESS — WIDER THAN FILED, and the exception is now named exactly.

**correction:** The title says `rt_probe`. **BOTH saves abort.** `WORLDMAP_gen_sub7b` aborts the
same way, so this is NOT a property of one save.
🔴 THE EXCEPTION, in full, from the second load:
  `System.InvalidOperationException: Collection was modified; enumeration
   operation may not execute.`
  at `FactionControl.CrossRefHandler_ResolveAllCrossReferences.Postfix()`
  ⇒ `thereallemon.factioncontrol` enumerates a list and mutates it mid-enumeration
  during `CrossRefHandler.ResolveAllCrossReferences`, which aborts `FinalizeLoading`.
⚠️ **AND MY OFFLINE PRE-FLIGHT WAS WRONG.** I read `WORLDMAP_gen_sub7b` as having
0 pawns and 0 settlements by regexing the raw `.rws`; the live world reports 38
settlements and 27 features. The regex looked for a serialised class name that is
not how those are written. A save's contents are not safely read by grep —
`savemap.py` exists for that reason.
⚠️ **AND THE FIRST CANARY WAS WRONG IN BOTH DIRECTIONS.** `list_debug_action_children
("Actions")` reports few or no VISIBLE children with no map loaded, and it
enumerated fine (13 children) on a game that had definitely aborted. It is
replaced by grepping Player.log for `ErrorWhileLoadingGame`, which the engine
writes only when it has given up. `w9_run.py` now blocks on that.

**ab:** 🧪 RAN 2026-08-20 AND WAS REFUSED BEFORE IT COULD START — which is itself the
answer to a different question. With `mandrake.inhabited` disabled,
`rimworld/load_game` REFUSED outright:
  *"Save 'WORLDMAP_gen_sub7b' cannot be loaded because 1 mod(s) recorded by the
    save are not currently active: Inhabited (local) (mandrake.inhabited)."*
⇒ 🔑 **A/B BY MOD REMOVAL IS NOT AVAILABLE ON A SAVE THAT RECORDS THE MOD.** The
bridge has an `ignoreModCompatibility` escape hatch, but forcing a load with a
recorded mod missing generates its own missing-def errors and CONFOUNDS the very
attribution the A/B exists to make. Refused on those grounds, not attempted.
⇒ 📌 And it means both candidate saves were written THIS MORNING with Inhabited
active — `rt_probe.rws` has an mtime of 07:42, not last night. Neither is the
clean pre-Inhabited artifact I took them for.
⇒ To attribute this properly the A/B has to run the other way: a save made
WITHOUT Inhabited, loaded on a stack without it. None exists yet.

**severity:** ⚠️ **The abort is real but its BLAST RADIUS is narrow, and that matters.** It
throws in a Harmony POSTFIX on `ResolveAllCrossReferences` — the engine's own
cross-reference resolution has already completed by then. Consistent with
observation: the world layer read back perfectly all morning (21,872 tiles, 38
settlements, 27 features, 100% tile validate). What did NOT complete is whatever
FactionControl intended to do to the faction roster.
⇒ world authoring can proceed on such a game, but every result from it is
PROVISIONAL and must be re-proven by a save→reload.

**old_ab:** 🧪 RUNNING 2026-08-20: `mandrake.inhabited` DISABLED (577 active, md5
6fef68dcbb43f132243a0569bb5de2f5; the 578 file is archived as
`*.ab-test-inhabited-on.xml`) and the game relaunched. Loading
`WORLDMAP_gen_sub7b` again decides it:
  abort GONE    ⇒ Inhabited trips a latent FactionControl bug. Inhabited is the
                  variable; FactionControl is the fault.
  abort REMAINS ⇒ Inhabited is exonerated and FactionControl breaks on these saves
                  regardless — which makes it a shipping-stack problem, not a
                  new-mod problem, and much more serious.
🔑 Either answer is worth the load. **Restore `mandrake.inhabited` afterwards
either way — the owner enabled it deliberately this morning.**
