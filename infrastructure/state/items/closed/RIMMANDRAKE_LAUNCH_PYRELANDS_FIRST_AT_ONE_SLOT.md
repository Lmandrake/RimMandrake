# RIMMANDRAKE_LAUNCH_PYRELANDS_FIRST_AT_ONE_SLOT

## spec
The owner by card 2026-11-17 (header "Next mod", `D:\ClaudeWork\rimmandrake\cards\cards.jsonl` line 114): "Which mod
gets the next run?" -> "Pyrelands (Recommended)". At max_live 1 the next free slot goes to Pyrelands' chain (its fixer
on RIMMANDRAKE_REVERSE_PYRE_WIND_BEARING_ONE_DIRECTION_STAGED today), never to Gimme Some Slack or Graffiti.

## found (measured 2026-11-17)
- `advancing` order was the only priority, and only `decide` honoured it. `maturation_autonomy.resolve` gated each
  steward/fixer run on `occupancy + len(launches)`, every launch of the tick counted, a later mod's included; so at
  max_live 1 a later mod's decide launch (a blind cycle, a build) took the slot and the earlier mod's fixer read
  slots_full (probe: P fixer + G blind launch -> launches ['G'], P slots_full, in either list order).
- `pilot_holders` had the same count (`planned = base + len(launches)`).
- A mod whose run had just ended (settling, settle_s 180) held no slot, so a later mod could take it in that window.
- A zero-token certificate rerun counted against the slot in resolve's count.

## built
- `maturation_dispatch.json`: Pyrelands first in `advancing`; `_advancing_doc` cites the card.
- `maturation_dispatch.py`: `prioritise()` runs after every layer in `_tick`: one pass in list order; a settling mod
  keeps its slot; a steward/fixer run refused only for a slot a later mod took is granted again (through
  `AUT._gate`); a launch past max_live goes back to slots_full naming the mods ahead. `pilot_holders` counts only the
  launches ahead of the mod. Certificate reruns and autolock/autorepin take no slot (`takes_slot`).
  maturation_autonomy.py was left alone (another builder holds it); the fix sits after it.

## acceptance
`python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py --priority` (also in the full run): 7 checks, P
(first, fixer owed) vs G (second, decide launch) at max_live 1. Watched failing 5 of 7 on 4d4dad7bcf's dispatch with
prioritise as the identity; passing 7 of 7 after. Live dry pass (state copied to scratch): with ExplosiveKnockback's
rescue run live, Pyrelands waits slots_full (correct: live runs finish); with that run's unit removed from the facts,
Pyrelands reads would_launch its fixer.

## criteria
- At max_live 1 with a fixer owed on the first advancing mod and a launch owed on a later one, the first mod's fixer
  launches and the later mod reads slots_full naming the mod ahead.
- A settling mod keeps its slot; a certificate rerun takes none; a pilot holder ahead beats a later launch.

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_dispatch selftest_maturation_autonomy
selftest_dispatch_pilot_holder` GREEN; `selftest_maturation_dispatch.py --priority` ALL PASS.

## refs
file: src/RimMandrake/rimflow/maturation_dispatch.py
file: src/RimMandrake/rimflow/maturation_dispatch.json
file: src/RimMandrake/rimflow/selftest_maturation_dispatch.py

## not changed
max_live stays 1. A live run is never stopped. The order of the other mods is unchanged.

## What the card said

<!-- answered 2026-11-17T18:37:14Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** New launches now wait until every live run has ended, then go one at a time. Three mods are waiting and the remaining system account may only cover one of them before the stop. Which mod gets the next run?
**Picked:** Pyrelands (Recommended)
**Its description:** Why: it is mid-repair. Its exam passed today; two test scenes and three text leftovers must be fixed before its final check. Buys: could reach the final check first. Costs: Slack and Graffiti wait for Wednesday. Recommended: closest to passing its version.
**Other options:** Gimme Some Slack · Graffiti · Leave the listed order
