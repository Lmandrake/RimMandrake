# Ratchet pilot round 3: mods, monitors, deploy order (BENCH plan, 2026-10-14)

Owner, 2026-10-14: *"Please ensure you are deploying all relevant mods into this Ratchet test. There were Bridge items
Foundry completed that might help you monitor the testing environment I believe."*

Written OFFLINE (no bridge, no game, no deploy, no ModsConfig write). Measurements were taken at bench HEAD 1274f7722f.
Repo root: `/home/mandrake/rm/bench` (`D:\Luke\dev\RimMandrake` is the mirror). Round 2 evidence:
`Transient/bench_live_20261014/SITTING.md`.

## 1. Mods

### Verdict

- **Tier change, committed with this plan:** `mandrake.rm.patches` is now in `TIERS["ratchet_pilot"]["want"]`
  (`src/RimMandrake/Utils/modset_builder.py`).
  - Rounds 1 and 2 hand-added it as "ratchet_pilot+patches", and `modcheck record` REFUSED the set as undeclared.
  - It carries `AnimalDessicatedTexPaths_Fix.xml` for Star Wars Animal Collection, which the closure loads. Without it,
    SWAC dessicated texture errors land in the Player.log budget.
  - `--tier ratchet_pilot` (plan only) now resolves to the same 23 mods as round 2's file. The only difference is
    position: rm.patches loads 19th, before rm.weathersuite and rut.patches, instead of 23rd. rut.patches still loads
    after it, as its `loadAfter` wants.
  - Round 3 applies `--tier ratchet_pilot`; no hand edits.
- **No other additions.** Every mod that holds pilot content, or that the pilot mods depend on, is already in the
  tier. Each candidate addition below was checked and rejected, with the reason.
- **No removals.**

### Repo mods relevant to the pilot

Dry runs (`deploy_custom_mods.py --mod <M>` and `--compose biomes`) were measured at 1274f7722f. `+` means a new file,
`~` a changed file, `-` a game-only file (kept).

