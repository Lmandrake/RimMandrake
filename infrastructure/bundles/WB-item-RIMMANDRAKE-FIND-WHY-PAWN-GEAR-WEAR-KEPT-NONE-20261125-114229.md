# WB-item-RIMMANDRAKE-FIND-WHY-PAWN-GEAR-WEAR-KEPT-NONE-20261125-114229

System: the pawn-in-liquid matrix (src/RimMandrake/FlowWorks/northstar/pawn_in_liquid_matrix.py) and its wear rows.

| member | outcome | commit | live reading |
|---|---|---|---|
| RIMMANDRAKE_FIND_WHY_PAWN_GEAR_WEAR_KEPT_NONE | REAL, fixed and closed | 877010b1c7 | ArchSmall stage pim_stage_20261125T045149.json: 42/42 wear rows PASS, acceptance rc 0 |

Learned: the cause was the site, not the companion. ArchBig applies the ship cut list (CherryPicker.SHIP.xml), which cuts
Apparel_PowerArmor, Apparel_PowerArmorHelmet, Apparel_Robe and Apparel_PackJump; ArchSmall has no Cherry Picker settings.
The offline check selftest_flowworks_pim_garments_uncut.py now catches a cut garment.

Found outside this system: RIMMANDRAKE_CLEAR_STALE_SWAP_MARKER_NOBODY_OWNS_ARCHSMALL_LIST (modset_builder refuses on a stale swap marker).

Next: nothing. Every member has an outcome. Context after the group: 228944 of 1000000 tokens (work_bundle.py context, GO ON).
