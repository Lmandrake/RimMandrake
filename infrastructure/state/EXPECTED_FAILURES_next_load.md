# Expected-failure signatures — consolidation proof load, 2026-09-08 (BENCH)
Written BEFORE launch per load-round §3. Seven changed/moved assemblies ride
this load (the sprint waiver: all are relocations/rebuilds, not new code).
Each fails in a distinguishable place:
1. RimMandrakeProperty.dll (merged) — TypeLoadException or XML "Could not find
   class" naming RimMandrake.Property / .TheftHauler / .SalvageClaim types.
2. SWBestiary carried DLLs (RimMandrakeLivestockRSW, JawaIkee) — "Could not
   find class" naming CompLightAversion or ThoughtWorker_IkeeNearby.
3. WeatherSuiteHook.dll — errors naming WeatherSuiteHook or RM_WS_ defs.
4. FireEcologyHook.dll (Pyrelands) — errors naming FireEcologyHook or RM_FE_.
5. RiverSteamHook.dll (ManyWaters) — errors naming RiverSteamHook.
6. DesertVehicleReskin.dll (tier move) — errors naming RM_DraughtFuelExtension.
7. Droidworks.dll (FOUNDRY ModulePersonality rebuild, swept commit 0f7da95c) —
   errors naming CompModulePersonality.
LOAD DECISION STRINGS: expected-present "Bridge token:" + 590 active;
expected-absent-above-baseline: "^Config error in", "Could not resolve
cross-reference", duplicate defName, "Recovered from incompatible".
