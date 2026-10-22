using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.FlowWorks.Machinery;
using static RimMandrake.FlowWorks.RM_SheetMath;

namespace RimMandrake.FlowWorks.Sheet
{
	/// <summary>CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED, Stage 1: the engine layer of canal overflow
	/// (design/RimMandrake/canal_overflow_flooding_2026-10-21.md §3 Option C as amended by §6; owner answers §5).
	///
	/// The sheet of water standing ABOVE ground on undug squares, in whole decilitres, run by the Verse-free kernel
	/// <see cref="RM_SheetMath"/> on the depth engine's own pulse (RM_MapComponent_Excavation.DoPulse calls
	/// <see cref="EnginePulse"/>). This class only maps the map onto the kernel and the kernel's transfers back onto the
	/// engine:
	/// - <b>Topology</b> is read from authoritative state each pulse (§6 item 7: dug grid, the stock's bodies, base and
	///   foundation layers, the edifice), never from a picture, over the wet cells dilated by sweeps + 1.
	/// - <b>Spills</b> (D1/D2: pump, rain, fill-in) enter at the lips nearest the inflow (§6 item 8) through
	///   <see cref="Offer"/> / <see cref="Probe"/>: offer → accepted dL, the caller debits exactly that (§6 item 1).
	///   Refused water is refused back to the inflow (back-pressure), never destroyed.
	/// - <b>Return</b> into a dug channel or a limited pond is the engine's own atomic pour / return leg
	///   (<see cref="RM_SheetMath.World.Credit"/>); a limitless body is the disclosed "joined the lake" (D6).
	/// - <b>Losses</b> (D6, disclosed): soak by the base ground's class, evaporation by temperature and roof. Mod Settings
	///   rates (RM_SheetSettings), the placeholders kept as defaults (owner card 2026-10-22), tuned on the walk.
	/// - <b>Picture</b>: overlay only (§6 item 2): <see cref="SectionLayer_RMSheetWater"/>. No temp terrain is written, so no vanilla
	///   side effect fires from a picture; the effects (crops, wading, fire) read the sheet grid itself (<see cref="Effects"/>).
	///
	/// Every FlowWorks liquid spills (owner 2026-10-22: <i>"Build for all flowworks liquids."</i>), each by its own FluidDef
	/// (RM_SheetFluidMath.RuleFor); different liquids never mix (a square or body holding another refuses); burnable spills
	/// spread and burn (D5, RM_SheetFire.cs). Saved: the kernel's whole continuation state (§6 item 4) plus this map's sheet
	/// fluid palette (its own, never the engine's compacting palette).</summary>
	public partial class RM_MapComponent_Sheet : MapComponent
	{
		// Loss rates (cm a day) per ground class / weather, never per biome (§3 step 4): Mod Settings (RM_SheetSettings), the
		// placeholder values kept as the defaults by owner card 2026-10-22, to be tuned on the walk.
		public const float EvapMaxFactor = 3f;
		private const int MaxLips = 16, LipWalkCap = 4096;

		private State state;
		private World world;
		private readonly Params prm = new Params();
		private List<FluidDef> fluids = new List<FluidDef>();
		private int[] stamp;
		private int stampId;
		private readonly PulseReport rep = new PulseReport();
		private RM_MapComponent_Excavation ex;

		public RM_MapComponent_Sheet(Map map) : base(map)
		{
		}

		public int WetCells => state?.WetCount ?? 0;

		private RM_MapComponent_Excavation Engine => ex ?? (ex = map.GetComponent<RM_MapComponent_Excavation>());

		private static FluidDef Water => RimMandrakeFlowWorks_DefOf.RM_Fluid_Water;

		private static readonly int[] DX = { 0, 1, 0, -1 }, DZ = { 1, 0, -1, 0 }; // the kernel's N, E, S, W

		// ── state ──

		private void Ensure()
		{
			int w = map.Size.x, h = map.Size.z;
			if (state == null || state.W != w || state.H != h)
			{
				if (state != null && state.WetCount > 0)
				{
					Log.Error("[RimMandrake.FlowWorks] sheet water state does not match this map's size; purging it (disclosed): "
						+ RM_Volume.FormatLitres(PurgeAll(state) / (double)RM_Volume.UnitsPerLitre));
				}
				uint salt = (uint)Gen.HashCombineInt(Find.World?.info?.Seed ?? 0, map.uniqueID);
				state = new State(w, h, salt);
			}
			if (world == null || world.W != w || world.H != h)
			{
				world = new World(w, h);
				for (int c = 0; c < w * h; c++)
				{
					world.Kinds[c] = Kind.Blocked; // a cell is Blocked until classified this pulse (fail closed)
				}
				world.Credit = Credit;
				stamp = new int[w * h];
				stampId = 0;
			}
			SyncParams();
		}

