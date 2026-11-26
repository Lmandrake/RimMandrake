# WORLD_NULLTEX_FLOOD_HUNT_NEEDS_A_STACK

## proof (corrected 2026-11-17, drain of the retired judge)
The offline half:

    python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_nulltex_probe.py

Measured 2026-11-17: rc=0, RESULT: GREEN. The selftest pin landed at 71eb4aba2c (the selftest now pins the
tool the build actually compiles).
Evidence: /Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/WORLD_NULLTEX_FLOOD_HUNT_NEEDS_A_STACK.txt

## why this is ready, not done — the item's own acceptance is live
`infrastructure/state/live_proofs/WORLD_NULLTEX_FLOOD_HUNT_NEEDS_A_STACK.criteria`:
  A1 L1 — jawa/nulltex_probe is ARMED on the GUI.DrawTexture leaf and its selftest null call comes back with
          a CAPTURED STACK
  A2 L2 — after a world load, captured null-texture stacks name a non-probe culprit frame, split into world
          load, menu and load time
The whole point of the item is a captured stack naming the culprit; a stack can only be captured inside the
running game's Mono. The offline selftest proves the probe compiles and is pinned, nothing more.

Next worker: arm the probe with the game up, load a world, and read the captured frames.
