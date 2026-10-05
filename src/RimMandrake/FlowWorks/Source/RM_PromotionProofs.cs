using System.Collections.Generic;
using System.Text;
using RimMandrake.FlowWorks.Pits;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// State reads for the FlowWorks northstar rows promoted out of validation_v2's UNBUILT register
	/// (2026-10-05): every bar there had a landed feature behind it except viscosity, and a row only stops
	/// being UNBUILT when something in the RUNNING game can be read for it. Each method is a jawa/static_call
	/// target taking one string and answering one line "KEY k=v k=v ...", so the bridge companion needs no
	/// new [Tool] and a stale DLL fails loudly ("Type not found" / "No public static").
	/// Debug surface only: nothing in play calls these.
	/// </summary>
	public static class RM_PromotionProofs
	{
		private static RM_MapComponent_Excavation Engine(out Map map)
		{
			map = Find.CurrentMap;
			return map?.GetComponent<RM_MapComponent_Excavation>();
		}

		private static bool TryCell(string arg, int at, out IntVec3 c)
		{
			c = IntVec3.Invalid;
			string[] p = (arg ?? "").Split(',');
			if (p.Length < at + 2 || !int.TryParse(p[at].Trim(), out int x) || !int.TryParse(p[at + 1].Trim(), out int z))
			{
				return false;
			}
			c = new IntVec3(x, 0, z);
			return true;
		}

		private static string F(float v)
		{
			return v.ToString("0.###", System.Globalization.CultureInfo.InvariantCulture);
		}

		/// <summary>PIT_DEPTH_DRAW_OFFSET_1. arg = a pawn's ThingID. Reads the pawn's REAL DrawPos (through the
		/// Harmony postfix) against its cell centre, so drawDz proves the patch is live, not just the math:
		/// "SINK id=.. cell=x,z depth=D fill=F fluid=.. sink=S drawDz=dz moving=b wallOverHead=r".</summary>
		public static string ProofPawnSink(string pawnId)
		{
			RM_MapComponent_Excavation ex = Engine(out Map map);
			if (ex == null)
			{
				return "REFUSED: no excavation component on the current map";
			}
			Pawn pawn = null;
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				if (p.ThingID == pawnId)
				{
					pawn = p;
					break;
				}
			}
			if (pawn == null)
			{
				return "REFUSED: no spawned pawn " + pawnId;
			}
			IntVec3 c = pawn.Position;
			int depth = ex.ExcavatedDepthAt(c);
			Vector3 draw = pawn.DrawPos;
			float dz = draw.z - c.ToVector3Shifted().z;
			float sink = RM_Patch_PitDepthDrawOffset.SinkOf(pawn, draw);
			float wall = RM_PitDrawMath.WallOverHeadRatio(depth, RimMandrakeFlowWorksSettings.pitSinkPerLevel,
				RM_PitDrawMath.HumanlikeFeetToHeadTop);
			return "SINK id=" + pawnId + " cell=" + c.x + "," + c.z + " depth=" + depth + " fill=" + ex.FillAt(c)
				+ " fluid=" + (ex.FluidAt(c)?.defName ?? "none") + " sink=" + F(sink) + " drawDz=" + F(dz)
				+ " moving=" + (pawn.pather != null && pawn.pather.Moving) + " wallOverHead=" + F(wall)
				+ " enabled=" + RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled;
		}

		/// <summary>LADDER_PRISON_DOOR_1. arg = "x,z,op", op raise | lower | read. Writes RM_CompLadder.raised the
		/// way the gizmo does and reads it back with the inspect line a player sees:
		/// "LADDER cell=x,z present=b raised=b inspect=...".</summary>
		public static string ProofLadder(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null || !TryCell(arg, 0, out IntVec3 c))
			{
				return "REFUSED: arg must be x,z,raise|lower|read on a current map";
			}
			string op = arg.Split(',').Length > 2 ? arg.Split(',')[2].Trim().ToLowerInvariant() : "read";
			RM_CompLadder comp = null;
			foreach (Thing t in c.GetThingList(map))
			{
				if (t.def == RimMandrakeFlowWorks_DefOf.RM_Ladder)
				{
					comp = t.TryGetComp<RM_CompLadder>();
					break;
				}
			}
			if (comp == null)
			{
				return "LADDER cell=" + c.x + "," + c.z + " present=False raised=None inspect=none";
			}
			if (op == "raise")
			{
				comp.raised = true;
			}
			else if (op == "lower")
			{
				comp.raised = false;
			}
			string inspect = (comp.CompInspectStringExtra() ?? "none").Replace(' ', '_');
			return "LADDER cell=" + c.x + "," + c.z + " present=True raised=" + comp.raised + " inspect=" + inspect;
		}

		/// <summary>PIT_COVER_FALL_REWIRE_1. arg = "x,z". What the cover over a superdeep cell prints against
		/// what the cell really is, and the majority terrain of its non-excavated 8-neighbours read straight off
		/// the terrain grid: "COVER cell=x,z present=b covered=b sprung=b depth=D cellTerrain=.. printed=..
		/// matOk=b around=.. inspect=..".</summary>
		public static string ProofCover(string arg)
		{
			RM_MapComponent_Excavation ex = Engine(out Map map);
			if (ex == null || !TryCell(arg, 0, out IntVec3 c) || !c.InBounds(map))
			{
				return "REFUSED: arg must be x,z on a current map with FlowWorks";
			}
			Building_PitCover cover = RM_PitCoverUtility.CoverAt(map, c);
			var counts = new Dictionary<string, int>();
			for (int i = 0; i < 8; i++)
			{
				IntVec3 n = c + GenAdj.AdjacentCells[i];
				if (!n.InBounds(map) || ex.IsExcavated(n))
				{
					continue;
				}
				string t = n.GetTerrain(map)?.defName ?? "null";
				counts[t] = counts.TryGetValue(t, out int k) ? k + 1 : 1;
			}
			string around = "none";
			int best = -1;
			foreach (KeyValuePair<string, int> kv in counts)
			{
				if (kv.Value > best)
				{
					best = kv.Value;
					around = kv.Key;
				}
			}
			TerrainDef printed = RM_PitCoverUtility.SurfaceAround(map, c);
			var sb = new StringBuilder("COVER cell=" + c.x + "," + c.z);
			sb.Append(" present=" + (cover != null));
			sb.Append(" covered=" + (cover != null && cover.Covered));
			sb.Append(" sprung=" + (cover != null && cover.Sprung));
			sb.Append(" depth=" + ex.ExcavatedDepthAt(c));
			sb.Append(" cellTerrain=" + (c.GetTerrain(map)?.defName ?? "null"));
			sb.Append(" printed=" + (printed?.defName ?? "null"));
			sb.Append(" matOk=" + (printed?.graphic?.MatSingle != null));
			sb.Append(" around=" + around);
			sb.Append(" inspect=" + (cover == null ? "none" : (cover.GetInspectString() ?? "").Replace(' ', '_').Replace('\n', '/')));
			return sb.ToString();
		}

		/// <summary>LIQUID_BODY_FLUID_IDENTITY_1 / viscosity. arg = "x,z,w,h". One token per cell, row-major:
		/// "ROW x,z:D/F/fluid/terrain;..." (terrain is TerrainAt, the temp fill layer included), plus the map's
		/// pulse count so a reader can tell where a viscous fluid's cadence stands.</summary>
		public static string ProofFluidRow(string arg)
		{
			RM_MapComponent_Excavation ex = Engine(out Map map);
			string[] p = (arg ?? "").Split(',');
			if (ex == null || p.Length != 4 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z)
				|| !int.TryParse(p[2], out int w) || !int.TryParse(p[3], out int h) || w * h > 400)
			{
				return "REFUSED: arg must be x,z,w,h (w*h <= 400) on a current map with FlowWorks";
			}
			var sb = new StringBuilder("ROW pulse=" + ex.PulseCount + " viscosity=" + RimMandrakeFlowWorksSettings.viscosityEnabled + " ");
			for (int j = 0; j < h; j++)
			{
				for (int i = 0; i < w; i++)
				{
					IntVec3 c = new IntVec3(x + i, 0, z + j);
					if (!c.InBounds(map))
					{
						continue;
					}
					sb.Append(c.x).Append(',').Append(c.z).Append(':').Append(ex.ExcavatedDepthAt(c)).Append('/')
						.Append(ex.FillAt(c)).Append('/').Append(ex.FluidAt(c)?.defName ?? "none").Append('/')
						.Append(c.GetTerrain(map)?.defName ?? "null").Append(';');
				}
			}
			return sb.ToString();
		}
	}
}