		private void SyncParams()
		{
			// Stage 3: the kernel's numbers are the Mod Settings (defaults = shipped). A lowered cap or wet-square limit only
			// refuses NEW water (the kernel never cuts a cell down to a cap: D10, §6 item 5).
			prm.CropKillPulses = Math.Max(1, RM_SheetSettings.cropDrownPulses);
			prm.SheetCapDl = Math.Max(DlPerCm, RM_SheetSettings.sheetCapCm * DlPerCm);
			prm.MaxWetCells = Math.Max(1, RM_SheetSettings.maxWetSquares);
			prm.RetentionDl = Math.Max(1, Mathf.RoundToInt(RM_SheetSettings.retentionCm * DlPerCm));
			prm.MinReceiveDl = Math.Max(1, prm.RetentionDl / 2);
			prm.SweepsPerPulse = Mathf.Clamp(RM_SheetSettings.sweepsPerPulse, 1, 12);
			prm.DoorLeakPermille = Mathf.Clamp(RM_SheetSettings.doorLeakPercent, 0, 100) * 10;
			float pulsesPerDay = GenDate.TicksPerDay / (float)RimMandrakeFlowWorksSettings.PulseIntervalTicks;
			for (int k = 0; k < fluids.Count; k++)
			{
				FluidDef f = fluids[k];
				// all liquids (owner 2026-10-22): each follows its own FluidDef; a liquid gone from the mod set keeps draining
				world.Fluids[k + 1] = f == null
					? new FluidRule { InfiltrationPermille = 1000, EvaporationPermille = 1000, NeverFreezes = true }
					: RM_SheetFluidMath.RuleFor(Burnable(f), f.hot, f.slipperiness > 0f, f.ticksPerTile, f.sheetSoakPercent,
						f.sheetEvaporationPercent);
				if (f != null && f.sheetBoilCmPerHour > 0f)
				{
					FluidRule r = world.Fluids[k + 1];
					r.BoilMilliDl = RM_SheetFluidMath.BoilMilliDlPerPulse(f.sheetBoilCmPerHour, DlPerCm, pulsesPerDay);
					r.BoilAboveDeciC = Mathf.RoundToInt(f.sheetBoilPointC * 10f);
					world.Fluids[k + 1] = r;
				}
			}
		}

		private byte Key(FluidDef f)
		{
			int i = fluids.IndexOf(f);
			if (i < 0)
			{
				if (fluids.Count >= 255)
				{
					return 0;
				}
				fluids.Add(f);
				i = fluids.Count - 1;
				if (world != null)
				{
					SyncParams();
				}
			}
			return (byte)(i + 1);
		}

		private FluidDef FluidOf(byte key) => key == 0 || key > fluids.Count ? null : fluids[key - 1];

		// ── topology (§6 item 7: authoritative layers, never the picture) ──

		/// <summary>GPT deep review 2026-10-22 #7: a cell whose kind changes (a wall removed, a door built) wakes itself and its
		/// neighbours, else a settled, lossless puddle slept on beside newly open ground.</summary>
		private void Classify(int idx)
		{
			Kind before = world.Kinds[idx];
			ClassifyCell(idx);
			if (state != null && world.Kinds[idx] != before)
			{
				RM_SheetMath.WakeAround(state, world, idx);
			}
		}

		private void ClassifyCell(int idx)
		{
			IntVec3 c = map.cellIndices.IndexToCell(idx);
			RM_MapComponent_Excavation e = Engine;
			world.RoomDl[idx] = 0;
			world.BodyFluid[idx] = 0;
			world.SoakMilliDl[idx] = 0;
			world.EvapMilliDl[idx] = 0;
			world.TempDeciC[idx] = Mathf.RoundToInt(GenTemperature.GetTemperatureForCell(c, map) * 10f);
			Building edifice = map.edificeGrid[idx];
			if (e != null && e.IsExcavated(c))
			{
				FluidDef held = e.FluidAt(c);
				bool ok = !RM_FlowDoorRules.SealsLiquid(edifice);
				world.Kinds[idx] = ok ? Kind.Receiver : Kind.Blocked;
				if (ok)
				{
					world.RoomDl[idx] = int.MaxValue / 4; // the engine's pour decides (World.Credit)
					world.BodyFluid[idx] = held == null ? (byte)0 : Key(held); // another liquid refuses (the kernel's Compatible)
				}
				return;
			}
			RM_LiquidBody body = e?.Stock?.IndexedBodyAt(map, c);
			if (body != null)
			{
				FluidDef bf = body.fluid ?? e.ActiveFluid;
				world.Kinds[idx] = body.limitless ? Kind.Sink : Kind.Receiver;
				world.RoomDl[idx] = int.MaxValue / 4; // the return leg decides (World.Credit)
				world.BodyFluid[idx] = bf == null ? (byte)0 : Key(bf); // a pond of another liquid refuses (fluids never mix)
				return;
			}
			TerrainDef baseT = map.terrainGrid.BaseTerrainAt(c);
			if (baseT != null && baseT.IsWater)
			{
				// natural water the stock does not track: it absorbs the sheet like a limitless body (disclosed)
				world.Kinds[idx] = Kind.Sink;
				world.BodyFluid[idx] = Key(Water);
				return;
			}
			if (edifice != null)
			{
				if (RM_FlowDoorRules.IsFlowDoor(edifice) || edifice is Frame)
				{
					world.Kinds[idx] = RM_FlowDoorRules.LetsLiquidThrough(edifice) ? Kind.Grate : Kind.Blocked;
				}
				else
				{
					world.Kinds[idx] = edifice is Building_Door ? Kind.Door : Kind.Blocked; // D4: doors leak slowly
				}
				if (world.Kinds[idx] == Kind.Blocked)
				{
					return;
				}
			}
			else if (map.terrainGrid.FoundationAt(c) != null)
			{
				world.Kinds[idx] = Kind.Blocked;
				return;
			}
			else
			{
				TerrainDef top = map.terrainGrid.TopTerrainAt(c);
				world.Kinds[idx] = top != null && top.passability == Traversability.Impassable ? Kind.Blocked : Kind.Open;
				if (world.Kinds[idx] == Kind.Blocked)
				{
					return;
				}
			}
			float pulsesPerDay = GenDate.TicksPerDay / (float)RimMandrakeFlowWorksSettings.PulseIntervalTicks;
			float soakCm = map.terrainGrid.UnderTerrainAt(c) != null ? 0f : SoakCmPerDay(baseT);
			world.SoakMilliDl[idx] = Mathf.RoundToInt(soakCm * DlPerCm * 1000f / pulsesPerDay);
			float t = GenTemperature.GetTemperatureForCell(c, map);
			float evapCm = t <= 0f ? 0f : RM_SheetSettings.dryCmPerDayAt20C * Mathf.Min(EvapMaxFactor, t / 20f)
				* (map.roofGrid.Roofed(c) ? RM_SheetSettings.roofedDryPercent / 100f : 1f);
			world.EvapMilliDl[idx] = Mathf.RoundToInt(evapCm * DlPerCm * 1000f / pulsesPerDay);
		}

