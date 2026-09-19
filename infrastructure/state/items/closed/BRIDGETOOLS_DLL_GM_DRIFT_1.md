# BRIDGETOOLS_DLL_GM_DRIFT_1

JawaBench companion DLL was reported 41 tools behind source because a prior build
was made without the `--gm` flag, which compiles out the whole `#if
JAWA_GM_TOOLS` region (39 tools gated there, plus the 2 always-named GM pair
`jawa/fire_incident`/`jawa/send_letter` — 41 total), not just those two.

## What this pass did (rebuild only, no deploy — game is UP)

- Ran `python.exe src/RimMandrake/bridgetools/build.py --gm` (plan-only, no
  `--apply`). Build succeeded from HEAD `58abbd445bb3...`, GM pair verified
  present in the built DLL.
- Compared the rebuilt artifact
  (`src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/JawaBench.BridgeTools.dll`)
  against source with `selftest_tool_metadata.py`:
  **PASS** — `DLL tool surface == source declarations, 317 tools (GM pair included)`.
- Also diffed the rebuilt (--gm) artifact against the currently DEPLOYED game
  copy (`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`)
  by tool name set: **identical, 317/317, 0 added, 0 removed.** The deployed
  copy's build stamp is commit `5ed3e2a13cce...` (2026-09-09 07:13 local) —
  it turns out someone already rebuilt-with-`--gm` and deployed earlier today,
  before this item was claimed, so the GM-tool gap was already closed on the
  live game copy. It is just 3 commits stale relative to current HEAD
  (`58abbd445bb3`), which is routine per-commit stamp drift, not a tool-count
  regression (verified: same 317-name set either side).
- Ran a bare `build.py` (no `--gm`) as a control, purely to confirm the
  failure mode names itself: it reported `LOSES` on exactly the 39
  GM-gated tools plus would drop `jawa/send_letter` from the deploy target
  (`fire_incident`/`send_letter` are the named pair; the other 37 are the
  rest of the `#if JAWA_GM_TOOLS` region) — refused to deploy without
  `--allow-tool-removal`, as designed. This build was NOT the one left in
  the local artifact folder — the final local artifact is the `--gm` build,
  re-run after this control to leave the correct one in place.

## Owed — next game-down window

1. `taskkill.exe /F /IM RimWorldWin64.exe`
2. `python.exe src/RimMandrake/bridgetools/build.py --gm --apply` (deploys
   the already-verified 317-tool DLL to the game's `BridgeTools/JawaBench/`
   folder)
3. Restart RimWorld (companions are discovered only at RimBridgeServer
   startup) — `launch_and_wait.sh`
4. Re-run `python3 src/RimMandrake/bridgetools/selftest_tool_metadata.py`
   against the fresh local build to reconfirm, and spot-check one of the
   39 previously-gated tools live (e.g. `jawa/fire_raid` with `dryRun=true`)
   per `rimbridge-companion`'s proof standard — `success: true` alone is not
   evidence.

Not closed: deploy + restart still required. Left `doing`.
