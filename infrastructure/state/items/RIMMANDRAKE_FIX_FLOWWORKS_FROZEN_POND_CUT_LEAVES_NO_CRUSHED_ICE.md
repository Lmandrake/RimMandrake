## spec
found-by: FlowWorks in-game visit 3 (RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_THREE_RUN_TWO), game a, flowworks tier, calm site, 2026-11-21 5:50 AM PST.
sc_ice row ICE_cut_leaves_crushed_ice FAIL (design/concepts/FlowWorks/version/in_game/visit_3/evidence/sc_ice_20261121T055019.json):
the cut LANDS on the frozen pond (terrain ThinIce, designator accepted, RM_DigCanalJob ran, why=landed), and it leaves no crushed
ice (crushed 0, 0). The control (unfrozen cut) is clean. Class MOD: RM_GroundClassMath.IceTerrains holds "Ice", "RM_PackedIce" and
"RM_ChillIceBedrock", not vanilla ThinIce (the surface a frozen pond takes), so RM_DigSpoil never picks RM_CutSpoil.CrushedIce on it.
The bar ice_cuts_and_melts names exactly this red: "cutting ice deletes it with no crushed ice and no melt".
Not fixed in the sitting: the fix is not known with confidence. Classing ThinIce as Ice ground also changes dig speed and spoil
everywhere a frozen water surface is cut; a cut of a frozen LIQUID body may need its own crushed-ice path (the cell stays a pond).

## verify
- `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_ice --out <json>` (bridge held, flowworks tier):
  every row PASS (ICE_cut_leaves_crushed_ice, ICE_melts_back_into_pond, the control).

## criteria
- A1 L0: an offline check fails on base 0a61d77503 (ThinIce cut picks no crushed-ice spoil) and passes on the fix.
- A2 L2: sc_ice live, every row PASS.

Acceptance test: `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_ice --out <json>` exits 0 (3 rows PASS);
watched red at visit 3 (rc 1, ICE_cut_leaves_crushed_ice FAIL). The offline half is the builder's to write (red on base first).

## refs
file: src/RimMandrake/FlowWorks/Source/RM_GroundClassMath.cs
file: src/RimMandrake/FlowWorks/Source/RM_DigSpoil.cs
