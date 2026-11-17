## spec
Build the two GSS tree leaves the Designer added on 2026-11-13 (stage 3), `floor_end_shocks_crossers` and `shock_reach_setting`
in `design/concepts/GimmeSomeSlack/tree.json`. His answer, 2026-11-06 (OWNER tsn 1793996551266756043): *"Every sparking end
shocks, but settable in settings to those three options: None, only downed lines, or all."* Default All; the constructor
rebuilding that conduit is safe; only the end cell bites, and only while it is drawn live (the sheet's agent detail).
Today neither has code (`AerialSettings.cs` has only `fallenWireShock`) nor a proof row.

Add proof rows (scene_rows or the aerial block), cite both leaves in `src/RimMandrake/GimmeSomeSlack/northstar/proof_leaves.py`,
and delete both entries from its `OWED`.

Acceptance test (offline part): delete the two OWED entries and run
`python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_proof_leaves.py`: exit 0 expected. On the filing commit it exits 1
with `leaf floor_end_shocks_crossers has no row` and `leaf shock_reach_setting has no row` (watched fail 2026-11-13).
Live part: `proof_all.py --live --no-shots` on SteveDesktop (testq, tier gimmesomeslack) gives the new rows PASS.
