# Empire siege patch (EMPIRE_ESCALATION_LADDER_1 ion-cordon)

## Status
DONE, no patch written: the premise was false.

## Findings
- `Data/Royalty/Defs/FactionDefs/Faction_Empire.xml` line 13: `<canSiege>true</canSiege>` on `Empire`.
  The "canSiege false" in the item came from Royalty's `Factions_Misc.xml` (OutlanderRefugee), not the Empire.
- Our reskin `src/RimUtinni/UtinniPatches/Patches/GalacticEmpire.xml` adds fields only (no Replace/Remove, no siege).
- 0 xpaths containing `canSiege` across 150 installed-mod XML files that mention it (Mods + workshop).
- Def dump (`measure record Empire`, captured 2026-10-04, 638 mods): has no `canSiege` field for any
  faction (Pirate control also absent), so runtime value is UNMEASURED there; source is the evidence.
- Engine: `RaidStrategyWorker_Siege.CanUseWith` returns `faction.def.canSiege`; the ladder passes
  `raidStrategy` explicitly, so `IncidentWorker_RaidEnemy.ResolveRaidStrategy` skips the check anyway.
- Real remaining L2 risk: `LordToil_Siege.CanBeBuilder` needs Construction + Firefighter enabled.

## Changed
- `infrastructure/state/items/EMPIRE_ESCALATION_LADDER_1.md`: risk text corrected.
