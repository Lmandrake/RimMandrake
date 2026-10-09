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
	public class RM_MapComponent_Excavation : MapComponent, RM_IFlowWorld
	{
		/// <summary>D. 0 = surface; 1..4 = shallow/mid/deep/SUPERDEEP.</summary>
		private byte[] depthGrid;

		/// <summary>F. Always clamped to 0 &lt;= F &lt;= D.</summary>
		private byte[] fillGrid;

		/// <summary>Which liquid this map's excavations carry. One per map this
		/// pass: per-cell liquid identity is the registry's (LiquidDef) and
		/// arrives with it, not here. Null until the first pulse resolves it.</summary>
		private FluidDef activeFluid;

		/// <summary>LIQUID_BODY_FLUID_IDENTITY_1 step 1. Per-cell liquid identity beside D and F: 0 = none, else
		/// 1 + an index into <see cref="fluidPalette"/>. A pit is not an RM_LiquidBody (its component is re-found
		/// every pulse), so identity has to live per cell. Every writer stamps the fluid it pours (steps 2-3); the
		/// PickDonor no-mix filter reads it. ActiveFluid survives only as the default SyncFluidIdentity stamps on a
		/// wet cell a save left unrecorded (the step-4 migration).</summary>
		private byte[] fluidGrid;

		private List<FluidDef> fluidPalette = new List<FluidDef>();

		private int nextPulseTick = -1;

		/// <summary>Fire-burn cadence while the depth engine is OFF only (GPT review #18). Not scribed: on load an
		/// off-engine fire waits at most one interval for its next burn.</summary>
		private int nextOffBurnTick = -1;

		/// <summary>VISCOSITY (FLOWWORKS_BUILD_PROGRAM_1 Phase 3/7): pulses run on this map, scribed so a viscous
		/// fluid's every-Nth-pulse cadence survives a save. <see cref="RM_StockMath.FluidMovesThisPulse"/>.</summary>
		private long pulseCount;

		public long PulseCount => pulseCount;

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

		/// <summary>EXCAVATION_LEGACY_MIGRATION_FLAG_1: set once the legacy terrain-to-grid rehydration has had
		/// its one chance on this map. Saved, so an all-zero grid on a later load (every channel filled in)
		/// is read as "nothing dug", never re-read from leftover channel terrain as a fresh excavation.</summary>
		private bool legacyRehydrationDone;

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

		/// <summary>Approach B phase 2: the pulse's grid transition lives in the Verse-free RM_FlowKernel
		/// (component walk, sinks, flow order, recipient order, donor pick, ledger); this component is its
		/// adapter (terrain, bodies, fluid palette, rendering). Derived, never scribed.</summary>
		private RM_FlowKernel flowKernel;

		/// <summary>excavatedCells as kernel indices, in the set's own iteration order, rebuilt per pulse.</summary>
		private readonly List<int> pulseSeeds = new List<int>();

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
		/// <summary>Read-only view of the excavated set (LIQUID_HEAT_PUSH_1). Never mutate while iterating.</summary>
		public IEnumerable<IntVec3> ExcavatedCells => excavatedCells;

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

		/// <summary>SUPERDEEP_PRISON_ROOM_1: the same test, null-safe on the grid, for region
		/// building (which runs in Map.FinalizeInit before this component's FinalizeInit).</summary>
		public bool IsSuperdeepRaw(IntVec3 c)
		{
			return depthGrid != null && c.InBounds(map)
				&& depthGrid[map.cellIndices.CellToIndex(c)] >= RM_ExcavationDepth.Superdeep;
		}

		public bool IsSuperdeepExcavation(IntVec3 c)
		{
			return c.InBounds(map)
				&& depthGrid[map.cellIndices.CellToIndex(c)] >= RM_ExcavationDepth.Superdeep;
		}

		/// <summary>SUPERDEEP_HOLDER_RETIRE_1. The DUG depth only (0 for natural
		/// liquid and undug ground) — what the trap rule and the descent detector
		/// read, for the same reason <see cref="IsSuperdeepExcavation"/> does.</summary>
		public int ExcavatedDepthAt(IntVec3 c)
		{
			return c.InBounds(map) ? depthGrid[map.cellIndices.CellToIndex(c)] : 0;
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
				WarnWrongSizedGrid("depth", depthGrid, cells);
				depthGrid = new byte[cells];
			}
			if (fillGrid == null || fillGrid.Length != cells)
			{
				WarnWrongSizedGrid("fill", fillGrid, cells);
				fillGrid = new byte[cells];
			}
			if (fluidGrid == null || fluidGrid.Length != cells)
			{
				WarnWrongSizedGrid("fluid", fluidGrid, cells);
				fluidGrid = new byte[cells];
			}
			if (fluidPalette == null)
			{
				fluidPalette = new List<FluidDef>();
			}
		}

		/// <summary>EXCAVATION_LOAD_SANITY_REPAIR_1: a grid of the wrong size is zeroed; say so, once per grid. A null
		/// grid is the normal first-load case and stays silent.</summary>
		private void WarnWrongSizedGrid(string which, byte[] old, int cells)
		{
			if (old != null && RimMandrakeFlowWorksSettings.excavationLoadRepairEnabled)
			{
				Log.Warning("[RimMandrake.FlowWorks] excavation " + which + " grid had " + old.Length + " cells but the map has "
					+ cells + "; it was reset to empty.");
			}
		}

		/// <summary>EXCAVATION_LOAD_SANITY_REPAIR_1 (FL-3). Runs once per map load after the lost-fluid report:
		/// clamps D to 0..4 and F to 0..D, clears fluid keys past the palette, then drops palette entries no cell
		/// uses (null entries included) and remaps the grid, so a long campaign never exhausts the 254 keys.
		/// One log line when anything changed.</summary>
		internal void RepairLoadedGrids()
		{
			if (!RimMandrakeFlowWorksSettings.excavationLoadRepairEnabled || depthGrid == null)
			{
				return;
			}
			RM_ExcavationSanityMath.Report r = RM_ExcavationSanityMath.Repair(depthGrid, fillGrid, fluidGrid,
				fluidPalette.Count, RM_ExcavationDepth.MaxDepth);
			int dropped = 0;
			bool[] used = RM_ExcavationSanityMath.KeysInUse(fluidGrid, fluidPalette.Count);
			byte[] remap;
			int newCount = RM_ExcavationSanityMath.BuildCompaction(used, out remap);
			if (newCount < fluidPalette.Count)
			{
				List<FluidDef> compact = new List<FluidDef>(newCount);
				for (int k = 1; k < used.Length; k++)
				{
					if (used[k])
					{
						compact.Add(fluidPalette[k - 1]);
					}
				}
				RM_ExcavationSanityMath.ApplyRemap(fluidGrid, remap);
				dropped = fluidPalette.Count - newCount;
				fluidPalette = compact;
			}
			if (r.Total > 0 || dropped > 0)
			{
				Log.Message("[RimMandrake.FlowWorks] excavation load repair: " + r.depthClamped + " depth, " + r.fillClamped
					+ " fill, " + r.fluidKeyCleared + " fluid key(s) fixed; " + dropped + " unused palette entr"
					+ (dropped == 1 ? "y" : "ies") + " dropped.");
			}
		}

		// ── fluid identity (LIQUID_BODY_FLUID_IDENTITY_1) ─────────────────

		/// <summary>The liquid recorded on a cell, or null for a dry/unrecorded cell.</summary>
		public FluidDef FluidAt(IntVec3 c)
		{
			if (fluidGrid == null || !c.InBounds(map))
			{
				return null;
			}
			int k = fluidGrid[map.cellIndices.CellToIndex(c)];
			return k == 0 || k > fluidPalette.Count ? null : fluidPalette[k - 1];
		}

		private byte PaletteKey(FluidDef fluid)
		{
			if (fluid == null)
			{
				return 0;
			}
			int i = fluidPalette.IndexOf(fluid);
			if (i < 0)
			{
				if (fluidPalette.Count >= 254)
				{
					return 0;
				}
				fluidPalette.Add(fluid);
				i = fluidPalette.Count - 1;
			}
			return (byte)(i + 1);
		}

		/// <summary>Stamps the map's ActiveFluid on every excavated cell whose F went 0 -&gt; &gt;0 without a record
		/// and clears the record where F is 0. Also the save migration (step 4): a save with no fluidGrid loads an
		/// all-zero grid and this stamps every wet cell. Bodies with no fluid (an old save) take ActiveFluid too.
		/// Behaviour-neutral: nothing reads the grid to decide flow yet.</summary>
		internal void SyncFluidIdentity()
		{
			EnsureGrids();
			byte active = PaletteKey(ActiveFluid);
			foreach (IntVec3 c in excavatedCells)
			{
				int i = map.cellIndices.CellToIndex(c);
				if (fillGrid[i] == 0)
				{
					fluidGrid[i] = 0;
				}
				else if (fluidGrid[i] == 0)
				{
					fluidGrid[i] = active;
				}
			}
			if (stock != null)
			{
				foreach (RM_LiquidBody b in stock.Bodies)
				{
					if (b.fluid == null)
					{
						b.fluid = ActiveFluid;
					}
				}
			}
		}

		/// <summary>LIQUID_BODY_FLUID_IDENTITY_1's named risk: a FluidDef removed from the mod set loads as a null
		/// palette entry, FluidAt answers null for its cells, and the sync would re-stamp them with ActiveFluid —
		/// a silent conversion. This makes it loud, once per map load, and zeroes those records so the
		/// re-stamp that follows is the disclosed migration rather than an accident.</summary>
		private void ReportLostPaletteFluids()
		{
			if (fluidPalette == null || fluidGrid == null || !fluidPalette.Contains(null))
			{
				return;
			}
			int cells = 0;
			for (int i = 0; i < fluidGrid.Length; i++)
			{
				int k = fluidGrid[i];
				if (k > 0 && k <= fluidPalette.Count && fluidPalette[k - 1] == null)
				{
					fluidGrid[i] = 0;
					cells++;
				}
			}
			int lost = 0;
			foreach (FluidDef f in fluidPalette)
			{
				if (f == null) lost++;
			}
			Log.Warning("[RimMandrake.FlowWorks] " + lost + " fluid(s) recorded in this save no longer exist in the "
				+ "loaded mod set; " + cells + " wet excavated cell(s) held them and are re-stamped as "
				+ (ActiveFluid?.defName ?? "null") + ". This is a conversion caused by the mod list, not by flow.");
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
			DataExposeUtility.LookByteArray(ref fluidGrid, "RM_excavationFluidGrid");
			Scribe_Collections.Look(ref fluidPalette, "RM_excavationFluidPalette", LookMode.Def);
			Scribe_Defs.Look(ref activeFluid, "RM_activeFluid");
			Scribe_Values.Look(ref nextPulseTick, "RM_nextPulseTick", -1);
			Scribe_Values.Look(ref pulseCount, "RM_pulseCount", 0L);
			Scribe_Values.Look(ref overflowDestroyedTotal, "RM_overflowDestroyedTotal", 0f);
			Scribe_Values.Look(ref legacyRehydrationDone, "RM_legacyRehydrationDone", false);
			// PHASE 4. Everything persistent the stock model adds is scribed
			// here: the original-terrain record, the bodies (their sticky
			// classification, stock, capacity, footprint and receded list, via
			// RM_LiquidBody.ExposeData), the rain remainder and the sink total.
			Scribe_Collections.Look(ref originalTerrain, "RM_originalTerrain",
				LookMode.Value, LookMode.Def, ref originalTerrainKeys, ref originalTerrainValues);
			Scribe_Deep.Look(ref stock, "RM_liquidStock");
			Scribe_Values.Look(ref rainAccumulator, "RM_rainAccumulator", 0f);
			Scribe_Values.Look(ref sinkTransferredTotal, "RM_sinkTransferredTotal", 0f);
			Scribe_Deep.Look(ref superdeepTrap, "RM_superdeepTrap");
			Scribe_Deep.Look(ref liquidFire, "RM_liquidFire");
			Scribe_Deep.Look(ref digDiscovery, "RM_digDiscovery");
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				if (superdeepTrap == null)
				{
					superdeepTrap = new RM_SuperdeepTrapState();
				}
				if (liquidFire == null)
				{
					liquidFire = new RM_LiquidFire();
				}
				if (digDiscovery == null)
				{
					digDiscovery = new RM_DigDiscoveryState();
				}
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
			if (!legacyRehydrationDone)
			{
				RehydrateFromTerrainIfEmpty();
				legacyRehydrationDone = true;
			}
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
			ReportLostPaletteFluids();
			RepairLoadedGrids();
			SyncFluidIdentity();
			// SUPERDEEP_HOLDER_RETIRE_1: a save written while the holder Thing
			// existed carries RM_SuperdeepPit Things; the def is gone, so the
			// loader drops them ("Could not load reference") — nothing to shed.
			superdeepTrap.ResetDetector();
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
			// trap. SUPERDEEP_HOLDER_RETIRE_1: the trap is the grid byte itself
			// (RM_SuperdeepTrap); no Thing is created by digging.
			if (d >= RM_ExcavationDepth.Superdeep)
			{
				superdeepCellCount++;
				// SUPERDEEP_PRISON_ROOM_1: the cell just crossed the pit wall; its rooms re-form.
				RM_PitRooms.NotifyPitnessChanged(map, c);
			}
			return d;
		}

		/// <summary>§5's fill-in path will call this when displaced liquid has
		/// nowhere to go. It is the ONE sanctioned exception to conservation of
		/// mass in the whole design, so it is recorded and announced rather
		/// than quietly dropped. The fill-in designator itself is program 2's.
		/// Counted in grid LEVELS (the unit F is stored in), not stock units: the one caller,
		/// ReportOverflow, passes levels and its player message says "level(s)".</summary>
		public void NotifyOverflowDestroyed(float levels)
		{
			if (levels <= 0f)
			{
				return;
			}
			overflowDestroyedTotal += levels;
			if (Prefs.DevMode)
			{
				Log.Warning("[RimMandrake.FlowWorks] conservation exception: " +
					levels.ToString("F1") + " fill level(s) overflowed with nowhere to go and were " +
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
			// LIQUID_BODY_FLUID_IDENTITY_1 step 2b: the displaced liquid keeps the fluid this cell held.
			FluidDef cellFluid = FluidAt(c) ?? ActiveFluid;
			// The F - (D-1) clamp lives in RM_StockMath so the selftest covers the
			// production arithmetic rather than a copy of it.
			int displaced = RM_StockMath.DisplacedLevels(d, f);
			depthGrid[i] = newD;
			fillGrid[i] = (byte)(f - displaced);
			// PHASE 5. A cell raised out of SUPERDEEP stops being a trap: the
			// grid byte drops and the trap rule stops applying on the next read.
			// Nobody is in a container, so nobody needs dropping out.
			if (d >= RM_ExcavationDepth.Superdeep)
			{
				superdeepCellCount--;
				RM_PitRooms.NotifyPitnessChanged(map, c);
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
				ApplyFillTerrain(c, cellFluid);
			}
			if (displaced > 0)
			{
				Displace(c, displaced, cellFluid);
			}
			return newD;
		}

		/// <summary>
		/// The displacement walk. Offer the liquid to the connected body,
		/// NEAREST FIRST — remaining channel cells below their brim, THEN the
		/// natural body up to its capacity — and destroy only what finds no
		/// room anywhere.
		///
		/// 🔴 THE CHANNEL IS SERVED BEFORE THE BODY, AND THAT IS NOT AN
		/// ORDERING PREFERENCE. §5's third consequence is a thing the player
		/// must SEE: <i>"the receiving cells' fill tiers rise, so displacement
		/// is visible: filling in one end of a canal makes the rest of it
		/// deeper."</i> A single breadth-first walk that credits whichever
		/// recipient it reaches first lets a pond one cell away swallow the
		/// whole displacement while the canal beyond it stays exactly as it
		/// was — mass conserved, and the only visible evidence of it gone. So
		/// the walk runs in two phases: phase 1 credits channel cells, nearest
		/// first; phase 2 offers whatever is still homeless to the source
		/// cells the walk touched, again nearest first.
		///
		/// 🔑 Whatever finds no room is the ONE sanctioned exception to
		/// conservation of mass in this whole design, which is why every exit
		/// from this method routes through <see cref="ReportOverflow"/> and is
		/// announced rather than quietly dropped. Everything else is a
		/// transfer.
		///
		/// <paramref name="units"/> is in fill LEVELS, the unit the grids hold.
		/// The body's stock is in fill-units of volume, so phase 2 converts —
		/// see <see cref="RM_LiquidStock.CreditLevels"/>.
		/// </summary>
		private void Displace(IntVec3 from, int units, FluidDef fluid)
		{
			if (!RimMandrakeFlowWorksSettings.fillInDisplacementEnabled)
			{
				// All-off degradation: no displacement at all, every level is
				// overflow. Still disclosed — the exception does not become
				// silent just because the mechanic is switched off, which is why
				// this takes the same reporting exit as a real overflow rather
				// than only writing a DevMode log.
				ReportOverflow(from, units);
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
			// Source cells in the order the walk reached them, i.e. nearest
			// first. They are NOT credited during phase 1 (see above) and are
			// never expanded through — the channel is what conducts, a pond is a
			// destination.
			List<IntVec3> sources = new List<IntVec3>();
			seen.Add(from);
			queue.Enqueue(from);
			int walked = 0;

			// ── phase 1: the channel, below the brim, nearest first ────────
			while (queue.Count > 0 && remaining > 0 && walked < MaxComponentCells)
			{
				IntVec3 c = queue.Dequeue();
				walked++;
				if (c != from)
				{
					if (IsSourceCell(c))
					{
						sources.Add(c);
						continue;
					}
					int ci = map.cellIndices.CellToIndex(c);
					int room = RM_StockMath.CellRoom(depthGrid[ci], fillGrid[ci]);
					// Fluids never mix (Q3): only a dry cell (which it then claims) or a same-fluid cell takes the levels;
					// the rest is the disclosed overflow. The walk still conducts through a foreign cell.
					if (room > 0 && !RM_StockMath.FluidsCompatible(fillGrid[ci] > 0, FluidAt(c), fluid))
					{
						room = 0;
					}
					if (room > 0)
					{
						int take = room < remaining ? room : remaining;
						if (fillGrid[ci] == 0)
						{
							fluidGrid[ci] = PaletteKey(fluid);
						}
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
					// A shut sluice seals its cell for displacement exactly as for the pulse (the kernel's sealedCell):
					// liquid is neither credited into it nor conducted past it (GPT FlowWorks review #7).
					if ((IsExcavated(n) || IsSourceCell(n)) && !RM_FlowDoorRules.SealsLiquid(map.edificeGrid[n]))
					{
						seen.Add(n);
						queue.Enqueue(n);
					}
				}
			}

			// ── phase 2: the natural body, nearest source cell first ───────
			// The body is the last resort and the reason a fill-in is
			// REVERSIBLE: liquid you spent digging comes back to the pond you
			// took it from, in the same fill-units the pulse debited to get it.
			float unitPerLevel = fluid != null ? fluid.volumePerTile : 1f;
			for (int i = 0; i < sources.Count && remaining > 0; i++)
			{
				FluidDef bodyFluid = stock.BodyAt(map, sources[i], this)?.fluid;
				if (bodyFluid != null && fluid != null && bodyFluid != fluid)
				{
					continue;
				}
				remaining -= stock.CreditLevels(map, sources[i], remaining, unitPerLevel, this);
			}

			for (int i = 0; i < credited.Count; i++)
			{
				ApplyFillTerrain(credited[i], fluid);
			}
			ReportOverflow(from, remaining);
		}

		/// <summary>Disclose destroyed liquid. §5 is explicit that this may not be
		/// silent — <i>"an overflow report so destroyed liquid is disclosed rather
		/// than silent — a message or an inspect line, since silent loss in a
		/// conservation-of-mass system reads as a bug."</i>
		///
		/// Zero destroyed says nothing, which is not silence about a loss: it is
		/// the case where there was no loss.</summary>
		private void ReportOverflow(IntVec3 at, int levels)
		{
			if (levels <= 0)
			{
				return;
			}
			NotifyOverflowDestroyed(levels);
			Messages.Message(
				"Filling in displaced more liquid than the channel could hold — "
				+ levels + " level(s) overflowed and were lost. "
				+ "Lost this way on this map so far: " + overflowDestroyedTotal.ToString("F0") + ".",
				new TargetInfo(at, map), MessageTypeDefOf.NeutralEvent, false);
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

		/// <summary>Read-only: the terrain this cell had before it was dug (or dried), or null when none is recorded.
		/// The wall faces use it to show what the cut was dug through (FLOWWORKS_VISUAL_PRINCIPLES_1).</summary>
		public TerrainDef OriginalTerrainAt(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return null;
			}
			return originalTerrain.TryGetValue(map.cellIndices.CellToIndex(c), out TerrainDef t) ? t : null;
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
				// EXCAVATION_LEGACY_MIGRATION_FLAG_1: a channel dug by a save that predates the record (rehydrated
				// from terrain) has nothing to restore; leaving channel terrain at D=0 is a dry trench the engine no
				// longer owns. Hand back the commonest neighbouring natural terrain instead, soil when there is none.
				if (RimMandrakeFlowWorksSettings.legacyFillFallbackEnabled
					&& RM_ExcavationDepth.DepthOfDryTerrain(map.terrainGrid.BaseTerrainAt(c)) != RM_ExcavationDepth.Surface)
				{
					TerrainDef fallback = FallbackTerrainFor(c);
					if (fallback != null)
					{
						map.terrainGrid.SetTerrain(c, fallback);
					}
				}
				return;
			}
			originalTerrain.Remove(i);
			if (map.terrainGrid.BaseTerrainAt(c) != original)
			{
				map.terrainGrid.SetTerrain(c, original);
			}
		}

		// PROVISIONAL (auto-decided 2026-10-09, EXCAVATION_LEGACY_MIGRATION_FLAG_1): fallback for an unrecorded cell is the
		// commonest non-channel, non-liquid neighbouring base terrain, else Soil (setting legacyFillFallbackEnabled, default on).
		private TerrainDef FallbackTerrainFor(IntVec3 c)
		{
			Dictionary<TerrainDef, int> votes = new Dictionary<TerrainDef, int>();
			TerrainDef best = null;
			int bestVotes = 0;
			for (int d = 0; d < 8; d++)
			{
				IntVec3 n = c + GenAdj.AdjacentCells[d];
				if (!n.InBounds(map))
				{
					continue;
				}
				TerrainDef t = map.terrainGrid.BaseTerrainAt(n);
				if (t == null || t.IsWater || RM_ExcavationDepth.DepthOfDryTerrain(t) != RM_ExcavationDepth.Surface)
				{
					continue;
				}
				int v;
				votes.TryGetValue(t, out v);
				votes[t] = ++v;
				if (v > bestVotes || (v == bestVotes && best != null && string.CompareOrdinal(t.defName, best.defName) < 0))
				{
					best = t;
					bestVotes = v;
				}
			}
			return best ?? TerrainDefOf.Soil;
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

		/// <summary>SUPERDEEP_HOLDER_RETIRE_1. The descent detector and the
		/// jumper set. Per-map state lives here so it scribes with the grid.</summary>
		private RM_SuperdeepTrapState superdeepTrap = new RM_SuperdeepTrapState();

		internal RM_SuperdeepTrapState SuperdeepTrap => superdeepTrap;

		/// <summary>FLOWWORKS_BUILD_PROGRAM_1 Phase 6: fire on the liquid (RM_LiquidFire).</summary>
		private RM_LiquidFire liquidFire = new RM_LiquidFire();
		/// <summary>LIQUID_HEAT_PUSH_1: hot/icy liquid warms or chills its room (vanilla heat). Derived, never scribed.</summary>
		private readonly RM_LiquidHeat liquidHeat = new RM_LiquidHeat();
		public RM_LiquidHeat LiquidHeat => liquidHeat;

		public RM_LiquidFire LiquidFire => liquidFire;

		/// <summary>FLOWWORKS_QUARRY_DIGGING_1: canal-dig finds (RM_DigDiscovery).</summary>
		private RM_DigDiscoveryState digDiscovery = new RM_DigDiscoveryState();

		public RM_DigDiscoveryState DigDiscovery => digDiscovery;

		/// <summary>Phase 6, ruling 7: burning takes one fill level off an excavated cell. Burned liquid leaves the
		/// world (the fire's disclosed exit, counted by RM_LiquidFire). Runs outside ResolveComponent's ledger.</summary>
		internal bool BurnOffLevel(IntVec3 c)
		{
			if (!IsExcavated(c))
			{
				return false;
			}
			int i = map.cellIndices.CellToIndex(c);
			if (fillGrid[i] == 0)
			{
				return false;
			}
			FluidDef fluid = FluidAt(c) ?? ActiveFluid;
			fillGrid[i] -= 1;
			if (fluid != null)
			{
				ApplyFillTerrain(c, fluid);
			}
			if (fillGrid[i] == 0)
			{
				fluidGrid[i] = 0;
			}
			return true;
		}

		/// <summary>FLOWWORKS_BUILD_PROGRAM_1 Phase 8: a pump lifts one level out of an excavated cell. The level
		/// is MOVED (into a tank), not lost, so it sits outside the pulse ledger exactly like a burn does.</summary>
		public bool TryTakeLevel(IntVec3 c, out FluidDef fluid)
		{
			fluid = null;
			if (!IsExcavated(c))
			{
				return false;
			}
			int i = map.cellIndices.CellToIndex(c);
			if (fillGrid[i] == 0)
			{
				return false;
			}
			fluid = FluidAt(c) ?? ActiveFluid;
			return BurnOffLevel(c);
		}

		/// <summary>Phase 8: a pump pours one level into an excavated cell with room (fluids never mix).</summary>
		public bool TryPourLevel(IntVec3 c, FluidDef fluid)
		{
			if (!IsExcavated(c) || fluid == null)
			{
				return false;
			}
			int f = FillAt(c);
			if (f >= DepthAt(c))
			{
				return false;
			}
			return TrySetDriverFill(c, f + 1, fluid);
		}

		public override void MapComponentTick()
		{
			base.MapComponentTick();
			if (superdeepCellCount > 0)
			{
				superdeepTrap.Tick(map, this);
			}
			// Always (every 250 ticks, one hediff lookup per pawn): the exposure hediff has no severityPerDay comp, so
			// this is its only recovery route, and it must keep running after the map's last pit is filled in
			// (GPT FlowWorks review #19).
			RM_PitExposure.Tick(map, this);
			liquidFire.Tick(map, this);
			// Own timer, not the pulse: heat is the liquid's presence, so it keeps running with the depth engine off.
			liquidHeat.Tick(map, this);
			if (excavatedCells.Count > 0)
			{
				RM_PitFillEffects.Tick(map, this);
			}
			int now = Find.TickManager.TicksGame;
			if (!RimMandrakeFlowWorksSettings.depthEngineEnabled)
			{
				// Nothing pours with the engine off, but a fire still burning (Tick above keeps its heat and harm)
				// must still consume its fuel, or it burns forever (GPT FlowWorks review #18). It runs on its OWN
				// timer: the pulse schedule stays frozen while the engine is off (E4 contract,
				// flowworks_northstar_script_plan_2026-10-02.md E4), so switching it back on pulses at once.
				// The first off-burn waits for the tick the pulse was due, so turning the engine off never burns early.
				if (now >= Mathf.Max(nextPulseTick, nextOffBurnTick))
				{
					nextOffBurnTick = now + RimMandrakeFlowWorksSettings.PulseIntervalTicks;
					liquidFire.BurnPulse(map, this, RimMandrakeFlowWorksSettings.PulseIntervalTicks);
				}
				return;
			}
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
			pulseCount++;
			// PHASE 4. Rain lands BEFORE the sort, so the water it adds is part
			// of the "before" the conservation ledger measures and cannot read
			// as a leak. It is genuine external input, like a limitless source.
			ApplyRain();
			// PHASE 6, ruling 7: the burn takes its levels before the components measure "before", so burned
			// liquid is never mistaken for a leak.
			liquidFire.BurnPulse(map, this, RimMandrakeFlowWorksSettings.PulseIntervalTicks);
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
			// FLOWWORKS_SHARED_SOURCE_STALL_1. The component walk lives in the
			// Verse-free RM_StockMath.CollectComponent so the selftest runs the
			// production code. A source cell JOINS a component as a donor but is
			// never expanded through (one channel touching an ocean must not walk
			// the ocean), and — the fix — a source cell is never marked visited
			// across components: every channel touching it gets it as a donor and
			// a flow order. Components resolve in excavatedCells order, so when a
			// LIMITED body cannot pay every adjacent channel's inlet in a pulse,
			// the lower-cell-index channel is paid first, unit by unit (the kernel sorts
			// the seeds, so session and post-load orders agree - owner ruling 2026-10-06).
			if (flowKernel == null || flowKernel.width != map.Size.x || flowKernel.height != map.Size.z)
			{
				flowKernel = new RM_FlowKernel(map.Size.x, map.Size.z) { world = this, maxComponentCells = MaxComponentCells };
				// FLOWWORKS_SLUICE_TWO_DOORS_1: a shut sluice seals its cell (one edifice-grid read per probe).
				flowKernel.sealedCell = idx => RM_FlowDoorRules.SealsLiquid(map.edificeGrid[idx]);
			}
			flowKernel.depth = depthGrid;
			flowKernel.fill = fillGrid;
			flowKernel.flowPerPulse = RimMandrakeFlowWorksSettings.FlowPerPulse;
			flowKernel.edgeSinksEnabled = RimMandrakeFlowWorksSettings.edgeSinksEnabled;
			flowKernel.viscosityEnabled = RimMandrakeFlowWorksSettings.viscosityEnabled;
			flowKernel.creepEnabled = RimMandrakeFlowWorksSettings.viscosityEnabled && RimMandrakeFlowWorksSettings.thickCreepEnabled;
			// FLOW_ORDER_EXTERNAL_INPUT_1: cells a driver (pump, drill) fed recently seed the flow order.
			PruneDriverInputs();
			flowKernel.externalInput = RimMandrakeFlowWorksSettings.pumpFedSpreadEnabled && driverInputTick.Count > 0
				? (System.Func<int, bool>)(idx => driverInputTick.ContainsKey(idx))
				: null;
			pulseSeeds.Clear();
			foreach (IntVec3 seed in excavatedCells)
			{
				pulseSeeds.Add(map.cellIndices.CellToIndex(seed));
			}
			flowKernel.Pulse(pulseSeeds, pulseCount);
			if (RimMandrakeFlowWorksSettings.edgeSinksEnabled)
			{
				sinkTransferredTotal += flowKernel.sinkDrained;
			}
			if (Prefs.DevMode)
			{
				for (int i = 0; i < flowKernel.imbalanceReports.Count; i++)
				{
					// The ledger. Every transfer inside a component is -1 and +1, so the only legitimate changes in
					// total fill are what sources credited in and what left down a sink. Anything else is a leak.
					Log.Warning("[RimMandrake.FlowWorks] conservation ledger does not balance: " +
						flowKernel.imbalanceReports[i] + ". This is a defect, not an overflow.");
				}
			}
			SyncFluidIdentity();
		}

		/// <summary>The fluid a donor cell would give: its body's for a source, the cell's own record otherwise.</summary>
		private FluidDef DonorFluid(IntVec3 n, bool source)
		{
			return source ? stock.BodyAt(map, n, this)?.fluid : FluidAt(n);
		}

		// ── RM_IFlowWorld: what RM_FlowKernel reads and writes outside the depth/fill arrays ──

		bool RM_IFlowWorld.IsNaturalLiquid(int idx)
		{
			return IsNaturalLiquid(map.cellIndices.IndexToCell(idx));
		}

		bool RM_IFlowWorld.CanSupply(int idx)
		{
			IntVec3 c = map.cellIndices.IndexToCell(idx);
			// FLUID_DISABLE_ALL_INPUTS_1: a natural body of a liquid switched off in Mod Settings feeds no new liquid.
			if (!InputAllowed(DonorFluid(c, true) ?? ActiveFluid))
			{
				return false;
			}
			return stock == null || stock.CanSupply(map, c, this);
		}

		/// <summary>FLUID_DISABLE_ALL_INPUTS_1: the one check every NEW liquid input passes — pump, drill, driver
		/// fill, natural-source transfer, rain and the legacy flood spread. What already stands stays: liquid already
		/// in a cut keeps moving and draining; only liquid entering the world is refused.</summary>
		public static bool InputAllowed(FluidDef fluid)
		{
			return RimMandrakeFlowWorksSettings.FluidAllowed(fluid);
		}

		bool RM_IFlowWorld.TryDebitLevel(int idx)
		{
			// Step 3: the debit unit is the SOURCE BODY's fluid, never the map's.
			IntVec3 c = map.cellIndices.IndexToCell(idx);
			FluidDef sourceFluid = DonorFluid(c, true) ?? ActiveFluid;
			return stock.TryDebit(map, c, sourceFluid != null ? sourceFluid.volumePerTile : 1f, this);
		}

		object RM_IFlowWorld.DonorFluid(int idx, bool source)
		{
			return DonorFluid(map.cellIndices.IndexToCell(idx), source);
		}

		object RM_IFlowWorld.CellFluid(int idx)
		{
			return FluidAt(map.cellIndices.IndexToCell(idx));
		}

		void RM_IFlowWorld.Claim(int idx, object fluid)
		{
			// First level into a dry cell claims it for the donor's fluid (step 2: identity at the writer).
			fluidGrid[idx] = PaletteKey((fluid as FluidDef) ?? ActiveFluid);
		}

		int RM_IFlowWorld.TicksPerTile(object fluid)
		{
			return ((fluid as FluidDef) ?? ActiveFluid)?.ticksPerTile ?? RM_StockMath.WaterTicksPerTile;
		}

		bool RM_IFlowWorld.IsSink(int idx)
		{
			return IsSinkCell(map.cellIndices.IndexToCell(idx));
		}

		void RM_IFlowWorld.ComponentResolved(List<int> component)
		{
			RenderComponentFill(component);
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
			// Rain is water (step 2b): it lands on a dry cell (claiming it) or a water cell, never on another fluid.
			FluidDef fluid = RimMandrakeFlowWorks_DefOf.RM_Fluid_Water ?? ActiveFluid;
			if (!InputAllowed(fluid))
			{
				return;   // FLUID_DISABLE_ALL_INPUTS_1: water switched off means rain adds none
			}
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
				if (!RM_StockMath.FluidsCompatible(fillGrid[i] > 0, FluidAt(c), fluid))
				{
					continue;
				}
				int room = depthGrid[i] - fillGrid[i];
				int add = room < levels ? room : levels;
				if (fillGrid[i] == 0)
				{
					fluidGrid[i] = PaletteKey(fluid);
				}
				fillGrid[i] += (byte)add;
				ApplyFillTerrain(c, fluid);
			}
		}

		// ── rendering F ───────────────────────────────────────────────────

		private void RenderComponentFill(List<int> component)
		{
			FluidDef fallback = ActiveFluid;
			for (int i = 0; i < component.Count; i++)
			{
				IntVec3 c = map.cellIndices.IndexToCell(component[i]);
				FluidDef fluid = FluidAt(c) ?? fallback;
				if (fluid != null && IsExcavated(c))
				{
					ApplyFillTerrain(c, fluid);
				}
			}
		}

		private void ApplyFillTerrain(IntVec3 c, FluidDef fluid)
		{
			if (fluid == null)
			{
				return;
			}
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
			FluidDef fluid = FluidAt(c) ?? ActiveFluid;
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
		/// Returns FALSE for a cell this engine does not own (not excavated), AND for
		/// an owned cell that refused the write (liquid switched off, or a different
		/// liquid already standing). Only the first is the signal to keep the
		/// driver's own behaviour; use <see cref="TrySetDriverFillOutcome"/> to tell
		/// them apart (FLOOD_DRIVER_OWNERSHIP_CONTRACT_1) — a driver that writes
		/// terrain after a Refused is writing on a cell this engine owns.
		/// A caller must record the previous <see cref="FillAt"/> itself if it
		/// intends to restore it: this engine deliberately keeps no per-driver
		/// undo stack, because the next pulse may legitimately move that liquid
		/// somewhere else and a stale undo would resurrect it.</summary>
		public bool TrySetDriverFill(IntVec3 c, int fill, FluidDef driverFluid = null)
		{
			return TrySetDriverFillOutcome(c, fill, driverFluid) == DriverFillOutcome.Applied;
		}

		/// <summary>FLOOD_DRIVER_OWNERSHIP_CONTRACT_1: what a driver write did. NotOwned = not excavated, the
		/// driver keeps its own behaviour; Refused = the engine owns the cell and declined (disabled or foreign
		/// liquid), the driver must leave the cell alone; Applied = written.</summary>
		public enum DriverFillOutcome { NotOwned, Refused, Applied }

		// FLOW_ORDER_EXTERNAL_INPUT_1: cell index -> tick a driver last RAISED its fill. Not saved: after a load a pump
		// re-marks its cell on its next write.
		private readonly Dictionary<int, int> driverInputTick = new Dictionary<int, int>();
		// PROVISIONAL (auto-decided 2026-10-09, FLOW_ORDER_EXTERNAL_INPUT_1): a driver input seeds the flow order for 5000 ticks after its last write.
		private const int DriverInputWindowTicks = 5000;
		private readonly List<int> driverInputScratch = new List<int>();

		private void PruneDriverInputs()
		{
			if (driverInputTick.Count == 0)
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			driverInputScratch.Clear();
			foreach (KeyValuePair<int, int> kv in driverInputTick)
			{
				if (now - kv.Value > DriverInputWindowTicks || depthGrid[kv.Key] == 0)
				{
					driverInputScratch.Add(kv.Key);
				}
			}
			foreach (int k in driverInputScratch)
			{
				driverInputTick.Remove(k);
			}
		}

		public DriverFillOutcome TrySetDriverFillOutcome(IntVec3 c, int fill, FluidDef driverFluid = null)
		{
			if (!c.InBounds(map))
			{
				return DriverFillOutcome.NotOwned;
			}
			int i = map.cellIndices.CellToIndex(c);
			byte d = depthGrid[i];
			if (d == 0)
			{
				return DriverFillOutcome.NotOwned;
			}
			if (fill < 0)
			{
				fill = 0;
			}
			if (fill > d)
			{
				fill = d;
			}
			// Step 2b: a driver claiming a dry cell stamps its fluid (default: the map's); it cannot pour into a cell
			// already holding a different fluid (fluids never mix): Refused, and the caller must leave the cell alone.
			FluidDef fluid = driverFluid ?? FluidAt(c) ?? ActiveFluid;
			// FLOWWORKS_REVIEW_LOOKS_ROUND_1: a liquid switched off in Mod Settings never pours into a cut.
			if (fill > fillGrid[i] && !InputAllowed(fluid))
			{
				return DriverFillOutcome.Refused;
			}
			if (fill > 0 && !RM_StockMath.FluidsCompatible(fillGrid[i] > 0, FluidAt(c), fluid))
			{
				return DriverFillOutcome.Refused;
			}
			if (fill > 0 && fillGrid[i] == 0)
			{
				fluidGrid[i] = PaletteKey(fluid);
			}
			if (fill > fillGrid[i])
			{
				driverInputTick[i] = Find.TickManager.TicksGame;
			}
			fillGrid[i] = (byte)fill;
			if (fill == 0)
			{
				fluidGrid[i] = 0;
			}
			if (fluid != null)
			{
				ApplyFillTerrain(c, fluid);
			}
			return DriverFillOutcome.Applied;
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
