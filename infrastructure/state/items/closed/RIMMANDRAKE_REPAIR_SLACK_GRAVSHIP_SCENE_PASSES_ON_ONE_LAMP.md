## spec
Gimme Some Slack (Design Version 0.2.0). A WRONG-CHECK FAULT ON BARS. Finding of the costly-acts study (`design/specs/2026-11-23-costly-test-acts/analysis.md` section 3, "The scene that ran is thinner than its text"; item RIMMANDRAKE_CENSUS_COSTLY_TEST_ACTS_REPEATED_HE_SAW_SHIP_FLY).

**Bars this scene decides: `gravship_connectivity` and `gravship_keeps_connections`** (the first lists `sc_gravship` under `decides` in `design/concepts/GimmeSomeSlack/version/test_table.json`; the second is the scene's `requirement` in `design/concepts/GimmeSomeSlack/scenes.json`). The keep-wires part of `mod_settings` is read by the same flight. So the PASS of visit 1 on those bars stands on a thinner scene than the bar text. [measured, code read]

**Measured:** `scenes.json` sc_gravship asks for: two wall-bracket anchors joined by a span, a battery and two consumers on conduit (one net asserted), and a planted control (the pre-launch cord set fed to the true-to-grid read against the landed map must FAIL by name). `src/RimMandrake/GimmeSomeSlack/northstar/gravship_scene.py` stages masts, a floor run and ONE lamp, no battery, no brackets, no second consumer, and runs no control; it writes `status PASS` with no control row (analysis section 12). The ship it flies is the recipe of `src/RimMandrake/bridgetools/prove_gravship.py`. The scene text's entry point is `validation.py::scene_gravship`.
Two ways to repair: stage what the text asks, or amend the text with a stated reason that a thinner scene decides the bar (the bar's owner text wins unless the Conductor rules; do not edit the text to pass). The grouped one-ship scene (RIMMANDRAKE_MERGE_SLACK_GRAVSHIP_CHECKS_ONE_SHIP_TWO_FLIGHTS) must carry the same four things; this ticket is the fault, that one is the saving.
Until repaired, the two bars' PASS is to be read as "decided on one lamp".

**Recommendation: current Design Version** (a bar's decider is wrong; no mod change, no version bump). The Conductor decides.

## verify
Acceptance test (offline proxy): `bash infrastructure/state/items/RIMMANDRAKE_REPAIR_SLACK_GRAVSHIP_SCENE_PASSES_ON_ONE_LAMP.acceptance.sh`
- Reads the code (string literals and names; not comments or docstrings) of gravship_scene.py and prove_gravship.py for the four things. WATCHED FAIL today (2026-11-24): `staging asks for 4 things; the code names 0; missing: ['wall-bracket anchors', 'a battery', 'two consumers', 'the planted control']`, exit 1. `--selftest` prints SELFTEST OK (4 cases: docstring only -> red; one lamp -> red; all four -> green; unreadable file -> could not look). Watched green.
- Weak: names in code do not prove the flight staged them. Part 2, UNRUN (live, needs Odyssey and a game): `gravship_scene.py on --out RESULT.json` and `off`; the result must carry a control row that is red when the pre-launch cord set is planted and green on the real landed set, and the census before launch must read the battery net (one net, two consumers) and the bracket span linked.

## criteria
- The proxy exits 0; the live result carries the four things and the control, with the control seen red on a planted fault and green on the real flight.
- The two bars' decision is re-read against the repaired scene (PASS stands or falls with it).
