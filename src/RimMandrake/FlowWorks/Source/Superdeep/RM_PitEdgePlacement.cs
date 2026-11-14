using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE (owner look 2026-11-14, his 3: "It should not let you install furniture that
	/// overlaps with a pit edge. Right now I can install a butcher table hanging over a pit in any configuration."): a building of
	/// more than one square is placed (built or installed: both go through CanPlaceBlueprintAt) only where every square of its
	/// footprint stands at one depth: all on the ground or all on one pit floor (RM_PitTrapMath.StraddleRefusal). A square under a
	/// deck or cover stands at the deck's height. FlowWorks' own pit work (ladders, ramps, bridges, covers, sluices, pumps) is
	/// made to meet an edge and is exempt. Mod Setting pitEdgeStraddleRefusedEnabled (off: anything may hang over a pit).
	/// </summary>
	[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.CanPlaceBlueprintAt_NewTemp))]
	[RimMandrake.Shared.PatchFeature("Furniture never hangs over a pit edge", typeof(RimMandrakeFlowWorksSettings), "pitEdgeStraddleRefusedEnabled")]
	public static class RM_PitEdgePlacement
	{
		private const string OwnPackage = "mandrake.rm.flowworks";

		private static readonly List<int> depths = new List<int>(16);

		[HarmonyPostfix]
		public static void Postfix(BuildableDef entDef, IntVec3 center, Rot4 rot, Map map, ref AcceptanceReport __result)
		{
			if (!__result.Accepted || !RimMandrakeFlowWorksSettings.pitEdgeStraddleRefusedEnabled || map == null || !(entDef is ThingDef td))
			{
				return;
			}
			bool own = string.Equals(td.modContentPack?.PackageId, OwnPackage, StringComparison.OrdinalIgnoreCase);
			if (!RM_PitTrapMath.StraddleRuleApplies(td.category == ThingCategory.Building, td.size.x * td.size.z, own))
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null || eng.ClimbCellCount == 0)
			{
				return;   // no pit on this map: the common case
			}
			string why = RefusalAt(map, eng, GenAdj.OccupiedRect(center, rot, td.Size));
			if (why != null)
			{
				__result = new AcceptanceReport(why);
			}
		}

		/// <summary>The straddle verdict for a footprint (null = it stands at one depth).</summary>
		public static string RefusalAt(Map map, RM_MapComponent_Excavation eng, CellRect rect)
		{
			depths.Clear();
			foreach (IntVec3 c in rect)
			{
				int d = c.InBounds(map) ? eng.HollowDepthAt(c) : 0;
				if (d > 0 && Pits.RM_SpanUtility.DeckedAt(map, c, out float deckM))
				{
					d = Math.Min(d, RM_SpanMath.Notches(deckM));
				}
				depths.Add(d);
			}
			return RM_PitTrapMath.StraddleRefusal(depths);
		}

		/// <summary>[proof] "defName;x;z;rot": the placement verdict a player gets ("ACCEPTED" or "REFUSED: reason"), read only.</summary>
		public static string ProofPlace(string arg)
		{
			Map map = Find.CurrentMap;
			string[] p = (arg ?? "").Split(';');
			if (map == null || p.Length < 3 || !int.TryParse(p[1], out int x) || !int.TryParse(p[2], out int z))
			{
				return "REFUSED: need a current map and \"defName;x;z[;rot]\"";
			}
			ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(p[0].Trim());
			if (def == null)
			{
				return "REFUSED: no ThingDef " + p[0];
			}
			Rot4 rot = p.Length > 3 && int.TryParse(p[3], out int r) ? new Rot4(r) : Rot4.North;
			AcceptanceReport rep = GenConstruct.CanPlaceBlueprintAt(def, new IntVec3(x, 0, z), rot, map, false, null, null,
				def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null);
			return rep.Accepted ? "ACCEPTED" : "REFUSED: " + rep.Reason;
		}
	}
}
