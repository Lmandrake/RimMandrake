using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS — the ramp (design/RimMandrake/relative_depth_climb_design_2026-10-12.md §8.4).
	/// Owner, 2026-10-12 (Q3): <i>"ramps &amp; stairs could descend swiftly (but not instantly) without movement penalty. A ramp
	/// could take up 1 square but go down up to 3 levels at a time without movement penalty."</i>
	///
	/// 1×1, built on a dug square (or a dry pond bed), rotatable: its rotation points UPHILL. It joins its own square to the
	/// cardinal neighbour it faces when that neighbour is 1 to "Levels a ramp spans" (default 3) levels shallower
	/// (RM_CliffMaskMath.RampJoins). That step is allowed for EVERY pawn, any size, both directions (enemies too), at flat
	/// walking cost (RM_PitTrapMath.StepCost viaRamp). It is structural: it enters the pocket grid and every band's cliff mask,
	/// so spawning or removing one bumps the climb generation; deconstructing it re-seals the pit.
	/// ART: the four-facing earth-and-timber ramp (Things/Building/FlowWorks/Excavation/RM_PitRamp, Graphic_Multi), installed
	/// through the art ledger at 04657a349b.
	/// </summary>
	public class RM_Building_PitRamp : Building
	{
		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			map.GetComponent<RM_MapComponent_Excavation>()?.BumpClimbGeneration();
		}

		public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
		{
			Map map = Map;
			base.DeSpawn(mode);
			map?.GetComponent<RM_MapComponent_Excavation>()?.BumpClimbGeneration();
			map?.reachability.ClearCache();
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			Map map = Map;
			RM_MapComponent_Excavation eng = map?.GetComponent<RM_MapComponent_Excavation>();
			if (eng == null)
			{
				return s;
			}
			IntVec3 up = Position + Rotation.FacingCell;
			int d = RM_SuperdeepTrap.StepDepthAt(map, eng, Position);
			int u = up.InBounds(map) ? RM_SuperdeepTrap.StepDepthAt(map, eng, up) : d;
			string line = RM_PitRamp.Usable && RM_CliffMaskMath.RampJoins(d, u, RM_PitRamp.MaxSpan)
				? "RMFlow_RampJoins".Translate(RM_Volume.FormatMetres(d - u))
				: "RMFlow_RampJoinsNothing".Translate(RM_Volume.FormatMetres(RM_PitRamp.MaxSpan));
			return string.IsNullOrEmpty(s) ? line : s + "\n" + line;
		}
	}

	public static class RM_PitRamp
	{
		public static bool Usable => RimMandrakeFlowWorksSettings.pitRampsEnabled;

		public static int MaxSpan => Mathf.Clamp(RimMandrakeFlowWorksSettings.pitRampMaxSpan, 1, 3);

		private static ThingDef def;
		private static bool looked;

		public static ThingDef Def
		{
			get
			{
				if (!looked)
				{
					looked = true;
					def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_PitRamp");
				}
				return def;
			}
		}

		/// <summary>The ramp standing in this square (a built one; blueprints and frames are not ramps), or null.</summary>
		public static Thing RampAt(Map map, IntVec3 c)
		{
			ThingDef d = Def;
			if (d == null || map == null || !c.InBounds(map))
			{
				return null;
			}
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i].def == d)
				{
					return things[i];
				}
			}
			return null;
		}

		/// <summary>Does a ramp join cardinal neighbours a and b (a ramp at a facing b, or at b facing a, spanning their
		/// depth difference)? aD / bD: their step depths (covers read 0).</summary>
		public static bool Joins(Map map, IntVec3 a, IntVec3 b, int aD, int bD)
		{
			if (!Usable || aD == bD || Def == null)
			{
				return false;
			}
			IntVec3 low = aD > bD ? a : b, high = aD > bD ? b : a;
			Thing r = RampAt(map, low);
			return r != null && low + r.Rotation.FacingCell == high
				&& RM_CliffMaskMath.RampJoins(System.Math.Max(aD, bD), System.Math.Min(aD, bD), MaxSpan);
		}

		/// <summary>The pocket grid's ramp pairs (cell index → the index it joins), over one depth array.</summary>
		public static Dictionary<int, int> Pairs(Map map, byte[] depth)
		{
			var pairs = new Dictionary<int, int>();
			if (!Usable || Def == null)
			{
				return pairs;
			}
			List<Thing> ramps = map.listerThings.ThingsOfDef(Def);
			CellIndices ci = map.cellIndices;
			for (int i = 0; i < ramps.Count; i++)
			{
				IntVec3 c = ramps[i].Position, up = c + ramps[i].Rotation.FacingCell;
				if (!c.InBounds(map) || !up.InBounds(map))
				{
					continue;
				}
				int a = ci.CellToIndex(c), b = ci.CellToIndex(up);
				if (RM_CliffMaskMath.RampJoins(depth[a], depth[b], MaxSpan))
				{
					pairs[a] = b;
				}
			}
			return pairs;
		}
	}

	/// <summary>Design §8.4 placement: a dug square (or a dry pond bed), facing a cardinal neighbour 1 to "Levels a ramp spans"
	/// levels shallower, never a square holding a ladder.</summary>
	public class PlaceWorker_PitRamp : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map,
			Thing thingToIgnore = null, Thing thing = null)
		{
			RM_MapComponent_Excavation eng = map?.GetComponent<RM_MapComponent_Excavation>();
			// WATERED_PIT_FIX_NO_WAY_IN: the ramp stands on the pit FLOOR, so it is judged on the holes (HollowDepthAt), wet or
			// dry; the climb depth reads a wet pit at its water surface and would refuse a ramp in any pit holding 1.5 m of water.
			if (eng == null || eng.HollowDepthAt(loc) == 0)
			{
				return "RMFlow_RampNeedsPit".Translate();
			}
			if (RM_LadderUtility.HasLadder(map, loc))
			{
				return "RMFlow_RampNotOnLadder".Translate();
			}
			IntVec3 up = loc + rot.FacingCell;
			int d = eng.HollowDepthAt(loc);
			int u = up.InBounds(map) ? eng.HollowDepthAt(up) : d;
			if (!RM_CliffMaskMath.RampJoins(d, u, RM_PitRamp.MaxSpan))
			{
				return "RMFlow_RampMustFaceUphill".Translate(RM_Volume.FormatMetres(RM_PitRamp.MaxSpan));
			}
			return true;
		}

		public override void DrawGhost(ThingDef def, IntVec3 center, Rot4 rot, Color ghostCol, Thing thing = null)
		{
			GenDraw.DrawFieldEdges(new List<IntVec3> { center + rot.FacingCell }, Color.white);
		}
	}
}
