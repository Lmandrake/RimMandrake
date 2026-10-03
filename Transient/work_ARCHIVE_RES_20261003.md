# GELATINOUSSLIME_ARCHIVE_RESURRECTION_1 — work log 2026-10-03

## Searched first
- src/: no snapshot or resurrection code in GelatinousSlime (grep resurrect/snapshot: only Titanoslime comment + a vanilla-resurrect-comp note). Nothing existing to reuse except
  the exposure tick (`MapComponent_SlimeExposure`, SlimeExposure.cs) and the Gene-archive/seeker vocabulary.
- artpipe (`artpipe_state.py find resurrect archive_vat`): 0 hits -> no art exists; building uses a green-tinted vanilla sheet (placeholder, like SlimeWorks.xml). No art queued.
- Today's Slime slices (SEAL_BREACH, FARM_RUINS, PIT_SOLVENT, SETTLING) touch other files; no overlap.

## Slime-side slice built (all inside src/RimMandrake/GelatinousSlime)
Defs/Source/validation/selftest/mock only. Outside the folder: this file only.
Belongs to OTHER items (not built): the Ascendant Ladder research tree / Helix quest line (faction_locked_trees.md §5.3; campaign `RimUtinni` ResearchRetag layer
re-parents the project); the owner's snapshot-field-list sign-off (criterion 1 — field list is below, owner has not seen it); the live criterion (needs bridge, forbidden here).

## Choices (all numbers [INVENTED])
- Snapshot field list (the identity question): name, gender, kind, race, xenotype, endogenes, xenogenes, biological + chronological age, skills (level+passion),
  traits (def+degree), childhood/adulthood backstory, direct relations (other pawn refs). NOT carried: memories/thoughts (they wake with none: "no memory of anything since"),
  hediffs/injuries/addictions (grown back whole), apparel/inventory, faction history.
- Touch = exposure tick (every 500 ticks) on a colonist/prisoner/slave humanlike that is being read (SlimeUtility.IsBeingRead, not resistant), plus an engulf by a titanoslime. One snapshot per pawn, overwritten.
  Slime rain: no separate hook; a rained-on pawn standing on slime is already covered, one off slime is not (the exposure tick keys on terrain).
- Resurrection: building `RM_ArchiveVat` (powered), gizmo lists snapshots whose person is dead; cost RM_RawSlime x150 + ComponentSpacer x4 paid from the map on start; 3 days powered to grow.
  Spawns a NEW pawn (fresh ThingID) overwritten from the snapshot; the dead corpse/record stays, so colony has both. Hediff `RM_ArchiveReturned` marks them. Memory `RM_KnewBothSelves` for kin.
- Tier: research `RM_ArchiveGrowing` requires vanilla `Archogenetics` (free mod). Campaign re-parent to the Ladder is the other item's.
- Sheet bans: ban 1 held (the body files; nothing is chosen by it). Ban 6 (no remote extraction): the vat only reads entries the body took on a pawn it touched in person; it never reaches out to a living pawn. The vat is not required to stand on slime terrain (not enforced).
- Toggle: `archiveResurrection` (Mod Settings, default on). Off: no new snapshots, vat gizmo inert; existing snapshots kept.

## Results
- winbuild GelatinousSlime: Build succeeded, 0 warnings; selftest_slime_suite exit 0 (61 components, 29 faults incl. new archive_resurrection_defs). New .cs added to csproj. Not live-tested (no bridge). Not deployed.
- Unverified in-engine: PawnGenerationRequest named args, genes.SetXenotypeDirect behaviour, relation restore. Live criterion (skill gained off body, dies, resurrects with pre-gain level) is OPEN.
