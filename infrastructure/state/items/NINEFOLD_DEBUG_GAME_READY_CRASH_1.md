# NINEFOLD_DEBUG_GAME_READY_CRASH_1 — start_debug_game_ready crashes the full-stack game, not a memory issue

`rimworld/start_debug_game_ready` reliably kills the RimWorld process on the
owner's full 596-mod list, mid quicktest-map setup, during the debug tool's
instant-research-completion sweep. Reproduced twice:

- **BENCH, 2026-09-05, host RAM 9.4 GB free** — assumed at the time to be
  memory pressure (a plausible read, given the same-day ComfyUI/rembg OOM
  kills elsewhere).
- **FOUNDRY, 2026-09-05, host RAM 33 GB free** — same crash, same exact
  spot in the log, with ample headroom. **This rules out host memory as the
  cause.**

## What the log shows, both times

`Player.log` ends abruptly inside a burst of `[Ninefold] <God> satiation
+N.0 (research completed: <ResearchDef>) -> ...` lines — the debug
quicktest path grants/completes research instantly, and Ninefold's
satiation hook fires once per completed `ResearchProjectDef` including
"shared input" cascades. No managed exception is logged, no Unity crash
dump is written (checked both times), the process is simply gone from
`tasklist.exe` afterward. The bridge connection drops with a raw socket
reset (`ConnectionResetError: [WinError 10054]`), consistent with the
process dying outright rather than a graceful shutdown.

## What's ruled out

- **Host memory pressure** — ruled out by the 33 GB-free reproduction.
- Not yet checked: whether this happens on `start_debug_game_ready` at all
  without Ninefold active (a control run on the minimal 21-mod list, which
  has no Ninefold and did NOT crash this session, is suggestive but not a
  clean isolation — the minimal list also has ~575 fewer research defs
  total, so either "no Ninefold" or "far fewer research defs to instant-
  complete" could explain the difference).

## Leading hypothesis, unconfirmed

Ninefold's research-completion hook (`GameComponent_Ninefold`'s satiation
handler, wired per `NINEFOLD_MISSING_EVENT_HOOKS_1`/
`NINEFOLD_RUNTIME_PROOF_BLOCKED_1`) may not be designed to handle receiving
every research completion in the ENTIRE tree fired in one instant burst
(the debug tool's behavior) rather than one-at-a-time as a real playthrough
would trigger them — a tight loop, a growing collection with no cap, or
repeated expensive work per event (a save, a UI redraw, a def-database
re-scan) could plausibly take an unbounded amount of time or stack depth
under that burst and crash without ever getting to log an exception.
**Not verified this pass** — this is a hypothesis for whoever picks this up
next, not a finding.

## Practical impact

Blocks any bridge-automated `start_debug_game_ready` quicktest on the
owner's full modlist while Ninefold is active. The **minimal-list + theme
mods** restart path (`modlist_swap.py --minimal --apply` plus manually
adding the 1-2 mods actually under test) is a reliable workaround for
UI/theme verification work that doesn't need Ninefold or the full research
tree — used successfully this session for `UI_SHELL_SLICE_BUILD_1`'s gizmo-
row check.

## criteria
- [ ] Root cause identified (Ninefold's research hook vs. something else
      entirely) — not attempted beyond the hypothesis above.
- [ ] A control run: full 596-mod list, Ninefold's DLL temporarily removed
      or its research hook disabled, confirm whether the crash still
      happens — would cleanly separate "Ninefold" from "any full-tree
      instant-research burst."
- [x] Host memory pressure ruled out as the cause (two data points, 9.4GB
      and 33GB free, same crash both times).