		/// <summary>Soak by the ground's class (§3 step 4: sand/soil/gravel high→low; rock, constructed floor, ice, mud, marsh
		/// and water take 0). PROVISIONAL.</summary>
		public static float SoakCmPerDay(TerrainDef t)
		{
			if (t == null || t.IsWater || t.passability == Traversability.Impassable)
			{
				return 0f;
			}
			string n = t.defName ?? "";
			if (n.IndexOf("Mud", StringComparison.OrdinalIgnoreCase) >= 0 || n.IndexOf("Marsh", StringComparison.OrdinalIgnoreCase) >= 0
				|| n.IndexOf("Ice", StringComparison.OrdinalIgnoreCase) >= 0)
			{
				return 0f;
			}
			if (n.IndexOf("Sand", StringComparison.OrdinalIgnoreCase) >= 0)
			{
				return RM_SheetSettings.soakCmPerDaySand;
			}
			if (t.fertility >= 0.5f)
			{
				return RM_SheetSettings.soakCmPerDaySoil;
			}
			return t.fertility > 0f ? RM_SheetSettings.soakCmPerDayGravel : 0f; // fertility 0: rock, smooth stone
		}

		/// <summary>Classify every cell the kernel can touch this pulse: the wet cells and, through sheet-holding cells, the
		/// next sweeps + 1 rings (a sweep moves water one cell; levelling and return read one further).</summary>
		private void RefreshAround()
		{
			stampId++;
			if (stampId == int.MaxValue)
			{
				Array.Clear(stamp, 0, stamp.Length);
				stampId = 1;
			}
			var frontier = new List<int>(state.Occ);
			foreach (int c in frontier)
			{
				stamp[c] = stampId;
				Classify(c);
			}
			int W = state.W, H = state.H;
			var next = new List<int>();
			for (int ring = 0; ring <= prm.SweepsPerPulse; ring++)
			{
				next.Clear();
				foreach (int c in frontier)
				{
					if (!World.HoldsSheet(world.Kinds[c]))
					{
						continue;
					}
					int x = c % W, z = c / W;
					for (int d = 0; d < 4; d++)
					{
						int nx = x + DX[d], nz = z + DZ[d];
						if (nx < 0 || nz < 0 || nx >= W || nz >= H)
						{
							continue;
						}
						int n = nz * W + nx;
						if (stamp[n] == stampId)
						{
							continue;
						}
						stamp[n] = stampId;
						Classify(n);
						next.Add(n);
					}
				}
				var swap = frontier;
				frontier = next;
				next = swap;
			}
		}

		/// <summary>World.Credit: the engine's own atomic transfer into a dug channel (its pour walk) or a limited pond (its
		/// return leg). Returns the dL it took; the kernel debits exactly that.</summary>
		private int Credit(int idx, int want, byte fluidKey)
		{
			RM_MapComponent_Excavation e = Engine;
			FluidDef f = FluidOf(fluidKey);
			if (e == null || f == null || want <= 0)
			{
				return 0;
			}
			IntVec3 c = map.cellIndices.IndexToCell(idx);
			if (e.IsExcavated(c))
			{
				FluidDef held = e.FluidAt(c);
				if (!RM_StockMath.FluidsCompatible(held != null, held, f))
				{
					return 0; // different liquids never mix
				}
				// a brimming square means a brimming body (one level surface per body): skip the walk
				if (e.WaterDlAt(c) >= e.DepthAt(c) * (long)RM_LevelSolve.U)
				{
					return 0;
				}
				long room = e.PourRoomDl(c, f, want);
				return room > 0 && e.TryPourDl(c, f, room) ? (int)room : 0;
			}
			long back = e.ReturnRoomDl(c, f, want);
			return back > 0 && e.TryReturnDl(c, f, back) ? (int)back : 0;
		}

		// ── spills (§6 items 1 and 8) ──

