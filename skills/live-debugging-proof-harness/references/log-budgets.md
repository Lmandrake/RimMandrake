# Log budgets on the full list

A log-budget row says "this session added no errors that name the mod". On the
owner's 550+ mod list, both of its instruments went blind on 2026-10-11 **while
reading as a clean PASS**: GSS Z, proof_hose Z and FlowWorks v2 E9. Every earlier
full-list budget PASS was partly blind, and no earlier result can be trusted as
evidence of a clean log.

## Blind way 1: Verse.Log's 10,000-message cap

`StopLoggingAtMessageCount` (decompiled 1.6 `Verse/Log.cs`, RimSage 2026-10-10) counts
every Unity message. At 10,000 it sets `Debug.unityLogger.logEnabled = false`. From
then on **Player.log and `jawa/drain_log` and the bridge journal all go silent while
the game runs fine**. You do not get suppressed errors, you get no record at all.
Only `Log.Clear` (which calls `Log.ResetMessageCount`) re-arms it. A chatty mod hits
the cap within one session: an MCR mood-chain logger did on 2026-10-03, and a
conversation mod did on 2026-10-11 ("Reached max messages limit" in Player.log).

- **Run start:** `validation_core.log_revive(B)` = `jawa/static_call Verse.Log Clear`
  plus a sentinel `Log.Warning` read back. `runner.py` does it per chain;
  `belt_watchdog` names the condition.
- **At the budget row:** `validation_core.log_alive(B, tag)`. A sentinel that does not
  come back means logging is dead, and the row is UNMEASURED.
- Proven live: a `Log.Warning` via `jawa/static_call` did not reach the journal, and
  after `Verse.Log.Clear` the next one did.

## Blind way 2: the bridge journal is a 1,000-entry ring

RimBridge keeps the last 1,000 journal entries **of every level**. On the full list an
intimacy mod writes ~0.3 info lines per tick (MEASURED: 176 per 600 ticks, "X cannot
currently do lovin'"). A warning is evicted ~3,400 ticks after it is written. So a
budget that reads `list_logs` once at the end of a 10-minute proof sees only its last
blocks. On 2026-10-11, v2's E9 saw "0 warn+ lines since base" though E7b's warning had
fired, and the `[RimBridge]` start line had scrolled out too.

- **`validation_core.LogTap`** (`tap_start(B)`; bridges call `tap_after(tool)`) is
  polled after every call in `TAP_TOOLS`: `step_game_ticks`, `load_game`, `save_game`,
  `get_ui_state`, `map_info`, `start_debug_game_ready`, `go_to_main_menu`, `order_pawn`.
  It is also polled at block ends. It keeps every warn+ entry and counts `lost`, the
  entries that scrolled out between two polls.
- ⚠️ **A repeated entry is ONE journal row** carrying the sequence of its **latest**
  occurrence and `RepeatCount N`. It covers `seq-N+1..seq`, and the tap's gap
  arithmetic depends on that.
- **`lost > 0` → UNMEASURED.** A full-list save load writes ~1,000 lines. The tap keeps
  them only if it is polled every couple of seconds during the load.

## Charging an error to the mod: the control

A 550-mod list has its own steady noise. Never charge "any error that names the mod"
or "any error after the test". The method (GSS `proof_all.p2c_control_noise`):

1. **Before any scene exists**: one save/load plus ~600 ticks. Every error message
   (digits normalised) in that window is the control set.
2. **Identity = message AND throwing frame.** If a control holds a generic
   `NullReferenceException`, that must not hide an NRE the mod throws.
3. **Exclude only errors in the control set that do not name the mod.** An error the
   session adds beyond the control is still charged, because it may be a clash.
4. **Open the control before the FIRST tick.** Vanilla `Faction.FactionTick` logs
   `Faction leader for <faction> is null.` via `Log.ErrorOnce`, once per session, on
   the first tick of a fresh quicktest world that holds leaderless campaign factions.
   A control opened after that tick never sees it.
5. **Some list noise fires on its own clock** and can miss the control. RimFridge's
   LoadedGame NRE was in one run's control and not the next. An error whose own first
   stack frame names another mod as its source is excluded as foreign
   (`_foreign_source`), and the count of foreign errors is reported.

Known per-load noise on the full list (MEASURED 2026-10-11): ReGrowthCore
`Map_FinalizeInit_Patch.RecolorMineables` and `RimFridge.RimFridgeComponent.StartedOrLoadedGame`
NRE on every map init or load.

## `[Ref XXXXXXXX] Duplicate stacktrace` has no frames

BetterStackTraces prints the full trace once, tagged `[Ref XXXXXXXX]`. After that it
writes only `[Ref XXXXXXXX] Duplicate stacktrace`, so the bridge journal entry for a
repeated exception has no frames. To name the throwing mod, resolve the ref against
the original `[Ref XXXXXXXX]` block in Player.log. The general triage of Player.log
is in `skills/rimworld-modding/references/player-log-triage.md`.

## What a budget row reports

`otherErrors`, `controlNoiseExcluded`, `controlNoiseThrowers`, the foreign count, the
tap's `polls` and `lost`, and the sentinel's text and `alive`. A reader must be able to
see **why** it is PASS. "0 errors naming the mod" with `lost` unreported is not
evidence.
