# Status pages: the successor to RimPulse (STATUS_PAGES_BUILD_REPLACE_RIMPULSE)

Owner, by card 2026-11-03: *"Retire it, build pages; the Desktop Archmagi can just have it open in a browser tab
regularly when regenerated; phone on request via Conductor."* RimPulse is retired
(`RIMPULSE_RETIRE_SUPERSEDED_BY_STATUS_PAGE`). What replaces it is two script-built pages, neither of which spends AI
tokens:

| page | answers | built by | how often |
|---|---|---|---|
| `D:\ClaudeWork\rimmandrake\conductor\RUNNING_NOW.md` | what is running this minute: workers, processes, the game, the clones | `src/RimMandrake/Utils/running_now.py` (`rm-running.timer`) | every minute |
| `D:\ClaudeWork\rimmandrake\conductor\STATUS_BOARD.html` | how it is going: Needs you, each mod's finished / in progress / stuck, the week's trends | `src/RimMandrake/Utils/status_board.py`, called by `running_now.py` after each fleet refresh | every 5 minutes |

## What the board promises (his card on the mockup, each one tested in `selftest_status_board.py`)

- **Every stuck line says what is planned and who it waits on.** `fleet_mods.stuck_of` turns each way an item can
  stand still (an owner question, a Relentless hold, a ledger block on an item, on time, on the game, on a judge, a
  standing FAIL) into a plan sentence and a waiter. A free-text block reason is cut to its first sentence and stripped
  of machine words (`plain_reason`).
- **"Needs you (N)" matches every needs-you tag.** The tag is written only when `owner_queue.is_his` says so, the
  same test that builds the Needs you list. A block whose reason mentions an old card of his reads "a past ruling of
  yours (parked on purpose, no question open)", never "you".
- **No cryptic lines**: no hold-class slug and no bare item id in the visible text (ids sit in hover titles).
- **Dark 70s-brown**, the palette of `project_maturity_dashboard.py`; **phone-readable** at 390 px.
- **Ops trends RimPulse never delivered**: per day, items finished, errors handled (a failure the machine caught and
  sent back by itself: failed blind check, weak proof, lost checker, close retry), errors to a person (a hold handed
  to the Conductor or him, a jam, an alarm), and game tests with a real answer out of those run. Source: the tick acts
  of the Relentless journal; a day before the journal starts reads "no record", never 0.

## What is still owed, and is not this item

- **The AI summary a few times a day.** The board's top lines are templated English. A short written digest
  (the Conductor's, through the CLI per the LLM-transport ruling) could sit above them; it needs its own schedule
  item, since it is the only part that spends tokens.
- **The phone copy.** On request, the Conductor sends him the page (he wants nothing pinned on his phone).
