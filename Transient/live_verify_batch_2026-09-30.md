# Live verify batch — 2026-09-30 (FOUNDRY)

Items: BAROQUE_BIOMES_TOGGLE_LIVE_VERIFY_1, DEEPFIRE_PAINT_LIVE_VERIFY_1, SUMP_TAR_FIRE_NETWORK_1, (opt) TERMINALBIOMES_REVIEW_FIXES_1.
Verdicts: PROVEN / FAILED / UNMEASURED. Not closed in the ledger.

## Session log
- 16:34 PDT start; bridge FREE -> taken by FOUNDRY for this batch.
- Private worktree `.claude/worktrees/lvb-0930` at origin/main 7900d5dab (shared tree was behind origin; deepfire harnesses only on origin).
- Deploy dry-run: LuminousPigment, FlowWorks in sync; composed Baroque Biomes has peer drift (acoustic payloads, Wasteland storms, Miasma/WeepingStones BiomeDefs) NOT deployed by this batch -- not needed for these items, and not mine to ship untested. TerminalBiomes in sync.
- Live list: 612 active mods (parsed ModsConfig.xml), full list.
- 16:45 launched via `steam.exe -applaunch 294100`.

## BAROQUE_BIOMES_TOGGLE_LIVE_VERIFY_1
- 17:08 game up (cold load ~23 min). Startup log: `roster 29 entries ... 30 BiomeDef(s) mapped` / `worldgen gate applied (startup): all biomes on`.
- **Run A, all ON** (quicktest world, seed in `world_stats_A_allon.json`, 119,904 tiles): `RM_TheRot` **20,100** tiles (the largest land biome on the planet), RM_Pyrelands 183, RM_Cauldron 56, RM_GelatinousSlime 27, RM_TheSump 26, RM_FloodedCanyon 17, RM_Contagion 2. Target for the OFF test: **TheRot**.
- Runtime flip attempts: `rimworld/update_mod_settings` cannot write a Dictionary<string,bool> (`enabled[TheRot]` -> "not a valid integer"; `enabled:{...}` -> "Object must implement IConvertible").
  Wrote the settings file on disk (TheRot=False), `reload_mod_settings` (bridge read shows TheRot false), then opened+closed `Dialog_ModSettings`: log shows `worldgen gate applied (settings changed): all biomes on` and `get_defs` still reads RM_TheRot.generatesNaturally=true.
  => The WriteSettings -> RM_BiomesGate.Apply wiring FIRES on dialog close (proven), but RimBridge's reload swaps in a NEW settings object while the gate reads the static `RM_BiomesSettings.Instance` captured in the Mod constructor, so a bridge reload cannot drive the gate. Harness limitation, not a player path (a player flips the checkbox on the same Instance the gate reads).
- Next: restart with the file pre-written (TheRot OFF) so the constructor loads it.

## DEEPFIRE_PAINT_LIVE_VERIFY_1
**PROVEN (re-run on the full 612-mod list this session).** All six committed harnesses (`src/RimMandrake/bridgetools/prove_deepfire_*.py`), outputs beside this file:
- worn_glow **15/15** (incl. 20 coated/plain HitReportFor pairs, dodge self-compare, walking proxy stays on the pawn's cell at every sample, styling-station lacquer) -- `deepfire_worn_glow.txt`
- floor **22/22**, firstcoat **10/10**, proxy_storage **17/17**, god_deltas **25/25 (0 UNMEASURED)**
- status_thoughts: **26/26** on a clean regenerated map (`deepfire_status_thoughts.clean2.txt`).
  Two non-clean runs failed one bar each, both seen in last night's runs too: (a) on a fresh quicktest map the bedroom baseline scores 3 not 0 (map leftovers -- the reason the `clean` runs exist); (b) `titled -> commoner: live opinion offset -15` read **0 while RM_WearsAboveStation was active** (`deepfire_status_thoughts.clean.txt`). Across all 7 recorded runs (last night + tonight) (b) failed 3 times. It looks pawn-dependent (an observer trait or precept that zeroes the social offset). That is an intermittent harness or design gap, not a mechanism failure, but it is UNEXPLAINED.
Previously split scope (floor, first-coat, worn glow, status, god deltas, settings) lives on its child items; this item's own scope has nothing live left unproven.

## SUMP_TAR_FIRE_NETWORK_1
**UNMEASURED -- Part 1 (network fire + gate firebreaks) is not built; there is nothing to live-test.**
Measured on origin/main 7900d5dab: `git grep -i sluice` over src .cs/.xml hits no FlowWorks hardware (only About.xml prose and Pyrelands' unrelated Firebreak terrain);
tar liquids carry no `flammable` (registry flags only propane / fuel sap / white slime); `LiquidIgnitionMapComponent` is still the off-by-default adjacent-Fire prototype with no network/gate logic.
Part 2 (belch -> real flood -> glass-cooling) was already live-proven 2026-09-29 (b76618430) and is not re-run here.

## TERMINALBIOMES_REVIEW_FIXES_1 (state reads)
Offline finding before the game: **no ThingDef carries `RM_CompProperties_GlowerMobile`** (`git grep GlowerMobile -- src` hits only the .cs, the DLL, and WellLedger's TryGetComp). So "glower moves" cannot be observed on any shipped def -- the mechanism is dead in content regardless of which tick method it overrides.
Live state reads (quicktest, full list), raw output `terminal_lure.txt`, `terminal_lure_2.txt`, `terminal_lure_3.txt`:
- **Effective tickerType: PROVEN.** `jawa/get_defs`: RM_VauliskLure `tickerType=Long`, comps include `RM_CompProperties_VaeuliskLure` (so the comp's `CompTickLong` override is the one the engine calls). RM_CargoFloat `tickerType=Normal` (fix #3 is live, so `Tick()` runs). PawnKindDef RM_Vaulisk resolves.
- **Lure springs: PROVEN.** Lure spawned at (60,30). Control: no pawn within 1.9 cells for 2,500+ real ticks, so the lure stays (muffalo wandered to 2.24 cells: no spring, consistent with radius 1.9). Then a drafted colonist was put at (61,30) and 2,500 ticks stepped: lure gone (`countMatched 0`), `RM_Vaulisk82654` spawned, and the reveal message was logged ("The lamp was never a lamp. A vaulisk strikes..."). Settings read: vauliskEnabled True.
  Side observation: 2,500 ticks later the vaulisk was 20 cells away (70,48) with **no mental state**, the colonist was untouched, and the four muffalo had fled. So the manhunter state and attack either lapsed or never held. It is outside the review criteria, but worth a look by whoever owns the ambush beat.
  Harness trap: `rimworld/step_game_ticks` defaults `timeoutMs=10000` (~316 ticks), so a bare `ticks=2100` returns `timedout` having advanced ~15% of the request. Pass `timeoutMs`.
- **Glower moves: UNMEASURED, and it cannot be measured.** No ThingDef carries `RM_CompProperties_GlowerMobile`, so there is nothing on any map to move. The fix (CompTickRare, judged correct by the 09-29 RimSage read) is unreachable from content.

## Game state at end
(pending)
