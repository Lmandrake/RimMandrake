using System.Collections.Generic;
using RimWorld;
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

		/// <summary>PHASE 4. The map's memory of what a cell was before FlowWorks
		/// touched its base terrain — written the first time a cell is dug, and
		/// the first time a natural liquid cell is dried by recession.
		///
		/// 🔴 THIS IS WHAT STOPS THE ENGINE LAUNDERING THE MAP. A receding pond
		/// writes dry terrain over a lake cell; a fill-in takes an excavation
		/// back to the surface. Without a record, both hand back generic soil
		/// and the map is permanently, silently altered by a mechanic that is
		/// supposed to be reversible. §5 names this explicitly and it is the one
		/// piece of Phase 4 that is a correctness requirement rather than a
		/// feature.</summary>
		private Dictionary<int, TerrainDef> originalTerrain = new Dictionary<int, TerrainDef>();

		private List<int> originalTerrainKeys;

		private List<TerrainDef> originalTerrainValues;

		/// <summary>PHASE 4. Stock, budget, classification, recession, refill.
		/// Held here rather than in a MapComponent of its own so that debits
		/// land in a defined order relative to the flow that caused them.</summary>
		private RM_LiquidStock stock = new RM_LiquidStock();

		/// <summary>Rain arrives in fractions of a fill level; a level is an
		/// integer. This carries the remainder between pulses so a light drizzle
		/// eventually fills a trench instead of rounding to nothing forever.</summary>
		private float rainAccumulator;

		/// <summary>Disclosed the same way <see cref="overflowDestroyedTotal"/>
		/// is, and kept SEPARATE from it on purpose (ruling 9): liquid down a
		/// sink is transferred off-map, not destroyed. A drain that deletes
		/// liquid and a drain that returns it to the world look identical on
		/// screen and are very different rules, so they are different counters.</summary>
		private float sinkTransferredTotal;

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

		// ════════════════════════════════════════════════════════════════
		// PHASE 5 — SUPERDEEP. Additive: nothing above was changed to add it.
		//
		// 🔴 IsSuperdeepExcavation IS NOT DepthAt >= Superdeep. DepthAt is the
		// read-through adapter and reports natural liquid terrain as SUPERDEEP,
		// which is correct for FLOW (a lake is a full deep cell) and catastrophic
		// for CAPTURE and for ruling 23 — every pawn wading a river would be
		// swallowed, and no shot could cross any water on the map. Capture and
		// the shooting rule are about a hole somebody dug, so they read the grid
		// and only the grid.
		// ════════════════════════════════════════════════════════════════

		/// <summary>Maintained incrementally so ruling 23's per-shot check can
		/// early-out in one int compare on the ~every map where nothing has been
		/// dug this deep.</summary>
		private int superdeepCellCount;

		public int SuperdeepCellCount => superdeepCellCount;

		public bool IsSuperdeepExcavation(IntVec3 c)
		{
			return c.InBounds(map)
				&& depthGrid[map.cellIndices.CellToIndex(c)] >= RM_ExcavationDepth.Superdeep;
		}

		/// <summary>Every excavated cell at D = 4. Walks the excavated set, not
		/// the whole map.</summary>
		public IEnumerable<IntVec3> SuperdeepCells()
		{
			foreach (IntVec3 c in excavatedCells)
			{
				if (depthGrid[map.cellIndices.CellToIndex(c)] >= RM_ExcavationDepth.Superdeep)
				{
					yield return c;
				}
			}
		}

		/// <summary>PHASE 4's stock model, for inspect strings and debug
		/// surfaces. Never null after construction.</summary>
		public RM_LiquidStock Stock => stock;

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
			// PHASE 4. Everything persistent the stock model adds is scribed
			// here: the original-terrain record, the bodies (their sticky
			// classification, stock, capacity, footprint and receded list, via
			// RM_LiquidBody.ExposeData), the rain remainder and the sink total.
			Scribe_Collections.Look(ref originalTerrain, "RM_originalTerrain",
				LookMode.Value, LookMode.Def, ref originalTerrainKeys, ref originalTerrainValues);
			Scribe_Deep.Look(ref stock, "RM_liquidStock");
			Scribe_Values.Look(ref rainAccumulator, "RM_rainAccumulator", 0f);
			Scribe_Values.Look(ref sinkTransferredTotal, "RM_sinkTransferredTotal", 0f);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				EnsureGrids();
				if (originalTerrain == null)
				{
					originalTerrain = new Dictionary<int, TerrainDef>();
				}
				if (stock == null)
				{
					stock = new RM_LiquidStock();
				}
			}
		}

		public override void FinalizeInit()
		{
			base.FinalizeInit();
			EnsureGrids();
			RehydrateFromTerrainIfEmpty();
			RebuildExcavatedSet();
			if (originalTerrain == null)
			{
				originalTerrain = new Dictionary<int, TerrainDef>();
			}
			if (stock == null)
			{
				stock = new RM_LiquidStock();
			}
			stock.RebuildIndex(map);
			// PHASE 5. Grow the SUPERDEEP holders a save predating this phase
			// never had, and shed the ones a save has if capture is now off.
			RM_SuperdeepCapture.SyncMap(map, this);
			syncedCaptureEnabled = RimMandrakeFlowWorksSettings.superdeepCaptureEnabled;
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
			superdeepCellCount = 0;
			for (int i = 0; i < depthGrid.Length; i++)
			{
				if (depthGrid[i] != 0)
				{
					excavatedCells.Add(map.cellIndices.IndexToCell(i));
					if (depthGrid[i] >= RM_ExcavationDepth.Superdeep)
					{
						superdeepCellCount++;
					}
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
			// PHASE 4: remember what was here BEFORE the first cut, so a fill-in
			// can hand the exact terrain back instead of generic soil. Recorded
			// on the transition out of surface only — deepening an existing
			// channel must not overwrite the record with RM_Channel_Empty.
			if (d == RM_ExcavationDepth.Surface)
			{
				RecordOriginalTerrain(c);
			}
			d = (byte)(d + 1);
			depthGrid[i] = d;
			excavatedCells.Add(c);
			TerrainDef want = RM_ExcavationDepth.DryTerrainFor(d);
			if (want != null && map.terrainGrid.BaseTerrainAt(c) != want)
			{
				map.terrainGrid.SetTerrain(c, want);
			}
			// PHASE 5, ruling 26. The last cut is the one that makes the cell a
			// trap, so the holder arrives with it and not before.
			if (d >= RM_ExcavationDepth.Superdeep)
			{
				superdeepCellCount++;
				RM_SuperdeepCapture.EnsureHolder(map, c);
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

		// ── filling in (PHASE 2's other half) ─────────────────────────────

		/// <summary>Can this cell be filled back in? Excavated cells only. A
		/// natural water cell is NOT fillable here: §18 gives that its own rule
		/// (most-abundant non-liquid neighbour, mud drying to rich soil, a haul
		/// cost) and it is a separate mechanic wearing the same word.</summary>
		public bool CanFillIn(IntVec3 c)
		{
			return c.InBounds(map) && depthGrid[map.cellIndices.CellToIndex(c)] != 0;
		}

		/// <summary>
		/// Raise a cell one level, displacing whatever no longer fits.
		///
		/// OWNER, 2026-09-16: <i>"There should also be a way to 'fill in' a canal
		/// that displaces liquid BACK. It does not destroy liquid if there's a
		/// place for it to go, but if it would 'overflow' it is destroyed."</i>
		///
		/// The displaced amount is what the new, shallower cell can no longer
		/// hold: <c>F - (D-1)</c>, clamped at zero. A trench holding one level
		/// out of four loses nothing when it is raised to three — the liquid
		/// simply sits higher, which is what actually happens when you shovel
		/// earth in under it.
		///
		/// Returns the new D.
		/// </summary>
		public byte FillIn(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return RM_ExcavationDepth.Surface;
			}
			int i = map.cellIndices.CellToIndex(c);
			byte d = depthGrid[i];
			if (d == 0)
			{
				return RM_ExcavationDepth.Surface;
			}
			byte f = fillGrid[i] > d ? d : fillGrid[i];
			byte newD = (byte)(d - 1);
			int displaced = f - newD;
			if (displaced < 0)
			{
				displaced = 0;
			}
			depthGrid[i] = newD;
			fillGrid[i] = (byte)(f - displaced);
			// PHASE 5. A cell raised out of SUPERDEEP stops being a trap, so its
			// holder goes with it. Destroy (not Despawn) because
			// Building_OpenPit.Destroy is what puts an occupant back on the map
			// instead of voiding them — the earth comes in and they come out.
			if (d >= RM_ExcavationDepth.Superdeep)
			{
				superdeepCellCount--;
				RM_SuperdeepCapture.RemoveHolder(map, c);
			}
			if (newD == RM_ExcavationDepth.Surface)
			{
				excavatedCells.Remove(c);
				fillGrid[i] = 0;
				// The temp fill layer must come off BEFORE the base terrain is
				// restored, or a brimming cell hands back its floor and keeps
				// standing water on top of it.
				ClearFillTerrain(c);
				RestoreOriginalTerrain(c);
			}
			else
			{
				TerrainDef want = RM_ExcavationDepth.DryTerrainFor(newD);
				if (want != null && map.terrainGrid.BaseTerrainAt(c) != want)
				{
					map.terrainGrid.SetTerrain(c, want);
				}
				ApplyFillTerrain(c, ActiveFluid);
			}
			if (displaced > 0)
			{
				Displace(c, displaced);
			}
			return newD;
		}

		/// <summary>
		/// The displacement walk. Offer the liquid to the connected body,
		/// NEAREST FIRST — remaining channel cells below their brim, then the
		/// natural body up to its capacity — and destroy only what finds no
		/// room anywhere.
		///
		/// 🔑 That last clause is the ONE sanctioned exception to conservation
		/// of mass in this whole design, which is why it routes through
		/// <see cref="NotifyOverflowDestroyed"/> and is announced rather than
		/// quietly dropped. Everything else here is a transfer.
		/// </summary>
		private void Displace(IntVec3 from, int units)
		{
			if (!RimMandrakeFlowWorksSettings.fillInDisplacementEnabled)
			{
				// All-off degradation: no displacement at all, every unit is
				// overflow. Still disclosed — the exception does not become
				// silent just because the mechanic is switched off.
				NotifyOverflowDestroyed(units);
				return;
			}
			int remaining = units;
			// LOCAL collections, not the pulse's shared scratch. A fill-in runs
			// from a JobDriver, not from inside DoPulse, so today they cannot
			// collide — but "cannot collide today" is how a reentrancy bug gets
			// written, and the walk is bounded and infrequent enough that the
			// allocation is free.
			HashSet<IntVec3> seen = new HashSet<IntVec3>();
			Queue<IntVec3> queue = new Queue<IntVec3>();
			List<IntVec3> credited = new List<IntVec3>();
			seen.Add(from);
			queue.Enqueue(from);
			int walked = 0;
			while (queue.Count > 0 && remaining > 0 && walked < MaxComponentCells)
			{
				IntVec3 c = queue.Dequeue();
				walked++;
				if (c != from)
				{
					if (IsSourceCell(c))
					{
						// The natural body is the last resort and the reason a
						// fill-in is REVERSIBLE: liquid you spent digging comes
						// back to the pond you took it from.
						float accepted = stock.TryCredit(map, c, remaining, this);
						remaining -= Mathf.FloorToInt(accepted);
						continue; // never expand through a source
					}
					int ci = map.cellIndices.CellToIndex(c);
					int room = depthGrid[ci] - fillGrid[ci];
					if (room > 0)
					{
						int take = room < remaining ? room : remaining;
						fillGrid[ci] += (byte)take;
						remaining -= take;
						credited.Add(c);
					}
				}
				for (int i = 0; i < 4; i++)
				{
					IntVec3 n = c + GenAdj.CardinalDirections[i];
					if (!n.InBounds(map) || seen.Contains(n))
					{
						continue;
					}
					if (IsExcavated(n) || IsSourceCell(n))
					{
						seen.Add(n);
						queue.Enqueue(n);
					}
				}
			}
			FluidDef fluid = ActiveFluid;
			for (int i = 0; i < credited.Count; i++)
			{
				ApplyFillTerrain(credited[i], fluid);
			}
			if (remaining > 0)
			{
				NotifyOverflowDestroyed(remaining);
				Messages.Message(
					"Filling in displaced more liquid than the channel could hold — "
					+ remaining + " level(s) overflowed and were lost.",
					new TargetInfo(from, map), MessageTypeDefOf.NeutralEvent, false);
			}
		}

		// ── the original-terrain record ───────────────────────────────────

		/// <summary>Remember a cell's base terrain the first time this engine
		/// overwrites it. Idempotent: the FIRST record wins, because the whole
		/// point is what was there before FlowWorks, not before the last
		/// change.</summary>
		public void RecordOriginalTerrain(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return;
			}
			int i = map.cellIndices.CellToIndex(c);
			if (originalTerrain.ContainsKey(i))
			{
				return;
			}
			TerrainDef t = map.terrainGrid.BaseTerrainAt(c);
			if (t != null)
			{
				originalTerrain[i] = t;
			}
		}

		/// <summary>Put back exactly what was there. Falls back to the cell's
		/// current terrain when nothing was recorded — which can only happen for
		/// a cell dug by a save that predates this record, and handing back what
		/// is already there is strictly better than guessing soil.</summary>
		public void RestoreOriginalTerrain(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return;
			}
			int i = map.cellIndices.CellToIndex(c);
			TerrainDef original;
			if (!originalTerrain.TryGetValue(i, out original) || original == null)
			{
				return;
			}
			originalTerrain.Remove(i);
			if (map.terrainGrid.BaseTerrainAt(c) != original)
			{
				map.terrainGrid.SetTerrain(c, original);
			}
		}

		/// <summary>Recession's write: dry one cell of a NATURAL body. The
		/// original terrain is recorded first, without exception — a receding
		/// pond must not permanently launder the map (§5).
		///
		/// Returns TRUE only when the cell was actually dried. The caller relies
		/// on that: a cell reported as receded but left as natural liquid is
		/// still a valid recession candidate next pass, and recording it anyway
		/// duplicates it without bound.</summary>
		public bool DryNaturalCell(IntVec3 c, FluidDef fluid)
		{
			if (!c.InBounds(map))
			{
				return false;
			}
			TerrainDef dry = fluid != null ? fluid.recededTerrain : null;
			if (dry == null)
			{
				// No recede terrain authored for this liquid: leave the cell
				// alone rather than inventing one. The stock still ran down and
				// the body still stops supplying; only the visible recession is
				// missing, and a missing visual beats a wrong terrain write.
				//
				// Nothing is recorded either — RecordOriginalTerrain below is
				// deliberately AFTER this guard, because a record with no
				// matching write leaves a restore entry for a cell that never
				// changed.
				return false;
			}
			RecordOriginalTerrain(c);
			map.terrainGrid.SetTerrain(c, dry);
			return true;
		}

		// ── map-edge sinks (ruling 9) ─────────────────────────────────────

		/// <summary>An excavated cell close enough to the map edge that liquid
		/// reaching it leaves the map. No building and no new def: the edge band
		/// vanilla already refuses construction in (GenGrid.NoBuildEdgeWidth,
		/// 10) is exactly the strip where a channel has nowhere left to go.
		///
		/// 🔑 A sink is the INVERSE of a limitless source, not a second
		/// conservation exception (ruling 9). Liquid down a sink is transferred
		/// off-map to the same off-map world an edge-touching body draws from.
		/// It is counted separately from destroyed overflow for that reason.</summary>
		public bool IsSinkCell(IntVec3 c)
		{
			if (!RimMandrakeFlowWorksSettings.edgeSinksEnabled || !c.InBounds(map))
			{
				return false;
			}
			return depthGrid[map.cellIndices.CellToIndex(c)] != 0
				&& c.CloseToEdge(map, GenGrid.NoBuildEdgeWidth);
		}

		public float SinkTransferredTotal => sinkTransferredTotal;

		// ── the pulse ─────────────────────────────────────────────────────

		/// <summary>PHASE 5. What <see cref="RM_SuperdeepCapture.SyncMap"/> was last
		/// run against, so flipping the capture toggle mid-game takes effect
		/// without a reload and costs one bool compare per tick otherwise.
		/// Deliberately NOT scribed: a load runs FinalizeInit's sync anyway.</summary>
		private bool syncedCaptureEnabled = true;

		public override void MapComponentTick()
		{
			base.MapComponentTick();
			if (syncedCaptureEnabled != RimMandrakeFlowWorksSettings.superdeepCaptureEnabled)
			{
				syncedCaptureEnabled = RimMandrakeFlowWorksSettings.superdeepCaptureEnabled;
				RM_SuperdeepCapture.SyncMap(map, this);
			}
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
			// PHASE 4. Rain lands BEFORE the sort, so the water it adds is part
			// of the "before" the conservation ledger measures and cannot read
			// as a leak. It is genuine external input, like a limitless source.
			ApplyRain();
			// PHASE 4. Stock first too: recession and refill decide which source
			// cells are still wet, and the flow below reads that.
			if (stock != null)
			{
				stock.Pulse(map, this, RimMandrakeFlowWorksSettings.PulseIntervalTicks);
			}
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
			for (int i = 0; i < pulseComponent.Count; i++)
			{
				IntVec3 c = pulseComponent[i];
				if (IsExcavated(c))
				{
					before += fillGrid[map.cellIndices.CellToIndex(c)];
				}
			}

			// PHASE 4, ruling 9 — SINKS, drained before the flow so the room a
			// sink opens is room this same pulse can pour into. That is what
			// makes "breach into a sink and the moat empties" read as a drain
			// rather than as a slow leak.
			float externalDrain = 0f;
			if (RimMandrakeFlowWorksSettings.edgeSinksEnabled)
			{
				int drainPerCell = RimMandrakeFlowWorksSettings.FlowPerPulse;
				for (int i = 0; i < pulseComponent.Count; i++)
				{
					IntVec3 c = pulseComponent[i];
					if (!IsExcavated(c) || !IsSinkCell(c))
					{
						continue;
					}
					int ci = map.cellIndices.CellToIndex(c);
					int take = fillGrid[ci] < drainPerCell ? fillGrid[ci] : drainPerCell;
					if (take <= 0)
					{
						continue;
					}
					fillGrid[ci] -= (byte)take;
					externalDrain += take;
				}
				sinkTransferredTotal += externalDrain;
			}

			pulseRecipients.Clear();
			for (int i = 0; i < pulseComponent.Count; i++)
			{
				IntVec3 c = pulseComponent[i];
				if (!IsExcavated(c))
				{
					continue;
				}
				int idx = map.cellIndices.CellToIndex(c);
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
						// PHASE 4. The 5:1 budget bites HERE and nowhere else: a
						// limitless body always pays, a limited one pays until
						// its stock is gone and then stops feeding the canal.
						// A failed debit must NOT move liquid — a transfer that
						// happens after its debit failed is precisely the silent
						// leak the ledger below exists to catch.
						if (!stock.TryDebit(map, donor, ActiveFluid != null ? ActiveFluid.volumePerTile : 1f, this))
						{
							break;
						}
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
			// the only legitimate changes in total fill are what sources
			// credited in and what left down a sink. Anything else is a leak,
			// and a leak is a bug.
			float imbalance = after - before - externalCredit + externalDrain;
			if (Prefs.DevMode && Mathf.Abs(imbalance) > 0.001f)
			{
				Log.Warning("[RimMandrake.FlowWorks] conservation ledger does not balance: " +
					"before=" + before.ToString("F1") + " after=" + after.ToString("F1") +
					" sourceCredit=" + externalCredit.ToString("F1") +
					" sinkDrain=" + externalDrain.ToString("F1") +
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
					// PHASE 4. A spent LIMITED body is not a donor. Skipping it
					// here rather than failing the debit later means the picker
					// can still find a wet neighbour in the same iteration.
					if (!stock.CanSupply(map, n, this))
					{
						continue;
					}
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

		// ── rain (ruling 25) ──────────────────────────────────────────────

		/// <summary>
		/// RULING 25, verbatim: <i>"Rain fills excavations only where
		/// unroofed."</i> Roofing is the player's lever and it costs nothing —
		/// the engine already tracks roof per cell, so this is one grid read.
		///
		/// Rain arrives in fractions of a level and a level is an integer, so
		/// the remainder is carried between pulses. Without that a light drizzle
		/// would round to zero forever and the whole mechanic would read as
		/// broken in exactly the weather where a player expects to see it.
		///
		/// This is the second place liquid legitimately enters the world (the
		/// first being a limitless body). It runs before the ledger's "before"
		/// is measured, so it can never be mistaken for a leak.
		/// </summary>
		private void ApplyRain()
		{
			if (!RimMandrakeFlowWorksSettings.rainFillsExcavationsEnabled || excavatedCells.Count == 0)
			{
				return;
			}
			float rainRate = map.weatherManager != null ? map.weatherManager.RainRate : 0f;
			if (rainRate <= 0.01f)
			{
				return;
			}
			rainAccumulator += rainRate * RimMandrakeFlowWorksSettings.rainFillPerPulse;
			int levels = 0;
			while (rainAccumulator >= 1f && levels < RM_ExcavationDepth.MaxDepth)
			{
				rainAccumulator -= 1f;
				levels++;
			}
			if (levels == 0)
			{
				return;
			}
			FluidDef fluid = ActiveFluid;
			foreach (IntVec3 c in excavatedCells)
			{
				int i = map.cellIndices.CellToIndex(c);
				if (fillGrid[i] >= depthGrid[i])
				{
					continue;
				}
				// The roof grid IS the rule. A roofed excavation stays dry in a
				// downpour, which is what makes roofing a trap a real decision.
				if (map.roofGrid.Roofed(c))
				{
					continue;
				}
				int room = depthGrid[i] - fillGrid[i];
				int add = room < levels ? room : levels;
				fillGrid[i] += (byte)add;
				ApplyFillTerrain(c, fluid);
			}
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

		/// <summary>Strip this engine's own fill terrain from one cell, and only
		/// its own — the same ownership rule <see cref="ApplyFillTerrain"/>
		/// follows, because a fill-in must not tear down a release some other
		/// path is still standing on.</summary>
		private void ClearFillTerrain(IntVec3 c)
		{
			FluidDef fluid = ActiveFluid;
			TerrainDef cur = map.terrainGrid.TempTerrainAt(c);
			if (cur != null && fluid != null && fluid.OwnsFillTerrain(cur))
			{
				map.terrainGrid.RemoveTempTerrain(c);
			}
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

		// ════════════════════════════════════════════════════════════════
		// DRIVER API — CANYON_FLOOD_ERASES_CANALS_1.
		//
		// ⚠️ ADDITIVE REGION. Everything above is the engine; this is the
		// whole of the surface a flood-driver client (ruling 8: FloodedCanyon
		// is a driver, this mod is the engine) may touch. Nothing above was
		// changed to add it.
		//
		// The read half already existed and needs nothing new: IsExcavated,
		// DepthAt, FillAt and CanLiquidEnter are all public. Only the WRITE
		// half is new, and it has to be, because the defect is precisely that
		// a driver was writing terrain on a cell this engine owns. A driver
		// that could only ASK would still have to act with SetTerrain, which
		// is the two-owners disease itself. So a driver raises and lowers F
		// here instead, and the engine remains the only thing that ever
		// decides what an excavated cell looks like.
		// ════════════════════════════════════════════════════════════════

		/// <summary>Set an excavated cell's F on behalf of a flood driver, and
		/// redraw it. Clamped to 0 &lt;= F &lt;= D, so a driver can never invent
		/// depth — LAW 1 is unreachable from here.
		///
		/// Returns FALSE for a cell this engine does not own (not excavated),
		/// which is the driver's signal to keep its own behaviour for that cell.
		/// A caller must record the previous <see cref="FillAt"/> itself if it
		/// intends to restore it: this engine deliberately keeps no per-driver
		/// undo stack, because the next pulse may legitimately move that liquid
		/// somewhere else and a stale undo would resurrect it.</summary>
		public bool TrySetDriverFill(IntVec3 c, int fill)
		{
			if (!c.InBounds(map))
			{
				return false;
			}
			int i = map.cellIndices.CellToIndex(c);
			byte d = depthGrid[i];
			if (d == 0)
			{
				return false;
			}
			if (fill < 0)
			{
				fill = 0;
			}
			if (fill > d)
			{
				fill = d;
			}
			fillGrid[i] = (byte)fill;
			FluidDef fluid = ActiveFluid;
			if (fluid != null)
			{
				ApplyFillTerrain(c, fluid);
			}
			return true;
		}

		/// <summary>Fill an excavated cell to its brim on behalf of a driver —
		/// what "a flood arrives at this cell" means once depth is the
		/// primitive. Same contract as <see cref="TrySetDriverFill"/>.</summary>
		public bool TryFloodDriverCell(IntVec3 c)
		{
			return TrySetDriverFill(c, DepthAt(c));
		}
	}
}
