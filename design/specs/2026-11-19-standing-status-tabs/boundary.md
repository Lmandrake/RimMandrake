# BOUNDARY: the standing status tabs (`./pages` and the self-reload of MATURATION_NOW), Design Version 0.1.0

Code: `src/RimMandrake/Utils/pages_open.py` (run by `./pages` at the repo root), and in `src/RimMandrake/Utils/maturation_now.py` the reload and build-time lines of the HTML page (`build`).
Item: `RIMMANDRAKE_BUILD_PAGES_OPENER_ONE_EDGE_WINDOW_THREE_TABS`. Design: `proposal.md` beside this page, option A. Why it
exists: the owner, 2026-11-19 about 7:02 PM PST: *"Please move MATURATION_NOW and FLEET_NOW into tabs alongside
CODEBASE_NOW"*. Written 2026-11-19. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_standing_tabs.py`. This page covers only the two parts named above, not the rest of
`maturation_now.py`.

## ACCEPTS (the only inputs the opener is built for)

- **a-conductor-folder-by-rmpaths.** The folder is `rmpaths.rm_path("conductor")` (env `RM_DATA_ROOT`), read each run.
- **a-windows-desktop-with-chrome.** `cmd.exe` reaches Windows from WSL2 and Chrome is registered as `chrome` (never Edge: owner, 2026-11-19 7:14 PM PST, *"OMG you used Edge?! never. Chrome please."*).

## DOES NOT SURVIVE (not promised; where the opener notices, it says so)

- **no-chrome-or-no-desktop.** The launch command fails; the opener prints the failure and exits 3. It cannot tell a
  window that opened and closed at once from one that never opened.
- **a-tab-the-owner-closed.** A closed tab stays closed until the next `./pages`. A second `./pages` opens a second window.
- **a-stale-tab-in-a-dead-writer.** The tab reloads the file; if the writer died, the file is old. The page shows its
  build time so that this can be seen. It has no banner (CODEBASE_NOW has one).

## PROMISES (each one is owed a test of the same name)

- **two-tabs-in-order.** One command opens one window whose tabs are CODEBASE_NOW.html, then
  MATURATION_NOW.html, each as a `file:///` URL (the fleet page is Augur's, not a tab here) in the conductor folder. Tested by `t_two_tabs_in_order`.
- **missing-page-named-others-open.** A page that is not on disk is named in the output as MISSING, the other pages
  still open, and the exit code is 2. All present: exit 0. Tested by `t_missing_page_named_others_open`.
- **folder-from-rmpaths.** Changing `RM_DATA_ROOT` changes the folder in every URL; no drive path is written in
  `pages_open.py`. Tested by `t_folder_from_rmpaths`.
- **never-fullscreen-never-steal-focus.** The launch asks for a minimized start and carries none of the fullscreen,
  kiosk or app flags; `--show` is the only way to a normal start. Tested by `t_never_fullscreen_never_steal_focus`.
- **dry-run-opens-nothing.** `--dry-run` prints the command and one URL per line, and calls no launcher. Tested by
  `t_dry_run_opens_nothing`.
- **maturation-page-reloads-and-shows-build-time.** The MATURATION_NOW.html page carries a refresh line of 300
  seconds and its build time in its first lines, visible. Tested by
  `t_maturation_page_reloads_and_shows_build_time`.


## LIMITS

- **300 seconds, the reload of the MATURATION_NOW tab.** Danger: a tab that reloads slower than its writer shows old
  data. The writer runs each dispatch tick (measured: the item's design table, 2026-11-19), and the tab shows the build time, so a tab older than that is plain to see.


## LIFE CYCLES (a move not listed here is a defect)

- **a run:** read the folder → check each page file → build one command → (dry run: print and exit 0/2) → launch →
  print each URL and each MISSING → exit 0 (all opened), 2 (a page missing), 3 (launch failed).

## MATURATION_NOW.md, section "Every mod, one line" (`maturation_now.py`, `one_line_md`)

- **Promise: no table, no cut text.** The section is one bullet per advancing mod (mod, version, stage, last movement; then
  its "Waits on" line and its "Needs you" line), and held, off or paused mods are one short list. Typora sizes table
  columns by the longest cell, so a table made narrow, tall rows. Test: `selftest_maturation_now.py` check 18.
- **Promise: a passed mod rests, it does not wait.** `waits_text` removes the leading "waiting:" for a passed mod.
  Test: check 18 (`waits_text` of a passed mod).
