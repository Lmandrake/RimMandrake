using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>Where liquid leaving the network at an Outflow hose end goes (rev 2 §3.5).</summary>
	/// <remarks>Body (POND_RETURN_LEG_BUILD_WATER_GOES_HOME): a natural pond square or its dry bed takes the level back
	/// into the pond's stock, whole levels only. Appended last so the older values keep their numbers.</remarks>
	public enum RM_OutletKind { Blocked, Channel, Ground, Body }

	/// <summary>
	/// Liquid networks L7 (rev 2 §3.5, §3.7): the world side of an Outflow end, and the spill. A level of a liquid with a channel
	/// form goes into an excavated cell at the end or the best one within 1.5 cells (RM_PumpMath.PickPour, A14); dry open ground
	/// takes any liquid as a spill: its filth (LiquidDef.spillFilth, else RM_Filth_LiquidSpill), one per litresPerFilth litres,
	/// cleanable by colonists in the home area. A full or foreign channel, or a wall, is BLOCKED and moves nothing. Filth is a
	/// world record of the spill, never converted back into liquid units.
	/// Spilled WATER is real water (owner 2026-10-18 on HOSE_LEFTOVER_FIX_NO_VANISHING_LITRES: <i>"it's not just filth, it's
	/// spilled water as per wetting the ground, plant growth"</i>): fresh water's spillFilth is Explosive Growth's
	/// RM_Filth_WaterSpill (its patch Patches/FlowWorks/RM_EG_FreshWaterSpillFilth.xml), a wet source plants on the cell
	/// drink (RM_WetSources.SpillFilthSource), so a hose's leftover on dry ground waters the ground it lands on.
	/// </summary>
	public static class RM_LiquidSpill
	{
		/// <summary>State read (probe, selftests): units spilled as filth this session, and spills no cell would take (logged).</summary>
		public static int SpilledUnits, Unplaced;

		/// <summary>What an Outflow end at <paramref name="end"/> does with <paramref name="liquid"/> (<paramref name="fluid"/> is
		/// its channel form, if any): pour into <paramref name="cell"/>, spill there, or nothing.</summary>
		public static RM_OutletKind Outlet(Map map, RM_MapComponent_Excavation ex, IntVec3 end, LiquidDef liquid, FluidDef fluid, out IntVec3 cell)
		{
			cell = IntVec3.Invalid;
			if (map == null || !end.InBounds(map) || (liquid == null && fluid == null))
			{
				return RM_OutletKind.Blocked;
			}
			fluid = fluid ?? liquid?.canalFluid;
			// HOSE_SPILL_MEND_POND_GETS_NOTHING (C1-F12): an end under a wall or a building pours nowhere, not into the cells beside it
			Building onEnd = end.GetEdifice(map);
			if (onEnd != null && onEnd.def.passability == Traversability.Impassable)
			{
				return RM_OutletKind.Blocked;
			}
			if (ex != null && fluid != null)
			{
				var cells = new List<IntVec3>();
				var cd = new List<(int room, bool wet, FluidDef fill)>();
				foreach (IntVec3 c in new[] { end }.Concat(GenAdj.CellsAdjacent8Way(new TargetInfo(end, map))))
				{
					// PUMP_CANAL_FEED_FIX_ONE_NOTCH_ONLY: exact-level water: any room in the canal the square joins (a sheet's canal
					// has no whole notch in any one square); whole-notch water: a whole notch in the square
					if (c.InBounds(map) && (RM_MapComponent_Excavation.LevelExact ? ex.PourRoomDl(c, fluid, 1) > 0 : ex.CanPourLevel(c, fluid)))
					{
						cells.Add(c);
						cd.Add((ex.DepthAt(c) - ex.FillAt(c), ex.FillAt(c) > 0, ex.FluidAt(c)));
					}
				}
				var tk = new List<(bool canProvide, FluidDef fluid)> { (true, fluid) };
				if (RM_PumpMath.PickPour(tk, cd, out _, out int ci))
				{
					cell = cells[ci];
					return RM_OutletKind.Channel;
				}
				// POND_RETURN_LEG_BUILD_WATER_GOES_HOME (G1): no dug cell takes it, but the pond (or its dried bed) it came
				// from may: the end square first, then its neighbours in the fixed adjacency order.
				foreach (IntVec3 c in new[] { end }.Concat(GenAdj.CellsAdjacent8Way(new TargetInfo(end, map))))
				{
					if (c.InBounds(map) && ex.CanReturnLevels(c, fluid, 1))
					{
						cell = c;
						return RM_OutletKind.Body;
					}
				}
			}
			// a full or foreign channel, or a wall: blocked; dry open ground takes a spill
			if ((ex != null && ex.IsExcavated(end)) || !end.Standable(map) || end.GetTerrain(map).IsWater)
			{
				return RM_OutletKind.Blocked;
			}
			cell = end;
			return RM_OutletKind.Ground;
		}

		/// <summary>The world leg for an outlet <paramref name="kind"/> at <paramref name="cell"/>: a channel cell takes a level, a
		/// pond takes a whole level back into its stock (all or nothing), dry ground takes the units as a spill. One place, so
		/// the pump's world-to-world move, its pour and the Dump drain all route the same way.</summary>
		public static RM_TransferLeg OutletLeg(Map map, RM_MapComponent_Excavation ex, RM_OutletKind kind, IntVec3 cell, LiquidDef liquid, FluidDef fluid)
		{
			switch (kind)
			{
				case RM_OutletKind.Channel:
					// k is tank units = decilitres (a level is RM_Volume.UnitsPerLevel): the pour spreads over the canal it joins
					return RM_TransferLeg.World(k => ex.PourRoomDl(cell, fluid, k) >= k, k => ex.TryPourDl(cell, fluid, k));
				case RM_OutletKind.Body:
					return RM_TransferLeg.World(k => BodyRoomDl(ex, cell, fluid, k) >= k, k => BodyTake(ex, cell, fluid, k));
				default:
					return RM_TransferLeg.Sink(k => Spill(map, cell, liquid, k));
			}
		}

		/// <summary>PUMP_CANAL_FEED_FIX_ONE_NOTCH_ONLY: the decilitres (tank units) an outlet <paramref name="kind"/> at
		/// <paramref name="cell"/> would take now, up to <paramref name="want"/>: a canal its room (the square, then the squares
		/// it joins), a pond its room, dry ground anything (a spill), blocked nothing.</summary>
		public static long OutletRoomDl(RM_MapComponent_Excavation ex, RM_OutletKind kind, IntVec3 cell, FluidDef fluid, long want)
		{
			switch (kind)
			{
				case RM_OutletKind.Channel:
					return ex.PourRoomDl(cell, fluid, want);
				case RM_OutletKind.Body:
					return BodyRoomDl(ex, cell, fluid, want);
				case RM_OutletKind.Ground:
					return want;
				default:
					return 0;
			}
		}

		/// <summary>A pond's room in dL (exact-level), or one whole level or nothing (whole-notch water).</summary>
		private static long BodyRoomDl(RM_MapComponent_Excavation ex, IntVec3 cell, FluidDef fluid, long want)
		{
			if (RM_MapComponent_Excavation.LevelExact)
			{
				return ex.ReturnRoomDl(cell, fluid, want);
			}
			int level = RM_PumpMath.TankUnitsPerLevel;
			return want >= level && ex.CanReturnLevels(cell, fluid, (int)(want / level)) ? want - want % level : 0;
		}

		private static bool BodyTake(RM_MapComponent_Excavation ex, IntVec3 cell, FluidDef fluid, long dl)
		{
			if (RM_MapComponent_Excavation.LevelExact)
			{
				return ex.TryReturnDl(cell, fluid, dl);
			}
			int level = RM_PumpMath.TankUnitsPerLevel;
			return dl % level == 0 && ex.TryReturnLevels(cell, fluid, (int)(dl / level));
		}

		/// <summary>True when the outlet takes whole levels only (a channel or a pond), false for a spill.</summary>
		public static bool WholeLevels(RM_OutletKind kind) => kind == RM_OutletKind.Channel || kind == RM_OutletKind.Body;

		/// <summary>State read: units hoses emptied when they stopped carrying (L8).</summary>
		public static int DrainedUnits;

		/// <summary>Where a stopped hose empties (rev 2 §3.7): out of its free end when it has one, else at the reel.</summary>
		public static IntVec3 DrainCell(Hose.CompHoseReel r, Map map)
		{
			if (r?.parent == null)
			{
				return IntVec3.Invalid;
			}
			IntVec3 end = r.EndCell;
			bool free = end.IsValid && map != null && map.GetComponent<Hose.RM_MapComponent_Hoses>()?.RelayOf(r) == null && Hose.HosePorts.FindAt(map, end, r.parent, out _, out _) == null;
			return free ? end : r.parent.Position;
		}

		/// <summary>L8 (rev 2 §3.7): a hose that stops carrying empties what it holds at <paramref name="cell"/> (its free end, else
		/// the reel): whole levels into a channel that takes them, the rest as a spill; never back into a tank. Conserved: the units
		/// leave the hose's ledger through the transfer service.</summary>
		public static void DrainHeld(Hose.CompHoseReel r, Map map, IntVec3 cell)
		{
			if (r == null || r.heldUnits <= 0)
			{
				return;
			}
			LiquidDef liquid = r.heldLiquid;
			if (map == null || !cell.IsValid)
			{
				// off any map (a reel taken off it): nowhere to put it; said once, never silent
				Log.WarningOnce("[FlowWorks] a hose holding " + r.heldUnits + " " + liquid?.defName + " left the map; the liquid went with it", 0x5B1118);
				object hl0 = liquid;
				RM_HoseHold.Drain(ref hl0, ref r.heldUnits, null);
				r.heldLiquid = null;
				return;
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			int units = r.heldUnits;
			int held = r.heldUnits;
			// the hose's ledger as the source leg; the world (channel levels, then a spill) as the sink
			RM_TransferLeg hose = RM_TransferLeg.Store(k => held >= k, k => { held -= k; return true; }, k => { held += k; return true; });
			RM_TransferLeg world = RM_TransferLeg.Sink(k => PlaceHeld(map, ex, cell, liquid, k));
			if (RM_LiquidTransfer.Move(units, hose, world, out _) == units)
			{
				DrainedUnits += units;
			}
			r.heldUnits = held;
			if (held <= 0)
			{
				r.heldLiquid = null;
			}
		}

		/// <summary>Held liquid reaching the world (HOSE_LEFTOVER_FIX_NO_VANISHING_LITRES): into the water it lands in first, in
		/// DECILITRES (a canal at or beside <paramref name="cell"/>, spreading over the squares it joins; or the pond there,
		/// C1-F10), then <see cref="Spill"/> for the rest, which never lets a litre leave unannounced.</summary>
		private static void PlaceHeld(Map map, RM_MapComponent_Excavation ex, IntVec3 cell, LiquidDef liquid, int units)
		{
			units -= PlaceInWater(map, ex, cell, liquid, units);
			if (units > 0)
			{
				Spill(map, cell, liquid, units);
			}
		}

		/// <summary>Put up to <paramref name="units"/> (dL) of <paramref name="liquid"/> into the canal or pond at or beside
		/// <paramref name="cell"/> (the outlet's own choice of square, repeated while one takes more). Returns the units placed.</summary>
		private static int PlaceInWater(Map map, RM_MapComponent_Excavation ex, IntVec3 cell, LiquidDef liquid, int units)
		{
			FluidDef fluid = liquid?.canalFluid;
			if (ex == null || fluid == null || units <= 0 || map == null || !cell.IsValid)
			{
				return 0;
			}
			int placed = 0;
			for (int guard = 0; guard < 9 && units > placed; guard++)
			{
				RM_OutletKind kind = Outlet(map, ex, cell, liquid, fluid, out IntVec3 c);
				if (!WholeLevels(kind))
				{
					break;
				}
				long room = OutletRoomDl(ex, kind, c, fluid, units - placed);
				if (room <= 0)
				{
					break;
				}
				bool ok = kind == RM_OutletKind.Channel ? ex.TryPourDl(c, fluid, room) : BodyTake(ex, c, fluid, room);
				if (!ok)
				{
					break;
				}
				placed += (int)room;
			}
			return placed;
		}

		/// <summary>The squares searched for water to take liquid that would otherwise be lost (a spill over water or a wall,
		/// a filth that will not lie): the nearest canal or pond of the liquid within this radius.</summary>
		public const float HomeRadius = 6.9f;

		/// <summary>HOSE_LEFTOVER_FIX_NO_VANISHING_LITRES, the conserving default (owner 2026-10-18: a puddle IS an allowed
		/// destination, and for water it is spilled water that wets the ground and feeds plants): liquid no filth can record goes into the nearest canal or pond of its kind within
		/// <see cref="HomeRadius"/>, nearest first. Returns the units placed.</summary>
		private static int PlaceNearby(Map map, IntVec3 cell, LiquidDef liquid, int units)
		{
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			if (ex == null || liquid?.canalFluid == null || units <= 0 || !cell.InBounds(map))
			{
				return 0;
			}
			int placed = 0;
			int n = GenRadial.NumCellsInRadius(HomeRadius);
			for (int i = 0; i < n && placed < units; i++)
			{
				IntVec3 c = cell + GenRadial.RadialPattern[i];
				if (!c.InBounds(map))
				{
					continue;
				}
				FluidDef f = liquid.canalFluid;
				long room = ex.IsExcavated(c) ? ex.PourRoomDl(c, f, units - placed) : BodyRoomDl(ex, c, f, units - placed);
				if (room <= 0)
				{
					continue;
				}
				bool ok = ex.IsExcavated(c) ? ex.TryPourDl(c, f, room) : BodyTake(ex, c, f, room);
				if (ok)
				{
					placed += (int)room;
				}
			}
			return placed;
		}

		/// <summary>HOSE_LEFTOVER_FIX_FULL_CANAL_LOSS (live day 3, S3.c: the pump lifted a 7th level into a hose over a brim-full
		/// canal; the hose drained onto it, the canal and everything within <see cref="HomeRadius"/> was full, and 975 L were the
		/// announced loss though the pond it was drawn from had the room): every dug square and every pond body of the liquid's
		/// kind on the map is offered the rest, nearest first (RM_LevelPour.PlaceNearestFirst), so liquid with a home anywhere
		/// on the map lands; returning to the intake pond is the common case. Returns the units placed.</summary>
		private static int PlaceAnywhere(Map map, IntVec3 cell, LiquidDef liquid, int units)
		{
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			FluidDef f = liquid?.canalFluid;
			if (ex == null || f == null || units <= 0 || !cell.InBounds(map))
			{
				return 0;
			}
			var homes = new List<IntVec3>();
			var dist = new List<long>();
			foreach (IntVec3 c in ex.ExcavatedCells)
			{
				homes.Add(c);
				dist.Add((c - cell).LengthHorizontalSquared);
			}
			int dug = homes.Count;
			if (ex.Stock != null)
			{
				foreach (RM_LiquidBody b in ex.Stock.Bodies)
				{
					if (b == null || b.cells.Count == 0 || (b.fluid ?? ex.ActiveFluid) != f)
					{
						continue;
					}
					IntVec3 best = b.cells[0];
					long bd = long.MaxValue;
					foreach (IntVec3 c in b.cells)
					{
						long d = (c - cell).LengthHorizontalSquared;
						if (d < bd)
						{
							bd = d;
							best = c;
						}
					}
					homes.Add(best);
					dist.Add(bd);
				}
			}
			long placed = RM_LevelPour.PlaceNearestFirst(dist, (i, want) =>
			{
				IntVec3 c = homes[i];
				if (i < dug)
				{
					long room = ex.PourRoomDl(c, f, want);
					return room > 0 && ex.TryPourDl(c, f, room) ? room : 0;
				}
				long br = BodyRoomDl(ex, c, f, want);
				return br > 0 && BodyTake(ex, c, f, br) ? br : 0;
			}, units);
			if (placed > 0)
			{
				HomedFarUnits += (int)placed;
			}
			return (int)placed;
		}

		/// <summary>State read: units that found no home within HomeRadius and landed farther off (PlaceAnywhere).</summary>
		public static int HomedFarUnits;

		/// <summary>Spill <paramref name="units"/> of <paramref name="liquid"/> at <paramref name="cell"/> as filth (rev 2 §3.7):
		/// RM_LiquidNetKernel.FilthCount pieces of the liquid's spill filth, propagating to a neighbour where the cell refuses; the
		/// generic spill where its own filth will not lie; one warning if nothing would. Always "accepts" (a sink).</summary>
		public static void Spill(Map map, IntVec3 cell, LiquidDef liquid, int units)
		{
			if (map == null || units <= 0)
			{
				return;
			}
			// SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP (Q4: spilled liquid only): a spill on a grated deck over a dug square drains
			// into the hole below (stock conserved); no filth lies on the grate for what drained
			units -= (int)Pits.RM_GrateEffects.DrainSpill(map, cell, liquid?.canalFluid, units);
			if (units <= 0)
			{
				return;
			}
			// C1-F11: a spill over the liquid's own pond (no filth lies on water) goes back into the pond's stock first, never
			// out of the ledger
			units -= ReturnToPond(map, cell, liquid, units);
			if (units <= 0)
			{
				return;
			}
			// HOSE_LEFTOVER_FIX_NO_VANISHING_LITRES: over water (a canal square, a pond no filth lies on) or a wall, the liquid
			// goes into the water it lands in or the nearest canal or pond of its kind first: never out of the ledger silently
			bool dryGround = cell.InBounds(map) && cell.Standable(map) && !cell.GetTerrain(map).IsWater;
			if (!dryGround)
			{
				units -= PlaceInWater(map, RM_SuperdeepTrap.EngineOf(map), cell, liquid, units);
				units -= PlaceNearby(map, cell, liquid, units);
				if (units <= 0)
				{
					return;
				}
			}
			int n = RM_LiquidNetKernel.FilthCount(units, RM_MachinerySettings.UnitsPerFilth);
			ThingDef own = liquid?.spillFilth ?? RimMandrakeFlowWorks_DefOf.RM_Filth_LiquidSpill;
			int made = 0;
			for (int i = 0; i < n; i++)
			{
				if (FilthMaker.TryMakeFilth(cell, map, own) || (own != RimMandrakeFlowWorks_DefOf.RM_Filth_LiquidSpill
				    && RimMandrakeFlowWorks_DefOf.RM_Filth_LiquidSpill != null && FilthMaker.TryMakeFilth(cell, map, RimMandrakeFlowWorks_DefOf.RM_Filth_LiquidSpill)))
				{
					made++;
					continue;
				}
				Unplaced++;
				break;
			}
			// the filth that lay records its share of the spill; the share no filth recorded is still liquid that must land
			int recorded = n <= 0 ? units : made >= n ? units : (int)((long)units * made / n);
			SpilledUnits += recorded;
			int rest = units - recorded;
			if (rest > 0)
			{
				rest -= PlaceNearby(map, cell, liquid, rest);
			}
			if (rest > 0)
			{
				// HOSE_LEFTOVER_FIX_FULL_CANAL_LOSS: nothing within HomeRadius took it (a brim-full canal, the intake pond farther
				// off): any water of its kind on the map, nearest first, before anything leaves the world
				rest -= PlaceAnywhere(map, cell, liquid, rest);
			}
			if (rest > 0)
			{
				// truly nowhere: the disclosed loss, announced with its amount (owner: overflow destroys only where the game
				// announces it); counted with the fill-in overflow in the L0 ledger
				LostUnits += rest;
				RM_SuperdeepTrap.EngineOf(map)?.ReportLiquidLost(cell, rest, "Spilled " + (liquid?.label ?? "liquid"));
				Log.WarningOnce("[FlowWorks] a spill of " + liquid?.defName + " at " + cell + " found no filth cell and no water within "
					+ HomeRadius + " squares; " + rest + " units were lost (announced)", 0x5B1117);
			}
		}

		/// <summary>State read: spilled units that found no filth cell and no water nearby and were lost, announced.</summary>
		public static int LostUnits;

		/// <summary>State read: spilled units that went back into a pond instead of lying as filth (C1-F11).</summary>
		public static int ReturnedUnits;

		/// <summary>C1-F11: credit up to <paramref name="units"/> of <paramref name="liquid"/> to a pond body of that liquid at
		/// <paramref name="cell"/> or beside it (the pond-return setting on). Returns the whole units it took.</summary>
		private static int ReturnToPond(Map map, IntVec3 cell, LiquidDef liquid, int units)
		{
			FluidDef fluid = liquid?.canalFluid;
			if (map == null || fluid == null || units <= 0 || !RimMandrakeFlowWorksSettings.pondReturnLegEnabled || !cell.InBounds(map))
			{
				return 0;
			}
			TerrainDef t = cell.GetTerrain(map);
			if (t == null || !t.IsWater)
			{
				return 0;   // dry ground: the spill lies as filth
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			if (ex?.Stock == null)
			{
				return 0;
			}
			int level = RM_PumpMath.TankUnitsPerLevel;
			foreach (IntVec3 c in new[] { cell }.Concat(GenAdj.CellsAdjacent8Way(new TargetInfo(cell, map))))
			{
				if (!c.InBounds(map) || ex.IsExcavated(c))
				{
					continue;
				}
				RM_LiquidBody body = ex.Stock.IndexedBodyAt(map, c);
				if (body == null || (body.fluid ?? ex.ActiveFluid) != fluid)
				{
					continue;
				}
				float want = LiquidTypes.RM_ContainerMaterialMath.BodyStockFor(units, fluid.volumePerTile, level);
				float took = ex.Stock.TryCredit(map, c, want, ex);
				// a part-credit counts up (never creates liquid: what the pond took covers at most what left the hose)
				int back = took >= want - 1e-4f ? units : System.Math.Min(units, (int)System.Math.Ceiling(took * level / fluid.volumePerTile - 1e-4));
				ReturnedUnits += back;
				return back;
			}
			return 0;
		}
	}
}
