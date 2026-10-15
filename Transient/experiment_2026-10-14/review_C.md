# Review C -- Pyrelands (ratchet pilot criterion 5)

BENCH reviewer, 2026-10-15. Every file: reachability checked, then a FULL-FILE read (no diff-scoped reviews), re-read after edits, then mark-clean.

Reachability: Defs/Patches load via the composed mandrake.rm.biomes (Biomes.compose.json); validate_patch over the mod root with --defs (550-mod load set): 0 errors. C#: 6 files in FireEcologyHook.csproj, PyrelandsFuzz.cs in SelfTest/Fuzz csproj (run by Utils/selftest_pyrelands_fuzz.py). Python: northstar_plan (driver plan), northstar_site/preflight (CLI, imported by plan/selftest), selftest_pyrelands_site (runner), validation (modcheck suite).

| file | reachable | findings | verdict |
|---|---|---|---|
| `src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Defs/LightningBreaker/RM_LightningBreaker.xml` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Defs/TerrainDefs/AshField.xml` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Defs/TerrainDefs/ScorchableGround.xml` | yes | stale comment (wired by RimUtinni Fire Ecology) corrected | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Defs/ThingDefs_Ash/Filth_LooseAsh.xml` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Defs/ThingDefs_Plants/EmberGrass.xml` | yes | comments described a graphicData colour tint that no longer exists; removed | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Defs/ThingDefs_Plants/Quickgrass.xml` | yes | comment called the stage selector 'owed'; it ships; corrected | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_Emberscythe.xml` | yes | stale RotSporeKit home/settings notes corrected | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_PyrelandsPortedFauna.xml` | yes | stale UtinniPatches/RotSporeKit notes; false 'no donor leatherDef' claim (Leather_Chitin, field-level MayRequire, honoured per DirectXmlToObject.cs:212) corrected | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_Ullai.xml` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Defs/ThingDefs_Sprayer/FirefoamSprayer.xml` | yes | DEFECT: weaponTags Gun/SimpleGun (+ inherited Gun) let pirate/outlander/mercenary/Empire kinds spawn armed with a harmless extinguisher; now Inherit=False own tag | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Defs/WeatherDefs/AshFall.xml` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Patches/RM_AcousticPayload_Pyrelands.xml` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs` | yes | stale 'ships in RimStarWars tier' comment; DLL rebuilt | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Source/Kernel/RM_BurnKernel.cs` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Source/Kernel/RM_FireEcoKernel.cs` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Source/MapComponent_BurnLine.cs` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Source/RM_JobGiver_BurrowOnFire.cs` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Source/RM_PyrelandsGiants.cs` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/Source/SelfTest/Fuzz/PyrelandsFuzz.cs` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/northstar_plan.py` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/northstar_site.py` | yes | none | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/preflight_pyrelands.py` | yes | DEFECT: gate C released the bridge via Windows python with no AGENT_SEAT (release could not act); now WSL as the seat. log_birth fallback comment corrected | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/selftest_pyrelands_site.py` | yes | vacuous checks (gate C 'PASS or FAIL'; burn_line registration via text grep) made real; new restore-via-session test | CLEAN (full review) |
| `src/RimMandrake/Pyrelands/validation.py` | yes | DEFECT: _restore_terrain (fulgurite sand patch) used t.bridge_call in a finally, a no-op after FAIL/UNMEASURED: half the map stayed sand for later chains; now via session, refusals -> chain teardown FAIL. Stale docstring (animal manifest) corrected | CLEAN (full review) |

## Checks run
- winbuild FireEcologyHook.csproj: 0 warnings/errors; DLL+.srchash committed.
- run_selftests --only selftest_pyrelands_fuzz, selftest_pyrelands_lint, selftest_pyrelands_site: GREEN.
- DEFAULTS in preflight == RM_PyrelandsSettings initialisers (scripted compare).
- Static per-game state: rolledFiresByMap (ConditionalWeakTable per Map), lastBurrowNudge/lastBurrowTimeout (per MapComponent): no session-wide tables keyed by thing id.

## Commits
ec183c5753 (XML), aba03b5f82 (C#), f251c81067 + eea5a1cd03 (Python).

No live checks needed: every fix is proven offline (selftests pin the two harness fixes; weaponTags is def data).
