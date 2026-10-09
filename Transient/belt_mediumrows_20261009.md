# Medium rows build log 2026-10-09

- CB-6 CONFIGERRORS: ConfigErrors added to VerminBreeder, ParentalEnrageExt, DrumLure, DungSeeder; builds; shipped names verified present by python scan. No Verse-free selftest possible (needs runtime).
- FL-6 LIQUID_UNIT roundtrip: selftest case added (133/133), contract para 5a in flowworks_mod_definition.md
- SS-5 DUNE_MOVED_EVENT: kernel DepthMoved + RM_DuneEvents.SandMoved + setting announceSandMoved; Stillsand listens (old Harmony hook targeted a method that no longer exists, so singing was silent); fuzz OK
- TB-1/X-4 HAZARD_NATIVE_TAG: RM_HazardNativeExtension + nativeTag on 9 hazard prop classes read by HazardTargeting.Affects; 3 Scald lists replaced by tag; 10 Scald species tagged; validation check can-fail proven. NOT done: folding Channel/Hydrocarbon/River native extensions (they gate currents in other mods, not Affects).
- EH-4 ENVHAZARDS_HAZARD_CLOCK_READOUTS: venom stand inspect line + Alert_VenomContactClock + hazardClockReadoutsEnabled. NOT done: tar beast wake has no clock (event-driven), wet-bulb is not in EH (Greentide XML), warm ground has no thing to hover.
- LP-5 LUMINOUS_PIGMENT_SETTINGS_READOUTS: reset-per-section for all 8 headings (71 fields, defaults snapshotted in static ctor), steer odds at skill 6/12/20, plain-dish family odds, mat life in hours. NOT done: 'hours of light per coat' (no such timer exists; coat lights are permanent).
- LP-9 DEEPFIRE_HEALTH_CHECK: MapComponent_DeepfireLights.Health() + 'Health: report' debug action + health_clean chain (selftest ALL OK). 'Failed paint eats no pigment' is not a light-book invariant, not covered.
- SC-5 SCARLANDS_RELOAD_MIDSTATE: RELOAD_STEPS (5 rows) + reload_midstate chain + static member-existence check (can-fail shown). Unrun live: scenes must be arranged by the sitting; ring-parts read is count-based (no carried-stack reader exists).
