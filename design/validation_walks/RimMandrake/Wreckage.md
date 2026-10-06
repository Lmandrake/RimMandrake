# Wreckage — validation walk
subject: src/RimMandrake/Wreckage  (packageId mandrake.rm.wreckage; composed into mandrake.rm.biomes as an engine entry)
deps: brrainz.harmony; mandrake.rm.environmentalhazards (RM_MechanicGates); first consumer TerminalBiomes' three Scald wrecks
list: minimal+biomes
status-hint: SLICE 1 (loot half of design step 1) — design/RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md §3c/§6/§7.

## must be true
- The nine loot ThingSetMakerDefs (5 tiers, 4 rare twins; Scrap has none) resolve            → defs.loot_tables_resolve
- The three Scald wrecks resolve and carry RM_CompProperties_SalvageLoot (Hull/Tank/Scrap)    → defs.scald_wrecks_resolve
- Every comp's tier names an existing table, and every rareChance > 0 has a _Rare table        → static: static_checks() (offline, also the comp's own ConfigErrors at load)
- Careful deconstruction of a Scald hull drops costList AND a Hull-tier roll                   → UNCOVERED: no bridge verb deconstructs with a pawn (a deconstruct-job [Tool] is owed)
- Smashing a wreck (KillFinalize) drops killedLeavings slag only, never the roll               → UNCOVERED: same missing deconstruct verb (the control needs both modes)
- The rare roll's chance rises with the salvager's Construction skill                          → UNCOVERED: needs the deconstruct verb plus many trials (spawn-many rule)
- salvageLoot off → deconstruct yields costList only                                           → UNCOVERED: needs the deconstruct verb
- lootGenerosity scales stack counts (ratio, not exact)                                        → UNCOVERED: needs the deconstruct verb
- skillScalesRare off → every salvager gets the comp's base rareChance                         → UNCOVERED: needs the deconstruct verb
- No load error names this mod                                                                 → load.no_errors_naming_this_mod

## anti-guessing notes
- RULED OUT: ThingComp.PostDestroy knows the pawn — it takes (DestroyMode, Map) only; the pawn is stashed by a prefix on JobDriver_Deconstruct.FinishedRemoving (RimSage, 2026-10-06)
- RULED OUT: the loot would replace vanilla yield — ThingWithComps.Destroy runs base.Destroy (GenLeaving) before every comp's PostDestroy, so the roll is added on top
- RULED OUT: adding <comps> to a ShipChunkBase child drops the inherited inspect string — list fields append on inheritance unless Inherit="False"
