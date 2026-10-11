# Long live proofs on the full list — the harness is the first thing to fail

A full-list proof run surfaces 2-4 NEW harness assumptions per ~15-minute run.
Rerunning to find them one at a time is the expensive way; **one fresh-context,
read-only audit of the whole fragility CLASS** — camera, tick stepping, idle
pawns, site margins, fog, save/load timing — found 8 at once (2026-10-11). Do it
before the second full-list run, not after the fifth.

- **The proof map does not stay calm.** Wild animals respawn after a one-time
  non-colonist sweep (a predator downed two colonists mid-run), idle colonists
  wander fast into test sites, and a map-gen insect hive throws its own NREs.
  Re-calm before EACH block (`rimworld-live-review` §1) and draft every colonist
  the block is not using.
- **Timing traps** — tick-keyed caches, a stepper that overshoots short states,
  load-call races: `rimbridge/references/traps.md`, "Bridge time is TICKS".
- **Log noise** is charged to a mod only against a same-list control:
  `rimworld-modding/references/player-log-triage.md`.

🔴 **A simplified model passes what the real operation refuses.** An install
precheck that judged a taut route with no nozzle lead-out accepted orders the
real lay then refused — the colonist carried the hose out to nothing; an offline
selftest that modelled the reel as 1×1 with no outlet stayed green while 7 live
rows went red. Where the real operation's trial run is cheap, gate on IT, not on
a model of it; and when a ruling changes the real geometry, re-check every live
scene built before it (`deciding-and-superseding`, "A stale belief hides…").
