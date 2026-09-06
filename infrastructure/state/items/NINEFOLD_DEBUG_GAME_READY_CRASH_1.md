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
- [x] **Reproduced deliberately with a memory watcher running in parallel
  (`tasklist.exe` RSS sampled every 3s).** Confirmed OOM, not a silent code
  fault: RSS climbed to and held around **18.2 GB**, a second
  near-empty `RimWorldWin64.exe` PID briefly appeared (crash-handler or
  relaunch attempt, not confirmed which), then the original PID's RSS
  cratered to 14.6 GB and the process vanished entirely one sample later.
  This reverses the inherited belief from an earlier session that OOM had
  been "ruled out" — that ruling was never re-derived this pass and this
  measurement contradicts it directly.
- [x] `readiness: "gameData"` (a lower bar) returns cleanly in ~2.8s with
  `mapCount: 0`, `mapDataReady: false` — the process has NOT generated a
  map yet at that point and is fine. The crash is specifically bound to
  whatever happens between `gameData` ready and `mapData` ready: RimWorld's
  own debug "quick test" scenario setup, which includes the bulk
  auto-research-everything action, runs in that window.
- [ ] Still open: is the ~18GB ceiling caused specifically by the
  bulk-research debug shortcut, or would ANY map generation on the full
  596-mod list hit it? This is the load-bearing open question — if it's
  the latter, this is not a debug-tool quirk, it threatens the real
  campaign's own map generation too. Not tested this pass (would mean
  generating a map some other way and watching memory the same way).
- [ ] Check whether this reproduces on the MINIMAL 21-mod list too — if
  minimal-only avoids it, narrows toward mod-interaction/volume rather
  than a single-mod defect, though 18GB on 596 mods vs however much on 21
  is not a fair apples-to-apples test of "is bulk-research the trigger."
- [ ] Windows Event Viewer (Application/System logs) for an actual
  OS-level fault report at the death timestamp, to distinguish "OS OOM
  killer" from "Unity's own out-of-memory handler tore itself down" —
  both are OOM, but the fix differs (system RAM/pagefile vs. a Unity
  heap-limit setting).

**Escalation, same investigation session**: a background shell task doing
nothing but polling `Player.log` and `tasklist.exe` every 2s was itself
killed by the harness with the reason "the system is running low on
memory" — at a moment coinciding with a fresh RimWorld reload in progress.
This means the memory pressure from a heavy RimWorld load is severe enough
to threaten OTHER processes sharing the host (WSL's own memory manager
shares physical RAM with the Windows side under WSL2), not just
`RimWorldWin64.exe` itself. `free -h` immediately after showed 32Gi free
of 35Gi — the pressure was transient and resolved once the previous
RimWorld process was gone. Recorded as a reason to not hammer repeated
full-modlist reloads back-to-back without letting memory settle between
attempts.

**Workaround for anyone needing a live map on the full list right now**:
do not call `start_debug_game_ready` past `readiness: "gameData"`. Load
the real campaign save instead of using the debug quicktest generator —
it never runs the bulk-research shortcut, and (as a bonus) is the actual
Ash'karr world rather than whatever random tile the quicktest scenario
picks.

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
