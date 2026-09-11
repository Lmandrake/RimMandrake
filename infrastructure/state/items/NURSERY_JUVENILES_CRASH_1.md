## spec
Nursery juveniles (`SeaBeasts_NurseryJuveniles.xml`, `MIASMA_NURSERY_KINDS_1`)
crashed EVERY game start once inheritance ran: a `NullReferenceException` in
`AlphaGenes_GeneDefGenerator_ImpliedGeneDefs_Patch.Postfix`, thrown during
`RimWorld.DefGenerator.GenerateImpliedDefs_PreResolve` — severe enough that
RimWorld's own recovery reset `ModsConfig.xml` and retried Core-only.
Bisect-proven 2026-09-11 (pull the file = clean load, RESET 0, config 43 vs
95). File was pulled from the game copy (`DEPLOY_HOLD.txt`) pending diagnosis.

## Root cause (confirmed from `Player-prev.log`, not inferred)
Right beside the NRE, an XML error: `<thingClass>Pawn</thingClass> doesn't
correspond to any field in type PawnKindDef. Context: <ThingDef
ParentName="RSW_Mee">...` — ThingDef-shaped content (thingClass, category,
statBases, race.thinkTreeMain, ...) ended up merged into what should have
been the `<PawnKindDef ParentName="RSW_Mee">` node.

RimWorld's `ParentName` resolution keys on the `Name=` attribute in a FLAT
namespace — NOT scoped by def type. Each of the 7 SeaBeasts base race files
(`SeaBeasts_Scalefish.xml`, `_Swarm.xml`, `_Opee.xml`) gave its ThingDef AND
its PawnKindDef the SAME `Name=` (e.g. `Name="RSW_Mee"` on both). That
collision was dormant: grepped the whole repo, and NOTHING used
`ParentName="RSW_Mee"` (or the other 6) before this nursery file added it —
first exerciser, first collision. The PawnKindDef half of the merge lost,
its `race` field ended up unresolved/null, and that's exactly what
`AlphaGenes`'s implied-gene-defs sweep NREs on (`element.RaceProps` →
`race.race`).

## Fix
Disambiguated the PawnKindDef `Name=` in the three base files to
`RSW_<X>_Kind` (defName unchanged — only the inheritance-anchor attribute
moved); updated this file's 7 `<PawnKindDef ParentName="RSW_X">` references
to `RSW_X_Kind` to match. `validate_patch.py`: 0 errors, 4/4 files. Deployed
via `deploy_custom_mods.py --mod SWBestiary --apply` (4 files, VERIFIED in
sync). `DEPLOY_HOLD.txt` entry updated in place to record the resolution
(not deleted — same convention as every other lifted hold in that file).

## verify
- [x] Root cause identified from the actual crash log, not guessed.
- [x] Fix authored, `validate_patch.py` clean, deployed to the game copy.
- [ ] **Live: next full RimWorld load (defs only parse at startup) shows no
  AlphaGenes/GeneDefGenerator NRE and no ModsConfig auto-reset** —
  `harvest_log.py` should read `Outer Rim`-style clean on any nursery-related
  check; owed to the next UP window, not forced here (the owner may be
  actively playing on this UP cycle — no unrequested restart).
- [ ] RUT_Miasma's wildAnimals refs to the 9 Juv kinds resolve now that the
  defNames exist again (defNames never changed, so this should be automatic
  — confirm on the same live load, don't assume).

## criteria
No config-error / NRE regression from this file's PawnKindDefs on a live
load; the nursery juveniles spawn and their `RaceProps` resolve normally.

## Watch out
🔑 This is a general RimWorld modding trap worth carrying forward: giving a
ThingDef and its paired PawnKindDef the SAME `Name=` (as opposed to the same
`defName`, which is fine and idiomatic) is a landmine that stays inert until
something actually uses `ParentName` against that shared name — a static
`validate_patch.py --defs` pass without an accompanying ParentName-collision
check would NOT have caught this before it shipped. Worth a lesson entry.
