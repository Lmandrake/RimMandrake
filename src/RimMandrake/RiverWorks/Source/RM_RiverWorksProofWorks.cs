using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.RiverWorks
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
			return s == null ? "UNMEASURED no RM_BankStake" : "LEVEE stakeIsEdifice=" + s.IsEdifice() + " leveeSetting=" + RM_RiverWorksSettings.stakeLineLevee;
		}
	}
}
