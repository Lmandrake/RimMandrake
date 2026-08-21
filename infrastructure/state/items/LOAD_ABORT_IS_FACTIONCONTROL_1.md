## 🔴 RULED — OWNER, 2026-08-21 08:39: FACTION CONTROL IS REMOVED FROM V1

> *"I was wrong. We should remove the Faction Control mod."*

Reversing his own 08:19 call to put it back and hunt the conflict. **The mod is out.** There
is no investigation to do and no conflicting-mod hunt to schedule; anything below that reads
as pending work on restoring it is superseded by this line.

**What was done to make it stick, not just true today:**

- `thereallemon.factioncontrol` is absent from the live `ModsConfig.xml` — 578 active.
- 🔴 **`ModsConfig.FULL.LATEST.xml` regenerated from the live config.** That file is what
  `modlist_swap.py --restore` restores FROM, and it still carried the entry — a single
  `--restore` would have put the load blocker straight back with nothing to warn anyone.
  The pre-removal list is kept as `ModsConfig.FULL.20260821_WITH_factioncontrol.xml`.
- ⚠️ **The cost, stated plainly:** we lose the faction-count spinners on the world-creation
  page. `JawaFactionSlate`'s generated patch already zeroes 48 FactionDefs, so that page
  matters less than it did — but `FACTION_SLATE_ZEROES_KEEPS_1` is now the ONLY lever over
  which factions generate, which raises its priority.
- ⚠️ Every save written while it was active still records it and needs
  `ignoreModCompatibility: true` once. Saves written since do not.

---

## spec
🔴 **THE LOAD BLOCKER IS THE MOD SET, NOT THE SAVES. Settled 2026-08-21, third save, third
abort.** `LOADS_ARE_BLOCKED_NEEDS_YOU_1` has been open since 2026-08-20 with two suspects:
either the two saves that failed were damaged, or something in the 578-mod stack kills every
load. It is the stack.

`WORLDMAP_gen` — written **by this mod set, tonight, with `<maps />` empty** — aborts with
the identical signature:

    Exception in FinalizeLoading(): System.InvalidOperationException:
        Collection was modified; enumeration operation may not execute.
      at System.Collections.Generic.List`1+Enumerator[T].MoveNextRare ()
      at FactionControl.CrossRefHandler_ResolveAllCrossReferences.Postfix ()
      at Verse.CrossRefHandler.ResolveAllCrossReferences ()
      at Verse.ScribeLoader.FinalizeLoading ()
    - POSTFIX com.rimworld.mod.factioncontrol

Read back afterwards: `status: no_game`, `programState: Entry`, `hasCurrentGame: false`.
The game bailed to the main menu. Three saves — `rt_probe`, `WORLDMAP_gen_sub7b`,
`WORLDMAP_gen` — three aborts, one stack frame.

### 🔴 AND THE CANARY MISSED IT

`ErrorWhileLoadingGame` read **0** on this abort. Every tool that gates on that string —
`w9_run.py`'s `canary()` above all — would have called this load healthy and proceeded onto
a dead game.

The reason is structural: `GameAndMapInitExceptionHandlers.ErrorWhileLoadingGame` fires on
**map** init. This save has no map, so the exception happened in `FinalizeLoading` and no
map-init handler existed to write the string. ⇒ **`ErrorWhileLoadingGame` detects a failed
load only when a MAP was involved.** The reliable signal is
`Exception in FinalizeLoading`, plus reading `programState` back.

## verify
The experiment, run 2026-08-21 04:00: `thereallemon.factioncontrol` removed from
`ModsConfig.xml` (579 → 578 active; the untouched list is snapshotted at
`infrastructure/state/modlists/ModsConfig.BEFORE_FACTIONCONTROL_TEST.xml`), then relaunch
and load `WORLDMAP_gen` again.

- loads clean ⇒ **FactionControl is the cause**, and v1's load blocker is one mod entry
- aborts again ⇒ FactionControl is only where it surfaces; the collection is being modified
  by something else during cross-ref resolution, and the next suspects are the other mods
  patching that method

Either way, read `Exception in FinalizeLoading`, `ErrorWhileLoadingGame`, and
`programState` — not just the first.

## criteria
- the cause is named with the log line that proves it
- 🔴 **`w9_run.py`'s canary is fixed to catch a no-map abort** before it is trusted again —
  it currently reports a bailed load as healthy
- and the owner's mod list is either restored, or the removal is written up as a v1 decision
  with what it costs (FactionControl is what lets a faction spinner go below a required
  count at world creation)

## notes
Filed by CHECK 2026-08-21 during the AFK run. ⚠️ The mod list is MODIFIED right now, one
entry down, for this experiment. The snapshot above is the owner's list as it stood; restore
from it if the experiment does not justify the removal.
