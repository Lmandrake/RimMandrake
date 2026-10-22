using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS phase 5 (owner follow-up 2026-10-20, design R10/Q4): a bridge across the gravship's
	/// edge COLLAPSES at launch and anyone on it falls (the ordinary span collapse: CollapseSpan, the own-faction setting as
	/// for any collapse). Runs before the ship is gathered (GenerateGravship builds its thing list from the substructure), so
	/// the fallen decks never fly. A suspension bridge stands over dug ground and substructure cannot be dug, so a bridge with
	/// every square on the ship is not expected; one with ANY square on the ship is treated as crossing the edge (conservative:
	/// its record would otherwise be left keyed to the old map). Applies to every suspension bridge, drawbridge or not.
	/// </summary>
	[HarmonyPatch(typeof(GravshipUtility), nameof(GravshipUtility.GenerateGravship))]
	[RimMandrake.Shared.PatchFeature("Suspension bridges survive a gravship launch")]
	public static class RM_Patch_GravshipLaunch_Bridges
	{
		public static int Collapsed;

		/// <summary>The bridges torn loose at the launch now under way (refilled by each launch; read only while
		/// GravshipUtility.generatingGravship): a winch flying off from one of these finds no leaf left to crash.</summary>
		public static readonly HashSet<SuspensionBridgeRecord> TornLoose = new HashSet<SuspensionBridgeRecord>();

		[HarmonyPrefix]
		public static void Prefix(Building_GravEngine engine)
		{
			TornLoose.Clear();
			Map map = engine?.Map;
			RM_MapComponent_SuspensionBridges comp = map == null ? null : RM_MapComponent_SuspensionBridges.Of(map);
			if (comp == null)
			{
				return;
			}
			HashSet<IntVec3> ship = new HashSet<IntVec3>(engine.ValidSubstructure);
			foreach (SuspensionBridgeRecord r in new List<SuspensionBridgeRecord>(comp.Bridges))
			{
				if (!TouchesShip(r, ship))
				{
					continue;
				}
				TornLoose.Add(r);
				for (int span = 0; span < r.SpanCount; span++)
				{
					foreach (int i in r.SpanIndices(span))
					{
						Building_SuspensionDeck d = RM_MapComponent_SuspensionBridges.StructuralDeckAt(map, r.Cell(0, i));
						if (d != null)
						{
							comp.CollapseSpan(d, "was torn loose when the gravship launched");
							Collapsed++;
							break;
						}
					}
				}
			}
		}

		/// <summary>Any square of the bridge (anchors included, every lane) on the ship's substructure.</summary>
		public static bool TouchesShip(SuspensionBridgeRecord r, HashSet<IntVec3> ship)
		{
			for (int lane = 0; lane < r.width; lane++)
			{
				for (int i = 0; i < r.length; i++)
				{
					if (ship.Contains(r.Cell(lane, i)))
					{
						return true;
					}
				}
			}
			return false;
		}
	}
}
