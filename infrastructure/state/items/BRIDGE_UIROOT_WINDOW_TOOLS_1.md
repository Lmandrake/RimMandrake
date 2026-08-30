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

## Live-verified 2026-08-30, FOUNDRY — PASS, both tools

Full 585-mod list, bridge live (426 tools, 301 `jawa/`), fresh
`start_debug_game_ready` quicktest map, `ticksGame: 1`.

**`jawa/window_list_close`** — four behaviours, each read back raw, not by
`success`:

1. `action=list` → `count: 4`, and the rows are REAL windows the game actually
   had open, including a genuine stuck-modal candidate:
   `Verse.ImmediateWindow` · `DubsMintMinimap.MainTabWindow_MiniMap` ·
   `LudeonTK.Dialog_DevPalette` (isDebug true) · `LudeonTK.EditWindow_Log`
   (optionalTitle **"Debug log"**, layer Dialog, isDebug true). A screenshot
   taken the same second shows exactly those two dev dialogs on screen — the
   list is not a guess about what MIGHT be open.
2. **Ambiguity refusal works and is genuinely non-destructive.**
   `close typeName="Window"` → `success: false`, *"'Window' matches 3 open
   windows. Pass closeAll=true, or use 'index' for one specific window."*,
   `details.matchedTypes` naming all three. A re-`list` immediately after
   returned the SAME 4 windows — it refused without closing anything.
3. `close typeName="EditWindow_Log"` → `closedCount: 1`,
   `closed: [{type: LudeonTK.EditWindow_Log, optionalTitle: "Debug log"}]`,
   `stillOpenCount: 3`; independent re-`list` → 3 windows, log window **gone**.
4. `close index=2` (the dev palette) → `closedCount: 1`, `closed:
   [LudeonTK.Dialog_DevPalette]`; re-`list` → 2 windows.
   Final screenshot `UIROOT_C_closed_1788115594.png` shows a clean map with
   **neither dialog drawn** — the visual confirms the read-back.

⇒ This is the direct fix for `stale-modal-blocks-every-later-call` proven end to
end: the bridge can now SEE an open modal and clear it.

**`jawa/screenshot_mode`** — read → write → read → look:
`{}` → `activeBefore/activeAfter: false`; `{enabled: true}` →
`activeBefore: false, activeAfter: true`; independent re-read → `true`;
`{enabled: false}` → `activeBefore: true, activeAfter: false`.

Proven by TRANSITION, not one frame — two shots seconds apart, same camera:
- `UIROOT_A_dialogs_on_1788115568.png` (mode OFF): full UI — bottom architect/tab
  bar, right-hand clock/date/FPS column, top colonist bar, pawn name labels, the
  Dev palette window.
- `UIROOT_B_mode_on_1788115569.png` (mode ON): **all of that gone**; only the map,
  the minimap and the Debug log remain. `Dialog_DevPalette` stopped drawing
  entirely, which is the documented `drawInScreenshotMode=false` behaviour.

Both PNGs in
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots`.

## criteria
- [x] Owner ruling: high priority, build now.
- [x] Both signatures read from 1.6 source, not guessed.
- [x] Builds clean, no duplicate alias (full surface re-scanned).
- [x] Deployed and proven live, including against a real stuck/open dialog —
      the game's own Debug log window was listed, then closed, and the close
      confirmed by an independent re-list AND by a screenshot. Ambiguous-match
      refusal proven non-destructive.

--- history ---
