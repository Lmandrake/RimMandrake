# RIMMASTER_FIX_AGENT_GAME_EVENTS_FILED_AS_OWNER: measured 2026-11-19 15:30 PST

- `./game --why "..." loading`, run by this detached helper (AGENT_SEAT=BENCH, RM_ROLE_UNIT set) on a temp ledger,
  wrote ONE event to `events/OWNER.jsonl`:
  `{"seat":"OWNER","event":"game","state":"LOADING","ranBy":"BENCH","role_unit":"rm-detached-bench-...","why":"..."}`.
- `owner_interaction.is_his_act` on that event: False. `ranBy` and `role_unit` are HANDS_FIELDS, so an agent's game
  event never runs his 45-minute clock (commit d3101f19b2, 2026-10-31, "only his own acts run his clock").
- Seat OWNER on a game event is by design: `./game`'s header says the event is OWNER's (his authority); `ranBy`
  names the acting seat. The 2026-11-08 events (cb497082d8) carry `ranBy: BENCH` too.
- Regression test that already holds the line: `src/RimMandrake/rimflow/selftest_owner_hold.py`
  `test_relayed_orders_are_not_his_acts` (a game event with `ranBy`, `role_unit`, `why`, ... is not his act); run
  2026-11-19 on this clone: all ok.
