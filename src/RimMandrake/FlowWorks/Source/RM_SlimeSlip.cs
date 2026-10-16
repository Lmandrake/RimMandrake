using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// SLIME_CROSSING_BUILD_SLIPPERY_SLOPE (owner: <i>"so slippery that it is nearly impossible to cross, and escape from
	/// the pit takes a great deal of time"</i>). A pawn walking through a cell whose fluid has <c>slipperiness</c> &gt; 0
	/// rolls once a second (RM_SlimeMath); a slip stuns it (vanilla StunHandler, so the pawn visibly stops) and throws a
	/// text mote over it, so nobody is ever slowed without a readable sign. A slip on a step toward shallower ground (the
	/// climb out) also slides it back to the start of that step. Route planning avoids slime through the fill terrains'
	/// own pathCost (FlowWorks_SlimeTerrain.xml). Mod Setting slimeSlipEnabled (off: slime is just a thick liquid).
	/// Scope: dug cells holding a slippery fill (canals, pits). Natural slime pools are not excavated cells and do not slip.
	/// </summary>
	public static class RM_SlimeSlip
	{
		/// <summary>Slips per pawn thingIDNumber this session — the census ProofReport reads (not saved: a proof surface).</summary>
		private static readonly Dictionary<int, int> slips = new Dictionary<int, int>();
		private static readonly Dictionary<int, int> climbSlips = new Dictionary<int, int>();

		private static readonly Color SlipText = new Color(0.75f, 0.95f, 0.55f);

		public static void Tick(Map map, RM_MapComponent_Excavation ex)
		{
			if (!RimMandrakeFlowWorksSettings.slimeSlipEnabled || Find.TickManager.TicksGame % RM_SlimeMath.IntervalTicks != 0)
			{
				return;
			}
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				if (p.Dead || p.Downed || p.pather == null || !p.pather.Moving || p.stances?.stunner == null
					|| p.stances.stunner.Stunned || p.Flying)
				{
					continue;
				}
				IntVec3 c = p.Position;
				if (!ex.IsExcavated(c))
				{
					continue;
				}
				int fill = ex.FillAt(c);
				if (fill <= 0 || Pits.RM_PitCoverUtility.IsCovered(map, c))
				{
					continue;
				}
				FluidDef fluid = ex.FluidAt(c) ?? ex.ActiveFluid;
				if (fluid == null || fluid.slipperiness <= 0f)
				{
					continue;
				}
				IntVec3 next = p.pather.nextCell;
				bool climbingOut = next.IsValid && next != c && next.InBounds(map)
					&& RM_SlimeMath.IsClimbingOut(ex.HollowDepthAt(c), ex.HollowDepthAt(next));
				float chance = RM_SlimeMath.SlipChance(fluid.slipperiness, fill, ex.DepthAt(c), climbingOut, false,
					RimMandrakeFlowWorksSettings.slimeSlipChanceMultiplier, RimMandrakeFlowWorksSettings.slimeClimbOutSlipFactor);
				if (!Rand.Chance(chance))
				{
					continue;
				}
				Slip(p, map, fluid, climbingOut);
			}
		}

		private static void Slip(Pawn p, Map map, FluidDef fluid, bool climbingOut)
		{
			p.stances.stunner.StunFor(RM_SlimeMath.StunTicks(RimMandrakeFlowWorksSettings.slimeSlipStunSeconds), null,
				addBattleLog: false, showMote: false);
			if (climbingOut)
			{
				p.pather.nextCellCostLeft = p.pather.nextCellCostTotal;   // slid back to the start of the climb
			}
			string what = fluid.label ?? "slime";
			MoteMaker.ThrowText(p.DrawPos + new Vector3(0f, 0f, 0.5f), map,
				climbingOut ? "Slid back into the " + what : "Slipped in the " + what, SlipText, 3.5f);
			int id = p.thingIDNumber;
			slips[id] = (slips.TryGetValue(id, out int n) ? n : 0) + 1;
			if (climbingOut)
			{
				climbSlips[id] = (climbSlips.TryGetValue(id, out int m) ? m : 0) + 1;
			}
		}

		/// <summary>static_call surface: "" -&gt; "SLIME n | id@x,z D= F= fluid= slip= slips= climbSlips= moving=" for every
		/// pawn on a dug cell holding liquid, plus the session slip counts. "reset" clears the counts first.</summary>
		public static string ProofReport(string arg)
		{
			if ((arg ?? "").Trim() == "reset")
			{
				slips.Clear();
				climbSlips.Clear();
			}
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null) return "REFUSED: no excavation component on the current map";
			var rows = new List<string>();
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				IntVec3 c = p.Position;
				int id = p.thingIDNumber;
				bool inLiquid = ex.IsExcavated(c) && ex.FillAt(c) > 0;
				if (!inLiquid && !slips.ContainsKey(id)) continue;
				FluidDef f = inLiquid ? (ex.FluidAt(c) ?? ex.ActiveFluid) : null;
				rows.Add(p.ThingID + "@" + c.x + "," + c.z + " D=" + ex.DepthAt(c) + " F=" + ex.FillAt(c)
					+ " fluid=" + (f?.defName ?? "none") + " slip=" + (f?.slipperiness ?? 0f).ToString("F2")
					+ " slips=" + (slips.TryGetValue(id, out int n) ? n : 0)
					+ " climbSlips=" + (climbSlips.TryGetValue(id, out int m) ? m : 0)
					+ " moving=" + (p.pather?.Moving ?? false));
			}
			return "SLIME " + rows.Count + " enabled=" + RimMandrakeFlowWorksSettings.slimeSlipEnabled + " | "
				+ string.Join(" | ", rows);
		}
	}
}
