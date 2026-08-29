# BRIDGE_UIROOT_WINDOW_TOOLS_1 — jawa/window_list_close + jawa/screenshot_mode

Filed 2026-08-29, FOUNDRY. Owner asked to "look more deeply" at the roster's vague
`Find.UIRoot` row before writing it off; both tools below came out of actually reading
`Verse/WindowStack.cs`, `Verse/Window.cs`, `Verse/UIRoot.cs` — real, well-anchored
capabilities, not a HARD/no-mechanism dead end after all. Owner: "Those are high
priority, do now."

## Spec

New file `JawaBenchUIRootTools.cs` (2 tools, ungated):
- `jawa/window_list_close` — `Find.WindowStack.Windows` to list every open dialog
  (type, optionalTitle, layer, ID, isDebug, forcePause); `Window.Close(doCloseSound)`
  to close one, addressed by `index` (precise) or `typeName` substring (refuses on an
  ambiguous multi-match unless `closeAll=true`). **This is the direct fix for a
  failure this project has already hit**: [[stale-modal-blocks-every-later-call]] — a
  stuck window silently blocked five runs' worth of calls before anyone thought to
  check for one. Nothing on the bridge could see or clear an open dialog before this.
- `jawa/screenshot_mode` — `Find.UIRoot.screenshotMode.Active`, the same flag the
  player's own screenshot-mode hotkey toggles. Pairs with this session's earlier
  `jawa/take_screenshot`: without it, a screenshot captures whatever cursor/dialog
  happened to be on screen.

## Verify
Builds clean, 0 errors 0 warnings. 281 unique `jawa/…` names, no duplicate alias
(full-surface re-scan). **Not deployed** — game up, BENCH holds bridge. Once deployed:
`window_list_close action=list` against a real open dialog (e.g. open the debug
window), confirm the read-back matches; `screenshot_mode enabled=true` then
`take_screenshot`, confirm the saved PNG has no cursor/dialog in it.

## criteria
- [x] Owner ruling: high priority, build now.
- [x] Both signatures read from 1.6 source, not guessed.
- [x] Builds clean, no duplicate alias (full surface re-scanned).
- [ ] Deployed and proven live, including against a real stuck/open dialog. Needs the
      game down, then bridge.

--- history ---
