# FOUNDRY acc_green_min acceptance sitting 2026-10-08
Bridge: FOUNDRY (taken 22:32 PDT). Previous acc_biomes game killed by PID 25656 (ours), tier acc_green_min applied (35 mods), launched via steam://rungameid.

## Milestones
- 22:33 launched.

## Results

## Skipped
- 22:34 game up on acc_green_min (35 mods). Suites run live via Transient/acc_biomes/run_live_suite.py, outputs in Transient/acc_green/run_*.txt.
- 22:50 First pass: GravshipLanding ALL_GREEN; Scarlands 26 pass/0 fail/17 unm; ShipVermin, Abyss, OasisMaker, Pyrinth, HugeThings had failures. Triage (source first):
  - ShipVermin: alert chain read the alert once right after a paused tick burst (AlertsReadout refreshes per rendered frame, not tick; MEASURED alert appears after ~240 ticks with real time) => checker timing, fixed with real-time polling; nest chain used debug path `Actions\Force nest...` but ToolMap actions are `Actions\T: Force nest...` => fixed path. Nest chain now measures.
  - OasisMaker fast_settings: 2500 ticks reached ring 7 of 8 => budget short, raised to 4000.
  - Pyrinth mineableThing: get_defs reads "(no such field)" for building.* => tool gap, now UNMEASURED not FAIL.
  - HugeThings: deployed copy was STALE (Titanic merge c954ccdca 22:15 landed after the previous deploy; defs/CrushRuleDefs etc missing) => redeployed via deploy_custom_mods --mod HugeThings --apply after killing our game (PID 29020), relaunched 22:5x.
  - Warcasket and Ninefold/LuminousPigment suites exceed 280-500 s with buffered output; rerun with python -u.
