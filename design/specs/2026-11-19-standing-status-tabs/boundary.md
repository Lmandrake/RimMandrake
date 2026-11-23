# BOUNDARY: the standing status tabs (`./pages` and the self-reload of MATURATION_NOW), Design Version 0.1.0

Code: `src/RimMandrake/Utils/pages_open.py` (run by `./pages` at the repo root), `src/RimMandrake/Utils/fleet_now.py` (run by `rm-fleet-now.timer`), and in `src/RimMandrake/Utils/maturation_now.py` the reload and build-time lines of the HTML page (`build`).
Item: `RIMMANDRAKE_BUILD_PAGES_OPENER_ONE_EDGE_WINDOW_THREE_TABS`. Design: `proposal.md` beside this page, option A. Why it
exists: the owner, 2026-11-19 about 7:02 PM PST: *"Please move MATURATION_NOW and FLEET_NOW into tabs alongside
CODEBASE_NOW"*. Written 2026-11-19. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_standing_tabs.py`. This page covers only the two parts named above, not the rest of
`maturation_now.py`.

## ACCEPTS (the only inputs the opener is built for)

- **a-conductor-folder-by-rmpaths.** The folder is `rmpaths.rm_path("conductor")` (env `RM_DATA_ROOT`), read each run.
- **a-windows-desktop-with-chrome.** `cmd.exe` reaches Windows from WSL2 and Chrome is registered as `chrome` (never Edge: owner, 2026-11-19 7:14 PM PST, *"OMG you used Edge?! never. Chrome please."*).

## DOES NOT SURVIVE (not promised; where the opener notices, it says so)

- **a-typora-theme-changed-after-a-build.** The theme is read each run; a tab shows the new look on its next reload.
- **a-markdown-feature-the-renderer-lacks.** The page uses `markdown_it` (CommonMark plus tables). A Typora-only extension
  (math, footnotes) would show raw. The source holds none (measured 2026-11-19: one fence, no headings).

- **no-chrome-or-no-desktop.** The launch command fails; the opener prints the failure and exits 3. It cannot tell a
  window that opened and closed at once from one that never opened.
- **a-tab-the-owner-closed.** A closed tab stays closed until the next `./pages`. A second `./pages` opens a second window.
- **a-stale-tab-in-a-dead-writer.** The tab reloads the file; if the writer died, the file is old. The page shows its
  build time so that this can be seen. It has no banner (CODEBASE_NOW has one).

## PROMISES (each one is owed a test of the same name)

- **three-tabs-in-order.** One command opens one window whose tabs are CODEBASE_NOW.html, FLEET_NOW.html, then
  MATURATION_NOW.html, each as a `file:///` URL (FLEET_NOW is `FLEET_NOW.html`, the page `fleet_now.py` makes from `running_now.py`'s `RELENTLESS_NOW.md`; `STATUS_BOARD.html` is the dead Relentless board and is not a tab: owner, 2026-11-19 7:09 PM PST, *"Not Relentless, FLEET_NOW"*) in the conductor folder. Tested by `t_three_tabs_in_order`.
- **missing-page-named-others-open.** A page that is not on disk is named in the output as MISSING, the other pages
  still open, and the exit code is 2. All present: exit 0. Tested by `t_missing_page_named_others_open`.
- **folder-from-rmpaths.** Changing `RM_DATA_ROOT` changes the folder in every URL; no drive path is written in
  `pages_open.py`. Tested by `t_folder_from_rmpaths`.
- **never-fullscreen-never-steal-focus.** The launch asks for a minimized start and carries none of the fullscreen,
  kiosk or app flags; `--show` is the only way to a normal start. Tested by `t_never_fullscreen_never_steal_focus`.
- **dry-run-opens-nothing.** `--dry-run` prints the command and one URL per line, and calls no launcher. Tested by
  `t_dry_run_opens_nothing`.
- **maturation-page-reloads-and-shows-build-time.** The MATURATION_NOW.html page carries a refresh line of 300
  seconds (the STATUS_BOARD cadence) and its build time in its first lines, visible. Tested by
  `t_maturation_page_reloads_and_shows_build_time`.

- **fleet-page-wraps-fresh-source.** When `RELENTLESS_NOW.md` is at most 600 seconds old, `FLEET_NOW.html` holds its
  body rendered as Typora renders it (inline HTML kept as is, a fenced block as fixed-width preformatted text, headings, lists and tables as such), a 60 second reload line and a visible build time; exit 0. Tested by `t_fleet_page_wraps_fresh_source`.
- **fleet-page-typora-look.** The page carries the CSS of the Typora theme the owner reads in (`blue-topaz-dark.css`
  with its `blue-topaz.css`, found from the Typora `profile.data` setting `darkTheme`; measured 2026-11-19: dark mode on,
  separate dark theme), inside `<div id="write">`, so background, text colour, font and width match his Typora
  window. His words, 7:14 PM PST: *"Use precisely the same thing you use for the .md version, ported to html"*. When the
  theme folder cannot be read the page uses the panel colours of the page itself (#14171c, #e8eaee) and says so in the
  build line. Tested by `t_fleet_page_typora_look`.
- **fleet-page-could-not-read.** When the source is missing or older than 600 seconds, the page says COULD NOT READ
  with the cause and shows no old body; exit 3. It never shows a stale body as current. Tested by
  `t_fleet_page_could_not_read`.
- **fleet-page-written-whole.** The page is written to a temp name and renamed, so a tab never reads half a page; no
  temp file is left. Tested by `t_fleet_page_written_whole`.

## LIMITS

- **300 seconds, the reload of the MATURATION_NOW tab.** Danger: a tab that reloads slower than its writer shows old
  data. The writer runs each dispatch tick (measured: the item's design table, 2026-11-19); STATUS_BOARD reloads at
  300 s (`status_board.RELOAD_S`), and the tab shows the build time, so a tab older than that is plain to see.

- **600 seconds, the oldest source `fleet_now.py` will wrap.** Danger: a dead `running_now.py` leaves a body that
  looks live. The source is written every minute (`rm-running.timer`), so 10 minutes is ten missed runs.
- **60 seconds, the FLEET_NOW reload**, the source's own cadence.

## LIFE CYCLES (a move not listed here is a defect)

- **a fleet run:** stat the source (missing or over 600 s: write the COULD NOT READ page, exit 3) → wrap the body → write
  temp, rename → exit 0.
- **a run:** read the folder → check each page file → build one command → (dry run: print and exit 0/2) → launch →
  print each URL and each MISSING → exit 0 (all opened), 2 (a page missing), 3 (launch failed).

## MATURATION_NOW.md, section "Every mod, one line" (`maturation_now.py`, `one_line_md`)

- **Promise: no table, no cut text.** The section is one bullet per advancing mod (mod, version, stage, last movement; then
  its "Waits on" line and its "Needs you" line), and held, off or paused mods are one short list. Typora sizes table
  columns by the longest cell, so a table made narrow, tall rows. Test: `selftest_maturation_now.py` check 18.
- **Promise: a passed mod rests, it does not wait.** `waits_text` removes the leading "waiting:" for a passed mod.
  Test: check 18 (`waits_text` of a passed mod).
