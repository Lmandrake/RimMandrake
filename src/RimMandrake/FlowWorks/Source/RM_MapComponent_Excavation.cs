using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>POND_RETURN_LEG_BUILD_WATER_GOES_HOME (GPT #11): what a restore of the recorded terrain did.</summary>
	public enum RM_RestoreResult { Restored, NoRecord, WriteFailed }

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
	/// CrackedLands's RM_MapComponent_CanyonFlood, which already owns a
	/// phased, save-safe, per-cell flow engine; this is a port of that shape,
	/// not an invention.
	///
	/// PILLAR 2: NO PER-TICK FLUID WORK. MapComponentTick calls, every tick,
	/// superdeepTrap.Tick (while a D=4 cell exists, or under the relative climb rule while anything is dug or a dry
	/// bed is a hollow), RM_PocketGrid.Tick, RM_PitExposure.Tick,
	/// liquidFire.Tick, liquidHeat.Tick, RM_SlimeSlip, RM_Swim, RM_PitFillEffects.Tick, RefreshDugSwim (every
	/// SwimRefreshTicks) and the water-look watcher (only while an excavated cell exists, where each says so). superdeepTrap.Tick does real work EVERY tick:
	/// it walks the spawned pawns, because the descent detector compares each
	/// pawn's cell with the one it held the tick before. The others each
	/// gate on their own interval and return. None of it is fluid work.
	/// The whole sort-and-overflow runs on a settings-tunable pulse cadence
	/// (default 250 ticks, vanilla's own rare cadence). There is no fluid
	/// simulation and there will not be one.
	/// RM_Levelling.Tick, then the liquid-net SettleTick and TheftTick, also run from MapComponentTick, once per pump cycle (250 ticks).
	///
	/// A SOURCE IS TERRAIN (owner ruling 2026-09-16, and ruling 24). A natural
	/// liquid cell is not a building with a comp — it reads as D = SUPERDEEP,
	/// F = SUPERDEEP through a READ-THROUGH ADAPTER below. Nothing is copied
	/// into the byte grids for it, so nothing can fall out of sync with the
	/// map when a lake is drained, dug into, or filled in. Limited stock,
	/// recession and refill (rulings 2 and 4) are live in RM_LiquidStock,
	/// run by <c>stock.Pulse</c> each pulse; rain lands through ApplyRain.
	/// </summary>
	public class RM_MapComponent_Excavation : MapComponent, RM_IFlowWorld, RM_ILevelWorld
	{
		/// <summary>D in notches (0.5 m each). 0 = surface; 1..3 shallow to deep; 4 (2 m, RM_ExcavationDepth.Superdeep) and deeper
		/// is a pit, up to RM_ExcavationDepth.MaxDigCeiling.</summary>
		private byte[] depthGrid;

		/// <summary>F. Always clamped to 0 &lt;= F &lt;= D.</summary>
		private byte[] fillGrid;

		/// <summary>WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES (owner 2026-10-17, ruled exactly level by card): the decilitres below
		/// one whole notch, per cell (0..U-1). A dug cell's water is W = F·U + part; F stays the whole-notch view every older
		/// reader uses. Written by the exact kernel (RM_FlowKernel.levelExactEnabled); 0 everywhere on a save from before it,
		/// so an old save loads with every litre unchanged. SCRIBED (2 bytes a cell, deflated).</summary>
		private ushort[] partGrid;

		/// <summary>WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: 0 = a save from before exact-level water (its ponds' stock was a float
		/// of levels), 1 = exact (ponds hold whole decilitres). The one-time migration in FinalizeInit logs every body's litres
		/// before and after.</summary>
		private int levelModel;

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

		/// <summary>POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK §8.3: the volume model this map's bodies were sized under.
		/// A new map starts current; a save without the key loads as 1 and is migrated once in FinalizeInit.</summary>
		private int volumeModel = RM_Volume.CurrentModel;

		/// <summary>LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (unified depth spec §9): 1 = the pond budget slider is gone and every limited
		/// pond is sized by its floor alone (RM_LiquidStock.MigrateBudgetMultiplier ran). A new map starts at 1; a save without
		/// the key loads as 0 and is migrated once in FinalizeInit.</summary>
		private int pondBudgetModel = 1;

		/// <summary>LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (unified depth spec §9, "RM_depthViewModel"): 1 = every wet dug square shows
		/// the look of its metres of water. A save without the key (0) has looks chosen by fullness: each wet dug square is
		/// re-picked once on load (nothing about the water changes).</summary>
		private int depthViewModel = 1;

		/// <summary>POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD (rebuild P14): 1 = wet dug squares carry their liquid on the BASE
		/// terrain layer (the one ladder, RM_WaterLadder), the temp layer left to vanilla (ice, floods). A save without the
		/// key (0) carries them on the temp layer: MigrateFillLayer moves every one to a base write once on load, litres
		/// logged before and after. A new map starts at 1.</summary>
		private int fillLayerModel = 1;

		/// <summary>POND_RETURN_LEG_BUILD_WATER_GOES_HOME, owner ruling 6 (GPT #10's natural-bed record): cell index → id
		/// of the pond a DUG dry-bed square was taken out of. Filling the square back in to the surface returns it there,
		/// dry. Separate from originalTerrain (the excavation's record), so lake provenance survives the dig.</summary>
		private Dictionary<int, int> detachedBedCells = new Dictionary<int, int>();
		private List<int> detachedBedKeys;
		private List<int> detachedBedValues;

		/// <summary>POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE, step 1 (GPT #9's ownership predicate): the bed depth (levels) of
		/// every DRY natural pond square, 0 elsewhere. Derived, never scribed: rebuilt in FinalizeInit from the bodies'
		/// receded lists; kept current by DryNaturalCell, RestoreOriginalTerrain and the dug-bed detach/reattach.</summary>
		private byte[] bedGrid;

		/// <summary>POND_BED step 2: how many bedGrid entries are non-zero (the climb rule's early-out), kept by SetBed.</summary>
		private int bedCellCount;

		/// <summary>LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP: the floor of every limited lake square, recorded once when its body
		/// formed (RM_LakeFloorMath.Floor), 0 elsewhere (BedLevelsAt then reads the water terrain: shallow 2, deep 4). SCRIBED: the shape a drained lake leaves and refills to must survive a reload exactly, and the
		/// water terrain it was derived from is gone once the lake is dry. A map with no big lake saves an all-zero grid.</summary>
		private byte[] bedRecord;

		/// <summary>LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP (R10 step 1): every natural body on this map has been formed (and each
		/// limited lake's floor recorded). False on a new map and on a save from before the flag: FinalizeInit forms them once.</summary>
		private bool lakeFloorsFormed;

		/// <summary>L0 ledger (G10): fill levels burned off by liquid fire, the fire's disclosed exit.</summary>
		private float burnedLevelsTotal;

		/// <summary>L0 ledger: whole levels the return leg credited to limitless bodies (they leave our books).</summary>
		private float limitlessReturnedTotal;

		/// <summary>POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD §7: the pond picture this map's bodies are laid in (0 = full-or-empty
		/// squares, the old model; 1 = one flat surface, shallowing all over). A save without the key loads as 0 and is re-laid
		/// once (touched ponds only) on the first pulse with "pondDepthEnabled" on; turning the setting off re-lays back.</summary>
		private int pondDepthModel;

		/// <summary>POND_DEPTH §4: cell index → tick a pond square was exposed as mud. It cracks to lakebed after the mud time
		/// ("pondMudDays"); water returning first skips the lakebed step. SCRIBED, so a reload does not crack fresh mud.</summary>
		private Dictionary<int, int> pondMudSince = new Dictionary<int, int>();
		private List<int> pondMudKeys;
		private List<int> pondMudValues;

		/// <summary>PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT: "dig to N m" — cell index → target depth in notches, for a square carrying
		/// an RM_DigCanal designation made by Designator_DigCanalTo. After each cut the job puts the designation back while the
		/// square is above its target (JobDriver_DigCanal). No entry = a plain one-notch dig. SCRIBED ("RM_digTargets"; absent in
		/// an older save = none). Entries without a designation are dropped on save.</summary>
		private Dictionary<int, int> digTargets = new Dictionary<int, int>();
		private List<int> digTargetKeys;
		private List<int> digTargetValues;

		/// <summary>POND_DEPTH: terrain restages left this pulse (the §8 cost guard), reset by RM_LiquidStock.Pulse.</summary>
		internal int pondStageWritesLeft;

		public int PondDepthModel
		{
			get => pondDepthModel;
			set => pondDepthModel = value;
		}
		/// <summary>FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS: levels the dev-placed flow sources poured in and the flow sinks
		/// took out (MapControls/). Both act BEFORE the kernel measures a pulse's "before", like rain, so the per-component
		/// ledger never sees them; these totals are where they are disclosed (the L0 ledger report).</summary>
		private float mapControlPouredTotal;
		private float mapControlDrainedTotal;

		/// <summary>A map control (source or sink) moved liquid across the map's boundary this pulse; recorded for the ledger.</summary>
		public void NoteMapControlFlow(int pouredLevels, int drainedLevels)
		{
			mapControlPouredTotal += pouredLevels;
			mapControlDrainedTotal += drainedLevels;
		}

		public float MapControlPouredTotal => mapControlPouredTotal;
		public float MapControlDrainedTotal => mapControlDrainedTotal;

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
		/// credits must sum to zero except the disclosed exits: this one (liquid destroyed by
		/// overflow the sheet refused) and the others LedgerReport lists (sunk, burned, released, to a limitless body).
		/// Recorded so each exit is disclosed rather than silent; a silent leak in a conservation-of-mass system reads as a bug.</summary>
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
		/// map cannot turn a bounded pulse into a frame hitch. Seeds the kernel only: every pulse overwrites the
		/// kernel's cap with RimMandrakeFlowWorksSettings.MaxNetworkCells.</summary>
		private const int MaxComponentCells = 6000;

		public RM_MapComponent_Excavation(Map map)
			: base(map)
		{
			EnsureGrids();
		}

		public float OverflowDestroyedTotal => overflowDestroyedTotal;

		/// <summary>Owner card 2026-10-22 ("Count silently, show in ledger"): what released floods (a heat-kit release, a forge
		/// flood, a tar belch) had nowhere to go, in dL. Counted with the overflow exit (destroyed), shown in the liquid ledger
		/// readout (Mod Settings, spilled-water section), never messaged.</summary>
		private long releaseLostDl;

		public long ReleaseLostDl => releaseLostDl;

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

		/// <summary>PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP: dug at all, null-safe for region building like IsSuperdeepRaw.</summary>
		public bool IsDugRaw(IntVec3 c)
		{
			return depthGrid != null && c.InBounds(map) && depthGrid[map.cellIndices.CellToIndex(c)] != 0;
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

		/// <summary>PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE: <see cref="ExcavatedDepthAt"/>, null-safe on the grid for region
		/// building (like IsSuperdeepRaw), which the pit-room test runs inside.</summary>
		public int ExcavatedDepthRaw(IntVec3 c)
		{
			return depthGrid != null && c.InBounds(map) ? depthGrid[map.cellIndices.CellToIndex(c)] : 0;
		}

		// ── PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP: the climb depth and its generation ──────────

		private int climbGeneration;

		/// <summary>Moves on every write that can change who is trapped where (depth, covers, climb settings); the pocket
		/// grid (RM_PocketGrid) rebuilds when it moved. Derived, never scribed.</summary>
		public int ClimbGeneration => climbGeneration;

		public void BumpClimbGeneration()
		{
			climbGeneration++;
		}

		/// <summary>The ONE depth the relative climb rule reads (design §8.1, GPT #17): the hollow depth, i.e. the dug depth,
		/// or a dry natural bed's depth (POND_BED step 2, RM_Volume.HollowDepth) when hollows are on.</summary>
		public int ClimbDepthAt(IntVec3 c)
		{
			int h = HollowDepthAt(c);
			if (h == 0 || swimCells.Count == 0)
			{
				return h;
			}
			return swimClimb.TryGetValue(map.cellIndices.CellToIndex(c), out int s) ? RM_SwimMath.ClimbDepthWithSwim(h, s) : h;
		}

		// ── SWIM_DUG_RESERVOIR_FIX_PAWNS_CANT_ENTER: dug water 2 m or deeper is swum (owner R12) ──────────
		// A swimmer floats at the surface, so the climb rule (pocket grid, cliff masks, RelativeVeto, step cost: all through
		// ClimbDepthAt / CopyClimbDepth) judges a dug swim square at its WATER SURFACE (RM_SwimMath.DugSwimClimbDepth): a brim-
		// full reservoir is level ground to a swimmer, a half-full sheer pit still has its wall above the water. The path grid
		// prices a swim square at the swim cost and the swim offset grids close it to non-swimmers (RM_SwimWater.IsDeepSwimCell
		// reads IsDugSwimCell). A DRY pit, water under 2 m and a liquid that is never swum keep the pit rules. Derived, never
		// scribed: refreshed every SwimRefreshTicks and after each pulse; a change moves the climb generation, re-cuts the swim
		// grids and re-reads those squares' path costs.
		public const int SwimRefreshTicks = 60;
		private readonly Dictionary<int, int> swimClimb = new Dictionary<int, int>();
		private readonly HashSet<int> swimCells = new HashSet<int>();
		private readonly Dictionary<int, int> swimFreshScratch = new Dictionary<int, int>();
		private readonly List<int> swimChangedScratch = new List<int>();

		/// <summary>A dug square holding swimmable water 2 m or deeper (swimming on).</summary>
		public bool IsDugSwimCell(IntVec3 c)
		{
			return swimCells.Count > 0 && c.InBounds(map) && swimCells.Contains(map.cellIndices.CellToIndex(c));
		}

		public int DugSwimCellCount => swimCells.Count;

		/// <summary>Re-derive the dug swim squares; returns how many changed (each change re-cuts what reads them).</summary>
		public int RefreshDugSwim()
		{
			bool on = Swimming.RM_SwimWater.On;
			// Scratch reused across calls (FlowWorks review 2026-10-22): this runs every SwimRefreshTicks on every map.
			Dictionary<int, int> fresh = swimFreshScratch;
			fresh.Clear();
			List<int> changed = swimChangedScratch;
			changed.Clear();
			if (on)
			{
				foreach (IntVec3 c in excavatedCells)
				{
					int i = map.cellIndices.CellToIndex(c);
					long dl = WaterDl(i);
					if (dl <= 0)
					{
						continue;
					}
					int s = RM_SwimMath.DugSwimClimbDepth(true, Swimming.RM_SwimWater.LiquidSwimmableAt(map, this, c), depthGrid[i],
						RM_LevelSolve.Metres(dl), (int)(dl / RM_LevelSolve.U));
					if (s >= 0)
					{
						fresh[i] = s;
					}
				}
			}
			foreach (KeyValuePair<int, int> kv in fresh)
			{
				if (!swimClimb.TryGetValue(kv.Key, out int old) || old != kv.Value)
				{
					changed.Add(kv.Key);
				}
			}
			foreach (int i in swimCells)
			{
				if (!fresh.ContainsKey(i))
				{
					changed.Add(i);
				}
			}
			if (changed.Count == 0)
			{
				return 0;
			}
			swimClimb.Clear();
			swimCells.Clear();
			foreach (KeyValuePair<int, int> kv in fresh)
			{
				swimClimb[kv.Key] = kv.Value;
				swimCells.Add(kv.Key);
			}
			BumpClimbGeneration();
			Swimming.RM_SwimPathing.Bump(map);
			foreach (int i in changed)
			{
				map.pathing?.RecalculatePerceivedPathCostAt(map.cellIndices.IndexToCell(i));
			}
			map.reachability?.ClearCache();
			return changed.Count;
		}

		/// <summary>POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE step 2: the depth a square reads as a hole — dug depth, else a dry
		/// pond square's bed depth (2 shallow, 4 deep) while <c>pondBedHollowEnabled</c>, else 0. What the climb rule, the
		/// pawn sink, the wall faces, the lip occlusion and the step cost read. Natural WATER is not a hole here (it reads 0,
		/// as before): only DepthAt reads it through as SUPERDEEP, for flow.</summary>
		public int HollowDepthAt(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return 0;
			}
			int i = map.cellIndices.CellToIndex(c);
			return RM_Volume.HollowDepth(depthGrid[i], bedGrid[i], RimMandrakeFlowWorksSettings.pondBedHollowEnabled);
		}

		/// <summary>Anything on this map the climb rule must look at: a dug square, or (hollows on) a dry bed square.</summary>
		public int ClimbCellCount => excavatedCells.Count + (RimMandrakeFlowWorksSettings.pondBedHollowEnabled ? bedCellCount : 0);

		/// <summary>Every square ClimbDepthAt can read non-zero: the dug set, then (hollows on) each pond's dry bed squares.</summary>
		public IEnumerable<IntVec3> ClimbCells()
		{
			foreach (IntVec3 c in excavatedCells)
			{
				yield return c;
			}
			if (!RimMandrakeFlowWorksSettings.pondBedHollowEnabled || bedCellCount == 0)
			{
				yield break;
			}
			foreach (RM_LiquidBody b in stock.Bodies)
			{
				for (int k = 0; k < b.receded.Count; k++)
				{
					if (IsNaturalBed(b.receded[k]))
					{
						yield return b.receded[k];
					}
				}
			}
		}

		/// <summary>ClimbDepthAt for every cell, into a CellIndices-ordered array (the pocket grid's input).</summary>
		public void CopyClimbDepth(byte[] into)
		{
			int n = System.Math.Min(depthGrid.Length, into.Length);
			System.Array.Copy(depthGrid, into, n);
			if (RimMandrakeFlowWorksSettings.pondBedHollowEnabled && bedCellCount > 0)
			{
				for (int i = 0; i < n; i++)
				{
					into[i] = (byte)RM_Volume.HollowDepth(depthGrid[i], bedGrid[i], true);
				}
			}
			// SWIM_DUG_RESERVOIR_FIX_PAWNS_CANT_ENTER: a dug swim square at its water surface (same rule as ClimbDepthAt)
			foreach (KeyValuePair<int, int> kv in swimClimb)
			{
				if (kv.Key < n)
				{
					into[kv.Key] = (byte)RM_SwimMath.ClimbDepthWithSwim(into[kv.Key], kv.Value);
				}
			}
		}

		/// <summary>Every excavated cell at D >= Superdeep (2 m or deeper). Walks the excavated set, not
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
			if (partGrid == null || partGrid.Length != cells)
			{
				if (partGrid != null)
				{
					WarnWrongSizedGrid("water part", new byte[partGrid.Length], cells);
				}
				partGrid = new ushort[cells];
			}
			if (fluidPalette == null)
			{
				fluidPalette = new List<FluidDef>();
			}
			if (bedGrid == null || bedGrid.Length != cells)
			{
				bedGrid = new byte[cells];
			}
			if (bedRecord == null || bedRecord.Length != cells)
			{
				WarnWrongSizedGrid("bed record", bedRecord, cells);
				bedRecord = new byte[cells];
			}
		}

		/// <summary>POND_ELEVATION_BUILD_LAKES_RUN_DEEP: record a lake square's deep bed (RM_LiquidStock.FormBody, once).</summary>
		public void RecordBedDepth(int i, int levels)
		{
			if (i >= 0 && i < bedRecord.Length)
			{
				bedRecord[i] = (byte)System.Math.Min(System.Math.Max(levels, 0), RM_BedMath.MaxStorableDepth);
			}
		}

		/// <summary>LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP: the floor generator's inputs for this map. The seed is the world's
		/// persistent value and the map's constant seed (both saved, so an old save forms its lakes the same on every machine);
		/// roughness is the tile's hilliness as the map generator used it, plus the biome's bias.</summary>
		public RM_LakeFloorMath.Params LakeFloorParams()
		{
			int seed = Gen.HashCombineInt(Find.World?.info?.persistentRandomValue ?? 0, map.ConstantRandSeed);
			int hill = 2;
			string biome = null;
			try
			{
				hill = (int)map.TileInfo.HillinessForElevationGen;
				biome = map.Biome?.defName;
			}
			catch (System.Exception)
			{
				// a map with no world tile (a pocket map): small hills
			}
			RM_LakeFloorMath.Params p = RM_LakeFloorMath.Params.Defaults(seed, RM_LakeFloorMath.Roughness(hill, biome));
			p.depthScale = RimMandrakeFlowWorksSettings.lakeDepthScale;
			p.roughnessScale = RimMandrakeFlowWorksSettings.lakeFloorRoughness;
			p.ceilingNotches = RimMandrakeFlowWorksSettings.DeepBedMaxDepth;
			p.shelfNotches = RimMandrakeFlowWorksSettings.LakeShoreShelfNotches;
			p.wayOutNotches = RimMandrakeFlowWorksSettings.LakeWayOutNotches;
			return p;
		}

		/// <summary>The deepest bed recorded on this map (0 = none past the deep notch): the proof's read.</summary>
		public int DeepestRecordedBed()
		{
			int m = 0;
			for (int i = 0; i < bedRecord.Length; i++)
			{
				if (bedRecord[i] > m)
				{
					m = bedRecord[i];
				}
			}
			return m;
		}

		/// <summary>POND_BED step 1: rebuild the derived bed grid from the bodies (a receded square that is not dug).</summary>
		private void RebuildBedGrid()
		{
			System.Array.Clear(bedGrid, 0, bedGrid.Length);
			bedCellCount = 0;
			foreach (RM_LiquidBody b in stock.Bodies)
			{
				TerrainDef mud = (b.fluid ?? ActiveFluid)?.recededTerrain;
				for (int k = 0; k < b.receded.Count; k++)
				{
					IntVec3 c = b.receded[k];
					if (c.InBounds(map) && !IsExcavated(c))
					{
						SetBed(map.cellIndices.CellToIndex(c), BedLevelsAt(c));
						// POND_BED step 2: a bed dried before hollows existed (or with them off) still shows the old mud; lay the
						// lakebed over it now. Only bare mud is repainted (a floor or anything the player laid stays).
						if (RimMandrakeFlowWorksSettings.pondBedHollowEnabled && mud != null && map.terrainGrid.TopTerrainAt(c) == mud
							&& !pondMudSince.ContainsKey(map.cellIndices.CellToIndex(c)))   // POND_DEPTH: fresh mud keeps its time
						{
							map.terrainGrid.SetTerrain(c, LakebedTerrainFor(c));
						}
					}
				}
			}
			BumpClimbGeneration();
		}

		/// <summary>POND_BED step 2: the one writer of bedGrid, so the count and the climb generation can never drift from it.</summary>
		private void SetBed(int i, int levels)
		{
			byte v = (byte)levels;
			if (bedGrid[i] == v)
			{
				return;
			}
			if (bedGrid[i] == 0)
			{
				bedCellCount++;
			}
			else if (v == 0)
			{
				bedCellCount--;
			}
			bedGrid[i] = v;
			BumpClimbGeneration();
		}

		/// <summary>POND_BED step 2 (owner look (b)): the cracked lakebed for this square's bed depth.</summary>
		private TerrainDef LakebedTerrainFor(IntVec3 c)
		{
			switch (RM_Volume.LakebedFor(BedLevelsAt(c)))
			{
				case "RM_Lakebed_Abyss": return RimMandrakeFlowWorks_DefOf.RM_Lakebed_Abyss;   // POND_ELEVATION: the deep middle
				case "RM_Lakebed_Deep": return RimMandrakeFlowWorks_DefOf.RM_Lakebed_Deep;
				default: return RimMandrakeFlowWorks_DefOf.RM_Lakebed_Shallow;
			}
		}

		/// <summary>POND_BED step 1 (GPT #9): is this a DRY square of a natural pond's bed — receded, not dug? One owner per
		/// drop: water arriving here belongs to the pond's stock (the return leg), never to a dug cell.</summary>
		public bool IsNaturalBed(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return false;
			}
			int i = map.cellIndices.CellToIndex(c);
			return bedGrid[i] != 0 && depthGrid[i] == 0;
		}

		/// <summary>POND_BED step 1: the bed depth of a dry pond square (2 shallow, 4 deep; 0 when not a bed), whatever the
		/// hollow setting. Step 2's readers go through HollowDepthAt / DepthAt, which honour it.</summary>
		public int NaturalBedDepthAt(IntVec3 c)
		{
			return IsNaturalBed(c) ? bedGrid[map.cellIndices.CellToIndex(c)] : 0;
		}

		/// <summary>POND_BED (owner by card 2026-10-14): the depth a first cut here would make (RM_Volume.FirstCutDepth), -1 when
		/// the dig is refused. The designator, the work giver and Deepen share it. Held to the designation cap (the deepest
		/// anyone may dig: DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL); the work giver asks again with the digger's own cap.</summary>
		public int FirstCutDepthAt(IntVec3 c)
		{
			return FirstCutDepthAt(c, RM_DigLabor.DesignationCap);
		}

		/// <summary><see cref="FirstCutDepthAt(IntVec3)"/> under one digger's cap.</summary>
		public int FirstCutDepthAt(IntVec3 c, int cap)
		{
			return RM_Volume.FirstCutDepth(NaturalBedDepthAt(c), RimMandrakeFlowWorksSettings.pondBedHollowEnabled,
				cap, RimMandrakeFlowWorksSettings.digToDepthEnabled);
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
		/// clamps D to 0..MaxDigCeiling and F to 0..D, clears fluid keys past the palette, then drops palette entries no cell
		/// uses (null entries included) and remaps the grid, so a long campaign never exhausts the 254 keys.
		/// One log line when anything changed.</summary>
		internal void RepairLoadedGrids()
		{
			if (!RimMandrakeFlowWorksSettings.excavationLoadRepairEnabled || depthGrid == null)
			{
				return;
			}
			// PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT: clamp to the 20 m ceiling, never to the cap setting (lowering the cap never
			// shallows a dug cell).
			RM_ExcavationSanityMath.Report r = RM_ExcavationSanityMath.Repair(depthGrid, fillGrid, fluidGrid,
				fluidPalette.Count, RM_ExcavationDepth.MaxDigCeiling);
			// WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: a part never stands above the brim or on an undug cell.
			r.fillClamped += RM_ExcavationSanityMath.RepairPart(depthGrid, fillGrid, partGrid, RM_LevelSolve.U);
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

		private bool paletteExhaustedWarned;

		/// <summary>FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO (P7): the key for <paramref name="fluid"/>, compacting a full
		/// palette in the running session. False only for a real fluid with no free key; every writer then refuses
		/// the cell BEFORE changing its fill or debiting a source, so a liquid never changes identity. A null fluid
		/// is key 0 and succeeds (the existing "unrecorded, take the map default" case).</summary>
		private bool TryPaletteKey(FluidDef fluid, out byte key)
		{
			if (fluidPalette == null)
			{
				fluidPalette = new List<FluidDef>();
			}
			int dropped;
			key = RM_ExcavationSanityMath.AllocateKey(fluidPalette, fluidGrid, fluid, RM_ExcavationSanityMath.MaxPaletteKeys,
				out dropped);
			if (dropped > 0)
			{
				Log.Message("[RimMandrake.FlowWorks] fluid palette was full; " + dropped + " unused entr"
					+ (dropped == 1 ? "y" : "ies") + " compacted in session.");
			}
			if (fluid != null && key == 0)
			{
				if (!paletteExhaustedWarned)
				{
					paletteExhaustedWarned = true;
					Log.Warning("[RimMandrake.FlowWorks] fluid palette exhausted: " + RM_ExcavationSanityMath.MaxPaletteKeys
						+ " distinct liquids are in excavated cells on this map; " + fluid.defName
						+ " is refused entry to dry cells rather than recorded as another liquid.");
				}
				return false;
			}
			return true;
		}

		private byte PaletteKey(FluidDef fluid)
		{
			byte key;
			TryPaletteKey(fluid, out key);
			return key;
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
				if (!WetDug(i))
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
			// WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: the part-notch grid, 2 bytes a cell (absent in an older save: all 0).
			byte[] partBytes = Scribe.mode == LoadSaveMode.Saving ? PackPart(partGrid) : null;
			DataExposeUtility.LookByteArray(ref partBytes, "RM_excavationPartGrid");
			if (Scribe.mode == LoadSaveMode.LoadingVars)
			{
				partGrid = UnpackPart(partBytes);
			}
			Scribe_Values.Look(ref levelModel, "RM_levelModel", 0);
			DataExposeUtility.LookByteArray(ref fluidGrid, "RM_excavationFluidGrid");
			DataExposeUtility.LookByteArray(ref bedRecord, "RM_bedDepthRecord");
			Scribe_Values.Look(ref lakeFloorsFormed, "RM_lakeFloorsFormed", false);
			Scribe_Collections.Look(ref fluidPalette, "RM_excavationFluidPalette", LookMode.Def);
			Scribe_Defs.Look(ref activeFluid, "RM_activeFluid");
			Scribe_Values.Look(ref nextPulseTick, "RM_nextPulseTick", -1);
			Scribe_Values.Look(ref pulseCount, "RM_pulseCount", 0L);
			Scribe_Values.Look(ref overflowDestroyedTotal, "RM_overflowDestroyedTotal", 0f);
			Scribe_Values.Look(ref releaseLostDl, "RM_releaseLostDl", 0L);
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
			Scribe_Values.Look(ref volumeModel, "RM_volumeModel", 1);
			Scribe_Values.Look(ref pondBudgetModel, "RM_pondBudgetModel", 0);
			Scribe_Values.Look(ref depthViewModel, "RM_depthViewModel", 0);
			Scribe_Values.Look(ref fillLayerModel, "RM_fillLayerModel", 0);
			Scribe_Collections.Look(ref detachedBedCells, "RM_detachedBedCells", LookMode.Value, LookMode.Value,
				ref detachedBedKeys, ref detachedBedValues);
			Scribe_Values.Look(ref burnedLevelsTotal, "RM_burnedLevelsTotal", 0f);
			Scribe_Values.Look(ref limitlessReturnedTotal, "RM_limitlessReturnedTotal", 0f);
			Scribe_Values.Look(ref mapControlPouredTotal, "RM_mapControlPouredTotal", 0f);
			Scribe_Values.Look(ref mapControlDrainedTotal, "RM_mapControlDrainedTotal", 0f);
			Scribe_Values.Look(ref pondDepthModel, "RM_pondDepthModel", 0);
			Scribe_Collections.Look(ref pondMudSince, "RM_pondMudSince", LookMode.Value, LookMode.Value, ref pondMudKeys, ref pondMudValues);
			if (Scribe.mode == LoadSaveMode.Saving)
			{
				PruneDigTargets();
			}
			Scribe_Collections.Look(ref digTargets, "RM_digTargets", LookMode.Value, LookMode.Value, ref digTargetKeys, ref digTargetValues);
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
				if (detachedBedCells == null)
				{
					detachedBedCells = new Dictionary<int, int>();
				}
				if (pondMudSince == null)
				{
					pondMudSince = new Dictionary<int, int>();
				}
				if (digTargets == null)
				{
					digTargets = new Dictionary<int, int>();
				}
			}
		}

		// ── PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT: "dig to N m" ───────────────────────────────────────

		/// <summary>The dig-to target on this square in notches, 0 when none (a plain one-notch dig).</summary>
		public int DigTargetAt(IntVec3 c)
		{
			return c.InBounds(map) && digTargets.TryGetValue(map.cellIndices.CellToIndex(c), out int t) ? t : 0;
		}

		/// <summary>Set (notches > 0) or clear (0) the dig-to target of a square.</summary>
		public void SetDigTarget(IntVec3 c, int notches)
		{
			if (!c.InBounds(map))
			{
				return;
			}
			int i = map.cellIndices.CellToIndex(c);
			if (notches > 0)
			{
				digTargets[i] = System.Math.Min(notches, RM_DigDepthMath.MaxDigCeiling);
			}
			else
			{
				digTargets.Remove(i);
			}
		}

		/// <summary>Does this square still owe cuts toward its dig-to target under today's caps (anyone's: a colonist-stopped
		/// order waits for machine labour)?</summary>
		public bool DigToOwesWork(IntVec3 c)
		{
			return RM_DigDepthMath.DigToOwesWork(ExcavatedDepthAt(c), DigTargetAt(c), RM_DigLabor.OrderCap);
		}

		/// <summary>Drop targets whose square carries no dig designation any more (cancelled, finished, or never placed).</summary>
		private void PruneDigTargets()
		{
			if (digTargets == null || digTargets.Count == 0 || map?.designationManager == null)
			{
				return;
			}
			List<int> dead = null;
			foreach (KeyValuePair<int, int> kv in digTargets)
			{
				IntVec3 c = map.cellIndices.IndexToCell(kv.Key);
				if (map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal) == null)
				{
					(dead ??= new List<int>()).Add(kv.Key);
				}
			}
			if (dead != null)
			{
				foreach (int k in dead)
				{
					digTargets.Remove(k);
				}
			}
		}

		private static byte[] PackPart(ushort[] grid)
		{
			if (grid == null)
			{
				return null;
			}
			byte[] b = new byte[grid.Length * 2];
			for (int i = 0; i < grid.Length; i++)
			{
				b[2 * i] = (byte)(grid[i] & 0xff);
				b[2 * i + 1] = (byte)(grid[i] >> 8);
			}
			return b;
		}

		private static ushort[] UnpackPart(byte[] b)
		{
			if (b == null)
			{
				return null;
			}
			ushort[] g = new ushort[b.Length / 2];
			for (int i = 0; i < g.Length; i++)
			{
				g[i] = (ushort)(b[2 * i] | (b[2 * i + 1] << 8));
			}
			return g;
		}

		/// <summary>WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: the one-time migration of a save from before exact-level water. Every
		/// canal square keeps its whole notches (W = F·U, part 0) and every pond its stock (RM_LiquidBody read its float stock
		/// into whole decilitres on load); one log line per body says its litres before and after, so "nothing lost" is
		/// read off the log, not assumed.</summary>
		private void MigrateLevelModel()
		{
			if (levelModel >= 1)
			{
				return;
			}
			long canalDl = 0;
			int wet = 0;
			foreach (IntVec3 c in excavatedCells)
			{
				int i = map.cellIndices.CellToIndex(c);
				if (WetDug(i))
				{
					wet++;
					canalDl += WaterDl(i);
				}
			}
			var sb = new System.Text.StringBuilder();
			sb.Append("[RimMandrake.FlowWorks] level model 0 -> 1 (exact decilitres, one surface per body): canals ")
				.Append(wet).Append(" wet square(s), ").Append(RM_Volume.FormatLitres(canalDl / 10f)).Append(" before and after");
			int ponds = 0;
			foreach (RM_LiquidBody b in stock.Bodies)
			{
				if (b.limitless)
				{
					continue;
				}
				ponds++;
				sb.Append("; pond #").Append(b.id).Append(" ").Append(RM_Volume.FormatLitres(b.legacyStock * RM_Volume.LitresPerLevel))
					.Append(" -> ").Append(RM_Volume.FormatLitres(b.stockDl / 10f));
			}
			sb.Append(" (").Append(ponds).Append(" limited pond(s)).");
			Log.Message(sb.ToString());
			levelModel = 1;
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
			BumpClimbGeneration(); // the pocket grid may have been built by region building before a legacy rehydrate
			if (originalTerrain == null)
			{
				originalTerrain = new Dictionary<int, TerrainDef>();
			}
			if (stock == null)
			{
				stock = new RM_LiquidStock();
			}
			stock.RebuildIndex(map);
			// Model 1 -> 2 rescales ponds (one square = one square). Model 2 -> 3 (litres) changes no pond: a pond's stock is
			// in fill-units of LEVELS, which did not change; every tank-unit holder converts itself (RM_Volume.FromLegacyUnits).
			if (volumeModel < RM_Volume.CurrentModel)
			{
				int rescaled = volumeModel < 2 ? stock.MigrateVolumeModel(this) : 0;
				Log.Message("[RimMandrake.FlowWorks] volume model " + volumeModel + " -> " + RM_Volume.CurrentModel
					+ ": " + rescaled + " limited pond(s) rescaled; canals unchanged; tanks keep every stored litre.");
				volumeModel = RM_Volume.CurrentModel;
			}
			RebuildBedGrid();
			ReportLostPaletteFluids();
			RepairLoadedGrids();
			SyncFluidIdentity();
			MigrateLevelModel();
			if (pondBudgetModel < 1)
			{
				int rescaled = stock.MigrateBudgetMultiplier(this);
				Log.Message("[RimMandrake.FlowWorks] pond budget model 0 -> 1 (the slider is gone): " + rescaled
					+ " limited pond(s) re-sized from their floor, each keeping its fill fraction.");
				pondBudgetModel = 1;
			}
			if (depthViewModel < 1)
			{
				int relaid = 0;
				foreach (IntVec3 c in excavatedCells)
				{
					int i = map.cellIndices.CellToIndex(c);
					if (WetDug(i))
					{
						ApplyFillTerrain(c, FluidAt(c) ?? ActiveFluid);
						relaid++;
					}
				}
				Log.Message("[RimMandrake.FlowWorks] depth view model 0 -> 1: " + relaid
					+ " wet dug square(s) re-pictured by their metres of water; no water moved.");
				depthViewModel = 1;
			}
			MigrateFillLayer();
			// LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP (R10): every lake gets its floor before the first tick (a new map), or once on
			// the first load of an older save; a lake already formed keeps its recorded floor. Books only: no terrain changes.
			if (!lakeFloorsFormed)
			{
				int formed = stock.FormAllBodies(map, this);
				lakeFloorsFormed = true;
				if (formed > 0)
				{
					Log.Message("[RimMandrake.FlowWorks] lake floors: " + formed + " natural body(ies) formed at map load, each limited"
						+ " lake's floor recorded (" + RM_Volume.FormatMetres(DeepestRecordedBed()) + " deepest); no terrain changed.");
				}
			}
			// SUPERDEEP_HOLDER_RETIRE_1: a save written while the holder Thing
			// existed carries RM_SuperdeepPit Things; the def is gone, so the
			// loader drops them ("Could not load reference") — nothing to shed.
			// FLOWWORKS_PITFALL_FIX_HISTORY_NOT_SAVED: the detector is NOT reset here. FinalizeInit runs after a load too, and
			// a reset wiped the lastCell/walkedInto the save had just restored, so an arrival made before the save was never
			// judged (live, lines_proof PITFALL_SAVED_ARRIVAL_FALLS 2026-10-22). A new map's state is new and empty anyway.
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
			// P14: a wet DUG square now carries its water on the base layer too (the one ladder); it is ours, never a
			// natural source, lake square or pond footprint. Before P14 a dug square's base was always a dry channel, so
			// this guard keeps every caller's answer exactly what it was.
			if (c.InBounds(map) && depthGrid[map.cellIndices.CellToIndex(c)] != 0)
			{
				return false;
			}
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
			int i = map.cellIndices.CellToIndex(c);
			byte d = depthGrid[i];
			if (d != 0)
			{
				return d;
			}
			if (IsNaturalLiquid(c))
			{
				return RM_ExcavationDepth.Superdeep;
			}
			// POND_BED step 2 (Option B): a dry pond square reads its bed depth, with FillAt 0 (an empty bed). Every writer
			// that pours into a cell guards on IsExcavated first, so a bed never takes canal water: the return leg
			// (TryReturnLevels) owns water arriving there.
			return (byte)RM_Volume.HollowDepth(0, bedGrid[i], RimMandrakeFlowWorksSettings.pondBedHollowEnabled);
		}

		/// <summary>POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK: the bed depth (= budget in levels) of a natural body square,
		/// read from the water it holds now, or from the recorded water terrain when it has receded or been dug.
		/// Deep water is RM_Volume.LevelsPerSquare, shallow water RM_Volume.ShallowBedLevels.</summary>
		public int BedLevelsAt(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return 0;
			}
			byte recorded = bedRecord[map.cellIndices.CellToIndex(c)];
			if (recorded != 0)
			{
				return recorded;   // POND_ELEVATION_BUILD_LAKES_RUN_DEEP: a lake's deep middle, recorded when it formed
			}
			// POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD: a drawn-down square shows a STAGE terrain (shallow water over a deep bed);
			// its bed is the water it was recorded with before the first stage write, never the stage it shows now.
			TerrainDef first = OriginalTerrainAt(c);
			if (first != null && first.IsWater)
			{
				return RM_Volume.BedLevels(first.passability == Traversability.Impassable, first.pathCost);
			}
			TerrainDef t = map.terrainGrid.BaseTerrainAt(c);
			if (t == null || !t.IsWater)
			{
				TerrainDef rec = OriginalTerrainAt(c);
				if (rec != null && rec.IsWater)
				{
					t = rec;
				}
			}
			if (t == null || !t.IsWater)
			{
				// A footprint cell with no water record (a pre-record save): the deep notch, the old read-through.
				return RM_Volume.LevelsPerSquare;
			}
			return RM_Volume.BedLevels(t.passability == Traversability.Impassable, t.pathCost);
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

		// ── WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: water in decilitres ──────────────────────────────

		/// <summary>Decilitres of liquid in a dug cell: F·U + part (0 for an undug cell).</summary>
		private long WaterDl(int i)
		{
			return depthGrid[i] == 0 ? 0 : fillGrid[i] * (long)RM_LevelSolve.U + partGrid[i];
		}

		/// <summary>True when a dug cell holds any liquid at all (a part-notch counts: 4.5 cm of water is water).</summary>
		private bool WetDug(int i)
		{
			return depthGrid[i] != 0 && (fillGrid[i] > 0 || partGrid[i] > 0);
		}

		/// <summary>Whole notches of room left below the brim, in decilitres' truth: a part-filled top notch has no room for a
		/// whole level (every whole-level writer asks this, so none can push a cell past its brim).</summary>
		private int RoomNotches(int i)
		{
			long room = depthGrid[i] * (long)RM_LevelSolve.U - WaterDl(i);
			return room <= 0 ? 0 : (int)(room / RM_LevelSolve.U);
		}

		/// <summary>The water a dug cell holds, in decilitres (the readout's truth: DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE reads
		/// this, the hole's depth from <see cref="ExcavatedDepthAt"/>). 0 for an undug cell.</summary>
		public long WaterDlAt(IntVec3 c)
		{
			return c.InBounds(map) ? WaterDl(map.cellIndices.CellToIndex(c)) : 0;
		}

		/// <summary>The water standing in a dug cell, in metres (true depth, not a band).</summary>
		public float WaterMetresAt(IntVec3 c)
		{
			return (float)RM_LevelSolve.Metres(WaterDlAt(c));
		}

		/// <summary>The water surface of a dug cell in metres relative to ground (0 = brim, negative below); NaN when dry.</summary>
		public float WaterSurfaceMetresAt(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return float.NaN;
			}
			int i = map.cellIndices.CellToIndex(c);
			if (!WetDug(i))
			{
				return float.NaN;
			}
			return (float)RM_LevelSolve.Metres(WaterDl(i) - depthGrid[i] * (long)RM_LevelSolve.U);
		}

		/// <summary>LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD / DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE: the decilitres on an UNDUG natural
		/// liquid square, from the solver's numbers: its pond's one surface over this square's floor (RM_LiquidStock.SquareWaterDl).
		/// Read-only: a body not yet formed is never formed here (<paramref name="body"/> null; the square reads as its full
		/// floor). <paramref name="floor"/> is the square's natural floor in notches. 0 when the square is not natural liquid.</summary>
		public double NaturalWaterDlAt(IntVec3 c, out RM_LiquidBody body, out int floor)
		{
			body = null;
			floor = 0;
			if (!IsSourceCell(c))
			{
				return 0.0;
			}
			floor = BedLevelsAt(c);
			body = stock.IndexedBodyAt(map, c);
			return stock.SquareWaterDl(map, body, c, floor, this);
		}

		/// <summary>R13: is this natural square part of a body that never runs dry? The formed body's sticky classification
		/// (ruling 16) when it has one; a square not yet in a body reads limitless when it is vanilla's own limitless water,
		/// a river or the ocean (R10: they stay vanilla and limitless).</summary>
		public bool IsLimitlessWaterAt(IntVec3 c, RM_LiquidBody body)
		{
			if (body != null)
			{
				return body.limitless;
			}
			TerrainDef t = c.InBounds(map) ? map.terrainGrid.BaseTerrainAt(c) : null;
			return t != null && t.IsWater && (t.IsRiver || t.defName.IndexOf("Ocean", System.StringComparison.Ordinal) >= 0);
		}

		/// <summary>DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE (owner R4; wording V8): the two-figure readout for a square, from the
		/// solver's numbers, or null when the square is neither dug nor natural liquid. A dug square: "Hole 7 m (ledge 4 m) ·
		/// Water 2.37 m (4,740 L)" (water = its own decilitres; a dry dug square reads Water 0.00 m). A limited pond square: the
		/// same, the hole being its natural floor and the water the pond's surface over it. A limitless square (sea, edge
		/// river): "Endless" (R13; wording 2026-10-20), never a litre count.</summary>
		public string DepthReadoutAt(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return null;
			}
			int i = map.cellIndices.CellToIndex(c);
			int hole;
			double water;
			if (depthGrid[i] != 0)
			{
				hole = depthGrid[i];
				water = WaterDl(i);
			}
			else
			{
				water = NaturalWaterDlAt(c, out RM_LiquidBody body, out hole);
				if (hole <= 0)
				{
					int dryBed = HollowDepthAt(c);
					if (dryBed <= 0)
					{
						return null;
					}
					hole = dryBed;   // a dried pond bed is a hole with no water in it
					water = 0.0;
				}
				else if (IsLimitlessWaterAt(c, body))
				{
					return RM_Volume.LimitlessReadout(hole);
				}
			}
			return RM_Volume.Readout(hole, LedgeAt(c, hole), water);
		}

		/// <summary>The ledge for the readout: the shallowest floor among the four squares around <paramref name="c"/> that is
		/// still below ground and above this hole's floor (the step a climber reaches first); 0 when the square opens straight
		/// onto the ground or has no shallower neighbour.</summary>
		private int LedgeAt(IntVec3 c, int hole)
		{
			int best = 0;
			for (int d = 0; d < 4; d++)
			{
				IntVec3 n = c + GenAdj.CardinalDirections[d];
				if (!n.InBounds(map))
				{
					continue;
				}
				int f = HollowDepthAt(n);
				if (f <= 0)
				{
					return 0;   // ground next door: no ledge between this hole and the surface
				}
				if (f < hole && (best == 0 || f < best))
				{
					best = f;
				}
			}
			return best;
		}

		/// <summary>Is the exact-level kernel running on this map now (the setting)? Readers that pick a look use it.</summary>
		public static bool LevelExact => RimMandrakeFlowWorksSettings.levelExactEnabled;

		// ── digging ───────────────────────────────────────────────────────

		/// <summary>Deepen a cell by one notch (0.5 m), to the designation cap at most (the deepest anyone may dig: debug
		/// actions and bridge digs). A pawn's cut goes through <see cref="DeepenWithin"/> (a separate name: bridge tools reflect GetMethod("Deepen"), which an overload makes ambiguous) with its own cap.</summary>
		public byte Deepen(IntVec3 c)
		{
			return DeepenWithin(c, RM_DigLabor.DesignationCap);
		}

		/// <summary>Deepen a cell by one notch (0.5 m), to <paramref name="cap"/> at most (DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL:
		/// the digger's cap, colonist 2 m / machine 20 m shipped). Returns the new D. LAW 1: this is the only thing that ever
		/// sets D, and it only ever goes down. A cell already deeper than a lowered cap is left as it is (never shallowed).</summary>
		public byte DeepenWithin(IntVec3 c, int cap)
		{
			if (!c.InBounds(map))
			{
				return RM_ExcavationDepth.Surface;
			}
			int i = map.cellIndices.CellToIndex(c);
			byte d = depthGrid[i];
			if (!RM_DigDepthMath.MayDeepen(d, cap))
			{
				return d;
			}
			byte before = d;
			// PHASE 4: remember what was here BEFORE the first cut, so a fill-in
			// can hand the exact terrain back instead of generic soil. Recorded
			// on the transition out of surface only — deepening an existing
			// channel must not overwrite the record with RM_Channel_Empty.
			byte next = (byte)(d + 1);
			if (d == RM_ExcavationDepth.Surface)
			{
				// POND_BED (owner by card 2026-10-14: "Dig deeper from the bed"): a dry bed square's first cut starts at the
				// bed's depth and goes one deeper; a bed already as deep as digging goes is left alone.
				int first = RM_Volume.FirstCutDepth(IsNaturalBed(c) ? bedGrid[i] : 0, RimMandrakeFlowWorksSettings.pondBedHollowEnabled,
					cap, RimMandrakeFlowWorksSettings.digToDepthEnabled);
				if (first < 0)
				{
					return d;
				}
				next = (byte)first;
				RecordOriginalTerrain(c);
				DetachIfDryBed(c, i);
			}
			d = next;
			depthGrid[i] = d;
			excavatedCells.Add(c);
			BumpClimbGeneration();
			// P14: ONE base write picks the square's picture: its dry floor by depth, or its water's ladder rung when wet
			// (a wet cell cut deeper is redrawn now rather than at the next pulse, forever with the depth engine off).
			ApplyFillTerrain(c, FluidAt(c) ?? ActiveFluid);
			// PHASE 5, ruling 26. The cut that CROSSES 2 m makes the cell a pit (SUPERDEEP_HOLDER_RETIRE_1: the trap is the grid
			// byte itself, RM_SuperdeepTrap; no Thing is created by digging). PIT_DEPTH_WIDEN: only the crossing counts; a pit
			// cut deeper is still one pit (the count used to rise on every cut past 2 m).
			if (d >= RM_ExcavationDepth.Superdeep && before < RM_ExcavationDepth.Superdeep)
			{
				superdeepCellCount++;
				// SUPERDEEP_PRISON_ROOM_1: the cell just crossed the pit wall; its rooms re-form.
				RM_PitRooms.NotifyPitnessChanged(map, c);
			}
			RM_PitRooms.NotifyDepthCrossed(map, c, before, d);
			// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 2 (P4): the cut has committed; the lines on this square break, once.
			Machinery.RM_LineDigBreak.OnDigCommitted(map, c, before, d);
			return d;
		}

		/// <summary>The destroyed-liquid exit, in grid LEVELS. Callers: ReportOverflow (the fill-in remainder the sheet
		/// refused), ReportLiquidLost (hose leftovers, released floods) and DetachIfDryBed (a detached bed's excess stock).
		/// Disclosed, never silent.</summary>
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
					"destroyed. Map total now " +
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
		/// hold (RM_LevelPour.KeptOnFillIn, in decilitres). A trench holding one level
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
			// POND_BED: a cut into a dry bed started at the bed's depth (Deepen), so filling it back in ends at the bed, not at
			// ground level: one fill past the bed's floor returns the square to its pond, never shallower than it was then
			// deeper again. Everything the cell held is displaced, as at the surface.
			int bedFloor = BedFloorOfCut(c, i);
			bool backToBed = bedFloor > 0 && newD <= bedFloor;
			if (backToBed)
			{
				newD = RM_ExcavationDepth.Surface;
			}
			// LIQUID_BODY_FLUID_IDENTITY_1 step 2b: the displaced liquid keeps the fluid this cell held.
			FluidDef cellFluid = FluidAt(c) ?? ActiveFluid;
			// The kept/displaced split lives in RM_LevelPour.KeptOnFillIn so the selftest covers the
			// production arithmetic rather than a copy of it.
			// CANAL_FILLIN_FIX_SHEET_WATER_DESTROYED: displacement is in DECILITRES. What no longer fits under the raised brim
			// (everything, filled to the surface or back to a pond bed) is displaced; a sheet under the new brim just sits higher.
			// A 4.5 cm sheet filled in used to be "destroyed" for want of a whole level to travel as; now it travels.
			long water = System.Math.Min(WaterDl(i), d * (long)RM_LevelSolve.U);
			long kept = RM_LevelPour.KeptOnFillIn(water, newD, newD == RM_ExcavationDepth.Surface || backToBed);
			long displacedDl = water - kept;
			depthGrid[i] = newD;
			fillGrid[i] = (byte)(kept / RM_LevelSolve.U);
			partGrid[i] = (ushort)(kept % RM_LevelSolve.U);
			BumpClimbGeneration();
			// PHASE 5. A cell raised out of SUPERDEEP stops being a trap: the
			// grid byte drops and the trap rule stops applying on the next read.
			// Nobody is in a container, so nobody needs dropping out. PIT_DEPTH_WIDEN: only the fill that crosses back above
			// 2 m (a 7 m pit filled to 6.5 m is still a pit).
			if (d >= RM_ExcavationDepth.Superdeep && newD < RM_ExcavationDepth.Superdeep)
			{
				superdeepCellCount--;
				RM_PitRooms.NotifyPitnessChanged(map, c);
			}
			RM_PitRooms.NotifyDepthCrossed(map, c, d, newD);
			if (newD == RM_ExcavationDepth.Surface)
			{
				excavatedCells.Remove(c);
				fillGrid[i] = 0;
				partGrid[i] = 0;
				// The water picture must come off BEFORE the base terrain is
				// restored, or a brimming cell hands back its floor and keeps
				// standing water on top of it (P14: the picture is on the base layer; a pre-P14 temp fill too).
				ClearFillTerrain(c, d);
				if (!ReattachIfDetachedBed(c, i) && !ReturnUndetachedBedCut(c, i))
				{
					RestoreOriginalTerrain(c);
				}
				// After ClearFillTerrain, which reads FluidAt. SyncFluidIdentity walks excavatedCells only, so a key
				// left here would pin a palette entry and answer a fluid for an undug cell.
				if (fluidGrid != null)
				{
					fluidGrid[i] = 0;
				}
			}
			else
			{
				ApplyFillTerrain(c, cellFluid);   // P14: dry floor by the new depth, or the water's rung (one base write)
			}
			if (displacedDl > 0)
			{
				Displace(c, displacedDl, cellFluid);
			}
			return newD;
		}

		/// <summary>
		/// The displacement walk. Offer the liquid to the connected body,
		/// NEAREST FIRST — remaining channel cells below their brim, THEN the
		/// natural body up to its capacity — and spill what finds no room as sheet
		/// water (CANAL_OVERFLOW stage 1); only what the sheet refuses is destroyed.
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
		/// 🔑 Whatever the sheet refuses is a disclosed exception to
		/// conservation of mass, which is why every exit
		/// from this method routes through <see cref="ReportOverflow"/> and is
		/// announced rather than quietly dropped. Everything else is a
		/// transfer.
		///
		/// <paramref name="dl"/> is in decilitres; phase 2 credits it with CreditDl (exact levels) or
		/// <see cref="RM_LiquidStock.CreditLevels"/> in whole levels (exact off).
		/// </summary>
		private void Displace(IntVec3 from, long dl, FluidDef fluid)
		{
			if (!RimMandrakeFlowWorksSettings.fillInDisplacementEnabled)
			{
				// All-off degradation: no displacement at all, every level is
				// overflow. Still disclosed — the exception does not become
				// silent just because the mechanic is switched off, which is why
				// this takes the same reporting exit as a real overflow rather
				// than only writing a DevMode log.
				// CANAL_OVERFLOW stage 1 (D1): homeless water spills as a sheet first; only what it refuses is destroyed.
				dl -= Sheet.RM_MapComponent_Sheet.SpillHomeless(map, from, dl, fluid);
				ReportOverflow(from, dl);
				return;
			}
			// ── phase 1: the channel, below the brim, nearest first ────────
			// CANAL_FILLIN_FIX_SHEET_WATER_DESTROYED: in DECILITRES (RM_LevelPour.Spread, the walk the pour shares and the
			// oracle differential checks), so a sheet's part-notch finds room a whole level never would.
			// FILLIN_DISPLACE_FIX_DRY_POND_SNUB (C5-F9): the walk is bounded by the map, not by the pulse's partition cap: a
			// network past 6000 squares used to stop the walk and destroy liquid its far channel had room for.
			// FILLIN_DISPLACE_FIX_DRY_POND_SNUB (C5-F8): a dry bed square of a pond is a destination too (the return leg's own
			// rule), so a fully drained pond takes back the water it has room for instead of it being lost.
			// A shut sluice seals its cell for displacement exactly as for the pulse (the kernel's sealedCell): liquid is
			// neither credited into it nor conducted past it (GPT FlowWorks review #7). Pond squares are destinations, never
			// conductors (phase 2).
			int start = map.cellIndices.CellToIndex(from);
			bool keyOk = TryPaletteKey(fluid, out byte claimKey);
			bool Enter(int i)
			{
				IntVec3 n = map.cellIndices.IndexToCell(i);
				return (depthGrid[i] != 0 || IsSourceCell(n) || IsDisplaceBed(n)) && !RM_FlowDoorRules.SealsLiquid(map.edificeGrid[i]);
			}
			bool Pond(int i)
			{
				IntVec3 n = map.cellIndices.IndexToCell(i);
				return depthGrid[i] == 0 && (IsSourceCell(n) || IsDisplaceBed(n));
			}
			long Room(int i)
			{
				// Fluids never mix (Q3): only a dry cell (which it then claims) or a same-fluid cell takes the water; the walk
				// still conducts through a foreign cell. P7: a dry cell that cannot record this fluid takes nothing.
				if (depthGrid[i] == 0 || !RM_StockMath.FluidsCompatible(WetDug(i), FluidAt(map.cellIndices.IndexToCell(i)), fluid)
					|| (!WetDug(i) && !keyOk))
				{
					return 0;
				}
				long r = depthGrid[i] * (long)RM_LevelSolve.U - WaterDl(i);
				return r > 0 ? r : 0;
			}
			var credits = new List<KeyValuePair<int, long>>();
			var sources = new List<int>();
			long remaining = dl - RM_LevelPour.Spread(start, dl, false, NeighbourIndex, Enter, Pond, Room, map.cellIndices.NumGridCells,
				credits, sources);
			foreach (KeyValuePair<int, long> cr in credits)
			{
				int ci = cr.Key;
				if (!WetDug(ci))
				{
					fluidGrid[ci] = claimKey;
				}
				long w = WaterDl(ci) + cr.Value;
				fillGrid[ci] = (byte)(w / RM_LevelSolve.U);
				partGrid[ci] = (ushort)(w % RM_LevelSolve.U);
			}

			// ── phase 2: the natural body, nearest source cell first ───────
			// The body is the last resort and the reason a fill-in is
			// REVERSIBLE: liquid you spent digging comes back to the pond you
			// took it from. Exact-level water: in decilitres (a part-notch goes home too); off: whole levels, as before.
			float unitPerLevel = fluid != null ? fluid.volumePerTile : 1f;
			for (int i = 0; i < sources.Count && remaining > 0; i++)
			{
				IntVec3 sc = map.cellIndices.IndexToCell(sources[i]);
				FluidDef bodyFluid = stock.BodyAt(map, sc, this)?.fluid;
				if (bodyFluid != null && fluid != null && bodyFluid != fluid)
				{
					continue;
				}
				if (LevelExact)
				{
					remaining -= stock.CreditDl(map, sc, remaining, this);
				}
				else
				{
					remaining -= stock.CreditLevels(map, sc, (int)(remaining / RM_LevelSolve.U), unitPerLevel, this) * (long)RM_LevelSolve.U;
				}
			}

			foreach (KeyValuePair<int, long> cr in credits)
			{
				ApplyFillTerrain(map.cellIndices.IndexToCell(cr.Key), fluid);
			}
			// CANAL_OVERFLOW stage 1 (D1, supersedes the 2026-09-16 destroy rule): the homeless remainder spills over the lip
			// as sheet water; only what the sheet refuses (switch off, caps, another liquid) is still destroyed and disclosed.
			remaining -= Sheet.RM_MapComponent_Sheet.SpillHomeless(map, from, remaining, fluid);
			ReportOverflow(from, remaining);
		}

		/// <summary>FILLIN_DISPLACE_FIX_DRY_POND_SNUB (C5-F8): a dry bed square displaced liquid may go home to — only while the
		/// return leg is on (its Mod Setting; off, only wet pond squares take displaced liquid, as before).</summary>
		private bool IsDisplaceBed(IntVec3 c)
		{
			return RimMandrakeFlowWorksSettings.pondReturnLegEnabled && IsNaturalBed(c);
		}

		/// <summary>Disclose destroyed liquid. §5 is explicit that this may not be
		/// silent — <i>"an overflow report so destroyed liquid is disclosed rather
		/// than silent — a message or an inspect line, since silent loss in a
		/// conservation-of-mass system reads as a bug."</i>
		///
		/// Zero destroyed says nothing, which is not silence about a loss: it is
		/// the case where there was no loss.</summary>
		private void ReportOverflow(IntVec3 at, long dl)
		{
			if (dl <= 0)
			{
				return;
			}
			NotifyOverflowDestroyed(dl / (float)RM_LevelSolve.U);
			Messages.Message(
				"Filling in displaced more liquid than the channel could hold — "
				+ RM_Volume.FormatLitres(dl / (double)RM_Volume.UnitsPerLitre) + " overflowed and were lost. "
				+ "Lost this way on this map so far: " + RM_Volume.FormatLitres(overflowDestroyedTotal * (double)RM_Volume.LitresPerLevel) + ".",
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
		public RM_RestoreResult RestoreOriginalTerrain(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return RM_RestoreResult.NoRecord;
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
				return RM_RestoreResult.NoRecord;
			}
			if (map.terrainGrid.BaseTerrainAt(c) != original)
			{
				map.terrainGrid.SetTerrain(c, original);
			}
			// GPT #11: the record goes only once the write is seen to have taken.
			if (map.terrainGrid.BaseTerrainAt(c) != original)
			{
				return RM_RestoreResult.WriteFailed;
			}
			originalTerrain.Remove(i);
			SetBed(i, 0);
			return RM_RestoreResult.Restored;
		}

		// ── POND_RETURN_LEG_BUILD_WATER_GOES_HOME: dug beds and the return leg ──

		/// <summary>Owner ruling 6: the first cut into a DRY bed square of a pond takes it out of that pond (G5 fix).</summary>
		private void DetachIfDryBed(IntVec3 c, int i)
		{
			if (IsNaturalLiquid(c))
			{
				return;
			}
			RM_LiquidBody body = stock.IndexedBodyAt(map, c);
			if (body == null || !body.receded.Contains(c))
			{
				return;
			}
			// A dug square is never bed, whether or not it leaves its pond (the load rebuild skips dug squares too, so the
			// session and a reload agree). With the setting off it stays a receded square of its pond: FillIn returns it dry.
			SetBed(i, 0);
			if (!RimMandrakeFlowWorksSettings.dugBedLeavesPondEnabled)
			{
				return;
			}
			float excess = stock.DetachBedCell(map, body, c, this);
			detachedBedCells[i] = body.id;
			SetBed(i, 0);
			if (excess > 0f)
			{
				FluidDef f = body.fluid ?? ActiveFluid;
				NotifyOverflowDestroyed(excess / (f != null && f.volumePerTile > 0f ? f.volumePerTile : 1f));
			}
		}

		/// <summary>POND_BED: the bed depth a dug square goes back to when filled in — its detached pond's bed depth while
		/// hollows are on, else 0 (filled to ground level as before).</summary>
		private int BedFloorOfCut(IntVec3 c, int i)
		{
			if (!RimMandrakeFlowWorksSettings.pondBedHollowEnabled || !originalTerrain.ContainsKey(i)
				|| (!detachedBedCells.ContainsKey(i) && !IsUndetachedBedCut(c)))
			{
				return 0;
			}
			return BedLevelsAt(c);
		}

		/// <summary>A cut into a dry bed square made while "Digging a dried bed takes the square out of its pond" was off:
		/// still in its pond's footprint (DetachIfDryBed left it there), so filling it in returns it dry, not wet. Water
		/// cannot be designated for digging, so a dug footprint square was dry bed when cut. Not "on the receded list": a
		/// refill drops a dug square from that list (RM_LiquidStock.Refill, GPT #3) while it stays in the footprint.</summary>
		private bool IsUndetachedBedCut(IntVec3 c)
		{
			return stock.IndexedBodyAt(map, c) != null;
		}

		/// <summary>The setting-off half of ruling 6: an undetached bed cut filled back in to the surface is dry bed of its pond
		/// again (terrain and bed grid), its water record kept for the pond's Restore. Writing the recorded water here would
		/// wet a square the pond never paid for (review 2026-10-14). False = not such a cut.</summary>
		private bool ReturnUndetachedBedCut(IntVec3 c, int i)
		{
			if (!originalTerrain.ContainsKey(i) || !IsUndetachedBedCut(c))
			{
				return false;
			}
			RM_LiquidBody body = stock.IndexedBodyAt(map, c);
			TerrainDef bed = RimMandrakeFlowWorksSettings.pondBedHollowEnabled ? LakebedTerrainFor(c) : (body.fluid ?? ActiveFluid)?.recededTerrain;
			if (bed == null)
			{
				return false;
			}
			map.terrainGrid.SetTerrain(c, bed);
			if (!body.receded.Contains(c))
			{
				body.receded.Add(c);   // back on the refill stack, on top: the pond re-wets it first, paid from its stock
			}
			SetBed(i, BedLevelsAt(c));
			return true;
		}

		/// <summary>Owner ruling 6's other half: a detached bed square filled back in to the surface goes back to its pond
		/// as DRY bed (its recorded water terrain stays recorded for the pond's Restore). False = not a detached bed.</summary>
		private bool ReattachIfDetachedBed(IntVec3 c, int i)
		{
			if (!detachedBedCells.TryGetValue(i, out int id))
			{
				return false;
			}
			detachedBedCells.Remove(i);
			RM_LiquidBody body = stock.BodyById(id);
			FluidDef f = body?.fluid ?? ActiveFluid;
			TerrainDef bed = f?.recededTerrain;
			if (body == null || bed == null || !originalTerrain.ContainsKey(i))
			{
				return false;
			}
			if (RimMandrakeFlowWorksSettings.pondBedHollowEnabled)
			{
				bed = LakebedTerrainFor(c);   // POND_BED step 2: it comes back as the hollow it was
			}
			map.terrainGrid.SetTerrain(c, bed);
			stock.ReattachBedCell(map, body, c, this);
			SetBed(i, BedLevelsAt(c));
			return true;
		}

		/// <summary>The return leg's read-only check (G1, GPT #5/#6): would the natural body owning <paramref name="c"/> (a
		/// wet square or a dry bed square, never a dug one) take <paramref name="levels"/> whole levels of
		/// <paramref name="fluid"/> right now? A foreign fluid is refused before anything changes; a limited body takes
		/// only whole levels up to its capacity; a limitless one takes any. Never forms a body.</summary>
		public bool CanReturnLevels(IntVec3 c, FluidDef fluid, int levels)
		{
			if (!RimMandrakeFlowWorksSettings.pondReturnLegEnabled || levels <= 0 || fluid == null || !c.InBounds(map) || IsExcavated(c))
			{
				return false;
			}
			RM_LiquidBody body = stock.IndexedBodyAt(map, c);
			if (body == null || (body.fluid ?? ActiveFluid) != fluid)
			{
				return false;
			}
			return RM_StockMath.CreditableLevels(body.limitless, body.stock, body.capacity, levels, fluid.volumePerTile) == levels;
		}

		/// <summary>The return leg: credit <paramref name="levels"/> whole levels to the body at <paramref name="c"/>, all or
		/// nothing (through <see cref="RM_LiquidStock.CreditLevels"/>, the one place stock rises). Refill and Restore re-wet
		/// the pond last-in-first-out on its pulse.</summary>
		public bool TryReturnLevels(IntVec3 c, FluidDef fluid, int levels)
		{
			if (!CanReturnLevels(c, fluid, levels))
			{
				return false;
			}
			RM_LiquidBody body = stock.IndexedBodyAt(map, c);
			int took = stock.CreditLevels(map, c, levels, fluid.volumePerTile, this);
			if (took == levels && body.limitless)
			{
				limitlessReturnedTotal += levels;
			}
			return took == levels;
		}

		/// <summary>L0 ledger probe (G10, GPT #21): every place this map keeps water, in tank units (a level =
		/// RM_Volume.UnitsPerLevel; a body fill-unit = UnitsPerLevel ÷ volumePerTile). Limitless bodies are a sentinel and
		/// are not summed; the exits (destroyed, sunk, burned, spilled, returned to limitless) are listed beside the total
		/// so a row compares before/after with exits added back.</summary>
		public string LedgerReport()
		{
			double bodiesU = 0, canalsU = 0, tanksU = 0, hoseU = 0;
			int limitless = 0;
			foreach (RM_LiquidBody b in stock.Bodies)
			{
				if (b.limitless) { limitless++; continue; }
				FluidDef f = b.fluid ?? ActiveFluid;
				float vpt = f != null && f.volumePerTile > 0f ? f.volumePerTile : 1f;
				// review day 2: the decilitre truth, never the float view (a big lake's float stock is off by tens of dL)
				bodiesU += b.stockDl * (RM_Volume.UnitsPerLevel / (double)RM_LevelSolve.U) / vpt;
			}
			foreach (IntVec3 c in excavatedCells)
			{
				// review day 2: whole notches AND the part-notch (FillAt alone dropped every sheet's decilitres, so water moving
				// between a whole notch and a part read as a leak or a gain)
				canalsU += WaterDlAt(c) * (RM_Volume.UnitsPerLevel / (double)RM_LevelSolve.U);
			}
			foreach (Thing t in map.listerThings.AllThings)
			{
				if (t is LiquidTypes.Building_LiquidTank tank)
				{
					tanksU += tank.storedUnits;
				}
				Hose.CompHoseReel r = (t as ThingWithComps)?.GetComp<Hose.CompHoseReel>();
				if (r != null)
				{
					hoseU += r.heldUnits;
				}
			}
			double total = bodiesU + canalsU + tanksU + hoseU;
			return "L0 ledger (tank units): total=" + total.ToString("F3")
				+ " bodies(limited)=" + bodiesU.ToString("F3") + " canals=" + canalsU.ToString("F0")
				+ " tanks=" + tanksU.ToString("F0") + " hoses=" + hoseU.ToString("F0")
				+ " | exits: destroyed=" + (overflowDestroyedTotal * RM_Volume.UnitsPerLevel).ToString("F1")
				+ " sunk=" + (sinkTransferredTotal * RM_Volume.UnitsPerLevel).ToString("F1")
				+ " burned=" + (burnedLevelsTotal * RM_Volume.UnitsPerLevel).ToString("F1")
				+ " spilled(session)=" + Machinery.RM_LiquidSpill.SpilledUnits
				+ " toLimitless=" + (limitlessReturnedTotal * RM_Volume.UnitsPerLevel).ToString("F1")
				+ " | inputs: flowSources=" + (mapControlPouredTotal * RM_Volume.UnitsPerLevel).ToString("F1")
				+ " fromLimitless(session, exact)=" + limitlessPaidDl * (RM_Volume.UnitsPerLevel / RM_LevelSolve.U)   // review day 2: was never read
				+ " exits: flowSinks=" + (mapControlDrainedTotal * RM_Volume.UnitsPerLevel).ToString("F1")
				+ " | limitless bodies=" + limitless + " (not summed)";
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
			// POND_BED step 2 (owner look (b)): the square is laid as cracked lakebed at its bed depth, read from the water
			// just recorded; with hollows off it is the fluid's flat recededTerrain (mud), as before.
			if (RimMandrakeFlowWorksSettings.pondBedHollowEnabled)
			{
				dry = LakebedTerrainFor(c);
			}
			map.terrainGrid.SetTerrain(c, dry);
			SetBed(map.cellIndices.CellToIndex(c), BedLevelsAt(c));
			return true;
		}

		// ── POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD: stage writes (RM_LiquidStock.StagePond decides, these write) ──

		/// <summary>The terrain a pond square shows at <paramref name="stage"/>, or null when this map cannot show it (then
		/// the caller leaves the square as it is: a missing look beats a wrong one).</summary>
		public TerrainDef PondStageTerrain(IntVec3 c, RM_PondDepthMath.Stage stage, FluidDef fluid)
		{
			TerrainDef first = OriginalTerrainAt(c);
			TerrainDef now = map.terrainGrid.BaseTerrainAt(c);
			TerrainDef original = first != null && first.IsWater ? first : (now != null && now.IsWater ? now : null);
			switch (stage)
			{
				case RM_PondDepthMath.Stage.Original:
					return original;
				// P14: the wet stages are the ONE ladder's rungs (RM_WaterLadder), the same terrains a wet dug square shows.
				case RM_PondDepthMath.Stage.Deep:
					return original != null && original.passability == Traversability.Impassable
						? original : RM_WaterLadderDefs.Freshwater(RM_WaterLadder.Rung.Deep);
				case RM_PondDepthMath.Stage.ChestDeep:
				case RM_PondDepthMath.Stage.Shallow:
				case RM_PondDepthMath.Stage.Thin:
				case RM_PondDepthMath.Stage.VeryShallow:
					return RM_WaterLadderDefs.Freshwater(RM_WaterLadder.RungOfPondStage(stage));
				case RM_PondDepthMath.Stage.Mud:
					return fluid?.recededTerrain;
				default:
					return RimMandrakeFlowWorksSettings.pondBedHollowEnabled ? LakebedTerrainFor(c) : fluid?.recededTerrain;
			}
		}

		/// <summary>Lay a WET stage on a pond square: records the original first (idempotent, as DryNaturalCell), writes, and
		/// clears the dry-bed record and the mud time. The original itself goes through RestoreOriginalTerrain, which drops
		/// the record. True when the square now shows <paramref name="t"/>.</summary>
		public bool StageNaturalCell(IntVec3 c, TerrainDef t)
		{
			if (t == null || !c.InBounds(map))
			{
				return false;
			}
			int i = map.cellIndices.CellToIndex(c);
			pondMudSince.Remove(i);
			if (OriginalTerrainAt(c) == t)
			{
				return RestoreOriginalTerrain(c) == RM_RestoreResult.Restored;
			}
			RecordOriginalTerrain(c);
			if (map.terrainGrid.BaseTerrainAt(c) != t)
			{
				map.terrainGrid.SetTerrain(c, t);
			}
			SetBed(i, 0);
			return map.terrainGrid.BaseTerrainAt(c) == t;
		}

		/// <summary>Expose a pond square as mud (the fluid's recededTerrain) and start its mud time. False when the fluid
		/// authors no receded terrain (nothing written, nothing recorded: DryNaturalCell's stance).</summary>
		public bool MudNaturalCell(IntVec3 c, FluidDef fluid, int now)
		{
			TerrainDef mud = fluid?.recededTerrain;
			if (mud == null || !c.InBounds(map))
			{
				return false;
			}
			RecordOriginalTerrain(c);
			map.terrainGrid.SetTerrain(c, mud);
			int i = map.cellIndices.CellToIndex(c);
			SetBed(i, BedLevelsAt(c));
			pondMudSince[i] = now;
			return true;
		}

		/// <summary>Is this pond square's mud past its time (or untimed: an old-model dry square)?</summary>
		public bool PondMudExpired(IntVec3 c, int now, int mudTicks)
		{
			return !pondMudSince.TryGetValue(map.cellIndices.CellToIndex(c), out int since) || now - since >= mudTicks;
		}

		public bool PondMudTimed(IntVec3 c)
		{
			return pondMudSince.ContainsKey(map.cellIndices.CellToIndex(c));
		}

		/// <summary>Crack expired mud to its lakebed (hollows on) and end its time.</summary>
		public void CrackPondMud(IntVec3 c, FluidDef fluid)
		{
			int i = map.cellIndices.CellToIndex(c);
			pondMudSince.Remove(i);
			TerrainDef bed = PondStageTerrain(c, RM_PondDepthMath.Stage.Lakebed, fluid);
			if (bed != null && map.terrainGrid.BaseTerrainAt(c) != bed)
			{
				map.terrainGrid.SetTerrain(c, bed);
			}
		}

		/// <summary>Drop every mud time (the toggle off: the old model has no mud stage).</summary>
		public void ClearPondMud()
		{
			pondMudSince.Clear();
		}

		/// <summary>Is this undug square natural liquid right now (base terrain IsWater)? Public read for RM_LiquidStock.</summary>
		public bool IsWaterNow(IntVec3 c)
		{
			return IsNaturalLiquid(c);
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
			if (!c.InBounds(map) || depthGrid[map.cellIndices.CellToIndex(c)] == 0)
			{
				return false;
			}
			// FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES: a map-edge setter (MapControls/RM_EdgeSetter) seals or drains an edge
			// on top of the automatic rule; with none placed, EdgeModes is null and the rule below is today's, unchanged.
			if (MapControls.RM_MapControls.EdgeModes(map) != null)
			{
				return MapControls.RM_MapControls.EdgeSinkAt(map, c, RimMandrakeFlowWorksSettings.edgeSinksEnabled);
			}
			return RimMandrakeFlowWorksSettings.edgeSinksEnabled && c.CloseToEdge(map, GenGrid.NoBuildEdgeWidth);
		}

		public float SinkTransferredTotal => sinkTransferredTotal;

		// ── the pulse ─────────────────────────────────────────────────────

		/// <summary>SUPERDEEP_HOLDER_RETIRE_1. The descent detector and the
		/// jumper set. Per-map state lives here so it scribes with the grid.</summary>
		private RM_SuperdeepTrapState superdeepTrap = new RM_SuperdeepTrapState();

		internal RM_SuperdeepTrapState SuperdeepTrap => superdeepTrap;

		/// <summary>FLOWWORKS_BUILD_PROGRAM_1 Phase 6: fire on the liquid (RM_LiquidFire).</summary>
		private RM_LiquidFire liquidFire = new RM_LiquidFire();

		/// <summary>FlowWorks GPT review 2026-10-22: redraws the water looks on a tint/band rung crossing (not saved: its first
		/// check after a load redraws every square that carries a look, once).</summary>
		private readonly RM_WaterLookWatcher lookWatcher = new RM_WaterLookWatcher();
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
			if (!TakeLevelCore(c, out FluidDef fluid))
			{
				return false;
			}
			burnedLevelsTotal += 1f;
			return true;
		}

		/// <summary>One level off an excavated cell, redrawn; the shared half of a burn and a pump take. Counts no exit:
		/// the L0 ledger's burned total is BurnOffLevel's alone (a pumped level is moved, not burned).</summary>
		private bool TakeLevelCore(IntVec3 c, out FluidDef fluid)
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
			fillGrid[i] -= 1;
			if (fluid != null)
			{
				ApplyFillTerrain(c, fluid);
			}
			if (!WetDug(i))
			{
				fluidGrid[i] = 0;
			}
			return true;
		}

		/// <summary>FLOWWORKS_BUILD_PROGRAM_1 Phase 8: a pump lifts one level out of an excavated cell. The level
		/// is MOVED (into a tank), not lost, so it sits outside the pulse ledger exactly like a burn does, but it is
		/// not an exit: it is not counted as burned.</summary>
		public bool TryTakeLevel(IntVec3 c, out FluidDef fluid)
		{
			return TakeLevelCore(c, out fluid);
		}

		/// <summary>LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD: up to <paramref name="maxDl"/> decilitres off a dug cell, the part-notch
		/// first and then whole notches, so a 4.5 cm sheet (900 dL, no whole notch) can be pumped or burned. Redrawn; the cell
		/// forgets its fluid once dry. Returns the dL taken (0: not dug, dry, or nothing asked). Counts no exit.</summary>
		private long TakeDlCore(IntVec3 c, long maxDl, out FluidDef fluid)
		{
			fluid = null;
			if (maxDl <= 0 || !IsExcavated(c))
			{
				return 0;
			}
			int i = map.cellIndices.CellToIndex(c);
			long w = WaterDl(i);
			if (w <= 0)
			{
				return 0;
			}
			long take = maxDl < w ? maxDl : w;
			long left = w - take;
			fluid = FluidAt(c) ?? ActiveFluid;
			fillGrid[i] = (byte)(left / RM_LevelSolve.U);
			partGrid[i] = (ushort)(left % RM_LevelSolve.U);
			if (fluid != null)
			{
				ApplyFillTerrain(c, fluid);
			}
			if (!WetDug(i))
			{
				fluidGrid[i] = 0;
			}
			return take;
		}

		/// <summary>A pump lifts up to <paramref name="maxDl"/> dL out of a dug cell (a thin sheet gives what it has). Moved, not
		/// burned: no exit is counted. With exact-level water off a cell holds whole notches only, so only whole notches are
		/// taken (the part grid stays empty).</summary>
		public long TryTakeDl(IntVec3 c, long maxDl, out FluidDef fluid)
		{
			if (!LevelExact)
			{
				maxDl -= maxDl % RM_LevelSolve.U;
			}
			return TakeDlCore(c, maxDl, out fluid);
		}

		/// <summary>Burning takes up to <paramref name="dl"/> decilitres off a dug cell (ruling 7's rate, applied in decilitres
		/// so a thin sheet burns away in a fraction of a day). The fire's disclosed exit; returns the dL burned.</summary>
		internal long BurnOffDl(IntVec3 c, long dl)
		{
			long took = TakeDlCore(c, dl, out _);
			if (took > 0)
			{
				burnedLevelsTotal += took / (float)RM_LevelSolve.U;
			}
			return took;
		}

		/// <summary>Liquid networks L6 (rev 2 §3.3): would <see cref="TryPourLevel"/> take a level of <paramref name="fluid"/> here?
		/// Read-only: excavated, room below the brim, the fluid allowed in, and no other fluid in the cell. Checked before a pump
		/// takes the source level of a world-to-world move.</summary>
		public bool CanPourLevel(IntVec3 c, FluidDef fluid)
		{
			if (fluid == null || !c.InBounds(map) || !IsExcavated(c))
			{
				return false;
			}
			if (LevelExact)
			{
				return PourRoomDl(c, fluid, RM_LevelSolve.U) >= RM_LevelSolve.U;   // PUMP_CANAL_FEED_FIX: the canal's room, not one square's
			}
			int i = map.cellIndices.CellToIndex(c);
			return RoomNotches(i) > 0 && InputAllowed(fluid) && RM_StockMath.FluidsCompatible(WetDug(i), FluidAt(c), fluid);
		}

		/// <summary>Phase 8: a pump pours one level into an excavated cell with room (fluids never mix). Exact-level water:
		/// the level spreads from the cell over the canal it joins (<see cref="TryPourDl"/>), so a canal holding a sheet still
		/// takes it (PUMP_CANAL_FEED_FIX_ONE_NOTCH_ONLY).</summary>
		public bool TryPourLevel(IntVec3 c, FluidDef fluid)
		{
			if (!IsExcavated(c) || fluid == null)
			{
				return false;
			}
			if (LevelExact)
			{
				return TryPourDl(c, fluid, RM_LevelSolve.U);
			}
			int f = FillAt(c);
			if (RoomNotches(map.cellIndices.CellToIndex(c)) <= 0)
			{
				return false;
			}
			return TrySetDriverFill(c, f + 1, fluid);
		}

		// ── PUMP_CANAL_FEED_FIX_ONE_NOTCH_ONLY / HOSE_LEFTOVER_FIX_NO_VANISHING_LITRES: pours in decilitres ──

		private int NeighbourIndex(int i, int dir)
		{
			IntVec3 n = map.cellIndices.IndexToCell(i) + GenAdj.CardinalDirections[dir];
			return n.InBounds(map) ? map.cellIndices.CellToIndex(n) : -1;
		}

		/// <summary>The pour walk (RM_LevelPour.Spread) from <paramref name="c"/> for up to <paramref name="want"/> dL of
		/// <paramref name="fluid"/>: dug squares not sealed by a shut sluice and holding no other liquid, each up to its room.
		/// Read-only on the grids; null credits = a refusal (liquid switched off, foreign start, no palette key).</summary>
		private long PlanPour(IntVec3 c, FluidDef fluid, long want, List<KeyValuePair<int, long>> credits, out byte claimKey)
		{
			claimKey = 0;
			if (fluid == null || want <= 0 || !c.InBounds(map) || !IsExcavated(c) || !InputAllowed(fluid))
			{
				return 0;
			}
			int start = map.cellIndices.CellToIndex(c);
			if (!RM_StockMath.FluidsCompatible(WetDug(start), FluidAt(c), fluid) || RM_FlowDoorRules.SealsLiquid(map.edificeGrid[c]))
			{
				return 0;
			}
			bool keyOk = TryPaletteKey(fluid, out claimKey);
			bool Joins(int i) => depthGrid[i] != 0 && !RM_FlowDoorRules.SealsLiquid(map.edificeGrid[i])
				&& RM_StockMath.FluidsCompatible(WetDug(i), FluidAt(map.cellIndices.IndexToCell(i)), fluid);
			long Room(int i)
			{
				if (!WetDug(i) && !keyOk)
				{
					return 0;
				}
				long r = depthGrid[i] * (long)RM_LevelSolve.U - WaterDl(i);
				return r > 0 ? r : 0;
			}
			return RM_LevelPour.Spread(start, want, true, NeighbourIndex, Joins, null, Room, RM_LevelPour.PourWalkCap, credits, null);
		}

		/// <summary>How many of <paramref name="want"/> dL of <paramref name="fluid"/> a pour at <paramref name="c"/> would place
		/// (the square, then the canal it joins). Exact-level off: one whole level if the square has a whole notch of room.</summary>
		public long PourRoomDl(IntVec3 c, FluidDef fluid, long want)
		{
			if (!LevelExact)
			{
				return want >= RM_LevelSolve.U && CanPourLevelWhole(c, fluid) ? RM_LevelSolve.U : 0;
			}
			return PlanPour(c, fluid, want, null, out _);
		}

		private bool CanPourLevelWhole(IntVec3 c, FluidDef fluid)
		{
			if (fluid == null || !c.InBounds(map) || !IsExcavated(c))
			{
				return false;
			}
			int i = map.cellIndices.CellToIndex(c);
			return RoomNotches(i) > 0 && InputAllowed(fluid) && RM_StockMath.FluidsCompatible(WetDug(i), FluidAt(c), fluid);
		}

		/// <summary>Pour exactly <paramref name="dl"/> decilitres of <paramref name="fluid"/> at <paramref name="c"/>, all or
		/// nothing: the square first, the rest over the dug squares it joins, nearest first (the pulse then levels it). A dry
		/// square claims the fluid. Exact-level off: whole levels only, into the square itself.</summary>
		public bool TryPourDl(IntVec3 c, FluidDef fluid, long dl)
		{
			if (dl <= 0 || fluid == null)
			{
				return false;
			}
			if (!LevelExact)
			{
				if (dl % RM_LevelSolve.U != 0)
				{
					return false;
				}
				// review day 3: room for EVERY level is checked before the one write (a per-level loop poured the first levels
				// and then returned false, so a caller keeping its liquid on false created water)
				long levels = dl / RM_LevelSolve.U;
				if (!CanPourLevelWhole(c, fluid) || RoomNotches(map.cellIndices.CellToIndex(c)) < levels)
				{
					return false;
				}
				return TrySetDriverFill(c, FillAt(c) + (int)levels, fluid);
			}
			var credits = new List<KeyValuePair<int, long>>();
			if (PlanPour(c, fluid, dl, credits, out byte key) != dl)
			{
				return false;
			}
			int now = Find.TickManager?.TicksGame ?? 0;
			foreach (KeyValuePair<int, long> cr in credits)
			{
				int i = cr.Key;
				int before = fillGrid[i];
				if (!WetDug(i))
				{
					fluidGrid[i] = key;
				}
				long w = WaterDl(i) + cr.Value;
				fillGrid[i] = (byte)(w / RM_LevelSolve.U);
				partGrid[i] = (ushort)(w % RM_LevelSolve.U);
				driverInputs.NoteWrite(i, before, fillGrid[i], now);
				ApplyFillTerrain(map.cellIndices.IndexToCell(i), fluid);
			}
			return true;
		}

		/// <summary>dL of <paramref name="fluid"/> the natural body at <paramref name="c"/> (a wet or dried pond square, never a
		/// dug one) would take back, up to <paramref name="want"/> (the return leg's rule, in decilitres: a limited pond up to its
		/// capacity, a limitless one anything).</summary>
		public long ReturnRoomDl(IntVec3 c, FluidDef fluid, long want)
		{
			if (!RimMandrakeFlowWorksSettings.pondReturnLegEnabled || want <= 0 || fluid == null || !c.InBounds(map) || IsExcavated(c))
			{
				return 0;
			}
			RM_LiquidBody body = stock.IndexedBodyAt(map, c);
			if (body == null || (body.fluid ?? ActiveFluid) != fluid)
			{
				return 0;
			}
			if (body.limitless)
			{
				return want;
			}
			long room = (long)System.Math.Round(body.capacity * (double)RM_LevelSolve.U) - body.stockDl;
			return room <= 0 ? 0 : room < want ? room : want;
		}

		/// <summary>Credit exactly <paramref name="dl"/> to the body at <paramref name="c"/>, all or nothing.</summary>
		public bool TryReturnDl(IntVec3 c, FluidDef fluid, long dl)
		{
			if (dl <= 0 || ReturnRoomDl(c, fluid, dl) != dl)
			{
				return false;
			}
			RM_LiquidBody body = stock.IndexedBodyAt(map, c);
			if (body.limitless)
			{
				limitlessReturnedTotal += dl / (float)RM_LevelSolve.U;
				return true;
			}
			body.stockDl += dl;
			return true;
		}

		/// <summary>HOSE_LEFTOVER_FIX_NO_VANISHING_LITRES: liquid with truly nowhere to go is the disclosed loss (owner: overflow
		/// destroys only where the game announces the amount): counted with the fill-in overflow and announced in litres.</summary>
		public void ReportLiquidLost(IntVec3 at, long dl, string what) => ReportLiquidLost(at, dl, what, false);

		/// <summary><paramref name="silent"/> (a released flood's remainder, owner card 2026-10-22 "Count silently, show in
		/// ledger"): counted exactly as the announced loss and in <see cref="ReleaseLostDl"/>, with no message.</summary>
		public void ReportLiquidLost(IntVec3 at, long dl, string what, bool silent)
		{
			if (dl <= 0)
			{
				return;
			}
			NotifyOverflowDestroyed(dl / (float)RM_LevelSolve.U);
			if (silent)
			{
				releaseLostDl += dl;
				return;
			}
			Messages.Message(what + " had nowhere to go: " + RM_Volume.FormatLitres(dl / (double)RM_Volume.UnitsPerLitre) + " were lost. "
				+ "Lost this way on this map so far: " + RM_Volume.FormatLitres(overflowDestroyedTotal * (double)RM_Volume.LitresPerLevel) + ".",
				new TargetInfo(at, map), MessageTypeDefOf.NeutralEvent, false);
		}

		public override void MapRemoved()
		{
			base.MapRemoved();
			RM_SuperdeepShooting.Forget(map);
		}

		public override void MapComponentUpdate()
		{
			base.MapComponentUpdate();
			// V2_PIT_ROWS_DIAGNOSE_NOBODY_STAYS_IN: with the clock stopped the tick-throttled pocket rebuild never runs.
			RM_PocketGrid.UpdatePaused(map, this);
		}

		public override void MapComponentTick()
		{
			base.MapComponentTick();
			// liquid networks L4 (rev 2 §3.2): tank jobs settle once per pump cycle (here, not in the hose component, which a
			// missing save-skip patch removes; tank-to-tank moves also run over rigid pipe with no hose at all)
			// PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL: passive levelling between bodies runs first, on the same cycle
			if (Find.TickManager.TicksGame % RM_PumpMath.CycleTicks == 7)
			{
				Machinery.RM_Levelling.Tick(map);
				Machinery.RM_LiquidNet.SettleTick(map);
				Machinery.RM_LiquidTheft.TheftTick(map);
			}
			// PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP: under the relative rule a fall can land in any dug cell (a rat into D 2),
			// so the detector runs while anything is dug (or, POND_BED step 2, a dry bed is a hollow).
			if (superdeepCellCount > 0 || (RM_PocketGrid.Relative && ClimbCellCount > 0))
			{
				superdeepTrap.Tick(map, this);
			}
			RM_PocketGrid.Tick(map, this);
			// Always (every 250 ticks, one hediff lookup per pawn): this removes the exposure marker from spawned pawns
			// while the setting is on, so it must keep running after the map's last pit is filled in (GPT FlowWorks
			// review #19). Off the map or with the setting off, HediffComp_PitExposureMarker removes it.
			RM_PitExposure.Tick(map, this);
			liquidFire.Tick(map, this);
			// Own timer, not the pulse: heat is the liquid's presence, so it keeps running with the depth engine off.
			liquidHeat.Tick(map, this);
			// SLIME_CROSSING_BUILD_SLIPPERY_SLOPE: natural slime slips too, so this runs even with nothing dug (own timer and switch)
			RM_SlimeSlip.Tick(map, this);
			// GPT deep review 2026-10-22 #5: spilled water on undug ground drowns too, so a map whose last pit was filled in
			// still runs it while any sheet is wet (the interval test first: GetComponent is not free every tick)
			if (excavatedCells.Count > 0
				|| (Find.TickManager.TicksGame % RM_FillEffectMath.IntervalTicks == 0
					&& (map.GetComponent<Sheet.RM_MapComponent_Sheet>()?.WetCells ?? 0) > 0))
			{
				RM_PitFillEffects.Tick(map, this);
			}
			// SWIM_DUG_RESERVOIR_FIX_PAWNS_CANT_ENTER: which dug squares are swum (own timer: pumps, hoses and fill-ins write
			// water between pulses, and the engine may be off)
			if ((excavatedCells.Count > 0 || swimCells.Count > 0) && Find.TickManager.TicksGame % SwimRefreshTicks == 11)
			{
				RefreshDugSwim();
			}
			// DEEP_WATER_BUILD_SWIM_OR_SINK: swim exhaustion everywhere, drowning on natural water (own 250-tick timer).
			Swimming.RM_Swim.Tick(map, this);
			// FlowWorks GPT review 2026-10-22: the water looks redraw when a square crosses a tint step or band rung (own timer:
			// pumps, hoses and ponds change water between pulses, and the engine may be off)
			if (Find.TickManager.TicksGame % RM_WaterLookWatcher.IntervalTicks == 17)
			{
				lookWatcher.Tick(map, this, excavatedCells);
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
			// FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS: dev-placed flow sources pour and flow sinks drain here, with rain and
			// before the components measure "before", so the ledger reads them as external input / output, never as a leak.
			MapControls.RM_MapControls.PulseAll(map, this);
			// PHASE 6, ruling 7: the burn takes its levels before the components measure "before", so burned
			// liquid is never mistaken for a leak.
			liquidFire.BurnPulse(map, this, RimMandrakeFlowWorksSettings.PulseIntervalTicks);
			// PHASE 4. Stock first too: recession and refill decide which source
			// cells are still wet, and the flow below reads that.
			if (stock != null)
			{
				stock.Pulse(map, this, RimMandrakeFlowWorksSettings.PulseIntervalTicks);
			}
			// CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED stage 1: spilled sheet water moves, runs back (credited through the
			// pour / return leg, so the solve below levels it this pulse), soaks and dries. Nothing when no sheet stands.
			map.GetComponent<Sheet.RM_MapComponent_Sheet>()?.EnginePulse();
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
			// WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES (owner 2026-10-17, ruled exactly level): decilitres, one surface per body.
			flowKernel.part = partGrid;
			flowKernel.levelExactEnabled = RimMandrakeFlowWorksSettings.levelExactEnabled;
			flowKernel.flowPerPulse = RimMandrakeFlowWorksSettings.FlowPerPulse;
			flowKernel.edgeSinksEnabled = RimMandrakeFlowWorksSettings.edgeSinksEnabled || MapControls.RM_MapControls.AnyDrainEdge(map);
			flowKernel.viscosityEnabled = RimMandrakeFlowWorksSettings.viscosityEnabled;
			flowKernel.creepEnabled = RimMandrakeFlowWorksSettings.viscosityEnabled && RimMandrakeFlowWorksSettings.thickCreepEnabled;
			flowKernel.creepWaterEnabled = RimMandrakeFlowWorksSettings.waterFrontCreepEnabled;
			flowKernel.levelBySurfaceEnabled = RimMandrakeFlowWorksSettings.levelBySurfaceEnabled;
			flowKernel.levelSetEnabled = RimMandrakeFlowWorksSettings.levelBySurfaceEnabled && RimMandrakeFlowWorksSettings.levelSetEnabled;
			// FLOW_ORDER_EXTERNAL_INPUT_1 part 2: the per-partition cap, and moving seams for a network bigger than it.
			flowKernel.maxComponentCells = RimMandrakeFlowWorksSettings.MaxNetworkCells;
			flowKernel.seamRotationEnabled = RimMandrakeFlowWorksSettings.networkSeamsMoveEnabled;
			// FLOW_ORDER_EXTERNAL_INPUT_1: cells a driver (pump, drill) fed recently seed the flow order.
			PruneDriverInputs();
			flowKernel.externalInput = RimMandrakeFlowWorksSettings.pumpFedSpreadEnabled && driverInputs.Count > 0
				? (System.Func<int, bool>)driverInputs.Contains
				: null;
			pulseSeeds.Clear();
			foreach (IntVec3 seed in excavatedCells)
			{
				pulseSeeds.Add(map.cellIndices.CellToIndex(seed));
			}
			// POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD, D2 (owner 2026-10-16: "It should slosh around until it levels, pond or canal
			// or otherwise."): a pond gives only while its surface stands above the ditch's water, and a canal above a pond's
			// surface runs back into it (after the flow, mouth-paced).
			// Exact-level water solves ponds and canals as one surface (RM_FlowKernel.ResolveExact): the whole-notch head rule and
			// its return half are the old engine's and stand down.
			bool headRule = RimMandrakeFlowWorksSettings.pondHeadRuleEnabled && RimMandrakeFlowWorksSettings.pondDepthEnabled
				&& stock != null && !RimMandrakeFlowWorksSettings.levelExactEnabled;
			flowKernel.sourceDrawdown = headRule ? (System.Func<int, int>)(idx => stock.DrawdownAt(map, map.cellIndices.IndexToCell(idx), this)) : null;
			flowKernel.returnLevel = headRule ? (System.Func<int, int, bool>)ReturnLevelToPond : null;
			flowKernel.Pulse(pulseSeeds, pulseCount);
			if (headRule)
			{
				pondReturned.Clear();
				if (flowKernel.ReturnToPonds(pulseSeeds) > 0)
				{
					for (int i = 0; i < pondReturned.Count; i++)
					{
						IntVec3 c = map.cellIndices.IndexToCell(pondReturned[i]);
						ApplyFillTerrain(c, FluidAt(c) ?? ActiveFluid);
					}
				}
			}
			if (flowKernel.edgeSinksEnabled)
			{
				sinkTransferredTotal += flowKernel.sinkDrained;
			}
			RunIntoBeds();
			if (Prefs.DevMode)
			{
				for (int i = 0; i < flowKernel.imbalanceReports.Count; i++)
				{
					// The ledger. Every transfer inside a component moves liquid, never makes it, so the only legitimate changes in
					// total fill are what sources credited in and what left down a sink. Anything else is a leak.
					Log.Warning("[RimMandrake.FlowWorks] conservation ledger does not balance: " +
						flowKernel.imbalanceReports[i] + ". This is a defect, not an overflow.");
				}
			}
			SyncFluidIdentity();
		}

		/// <summary>POND_BED step 2 (design §7 #8, Option B "canal backflow can refill it"): after the kernel's pulse, a dug
		/// square whose water stands above a neighbouring dry bed square's floor (RM_Volume.RunsIntoBed: a brim-full canal
		/// always) pours one level into it (exact-level water: up to one level's decilitres, so a thin sheet with no whole notch
		/// runs in too), and that water is credited to the POND's stock through the return leg, never
		/// to a dug cell. Refill and Restore then re-wet the bed last-in-first-out. All or nothing per level: the take
		/// happens only once the pond is known to accept it, so nothing is created or lost.</summary>
		private void RunIntoBeds()
		{
			if (!RimMandrakeFlowWorksSettings.pondBedHollowEnabled || !RimMandrakeFlowWorksSettings.pondReturnLegEnabled
				|| bedCellCount == 0 || excavatedCells.Count == 0)
			{
				return;
			}
			List<IntVec3> pours = null;
			List<IntVec3> beds = null;
			foreach (IntVec3 c in excavatedCells)
			{
				int i = map.cellIndices.CellToIndex(c);
				// FlowWorks review 2026-10-22 (thin part-notch sheet never ran into a dry bed): f is the water's notches ROUNDED UP
				// (ceil(W / U)), so a sheet with no whole notch (F 0, part > 0) is water too. For integer depths, d - ceil(W/U) < bed
				// is exactly "the surface (brim minus W) stands above the bed floor"; with no part-notch it is F, as before.
				long w = System.Math.Min(WaterDl(i), depthGrid[i] * (long)RM_LevelSolve.U);
				int f = (int)((w + RM_LevelSolve.U - 1) / RM_LevelSolve.U);
				// A shut sluice seals its cell (the kernel's sealedCell): on the canal square it holds the water in, on the bed
				// square it keeps the water out (review 2026-10-14: only the canal side was checked).
				if (f == 0 || RM_FlowDoorRules.SealsLiquid(map.edificeGrid[c]))
				{
					continue;
				}
				for (int k = 0; k < 4; k++)
				{
					IntVec3 n = c + GenAdj.CardinalDirections[k];
					if (n.InBounds(map) && RM_Volume.RunsIntoBed(depthGrid[i], f, NaturalBedDepthAt(n))
						&& !RM_FlowDoorRules.SealsLiquid(map.edificeGrid[n]))
					{
						if (pours == null) { pours = new List<IntVec3>(); beds = new List<IntVec3>(); }
						pours.Add(c);
						beds.Add(n);
						break;
					}
				}
			}
			if (pours == null)
			{
				return;
			}
			for (int p = 0; p < pours.Count; p++)
			{
				FluidDef fluid = FluidAt(pours[p]) ?? ActiveFluid;
				if (LevelExact)
				{
					// Exact-level water: up to one level's decilitres (a thin sheet gives what it has), all or nothing per pour.
					long want = System.Math.Min(WaterDlAt(pours[p]), (long)RM_LevelSolve.U);
					long room = ReturnRoomDl(beds[p], fluid, want);
					if (room <= 0)
					{
						continue;
					}
					long took = TakeDlCore(pours[p], room, out _);
					if (took > 0 && !TryReturnDl(beds[p], fluid, took) && !TryPourDl(pours[p], fluid, took))
					{
						ReportLiquidLost(pours[p], took, "Water running into a dry pond bed");   // defensive: checked above, so never expected
					}
					continue;
				}
				if (!CanReturnLevels(beds[p], fluid, 1) || !TakeLevelCore(pours[p], out _))
				{
					continue;
				}
				if (!TryReturnLevels(beds[p], fluid, 1))
				{
					TrySetDriverFill(pours[p], FillAt(pours[p]) + 1, fluid);   // defensive: checked above, so never expected
				}
			}
		}

		/// <summary>D2's return half: one level of dug square <paramref name="dugIdx"/>'s water goes home to the pond behind
		/// source <paramref name="srcIdx"/> through the return leg (all or nothing; the stock rises by exactly that level).</summary>
		private bool ReturnLevelToPond(int srcIdx, int dugIdx)
		{
			IntVec3 dug = map.cellIndices.IndexToCell(dugIdx);
			FluidDef fluid = FluidAt(dug) ?? ActiveFluid;
			if (!TryReturnLevels(map.cellIndices.IndexToCell(srcIdx), fluid, 1))
			{
				return false;
			}
			pondReturned.Add(dugIdx);   // re-laid after the kernel lowers it (fill terrain)
			return true;
		}

		private readonly List<int> pondReturned = new List<int>();

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

		bool RM_IFlowWorld.CanClaim(object fluid)
		{
			byte unused;
			return TryPaletteKey((fluid as FluidDef) ?? ActiveFluid, out unused);
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

		// ── RM_ILevelWorld: the exact-level kernel's reads and writes of natural bodies, in decilitres ──

		int RM_ILevelWorld.LevelBodyOf(int idx)
		{
			IntVec3 c = map.cellIndices.IndexToCell(idx);
			// FLUID_DISABLE_ALL_INPUTS_1: a natural body of a liquid switched off feeds no new liquid: not a node at all.
			if (!InputAllowed(DonorFluid(c, true) ?? ActiveFluid))
			{
				return -2;
			}
			return stock == null ? -1 : stock.LevelBodyOf(map, c, this);
		}

		long RM_ILevelWorld.BodyStockDl(int body)
		{
			return stock.LevelStockDl(stock.BodyById(body), this);
		}

		void RM_ILevelWorld.SetBodyStockDl(int body, long dl)
		{
			stock.SetLevelStockDl(stock.BodyById(body), dl, this);
		}

		int[] RM_ILevelWorld.BodyHistogram(int body)
		{
			return stock.DepthHistogramOf(map, stock.BodyById(body), this);
		}

		int RM_ILevelWorld.BedAt(int idx)
		{
			return BedLevelsAt(map.cellIndices.IndexToCell(idx));
		}

		/// <summary>dL limitless sources paid into dug squares (exact kernel), for the L0 ledger. Not scribed.</summary>
		private long limitlessPaidDl;
		public long LimitlessPaidDl => limitlessPaidDl;

		void RM_ILevelWorld.NoteLimitlessDl(object fluid, long dl)
		{
			limitlessPaidDl += dl;
		}

		/// <summary>WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES, owner R9 (2026-10-17): the per-body surface-gap diagnostic over the
		/// dug squares in <paramref name="rect"/> (the whole map when null): every connected body of water, its square count and
		/// the spread of its surface in metres (RM_SurfaceGap). Read by RM_NorthstarProofs.ProofLevelSurface.</summary>
		public List<RM_SurfaceGap.Body> SurfaceGaps(CellRect? rect = null)
		{
			var cells = new List<int>();
			foreach (IntVec3 c in excavatedCells)
			{
				if (rect == null || rect.Value.Contains(c))
				{
					cells.Add(map.cellIndices.CellToIndex(c));
				}
			}
			var pondSurf = new Dictionary<int, double>();
			System.Func<int, int, int> cardinal = (i, d) =>
			{
				IntVec3 n = map.cellIndices.IndexToCell(i) + GenAdj.CardinalDirections[d];
				return n.InBounds(map) ? map.cellIndices.CellToIndex(n) : -1;
			};
			System.Func<int, int> pondOf = i =>
			{
				IntVec3 n = map.cellIndices.IndexToCell(i);
				if (!IsSourceCell(n))
				{
					return -1;
				}
				int b = stock.LevelBodyOf(map, n, this);
				return b < 0 ? -2 : b;
			};
			System.Func<int, double> surf = b =>
			{
				RM_LiquidBody body = stock.BodyById(b);
				return body == null ? 0.0 : RM_LevelSolve.PondSurfaceHeight(stock.DepthHistogramOf(map, body, this),
					stock.LevelStockDl(body, this));
			};
			return RM_SurfaceGap.Measure(cells, i => depthGrid[i], WaterDl, i => FluidAt(map.cellIndices.IndexToCell(i)),
				cardinal, pondOf, surf, i => BedLevelsAt(map.cellIndices.IndexToCell(i)),
				i => RM_FlowDoorRules.SealsLiquid(map.edificeGrid[i]));
		}



		// ── rain (ruling 25) ──────────────────────────────────────────────

		/// <summary>The most rain one pulse can add to a square, in notches (a burst cap, not a depth).</summary>
		private const int RainMaxNotchesPerPulse = 4;

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
		/// Rain is external input, like a limitless body or a map-control flow source. It runs before the ledger's
		/// "before" is measured, so it can never be mistaken for a leak.
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
			// A per-pulse cap on a downpour (4 notches), not a depth: each square takes at most its own room (RoomNotches below),
			// so a 7 m pit fills by rain to its brim over pulses (PIT_DEPTH_WIDEN: no longer the dig cap's constant).
			while (rainAccumulator >= 1f && levels < RainMaxNotchesPerPulse)
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
				// The roof grid IS the rule. A roofed excavation stays dry in a
				// downpour, which is what makes roofing a trap a real decision.
				// Checked FIRST (FlowWorks review 2026-10-22): a roofed brimming square catches no rain, so none runs over its lip.
				if (map.roofGrid.Roofed(c))
				{
					continue;
				}
				int room = RoomNotches(i);
				if (room <= 0)
				{
					// CANAL_OVERFLOW stage 1 (D2): rain on a brimming square runs over the canal's lip (switch off: as before)
					if (WetDug(i) && FluidAt(c) == fluid)
					{
						Sheet.RM_MapComponent_Sheet.RainOverflow(map, c, levels, fluid);
					}
					continue;
				}
				if (!RM_StockMath.FluidsCompatible(WetDug(i), FluidAt(c), fluid))
				{
					continue;
				}
				int add = room < levels ? room : levels;
				if (!WetDug(i))
				{
					byte rainKey;
					if (!TryPaletteKey(fluid, out rainKey))
					{
						continue;   // P7: no key for water -> this dry cell stays dry, never mis-recorded (and spills nothing)
					}
					fluidGrid[i] = rainKey;
				}
				if (add < levels)
				{
					Sheet.RM_MapComponent_Sheet.RainOverflow(map, c, levels - add, fluid);   // CANAL_OVERFLOW stage 1 (D2)
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
			if (!c.InBounds(map))
			{
				return;
			}
			int i = map.cellIndices.CellToIndex(c);
			if (depthGrid[i] == 0)
			{
				return;   // the engine draws only its own dug squares; a lake square is RM_LiquidStock.StagePond's
			}
			// LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (unified depth spec §4.1): ONE rule for every dug square, canal or pit, exact-level
			// water or not: the look is chosen by the TRUE metres of water standing in it (under 25 cm, 0.5, 1, 1.5, 2 m and
			// deeper), never by how full the hole is. A part-filled pit shows its water's depth like any canal (4 cm in a 2 m pit
			// is a thin sheet, not "very deep water"); what the pit's own fill terrain carried for pathing (cost 300: nobody
			// routes through a pit by choice) is kept by RM_Patch_WetPitPlanningCost, and the trap, the hold and the climb read
			// the depth grid, never the terrain (ruling 26: a pit captures as if dry).
			//
			// POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD (rebuild P14, owner R10: one kind of water): the picture is a BASE-layer
			// write. Wet: the liquid's rung of the one ladder (water: RM_WaterLadder's freshwater terrains, the same a drawn-down
			// lake shows; every other liquid its own non-temporary fill tiers). Dry: the dug floor from the depth grid
			// (RM_Channel_*), recomputed, never stored as a second truth. The TEMP layer is left to vanilla: ice
			// (FreezeManager) and floods lie over our water as they do over a lake, and the water-body tracker sees the square
			// (GetWaterBodyType reads the base layer), which is what gives dug water fish and ice (engine doc §2.2).
			// Things on the square follow vanilla's terrain-change rules (TerrainGrid.DoTerrainChangedEffects, the same call
			// the temp write made): plants without the new band's tags die, filth the band refuses goes, a blueprint or frame
			// the band cannot carry is cancelled. THE one rule for a BUILT building whose affordance the new band lacks: it
			// stands (vanilla never removes a built thing on a terrain change, and neither did the temp-layer fill).
			TerrainDef want = null;
			if (WetDug(i))
			{
				if (fluid == null)
				{
					return;
				}
				want = fluid.WetTerrainForBand(RM_ExcavationDepth.FillTier(WaterDl(i)));
			}
			if (want == null)
			{
				want = RM_ExcavationDepth.DryTerrainFor(depthGrid[i]);
			}
			if (want == null)
			{
				return;
			}
			TerrainDef cur = map.terrainGrid.BaseTerrainAt(c);
			if (cur == want)
			{
				return;
			}
			FluidDef held = FluidAt(c) ?? fluid;
			bool drained = held != null && held.OwnsWetTerrain(cur) && !held.OwnsWetTerrain(want);
			map.terrainGrid.SetTerrain(c, want);
			if (drained)
			{
				Machinery.Kits.RM_FluidResidue.NoteDrained(map, c, held);
			}
		}

		/// <summary>Take the water picture off a square being filled back in to the surface (its depth already 0): a pre-P14
		/// temp fill this engine placed comes off the temp layer, and a base-layer water picture becomes the dry floor of
		/// <paramref name="oldDepth"/> so the restore that follows (or the legacy fallback, which keys on a channel terrain)
		/// starts from a dug floor, never from standing water. Only this engine's own pictures: a release some other path is
		/// still standing on is left alone.</summary>
		private void ClearFillTerrain(IntVec3 c, byte oldDepth)
		{
			FluidDef fluid = FluidAt(c) ?? ActiveFluid;
			if (fluid == null)
			{
				return;
			}
			TerrainDef temp = map.terrainGrid.TempTerrainAt(c);
			if (temp != null && fluid.OwnsFillTerrain(temp))
			{
				map.terrainGrid.RemoveTempTerrain(c);
			}
			TerrainDef cur = map.terrainGrid.BaseTerrainAt(c);
			if (fluid.OwnsWetTerrain(cur))
			{
				TerrainDef dry = RM_ExcavationDepth.DryTerrainFor(oldDepth > 0 ? oldDepth : RM_ExcavationDepth.Shallow);
				if (dry != null)
				{
					map.terrainGrid.SetTerrain(c, dry);
					Machinery.Kits.RM_FluidResidue.NoteDrained(map, c, fluid);
				}
			}
		}

		/// <summary>P14's one-time save migration (fillLayerModel 0 -> 1). A save from before P14 carries every wet dug
		/// square's liquid on the TEMP layer: each such fill this engine placed comes off, and the square is redrawn on the
		/// BASE layer from the grids. No water moves: the grids are the truth and are not written; the litres are summed
		/// before and after and logged, so "nothing lost" is read off the log, not assumed. Back up the Saves folder before
		/// the first load (the item's instruction; downgrade is unsupported).</summary>
		private void MigrateFillLayer()
		{
			if (fillLayerModel >= 1)
			{
				return;
			}
			long beforeDl = 0, afterDl = 0;
			int wet = 0, tempFills = 0, baseWet = 0;
			List<FluidDef> fluids = DefDatabase<FluidDef>.AllDefsListForReading;
			foreach (IntVec3 c in excavatedCells)
			{
				int i = map.cellIndices.CellToIndex(c);
				beforeDl += WaterDl(i);
				TerrainDef temp = map.terrainGrid.TempTerrainAt(c);
				if (temp != null)
				{
					for (int k = 0; k < fluids.Count; k++)
					{
						if (fluids[k].OwnsFillTerrain(temp))
						{
							map.terrainGrid.RemoveTempTerrain(c);
							tempFills++;
							break;
						}
					}
				}
				ApplyFillTerrain(c, FluidAt(c) ?? ActiveFluid);
				if (WetDug(i))
				{
					wet++;
					FluidDef f = FluidAt(c) ?? ActiveFluid;
					if (f != null && f.OwnsWetTerrain(map.terrainGrid.BaseTerrainAt(c)))
					{
						baseWet++;
					}
				}
				afterDl += WaterDl(i);
			}
			Log.Message("[RimMandrake.FlowWorks] fill layer model 0 -> 1 (wet dug squares on the base layer, P14): " + wet
				+ " wet dug square(s), " + tempFills + " temp fill(s) taken off, " + baseWet + " base write(s) standing; "
				+ RM_Volume.FormatLitres(beforeDl / 10f) + " before, " + RM_Volume.FormatLitres(afterDl / 10f) + " after"
				+ (beforeDl == afterDl ? " (unchanged)." : " (CHANGED: report this)."));
			fillLayerModel = 1;
		}

		// ── the gate the legacy flood consults ────────────────────────────

		/// <summary>§4's "biggest gap", closed: liquid may only enter a cell
		/// that has been excavated, or a cell that is already part of a liquid
		/// body. Both are the same test, because a natural body reads through
		/// as SUPERDEEP.</summary>
		public bool CanLiquidEnter(IntVec3 c)
		{
			// POND_BED step 2: NOT DepthAt > 0 any more, which now reads a dry bed as a hollow; a legacy flood spreading
			// onto a bed would write terrain on the pond's square. Dug or natural liquid, exactly as before.
			return IsExcavated(c) || IsNaturalLiquid(c);
		}

		// ════════════════════════════════════════════════════════════════
		// DRIVER API — CANYON_FLOOD_ERASES_CANALS_1.
		//
		// ⚠️ ADDITIVE REGION. Everything above is the engine; this is the
		// whole of the surface a flood-driver client (ruling 8: CrackedLands
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

		// FLOW_ORDER_EXTERNAL_INPUT_1: cells a driver fed recently (RM_DriverInputs, selftested). Not saved: a driver
		// re-marks its cell on its next write, or on its next cycle backed up against a brimming cell (P4).
		private readonly RM_DriverInputs driverInputs = new RM_DriverInputs();

		private void PruneDriverInputs()
		{
			driverInputs.Prune(Find.TickManager.TicksGame, i => depthGrid[i] == 0);
		}

		/// <summary>PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD (P4): a driver holding liquid for this excavated cell found it
		/// brimming. It is still feeding the channel, so the cell stays a flow-order input (after a load the input set
		/// starts empty, and this is how a pump against a full outlet re-marks it). Ignored on a dry or unexcavated cell.</summary>
		public void NoteDriverBackedUp(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return;
			}
			int i = map.cellIndices.CellToIndex(c);
			if (depthGrid[i] > 0 && fillGrid[i] >= depthGrid[i])
			{
				driverInputs.NoteBackedUp(i, Find.TickManager.TicksGame);
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
			// Redraw with the liquid the cell HELD when it had one: a drain to 0 by a driver naming another fluid
			// must strip the held fluid's terrain (OwnsFillTerrain is per fluid), not leave it on a dry cell.
			FluidDef render = FluidAt(c) ?? fluid;
			// FLOWWORKS_REVIEW_LOOKS_ROUND_1: a liquid switched off in Mod Settings never pours into a cut.
			if (fill > fillGrid[i] && !InputAllowed(fluid))
			{
				return DriverFillOutcome.Refused;
			}
			if (fill > 0 && !RM_StockMath.FluidsCompatible(WetDug(i), FluidAt(c), fluid))
			{
				return DriverFillOutcome.Refused;
			}
			if (fill > 0 && !WetDug(i))
			{
				byte driverKey;
				if (!TryPaletteKey(fluid, out driverKey))
				{
					return DriverFillOutcome.Refused;   // P7: refused before any fill changes
				}
				fluidGrid[i] = driverKey;
			}
			driverInputs.NoteWrite(i, fillGrid[i], fill, Find.TickManager.TicksGame);
			fillGrid[i] = (byte)fill;
			// WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: a driver sets whole notches; the part-notch below them stays, except at
			// the two ends a driver means literally: drained to 0 (it took everything) or filled to the brim (nothing above it).
			if (fill == 0 || fill >= d)
			{
				partGrid[i] = 0;
			}
			if (fill == 0)
			{
				fluidGrid[i] = 0;
			}
			if (render != null)
			{
				ApplyFillTerrain(c, render);
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
