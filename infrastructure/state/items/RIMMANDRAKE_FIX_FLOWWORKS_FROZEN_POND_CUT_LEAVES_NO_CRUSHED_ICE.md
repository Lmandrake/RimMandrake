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

## stage (steward, RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_THREE_FAILURES_BACK, 2026-11-21)
needs offline. The fault is in pure code that the C# SelfTest already compiles: `RM_GroundClassMath.Classify` (GroundClassChecks.cs
case `IceDig_ice_and_packed_snow_cut_into_crushed_ice` asserts Ice, RM_PackedIce, RM_ChillIceBedrock, RM_PackedSnow and VEE dense
snow, never ThinIce) and `CutYield`. Offline acceptance: a new C# SelfTest case (in GroundClassChecks.cs, or beside RM_DigSpoil's
pick) asserts that a cut on the surface a frozen pond takes (vanilla ThinIce) yields RM_CutSpoil.CrushedIce, and that loose Snow
and unfrozen water still do not. Run it at the parent first (red), then on the fix (green), with the FlowWorks C# SelfTest
`--only <case>`. The fixer decides the design (ThinIce as Ice ground, or a frozen-liquid crushed-ice path); the bar
ice_cuts_and_melts decides, not this text.
In-game check: test table stage-6 id `sc_ice`, live command
`python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_ice --out <json>`. The fixer records it UNRUN for
Stage 6 with `maturation.py unrun` when it closes this item on the offline test.
