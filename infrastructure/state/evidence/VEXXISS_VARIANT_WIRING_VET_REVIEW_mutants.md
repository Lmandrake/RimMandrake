# VEXXISS_VARIANT_WIRING_VET_REVIEW proof mutants (2026-11-03, gen 3)
proof: python3 infrastructure/state/evidence/VEXXISS_VARIANT_WIRING_VET_REVIEW_proof.py -> exit 0 on the code as it stands
each mutant on a temp copy (--repo-root/--deployed-root/--skip-review) except dirty, run on the real file then restored:
- VE_south_absent_both: FAIL repo texture exists: Textures/Things/Pawn/Animal/RM_Vexxiss/RM_VexxissV_E_south.png ; RESULT FAIL (3 failures)
- alt_removed: FAIL alternateGraphics names Things/Pawn/Animal/RM_Vexxiss/RM_VexxissV_E (got ['Things/Pawn/Animal/RM_Vexxiss/RM_Vexxiss']) ; RESULT FAIL (1 failures)
- baseline: no FAIL (baseline) ; RESULT PASS (0 failures)
- chance_025: FAIL alternateGraphicChance == 0.5 (got '0.25') ; RESULT FAIL (1 failures)
- dirty: FAIL review CLEAN: ['DIRTY  src/RimMandrake/Cauldron/Defs/ThingDefs_Races/RM_CauldronFauna.xml  (content changed since clean mark at daab7031d0 on 2026-10-24)'] ; RESULT FAIL (2 failures)
- drift_VE_east: FAIL deployed texture identical: Textures/Things/Pawn/Animal/RM_Vexxiss/RM_VexxissV_E_east.png ; RESULT FAIL (2 failures)
- missing_VE_north: FAIL deployed texture identical: Textures/Things/Pawn/Animal/RM_Vexxiss/RM_VexxissV_E_north.png ; RESULT FAIL (2 failures)
- xml_drift: FAIL deployed def identical: /home/mandrake/.seat-tmp/BENCH/tmp.pnciEDlzal/dep/Defs/ThingDefs_Races/RM_CauldronFauna.xml ; RESULT FAIL (1 failures)
