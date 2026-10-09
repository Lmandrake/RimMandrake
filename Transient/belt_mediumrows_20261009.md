# Medium rows build log 2026-10-09

- CB-6 CONFIGERRORS: ConfigErrors added to VerminBreeder, ParentalEnrageExt, DrumLure, DungSeeder; builds; shipped names verified present by python scan. No Verse-free selftest possible (needs runtime).
- FL-6 LIQUID_UNIT roundtrip: selftest case added (133/133), contract para 5a in flowworks_mod_definition.md
- SS-5 DUNE_MOVED_EVENT: kernel DepthMoved + RM_DuneEvents.SandMoved + setting announceSandMoved; Stillsand listens (old Harmony hook targeted a method that no longer exists, so singing was silent); fuzz OK
- TB-1/X-4 HAZARD_NATIVE_TAG: RM_HazardNativeExtension + nativeTag on 9 hazard prop classes read by HazardTargeting.Affects; 3 Scald lists replaced by tag; 10 Scald species tagged; validation check can-fail proven. NOT done: folding Channel/Hydrocarbon/River native extensions (they gate currents in other mods, not Affects).