		/// <summary>Lips nearest the inflow first: a walk outward through the connected dug body from <paramref name="origin"/>
		/// (the pump's outlet, the rained-on square, the filled-in square); every sheet-holding undug neighbour it meets is a lip.
		/// The origin itself is a lip when it is undug (a filled-in square). Classifies what it meets.</summary>
		private int[] FindLips(IntVec3 origin, FluidDef fluid)
		{
			RM_MapComponent_Excavation e = Engine;
			var lips = new List<int>(MaxLips);
			if (e == null || !origin.InBounds(map))
			{
				return lips.ToArray();
			}
			int W = state.W, H = state.H;
			int start = map.cellIndices.CellToIndex(origin);
			var seen = new HashSet<int> { start };
			var queue = new Queue<int>();
			if (e.IsExcavated(origin))
			{
				queue.Enqueue(start);
			}
			else
			{
				Classify(start);
				if (World.HoldsSheet(world.Kinds[start]))
				{
					lips.Add(start);
				}
				queue.Enqueue(start); // the filled-in square's dug neighbours are the body it left
			}
			int walked = 0;
			while (queue.Count > 0 && lips.Count < MaxLips && walked++ < LipWalkCap)
			{
				int p = queue.Dequeue();
				int x = p % W, z = p / W;
				for (int d = 0; d < 4 && lips.Count < MaxLips; d++)
				{
					int nx = x + DX[d], nz = z + DZ[d];
					if (nx < 0 || nz < 0 || nx >= W || nz >= H)
					{
						continue;
					}
					int n = nz * W + nx;
					if (!seen.Add(n))
					{
						continue;
					}
					IntVec3 nc = map.cellIndices.IndexToCell(n);
					if (e.IsExcavated(nc))
					{
						FluidDef held = e.FluidAt(nc);
						if (!RM_FlowDoorRules.SealsLiquid(map.edificeGrid[n]) && RM_StockMath.FluidsCompatible(held != null, held, fluid))
						{
							queue.Enqueue(n);
						}
						continue;
					}
					Classify(n);
					if (World.HoldsSheet(world.Kinds[n]))
					{
						lips.Add(n);
					}
				}
			}
			return lips.ToArray();
		}

		/// <summary>The master switch, the per-inflow switch (stage 3), the depth engine, and the fluid: water, or any other
		/// FlowWorks liquid while "other liquids spill" is on (owner 2026-10-22: <i>"Build for all flowworks liquids."</i>).</summary>
		private bool Accepts(FluidDef fluid, Source from) =>
			RM_SheetSettings.SpillsFrom(from) && RimMandrakeFlowWorksSettings.depthEngineEnabled && fluid != null
			&& (fluid == Water || RM_SheetSettings.otherLiquidsSpillEnabled);

		private SpillOffer MakeOffer(IntVec3 origin, long dl, FluidDef fluid, Source from)
		{
			Ensure();
			return new SpillOffer
			{
				LipNearestFirst = FindLips(origin, fluid),
				AmountDl = (int)Math.Min(dl, int.MaxValue / 2),
				Fluid = Key(fluid),
				From = from,
			};
		}

		/// <summary>How many of <paramref name="dl"/> a spill at <paramref name="origin"/> would place now, changing no water.
		/// 0 when the switch is off or the fluid is not accepted (Accepts).</summary>
		public long Probe(IntVec3 origin, long dl, FluidDef fluid, Source from)
		{
			if (dl <= 0 || !Accepts(fluid, from))
			{
				return 0;
			}
			SpillOffer o = MakeOffer(origin, dl, fluid, from);
			return o.Fluid == 0 ? 0 : PreviewSpill(state, world, prm, o);
		}

		/// <summary>Spill up to <paramref name="dl"/> over the lips nearest <paramref name="origin"/>. Returns the dL accepted;
		/// the caller debits exactly that and keeps (refuses back) the rest.</summary>
		public long Offer(IntVec3 origin, long dl, FluidDef fluid, Source from)
		{
			if (dl <= 0 || !Accepts(fluid, from))
			{
				return 0;
			}
			SpillOffer o = MakeOffer(origin, dl, fluid, from);
			if (o.Fluid == 0)
			{
				return 0;
			}
			int got = ResolveSpills(state, world, prm, new[] { o })[0];
			if (got > 0)
			{
				TellOverflowOnce(origin, from, fluid);
				// a spill between pulses changes the picture now (the overlay draws a fresh square's tier from its dL)
				foreach (int k in o.LipNearestFirst)
				{
					map.mapDrawer.MapMeshDirty(map.cellIndices.IndexToCell(k), MapMeshFlagDefOf.Terrain);
				}
			}
			return got;
		}

		public static RM_MapComponent_Sheet Of(Map map) => map?.GetComponent<RM_MapComponent_Sheet>();

		/// <summary>The fill-in hook (D1): the homeless remainder of a displacement spills. Returns dL accepted.</summary>
		public static long SpillHomeless(Map map, IntVec3 from, long dl, FluidDef fluid) =>
			Of(map)?.Offer(from, dl, fluid, Source.FillIn) ?? 0;

		/// <summary>The flood hook (D2, owner card 2026-10-22): what a <c>Flood_FlowWorks</c> release (a heat-kit release, a
		/// forge flood, a tar belch) still holds when its walk ends spills over the lips nearest its seed. Returns dL accepted;
		/// the release debits exactly that and discloses what nobody took.</summary>
		public static long SpillRelease(Map map, IntVec3 seed, long dl, FluidDef fluid) =>
			Of(map)?.Offer(seed, dl, fluid, Source.Flood) ?? 0;

		/// <summary>The rain hook (D2): <paramref name="levels"/> of rain on a brimming, unroofed square of water run over its
		/// lip. Rain is external input: what the sheet refuses is simply not added, as before.</summary>
		public static void RainOverflow(Map map, IntVec3 c, int levels, FluidDef rain)
		{
			if (levels <= 0 || map.roofGrid.Roofed(c))
			{
				return;
			}
			RM_MapComponent_Excavation e = map.GetComponent<RM_MapComponent_Excavation>();
			FluidDef held = e?.FluidAt(c);
			if (held != null && held != rain)
			{
				return;
			}
			Of(map)?.Offer(c, levels * (long)RM_LevelSolve.U, rain, Source.Rain);
		}

