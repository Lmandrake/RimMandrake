# tank_loop (offline trace, 2026-10-13)

Verdict: HARNESS (row predates the 2026-10-11 bottle-loop C# fix), no mod defect found.

- Chain: `toggle_tank_loop` in `src/RimMandrake/FlowWorks/northstar/extensions.py` (`_tank_loop_plot`).
- Cause of "pour-in never ran, tank Empty, Job: Store": `RM_TankBottleRules.PoursInto(mode, playerOrdered)` allows an UNASKED pour only into a **Fill**-mode tank; a freshly built tank is **Store**. `WorkGiver_EmptyBottleIntoTank` therefore never finds a tank. Draw-out (`FillsFrom`) works only from Store/Empty/Dump, never Fill, so a single tank cannot show rise-then-fall unasked.
- Bottle def: `RM_BottleItemBase` is stuffed (Leathery/Stony/Metallic, FLOWWORKS_CONTAINER_MATERIALS_1). spawn_batch takes `stuff=`; without it the game logs "madeFromStuff but stuff=null" and assigns a default. Benign log noise, NOT the failure. Fixed: stuff="Leather_Plain" on both bottle spawns + selftest probe in selftest_extensions.py.
- Fill job path: terrain `WorkGiver_FillBottle` (gate bottleLoopEnabled, prio 50, 60-cell search) races `RM_FillFromTankWorkGiver` (47) - the TANK_LOOP_REBUILD item's point stands.
- Rebuild needed (live-validated, not done): (a) draw-out half = tank pre-filled via probe `filltank:x,z=RM_Liquid_FreshWater,100` (Store mode default) + one RM_BottleEmpty, bottleLoopEnabled off so terrain giver cannot win; ON: units fall / filled bottle appears; OFF (tankLoopEnabled): unchanged 3000 ticks. (b) pour-in half needs Fill mode: only settable via the "Job:" gizmo (liquid_checks.gizmo_cycle) or a forced order (bypasses the toggle). The extension harness `t` has no HoseProbe (`hp`) channel nor a tank-mode setter; a tiny static proof method would be needed.
