# MIASMA_YOUNG_CALL_1 work log (2026-10-03)
Started. Choices:
- Found: step 1/3 cry already exists as RM_HediffComp_LocatableCall on RUT_StrandedDeformation (EnvironmentalHazards, outside Miasma; ticks while spawned, so pen keeps crying). Not touched.
- New in Miasma only: RM_MapComponent_YoungCall.cs (first-cry letter per map; every 250 ticks sends the nearest living, un-downed RM_WardenMother within 60 cells a Goto to the water cell nearest the crying young; never dry; "its mother" = nearest warden mother, ledger's motherPawn is private).
- Toggle youngCallEnabled: gates the letter+mother AND the cry itself (applier nulls callSound on the shared hediff comp props by reflection, stashed/restored), so no outside-folder edit.
- No art, no new sound asset (reuses Pawn_Frog_Call already on the hediff). No new SoundDef.
- Built OK (RimMandrake.Miasma.dll); validation.py static PASS; validate_patch 0 errors on keyed file. Live criteria (cry heard, mother Goto stops at water edge) UNMEASURED: suite chain young_call. Existing cry is in EnvironmentalHazards (untouched).
