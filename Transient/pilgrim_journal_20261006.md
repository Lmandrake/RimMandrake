# WARSCAR_PILGRIM_JOURNAL_ANTIQUITY_1 — 2026-10-06 (FOUNDRY, offline, uncommitted)

## findings
- Scarlands ladder EXISTS (RUT_ScarlandsLadder, 5 ruled rungs) and the journal already advanced it via a CompUsable read (WARSCAR_PILGRIM_CAMPS_1). SCARLANDS_MECHANICS_2 is unrelated kit work.
- Antiquities: src/RimUtinni/Antiquities (CompAntiquity, WorkGiver/JobDriver_ExamineAntiquity, RUT_AntiquityReadingStation). WorkGiver matched a hardcoded defName set.
- Art: RUT_PilgrimJournal.png already installed (artpipe done/). Nothing generated.

## built
- Antiquities: IAntiquityCatalogueListener (CompAntiquity.cs); AntiquityUtility.HasCatalogueListener; WorkGiver now comp-based (any CompAntiquity) and offers listener pieces after VOICE; JobDriver notifies listeners on catalogue, skips research credit when no stage left.
- ScarlandsLadder: CompRUT_PilgrimJournal implements the listener -> RUT_PilgrimJournals.Read; CompUsable/UseEffect read REMOVED (one route); journal XML gains CompProperties_Antiquity; hard dep + loadAfter mandrake.rut.antiquities; csproj references Antiquities dll.

## validation
- winbuild both: 0W/0E. ScarlandsLadder validation.py STATIC PASS. validate_patch journal XML + About: 0 errors.

## left / questions
- Q1 research credit: a journal currently also counts as one artifact toward the current RUT_Antiq_* stage. Intended?
- Q2 duration: read is now the station's full day (half after LANGUAGE), not 600 ticks. OK?
- Q3 two letters per journal (antiquity progress + journal page). Merge?
- Live: no bridge proof of the station route yet.
