# Night C# review 2026-10-09 (BENCH, owner asleep)

Commits: 66ead45fb, 33846bde3, 6c08832b8. Full-file reads; engine facts from RimSage (decompiled 1.6).

## src/RimUtinni/EmpirePursuit/Source/AnomalySuppression.cs — CLEAN
- Prefix on static `GenStep_Monolith.GenerateMonolith(IntVec3, Map)`; that is the ONLY monolith spawn at map gen —
  both callers (GenStep_Monolith.ScatterAt and ScenPart_MonolithGeneration.PostMapGenerate) route through it.
  GameComponent_Anomaly.TriggerVoidAwakening's own spawn is unreachable without a monolith.
- Scenario match: ScenarioDef.PostLoad fills scenario.name from label, so the name fallback works on the
  copied game Scenario. Prepare() guards a renamed target. No findings.
- Judgement (not a bug): no Mod Settings toggle for this suppression (CLAUDE.md "every mod ships Mod Settings").
  A data-only alternative also exists: ScenPart_MonolithGeneration with method Disabled.

## src/RimMandrake/TerminalBiomes/Source/RM_TwilightFloraBehaviour.cs — FIXED, not marked clean
1. HIGH (fixed): RM_CompWiltAboveGlow dealt lethal Rotting damage inside CompTickLong. Plant.TickLong calls
   base.TickLong() (comps) and then reads base.Map -> PlantUtility.GrowthSeasonNow(pos, null) -> NRE. Every
   murkspindle that wilts to death under a well logs a red "Exception ticking" error. Fix: the comp never deals
   the killing blow; a new RM_MapComponent_DeferredPlantKill (same file, unsaved queue) kills it on the next map tick.
2. LOW (judgement): gloamurn on the RM_SeabedFloor_TwilightSea map can never charge (the well ledger only runs on
   RM_TwilightSea), so it is permanently dark there. IsTwilightFloor() admits both biomes for the genstep.
3. LOW: `charging` is not scribed — inspect line reads "dark" for up to one long tick after load. Cosmetic.
- Checked OK: CompGlower consults comps implementing IThingGlower (Verse/CompGlower.ShouldBeLitNow); glower state
  restored on load from scribed `discharging`; GroundGlowAt(c, ignoreCavePlants, ignoreSky) arg order correct;
  hosts/defs RM_HoolimbrePlant, RM_NoothelmPlant, RM_LampBladder, RM_Skylight exist; genstep order 905 > Plants 900.
- Same latent pattern elsewhere (not reviewed tonight): RM_CompScriptedDieOff.DieNow (EnvironmentalHazards) kills a
  plant from CompTickLong — likely the same NRE.

## src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_WellLedger.cs — CLEAN (whole file read)
- Opened() runs before the well joins `wells`; Closed() before removal — the "others" list correctly excludes it.
- Flora hooks only fire where the ledger is active (RM_TwilightSea + settings). No Scribe gaps.
- Minor perf (pre-existing): MaybeFireWarningLetter scans all things every 250 ticks per waning well until it fires.

## src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs — diff reviewed only, NOT marked clean
- Tonight's diffs (3 toggles, Scribe defaults true = shipped behaviour, UI labels) are correct. File has 5 other
  commits since its clean mark (fe6140ff4); a full-file pass is owed before it can be marked clean.

## src/RimMandrake/TerminalBiomes/Source/RM_ScaldThurlspongeWrecks.cs — CLEAN
- Biome extraGenSteps are merged then sorted by order (MapGenerator.GenerateContentsIntoMap), so 966 runs after 965.
- Judgement: thurlsponge's wildTerrainTags are RM_SeaFloorGround (deep floor) but this step plants it on
  RUT_ScaldShallow beside surface wrecks — matches the design line, flagged only as a habitat inconsistency.

## Selftests
run_selftests: 280 pass, 1 FAIL — selftest_utinnipatches_dump.py (shipped UtinniPatches defs vs def dump), which
these C# commits do not touch.
