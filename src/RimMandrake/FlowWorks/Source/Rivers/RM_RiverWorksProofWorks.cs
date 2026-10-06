using System.Linq;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Rivers
{
	/// <summary>
	/// Slice 2 probes for the first script (validation.py chain "works"), via jawa/static_call. Each
	/// builds what it needs on the current map's own river (a test map is disposable), reads state,
	/// and returns one line. "UNMEASURED ..." = the question could not be asked, never a pass.
	/// </summary>
	public static class RM_RiverWorksProofWorks
	{
		private static RM_PlaceWorker_RiverWeir placeWorker = new RM_PlaceWorker_RiverWeir();

		private static bool Allowed(Map map, IntVec3 c, Rot4 r)
		{
			return placeWorker.AllowsPlacing(RM_RiverWorksDefOf.RM_BankWeir, c, r, map).Accepted;
		}

		/// <summary>First bank-edge site with a surface current on its wet end and a free footprint.</summary>
		public static bool FindWeirSite(Map map, out IntVec3 loc, out Rot4 rot)
		{
			RM_MapComponent_RiverCurrent comp = map.GetComponent<RM_MapComponent_RiverCurrent>();
			foreach (IntVec3 c in map.AllCells)
			{
				for (int r = 0; r < 4; r++)
				{
					Rot4 tr = new Rot4(r);
					if (!Allowed(map, c, tr))
					{
						continue;
					}
					bool free = true;
					bool wetHasFlow = false;
					foreach (IntVec3 o in GenAdj.OccupiedRect(c, tr, RM_RiverWorksDefOf.RM_BankWeir.Size))
					{
						if (o.GetEdifice(map) != null)
						{
							free = false;
						}
						if (comp != null && comp.FlowDirAt(o) >= 0 && RM_RiverWorks.IsWaterCell(map, o))
						{
							wetHasFlow = true;
						}
					}
					if (free && wetHasFlow)
					{
						loc = c;
						rot = tr;
						return true;
					}
				}
			}
			loc = IntVec3.Invalid;
			rot = Rot4.North;
			return false;
		}

		private static RM_Building_BankWeir SpawnWeir(Map map, out string why)
		{
			why = null;
			if (!FindWeirSite(map, out IntVec3 loc, out Rot4 rot))
			{
				why = "UNMEASURED no bank-edge weir site with a current on this map";
				return null;
			}
			Thing t = ThingMaker.MakeThing(RM_RiverWorksDefOf.RM_BankWeir);
			t.SetFaction(Faction.OfPlayer);
			return GenSpawn.Spawn(t, loc, map, rot) as RM_Building_BankWeir;
		}

		/// <summary>place.weir_bank_edge: "PLACE edge=True dry=False wet=False".</summary>
		public static string ProofWeirPlace(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null)
			{
				return "UNMEASURED no map";
			}
			bool edge = FindWeirSite(map, out _, out _);
			bool dry = false, wet = false, sawDry = false, sawWet = false;
			foreach (IntVec3 c in map.AllCells)
			{
				if (sawDry && sawWet)
				{
					break;
				}
				CellRect r = GenAdj.OccupiedRect(c, Rot4.North, RM_RiverWorksDefOf.RM_BankWeir.Size);
				if (!r.InBounds(map))
				{
					continue;
				}
				int w = 0;
				foreach (IntVec3 o in r)
				{
					if (RM_RiverWorks.IsWaterCell(map, o)) w++;
				}
				if (w == 0 && !sawDry && r.Area == 2 && c.GetAffordances(map).Contains(TerrainAffordanceDefOf.Light))
				{
					sawDry = true;
					dry = Allowed(map, c, Rot4.North);
				}
				else if (w == 2 && !sawWet)
				{
					sawWet = true;
					wet = Allowed(map, c, Rot4.North);
				}
			}
			if (!edge || !sawDry || !sawWet)
			{
				return "UNMEASURED site edge=" + edge + " sawDry=" + sawDry + " sawWet=" + sawWet;
			}
			return "PLACE edge=" + edge + " dry=" + dry + " wet=" + wet;
		}

		/// <summary>weir.arrest_and_pool: spawns a weir; "POOL cells=N dropped=D arrestedWet=B".</summary>
		public static string ProofWeirPool(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_RiverCurrent comp = map?.GetComponent<RM_MapComponent_RiverCurrent>();
			if (comp == null)
			{
				return "UNMEASURED no map or no current component";
			}
			RM_Building_BankWeir w = SpawnWeir(map, out string why);
			if (w == null)
			{
				return why;
			}
			comp.MarkWorksDirty();
			HashSet<int> pool = new HashSet<int>();
			w.AddPoolCells(comp, pool);
			int dropped = 0;
			foreach (int i in pool)
			{
				IntVec3 c = map.cellIndices.IndexToCell(i);
				int baseLane = RM_RiverCurrentLanes.LaneOf(c.GetTerrain(map));
				if (comp.LaneAt(c) < baseLane) dropped++;
			}
			bool arrested = RM_CompRiverArrester.CellArrested(map, w.WaterCell);
			string res = "POOL cells=" + pool.Count + " dropped=" + dropped + " arrestedWet=" + arrested + " at=" + w.Position;
			if (arg != "keep")
			{
				w.Destroy();
			}
			return res;
		}

		/// <summary>weir.fish_draws_stock: spawns a weir and forces N catch rolls; reports the stock.</summary>
		public static string ProofWeirCatch(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null)
			{
				return "UNMEASURED no map";
			}
			int n = int.TryParse(arg, out int k) && k > 0 ? k : 10;
			RM_Building_BankWeir w = SpawnWeir(map, out string why);
			if (w == null)
			{
				return why;
			}
			WaterBody body = map.waterBodyTracker?.WaterBodyAt(w.WaterCell);
			if (body == null || !body.HasFish)
			{
				w.Destroy();
				return "UNMEASURED the weir's water body has no fish stock";
			}
			float before = body.Population;
			int fish = 0;
			int drift = 0;
			for (int i = 0; i < n; i++)
			{
				string r = w.TryCatch();
				if (r.Contains("fish=") && !r.Contains("fish=missed") && !r.Contains("fish=no") && !r.Contains("fish=full") && !r.Contains("fish=off"))
				{
					fish++;
				}
				if (r.Contains("drift=") && !r.Contains("drift=missed") && !r.Contains("drift=none") && !r.Contains("drift=full") && !r.Contains("drift=off"))
				{
					drift++;
				}
			}
			float after = body.Population;
			int held = w.HeldCatch().Count;
			w.Destroy();
			return "CATCH fishRolls=" + fish + " driftRolls=" + drift + " held=" + held
				+ " before=" + before.ToString("F1") + " after=" + after.ToString("F1") + " biome=" + map.Biome.defName;
		}

		/// <summary>breach.wash / breach.cascade_order: spawns a weir with catch and a downstream stake
		/// line, runs it down, breaches it; "BREACH washed=N heldAfter=H stakes=S".</summary>
		public static string ProofBreach(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_RiverCurrent comp = map?.GetComponent<RM_MapComponent_RiverCurrent>();
			if (comp == null)
			{
				return "UNMEASURED no map or no current component";
			}
			RM_Building_BankWeir w = SpawnWeir(map, out string why);
			if (w == null)
			{
				return why;
			}
			Thing catchThing = ThingMaker.MakeThing(ThingDefOf.RawPotatoes);
			catchThing.stackCount = 10;
			GenPlace.TryPlaceThing(catchThing, w.BankCell, map, ThingPlaceMode.Near);
			int heldBefore = w.HeldCatch().Count;
			w.HitPoints = 1;
			w.Breach();
			int heldAfter = w.HeldCatch().Count;
			string res = "BREACH heldBefore=" + heldBefore + " heldAfter=" + heldAfter + " breaching=" + w.Breaching
				+ " arrestOff=" + !w.ArrestActive + " at=" + w.Position;
			if (arg != "keep")
			{
				w.Destroy();
			}
			return res;
		}

		/// <summary>silt.richen_and_revert: spawns a trap on swappable soil; "SILT richened=B reverted=B".</summary>
		public static string ProofSilt(string arg)
		{
			Map map = Find.CurrentMap;
			ThingDef trapDef = RM_RiverWorksDefOf.RM_SiltTrap;
			RM_SiltSwapExtension table = trapDef?.GetModExtension<RM_SiltSwapExtension>();
			if (map == null || table == null)
			{
				return "UNMEASURED no map or no swap table";
			}
			foreach (IntVec3 c in map.AllCells)
			{
				if (!c.Standable(map) || c.GetEdifice(map) != null || table.RichFor(c.GetTerrain(map)) == null)
				{
					continue;
				}
				Thing t = ThingMaker.MakeThing(trapDef);
				t.SetFaction(Faction.OfPlayer);
				RM_Building_SiltTrap trap = GenSpawn.Spawn(t, c, map) as RM_Building_SiltTrap;
				if (trap == null)
				{
					return "UNMEASURED trap did not spawn";
				}
				IntVec3 cell = trap.RichenOne();
				if (!cell.IsValid)
				{
					trap.Destroy();
					continue;
				}
				TerrainDef rich = cell.GetTerrain(map);
				trap.Clog();
				TerrainDef back = cell.GetTerrain(map);
				trap.Destroy();
				return "SILT richened=" + rich.defName + " reverted=" + back.defName + " changed=" + (rich != back);
			}
			return "UNMEASURED no swappable soil on this map";
		}

		/// <summary>ferry.rope: two posts across the current; "FERRY paired=B rope=N ropeExempt=B".</summary>
		public static string ProofFerry(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_RiverCurrent comp = map?.GetComponent<RM_MapComponent_RiverCurrent>();
			if (comp == null || !FindWeirSite(map, out IntVec3 site, out _))
			{
				return "UNMEASURED no map, no current, or no bank";
			}
			// From a bank cell beside the river, walk straight across the current to the far bank.
			IntVec3 water = IntVec3.Invalid;
			foreach (IntVec3 o in GenAdj.CellsAdjacent8Way(new TargetInfo(site, map)))
			{
				if (comp.FlowDirAt(o) >= 0) { water = o; break; }
			}
			if (!water.IsValid)
			{
				return "UNMEASURED no water beside the site";
			}
			int across = (comp.FlowDirAt(water) + 2) % 8;
			IntVec3 a = WalkToBank(map, water, across);
			IntVec3 b = WalkToBank(map, water, (across + 4) % 8);
			if (!a.IsValid || !b.IsValid)
			{
				return "UNMEASURED could not find two banks across the current";
			}
			Thing pa = ThingMaker.MakeThing(RM_RiverWorksDefOf.RM_FerryPost);
			pa.SetFaction(Faction.OfPlayer);
			Thing pb = ThingMaker.MakeThing(RM_RiverWorksDefOf.RM_FerryPost);
			pb.SetFaction(Faction.OfPlayer);
			RM_Building_FerryPost fa = GenSpawn.Spawn(pa, a, map) as RM_Building_FerryPost;
			GenSpawn.Spawn(pb, b, map);
			comp.MarkWorksDirty();
			bool paired = fa?.Partner != null;
			int rope = comp.RopeCellCount;
			bool ropeExempt = comp.OnRope(water);
			string res = "FERRY paired=" + paired + " rope=" + rope + " ropeExempt=" + ropeExempt + " a=" + a + " b=" + b;
			if (arg != "keep")
			{
				pa.Destroy();
				pb.Destroy();
			}
			return res;
		}

		private static IntVec3 WalkToBank(Map map, IntVec3 from, int dir)
		{
			IntVec3 c = from;
			for (int i = 0; i < 60; i++)
			{
				c = new IntVec3(c.x + RM_RiverMath.StepX[dir], 0, c.z + RM_RiverMath.StepZ[dir]);
				if (!c.InBounds(map))
				{
					return IntVec3.Invalid;
				}
				if (!RM_RiverWorks.IsWaterCell(map, c))
				{
					return c.Standable(map) && c.GetEdifice(map) == null ? c : IntVec3.Invalid;
				}
			}
			return IntVec3.Invalid;
		}

		/// <summary>levee.holds: "LEVEE stakeIsEdifice=B" - the engine fact the levee rests on.</summary>
		public static string ProofLeveeFact(string arg)
		{
			ThingDef s = RM_RiverWorksDefOf.RM_BankStake;
			return s == null ? "UNMEASURED no RM_BankStake" : "LEVEE stakeIsEdifice=" + s.IsEdifice() + " leveeSetting=" + RM_RiversSettings.stakeLineLevee;
		}

		// ── taken over 2026-10-05 with the merge into FlowWorks ─────────────

		/// <summary>breach.cascade_order: a weir with stakes placed around it on dry ground is breached;
		/// reads the snap schedule. Every stake downstream of the weir is scheduled, nearest-downstream
		/// first (ticks never decrease with downstream distance); every stake more than a cell upstream
		/// is spared. "CASCADE stakes=N scheduled=S spared=U monotone=B upstreamSpared=B".</summary>
		public static string ProofCascadeOrder(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null || RM_RiverWorksDefOf.RM_BankStake == null)
			{
				return "UNMEASURED no map or no RM_BankStake";
			}
			RM_Building_BankWeir w = SpawnWeir(map, out string why);
			if (w == null)
			{
				return why;
			}
			int dir = w.FlowDirForProof;
			if (dir < 0)
			{
				w.Destroy();
				return "UNMEASURED the weir's wet cell has no flow direction";
			}
			List<Thing> stakes = new List<Thing>();
			List<float> orders = new List<float>();
			bool anyUp = false, anyDown = false;
			foreach (IntVec3 c in GenRadial.RadialCellsAround(w.Position, 12f, false))
			{
				if (stakes.Count >= 12)
				{
					break;
				}
				if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null || RM_RiverWorks.IsWaterCell(map, c)
					|| c.GetFirstPawn(map) != null || w.OccupiedRect().Contains(c))
				{
					continue;
				}
				float order = RM_RiverMath.DownstreamDistance(c.x - w.Position.x, c.z - w.Position.z, dir);
				if (order < -1f && anyUp && stakes.Count >= 6 && !anyDown)
				{
					continue; // keep room for downstream stakes
				}
				Thing s = ThingMaker.MakeThing(RM_RiverWorksDefOf.RM_BankStake);
				s.SetFaction(Faction.OfPlayer);
				GenSpawn.Spawn(s, c, map);
				stakes.Add(s);
				orders.Add(order);
				anyUp |= order < -1f;
				anyDown |= order > 1f;
			}
			w.HitPoints = 1;
			w.Breach();
			int scheduled = 0, spared = 0;
			bool upstreamSpared = true;
			List<KeyValuePair<float, int>> down = new List<KeyValuePair<float, int>>();
			for (int i = 0; i < stakes.Count; i++)
			{
				int tick = w.CascadeTickFor(stakes[i]);
				if (orders[i] < -1f)
				{
					if (tick >= 0) upstreamSpared = false;
				}
				else if (tick >= 0)
				{
					down.Add(new KeyValuePair<float, int>(orders[i], tick));
				}
				if (tick >= 0) scheduled++; else spared++;
			}
			down.Sort((a, b) => a.Key.CompareTo(b.Key));
			bool monotone = true;
			for (int i = 1; i < down.Count; i++)
			{
				if (down[i].Value < down[i - 1].Value) monotone = false;
			}
			int downCount = 0;
			for (int i = 0; i < orders.Count; i++) if (orders[i] >= -1f) downCount++;
			bool allDownScheduled = down.Count == downCount;
			for (int i = 0; i < stakes.Count; i++)
			{
				if (!stakes[i].Destroyed) stakes[i].Destroy();
			}
			w.Destroy();
			return "CASCADE stakes=" + stakes.Count + " scheduled=" + scheduled + " spared=" + spared + " anyUp=" + anyUp
				+ " anyDown=" + anyDown + " monotone=" + monotone + " upstreamSpared=" + upstreamSpared
				+ " allDownScheduled=" + allDownScheduled;
		}

		/// <summary>levee.holds / levee.gap_leaks (the flood check): spawns a vanilla SeasonalFlood on the
		/// river, stakes one dry cell and leaves another bare, and asks the flood itself
		/// (Flood.CanFloodSpreadInto, patched) whether it may spread into each - then flips stakeLineLevee
		/// off and asks again. "LEVEE stakeHolds=B gapLeaks=B offLetsThrough=B".</summary>
		public static string ProofLevee(string arg)
		{
			Map map = Find.CurrentMap;
			ThingDef floodDef = DefDatabase<ThingDef>.GetNamedSilentFail("SeasonalFlood");
			if (map == null || floodDef == null || RM_RiverWorksDefOf.RM_BankStake == null)
			{
				return "UNMEASURED no map, no SeasonalFlood (Odyssey) or no RM_BankStake";
			}
			RM_MapComponent_RiverCurrent comp = map.GetComponent<RM_MapComponent_RiverCurrent>();
			if (comp == null || !FindWeirSite(map, out IntVec3 site, out _))
			{
				return "UNMEASURED no river bank on this map";
			}
			System.Reflection.MethodInfo spread = HarmonyLib.AccessTools.Method(typeof(Flood), "CanFloodSpreadInto");
			System.Reflection.MethodInfo pot = HarmonyLib.AccessTools.Method(typeof(Flood), "CanFloodPotentiallySpreadInto");
			if (spread == null || pot == null)
			{
				return "UNMEASURED Flood members not found";
			}
			Flood flood = GenSpawn.Spawn(ThingMaker.MakeThing(floodDef), site, map) as Flood;
			if (flood == null || flood.Destroyed)
			{
				return "UNMEASURED the flood found no cells to open from here";
			}
			IntVec3 stakeCell = IntVec3.Invalid, gapCell = IntVec3.Invalid;
			foreach (IntVec3 c in GenRadial.RadialCellsAround(site, 10f, false))
			{
				if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null || c.GetFirstPawn(map) != null
					|| !(bool)pot.Invoke(flood, new object[] { c }))
				{
					continue;
				}
				if (!stakeCell.IsValid) stakeCell = c;
				else if (!gapCell.IsValid) { gapCell = c; break; }
			}
			if (!gapCell.IsValid)
			{
				flood.Destroy();
				return "UNMEASURED no two dry cells the flood could reach";
			}
			Thing s = ThingMaker.MakeThing(RM_RiverWorksDefOf.RM_BankStake);
			s.SetFaction(Faction.OfPlayer);
			GenSpawn.Spawn(s, stakeCell, map);
			bool stakeHolds = !(bool)spread.Invoke(flood, new object[] { stakeCell });
			bool gapLeaks = (bool)spread.Invoke(flood, new object[] { gapCell });
			bool was = RM_RiversSettings.stakeLineLevee;
			bool offLetsThrough;
			try
			{
				RM_RiversSettings.stakeLineLevee = false;
				offLetsThrough = (bool)spread.Invoke(flood, new object[] { stakeCell });
			}
			finally
			{
				RM_RiversSettings.stakeLineLevee = was;
			}
			s.Destroy();
			flood.Destroy();
			return "LEVEE stakeHolds=" + stakeHolds + " gapLeaks=" + gapLeaks + " offLetsThrough=" + offLetsThrough
				+ " stake=" + stakeCell + " gap=" + gapCell;
		}

		/// <summary>ferry.undrafted_rope: strings a ferry, forces the path grid to recompute, and reads the
		/// undrafted perceived cost on a rope cell versus the same river off the rope.
		/// "ROPEPATH onRope=N offRope=M guided=B".</summary>
		public static string ProofFerryPath(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_RiverCurrent comp = map?.GetComponent<RM_MapComponent_RiverCurrent>();
			if (comp == null)
			{
				return "UNMEASURED no map or no current component";
			}
			string ferry = ProofFerry("keep");
			if (!ferry.StartsWith("FERRY paired=True"))
			{
				return ferry.StartsWith("UNMEASURED") ? ferry : "UNMEASURED ferry did not pair: " + ferry;
			}
			IntVec3 onRope = IntVec3.Invalid, offRope = IntVec3.Invalid;
			foreach (int i in comp.RopeIndicesNoRebuild)
			{
				IntVec3 c = map.cellIndices.IndexToCell(i);
				if (RM_RiverWorks.IsWaterCell(map, c)) { onRope = c; break; }
			}
			if (onRope.IsValid)
			{
				TerrainDef ropeTerrain = onRope.GetTerrain(map);
				foreach (IntVec3 c in GenRadial.RadialCellsAround(onRope, 12f, false))
				{
					if (c.InBounds(map) && c.GetTerrain(map) == ropeTerrain && !comp.OnRope(c)) { offRope = c; break; }
				}
			}
			int costOn = -1, costOff = -1;
			if (onRope.IsValid && offRope.IsValid)
			{
				PathFinderMapData data = map.pathFinder.MapData;
				HarmonyLib.AccessTools.Method(typeof(PathFinderMapData), "Notify_MapDirtied")?.Invoke(data, null);
				data.GatherData(new List<PathRequest>());
				costOn = RM_RopePathing.UndraftedCostAt(map, onRope);
				costOff = RM_RopePathing.UndraftedCostAt(map, offRope);
			}
			foreach (Thing p in map.listerThings.ThingsOfDef(RM_RiverWorksDefOf.RM_FerryPost).ToArray())
			{
				p.Destroy();
			}
			if (!onRope.IsValid || !offRope.IsValid)
			{
				return "UNMEASURED no river cell on/off the rope to compare";
			}
			return "ROPEPATH onRope=" + costOn + " offRope=" + costOff + " guided=" + RM_RopePathing.Active;
		}
	}
}