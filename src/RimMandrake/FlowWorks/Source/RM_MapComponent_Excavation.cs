using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// The depth/fill grid and the pulse engine — §6 option B, and the home of
	/// the D/F primitive (ruling 18).
	///
	/// WHY A MAPCOMPONENT AND NOT A THING PER CELL. Three independent problems
	/// converge on one object (spec §6): the channel-constraint problem wants a
	/// channel-aware owner, irrigation wants a per-cell soak map, and ignition
	/// wants something that can walk the liquid backwards toward its source. A
	/// 200-cell canal alight must be one component doing a bounded walk, not
	/// 200 Things each ticking. The in-repo precedent is
	/// FloodedCanyon's RM_MapComponent_CanyonFlood, which already owns a
	/// phased, save-safe, per-cell flow engine; this is a port of that shape,
	/// not an invention.
	///
	/// PILLAR 2 HOLDS. Nothing here runs per tick. MapComponentTick does one
	/// integer compare and returns; the whole sort-and-overflow runs on a
	/// settings-tunable pulse cadence (default 250 ticks, vanilla's own rare
	/// cadence). There is no fluid simulation and there will not be one.
	///
	/// A SOURCE IS TERRAIN (owner ruling 2026-09-16, and ruling 24). A natural
	/// liquid cell is not a building with a comp — it reads as D = SUPERDEEP,
	/// F = SUPERDEEP through a READ-THROUGH ADAPTER below. Nothing is copied
	/// into the byte grids for it, so nothing can fall out of sync with the
	/// map when a lake is drained, dug into, or filled in. Sources in this
	/// pass are all treated as fed (limitless, sticky per ruling 16); a
	/// LIMITED stock with rain/season/seepage refill (rulings 2 and 4) is
	/// bookkeeping this engine has the hooks for and does not yet do.
	/// </summary>
	public class RM_MapComponent_Excavation : MapComponent
	{
		/// <summary>D. 0 = surface; 1..4 = shallow/mid/deep/SUPERDEEP.</summary>
		private byte[] depthGrid;

		/// <summary>F. Always clamped to 0 &lt;= F &lt;= D.</summary>
		private byte[] fillGrid;

		/// <summary>Which liquid this map's excavations carry. One per map this
		/// pass: per-cell liquid identity is the registry's (LiquidDef) and
		/// arrives with it, not here. Null until the first pulse resolves it.</summary>
		private FluidDef activeFluid;

		private int nextPulseTick = -1;

		/// <summary>The running conservation ledger. Every pulse's debits and
		/// credits must sum to zero except liquid destroyed by §5 overflow —
		/// the ONE sanctioned place in the whole design where liquid leaves the
		/// world unspent. Recorded so the exception is disclosed rather than
		/// silent; a silent leak in a conservation-of-mass system reads as a bug.</summary>
		private float overflowDestroyedTotal;

		/// <summary>Derived, never scribed: rebuilt from depthGrid on load.</summary>
		private readonly HashSet<IntVec3> excavatedCells = new HashSet<IntVec3>();

		private readonly HashSet<IntVec3> pulseVisited = new HashSet<IntVec3>();

		private readonly Queue<IntVec3> pulseQueue = new Queue<IntVec3>();

		private readonly List<IntVec3> pulseComponent = new List<IntVec3>();

		private readonly List<IntVec3> pulseRecipients = new List<IntVec3>();

		/// <summary>A single connected excavation this big is already far past
		/// anything a colony digs by hand; the cap exists so one pathological
		/// map cannot turn a bounded pulse into a frame hitch.</summary>
		private const int MaxComponentCells = 6000;

		public RM_MapComponent_Excavation(Map map)
			: base(map)
		{
			EnsureGrids();
		}

		public float OverflowDestroyedTotal => overflowDestroyedTotal;

		public int ExcavatedCellCount => excavatedCells.Count;

		public FluidDef ActiveFluid
		{
			get
			{
				if (activeFluid == null)
				{
					activeFluid = RimMandrakeFlowWorks_DefOf.RM_Fluid_Water;
				}
				return activeFluid;
			}
			set { activeFluid = value; }
		}

		// ── grids ─────────────────────────────────────────────────────────

		private void EnsureGrids()
		{
			int cells = map.cellIndices.NumGridCells;
			if (depthGrid == null || depthGrid.Length != cells)
			{
				depthGrid = new byte[cells];
			}
			if (fillGrid == null || fillGrid.Length != cells)
			{
				fillGrid = new byte[cells];
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			// DataExposeUtility.LookByteArray is vanilla's own map-sized-array
			// idiom (FogGrid/SnowGrid/RoofGrid all route through it): it
			// deflates the array and writes whichever of the compressed or raw
			// base64 form is shorter, and handles the Scribe.mode branch
			// internally, so callers do not guard on it.
			DataExposeUtility.LookByteArray(ref depthGrid, "RM_excavationDepthGrid");
			DataExposeUtility.LookByteArray(ref fillGrid, "RM_excavationFillGrid");
			Scribe_Defs.Look(ref activeFluid, "RM_activeFluid");
			Scribe_Values.Look(ref nextPulseTick, "RM_nextPulseTick", -1);
			Scribe_Values.Look(ref overflowDestroyedTotal, "RM_overflowDestroyedTotal", 0f);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				EnsureGrids();
			}
		}

		public override void FinalizeInit()
		{
			base.FinalizeInit();
			EnsureGrids();
			RehydrateFromTerrainIfEmpty();
			RebuildExcavatedSet();
		}

		/// <summary>A save written before this grid existed has dug cells on the
		/// map and nothing in the grid. Every one of them is RM_Channel_Empty,
		/// i.e. shallow, so D is recoverable exactly. Runs once and only when
		/// the grid is genuinely empty, so it can never stomp a real grid.</summary>
		private void RehydrateFromTerrainIfEmpty()
		{
			for (int i = 0; i < depthGrid.Length; i++)
			{
				if (depthGrid[i] != 0)
				{
					return;
				}
			}
			int recovered = 0;
			foreach (IntVec3 c in map.AllCells)
			{
				byte d = RM_ExcavationDepth.DepthOfDryTerrain(map.terrainGrid.BaseTerrainAt(c));
				if (d != 0)
				{
					depthGrid[map.cellIndices.CellToIndex(c)] = d;
					recovered++;
				}
			}
			if (recovered > 0)
			{
				Log.Message("[RimMandrake.FlowWorks] rehydrated " + recovered +
					" excavated cells from terrain (save predates the depth grid).");
			}
		}

		private void RebuildExcavatedSet()
		{
			excavatedCells.Clear();
			for (int i = 0; i < depthGrid.Length; i++)
			{
				if (depthGrid[i] != 0)
				{
					excavatedCells.Add(map.cellIndices.IndexToCell(i));
				}
			}
		}

		// ── the read-through adapter ──────────────────────────────────────

		private bool IsNaturalLiquid(IntVec3 c)
		{
			TerrainDef baseTerrain = map.terrainGrid.BaseTerrainAt(c);
			return baseTerrain != null && baseTerrain.IsWater;
		}

		/// <summary>A cell that supplies liquid without being excavated: natural
		/// liquid terrain. Ruling 24 — a source is terrain, not a building.</summary>
		public bool IsSourceCell(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return false;
			}
			return depthGrid[map.cellIndices.CellToIndex(c)] == 0 && IsNaturalLiquid(c);
		}

		public bool IsExcavated(IntVec3 c)
		{
			return c.InBounds(map) && depthGrid[map.cellIndices.CellToIndex(c)] != 0;
		}

		/// <summary>D, with natural liquid terrain reading through as SUPERDEEP.
		/// Read-through, not a copy: nothing is written into the grid for a
		/// lake, so the grid can never disagree with the map about one.</summary>
		public byte DepthAt(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return RM_ExcavationDepth.Surface;
			}
			byte d = depthGrid[map.cellIndices.CellToIndex(c)];
			if (d != 0)
			{
				return d;
			}
			return IsNaturalLiquid(c) ? RM_ExcavationDepth.Superdeep : RM_ExcavationDepth.Surface;
		}

		/// <summary>F, with a natural source reading through as full.</summary>
		public byte FillAt(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return 0;
			}
			int i = map.cellIndices.CellToIndex(c);
			byte d = depthGrid[i];
			if (d == 0)
			{
				return IsNaturalLiquid(c) ? RM_ExcavationDepth.Superdeep : (byte)0;
			}
			return fillGrid[i] > d ? d : fillGrid[i];
		}

		// ── digging ───────────────────────────────────────────────────────

		/// <summary>Deepen a cell by one level, to SUPERDEEP at most. Returns the
		/// new D. LAW 1: this is the only thing that ever sets D, and it only
		/// ever goes down.</summary>
		public byte Deepen(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return RM_ExcavationDepth.Surface;
			}
			int i = map.cellIndices.CellToIndex(c);
			byte d = depthGrid[i];
			if (d >= RM_ExcavationDepth.MaxDepth)
			{
				return d;
			}
			d = (byte)(d + 1);
			depthGrid[i] = d;
			excavatedCells.Add(c);
			TerrainDef want = RM_ExcavationDepth.DryTerrainFor(d);
			if (want != null && map.terrainGrid.BaseTerrainAt(c) != want)
			{
				map.terrainGrid.SetTerrain(c, want);
			}
			return d;
		}

		/// <summary>§5's fill-in path will call this when displaced liquid has
		/// nowhere to go. It is the ONE sanctioned exception to conservation of
		/// mass in the whole design, so it is recorded and announced rather
		/// than quietly dropped. The fill-in designator itself is program 2's.</summary>
		public void NotifyOverflowDestroyed(float fillUnits)
		{
			if (fillUnits <= 0f)
			{
				return;
			}
			overflowDestroyedTotal += fillUnits;
			if (Prefs.DevMode)
			{
				Log.Warning("[RimMandrake.FlowWorks] conservation exception: " +
					fillUnits.ToString("F1") + " fill-units overflowed with nowhere to go and were " +
					"destroyed (spec §5 — the only sanctioned case). Map total now " +
					overflowDestroyedTotal.ToString("F1") + ".");
			}
		}

		// ── the pulse ─────────────────────────────────────────────────────

		public override void MapComponentTick()
		{
			base.MapComponentTick();
			if (!RimMandrakeFlowWorksSettings.depthEngineEnabled)
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			if (now < nextPulseTick)
			{
				return;
			}
			nextPulseTick = now + RimMandrakeFlowWorksSettings.PulseIntervalTicks;
			DoPulse();
		}

		/// <summary>§21's algorithm, over each connected excavated set: sort
		/// deepest-first, pour, overflow at F == D into adjacent cells with
		/// room, repeat. A sort plus an overflow, and that is the whole
		/// "physics" — no pressure, no velocity, no simulation.</summary>
		private void DoPulse()
		{
			if (excavatedCells.Count == 0)
			{
				return;
			}
			pulseVisited.Clear();
			foreach (IntVec3 seed in excavatedCells)
			{
				if (pulseVisited.Contains(seed))
				{
					continue;
				}
				pulseComponent.Clear();
				pulseQueue.Clear();
				pulseQueue.Enqueue(seed);
				pulseVisited.Add(seed);
				while (pulseQueue.Count > 0 && pulseComponent.Count < MaxComponentCells)
				{
					IntVec3 c = pulseQueue.Dequeue();
					pulseComponent.Add(c);
					// A source cell JOINS a component as a donor but is never
					// expanded through. Otherwise one channel touching an ocean
					// would walk the ocean, which is thousands of cells of
					// nothing: a source is always full and never needs solving.
					if (IsSourceCell(c))
					{
						continue;
					}
					for (int i = 0; i < 4; i++)
					{
						IntVec3 n = c + GenAdj.CardinalDirections[i];
						if (!n.InBounds(map) || pulseVisited.Contains(n))
						{
							continue;
						}
						if (IsExcavated(n) || IsSourceCell(n))
						{
							pulseVisited.Add(n);
							pulseQueue.Enqueue(n);
						}
					}
				}
				ResolveComponent();
			}
		}

		private void ResolveComponent()
		{
			float before = 0f;
			pulseRecipients.Clear();
			for (int i = 0; i < pulseComponent.Count; i++)
			{
				IntVec3 c = pulseComponent[i];
				if (!IsExcavated(c))
				{
					continue;
				}
				int idx = map.cellIndices.CellToIndex(c);
				before += fillGrid[idx];
				if (fillGrid[idx] < depthGrid[idx])
				{
					pulseRecipients.Add(c);
				}
			}
			if (pulseRecipients.Count == 0)
			{
				RenderComponentFill();
				return;
			}
			// Step 1 of §21: deepest first. The comparison is on D alone, with a
			// cell-index tie-break so the order is identical on every machine
			// and survives a save — a pulse must not depend on hash ordering.
			pulseRecipients.Sort(CompareDeepestFirst);

			float externalCredit = 0f;
			int perCell = RimMandrakeFlowWorksSettings.FlowPerPulse;
			for (int i = 0; i < pulseRecipients.Count; i++)
			{
				IntVec3 r = pulseRecipients[i];
				int ri = map.cellIndices.CellToIndex(r);
				int moved = 0;
				while (moved < perCell && fillGrid[ri] < depthGrid[ri])
				{
					IntVec3 donor = PickDonor(r, depthGrid[ri]);
					if (!donor.IsValid)
					{
						break;
					}
					if (IsSourceCell(donor))
					{
						// Credited from off-map / from the body itself. Under
						// ruling 16 a source is sticky-limitless, so this is a
						// real external credit and not an unbalanced ledger.
						externalCredit += 1f;
					}
					else
					{
						fillGrid[map.cellIndices.CellToIndex(donor)] -= 1;
					}
					fillGrid[ri] += 1;
					moved++;
				}
			}

			float after = 0f;
			for (int i = 0; i < pulseComponent.Count; i++)
			{
				IntVec3 c = pulseComponent[i];
				if (IsExcavated(c))
				{
					after += fillGrid[map.cellIndices.CellToIndex(c)];
				}
			}
			// The ledger. Every transfer inside the component is -1 and +1, so
			// the only legitimate change in total fill is what sources credited
			// in. Anything else is a leak, and a leak is a bug.
			float imbalance = after - before - externalCredit;
			if (Prefs.DevMode && Mathf.Abs(imbalance) > 0.001f)
			{
				Log.Warning("[RimMandrake.FlowWorks] conservation ledger does not balance: " +
					"before=" + before.ToString("F1") + " after=" + after.ToString("F1") +
					" sourceCredit=" + externalCredit.ToString("F1") +
					" imbalance=" + imbalance.ToString("F1") + ". This is a defect, not an overflow.");
			}
			RenderComponentFill();
		}

		private int CompareDeepestFirst(IntVec3 a, IntVec3 b)
		{
			int da = depthGrid[map.cellIndices.CellToIndex(a)];
			int db = depthGrid[map.cellIndices.CellToIndex(b)];
			if (da != db)
			{
				return db - da;
			}
			return map.cellIndices.CellToIndex(a) - map.cellIndices.CellToIndex(b);
		}

		/// <summary>The two clauses that are the entire flow model.
		///
		///   GRAVITY  — a neighbour gives to a DEEPER cell whether or not it is
		///              brimming. That is what makes "a breach into a deeper
		///              cell drains the shallower one" free, and it is what
		///              fills terraces bottom-up.
		///   OVERFLOW — a neighbour at F == D gives to ANY cell with room. This
		///              is the step §21 calls out as load-bearing: without it a
		///              SUPERDEEP source could never feed a shallower canal,
		///              because liquid does not run uphill, and the whole canal
		///              fantasy dies. A source is a full SUPERDEEP cell, so it
		///              spills into any shallower channel dug at its edge.
		///
		/// Deterministic: fixed direction order, strict &gt; on the score, so
		/// ties always resolve to the same neighbour.</summary>
		private IntVec3 PickDonor(IntVec3 r, byte depthR)
		{
			IntVec3 best = IntVec3.Invalid;
			int bestScore = -1;
			for (int i = 0; i < 4; i++)
			{
				IntVec3 n = r + GenAdj.CardinalDirections[i];
				if (!n.InBounds(map))
				{
					continue;
				}
				byte dn;
				byte fn;
				bool source = IsSourceCell(n);
				if (source)
				{
					dn = RM_ExcavationDepth.Superdeep;
					fn = RM_ExcavationDepth.Superdeep;
				}
				else
				{
					int ni = map.cellIndices.CellToIndex(n);
					dn = depthGrid[ni];
					if (dn == 0)
					{
						continue;
					}
					fn = fillGrid[ni];
				}
				if (fn == 0)
				{
					continue;
				}
				if (depthR <= dn && fn < dn)
				{
					continue; // neither deeper than the donor nor brimming
				}
				int score = source ? 1000 : (fn * 10 + dn);
				if (score > bestScore)
				{
					bestScore = score;
					best = n;
				}
			}
			return best;
		}

		// ── rendering F ───────────────────────────────────────────────────

		private void RenderComponentFill()
		{
			FluidDef fluid = ActiveFluid;
			if (fluid == null)
			{
				return;
			}
			for (int i = 0; i < pulseComponent.Count; i++)
			{
				IntVec3 c = pulseComponent[i];
				if (IsExcavated(c))
				{
					ApplyFillTerrain(c, fluid);
				}
			}
		}

		private void ApplyFillTerrain(IntVec3 c, FluidDef fluid)
		{
			int i = map.cellIndices.CellToIndex(c);
			byte d = depthGrid[i];
			byte f = fillGrid[i];
			TerrainDef want = fluid.FillTerrainFor(RM_ExcavationDepth.FillTier(f, d), d);
			TerrainDef cur = map.terrainGrid.TempTerrainAt(c);
			if (cur == want)
			{
				return;
			}
			if (want == null)
			{
				// Only ever clear a temp terrain THIS engine placed. The legacy
				// Flood_FlowWorks release path also writes the temp layer, and
				// an empty engine cell must not strip a release that is still
				// standing — two owners for one cell is the defect the single
				// engine exists to remove, not to reproduce.
				if (cur != null && fluid.OwnsFillTerrain(cur))
				{
					map.terrainGrid.RemoveTempTerrain(c);
				}
				return;
			}
			map.terrainGrid.SetTempTerrain(c, want);
		}

		// ── the gate the legacy flood consults ────────────────────────────

		/// <summary>§4's "biggest gap", closed: liquid may only enter a cell
		/// that has been excavated, or a cell that is already part of a liquid
		/// body. Both are the same test, because a natural body reads through
		/// as SUPERDEEP.</summary>
		public bool CanLiquidEnter(IntVec3 c)
		{
			return DepthAt(c) > RM_ExcavationDepth.Surface;
		}
	}
}