		/// <summary>The pump hook (D2), part 1: the brimming outlet square of water in a backed-up pump's reach whose canal lip
		/// takes a whole level now (exact probe). False with the switch off or when no lip has room (backed up, as before).</summary>
		public static bool PumpSpillOutlet(Map map, List<IntVec3> cells, List<(int room, bool wet, FluidDef fill)> cd, int units,
			FluidDef fluid, out IntVec3 outlet)
		{
			outlet = IntVec3.Invalid;
			RM_MapComponent_Sheet sheet = Of(map);
			if (sheet == null || !sheet.Accepts(fluid, Source.Pump))
			{
				return false;
			}
			for (int c = 0; c < cells.Count; c++)
			{
				if (cd[c].room > 0 || !cd[c].wet || cd[c].fill != fluid)
				{
					continue;
				}
				if (sheet.Probe(cells[c], units, fluid, Source.Pump) == units)
				{
					outlet = cells[c];
					return true;
				}
			}
			return false;
		}

		/// <summary>The pump hook (D2), part 2: the sheet at <paramref name="outlet"/>'s lip as the destination leg of a
		/// transfer (checked by the exact probe before anything moves, never undone; the tank leg is the reversible one).</summary>
		public static RM_TransferLeg SpillLeg(Map map, IntVec3 outlet, FluidDef fluid, Source from)
		{
			RM_MapComponent_Sheet sheet = Of(map);
			return RM_TransferLeg.World(
				k => sheet != null && sheet.Probe(outlet, k, fluid, from) == k,
				k => sheet != null && sheet.Offer(outlet, k, fluid, from) == k);
		}

		// ── the pulse ──

		/// <summary>Called from RM_MapComponent_Excavation.DoPulse, before the channel solve (so water that runs back is
		/// levelled the same pulse). Runs whether or not the switch is on: water already standing keeps draining (D7).</summary>
		public void EnginePulse()
		{
			if (state == null)
			{
				return;
			}
			if (state.WetCount == 0)
			{
				// GPT deep review 2026-10-22 #8: the cells that dried LAST (Dry all, burnt out, drained) are reported by the next
				// pulse, which never comes on a dry map; flush them here so their path cost and picture follow
				foreach (var (cell, _) in state.Dried)
				{
					IntVec3 c = map.cellIndices.IndexToCell(cell);
					map.mapDrawer.MapMeshDirty(c, MapMeshFlagDefOf.Terrain);
					map.pathing?.RecalculatePerceivedPathCostAt(c);
				}
				state.Dried.Clear();
				return;
			}
			long t0 = System.Diagnostics.Stopwatch.GetTimestamp();
			long mem0 = GC.GetTotalMemory(false);
			Ensure();
			RefreshAround();
			HandOverTakenCells();
			NoteNonWater();
			long k0 = System.Diagnostics.Stopwatch.GetTimestamp();
			RM_SheetMath.Pulse(state, world, prm, rep);
			long k1 = System.Diagnostics.Stopwatch.GetTimestamp();
			foreach (var (cell, _, _) in rep.TierChanged)
			{
				IntVec3 c = map.cellIndices.IndexToCell(cell);
				map.mapDrawer.MapMeshDirty(c, MapMeshFlagDefOf.Terrain);
				map.pathing?.RecalculatePerceivedPathCostAt(c);   // Stage 2: the wading cost follows the tier
				perfDirty++;
			}
			Effects();
			// perf (§6 item 12: kernel and whole pulse recorded separately; RM_SheetProofs.ProofSheetPerf reads these)
			long t1 = System.Diagnostics.Stopwatch.GetTimestamp();
			double tick = 1000.0 / System.Diagnostics.Stopwatch.Frequency;
			perfPulses++;
			perfKernelMs += (k1 - k0) * tick;
			double ms = (t1 - t0) * tick;
			perfPulseMs += ms;
			perfMaxPulseMs = Math.Max(perfMaxPulseMs, ms);
			perfAllocB += Math.Max(0, GC.GetTotalMemory(false) - mem0);
			perfWetMax = Math.Max(perfWetMax, state.WetCount);
		}

		// ── Stage 2 effects (D3 crops and irrigation, pawns, fire): read from the grid, never from a picture (§6 item 2) ──

		private static readonly List<IntVec3> soakCells = new List<IntVec3>();
		private static Func<Map, IEnumerable<IntVec3>, int, int> soakApi;
		private static bool soakLooked;

		/// <summary>ExplosiveGrowthAPI.SoakCells found by name (no hard reference: FlowWorks does not depend on Explosive Growth).
		/// Null when that mod is not loaded.</summary>
		public static Func<Map, IEnumerable<IntVec3>, int, int> SoakApi
		{
			get
			{
				if (!soakLooked)
				{
					soakLooked = true;
					try
					{
						Type t = GenTypes.GetTypeInAnyAssembly("RimMandrake.ExplosiveGrowth.ExplosiveGrowthAPI");
						System.Reflection.MethodInfo m = t?.GetMethod("SoakCells", new[] { typeof(Map), typeof(IEnumerable<IntVec3>), typeof(int) });
						if (m != null)
						{
							soakApi = (Func<Map, IEnumerable<IntVec3>, int, int>)Delegate.CreateDelegate(typeof(Func<Map, IEnumerable<IntVec3>, int, int>), m);
						}
					}
					catch (Exception e)
					{
						Log.Warning("[RimMandrake.FlowWorks] spilled water could not find Explosive Growth's soak (" + e.Message + "); it will not irrigate.");
					}
				}
				return soakApi;
			}
		}

