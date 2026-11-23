# RIMMANDRAKE_BUILD_TAP_CERTIFICATE_CANARY_RUNS_OFF_STAGE

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** the certification suite of `05_build_design.md` decision 4: for every tap, a positive and a negative
  route fixture by real engine acts, in a disposable game; a planted blind tap; the list of foreign patches per tapped
  method; the certificate file keyed by companion hash, mod list fingerprint, patch inventory hash and the settings hash of
  every mod with a patch on a tapped method; the check at arm, which performs no gameplay act and compares the scene's
  needed routes with the certificate; the run-time witness (entries against records); the reference scene run with
  and without tracks. From this ticket on, a run with a valid certificate is no longer BOOTSTRAP.
- **Needs:** both tap tickets and the gates ticket.

Depends on: `RIMMANDRAKE_BUILD_CAST_TRACKS_AND_JOB_TAPS_FIRST_FAMILY`, `RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY`, `RIMMANDRAKE_BUILD_INCIDENT_QUEST_MENTAL_GATES_BEFORE_CERTIFICATE`.

## verify

Acceptance test (offline), 11 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_tap_certificate.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_tap_certificate.py`, 11 checks: a certificate for
  another companion hash is refused (1); for another mod list (1); a changed patch inventory is refused (1); a tap
  with a route not shown is listed as such, never as covered (1); a scene that needs an uncertified tap is COULD NOT
  ARM (1); the arm check calls no op of the act list (1); a foreign prefix is named on the receipt (1); a missing
  certificate is "could not look", never "covered" (1); a changed setting of a mod with a foreign patch voids the
  certificate (1); an entry with no record voids that tap's coverage for the run (1); an absence on a method with a
  foreign prefix reads "not provable here" (1).

- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_tap_certificate.py`, 4 rows: every fixture
  leaves its record on the 13-mod list; the same on the full list, with each foreign patch named; one hook taken off
  by hand is reported blind; the suite's time is printed.

Live state at filing: UNRUN: its script `prove_tap_certificate.py` does not exist yet.

## criteria

- The acceptance test prints 11 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red (live):** a tap whose Harmony patch was never installed while the recorder's unit
  tests pass.
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
