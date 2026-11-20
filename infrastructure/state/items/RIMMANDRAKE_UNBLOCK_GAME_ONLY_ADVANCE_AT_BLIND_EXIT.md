# RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT

Filed by the detached helper on RIMMANDRAKE_CLEAR_FLOWWORKS_PAPERWORK_TO_GAME_ONLY_ROAD, 2026-11-19 7:47 PM PST. Pipeline
machinery, class BLOCKS for FlowWorks' move to Stage 6.

## spec
The Conductor decided FlowWorks 0.1.0 goes to Stage 6 by the game-only road, with no fifth blind cycle
(`maturation.py advance FlowWorks --to in_game --game-only <IDs> ...`). A dry `maturation.evaluate` of that move
(measured 7:45 PM PST on 47ff540ca, writes nothing) passes the `game_only` clause with the five game-side tickets, but
refuses two other clauses:

- `exit_met`: blind_challenge -> in_game is also the FORWARD step (`evaluate`: `forward` is true), so
  `exit_met_clause` applies. Cycle 4 reads not met for two reasons, and neither can clear offline:
  1. its own Exit block says `exit_met: false`, because it FIXED four Problems, so `read_exit` owes a new blind judge
     (`judge_owed`). The Conductor ruled out that fifth cycle.
  2. three lane-1 `not_kernel` UNSETTLED rows (SHEET, THIRST, DRILL) name offline bars (proves_at 4-5), so
     `_lane1_deferred` does not defer them (the loophole that RIMMANDRAKE_DEFER_BLIND_EXIT_STAGE_SIX_ROWS_NEVER_OFFLINE
     closed). They are now filed as game-side tickets: the game alone can show them.
  The only override is `--owner-said OWNER:<tsn>`, an event of his on the OWNER shard that carries `ownerSaid` or
  `byCard` (`owner_event`). A Conductor `--per-ruling` event carries neither, so the Conductor cannot make that move
  by itself.
- `judge_certificate`: it also applies to a forward move out of blind_challenge. For its state after tonight's
  `certificate --run`, see the note on RIMMANDRAKE_CLEAR_FLOWWORKS_PAPERWORK_TO_GAME_ONLY_ROAD.

The two routes, and whose each one is:
- (a) his words, as an OWNER event, then `advance ... --owner-said OWNER:<tsn>`; no code changes.
- (b) a reader change: when the move is game-only and its `game_only` clause passes, `exit_met` does not count two
  things: a `judge_owed` that comes only from the cycle's own FIXED Problems, and lane-1 not_kernel rows whose bars
  each have a named game-only item. This loosens an exit gate, so it is the Conductor's mindful act (`lost:`, `undo:`),
  not a helper's. That is why this helper set the fix down (§Touching code, test 2: it needs a looser bar).

## verify
`python3 src/RimMandrake/rimflow/acceptance/game_only_blind_exit_accept.py` from the repo root. Red today:
`FAIL 0/1: exit_met refused` (watched 7:46 PM PST). Expected pass count: 1/1. This oracle tests route (b). Route (a)
does not change code and is checked by the advance itself.

Acceptance test: `src/RimMandrake/rimflow/acceptance/game_only_blind_exit_accept.py` (1 check; red on 47ff540ca).

## criteria
The Conductor picks (a) or (b). For (b), the acceptance reads `PASS 1/1` and `selftest_maturation.py` stays green; a
blind exit with an unfixed Problem, or an offline row with no named game-only item, still refuses.

## refs
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/acceptance/game_only_blind_exit_accept.py
