# WB-item-RIMMANDRAKE-READ-FIX-7A5DCDBC88-WITH-FRESH-EYES-20261127-130302

One member, one group. Done in one context (no restart).

| ticket | outcome | commit |
|---|---|---|
| RIMMANDRAKE_READ_FIX_7A5DCDBC88_WITH_FRESH_EYES | fresh read of 8 files; 1 significant finding fixed test first; 4 files READ-CLEAN, 4 FLAGGED | fix 3e3685e2be, polish 58eee0b36b, record b5507502780f |

- Finding: `jawa/install_blueprint` refused another map only for an unspawned carried form. A carried wreck still spawned on a
  caravan's away map got a blueprint on the home map and success, so `sc_caravan_wreck_home` could read "arrived" too early.
  Fix: `JawaBenchWreckReadsCore.Classify` takes `onThisMap` (the tool passes `t.MapHeld == map`); unit
  `install_refuses_another_map`, 2 plants seen red, wiring check. `selftest_wreck_reads.py`: PASS 21 units, 23 plants, 7 wirings.
- Bridge tools project compiled against D:\SteamLibrary's RimWorld (0 errors). The companion DLL is not committed.
- Live pass: UNRUN (`work_bundle.py live`): this run is on SteveDesktop; no ArchBig/ArchSmall here, the lane is not reachable
  from here. Filed RIMMANDRAKE_ROUTE_STEVEDESKTOP_BUNDLE_LIVE_PASS_LANE_UNREACHABLE. Command:
  `python.exe src/RimMandrake/bridgetools/prove_wreck_reads.py` (rows install.*), or the lane's proof A1 of
  RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL.
- Nits left in files this run did not change (comment text only): `WreckReadsSelfTest.csproj` and `prove_wreck_reads.py`
  headers still say "four wreck reads" (there are seven).