		/// <summary>How long one pulse's soak keeps a square watered (Explosive Growth reads it as irrigated).</summary>
		public const int IrrigateTicks = 15000;

		private void Effects()
		{
			// D3: a crop under standing overflow for the whole delay drowns (the kernel's timer fired this pulse); a readable sign
			if (RM_SheetSettings.cropsDrownEnabled && rep.CropKilled.Count > 0)
			{
				int killed = 0;
				IntVec3 at = IntVec3.Invalid;
				foreach (int k in rep.CropKilled)
				{
					IntVec3 c = map.cellIndices.IndexToCell(k);
					Plant plant = c.GetPlant(map);
					if (plant != null && !plant.Destroyed && plant.def.plant != null && !plant.def.plant.IsTree)
					{
						plant.Kill();
						killed++;
						at = c;
					}
				}
				if (killed > 0)
				{
					Messages.Message("Standing water drowned " + killed + " plant" + (killed == 1 ? "" : "s") + " after "
						+ (prm.CropKillPulses * (float)RimMandrakeFlowWorksSettings.PulseIntervalTicks / GenDate.TicksPerDay).ToString("0.#")
						+ " days under it.", new TargetInfo(at, map), MessageTypeDefOf.NegativeEvent, false);
				}
			}
			// D3: water that soaked in irrigates (water only: another liquid soaking in waters nothing)
			if (RM_SheetSettings.irrigateEnabled && rep.Soaked.Count > 0 && SoakApi != null)
			{
				soakCells.Clear();
				foreach (var (k, _) in rep.Soaked)
				{
					if (!nonWater.Contains(k))
					{
						soakCells.Add(map.cellIndices.IndexToCell(k));
					}
				}
				try
				{
					irrigatedTotal += SoakApi(map, soakCells, IrrigateTicks);
				}
				catch (Exception e)
				{
					soakApi = null;
					Log.Warning("[RimMandrake.FlowWorks] Explosive Growth's soak failed (" + e.Message + "); spilled water stops irrigating.");
				}
			}
			// pawns: SoakingWet at sheet depth (vanilla's floodwater thought); the path cost is the PathGrid postfix
			if (RM_SheetSettings.pawnEffectsEnabled && ThoughtDefOf.SoakingWet != null)
			{
				IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
				for (int i = 0; i < pawns.Count; i++)
				{
					Pawn p = pawns[i];
					// GPT deep review 2026-10-22 #6: the mood guard used to skip the whole pawn, so animals (no mood memories)
					// waded poisoned spills untouched; it now guards the thought only
					if (p.Flying)
					{
						continue;
					}
					Tier t = TierAt(p.Position);
					if (t == Tier.Sheet || t == Tier.Pool)
					{
						FluidDef f = FluidAt(p.Position);
						if (!Burnable(f) && p.needs?.mood?.thoughts?.memories != null)
						{
							p.needs.mood.thoughts.memories.TryGainMemoryFast(ThoughtDefOf.SoakingWet);
						}
						// all liquids: a poisoned spill builds toxins as the canal does (RM_FillEffectMath.ToxinPerCheck, fill = dL / notch)
						if (f != null && f.toxicPerDayAtBrim > 0f && HediffDefOf.ToxicBuildup != null)
						{
							float add = RM_FillEffectMath.ToxinPerCheck(DlAt(p.Position) / (float)RM_LevelSolve.U, 1, f.toxicPerDayAtBrim,
								p.GetStatValue(StatDefOf.ToxicEnvironmentResistance), p.Flying)
								* RimMandrakeFlowWorksSettings.PulseIntervalTicks / (float)RM_FillEffectMath.IntervalTicks;
							if (add > 0f)
							{
								HealthUtility.AdjustSeverity(p, HediffDefOf.ToxicBuildup, add);
							}
						}
					}
				}
			}
			// fire: a sheet of a liquid that does not burn puts it out; a fuel sheet never does (it burns, RM_SheetFire.cs)
			if (RM_SheetSettings.putsOutFireEnabled)
			{
				List<Thing> fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
				for (int i = fires.Count - 1; i >= 0; i--)
				{
					Thing f = fires[i];
					if (f.Spawned && f is Fire fire && fire.parent == null && StandingDlAt(map, f.Position) >= prm.RetentionDl
						&& RM_SheetFluidMath.PutsOutFire(Burnable(FluidAt(f.Position))))
					{
						f.Destroy();
					}
				}
			}
		}

		private long irrigatedTotal;
		private bool toldOverflow;

		/// <summary>The readable sign (§4 stage 2): the first spill on a map says so, once per map (saved).</summary>
		private void TellOverflowOnce(IntVec3 origin, Source from, FluidDef fluid)
		{
			if (toldOverflow)
			{
				return;
			}
			toldOverflow = true;
			string what = from == Source.Pump ? "A pump is pouring into a full channel" : from == Source.Rain ? "Rain is filling a full channel"
				: from == Source.FillIn ? "Filling a channel in squeezed water out" : from == Source.Gravity ? "A tank is draining into a full channel"
				: "Released water reached a full channel";
			Messages.Message(what + ": the channel is overflowing and " + (fluid == Water || fluid == null ? "water" : fluid.label)
				+ " is spilling onto the ground.", new TargetInfo(origin, map),
				MessageTypeDefOf.CautionInput, false);
		}

