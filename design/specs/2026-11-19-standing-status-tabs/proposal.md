# Proposal: one standing browser for the status pages (CODEBASE_NOW, FLEET_NOW, MATURATION_NOW)

Item: `RIMMANDRAKE_REVIVE_CLEAN_DIRTY_TREEMAP_ON_STANDING_TABS`. His words on the card of 2026-11-19 5:54 PM PST:
*"perhaps this should become tabs in a standing browser actually, along with FLEET_NOW and MATURATION_NOW in their own
windows"*. This page is a proposal. Nothing on it is built, and no window was opened on his desktop. Written
2026-11-19.

## What exists today (measured 2026-11-19, 6:20 PM PST)

All the pages are files in `D:\ClaudeWork\rimmandrake\conductor\`. Each one is written by a program, with no model call.

| what he calls it | file | written by | how often | reloads itself in an open tab |
|---|---|---|---|---|
| CODEBASE_NOW | `CODEBASE_NOW.html` | `codebase_now.py`, `rm-codebase-now.timer` | 15 min | yes, 900 s; also shows STALE past 1 h |
| MATURATION_NOW | `MATURATION_NOW.html` and `MATURATION_NOW.md` | `maturation_now.py`, called by the maturation dispatch tick | each tick | no |

There is no opener. The Windows Startup folder holds one shortcut, `Start Agent Fleet.lnk`, and it runs
`launch_fleet.ps1`. That script opens terminal windows only. No scheduled task names these pages. No file in the
repo opens them. He opens each page by hand. The "standard suite" is that folder today.

The older hub (`infrastructure/dashboards/hub/`) is a tabbed shell. It needs a Claude Artifact publish step (tokens)
or `build_standalone.py`. Its health tab is the older treemap. It is not a candidate: it spends tokens, and its data
goes stale between publishes.

## Three ways to do it

### A. One Chrome window, one tab per page (recommended)

A small `./pages` command (and, if he wants it, a second Startup shortcut) runs
`chrome.exe --new-window <url> <url> <url>` with the HTML pages. Each page reloads itself.
- **To build:** the opener, about 30 lines. Also a self-reload line in `maturation_now.py`. The fleet page is Augur's `D:\ClaudeWork\augur\dashboard\FLEET_NOW.md`, not a tab.
- **Buys:** the cheapest path. The tabs are real browser tabs (Ctrl+Tab), and he can zoom and search each one.
- **Costs:** a closed tab stays closed until the next `./pages`. Chrome puts the tabs in his normal profile, among his
  own tabs.

### B. Own windows: one chrome-free window per page

The same opener runs `chrome.exe --app=<url> --window-position=x,y --window-size=w,h` once per page. Each page then
has its own window with no tab strip, at a fixed place (one per monitor, or tiled).
- **To build:** A, plus a window layout in a small JSON file that he can edit.
- **Buys:** "in their own windows", word for word. Each page stays in sight at one time, and Alt+Tab names each one.
- **Costs:** three windows to manage. Placement on a second monitor needs a measured layout. App windows need a
  separate Chrome profile, or they can join his main window.

### C. One shell page with tabs, served locally

A static `STANDING.html` in the same folder holds a tab strip and one iframe per page, and it reloads the active
iframe on the page's cadence. A browser does not render a Markdown page, so FLEET_NOW comes in as `FLEET_NOW.html`.
- **To build:** the shell page and its selftest. Chromium may refuse a `file://` page inside a `file://` frame, so a
  small local static server (`python -m http.server` as a user unit) can be needed. That server can also serve the
  phone over Tailscale.
- **Buys:** one bookmark and one window, with tabs that we control (badge colours from each page's age, a STALE dot).
- **Costs:** the most to build, one more daemon to keep alive (a deadman promise), and a second tab layer inside the
  browser's own tabs.

## Recommendation

Start with **A**. It costs one small helper run, it uses pages that already exist, and it can grow into B by a flag
(`./pages --windows`). Build C only if he wants the phone to read the same set.

In any case, these acts are his: he must say whether a Startup shortcut may open windows at logon, and which monitor
gets each window. This run opened nothing on his desktop.

## Owed work (from the card; where each goes)

- The treemap is back as a standing page (`CODEBASE_NOW.html`). Its promises are on
  `design/specs/2026-11-19-codebase-now/boundary.md`. Done in this item.
- The opener (A or B) is filed as its own item. It waits on his pick.
