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
			// through the gizmo's own writer, so reachability, the cliff masks and the path grid hear of it (writing the field
			// alone left every route planned against the old ladder state)
			if (op == "raise")
			{
				comp.SetRaised(true);
			}
			else if (op == "lower")
			{
				comp.SetRaised(false);
			}
			string inspect = (comp.CompInspectStringExtra() ?? "none").Replace(' ', '_');
			return "LADDER cell=" + c.x + "," + c.z + " present=True raised=" + comp.raised + " inspect=" + inspect;
		}

		/// <summary>FLOWWORKS_FORCED_PIT_FALL_ROW_1. arg = "pawnId,x,z". Launches the pawn as a vanilla
		/// PawnFlyer (ThingDefOf.PawnFlyer, the same MakeFlyer + GenSpawn.Spawn-at-destination pair
		/// JumpUtility.DoJump uses) to land on x,z, so the landing runs through PawnFlyer.RespawnPawn and
		/// RM_Patch_PawnFlyer_LandInPit exactly as a real forced arrival would. No fall is applied here:
		/// "FLYER id=.. from=x,z to=x,z depth=D launched=b".</summary>
		public static string ProofForcedFlyer(string arg)
		{
			RM_MapComponent_Excavation ex = Engine(out Map map);
			string[] p = (arg ?? "").Split(',');
			if (ex == null || p.Length < 3 || !TryCell(arg, 1, out IntVec3 dest) || !dest.InBounds(map))
			{
				return "REFUSED: arg must be pawnId,x,z on a current map with FlowWorks";
			}
			string id = p[0].Trim();
			Pawn pawn = null;
			foreach (Pawn q in map.mapPawns.AllPawnsSpawned)
			{
				if (q.ThingID == id)
				{
					pawn = q;
					break;
				}
			}
			if (pawn == null)
			{
				return "REFUSED: no spawned pawn " + id;
			}
			IntVec3 from = pawn.Position;
			PawnFlyer flyer = PawnFlyer.MakeFlyer(ThingDefOf.PawnFlyer, pawn, dest, null, null);
			bool launched = flyer != null && GenSpawn.Spawn(flyer, dest, map) != null;
			return "FLYER id=" + id + " from=" + from.x + "," + from.z + " to=" + dest.x + "," + dest.z
				+ " depth=" + ex.ExcavatedDepthAt(dest) + " launched=" + launched;
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
		/// <summary>POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD live row L8 (northstar/liquid_checks.py): the pond indexed at "x,z" —
		/// its drawdown s, part-level r, picture wet count, stock, and a terrain census over its footprint (deep, chest, shallow,
		/// thin, own = still its original water, mud, lakebed, other). Read-only; never forms a body.</summary>
		public static string ProofPondDepth(string arg)
		{
			RM_MapComponent_Excavation ex = Engine(out Map map);
			string[] p = (arg ?? "").Split(',');
			if (ex == null || p.Length != 2 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z))
			{
				return "REFUSED: arg must be x,z on a current map with FlowWorks";
			}
			IntVec3 at = new IntVec3(x, 0, z);
			RM_LiquidBody body = at.InBounds(map) ? ex.Stock.IndexedBodyAt(map, at) : null;
			if (body == null)
			{
				return "REFUSED: no formed pond at " + x + "," + z;
			}
			int deep = 0, chest = 0, shallow = 0, thin = 0, own = 0, mud = 0, lakebed = 0, other = 0;
			TerrainDef mudDef = (body.fluid ?? ex.ActiveFluid)?.recededTerrain;
			foreach (IntVec3 c in body.cells)
			{
				if (!c.InBounds(map) || ex.IsExcavated(c))
				{
					continue;
				}
				TerrainDef t = map.terrainGrid.BaseTerrainAt(c);
				TerrainDef first = ex.OriginalTerrainAt(c);
				if (t == RimMandrakeFlowWorks_DefOf.RM_WaterThin) thin++;
				else if (t == RimMandrakeFlowWorks_DefOf.RM_WaterChestDeepStill) chest++;
				else if (t != null && t.IsWater && (first == null || first == t)) own++;
				else if (t == TerrainDefOf.WaterDeep) deep++;
				else if (t == TerrainDefOf.WaterShallow) shallow++;
				else if (t == mudDef) mud++;
				else if (t == RimMandrakeFlowWorks_DefOf.RM_Lakebed_Shallow || t == RimMandrakeFlowWorks_DefOf.RM_Lakebed_Deep
					|| t == RimMandrakeFlowWorks_DefOf.RM_Lakebed_Abyss) lakebed++;
				else other++;
			}
			bool applies = ex.Stock.DepthModelApplies(map, body, ex);
			ex.Stock.DepthReport(map, body, ex, out int s, out int r, out int wet);
			return "POND id=" + body.id + " pulse=" + ex.PulseCount + " model=" + ex.PondDepthModel + " applies=" + applies
				+ " limitless=" + body.limitless + " stock=" + body.stock.ToString("F2") + " capacity=" + body.capacity.ToString("F2")
				+ " s=" + s + " r=" + r + " wet=" + wet + " census=deep:" + deep + ",chest:" + chest + ",shallow:" + shallow
				+ ",thin:" + thin + ",own:" + own + ",mud:" + mud + ",lakebed:" + lakebed + ",other:" + other;
		}

		public static string ProofFluidRow(string arg)
		{
			RM_MapComponent_Excavation ex = Engine(out Map map);
			string[] p = (arg ?? "").Split(',');
			if (ex == null || p.Length != 4 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z)
				|| !int.TryParse(p[2], out int w) || !int.TryParse(p[3], out int h)
				|| w < 1 || h < 1 || w > 400 || h > 400 || w * h > 400)   // C8b-F6: no overflow, no negatives
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
