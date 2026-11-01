# ARENA_DAYZERO_PROVE_GAME_DEV_BAR_LIFTS

Filed (OWNER): the day-0 gate. `seat_focus.until_item` in `src/RimMandrake/rimflow/dispatcher_schedule.json` reads this
item; marking it implemented ends the FOUNDRY game-dev bar (OP-20261031T1433Z).

## verify
- L0: implement only when every ARENA_ trial item and TESTER_PROMPT_TUNE_REJECTS_MOST_GOOD_WORK are implemented and the
  failure drill has passed. Before marking, list each open ARENA_/TRIO_ item on this item as implemented or excluded,
  with who excluded it. After marking, `rimflow next --seat FOUNDRY --peek` offers an item outside `include_prefixes`.
- Stopping point: finish.

## criteria
- A1 L0: every trial item accounted for by name; the bar demonstrably lifted
