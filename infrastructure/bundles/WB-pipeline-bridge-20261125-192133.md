# WB-pipeline-bridge-20261125-192133 state

Worker run on SteveDesktop, started 2026-11-25 11:22 AM PST. Context after class step: about 150k of 1M.

## What this system is now
- 23 of 25 members are BUILT and owe only a live reading; nothing to fix in their code is known.
- The SteveDesktop lane lost 8 attempts to one fault with no ticket: a `live-proof` line written `python3 ...` cannot
  reach the bridge from WSL (NAT mode). FIXED at aa1f34fac8 (`worker.py` `run_proof_line` reruns once under
  python.exe; `selftest_steve_worker_wsl_proof.py`, red before, green after).
- Drive Steve1 from this machine with `source infrastructure/stevedesktop/testcentre_env.sh` and `python.exe`, held by
  `python3 src/RimMandrake/rimflow/host_guard.py run --seat BENCH --for "<what>" -- <cmd>`.
- Raid tests are paused (`raid_pause.py show`): MAP_AWARENESS A9/A10 and THING_LOOKUP A5 cannot run.
- Full-list testing is retired until integration (CLAUDE.md §Mod development runs on small lists): a criterion that
  names the full list is read on the small list, or refused when only the full list can decide it.

## Done
| member | outcome | commit / reading |
|---|---|---|
| (lane fault, no ticket) | fixed | aa1f34fac8 |

## Next, in order
1. Live sitting on Steve1: MAP_AWARENESS proofs (not A9/A10), then the read-only tool checks of the other members.
2. Save + reload checks (BRIDGE_TARGETS, FRAME_HIST), then a restart check (AWARENESS A1, PAWN_ORIGIN A2, TPS C3).
3. Refusals with reasons: FLYERFRAMES (owner act), raid clauses, full-list-only criteria.
