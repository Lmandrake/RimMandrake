using System.Reflection;
using HarmonyLib;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// jawa/static_call read surface for the 2026-10-05 build pass's extension rows
	/// (northstar/extensions.py). Each method takes ONE string, reads live state through the shipping
	/// code's own predicates, and writes nothing except where its doc says so. Dev surface only:
	/// nothing in the game calls it.
	/// </summary>
	public static class RM_NorthstarProofs
	{
		private static bool Cell(string s, out IntVec3 c)
		{
			c = IntVec3.Invalid;
			string[] p = (s ?? "").Split(',');
			if (p.Length != 2 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z))
			{
				return false;
			}
			c = new IntVec3(x, 0, z);
			return true;
		}

		private static Pawn PawnById(Map map, string id)
		{
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				if (p.ThingID == id || p.thingIDNumber.ToString() == id)
				{
					return p;
				}
			}
			return null;
		}

		/// <summary>SUPERDEEP_PRISON_ROOM_1. arg "px,pz|lx,lz" (a pit cell, a lip cell):
		/// "ROOM split=b pitRoom=b proper=b edge=b prison=b roomsOn=b pitId=n lipId=n".</summary>
		public static string ProofRoom(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split('|');
			if (map == null || a.Length != 2 || !Cell(a[0], out IntVec3 pc) || !Cell(a[1], out IntVec3 lc)
				|| !pc.InBounds(map) || !lc.InBounds(map))
			{
				return "REFUSED: arg must be px,pz|lx,lz on the current map";
			}
			Room pit = pc.GetRoom(map);
			Room lip = lc.GetRoom(map);
			if (pit == null || lip == null)
			{
				return "REFUSED: no room at " + (pit == null ? pc : lc);
			}
			return "ROOM split=" + (pit != lip) + " pitRoom=" + RM_PitRooms.IsPitRoom(pit) + " proper=" + pit.ProperRoom
				+ " edge=" + pit.TouchesMapEdge + " prison=" + pit.IsPrisonCell + " roomsOn=" + RM_PitRooms.RoomsOn
				+ " pitId=" + pit.ID + " lipId=" + lip.ID;
		}

		/// <summary>Capture down. arg = target pawn id: "VERDICT v held=b prisoner=b cell=x,z".</summary>
		public static string ProofCaptureDown(string pawnId)
		{
			Map map = Find.CurrentMap;
			Pawn p = map == null ? null : PawnById(map, pawnId);
			if (p == null)
			{
				return "REFUSED: no spawned pawn " + pawnId;
			}
			return "VERDICT " + RM_PitRooms.CaptureDownVerdict(p) + " held=" + RM_SuperdeepTrap.IsHeld(p)
				+ " prisoner=" + p.IsPrisonerOfColony + " cell=" + p.Position.x + "," + p.Position.z;
		}

		/// <summary>Lip service. arg "workerId|x,z|JobDefName": asks the PathFollower patch's own gate
		/// (ShouldServeFromLipFor) and the lip finder: "LIP serve=b kind=k lip=x,z lipSuperdeep=b dist=d".</summary>
		public static string ProofLip(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split('|');
			if (map == null || a.Length != 3 || !Cell(a[1], out IntVec3 target))
			{
				return "REFUSED: arg must be workerId|x,z|JobDefName";
			}
			Pawn w = PawnById(map, a[0]);
			JobDef job = DefDatabase<JobDef>.GetNamedSilentFail(a[2]);
			if (w == null || job == null)
			{
				return "REFUSED: no worker " + a[0] + " or no JobDef " + a[2];
			}
			bool serve = RM_PitRooms.ShouldServeFromLipFor(w, job, target, out RM_PitRoomMath.LipKind kind);
			if (!serve)
			{
				return "LIP serve=False kind=" + kind;
			}
			if (!RM_PitRooms.TryFindLipCell(w, target, kind, out IntVec3 lip))
			{
				return "LIP serve=True kind=" + kind + " lip=none";
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			return "LIP serve=True kind=" + kind + " lip=" + lip.x + "," + lip.z + " lipSuperdeep="
				+ ex.IsSuperdeepExcavation(lip) + " dist=" + lip.DistanceTo(target).ToString("0.##");
		}

		/// <summary>Phase 8 pump. arg "x,z" reads; "x,z|pour" / "x,z|draw" flips the mode as the gizmo does.
		/// "PUMP running=b moved=n pour=b tank=def:units".</summary>
		public static string ProofPump(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split('|');
			if (map == null || !Cell(a[0], out IntVec3 c) || !c.InBounds(map))
			{
				return "REFUSED: arg must be x,z[|pour|draw]";
			}
			Building_LiquidPump pump = c.GetFirstBuilding(map) as Building_LiquidPump;
			if (pump == null)
			{
				return "REFUSED: no RM_LiquidPump at " + c;
			}
			if (a.Length > 1)
			{
				pump.pourMode = a[1] == "pour";
			}
			PropertyInfo running = AccessTools.Property(typeof(Building_LiquidPump), "Running");
			Building_LiquidTank tank = null;
			foreach (IntVec3 n in GenAdj.CellsAdjacent8Way(pump))
			{
				if (n.InBounds(map) && n.GetFirstBuilding(map) is Building_LiquidTank t)
				{
					tank = t;
					break;
				}
			}
			return "PUMP running=" + (running?.GetValue(pump) ?? "?") + " moved=" + pump.Moved + " pour=" + pump.pourMode
				+ " tank=" + (tank == null ? "none" : (tank.storedLiquid?.defName ?? "empty") + ":" + tank.storedUnits);
		}

		/// <summary>EXCAVATION_WALL_ART_1 carrier. arg "x,z": regenerates the cell's section layer and reads it.
		/// "WALLS visible=b verts=n" (verts = the layer's built geometry for that whole section).</summary>
		public static string ProofWallFaces(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null || !Cell(arg, out IntVec3 c) || !c.InBounds(map))
			{
				return "REFUSED: arg must be x,z";
			}
			Section s = map.mapDrawer.SectionAt(c);
			SectionLayer layer = s?.GetLayer(typeof(SectionLayer_RMExcavationWalls));
			if (layer == null)
			{
				return "REFUSED: no SectionLayer_RMExcavationWalls on the section at " + c;
			}
			layer.Regenerate();
			int verts = 0;
			foreach (LayerSubMesh sm in layer.subMeshes)
			{
				verts += sm.verts.Count;
			}
			return "WALLS visible=" + layer.Visible + " verts=" + verts;
		}
	}
}
