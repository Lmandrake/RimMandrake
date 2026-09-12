using LudeonTK;
using Verse;

namespace RimMandrake.ShipVermin
{
	// WRECKAGE_VERMIN_SPAWN_1 re-block debug hook. Same pattern as the sibling
	// FloodedCanyon mod's own RM_FloodedCanyonDebugActions: force + report a
	// mechanism that would otherwise take real days of ticks (or, per this
	// item's history, fail silently on every branch) to observe.
	//
	// ToolMap (not a plain Action) because RM_CompVerminNest lives on a
	// specific wreck Thing, not a singleton MapComponent — the bridge's
	// execute_debug_action can drive a ToolMap leaf with either x/z or a
	// thingId, which resolves to the clicked cell either way.
	public static class RM_ShipVerminDebugActions
	{
		private const string CAT = "RMShipVermin";

		// 🔴 DO NOT wrap this method's body in its own `new DebugTool(...)`.
		// The [DebugAction] ToolMap dispatcher (LudeonTK.DebugActionNode.Enter)
		// ALREADY does `DebugTools.curTool = new DebugTool(LabelNow, action)`
		// where `action` IS this attributed method — so this method itself is
		// the click handler, called with the real click already having
		// happened and UI.MouseCell() already valid. Registering a SECOND,
		// inner DebugTool from inside it (the first version of this file did
		// exactly that) just re-arms the tool on click #1 and defers the real
		// payload to a click #2 that never came — the debug hook itself was
		// silently swallowing its own trigger. Confirmed against vanilla
		// (Verse.DebugToolsSpawning.MakeFilthx100 et al.), which never does this.
		[DebugAction(CAT, "Force nest spawn attempt (click wreck)",
			actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
		private static void ForceSpawnAttempt()
		{
			RM_CompVerminNest comp = FindNestCompAt(UI.MouseCell());
			if (comp == null)
			{
				Log.Message("[RMShipVerminDebug] no RM_CompVerminNest at " + UI.MouseCell());
				return;
			}
			string result = comp.AttemptSpawn(verbose: true);
			Log.Message("[RMShipVerminDebug] AttemptSpawn -> " + result);
		}

		[DebugAction(CAT, "Report nest state (click wreck)",
			actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
		private static void ReportState()
		{
			RM_CompVerminNest comp = FindNestCompAt(UI.MouseCell());
			if (comp == null)
			{
				Log.Message("[RMShipVerminDebug] no RM_CompVerminNest at " + UI.MouseCell());
				return;
			}
			Log.Message("[RMShipVerminDebug] wreckSpawningEnabled=" + ShipVerminSettings.wreckSpawningEnabled
				+ " ticksUntilNextSpawn=" + comp.DebugTicksUntilNextSpawn()
				+ " ticksGame=" + Find.TickManager.TicksGame);
		}

		private static RM_CompVerminNest FindNestCompAt(IntVec3 cell)
		{
			Map map = Find.CurrentMap;
			if (map == null || !cell.InBounds(map))
			{
				return null;
			}
			foreach (Thing t in cell.GetThingList(map))
			{
				if (t is ThingWithComps twc)
				{
					RM_CompVerminNest comp = twc.GetComp<RM_CompVerminNest>();
					if (comp != null)
					{
						return comp;
					}
				}
			}
			return null;
		}
	}
}
