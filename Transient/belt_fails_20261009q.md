# belt fails 2026-10-09q — offline fixes for bridge5 (k) FAILs

Source log: Transient/belt_bridge5_20261009k.md. All offline; nothing deployed, no bridge.

## (a) LASSO_CHERRYPICKER_REMOVAL_1 — FIXED in src (ddb3795da)
Make_AM_Lasso* are implied recipes generated from Melee Animation's own recipeMaker before Cherry Picker runs; no other
installed mod references AM_Lasso (full sweep). UtinniPatches/Patches/MeleeAnimation_LassoRemoval.xml strips recipeMaker
from AM_LassoBaseMakeable + children. validate_patch 0 errors; new selftest_lasso_removal.py (probe 3 -> 0). A2 spawn setting still owed at game-down.

## (b) DROIDWORKS_FORMAT_TIERS_1 — FIXED in src (6f98539db)
ShouldHaveNeed postfix (Priority.Last) vetoes every non-power need on Mindless/Blank droids; RSW_DW_BlankStandbyInsert
(Humanlike_PostMain) stands Blank droids with a Wait job. Droidworks builds 0/0; fuzz 11007 cases OK with new invariants.

## (c) KINETIC_BLAST_WEAPONS_1 EK body_override / shield_counter — proof staging only, no mod-code change
body_override: verdict used displacement of live animals (control logged too_big but walked 5 cells); now journal-based.
shield_counter: fresh belt at energy 0; scene now charges it and reads the counter's own record. EK builds; kernel 91/91; STATIC PASS.

Live-verify criteria for each are on the items' notes.
