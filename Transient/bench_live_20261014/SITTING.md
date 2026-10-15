# BENCH live round 2 + ratchet pilot, 2026-10-14

Code at **28247cdeff** (`git archive` to ext4 `/home/mandrake/.seat-tmp/BENCH/r3_export`; python copy at
`D:\Luke\dev\_rmscratch\bench_live_20261014`). Tier ratchet_pilot+patches, 23 mods (ModsConfig md5 0bab16fa).
- Deploys: FlowWorks 4 files (DLL+srchash, RM_LiquidLogistics.xml, XTall tank png) VERIFIED; PyrelandsMechanics and
  composed biomes in sync (the Pyre burrower fix d4a56f1ec0 DLL was already deployed). dll_source_stamp: FlowWorks and
  FireEcologyHook MATCH. Companion rebuilt from the export: identical to the deployed DLL.
- Launch via Steam READY 180 s (`launch.txt`).
- Census: 396 tools declared in the DLL, 396 live. `jawa/revoke` is not a tool: it is a phantom from the old
  name scanner reading "Grant/revoke" prose in jawa/royal_title (build.py docstring). Nothing to file.
- JawaBench test profile had expired (2026-10-13 18:00Z); renewed to 2026-10-15T12:00Z, same keys.

| item | check | result |
|---|---|---|
| SAFE_ADVANCE_MENU_DIAGNOSE_LUCKY_NULLREF | quicktest, safe_advance 20000 timeoutMs=0, go_to_main_menu, status (`menu_probe.json`) | **PASS** with a label deviation: aborted, tickTo 961 > tickFrom 1, 0 NRE / 0 "stepper exception" in Player.log. abortWhy reads `map_gone: start map #0 ...`, not `game_changed` - teardown drops the map before Current.Game changes |
| PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE (run 1, 28247cdeff) | site `NS_Pyrelands_site_1_417df172fdb5_r2` (fresh, 52.8 C), fixture reloaded before EVERY trial, Ashwallow 5 cells from a 6x6 fire, job sampled every 10 ticks x40 (`burrow/burrow_cold_*.json`) | 11/16 dove at 50 ticks, 5/16 at 270-350 after a long GotoWander; Flee 0/16. **MOD bug found:** the nudge table was static; a reload re-issues the same thingIDNumber at the same tick (fireTick 376511 every trial) so the previous trial's entry blocked the first nudge for 250 ticks. Fixed in 0afba7de51 (per-component table) |
| same, run 2 (0afba7de51, restarted) | same probe (`burrow/burrow2_cold_*.json`) | **PASS** 10/10 dove at 50 ticks, incl. two repeated ids. Flee never preceded a dive (0/26 over both runs). "Flee can still win" is INFERRED: the nudge only calls CheckForJobOverride, so the think tree keeps AnimalFlee above the burrow giver; night 2026-10-13 cold_2 showed Flee ending a dive |

Restart at 0afba7de51: FlowWorks (tank defs/textures 9fece3b324), PyrelandsMechanics DLL, composed Pyrelands (FireEcologyHook + RM_LightningBreaker.xml) deployed and VERIFIED; GSS in sync. Companion NOT rebuilt: it stays the 28247cdeff build (b59c434462's jawa/health tools are in source, undeployed). Launch READY 113 s (`launch_2.txt`).
