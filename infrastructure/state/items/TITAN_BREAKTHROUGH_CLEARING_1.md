# TITAN_BREAKTHROUGH_CLEARING_1 — Titans smash through obstacles

Filed 2026-10-07 by BENCH from `HUGE_THINGS_GPT_REVIEW_1` (full GPT review of the merged Huge Things, `c954ccdca`). Mod: `src/RimMandrake/HugeThings`. Do not deploy as part of filing.

## spec
Owed by ruling. Card #1 of `TITANIC_CREATURES_MOD_1` (owner, 2026-09-09): *"a titan … smashes through anything built"*. The merge adds T3-smashes-giant-plants (`huge_titan_merge_design_2026-10-07.md`). Findings B3.4 / C3.5 / D3.2 / B1.3 / C1.3 / D1.3 in `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW.md` (triage `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW_TRIAGE.md`), all independently raised by three parts.

Current state: destruction runs only from the `Thing.Position` postfix while the titan is moving. In 1.6 a path request to a destination walled off by impassable buildings or trunks fails reachability, or detours, before any step happens, so the titan never touches the wall it is ruled to smash. The walk plan itself expects "routes around and damages while brushing past".

Design and build (FOUNDRY): a bounded clearing behaviour. When a tiered titan's path is blocked (or the detour is much longer) by crush-table-eligible buildings or smash-tier giant plants, it approaches, strikes the obstacle (the plant OWNER, never the blocker proxy) on a timed cadence through the same crush rules, and repaths after destruction. Protected things (exact-protected defs, chunks, quest objects) are never targets. Pair with `LARGEPAWNS_BRIDGE_HARDENING_1` (Large Pawns' uncurated wall-break goes off). Coordinate with CreatureBehaviors if a shared job fits there. The setting needs its own toggle.

## verify
A walk lane is fully sealed by a wall plus a smash-tier giant plant, with no detour. The titan breaks through and arrives. A protected building in a second sealed lane is never struck.

## criteria
A1: the clearing behaviour exists behind a setting. A2: the sealed-lane and protected-lane walk results are recorded.

NEXT: claim it and fix the bullets in order, citing the review IDs in the commit.
