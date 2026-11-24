# How to wire the three bridge tools into a visit (a note; nothing is wired yet)

Item `RIMMANDRAKE_BUILD_BRIDGE_RECEIPT_CALM_AND_TAP_EITHER_WAY`. Another run edited the Stage 6 exit reader on
2026-11-23, so this note leaves the visit code alone.

1. **Before the first row, and after each restart or load of a game**: `build_match.py loaded --mod M --game <name>` (WSL) or
   `loaded_build.loaded(root, M, reply)` with the reply of `jawa/running_mods` (`details=false, assembly="",
   loadedOf="ours"`). Exit 1 (WRONG_BUILD, WRONG_LIST, WRONG_GAME, NOT_LOADED): deploy and restart; run no row. Exit 2: look
   again. Exit 4 (no DLL): go on, and say that the loaded code was not identified.
2. **In each row**: merge `loaded_verdict`, `listFingerprint`, `gameKey` and `pid` beside build_match.identity's fields.
   `identity` proves the folder. The receipt proves the process. A row whose `pid` differs from the checked one was not
   checked.
3. **Calm**: `jawa/quiet_site action=calm keepIds=<cast> [allowIncidents=<def>] [except=<control>]` at the start of a map
   (`clear=true` on a test map only); `action=reassert` before each block and after each load; `action=read` at the end of
   the deciding window, never `reassert` inside it. `calm=false` before a block: an APPARATUS FAULT that names `notCalm`.
   A breach row inside the window: the record that an ENVIRONMENT FAULT needs. `action=release` before any save.
4. **Tap**: `jawa/first_exception action=arm label=<row>` at the start of a row, `action=read` at its end. `SEEN`: put
   `window.firstException` in the row's record. `NONE_SEEN_PARTIAL` or `NOT_ARMED`: never "no exception".
5. `modcheck/quiet_site.py` (`QuietSite.apply`) can call `action=calm` in place of its eight calls. Its drain, its modal
   broker and its support guard stay.
