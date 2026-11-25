# Plan: the smallest set of pages, one home per fact (2026-11-24)

Item `RIMMANDRAKE_REMOVE_RELENTLESS_NOW_PAGE_CONSOLIDATE_MONITORS_HE_SAID_SLEEK`. The owner, 2026-11-24: "Please consolidate infrastructure so
that all of these monitors, reports, etc. are clean, consistent, minimal, sleek, and self-cross-referencing." The rows: `census.md` beside this.

## The set, and the question that each page answers

| question | its one home |
|---|---|
| what is running; what is each account; what is each machine | `D:\ClaudeWork\augur\dashboard\FLEET_NOW.md` |
| what needs me; what is each mod doing | `D:\ClaudeWork\rimmandrake\conductor\MATURATION_NOW.md` (lists: `MATURATION_DETAIL.md`; phone: `MATURATION_NOW_phone\`) |
| which code is clean | `D:\ClaudeWork\rimmandrake\conductor\CODEBASE_NOW.html` |
| what alarms are open; how healthy is the machinery (Operations' page) | `D:\ClaudeWork\rimmandrake\ops_watch\digest.md` |
| which calls did agents make for me today | `Transient\delegated_digest_<date>.md`, delivered by the Conductor |

There are five pages and one daily digest. No page repeats another page's fact. A page that shows a fact from another page shows only a
count and the path of its home. Each other output in `census.md` is a data file or a log that a program reads, not a page.

## The rules for the set

1. **One home per fact.** A new fact goes on the page whose question it answers. If no page's question fits, the fact needs a ticket,
   not a new page.
2. **Every page links to the others at its top.** `src/RimMandrake/Utils/pages_index.py` holds the one list (label, full Windows path,
   question). MATURATION_NOW, MATURATION_DETAIL, CODEBASE_NOW and the ops digest print `crossref_md` or `crossref_html` under their title
   (the ops digest prints it under its headline line, which a selftest pins). FLEET_NOW is Augur's: it draws the same links from
   `D:\ClaudeWork\augur\config\dashboard.json` `links`. `selftest_pages_index.py` checks the list, each renderer and the Augur config;
   `--live` also reads each page on disk.
3. **One visual language.** The owner likes the warm dark-brown 1970s palette on dashboards, and he reads markdown in Typora.
   MATURATION_NOW and CODEBASE_NOW already use it (`#171310` ground, `#e0803a` and `#f0a867` accents, `#efe7d9` text). FLEET_NOW
   (Augur) draws blue-grey (`#14181d`). The restyle is design work in another repo, so this run does not do it: ticket
   `RIMMANDRAKE_RESTYLE_FLEET_NOW_IN_BROWN_LIKE_ITS_PEERS` (below).
4. **A page that loses its writer is deleted, with its links, in the same change.** The check `t_no_relentless_page_or_board`
   (`selftest_standing_tabs.py`) holds this for the removed pages.
5. **Retired names stay out of the page vocabulary.** Item names, seat names and quoted text that hold a retired word are data and stay.
   A page's own words, keys and alarms do not use the retired names relentless, FOUNDRY or pulse. The open case is in `census.md`.

## Done in this run

- Removed: RELENTLESS_NOW (both forms), STATUS_BOARD, ARTISAN_NOW and WHITTLE_NOW (both forms each, with their state files), the
  running_* data files, two one-off files of the retired Relentless era and the dead `D:\ClaudeWork\rimmandrake\dashboard\digests\` folder.
- The links at the top of each page (rule 2), and Augur's links repointed from the removed pages to the kept ones.

## Owed, as tickets with their acceptance checks

- `RIMMANDRAKE_DRAW_STEVE_SERVICES_ON_FLEETNOW_JSON_HAS_THEM`: FLEET_NOW draws SteveDesktop's services.
- `RIMMANDRAKE_CLEAR_RETIRED_ALARMS_OPS_MEMORY_OPEN_SINCE_NOV`: five alarm lines of removed collectors leave `memory.md`.
- `RIMMANDRAKE_DIAGNOSE_RUNP_TIMERS_PILING_ON_IDLE_DISPATCHER`: the 116 transient timers.
- `RIMMANDRAKE_RESTYLE_FLEET_NOW_IN_BROWN_LIKE_ITS_PEERS`: rule 3, on Archmagi (Augur may keep its own palette on the Macs).
