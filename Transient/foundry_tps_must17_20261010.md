# TPS MUST17 full-list run 2026-10-10

## status
started Sat Oct 10 09:49:23 PDT 2026

## steps
- 16:4xZ bridge taken (FOUNDRY). Added GM-only `jawa/tps_test_attribution` (a5bc4db4a) for in-session timer A/B; build.py --gm --apply deployed (game down).
- live list was 67 (PRESWAP.20261010_082925 archive); restored FULL.LATEST = 551 active (md5 1ab545a0...).
- 16:51:06Z Steam launch (launch_and_wait.sh); log truncated at +2 s; cold load in progress.
- fixed `./game` modlist guard (always warned NOT FULL: modlist_swap.py not executable) b917cee72.
- tps_observer.py (b80aaf3a7): standing observer; Windows python pass OK, probe found game pid 35524 start 16:51:08.010Z.
- 17:03/17:06Z belt_watchdog: tps STALE (loading, expected); overall DEAD is the 99h-old situational_rerun runner heartbeat, not this run - not acted on.
- 17:2xZ FULL-LIST LOAD FAILED (~33 min): `Caught exception while loading play data` - NRE in MinifyEverything.GenerateImpliedDefsPostfix
  (a ThingDefCountClass with null thingDef: some costList names a def that does not exist; silent cross-ref mode logs nothing).
  RimWorld reset ModsConfig to 6 (Core+DLC) and "could not recover". Game killed; FULL.LATEST (551) restored to ModsConfig.
- Diagnosis filed as FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO (MinifyEverything Mass-from-costList Sum hits a null costList thingDef; XML costList scan of all 551 mods finds no ghost -> a patch or C# builds it).
- MUST 17 on the full list is BLOCKED by that. Fallback for partial evidence: restored the 67-mod list that was live before this run (PRESWAP.20261010_082925) and relaunching.
- 17:41-17:48Z quicktest on 67-list (RM_TheRot, 250x250): Normal 45s, Fast 45s, Superfast with attribution on/off/on/off/on 60 s legs. From 10:42:28 local a map component took 93-96% of tick time: TPS ~17 at every speed (ratio 0.05 at Superfast); sustained LOW judged.

## results
- (1) full-list cold load: FAILED (FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO). Live list returned to the 67-mod PRESWAP list.
- (2) autostart, no bridge call: PASS on the 67-mod list (session 2cc9627c, `startedBy bridge-registration`, sampler+attribution complete, menu row, heartbeat). Full list: OWED.
- (3) overhead, in-session ABAB (`jawa/tps_test_attribution`), Superfast, sim-bound map (~54 ms/tick):
  on 17.69 / 18.65 / 17.61 TPS, off 17.19 / 17.25 TPS -> timer cost not measurable (noise ~+-4 %).
  Profiler estimate: 10 timer pairs/tick, 0.0004 ms/tick (< 0.01 % of tick time). Sampler-off and no-attribution-patched
  configs (restarts) UNMEASURED; light-tick and full-list workloads UNMEASURED.
- (4) mixed speeds: ratios sensible (Normal 0.95 until a map component took 93-96 % of tick time -> ~17 TPS at every speed,
  `SUSTAINED LOW`, 0 incidents). Filed ROT_MAPCOMP_HUNT_FORTY_SEVEN_MS.
- (5) belt_watchdog `tps` line: WARN SUSTAINED LOW reported correctly. Standing observer: tps_observer.py + Windows task
  `RimMandrake\TPS Observer` (pythonw, every 2 min), `observer_last.json` confirms passes (games probed with start time).
- (6) no `rimflow verify`: C4 needs the full list; nothing there proven.
- Game left UP on the 67-mod list, quicktest map paused; bridge released.