		/// <summary>Liquid sheet water standing on <paramref name="c"/> in dL (0 when frozen: ice is not water to wade or drown in).</summary>
		public static int StandingDlAt(Map map, IntVec3 c)
		{
			if (anyWet <= 0)
			{
				return 0;
			}
			RM_MapComponent_Sheet s = Of(map);
			return s == null || s.TierAt(c) == Tier.Ice ? 0 : s.DlAt(c);
		}

		/// <summary>The wading cost the PathGrid postfix adds: 0 dry or film, the setting at sheet tier, twice it in a pool.</summary>
		public static int PathCostAt(Map map, IntVec3 c)
		{
			if (anyWet <= 0 || !RM_SheetSettings.pawnEffectsEnabled)
			{
				return 0;
			}
			RM_MapComponent_Sheet s = Of(map);
			if (s == null)
			{
				return 0;
			}
			Tier t = s.TierAt(c);
			return t == Tier.Sheet ? RM_SheetSettings.sheetPathCost : t == Tier.Pool ? 2 * RM_SheetSettings.sheetPathCost : 0;
		}

		/// <summary>Squares of spilled water on every map: the cheap gate the path-cost postfix reads before any map lookup.</summary>
		private static int anyWet;
		private static Game anyWetGame;
		private int countedWet;

		public override void MapComponentTick()
		{
			FireTick();
			// a game torn down by loading another save never calls MapRemoved (review 2026-10-22): the old game's count would keep
			// the gate open forever, sending every path-cost query through a component lookup; a new Game starts it from zero
			if (anyWetGame != Current.Game)
			{
				anyWetGame = Current.Game;
				anyWet = 0;
			}
			// keep the global gate in step with this map (cheap: one int compare a tick)
			int w = state?.WetCount ?? 0;
			if (w != countedWet)
			{
				anyWet += w - countedWet;
				countedWet = w;
			}
		}

		public override void MapRemoved()
		{
			anyWet -= countedWet;
			countedWet = 0;
			base.MapRemoved();
		}

		// ── D2 gravity feed: a Dump tank (it stands above the ground, so its head is above the brim) keeps pushing into a full
		// channel; what the channel cannot take spills over its lip ──

		/// <summary>dL a gravity feed at the full channel square <paramref name="end"/> could spill now (exact probe, nothing moves).</summary>
		public static long GravityProbe(Map map, IntVec3 end, long dl, FluidDef fluid)
		{
			RM_MapComponent_Sheet s = Of(map);
			RM_MapComponent_Excavation e = map?.GetComponent<RM_MapComponent_Excavation>();
			if (s == null || e == null || !e.IsExcavated(end) || e.FluidAt(end) != fluid || e.WaterDlAt(end) < e.DepthAt(end) * (long)RM_LevelSolve.U)
			{
				return 0;
			}
			return s.Probe(end, dl, fluid, Source.Gravity);
		}

		// ── perf counters (RM_SheetProofs.ProofSheetPerf) ──
		internal int perfPulses, perfDirty, perfWetMax;
		internal double perfKernelMs, perfPulseMs, perfMaxPulseMs;
		internal long perfAllocB;

		internal void PerfReset()
		{
			perfPulses = perfDirty = perfWetMax = 0;
			perfKernelMs = perfPulseMs = perfMaxPulseMs = 0;
			perfAllocB = 0;
		}

		// ── proof accessors (RM_SheetProofs) ──
		internal State ProofState => state;
		internal Params ProofParams { get { Ensure(); return prm; } }
		internal long IrrigatedTotal => irrigatedTotal;

		/// <summary>What the kernel takes this square to be now (classified fresh from the authoritative layers).</summary>
		internal Kind KindAt(IntVec3 c)
		{
			Ensure();
			int i = map.cellIndices.CellToIndex(c);
			Classify(i);
			return world.Kinds[i];
		}

		/// <summary>A wet square the engine now owns (dug under the sheet, a pond under it) hands its water over: into the
		/// channel or pond through the engine's own credit, into a limitless body as "joined the lake". What the engine cannot
		/// take stays on the square (it flows on from there, or dries).</summary>
		private void HandOverTakenCells()
		{
			var taken = new List<int>();
			foreach (int k in state.Occ)
			{
				if (world.Kinds[k] == Kind.Receiver || world.Kinds[k] == Kind.Sink)
				{
					taken.Add(k);
				}
			}
			foreach (int k in taken)
			{
				if (world.Kinds[k] == Kind.Sink)
				{
					byte bf = world.BodyFluid[k];
					if (bf == 0 || bf == state.Fluid[k])
					{
						HandOver(state, k, state.Dl[k], true);
					}
					continue; // another liquid's lake never takes it (it dries where it lies)
				}
				if (world.BodyFluid[k] != 0 && world.BodyFluid[k] != state.Fluid[k])
				{
					continue;
				}
				int got = Credit(k, state.Dl[k], state.Fluid[k]);
				if (got > 0)
				{
					HandOver(state, k, got, false);
				}
			}
		}

		// ── readouts, purge, ledger ──

		/// <summary>The tier to DRAW: the kernel's (with hysteresis), or for a square spilled since the last pulse the tier its
		/// dL calls for (read-only: the kernel's own state is never touched outside the kernel).</summary>
		public Tier TierAt(IntVec3 c)
		{
			if (state == null || !c.InBounds(map))
			{
				return Tier.None;
			}
			int i = map.cellIndices.CellToIndex(c);
			Tier t = state.Tiers[i];
			return t == Tier.None && state.Dl[i] > 0 ? NextTier(Tier.None, state.Dl[i], prm) : t;
		}

