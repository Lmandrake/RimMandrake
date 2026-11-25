# RIMMANDRAKE_BUILD_INCIDENT_QUEST_MENTAL_GATES_BEFORE_CERTIFICATE

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** the three gates that the calm profile will use, as mechanisms with an allow list and an attempt count:
  incidents at `IncidentWorker.TryExecute` (on the present awareness hook), quests at `QuestManager.Add`, mental
  states at `MentalStateHandler.TryStartMentalState`; the queued incidents held aside and given back with every
  absolute tick moved by the time held (the fire tick and the retry window). They are built before the certificate so
  that the certificate can show a held route and a refused route for each.
- **Needs:** the world event taps ticket.

Depends on: `RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY`.

## verify

Acceptance test (offline), 9 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_gates.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_gates.py`, 9 checks: the allow list lets one
  named incident through once (1); a held attempt is counted and recorded with its caller (1); a gate that is off
  changes nothing and records nothing (1); a held queue entry comes back with its fire tick and its retry window both
  moved (2); an entry already past its retry window when held is reported, never dropped in silence (1); the hook
  rules for the two new gate sites (2); with a canonical save loaded (CAMPAIGN), every gate is refused (1).

Live test: none drafted in the build order for this ticket.

## criteria

- The acceptance test prints 9 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** a queue return that moves the fire tick only (GPT's case: the entry expires at
  once).
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
