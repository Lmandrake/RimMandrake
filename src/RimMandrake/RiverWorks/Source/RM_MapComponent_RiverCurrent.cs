using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.RiverWorks
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
			return RM_RiverCurrentLanes.LaneOf(c.GetTerrain(map));
		}

		public bool HasCurrent(IntVec3 c)
		{
			return LaneAt(c) != RM_RiverMath.LaneNone;
		}

		// ── ticking ───────────────────────────────────────────────────────────

		public override void MapComponentTick()
		{
			if (!RM_RiverWorksSettings.CurrentActive)
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
				surge = RM_RiverWorksSettings.floodSurgeEnabled && RM_RiverWorks.FloodActive(map);
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
			if (RM_RiverWorksSettings.carryItems)
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
				if (t is Pawn ep && RM_RiverWorksSettings.washOffMapEdge)
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
			if (t is Pawn hp && centre && RM_RiverWorksSettings.crossingHazardsEnabled)
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
			if (Rand.Chance(RM_RiverWorksSettings.bruiseChancePerStep))
			{
				p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, Rand.Range(2f, 5f))); // PROVISIONAL amount
			}
			if (!p.Dead && p.carryTracker?.CarriedThing != null && Rand.Chance(RM_RiverWorksSettings.dropChancePerStep))
			{
				p.carryTracker.TryDropCarriedThing(p.Position, ThingPlaceMode.Near, out Thing _);
			}
		}

		private int CadenceFor(Thing t, IntVec3 c)
		{
			return RM_RiverMath.Cadence(LaneAt(c), surge, t is Pawn,
				RM_RiverWorksSettings.currentStrength,
				RM_RiverWorksSettings.scaleWithRiverSize ? sizeFactor : 1f,
				RM_RiverWorksSettings.centreTicksPerCell, RM_RiverWorksSettings.marginTicksPerCell,
				RM_RiverWorksSettings.itemDriftFactor);
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
					if (p.RaceProps.Animal && !RM_RiverWorksSettings.carryAnimals)
					{
						return false;
					}
					if (!p.RaceProps.Animal && !RM_RiverWorksSettings.carryStrangers)
					{
						return false;
					}
				}
				else if (p.RaceProps.Animal && !RM_RiverWorksSettings.carryAnimals)
				{
					return false;
				}
			}
			else if (!RM_RiverWorksSettings.carryItems)
			{
				return false;
			}
			return !IsArrestedOrFord(t.Position);
		}

		private bool IsArrestedOrFord(IntVec3 c)
		{
			return NearFord(c) || RM_RiverWorks.IsArrested(map, c);
		}

		/// <summary>Cells on and beside RM_FordStones are not carried (design §3.7). The sea's
		/// channel current reads the same defName, so this terrain makes its exemption real.</summary>
		public bool NearFord(IntVec3 c)
		{
			if (!RM_RiverWorksSettings.fordsEnabled)
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
