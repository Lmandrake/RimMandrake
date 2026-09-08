# PawnFlavor — validation walk
subject: src/RimUtinni/PawnFlavor  (packageId mandrake.rut.pawnflavor)
deps: none hard (loadAfter Ludeon.RimWorld, Ludeon.RimWorld.Royalty [vanilla/DLC], mandrake.jawa.patches [=UtinniPatches, this campaign's own mod, not third-party]). The three PawnFlavorPhase2_* patch files are each PatchOperationFindMod-gated per-block against ~56 combined third-party mods (Alpha Animals, Alpha Biomes, Biotech, ABF: Synstructs Core, Vanilla Traits Expanded, Outer Rim - Droid Depot, and dozens more) — safe no-ops when absent.
list: minimal (core backstories/traits/wiring need nothing else) | full needed to exercise any single PawnFlavorPhase2_* relabel block, since each is gated on one specific third-party mod being active
status-hint: faction-keyed pawn flavor for Ash'karr — 50 BackstoryDefs across ten factions (2 childhoods + 3 adulthoods each, per faction-specific files), 13 TraitDefs, a patch wiring one JawaBSC_<Faction> backstory category into every faction's backstoryFilters, and three large PatchOperationFindMod patches that relabel other mods' ThoughtDef/XenotypeDef/MentalBreakDef flavor text to Jawa voice when those mods are present.

## must be true
- Every Backstories_*.xml file loads with no config error; between the six files at least 50 BackstoryDefs total exist (defName counts observed: Deepwater 5, Empire_Hutt 10, FDE_Droids 6, Geonosian_Helix_Blackstar 15, Homestead_Tribes 13, Moot_Wildsteam_Junkers 18 — some are childhood-only subsets, sum across files per faction).
- Traits_JawaPawnFlavor.xml defines exactly 13 TraitDefs, defNames prefixed RUT_Jawa_ (e.g. RUT_Jawa_WaterDiscipline, RUT_Jawa_SandStoic, RUT_Jawa_PodracerReflexes).
- FactionBackstoryWiring.xml's PatchOperationConditional on FactionDef[defName="Empire"]/backstoryFilters adds a JawaBSC_Empire category li when that faction's raw node exists; the same pattern adds JawaBSC_Blackstar to Pirate and JawaBSC_Moot to Jawa_IndigenousTribes.
- Factions that inherit backstoryFilters from an abstract parent (OutlanderCivil, Jawa_HuttCartel, Jawa_WildsteamClan, Jawa_GeonosianFoundryHive, Jawa_AscendantHelix, Jawa_DeepwaterCompact, TribeCivil, Jawa_Junkers) end up with a FULL backstoryFilters list restating the parent's categories (Outlander/Offworld, Tribal, or Pirate) PLUS the Jawa category — since a patched child list overrides rather than merges with the parent.
- Jawa_Junkers' own declared backstoryFilters list (Pirate + JawaBSC_Moot per the file) sheds the Blackstar leak that the Pirate-faction patch would otherwise inherit through PirateBandBase.
- With a PawnFlavorPhase2_* target mod (e.g. Biotech for Xenotype, ABF: Synstructs Core for MentalBreak) active, the matching def's label/description text is replaced by the Jawa-voiced string in this patch file, never left at the source mod's original wording.

## the walk
1. [L] Player.log after load (minimal list) contains no "Config error in mandrake.rut.pawnflavor" and no XML error naming any Backstories_*.xml, Traits_JawaPawnFlavor.xml, or FactionBackstoryWiring.xml
2. [D] def read-back: BackstoryDef RUT_Jawa_CisternHatched exists (Deepwater set)
3. [D] def read-back: TraitDef RUT_Jawa_WaterDiscipline exists
4. [D] def read-back: FactionDef Empire; backstoryFilters contains a categories entry JawaBSC_Empire
5. [D] def read-back: FactionDef OutlanderCivil; backstoryFilters contains BOTH an Outlander/Offworld-derived category AND JawaBSC_Empire is absent (only the Jawa category matching OutlanderCivil's own faction set should be present — confirms override-not-merge landed correctly rather than silently dropping the parent categories)
6. [D] def read-back: FactionDef Jawa_Junkers; backstoryFilters contains Pirate and JawaBSC_Moot, and does NOT contain JawaBSC_Blackstar
7. [L] with Biotech active in the load: Player.log contains no XML error naming PawnFlavorPhase2_Xenotype.xml
8. [D] with Biotech active: def read-back defType=XenotypeDef defName=Baseliner; description = "No genes worth logging. A baseliner works like your grandfather worked — hands, sweat, and whatever tool's in reach. Cheap to feed, easy to trust, nothing to trade for. Every clan's got a few; every clan needs them."
9. [L] with ABF: Synstructs Core active in the load: Player.log contains no XML error naming PawnFlavorPhase2_MentalBreak.xml
10. [D] with ABF: Synstructs Core active: def read-back defType=MentalBreakDef defName=ABF_MentalBreak_Synstruct_FriendlyGrassObsession; label = "circuits gone soft for green things"
