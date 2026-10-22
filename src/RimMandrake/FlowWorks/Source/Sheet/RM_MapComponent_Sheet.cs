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
	/// - <b>Losses</b> (D6, disclosed): soak by the base ground's class, evaporation by temperature and roof. PROVISIONAL
	///   rates (constants below), to be tuned at Stage 3/4.
	/// - <b>Picture</b>: overlay only (§6 item 2): <see cref="SectionLayer_RMSheetWater"/>. No temp terrain is written, so
	///   nothing vanilla (crop kill, filth wash, fire, path cost) happens yet — those are Stage 2 effects.
	///
	/// Water only in Stage 1 (§6 item 10). Saved: the kernel's whole continuation state (§6 item 4) plus this map's sheet
	/// fluid palette (its own, never the engine's compacting palette).</summary>
	public class RM_MapComponent_Sheet : MapComponent
	{
		// PROVISIONAL loss rates (cm a day), per ground class / weather, never per biome (§3 step 4). Not owner-ruled.
		public const float SoakCmPerDaySand = 4f, SoakCmPerDaySoil = 2f, SoakCmPerDayGravel = 1f;
		public const float EvapCmPerDayAt20C = 0.5f, EvapRoofedFactor = 0.3f, EvapMaxFactor = 3f;
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
			prm.CropKillPulses = PulsesFor(TicksPerWeek, RimMandrakeFlowWorksSettings.PulseIntervalTicks);
			for (int k = 0; k < fluids.Count; k++)
			{
				FluidDef f = fluids[k];
				world.Fluids[k + 1] = new FluidRule
				{
					InfiltrationPermille = 1000,
					EvaporationPermille = 1000,
					FreezeDeciC = 0,
					NeverFreezes = f != Water, // Stage 1 carries water only; other fluids' rules arrive with them
				};
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

		private void Classify(int idx)
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
				bool ok = !RM_FlowDoorRules.SealsLiquid(edifice) && (held == null || held == Water);
				world.Kinds[idx] = ok ? Kind.Receiver : Kind.Blocked;
				if (ok)
				{
					world.RoomDl[idx] = int.MaxValue / 4; // the engine's pour decides (World.Credit)
					world.BodyFluid[idx] = held == null ? (byte)0 : Key(Water);
				}
				return;
			}
			RM_LiquidBody body = e?.Stock?.IndexedBodyAt(map, c);
			if (body != null)
			{
				FluidDef bf = body.fluid ?? e.ActiveFluid;
				if (bf != Water)
				{
					world.Kinds[idx] = Kind.Blocked; // a foreign body refuses (fluids never mix)
					return;
				}
				world.Kinds[idx] = body.limitless ? Kind.Sink : Kind.Receiver;
				world.RoomDl[idx] = int.MaxValue / 4; // the return leg decides (World.Credit)
				world.BodyFluid[idx] = Key(Water);
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
			float evapCm = t <= 0f ? 0f : EvapCmPerDayAt20C * Mathf.Min(EvapMaxFactor, t / 20f)
				* (map.roofGrid.Roofed(c) ? EvapRoofedFactor : 1f);
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
				return SoakCmPerDaySand;
			}
			if (t.fertility >= 0.5f)
			{
				return SoakCmPerDaySoil;
			}
			return t.fertility > 0f ? SoakCmPerDayGravel : 0f; // fertility 0: rock, smooth stone
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
		private int[] FindLips(IntVec3 origin)
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
						if (!RM_FlowDoorRules.SealsLiquid(map.edificeGrid[n]) && (held == null || held == Water))
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

		/// <summary>The master switch, the per-inflow switch (stage 3), the depth engine, and a carried fluid (water only).</summary>
		private bool Accepts(FluidDef fluid, Source from) =>
			RM_SheetSettings.SpillsFrom(from) && RimMandrakeFlowWorksSettings.depthEngineEnabled && fluid != null && fluid == Water;

		private SpillOffer MakeOffer(IntVec3 origin, long dl, FluidDef fluid, Source from)
		{
			Ensure();
			return new SpillOffer
			{
				LipNearestFirst = FindLips(origin),
				AmountDl = (int)Math.Min(dl, int.MaxValue / 2),
				Fluid = Key(fluid),
				From = from,
			};
		}

		/// <summary>How many of <paramref name="dl"/> a spill at <paramref name="origin"/> would place now, changing no water.
		/// 0 when the switch is off or the fluid is not carried (Stage 1: water only).</summary>
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
			out IntVec3 outlet)
		{
			outlet = IntVec3.Invalid;
			RM_MapComponent_Sheet sheet = Of(map);
			if (sheet == null || !sheet.Accepts(Water, Source.Pump))
			{
				return false;
			}
			for (int c = 0; c < cells.Count; c++)
			{
				if (cd[c].room > 0 || !cd[c].wet || cd[c].fill != Water)
				{
					continue;
				}
				if (sheet.Probe(cells[c], units, Water, Source.Pump) == units)
				{
					outlet = cells[c];
					return true;
				}
			}
			return false;
		}

		/// <summary>The pump hook (D2), part 2: the sheet at <paramref name="outlet"/>'s lip as the destination leg of a
		/// transfer (checked by the exact probe before anything moves, never undone; the tank leg is the reversible one).</summary>
		public static RM_TransferLeg SpillLeg(Map map, IntVec3 outlet, Source from)
		{
			RM_MapComponent_Sheet sheet = Of(map);
			return RM_TransferLeg.World(
				k => sheet != null && sheet.Probe(outlet, k, Water, from) == k,
				k => sheet != null && sheet.Offer(outlet, k, Water, from) == k);
		}

		// ── the pulse ──

		/// <summary>Called from RM_MapComponent_Excavation.DoPulse, before the channel solve (so water that runs back is
		/// levelled the same pulse). Runs whether or not the switch is on: water already standing keeps draining (D7).</summary>
		public void EnginePulse()
		{
			if (state == null || state.WetCount == 0)
			{
				return;
			}
			Ensure();
			RefreshAround();
			HandOverTakenCells();
			RM_SheetMath.Pulse(state, world, prm, rep);
			foreach (var (cell, _, _) in rep.TierChanged)
			{
				map.mapDrawer.MapMeshDirty(map.cellIndices.IndexToCell(cell), MapMeshFlagDefOf.Terrain);
			}
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
					HandOver(state, k, state.Dl[k], true);
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
				+ (s.TierAt(c) == Tier.Ice ? ", frozen" : "");
		}

		public string LedgerLine()
		{
			if (state == null)
			{
				return "no spilled water.";
			}
			string L(long dl) => RM_Volume.FormatLitres(dl / (double)RM_Volume.UnitsPerLitre);
			return "spilled " + L(state.TotalIn) + "; standing " + L(state.Standing) + " on " + state.WetCount + " squares; ran back "
				+ L(state.Returned) + ", joined lakes " + L(state.JoinedLake) + ", soaked " + L(state.Soaked) + ", dried "
				+ L(state.Evaporated) + ", dried by hand " + L(state.Purged) + (state.LedgerCloses ? "" : " (LEDGER OPEN: a bug)");
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
