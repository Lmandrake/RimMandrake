# GSS flips — GSS_SWITCHES_PROVE_TWENTY_UNFLIPPED (A2)

Status: built, ready for a short live check (offline only; no bridge used).

New rows in `src/RimMandrake/GimmeSomeSlack/validation_aerial.py` (`flips_block`, also run inside `run_live` before AZ log budget, declared in proof_all `DECLARED_ROWS["aerial"]`):
- M20a_fallen_wire_shock_flip: shock off -> no RM_FallenWireShock hediff on a downed animal at the live tip; on -> hediff.
- M20b_fallen_wire_knockback_flip: knockback 0 -> shocked, not moved; 3 -> shocked and moved (up to 3 pawns).
- M20c_fallen_wire_ignites_flip: Filth_Fuel on the live tip; ignites off -> no Fire over 12 sweeps (3000 ticks); on -> Fire within 12 sweeps (35%/sweep, miss 0.6%).
- M20d_keep_wires_setting_roundtrip: WIRING ONLY (field flips and reads back). keepWiresOnGravship behaviour needs a gravship launch (generatingGravship is only true inside the engine despawn loop); stays owed.
- M20_flip_scene_built: harness row (site: battery + 2 masts, span blown, F1 holds a live fallen half).

Offline: selftest_proof_all.py check 7 drives the real flips_block against a faithful and a broken fake bridge (PASS / FAIL respectively); proof_all --offline-gate red=[]; run_selftests 323 PASS / 0 FAIL.
Unproven until live: tool arg shapes (spawn_pawn faction="none" Muffalo, pawn_force_incapacitate action="downed", list_pawns includeHealth/pos shape), list_things defName="Fire", rimworld/spawn_thing Filth_Fuel.

Live command (about 4-5 min, dominated by the 3000-tick ignite control):
  python.exe src/RimMandrake/GimmeSomeSlack/validation_aerial.py --flips
A3 (11 hose keys) still waits on HOSE_REEL_MIGRATE_TO_FLOWWORKS_AT_LAST.
