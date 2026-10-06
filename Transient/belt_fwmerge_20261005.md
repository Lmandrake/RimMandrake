# FlowWorks <- RiverWorks merge (2026-10-05)

Owner 2026-10-05, typed: "I think river works needs to be part of flow works."

## Status
- skeleton written
- moved + rewired; TB builds; FlowWorks built from scratch clone (0 errors), C# SelfTest 86/86, run_selftests 183/184 (selftest_human_review KeyError under parallel run only; passes alone, peer is editing human_review.py), walklint clean, doctor: no river orphans

## Inventory

## Moved
Source/*.cs -> FlowWorks/Source/Rivers/ (ns RimMandrake.FlowWorks.Rivers; RM_RiverWorksMod.cs -> RM_RiversSettings.cs, a static
section scribed by RimMandrakeFlowWorksSettings.ExposeData and drawn by its window; view height 5400 -> 7400);
Defs/* -> FlowWorks/Defs/Rivers/; Patches -> FlowWorks/Patches/Rivers/; Textures -> Textures/Things/Building/FlowWorks/Rivers/
(art tool move_mod_textures.py: 4 installed, 4 retired); selftest_riverworks.py -> FlowWorks/selftest_flowworks_rivers.py;
validation.py -> FlowWorks/northstar/extensions_rivers.py (suite FlowWorksRivers); walk RiverWorks.md -> FlowWorksRivers.md
(subject FlowWorks, feature: rivers). Harmony id mandrake.rm.flowworks.rivers. Deleted: About, csproj, DLL+srchash.

## Settings keys added (for site_spec owner)
NOT added to RimMandrakeFlowWorksSettings' class body, so site_spec SETTINGS parity is unaffected. They live in
static class RimMandrake.FlowWorks.Rivers.RM_RiversSettings (Source/Rivers/RM_RiversSettings.cs), scribed into the
SAME settings file (RimMandrakeFlowWorksMod) — 40 keys, none collide (selftest_flowworks_rivers.py checks):
bools (22): riverWorksEnabled surfaceCurrentEnabled scaleWithRiverSize floodSurgeEnabled countSeasonalFloods
countTorrentialRainFloods carryAnimals carryStrangers carryItems washOffMapEdge pathfinderAvoidsCurrents
crossingHazardsEnabled fordsEnabled bankWorksEnabled breachEnabled stakeLineLevee weirCatchesFish weirCatchesDrift
breachWashesCatch siltRichening ferryEnabled ferryRopeGuidesColonists(new)
numbers (18): currentStrength centreTicksPerCell marginTicksPerCell itemDriftFactor washedAwayMinDays washedAwayMaxDays
bruiseChancePerStep dropChancePerStep wearRateMultiplier breachHpFraction stakeSnapTicksPerCell weirPoolLength
weirCatchIntervalHours weirHeldCatchCap weirDriftChance breachWashCells siltIntervalDays ferryMaxSpan
To register in site_spec: add "RimMandrake.FlowWorks.Rivers.RM_RiversSettings": {...} to SETTINGS and
"...RM_RiversSettings": os.path.join("Rivers","RM_RiversSettings.cs") to SETTINGS_SOURCES (MOD_CLASSES unchanged).
To register the suite in FlowWorks/validation.py (append-only, after the EXT chains loop):
    import extensions_rivers as RIV
    suite.toggles += [t for t in RIV.suite.toggles if t not in suite.toggles]
    suite.chains += RIV.suite.chains

## Still in TerminalBiomes and why
Sea current (RM_MapComponent_ChannelCurrent), undersurge, sink, cargo float/harness, Twilight channel genstep (spawns
the FlowWorks weir 1x2 + stakes), RM_BankSilt terrains + RM_SiltTrap_SeaSwap.xml patch (adds the sea pair to the
trap's swap table), its biome toggles. All sea-only content; TerminalBiomes -> FlowWorks is a hard dependency
(About + assembly reference RimMandrakeFlowWorks.dll), FlowWorks never references TerminalBiomes.

## References fixed
TerminalBiomes About (riverworks dep + loadAfter removed), csproj Reference -> FlowWorks DLL, 4 .cs + patch xpath Class
names, comments; FlowWorks About (Rivers paragraph, Odyssey loadAfter, stale "Harmony for one patch" sentence fixed);
human_review.py L09-L13 probes; required_checks.json RiverWorks row removed (modcheck status had no RiverWorks key:
forget-key said "nothing to forget"); 3 design docs; flowworks_remaining rows 12/13. Not referenced: modset_builder,
modlists snapshots, deploy_custom_mods, live ModsConfig (rm.riverworks was never active). Ledger shards untouched
(append-only). code_review: no records at new paths -> DIRTY. FlowWorks_review.html (generated) left for its owner
to regenerate.

## Taken-over items
- levee flood check: ProofLevee (vanilla SeasonalFlood asked CanFloodSpreadInto on a stake vs a gap; off side) +
  component levee_holds_and_gap_leaks.
- order-stake breaks (breach.cascade_order): ProofCascadeOrder + weir CascadeTickFor accessor; component breach_cascade_order.
- ferry rope for undrafted colonists: RM_RopePathing Harmony postfix on PerceptualSource.ComputeAll/UpdateIncrementally
  zeroes costUndrafted on rope cells; component notifies the path grid on rope/setting change; new toggle
  ferryRopeGuidesColonists; ProofFerryPath + component ferry_rope_undrafted.
- NEW ROWS NEEDED list: all 8 rows exist in extensions_rivers.py chain "works" (+3 above); weir.biome_drift still
  only reported (driftRolls), sea.unchanged stays TerminalBiomes'.
- sluice box + panning: BLOCKED — rivers-carry column has 0/37 owner-approved rows and no registry loader
  (MINERALS_WHERE_THEY_BELONG_1).

## Owed
- Game Mods folder: C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\RiverWorks still deployed (inactive in
  ModsConfig, so harmless); deploy_custom_mods.py cannot delete a whole retired folder. Remove it and redeploy FlowWorks +
  TerminalBiomes (`deploy_custom_mods.py --mod FlowWorks --mod TerminalBiomes --apply --prune`) once the liquid-machinery
  peer's uncommitted FlowWorks Defs land (deploying now would ship their half-done work). Bridge was FREE, game down.
- FlowWorks DLL was built from HEAD + this merge only (scratch shared clone), because the peer's uncommitted
  Source/Machinery breaks the build; the peer's next FlowWorks build includes Rivers automatically.
- Register extensions_rivers in FlowWorks/validation.py and RM_RiversSettings in site_spec (lines above) — owners of those files.
- FlowWorks_review.html is generated from human_review.py; regenerate when its owner next runs it.
- Live verify (bridge, river quicktest map): extensions_rivers chains current/swept/works (16 components).
- Real art for the four bank-works placeholders.

### Inventory (measured 2026-10-05, python sweep 'riverworks'|'river works', sanity probe korrum=364 hits)
RiverWorks: About (mandrake.rm.riverworks; deps Core, Odyssey, Harmony), csproj (10 .cs), DLL+.srchash,
Defs: RiverDriftDefs/RM_RiverDrift_Vanilla.xml, TerrainDefs/RM_FordStones.xml, ThingDefs_Buildings/RM_BankWorks.xml;
Patches/RM_Fordable_Water.xml; Textures/Things/Building/RiverWorks/{RM_BankStake,RM_BankWeir,RM_FerryPost,RM_SiltTrap}.png
(4 art-ledger records, BENCH shard); no Languages; one Harmony patch (Flood.CanFloodSpreadInto levee postfix);
ModSettings RM_RiverWorksSettings (21 bools + 19 numbers); selftest_riverworks.py; validation.py (3 chains, 13 rows);
walk design/validation_walks/RimMandrake/RiverWorks.md; modcheck required_checks.json key RiverWorks.
Inbound: TerminalBiomes (About dep+loadAfter, csproj Reference, 4 .cs type refs, patch xpath Class, 3 comments),
FlowWorks/human_review.py (L09-L13 probes), review html (generated), 4 design docs, ledger shards (append-only, untouched).
Not referenced by: modset_builder tiers, modlists snapshots, deploy_custom_mods, live ModsConfig (inactive; game folder deployed).
