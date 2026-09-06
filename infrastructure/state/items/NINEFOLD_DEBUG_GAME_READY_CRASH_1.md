## spec
Reproduced live, 2026-09-06, while working `BIOME_SPAWN_FLORA_AUDIT_1` on
the full 596-mod list: `rimworld/start_debug_game_ready` (readiness
`mapData`, `pauseIfNeeded: true`, `timeoutMs: 280000`) never returned — the
bridge client's own socket eventually raised `ConnectionResetError: An
existing connection was forcibly closed by the remote host`. `tasklist.exe`
confirmed `RimWorldWin64.exe` was gone entirely; `./game` re-measured and
corrected the ledger DOWN.

**What the log shows, and doesn't.** The tail of `Player.log` at the moment
of death shows the quicktest's own bulk "research everything" debug action
completing dozens of research projects in a tight burst, each one firing
`[Ninefold] <god> satiation ... -> ...` lines (`Patch_ResearchCompleted.cs`
postfixing `ResearchManager.FinishProject`) — no managed exception, no
Unity/Mono crash stack, no native crash-dump banner anywhere in the log.
That absence is itself informative: a real unhandled exception or access
violation normally prints one. Its absence is more consistent with an
external kill (Windows OOM, a watchdog) than a code fault inside the game
process — **not confirmed**, just the shape of the evidence.

**Read the Ninefold hook before blaming it, per doctrine.** Checked
`Patch_ResearchCompleted.cs` and `GameComponent_Ninefold.ApplyDelta`
directly: the postfix has a correct re-entrancy guard (`__state` from the
prefix, since `FinishProject` recurses into prerequisites), and `ApplyDelta`
itself is a single `Mathf.Clamp` plus one conditional `Log.Message` gated on
`Prefs.DevMode`. No allocation loop, no O(n²) shape, no save/UI call. It is
a plausible LOG-VOLUME contributor (hundreds of research completions ×
2 log lines each, across a debug quicktest that dev-mode-completes a large
modded techtree) but nothing in it reads as a crash cause on its own — this
item's name should not be read as an accusation against that file; it is
just the last visible activity before the process died, and needs whatever
else fires per-research-completion (every other mod's own hooks, if any)
checked before pointing at Ninefold specifically.

**Reproduction is exactly the standard rimbridge-companion quicktest
opener** (`readiness="mapData"`, `pauseIfNeeded=True`) — the documented
"about one minute" pattern every `prove_*.py` script uses. If this is
reliably reproducible on the full modlist, it blocks EVERY live-proof
pass that needs a quicktest map on the full list, not just this one.

## verify
- [ ] Reproduce at least once more, deliberately, watching Windows memory
  (`tasklist.exe` RSS) in the seconds immediately before death — confirm or
  rule out OOM as the mechanism (was ruled out once before per an earlier
  session's note; this pass did not re-derive that, it's inherited belief,
  flag it as unconfirmed here too).
- [ ] Try `readiness: "gameData"` or `"currentMap"` (lower bars than
  `mapData`) to see whether the crash happens during RimWorld's OWN
  quicktest-scenario setup (before any readiness the tool checks) or during
  something the tool itself does after that setup — narrows where in the
  sequence it dies.
- [ ] Check whether this reproduces on the MINIMAL 21-mod list too, or only
  the full 596 — if minimal-only avoids it, this is almost certainly a
  mod-interaction/volume problem, not a single-mod defect.
- [ ] If reproducible, check Windows Event Viewer (Application/System logs)
  for an actual OS-level fault report for `RimWorldWin64.exe` at the death
  timestamp — the one artifact that would distinguish "killed" from
  "crashed silently."

## criteria
A quicktest map (`mapData` or better) reachable on the full 596-mod list
without the process disappearing, OR a confirmed, named root cause if it
turns out to be structurally unavoidable at this mod count (in which case
the fix is elsewhere — e.g. skip the debug scenario's bulk-research step
entirely and settle a normal way instead).

## Watch out
🔶 Every `prove_*.py` script and the `rimbridge-companion` skill's own
canonical quicktest opener assumes this call just works. Until this closes,
any live-proof pass on the full modlist should expect it to fail and budget
a relaunch (~500s to bridge-up per two measurements this session, full
mapData readiness likely longer) — or fall back to a manually-driven
world-tile-set + travel/settle flow that never invokes RimWorld's own
bulk-research debug action.