| mod (packageId) | why it is relevant | in tier | deployed vs HEAD |
|---|---|---|---|
| GimmeSomeSlack (`mandrake.rm.gimmesomeslack`) | Pilot mod. The JawaBench companion's tools TypeLoad-fail without it (MEASURED 2026-10-07). | yes | **in sync** (130 files) |
| FlowWorks (`mandrake.rm.flowworks`) | Pilot mod | yes | **DRIFT** +1 ~6: DLL and srchash, Terrain, ThingDefs, LiquidKits, Keys, new `Patches/Canals/FlowWorks_ClimbAbility.xml`; -8 old result JSONs |
| Baroque Biomes, composed (`mandrake.rm.biomes`) | Holds Pyrelands, the FireEcologyHook DLL, LightningBreaker, FloodedCanyon, EnvironmentalHazards | yes | **DRIFT** +19 ~6: the b020cf6c43 art (dessicated corpses for 6 creatures, barbslinger spike, breaker core and _Off, firefoam sprayer), `FireEcologyHook.dll` and srchash, 4 Pyrelands defs; -1 old Quickgrass png |
| PyrelandsMechanics (`mandrake.rut.pyrelandsmechanics`) | Pilot (the Utinni Pyrelands mechanics: burrow, factions) | yes | **DRIFT** ~2: DLL and srchash |
| UtinniPatches (`mandrake.rut.patches`) | `WildAnimals_Pyrelands.xml` (the Pyrelands cast); PyrelandsMechanics hard-depends on it | yes | **DRIFT** ~13: BiomeDefs and WildAnimals for other biomes. Deploy anyway (one HEAD). |
| SWBestiary (`mandrake.rsw.swbestiary`) | 7 RSW_ Pyrelands animals; without it GenStep_Animals NREs (tier note) | yes | **DRIFT** +13: Tauntaun, Tibidee, Vapaad, DonorPack_W2a, spit icons, dessicated pngs |
| LuminousPigment (`mandrake.rm.luminouspigment`) | FlowWorks liquids consumer (glow tank); a hard dependency of biomes | yes | **in sync** (32) |
| WeatherSuite (`mandrake.rm.weathersuite`) | A hard dependency of rut.patches | yes | **in sync** (9) |
| MandrakePatches (`mandrake.rm.patches`) | SWAC texture-path fix | yes (now declared) | **in sync** (21) |
| JawaBench companion (not a mod: `<RimWorld>\BridgeTools\JawaBench\`) | The monitors (section 2) | n/a | **STALE.** It is the 28247cdeff build, without b59c434462's `jawa/health` and `jawa/health_profile`, so `selftest_tool_metadata` fails until it is rebuilt. |

### Candidates checked and kept OUT

- **ExplosiveGrowth (`mandrake.rm.explosivegrowth`): OUT for round 3.**
  - **It is a real FlowWorks consumer.** `RM_SoakSources.PulseIrrigation` reads FlowWorks through the shared
    `src/RimMandrake/_Shared/FlowWorksIrrigation/FlowWorksIrrigationRead.cs`. That file reflects
    `RM_MapComponent_Excavation.depthGrid`, `.fillGrid` and `.ActiveFluid`, and all three still exist at HEAD
    (`RM_MapComponent_Excavation.cs:48`, `:51`, `:317`).
  - **Its DLL is source-current.** The srchash line for the shared file equals today's sha256 (4c402b74…).
  - **The pond hollow (acfae20df4) cannot break it.** A natural bed is read by `NaturalBedDepthAt`, not
    `depthGrid`. EG only ever soaks DUG cells, and that is the BUILT behaviour.
  - **Its only other soft reference** is `TypeByName("RimMandrake.EnvironmentalHazards.RM_MapComponent_GradientAxis")`,
    which is a reflection read inside composed biomes. Its About.xml hard-depends on Harmony only. It does **not** drag
    in RimUtinni PlantGrowth (only the older `explosivegrowth` tier does) or FloodedCanyon (already in via biomes).
  - **Why it stays out anyway:** its Harmony postfix multiplies `Plant.GrowthRate` on soaked cells, and weather soak is
    on by default. The Pyrelands rows that measure plant growth (scorchfruit, embergrass_regrow,
    ash_fertile_when_watered) would carry a second mod's multiplier, so a PASS or FAIL would no longer be Pyrelands'
    alone. That breaks the pilot's blame isolation.
  - **It has no row to run here.** Its north-star script (`EXPLOSIVE_GROWTH_FIRST_SCRIPT_1`) has no irrigation row:
    `irrigationSoakEnabled` appears only in the toggle tables, marked "needs FlowWorks". It is written for the
    `explosivegrowth_solo` tier. No live run is recorded for it, and its deployed copy is stale (DLL ~2).
  - **Recommendation:** run its first live sitting on `explosivegrowth_solo`. Then file a FlowWorks irrigation smoke
    row (a dug cell holding RM_Fluid_Water, then a soaked plant with rate ratio > 1) for a later "pilot + consumers"
    round. It does not belong in this exit-criterion run.
- **Salvation Rites (`mandrake.rut.rites`) and the Struck Glass rite: OUT.**
  `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1` is unbuilt (no "struck glass" def anywhere in src/). The rites mod
  hard-depends on `mandrake.rut.antiquities` and is campaign tier. Nothing in the pilot reads it.
- **AshkarrWeatherSuite (`mandrake.rut.weathersuite`): OUT.** It adds campaign folk-sign letters on Pyrelands weather.
  Those letters would be noise on the site, and no row reads them.
- **Watchers, StructureInjectionsSW, PawnFlavor, WildsteamEggBounty: OUT.**
  - Their Pyrelands mentions are comments or prose: a think-tree priority note, a tile mutator list, backstory text,
    and a faction lookup.
  - None of them is read by a pilot row.
- **Other FlowWorks dependents: OUT.**
  - Consumers outside biomes, by `loadAfter` only: Bazaar, ExplosiveKnockback, KineticArms, Bacta, Armoury,
    StarWarsRaces.
  - TerminalBiomes, TheForge, TheSump, Stillsand, LongShade, Warscar and Miasma are already loaded, folded into
    biomes.
  - Each of the outside consumers adds a mod with no pilot row.

### Findings from the audit (not tier changes; file them)

- **FlowWorks scatter GenSteps never load.** `src/RimMandrake/FlowWorks/Defs/Machinery/RM_LiquidWorksScatter.xml`
  guards 4 GenStepDefs (DesalPlant and the other liquid-works ruins) with `MayRequire="mandrake.rm.environmentalhazards"`.
  - That packageId is folded into `mandrake.rm.biomes` (compose: "30 folded packageId(s) dropped from every list"), and
    the compose step does not rewrite MayRequire.
  - So the liquid-works ruins never scatter on any list. The engine logs nothing for this.
  - The fix is to guard on `mandrake.rm.biomes`. This is FOUNDRY work, and it touches nothing in the pilot rows.
- **Same class in UtinniPatches:** `Defs/BiomeDefs/RUT_Webwork.xml:158` has
  `<RM_Ollathrix MayRequire="mandrake.rm.webwork">` (webwork is folded). It is not a pilot biome.

## 2. Monitors

The deployed DLL was measured for UTF-16 and UTF-8 tool names. Every tool below is in the deployed companion
**except `jawa/health` and `jawa/health_profile`**. All bridge calls use `rimbridge_client.RimBridge(...).call(tool, {...})`,
the pattern in `Transient/bench_live_20261014/menu_probe.py`.

| tool | watches | source | deployed | round 3 use |
|---|---|---|---|---|
| `jawa/companion_handshake` | which profile (test or campaign), tools loaded, prefixes installed | `JawaBenchCompanionSafety.cs:270` | yes | First call after READY. The test profile expires **2026-10-15T12:00Z**: renew it if round 3 runs past that. |
| **`jawa/health`** (b59c434462) | frame-interval histogram (`tps.frame-hist`), GC coincidence on gaps of 250 ms or more, log counts and the Verse.Log cap state, bridge occupancy and queue delay, capability inventory | `JawaBenchHealthTools.cs:23` | **NO** | After the rebuild: `{"action":"arm","minutes":240}` once at READY. `{"action":"status","sinceMinutes":N}` after each suite, saved as `health_<suite>.json`. `{"action":"disarm"}` at teardown. Read the `cost` field: that **is** the live proof and cost owed by `HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP`. If C1 GSS wall time rises more than 10% over round 2's 392 s, `switch metric=tps.frame-hist on=false` and note it. |
| **`jawa/health_profile`** | method timing on an exact allowlist; preset `own` covers our map-component ticks | `JawaBenchHealthTools.cs:120` | **NO** | One window only, during the Pyrelands pieces: `{"action":"start","preset":"own","minutes":10}`, then `{"action":"status"}`, saved as `profile_pyre.json`. Test profile only. It expires on its own. |
| `jawa/vitals` | pawn deaths, downs and mental states with tombstones, the clock ledger, stuck modals, GameEnded, specimens | `JawaBenchVitalsTools.cs:21` | yes | Auto-armed by every `jawa/safe_advance`, and `validation_core` waits already go through safe_advance (WATCH_WAIT_WIRE_SMALL_STEPS). Explicitly, for row C3: `{"action":"arm","ttlMin":120,"critical":"<colonist ids>","row":"pyre"}`, then `{"action":"events","sinceSeq":N}` after each piece. Round 2's `TESTENV_WILD_DOWNED_REPAIR_STOPS_CLOCK` (a wild animal downed mid-advance) is exactly what its events show. |
| `jawa/safe_advance` | chunked stepping that stops on the vitals latch | `JawaBenchVitalsTools.cs:150` | yes | Already in use. Never use raw `step_game_ticks` in ad hoc probes. Any wait over 30000 ticks on a populated map needs `timeException=true`. A teardown reads `aborted map_gone:`, which is expected (round 2). |
| `modcheck/governor.py` (`RowGovernor`) | each row's outcome from the vitals latch (PASS, FAIL, RESTART, UNMEASURED) | `src/RimMandrake/Utils/modcheck/governor.py:220` | Python | For ad hoc worklist probes (not the three suites): `G.RowGovernor(session).arm()`, then `.advance()` and check. `env_item_lines()` prints the TESTENV items to file. |
| `jawa/quiet_site` and `modcheck/quiet_site.py` | threat structures, proximity letters, storyteller and wild spawner | `JawaBenchQuietSiteTools.cs:30` | yes | Already wired into the site builders. Call `{"action":"status"}` after each fixture reload; re-apply storyteller-off after any load. |
| `jawa/telemetry_tier` and `jawa/telemetry_mark` | 1 s TPS windows, `exc` before the 10k cap, bridge occupancy, a flight ring dumped on a tick over 250 ms | `JawaBenchTpsTierTools.cs:17,44` | yes | `{"tier":"test","ttl_min":240,"why":"ratchet round 3"}` at READY. `telemetry_mark` (`{"dump":true}`) at each suite start and end. `{"tier":"campaign"}` at teardown. |
| `jawa/tps_report` and `tps_record.py` | the always-on sampler | `JawaBenchTpsSampler.cs` | yes | Offline after the round: `python3 src/RimMandrake/Utils/tps_record.py --at "<start>" --span 3h --health` |
| `health_observer.py` (external) | game CPU, memory, Player.log growth and rotation, startup milestones; 0.30% of one core | `src/RimMandrake/Utils/health_observer.py` | Python | Start before launch: `python.exe src/RimMandrake/Utils/health_observer.py --for 14400` (Windows python, cwd the copy). Read with `python3 src/RimMandrake/Utils/health_observer.py --read --last 50`. Not a standing task (MUST 17 C1): run by hand and stop at teardown. |
| `telemetry` CLI | recorded TPS, health, bridge calls and deploy history | `src/RimMandrake/Utils/telemetry/cli.py` | Python (python.exe) | `telemetry health` before launch (is the daemon up?), then `telemetry around deploy:<id>` and `telemetry bridge --since 3h` at debrief |
| Bridge concurrency guard | refuses `go_to_main_menu` while another pid is mid-call | `src/RimMandrake/Utils/bridge_concurrency_guard.py` | auto | Automatic through `rimbridge_client`. It is blind under WSL (no call log), so run the drivers with **python.exe** for it to bite. |
| `LogTap` | warn and error journal per run, and whether entries were lost | `src/RimMandrake/Utils/validation_core.py:169` | Python | Already in the suites. A row whose budget shows `lost > 0` is not evidence. |
| `jawa/awareness`, `jawa/pawn_origin`, `jawa/thing_explain` | incident journal, where a pawn came from | `JawaBenchAwarenessTools.cs:42` | yes | Arm only to diagnose a surprise visitor or animal: `{"action":"arm"}` (TTL 30 min). The incident journal costs about 2.8 ms per call. |

Other FOUNDRY and BENCH items completed in the last 5 days that are already in the deployed DLL:
`BRIDGE_TPS_REGULAR_REPORT_1`, `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS`, `COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT`,
`COMPANION_HANDSHAKE_BUILD_SAY_WHAT_LOADED`, `BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD`,
`BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN`, `BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID`,
`LAUNCHER_READY_HARDEN_OLD_LOG_LINES_LIE`, `BRIDGE_KILL_HOSTILES_TOOL_1`, `TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO`,
and `MAP_DROP_DIAGNOSE_MENU_MIDRUN_GHOST`, which is the concurrency guard. The offline `health_forensics.py`
(`save-census <.rws>`) can census the site fixture saves before they are loaded.

## 3. Round 3 deploy list (driver, after tonight's builders land; game DOWN, bridge held)

**The one-HEAD rule** (`design/RimMandrake/ratchet_workflow_and_token_burst_design_2026-10-11.md` §exit criterion): every
mod and the companion come from ONE commit.
- Take `git rev-parse HEAD` once and `git archive` it to ext4. Deploy, build and run the suites all from that export.
- Record the sha in SITTING.md. A fix that lands mid-round means a new round, never a partial redeploy.
- Do not use a python-only scratch copy for the suites. Round 1 and round 2 both lost runs to a copy missing
  `Biomes.compose.json`, `src/Directory.Build.*` or Textures. The Windows-side copy must be the WHOLE export.

1. `modset_builder.py --tier ratchet_pilot` (plan), then `--apply`. Confirm 23 mods, rm.patches included.
2. `deploy_custom_mods.py --mod GimmeSomeSlack`. In sync at 1274f7722f; re-plan at the round's HEAD.
3. `--mod FlowWorks` (plan, then `--apply`)
4. `--mod LuminousPigment`
5. `--mod WeatherSuite`
6. `--mod MandrakePatches`
7. `--compose biomes` (Pyrelands, FireEcologyHook, the b020cf6c43 art)
8. `--mod SWBestiary`
9. `--mod UtinniPatches`
10. `--mod PyrelandsMechanics`
11. **Companion:** `python3 src/RimMandrake/bridgetools/build.py --gm` (plan), then `--gm --apply`.
    - It refuses while RimWorld runs, and it refuses tool removal.
    - Then run `selftest_tool_metadata.py`. It must pass once the artifact carries the health tools.
    - The census after READY should be 396 + 2 (`jawa/health`, `jawa/health_profile`).

After every `--apply`: re-run the plan, which must read "Everything in sync". Then run
`dll_source_stamp.py check` for FlowWorks, FireEcologyHook and PyrelandsMechanics, which must MATCH. `-` lines are
kept, not pruned. Then launch via Steam, wait for READY, and make the section 2 arming calls before C1.