		public int DlAt(IntVec3 c) => state == null || !c.InBounds(map) ? 0 : state.Dl[map.cellIndices.CellToIndex(c)];

		/// <summary>The liquid spilled on <paramref name="c"/>, or null (dry, or a liquid gone from the mod set).</summary>
		public FluidDef FluidAt(IntVec3 c) => state == null || !c.InBounds(map) ? null : FluidOf(state.Fluid[map.cellIndices.CellToIndex(c)]);

		public static bool Burnable(FluidDef f) => f != null && f.fireKind != RM_FluidFireKind.None;

		/// <summary>Squares holding a liquid other than water before this pulse (what they soak in irrigates nothing).</summary>
		private readonly HashSet<int> nonWater = new HashSet<int>();

		private void NoteNonWater()
		{
			nonWater.Clear();
			int w = fluids.IndexOf(Water) + 1; // 0 when water never spilled here: every wet square is another liquid
			foreach (int k in state.Occ)
			{
				if (state.Fluid[k] != w)
				{
					nonWater.Add(k);
				}
			}
		}

		/// <summary>The mouseover line for a wet undug square: "Spilled water 1.2 cm (24 L)", or "… frozen".</summary>
		public static string ReadoutAt(Map map, IntVec3 c)
		{
			RM_MapComponent_Sheet s = Of(map);
			int dl = s?.DlAt(c) ?? 0;
			if (dl <= 0)
			{
				return null;
			}
			string what = (s.FluidOf(s.state.Fluid[map.cellIndices.CellToIndex(c)])?.label ?? "liquid").CapitalizeFirst();
			string depth = (dl / (double)DlPerCm).ToString(dl < 10 * DlPerCm ? "0.0" : "0", System.Globalization.CultureInfo.InvariantCulture);
			return "Spilled " + what.ToLowerInvariant() + " " + depth + " cm (" + RM_Volume.FormatLitres(dl / (double)RM_Volume.UnitsPerLitre) + ")"
				+ (s.TierAt(c) == Tier.Ice ? ", frozen" : s.IsBurning(c) ? ", burning" : "");
		}

		public string LedgerLine()
		{
			if (state == null)
			{
				long rl = Engine?.ReleaseLostDl ?? 0;
				return "no spilled liquid" + (rl > 0 ? "; released floods with nowhere to go lost "
					+ RM_Volume.FormatLitres(rl / (double)RM_Volume.UnitsPerLitre) : "") + ".";
			}
			string L(long dl) => RM_Volume.FormatLitres(dl / (double)RM_Volume.UnitsPerLitre);
			// owner card 2026-10-22 "Count silently, show in ledger": a release's lost remainder is shown here, never messaged
			long releaseLost = Engine?.ReleaseLostDl ?? 0;
			return "spilled " + L(state.TotalIn) + "; standing " + L(state.Standing) + " on " + state.WetCount + " squares; ran back "
				+ L(state.Returned) + ", joined lakes " + L(state.JoinedLake) + ", soaked " + L(state.Soaked) + ", dried "
				+ L(state.Evaporated) + ", burned " + L(state.Burned) + ", dried by hand " + L(state.Purged)
				+ (state.LedgerCloses ? "" : " (LEDGER OPEN: a bug)")
				+ "; released floods with nowhere to go lost " + L(releaseLost);
		}

		/// <summary>"Dry all spilled water now": a DISCLOSED purge (D7), never silent.</summary>
		public void DryAll()
		{
			if (state == null || state.WetCount == 0)
			{
				return;
			}
			var cells = new List<int>(state.Occ);
			long dl = PurgeAll(state);
			foreach (int k in cells)
			{
				map.mapDrawer.MapMeshDirty(map.cellIndices.IndexToCell(k), MapMeshFlagDefOf.Terrain);
			}
			Messages.Message("Dried all spilled water on this map by hand: " + RM_Volume.FormatLitres(dl / (double)RM_Volume.UnitsPerLitre)
				+ " removed (counted as dried by hand).", MessageTypeDefOf.NeutralEvent, false);
		}

		// ── persistence (§6 item 4) ──

		public override void ExposeData()
		{
			base.ExposeData();
			byte[] data = Scribe.mode == LoadSaveMode.Saving && state != null && (state.WetCount > 0 || state.TotalIn > 0) ? Save(state) : null;
			if (Scribe.mode != LoadSaveMode.Saving || data != null)
			{
				DataExposeUtility.LookByteArray(ref data, "RM_sheetState");
			}
			Scribe_Collections.Look(ref fluids, "RM_sheetFluids", LookMode.Def);
			Scribe_Values.Look(ref toldOverflow, "RM_sheetToldOverflow", false);
			Scribe_Values.Look(ref irrigatedTotal, "RM_sheetIrrigated", 0L);
			ExposeFire();
			if (Scribe.mode == LoadSaveMode.LoadingVars && data != null)
			{
				try
				{
					state = Load(data);
				}
				catch (Exception e)
				{
					Log.Error("[RimMandrake.FlowWorks] spilled-water state in this save could not be read (" + e.Message
						+ "); the map starts with no spilled water. This is a lost record, not flow.");
					state = null;
				}
			}
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				if (fluids == null)
				{
					fluids = new List<FluidDef>();
				}
				if (fluids.Contains(null))
				{
					Log.Warning("[RimMandrake.FlowWorks] a spilled liquid recorded in this save no longer exists in the loaded mod set; "
						+ "its squares keep their litres and drain as before.");
				}
			}
		}
	}
}
