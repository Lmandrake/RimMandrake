# RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** on the sibling's calm tool: named, versioned profiles; a control reads HELD only after a planted
  breach of its kind was seen stopped on this mod list (in the certification session), else ARMED UNPROVEN; the breach
  log in the trace; the three gates of the gates ticket joined into the profile with a scene's exceptions; the profile
  armed again after a load; the lease; destructive controls refused only while a canonical world save is loaded (CAMPAIGN).
- **Needs:** the run-plan ticket; the gates ticket; the tap certificate; the sibling's calm tool.

Depends on: `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`, `RIMMANDRAKE_BUILD_INCIDENT_QUEST_MENTAL_GATES_BEFORE_CERTIFICATE`, `RIMMANDRAKE_BUILD_TAP_CERTIFICATE_CANARY_RUNS_OFF_STAGE`, `RIMMANDRAKE_BUILD_BRIDGE_RECEIPT_CALM_AND_TAP_EITHER_WAY`.

## verify

Acceptance test (offline), 11 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_calm_profile.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_calm_profile.py`, 11 checks on the pure part: a
  control reads HELD only with its certificate line (1); a scene's exception opens one gate for one named event and
  closes it at leave (1); a hold on needs is two entries, the hold and what did not happen (1); the put-back runs in
  reverse order with read-back (1);
  a lease that ran out puts back (1); a value that could not be put back is named (1); a destructive control with a
  canonical save loaded is refused by name, and runs on any other save (1); "attempts stopped" and "scheduling switched off" are two numbers (1); a second
  driver's call is a breach of class APPARATUS (1); unknown profile keys are refused (1); a control of class NOT
  UNDONE is listed as such (1).

- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_calm_profile.py`, 5 rows: a planted incident,
  a planted wild animal at the stage edge and a planted weather change each give one breach record that names them (3);
  a load in the middle changes no status (1); a killed driver leaves no control on after the lease (1).

Live state at filing: UNRUN: its script `prove_calm_profile.py` does not exist yet.

## criteria

- The acceptance test prints 11 checks passed and exits 0.
- At least one planted fault per promise was seen red before the ticket closes (the build order names no plant here).
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
