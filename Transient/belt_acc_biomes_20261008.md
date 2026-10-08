# FOUNDRY acc_biomes acceptance sitting 2026-10-08
Bridge: FOUNDRY. Game UP on tier acc_biomes (15 mods) launched 21:40 via Steam. Tool: python.exe from repo root.

## Milestones
- 21:41 start. belt_watchdog reports DEAD for a STALE situational_rerun heartbeat (39h old, a prior runner), not the game; `./game` measures RUNNING, bridge answers. Not killing anything.

## Results (item criterion verdict)

## Skipped (needs a different tier)
- 21:50 L1 done: 6 verifies recorded (2 pass->validated/done, 4 partial), 5 findings filed so far; L2 driver Transient/acc_biomes/run_live_suite.py runs modcheck suites on the live tier with no ModsConfig swap. Ran FloodedCanyon RustCathedral Stillsand Greentide.
- 22:15 Wasteland re-run on a real RM_Wasteland map via retile.py: pass A2/A3 GPT, fail MECHANICS A3, finding WASTELAND_TOXIC_BUILDUP_NEVER_APPLIES_1
- 22:35 Ran live (no ModsConfig swap) modcheck suites on acc_biomes-15: FloodedCanyon RustCathedral Stillsand Greentide TheForge Cauldron Wasteland(x2) Wreckage LeaningScrub Webwork Scarlands CreatureBehaviors TheSump Contagion GelatinousSlime Miasma LongShade EnvironmentalHazards; traction-lance gauntlet via static_call. Results in Transient/modcheck/*_20261008*.
- Skipped (different tier): MOD_OPTIONS_RETROFIT_1 (full list), JAWA_SWIM_HOOD_KEEP_1, MOVING_DUNES_BUILD_1, EMPIRE_ESCALATION_LADDER_1, KINETIC_BLAST_WEAPONS_1, WEEPINGSTONES C6, RUSTCATHEDRAL A4 (needs swbestiary), LIVE_ROUND2 A3 (WhisperSarlaccSign genstep needs its biome map), flowworks/bacta/droidworks/harness items, items needing new probes (pits, hoist, vault thaw...).
- No unattended flyer tests done.
