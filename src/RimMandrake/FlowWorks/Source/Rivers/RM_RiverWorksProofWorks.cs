using System.Linq;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Rivers
{
	/// <summary>
	/// Slice 2 probes for River Works' scripts (src/RimMandrake/FlowWorks/northstar/extensions_rivers.py and
	/// river_site.py), via jawa/static_call. Each
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
			// Away from the map edge: the first site in AllCells order sat on row 0, where the river ENTERS the map, so it
			// had no upstream to pool (MEASURED 2026-10-06, Desert river tile 162: "POOL cells=0 ... at=(79, 0, 0)").
			int margin = RM_RiversSettings.weirPoolLength + 4;
			foreach (IntVec3 c in map.AllCells)
			{
				if (c.x < margin || c.z < margin || c.x >= map.Size.x - margin || c.z >= map.Size.z - margin)
				{
					continue;
				}
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

		/// <summary>weir.arrest_and_pool: spawns a weir; "POOL cells=N dropped=D arrestedWet=B at=C" plus the wet cell's
		/// flow neighbourhood (FlowNeighbourhood), so a pool of 0 explains itself.</summary>
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
			string res = "POOL cells=" + pool.Count + " dropped=" + dropped + " arrestedWet=" + arrested + " at=" + w.Position
				+ " " + FlowNeighbourhood(comp, w.WaterCell);
			if (arg != "keep")
			{
				w.Destroy();
			}
			return res;
		}

		/// <summary>WEIR_POOL_DIAGNOSE_DAMMED_AT_THE_EDGE: the evidence a pool count alone hides, one token per field
		/// (no spaces, so extensions_rivers.py's _kv parses it): the wet cell, its compass flow dir (0=E, CCW, -1 none),
		/// each of the 8 neighbours as dx,dz:dir, the old exact-step rule's verdict and the new walk's first step.</summary>
		private static string FlowNeighbourhood(RM_MapComponent_RiverCurrent comp, IntVec3 wet)
		{
			System.Func<int, int, int> dirAt = (x, z) => comp.FlowDirAt(new IntVec3(x, 0, z));
			int wetDir = dirAt(wet.x, wet.z);
			List<string> nbr = new List<string>();
			bool exactStep = false;
			for (int i = 0; i < 8; i++)
			{
				int dx = RM_RiverMath.StepX[i];
				int dz = RM_RiverMath.StepZ[i];
				int d = dirAt(wet.x + dx, wet.z + dz);
				nbr.Add(dx + "," + dz + ":" + d);
				if (d >= 0 && dx + RM_RiverMath.StepX[d] == 0 && dz + RM_RiverMath.StepZ[d] == 0)
				{
					exactStep = true;
				}
			}
			bool backHasFlow = wetDir >= 0 && dirAt(wet.x - RM_RiverMath.StepX[wetDir], wet.z - RM_RiverMath.StepZ[wetDir]) >= 0;
			int step = RM_RiverMath.UpstreamStep(wet.x, wet.z, dirAt);
			return "wetCell=" + wet.x + "," + wet.z + " wetDir=" + wetDir + " nbr=" + string.Join("|", nbr)
				+ " oldRuleFinds=" + (exactStep || backHasFlow) + " newFirstStep=" + (step < 0 ? "none"
				: RM_RiverMath.StepX[step] + "," + RM_RiverMath.StepZ[step]);
		}

		/// <summary>weir.joined_wall (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS, owner 2026-10-16 by card: "Weirs join into one
		/// continuous wall"): spawns a bank weir, then an all-water section end to end beyond its wet end. "JOIN placeOk=B
		/// run=N headIsBank=B joint=B poolSingle=N poolJoined=N poolGap=N". EXPECT placeOk run=2 headIsBank joint,
		/// poolJoined >= poolSingle > 0, poolGap = 0 (one broken section drains the run). LIES: no wet cell beyond the
		/// first weir's wet end (a one-cell-wide river) returns UNMEASURED, never a pass.</summary>
		public static string ProofWeirJoin(string arg)
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
			RM_Building_BankWeir w2 = null;
			try
			{
				HashSet<int> single = new HashSet<int>();
				w.AddPoolCells(comp, single);
				CellRect own = w.OccupiedRect();
				IntVec3 lo = RM_WeirRun.EndCell(w.Position, w.Rotation, w.def.Size, false);
				IntVec3 hi = RM_WeirRun.EndCell(w.Position, w.Rotation, w.def.Size, true);
				IntVec3 end = lo.DistanceToSquared(w.WaterCell) <= hi.DistanceToSquared(w.WaterCell) ? lo : hi;
				IntVec3 axis = w.Rotation.IsHorizontal ? IntVec3.East : IntVec3.North;
				IntVec3 found = IntVec3.Invalid;
				foreach (IntVec3 cand in new[] { end, end + axis, end - axis })
				{
					CellRect r = GenAdj.OccupiedRect(cand, w.Rotation, w.def.Size);
					if (!r.InBounds(map) || !r.Contains(end) || r.Overlaps(own))
					{
						continue;
					}
					if (Allowed(map, cand, w.Rotation))
					{
						found = cand;
						break;
					}
				}
				if (!found.IsValid)
				{
					return "UNMEASURED no all-water section fits beyond the weir's wet end at " + end;
				}
				Thing t = ThingMaker.MakeThing(RM_RiverWorksDefOf.RM_BankWeir);
				t.SetFaction(Faction.OfPlayer);
				w2 = GenSpawn.Spawn(t, found, map, w.Rotation) as RM_Building_BankWeir;
				if (w2 == null)
				{
					if (!t.Destroyed) t.Destroy();
					return "UNMEASURED the second weir did not spawn at " + found;
				}
				comp.MarkWorksDirty();
				HashSet<int> joined = new HashSet<int>();
				w.AddPoolCells(comp, joined);
				w2.AddPoolCells(comp, joined);
				bool headIsBank = w.RunHead() == w && w2.RunHead() == w;
				bool joint = RM_WeirRun.JoinedAt(w, end == hi) && w2.Run().Count == 2;
				int run = w.Run().Count;
				w2.Arrester.Active = false;
				HashSet<int> gap = new HashSet<int>();
				w.AddPoolCells(comp, gap);
				w2.AddPoolCells(comp, gap);
				w2.Arrester.Active = true;
				return "JOIN placeOk=True run=" + run + " headIsBank=" + headIsBank + " joint=" + joint + " poolSingle=" + single.Count
					+ " poolJoined=" + joined.Count + " poolGap=" + gap.Count + " at=" + w.Position + "+" + found;
			}
			finally
			{
				if (arg != "keep")
				{
					if (w2 != null && !w2.Destroyed) w2.Destroy();
					if (!w.Destroyed) w.Destroy();
				}
			}
		}

		/// <summary>weir.captures_floating (WEIR_CATCH_FIX_NO_FREE_FISH, owner 2026-10-23: "they should just capture anything
		/// floating downstream. No auto fish capture."): spawns a weir, lays a 10-stack in its first intake cell (where the
		/// carry stops a drifting thing), forces CaptureFloating; "CAPTURE intake=N lifted=L onDry=B unitsBefore=U
		/// unitsAfter=V created=C at=P". created counts item stacks within 4 cells that were not there before, beyond the
		/// probe's own: the weir must make nothing.</summary>
		public static string ProofWeirCapture(string arg)
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
			Thing stack = null;
			try
			{
				List<IntVec3> intake = w.IntakeCells().FindAll(c => c.InBounds(map) && c.Standable(map) && c.GetFirstItem(map) == null);
				if (intake.Count == 0)
				{
					return "UNMEASURED intake=0: no free cell whose current runs onto this weir at=" + w.Position;
				}
				HashSet<Thing> before = new HashSet<Thing>();
				foreach (Thing t in GenRadial.RadialDistinctThingsAround(w.Position, map, 4f, true))
				{
					if (t.def.category == ThingCategory.Item) before.Add(t);
				}
				stack = ThingMaker.MakeThing(ThingDefOf.WoodLog); // the probe's own floating stack, not the weir's
				stack.stackCount = 10;
				GenSpawn.Spawn(stack, intake[0], map);
				int lifted = w.CaptureFloating();
				bool onDry = stack.Spawned && !comp.HasCurrent(stack.Position);
				int unitsAfter = stack.Spawned ? stack.stackCount : 0;
				int created = 0;
				foreach (Thing t in GenRadial.RadialDistinctThingsAround(w.Position, map, 4f, true))
				{
					if (t.def.category == ThingCategory.Item && t != stack && !before.Contains(t)) created++;
				}
				return "CAPTURE intake=" + intake.Count + " lifted=" + lifted + " onDry=" + onDry + " unitsBefore=10 unitsAfter="
					+ unitsAfter + " created=" + created + " at=" + w.Position;
			}
			finally
			{
				if (arg != "keep")
				{
					DestroyIfSpawned(stack);
					if (!w.Destroyed) w.Destroy();
				}
			}
		}

		/// <summary>river.flotsam (owner by card 2026-10-23 07:19, "Yes, occasional flotsam"): forces one flotsam spawn at
		/// the upstream edge, then lays that piece on a downstream-edge cell and steps it once; "FLOTSAM spawn=... entries=N
		/// onEntry=B leftEdge=B". UNMEASURED when the map has no river entry or this biome has no drift list.</summary>
		public static string ProofRiverFlotsam(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_RiverCurrent comp = map?.GetComponent<RM_MapComponent_RiverCurrent>();
			if (comp == null)
			{
				return "UNMEASURED no map or no current component";
			}
			int before = comp.FlotsamCount;
			string r = comp.TrySpawnFlotsam(true);
			if (!r.StartsWith("spawned=") || comp.FlotsamCount <= before)
			{
				return "UNMEASURED flotsam did not spawn: " + r + " entries=" + comp.EntryCells().Count;
			}
			Thing t = null;
			foreach (IntVec3 c in comp.EntryCells())
			{
				Thing f = c.GetFirstItem(map);
				if (f != null && comp.IsFlotsam(f))
				{
					t = f;
					break;
				}
			}
			bool onEntry = t != null;
			bool left = false;
			if (t != null)
			{
				foreach (IntVec3 c in map.AllCells)
				{
					int d = comp.FlowDirAt(c);
					if (d < 0 || !c.Standable(map) || c.GetFirstItem(map) != null)
					{
						continue;
					}
					IntVec3 n = new IntVec3(c.x + RM_RiverMath.StepX[d], 0, c.z + RM_RiverMath.StepZ[d]);
					if (n.InBounds(map))
					{
						continue;
					}
					t.Position = c; // the downstream edge
					comp.StepOne(t);
					left = t.Destroyed;
					break;
				}
				if (!t.Destroyed && arg != "keep")
				{
					t.Destroy();
				}
			}
			return "FLOTSAM " + r + " entries=" + comp.EntryCells().Count + " onEntry=" + onEntry + " leftEdge=" + left;
		}

		/// <summary>breach.wash: spawns a weir with a stack of catch on its bank, runs it down, breaches it;
		/// "BREACH heldBefore=N heldAfter=H breaching=B arrestOff=B at=C" (the stake cascade is ProofCascadeOrder).</summary>
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
				DestroyIfSpawned(catchThing);   // the probe's own stack, as ProofBreachNoRoom: no litter left to drift
			}
			return res;
		}

		/// <summary>breach.wash_no_room (A2 of WEIR_WASH_ITEM_LOSS_MEND_PLACE_FIRST): a breach whose strand has no
		/// placeable cell must leave every held stack spawned where it sat, not lost. A real "no room" cannot be staged:
		/// the despawned stack's own cell is always free and inside the engine's 12.9-cell Near search, so this hands
		/// the wash an extra validator refusing every cell (RM_Building_BankWeir.washPlaceValidator) - the engine's own
		/// TryFindPlaceSpotNear then fails exactly as it does with no room. Spawns a weir with 10 potatoes on its bank.
		/// "NOROOM asked=Q held=N spawned=S atOld=A unitsBefore=U unitsAfter=V breaching=B";
		/// asked=0 means placement was never attempted (no strand downstream) and the line is UNMEASURED.</summary>
		public static string ProofBreachNoRoom(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_RiverCurrent comp = map?.GetComponent<RM_MapComponent_RiverCurrent>();
			if (comp == null)
			{
				return "UNMEASURED no map or no current component";
			}
			if (!RM_RiversSettings.breachWashesCatch)
			{
				return "UNMEASURED breachWashesCatch is off";
			}
			RM_Building_BankWeir w = SpawnWeir(map, out string why);
			if (w == null)
			{
				return why;
			}
			Thing catchThing = ThingMaker.MakeThing(ThingDefOf.RawPotatoes);
			catchThing.stackCount = 10;
			GenPlace.TryPlaceThing(catchThing, w.BankCell, map, ThingPlaceMode.Near);
			List<Thing> held = w.HeldCatch();
			List<IntVec3> from = held.Select(t => t.Position).ToList();
			int unitsBefore = held.Sum(t => t.stackCount);
			int asked = 0;
			w.HitPoints = 1;
			RM_Building_BankWeir.washPlaceValidator = c => { asked++; return false; };
			try
			{
				w.Breach();
			}
			finally
			{
				RM_Building_BankWeir.washPlaceValidator = null;
			}
			int spawned = 0, atOld = 0, unitsAfter = 0;
			for (int i = 0; i < held.Count; i++)
			{
				Thing t = held[i];
				if (t.Destroyed || !t.Spawned || t.Map != map)
				{
					continue;
				}
				spawned++;
				unitsAfter += t.stackCount;
				if (t.Position == from[i])
				{
					atOld++;
				}
			}
			string res = (asked == 0 ? "UNMEASURED wash never tried to place (no strand downstream) " : "")
				+ "NOROOM asked=" + asked + " held=" + held.Count + " spawned=" + spawned + " atOld=" + atOld
				+ " unitsBefore=" + unitsBefore + " unitsAfter=" + unitsAfter + " breaching=" + w.Breaching + " at=" + w.Position;
			if (arg != "keep")
			{
				w.Destroy();
				DestroyIfSpawned(catchThing);
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
			return SpawnFerry(arg, out _, out _);
		}

		/// <summary>ProofFerry's body; <paramref name="pa"/>/<paramref name="pb"/> are the two posts it spawned
		/// (null when it spawned none), so a caller that keeps them can remove exactly those and no player post.</summary>
		private static string SpawnFerry(string arg, out Thing pa, out Thing pb)
		{
			pa = null;
			pb = null;
			Map map = Find.CurrentMap;
			RM_MapComponent_RiverCurrent comp = map?.GetComponent<RM_MapComponent_RiverCurrent>();
			if (comp == null)
			{
				return "UNMEASURED no map or no current component";
			}
			// A straight line across the current between two posts a player could build. TESTENV_FERRY_ROPE_HARDEN_WIDE_RIVER_BANKS
			// (r8, a size-2.5 river ~33 cells wide): ONE line from the first weir site was tried, and one tree on its far
			// bank cell read "could not find two banks". Every moving-water cell is now a start; the LONGEST crossing whose
			// two bank cells take a post and lie within ferryMaxSpan wins (r9: shortest-wins strung a 1-cell side trickle,
			// rope=3, not the main current). What is measured below is unchanged.
			if (!FindFerryCrossing(map, comp, out IntVec3 water, out IntVec3 a, out IntVec3 b, out string why))
			{
				return "UNMEASURED could not find two banks across the current: " + why;
			}
			pa = ThingMaker.MakeThing(RM_RiverWorksDefOf.RM_FerryPost);
			pa.SetFaction(Faction.OfPlayer);
			pb = ThingMaker.MakeThing(RM_RiverWorksDefOf.RM_FerryPost);
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

		/// <summary>The longest straight crossing of the current a rope can span (the main channel, not a side trickle): from a moving-water cell, walk across its flow
		/// (FlowDirAt+2) both ways to the first dry cell; both must take a post (standable, no edifice) and lie at most
		/// ferryMaxSpan apart. False with the counts of why when no cell gives one (told apart: a river too wide for the
		/// rope, a bank that will not take a post, a walk that leaves the map).</summary>
		public static bool FindFerryCrossing(Map map, RM_MapComponent_RiverCurrent comp, out IntVec3 water, out IntVec3 a,
			out IntVec3 b, out string why)
		{
			water = a = b = IntVec3.Invalid;
			int span = RM_RiversSettings.ferryMaxSpan;
			int starts = 0, offMap = 0, blocked = 0, tooWide = 0;
			float best = -1f;
			foreach (IntVec3 c in map.AllCells)
			{
				int flow = comp.FlowDirAt(c);
				if (flow < 0 || !RM_RiverWorks.IsWaterCell(map, c))
				{
					continue;
				}
				starts++;
				int across = (flow + 2) % 8;
				IntVec3 cb = IntVec3.Invalid;
				int r = WalkToBank(map, c, across, span, out IntVec3 ca);
				if (r == 0)
				{
					r = WalkToBank(map, c, (across + 4) % 8, span, out cb);
				}
				if (r != 0)
				{
					if (r == 1) { offMap++; } else if (r == 2) { tooWide++; } else { blocked++; }
					continue;
				}
				float d = ca.DistanceTo(cb);
				if (d > span)
				{
					tooWide++;
					continue;
				}
				if (d > best)
				{
					best = d;
					water = c;
					a = ca;
					b = cb;
				}
			}
			why = "starts=" + starts + " offMap=" + offMap + " tooWide=" + tooWide + " blockedBank=" + blocked + " maxSpan=" + span;
			return water.IsValid;
		}

		/// <summary>Walk from <paramref name="from"/> in <paramref name="dir"/> to the first non-water cell, at most
		/// <paramref name="maxSteps"/> steps. 0 = a bank that takes a post (<paramref name="bank"/>), 1 = left the map,
		/// 2 = still water after maxSteps (wider than the rope), 3 = the bank cell is not standable or holds an edifice.</summary>
		private static int WalkToBank(Map map, IntVec3 from, int dir, int maxSteps, out IntVec3 bank)
		{
			bank = IntVec3.Invalid;
			IntVec3 c = from;
			for (int i = 0; i < maxSteps; i++)
			{
				c = new IntVec3(c.x + RM_RiverMath.StepX[dir], 0, c.z + RM_RiverMath.StepZ[dir]);
				if (!c.InBounds(map))
				{
					return 1;
				}
				if (!RM_RiverWorks.IsWaterCell(map, c))
				{
					if (!c.Standable(map) || c.GetEdifice(map) != null)
					{
						return 3;
					}
					bank = c;
					return 0;
				}
			}
			return 2;
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
			string ferry = SpawnFerry("keep", out Thing postA, out Thing postB);
			if (!ferry.StartsWith("FERRY paired=True"))
			{
				DestroyIfSpawned(postA);
				DestroyIfSpawned(postB);
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
			// only the two posts this probe spawned; a ferry the player built stays
			DestroyIfSpawned(postA);
			DestroyIfSpawned(postB);
			if (!onRope.IsValid || !offRope.IsValid)
			{
				return "UNMEASURED no river cell on/off the rope to compare";
			}
			return "ROPEPATH onRope=" + costOn + " offRope=" + costOff + " guided=" + RM_RopePathing.Active;
		}

		private static void DestroyIfSpawned(Thing t)
		{
			if (t != null && !t.Destroyed)
			{
				t.Destroy();
			}
		}
	}
}