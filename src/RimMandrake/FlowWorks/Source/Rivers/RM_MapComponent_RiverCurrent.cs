using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Rivers
{
	/// <summary>
	/// SURFACE_RIVER_WEIRS_1 slice 1 — the surface current (design §3.1).
	///
	/// Direction comes from vanilla's own per-cell river flow vector
	/// (<c>map.waterInfo.riverFlowMap</c>, written by TileMutatorWorker_River and saved by
	/// WaterInfo), quantised to 8 compass steps once per map. Nothing is authored or saved
	/// here, so adding or removing the mod mid-game is safe. Lane is read live from the
	/// terrain, so a bridge or ford laid later simply stops reading as river.
	///
	/// The shove itself is TerminalBiomes' proven idiom (register every 250 ticks, step every
	/// 15; pawn: StopDead + Position + Notify_Teleported), re-written here as new code rather
	/// than moved, because that file is live sea content. Moving it is the next slice.
	/// </summary>
	public class RM_MapComponent_RiverCurrent : MapComponent
	{
		private const int ScanIntervalTicks = 250;

		private const int ProcessIntervalTicks = 15;

		private sbyte[] flowDir;

		private bool gridBuilt;

		private bool anyCurrent;

		private float sizeFactor = 1f;

		private bool surge;

		private bool warnedThisMap;

		private int scanCooldown;

		private int processCooldown;

		private readonly Dictionary<Thing, int> nextMoveTick = new Dictionary<Thing, int>();

		private TerrainDef fordDef;

		private bool fordLooked;

		// Slice 2: the works' footprint on the current - weir slack pools (lane drops one) and ferry
		// rope lines (not carried). Derived from the buildings, never saved; rebuilt when dirty.
		private readonly HashSet<int> poolCells = new HashSet<int>();

		private readonly HashSet<int> ropeCells = new HashSet<int>();

		private bool worksDirty = true;

		public RM_MapComponent_RiverCurrent(Map map) : base(map)
		{
		}

		public bool AnyCurrent
		{
			get
			{
				EnsureGrid();
				return anyCurrent;
			}
		}

		public bool SurgeActive => surge;

		public void MarkWorksDirty()
		{
			worksDirty = true;
		}

		public int PoolCellCount
		{
			get
			{
				EnsureWorks();
				return poolCells.Count;
			}
		}

		public int RopeCellCount
		{
			get
			{
				EnsureWorks();
				return ropeCells.Count;
			}
		}

		public bool InPool(IntVec3 c)
		{
			EnsureWorks();
			return c.InBounds(map) && poolCells.Contains(map.cellIndices.CellToIndex(c));
		}

		/// <summary>The rope cells as last built, WITHOUT rebuilding: read from inside the path grid's
		/// own recompute (RM_RopePathing), where a rebuild would notify the grid re-entrantly.</summary>
		public HashSet<int> RopeIndicesNoRebuild => ropeCells;

		private bool ropeGuidedLast;

		public bool OnRope(IntVec3 c)
		{
			EnsureWorks();
			return c.InBounds(map) && ropeCells.Contains(map.cellIndices.CellToIndex(c));
		}

		private void EnsureWorks()
		{
			if (!worksDirty)
			{
				return;
			}
			worksDirty = false;
			HashSet<int> ropeBefore = new HashSet<int>(ropeCells);
			bool guidedBefore = ropeGuidedLast;
			poolCells.Clear();
			ropeCells.Clear();
			try
			{
				RebuildWorks();
			}
			finally
			{
				ropeGuidedLast = RM_RopePathing.Active;
				NotifyRopeDelta(ropeBefore, guidedBefore != ropeGuidedLast);
			}
		}

		/// <summary>Rope cells that appeared or vanished (or all of them, when the guide setting
		/// flipped) are re-read by the path grid, so undrafted routing follows the rope at once.</summary>
		private void NotifyRopeDelta(HashSet<int> before, bool all)
		{
			PathFinderMapData data = map.pathFinder?.MapData;
			if (data == null)
			{
				return;
			}
			foreach (int i in before)
			{
				if (all || !ropeCells.Contains(i))
				{
					data.Notify_CellDelta(map.cellIndices.IndexToCell(i));
				}
			}
			foreach (int i in ropeCells)
			{
				if (all || !before.Contains(i))
				{
					data.Notify_CellDelta(map.cellIndices.IndexToCell(i));
				}
			}
		}

		private void RebuildWorks()
		{
			if (!RM_RiversSettings.WorksActive)
			{
				return;
			}
			EnsureGrid();
			ThingDef weir = RM_RiverWorksDefOf.RM_BankWeir;
			if (weir != null && anyCurrent)
			{
				List<Thing> ws = map.listerThings.ThingsOfDef(weir);
				for (int i = 0; i < ws.Count; i++)
				{
					(ws[i] as RM_Building_BankWeir)?.AddPoolCells(this, poolCells);
				}
			}
			ThingDef post = RM_RiverWorksDefOf.RM_FerryPost;
			if (post != null && RM_RiversSettings.ferryEnabled)
			{
				List<Thing> ps = map.listerThings.ThingsOfDef(post);
				for (int i = 0; i < ps.Count; i++)
				{
					(ps[i] as RM_Building_FerryPost)?.AddRopeCells(ropeCells);
				}
			}
		}

		public float SizeFactor => sizeFactor;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref warnedThisMap, "rmRiverWarned", false);
		}

		// ── the grid ──────────────────────────────────────────────────────────

		private void EnsureGrid()
		{
			if (gridBuilt)
			{
				return;
			}
			gridBuilt = true;
			int n = map.cellIndices.NumGridCells;
			flowDir = new sbyte[n];
			for (int i = 0; i < n; i++)
			{
				flowDir[i] = -1;
			}
			List<float> flow = map.waterInfo?.riverFlowMap;
			if (flow == null || flow.Count < n * 2)
			{
				return; // no river mutator ran on this map: no current anywhere
			}
			int sizeZ = map.Size.z;
			foreach (IntVec3 c in map.AllCells)
			{
				int fi = (c.x * sizeZ + c.z) * 2; // WaterInfo.GetWaterMovement's own indexing
				int dir = RM_RiverMath.Quantise(flow[fi], flow[fi + 1]);
				if (dir >= 0)
				{
					flowDir[map.cellIndices.CellToIndex(c)] = (sbyte)dir;
					anyCurrent = true;
				}
			}
			sizeFactor = RiverSizeFactor();
		}

		private float RiverSizeFactor()
		{
			float width = 0f;
			if (map.TileInfo is SurfaceTile st && st.Rivers != null)
			{
				for (int i = 0; i < st.Rivers.Count; i++)
				{
					RiverDef r = st.Rivers[i].river;
					if (r != null && r.widthOnMap > width)
					{
						width = r.widthOnMap;
					}
				}
			}
			return RM_RiverMath.SizeFactor(width);
		}

		/// <summary>Compass index 0..7 of the current at c, or -1.</summary>
		public int FlowDirAt(IntVec3 c)
		{
			EnsureGrid();
			if (!c.InBounds(map))
			{
				return -1;
			}
			return flowDir[map.cellIndices.CellToIndex(c)];
		}

		public int LaneAt(IntVec3 c)
		{
			if (!c.InBounds(map) || FlowDirAt(c) < 0)
			{
				return RM_RiverMath.LaneNone;
			}
			int lane = RM_RiverCurrentLanes.LaneOf(c.GetTerrain(map));
			if (lane != RM_RiverMath.LaneNone && InPool(c))
			{
				lane = RM_RiverMath.PoolLane(lane); // the weir's slack water drops one lane
			}
			return lane;
		}

		public bool HasCurrent(IntVec3 c)
		{
			return LaneAt(c) != RM_RiverMath.LaneNone;
		}

		// ── ticking ───────────────────────────────────────────────────────────

		public override void MapComponentTick()
		{
			if (!RM_RiversSettings.CurrentActive)
			{
				if (nextMoveTick.Count > 0)
				{
					nextMoveTick.Clear();
				}
				return;
			}
			EnsureGrid();
			if (!anyCurrent)
			{
				return;
			}
			if (--scanCooldown <= 0)
			{
				scanCooldown = ScanIntervalTicks;
				worksDirty = true; // cheap: a weir's HP-driven re-arm or a settings flip shows up within 250 ticks
				surge = RM_RiversSettings.floodSurgeEnabled && RM_RiverWorks.FloodActive(map);
				Scan();
			}
			if (--processCooldown <= 0)
			{
				processCooldown = ProcessIntervalTicks;
				Process();
			}
		}

		private void Scan()
		{
			List<Thing> candidates = new List<Thing>(map.mapPawns.AllPawnsSpawned);
			if (RM_RiversSettings.carryItems)
			{
				candidates.AddRange(map.listerThings.ThingsInGroup(ThingRequestGroup.HaulableEver));
			}
			HashSet<Thing> present = new HashSet<Thing>();
			for (int i = 0; i < candidates.Count; i++)
			{
				Thing t = candidates[i];
				if (t == null || t.Destroyed || !t.Spawned || !IsCarried(t) || !HasCurrent(t.Position))
				{
					continue;
				}
				present.Add(t);
				if (!nextMoveTick.ContainsKey(t))
				{
					nextMoveTick[t] = Find.TickManager.TicksGame + CadenceFor(t, t.Position);
					if (t is Pawn p)
					{
						MaybeWarnFirstEntry(p);
					}
				}
			}
			if (nextMoveTick.Count == present.Count)
			{
				return;
			}
			List<Thing> stale = new List<Thing>();
			foreach (Thing k in nextMoveTick.Keys)
			{
				if (!present.Contains(k))
				{
					stale.Add(k);
				}
			}
			for (int i = 0; i < stale.Count; i++)
			{
				nextMoveTick.Remove(stale[i]);
			}
		}

		private void Process()
		{
			if (nextMoveTick.Count == 0)
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			List<Thing> keys = new List<Thing>(nextMoveTick.Keys);
			for (int i = 0; i < keys.Count; i++)
			{
				Thing t = keys[i];
				if (t == null || t.Destroyed || !t.Spawned || t.Map != map)
				{
					nextMoveTick.Remove(t);
					continue;
				}
				if (nextMoveTick.TryGetValue(t, out int due) && now >= due)
				{
					StepOne(t);
				}
			}
		}

		/// <summary>One shove. Public so the first script can drive it deterministically.</summary>
		public void StepOne(Thing t)
		{
			IntVec3 pos = t.Position;
			int lane = LaneAt(pos);
			int dir = FlowDirAt(pos);
			if (lane == RM_RiverMath.LaneNone || dir < 0 || !IsCarried(t))
			{
				nextMoveTick.Remove(t);
				return;
			}
			IntVec3 next = new IntVec3(pos.x + RM_RiverMath.StepX[dir], 0, pos.z + RM_RiverMath.StepZ[dir]);
			if (!next.InBounds(map))
			{
				nextMoveTick.Remove(t);
				if (t is Pawn ep && RM_RiversSettings.washOffMapEdge)
				{
					RM_WorldComponent_SweptAway.WashAway(ep);
				}
				return; // items, and pawns with the edge rule off, stop at the edge
			}
			if (!next.Standable(map))
			{
				nextMoveTick.Remove(t);
				return; // a bend, a wall, a bridge pier: the carry ends here
			}
			bool centre = RM_RiverMath.BehavesAsCentre(lane, surge);
			Move(t, next);
			if (t is Pawn hp && centre && RM_RiversSettings.crossingHazardsEnabled)
			{
				ApplyHazards(hp);
			}
			if (t.Destroyed || !t.Spawned || IsArrestedOrFord(next))
			{
				nextMoveTick.Remove(t);
				return;
			}
			nextMoveTick[t] = Find.TickManager.TicksGame + CadenceFor(t, next);
		}

		private static void Move(Thing t, IntVec3 next)
		{
			if (t is Pawn pawn)
			{
				pawn.pather?.StopDead();
				pawn.Position = next;
				pawn.Notify_Teleported(false);
			}
			else
			{
				t.Position = next;
			}
		}

		private static void ApplyHazards(Pawn p)
		{
			if (p.Dead)
			{
				return;
			}
			// Owner card 2: "being swept bruises and can make a pawn drop what it carries".
			if (Rand.Chance(RM_RiversSettings.bruiseChancePerStep))
			{
				p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, Rand.Range(2f, 5f))); // PROVISIONAL amount
			}
			if (!p.Dead && p.carryTracker?.CarriedThing != null && Rand.Chance(RM_RiversSettings.dropChancePerStep))
			{
				p.carryTracker.TryDropCarriedThing(p.Position, ThingPlaceMode.Near, out Thing _);
			}
		}

		private int CadenceFor(Thing t, IntVec3 c)
		{
			return RM_RiverMath.Cadence(LaneAt(c), surge, t is Pawn,
				RM_RiversSettings.currentStrength,
				RM_RiversSettings.scaleWithRiverSize ? sizeFactor : 1f,
				RM_RiversSettings.centreTicksPerCell, RM_RiversSettings.marginTicksPerCell,
				RM_RiversSettings.itemDriftFactor);
		}

		// ── who is carried ────────────────────────────────────────────────────

		/// <summary>Design §3.1: pawns, corpses and loose items. Never buildings, fliers,
		/// river-native races, or anything on/beside a ford or in an arrested cell.</summary>
		public bool IsCarried(Thing t)
		{
			if (t is Building || t.def.category == ThingCategory.Building)
			{
				return false;
			}
			if (t is Pawn p)
			{
				if (p.Flying || p.def.GetModExtension<RM_RiverNativeExtension>() != null)
				{
					return false;
				}
				bool player = p.Faction != null && p.Faction.IsPlayer;
				if (!player && p.HostFaction != null && p.HostFaction.IsPlayer)
				{
					player = true; // prisoners and guests are ours to lose
				}
				if (!player)
				{
					if (p.RaceProps.Animal && !RM_RiversSettings.carryAnimals)
					{
						return false;
					}
					if (!p.RaceProps.Animal && !RM_RiversSettings.carryStrangers)
					{
						return false;
					}
				}
				else if (p.RaceProps.Animal && !RM_RiversSettings.carryAnimals)
				{
					return false;
				}
			}
			else if (!RM_RiversSettings.carryItems)
			{
				return false;
			}
			return !IsArrestedOrFord(t.Position);
		}

		private bool IsArrestedOrFord(IntVec3 c)
		{
			if (NearFord(c) || RM_RiverWorks.IsArrested(map, c))
			{
				return true;
			}
			if (!RM_RiversSettings.WorksActive)
			{
				return false;
			}
			return RM_CompRiverArrester.CellArrested(map, c) || (RM_RiversSettings.ferryEnabled && OnRope(c));
		}

		/// <summary>Cells on and beside RM_FordStones are not carried (design §3.7). The sea's
		/// channel current reads the same defName, so this terrain makes its exemption real.</summary>
		public bool NearFord(IntVec3 c)
		{
			if (!RM_RiversSettings.fordsEnabled)
			{
				return false;
			}
			if (!fordLooked)
			{
				fordDef = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_FordStones");
				fordLooked = true;
			}
			if (fordDef == null || !c.InBounds(map))
			{
				return false;
			}
			if (c.GetTerrain(map) == fordDef)
			{
				return true;
			}
			for (int i = 0; i < 8; i++)
			{
				IntVec3 a = c + GenAdj.AdjacentCells[i];
				if (a.InBounds(map) && a.GetTerrain(map) == fordDef)
				{
					return true;
				}
			}
			return false;
		}

		private void MaybeWarnFirstEntry(Pawn p)
		{
			if (warnedThisMap || p.Faction == null || !p.Faction.IsPlayer)
			{
				return;
			}
			warnedThisMap = true;
			Messages.Message(p.LabelShortCap + " is being swept downstream by the river's current. "
			  + "Fast water cannot be waded out of; build a ford or a bridge to cross.",
				p, MessageTypeDefOf.NegativeEvent);
		}
	}
}
