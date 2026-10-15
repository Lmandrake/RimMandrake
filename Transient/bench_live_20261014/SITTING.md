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
