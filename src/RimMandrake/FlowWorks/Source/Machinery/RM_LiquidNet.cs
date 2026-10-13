using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.Machinery.Kits;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>Marks a ThingDef as the UNIVERSAL PIPE: the permanent per-cell line that carries any liquid (owner 2026-10-04:
	/// "universal pipes that can carry any liquid of any kind"). Built in Phase 8 as the framework's "liquid hose"
	/// (RM_HoseSpool); renamed at the hose port (2026-10-11, Q1 default) because the reel's flexible hose is FlowWorks' only
	/// hose now. NOT terrain and NOT a VE pipe.</summary>
	public class RM_UniversalPipeExtension : DefModExtension
	{
	}

	/// <summary>The extension's name for its first week (built 2026-10-05). Kept as an empty subclass so an XML patch from
	/// another mod naming it still resolves. Delete at the world remake.</summary>
	[System.Obsolete("Use RM_UniversalPipeExtension (hose port, 2026-10-11).")]
	public class RM_LiquidHoseExtension : RM_UniversalPipeExtension
	{
	}

	/// <summary>
	/// The liquid net: which tanks a pump, converter, adapter, reactor or bath bench can reach, and by which route. The RULES live
	/// in the Verse-free RM_LiquidNetKernel (selftested); this is the adapter that shows the kernel the map:
	///   * a machine reaches every tank touching it (8-way), every tank touching a universal-pipe run that touches it (pipes
	///     conduct cardinally, like a conduit), and every tank at the far end of a laid flexible hose coupled to it, to a pipe on
	///     its net, or to a relay reel on such a hose (hose port step 6);
	///   * tanks and machines never conduct: a tank is an endpoint, so two runs never merge through a tank by accident.
	/// Mod Settings: universalPipesEnabled (off: pipes conduct nothing); hose_enabled (off: hoses carry nothing).
	/// </summary>
	public static class RM_LiquidNet
	{
		/// <summary>Search cap: a pipe run longer than this is not followed further (PROVISIONAL; the component cap).</summary>
		public const int MaxPipeCells = RM_NetComponents.MaxConductors;

		public static bool IsPipe(Thing t)
		{
			return t?.def?.GetModExtension<RM_UniversalPipeExtension>() != null;
		}

		public static bool HasPipe(IntVec3 c, Map map)
		{
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (IsPipe(things[i]))
				{
					return true;
				}
			}
			return false;
		}

		// ---------------------------------------------------------------- hydraulic roles (FINAL §3.1)
		private static HashSet<ThingDef> bathBenches;

		/// <summary>Benches that are recipe users of any recipe carrying RM_RecipeLiquidExtension (resolved once).</summary>
		private static bool IsBathBench(ThingDef d)
		{
			if (bathBenches == null)
			{
				var set = new HashSet<ThingDef>();
				foreach (RecipeDef r in DefDatabase<RecipeDef>.AllDefsListForReading)
				{
					if (r.GetModExtension<RM_RecipeLiquidExtension>() == null)
					{
						continue;
					}
					foreach (ThingDef u in r.AllRecipeUsers)
					{
						set.Add(u);
					}
				}
				bathBenches = set;
			}
			return d != null && bathBenches.Contains(d);
		}

		/// <summary>What a thing is to the liquid: decided only by FlowWorks' own types. VE PipeSystem and DBH things stay visual
		/// couplings (None): liquid enters or leaves those nets through CompLiquidPipeAdapter, a Machine.</summary>
		public static RM_NetRole RoleOfThing(Thing t)
		{
			if (t == null || !t.Spawned)
			{
				return RM_NetRole.None;
			}
			RM_NetRole role = RoleOfKind(t);
			// L9 (rev 2 §3.4, owner Q4): another faction's tank or machine joins the network (taking from it is theft); with liquid
			// theft off in Mod Settings it does not join at all. Unowned things (ruins) always join.
			if ((role == RM_NetRole.Tank || role == RM_NetRole.Machine) && !RM_MachinerySettings.liquidTheftEnabled && IsForeign(t))
			{
				return RM_NetRole.None;
			}
			return role;
		}

		/// <summary>Owned by a faction that is not the player's (an unowned ruin is not foreign).</summary>
		public static bool IsForeign(Thing t) => t?.Faction != null && !t.Faction.IsPlayer;

		/// <summary>The role by type alone (spawned or not): what HosePorts caches per def.</summary>
		public static RM_NetRole RoleOfKind(Thing t)
		{
			if (t == null)
			{
				return RM_NetRole.None;
			}
			if (t is Building_LiquidTank)
			{
				return RM_NetRole.Tank;
			}
			if (IsPipe(t))
			{
				return RM_NetRole.Pipe;
			}
			if (t is Building_LiquidPump)
			{
				return RM_NetRole.Machine;
			}
			if (t is ThingWithComps tw && (tw.GetComp<CompLiquidPipeAdapter>() != null || tw.GetComp<CompLiquidConverter>() != null
			                               || tw.GetComp<CompLiquidReactor>() != null))
			{
				return RM_NetRole.Machine;
			}
			return IsBathBench(t.def) ? RM_NetRole.Machine : RM_NetRole.None;
		}

		/// <summary>The vertex a hose port thing stands for: a pipe is its cell (the cell the BFS walks), anything else itself.</summary>
		internal static object VertexOf(Thing t)
		{
			return IsPipe(t) ? (object)t.Position : t;
		}

		// ---------------------------------------------------------------- the graph the kernel reads
		internal sealed class MapGraph : IRM_NetGraph
		{
			private readonly Map map;
			private readonly RM_HoseLinks links;

			public MapGraph(Map map, RM_HoseLinks links)
			{
				this.map = map;
				this.links = links;
			}

			public bool PipesEnabled => RM_MachinerySettings.universalPipesEnabled;

			public RM_NetRole RoleOf(object v)
			{
				if (v is IntVec3 c)
				{
					return c.InBounds(map) && HasPipe(c, map) ? RM_NetRole.Pipe : RM_NetRole.None;
				}
				if (v is CompHoseReel)
				{
					return RM_NetRole.Relay;
				}
				if (v is RM_NetPort)
				{
					return RM_NetRole.Port;
				}
				return RoleOfThing(v as Thing);
			}

			public int Order(object v) => v is Thing t ? t.thingIDNumber : 0;

			private IEnumerable<object> ThingsIn(IEnumerable<IntVec3> cells, object exclude, RM_NetRole role)
			{
				foreach (IntVec3 c in cells)
				{
					if (!c.InBounds(map))
					{
						continue;
					}
					List<Thing> things = c.GetThingList(map);
					for (int i = 0; i < things.Count; i++)
					{
						if (things[i] != exclude && RoleOfThing(things[i]) == role)
						{
							yield return things[i];
						}
					}
				}
			}

			public IEnumerable<object> OriginTanks(object origin)
			{
				// a machine's touch store (8-way); a tank touches no store of its own
				return origin is Thing t && RoleOfThing(t) == RM_NetRole.Machine
					? ThingsIn(GenAdj.CellsAdjacent8Way(t), t, RM_NetRole.Tank)
					: Enumerable.Empty<object>();
			}

			public IEnumerable<object> OriginPipeCells(object origin)
			{
				if (!(origin is Thing t) || !t.Spawned)
				{
					yield break;
				}
				// a tank attaches through a pipe cardinal to it or under it; a machine through one 8-way around it or under it
				IEnumerable<IntVec3> around = RoleOfThing(t) == RM_NetRole.Tank ? GenAdj.CellsAdjacentCardinal(t) : GenAdj.CellsAdjacent8Way(t);
				foreach (IntVec3 c in around.Concat(t.OccupiedRect()))
				{
					if (c.InBounds(map) && HasPipe(c, map))
					{
						yield return c;
					}
				}
			}

			public IEnumerable<object> PipeTanks(object pipeCell)
			{
				var c = (IntVec3)pipeCell;
				return ThingsIn(GenAdj.CellsAdjacentCardinal(c, Rot4.North, IntVec2.One).Concat(new[] { c }), null, RM_NetRole.Tank).Distinct();
			}

			public IEnumerable<object> PipeMachines(object pipeCell)
			{
				var c = (IntVec3)pipeCell;
				return ThingsIn(GenAdj.CellsAdjacent8Way(c, Rot4.North, IntVec2.One).Concat(new[] { c }), null, RM_NetRole.Machine).Distinct();
			}

			public IEnumerable<object> PipeNeighbours(object pipeCell)
			{
				var c = (IntVec3)pipeCell;
				for (int d = 0; d < 4; d++)
				{
					IntVec3 n = c + GenAdj.CardinalDirections[d];
					if (n.InBounds(map) && HasPipe(n, map))
					{
						yield return n;
					}
				}
			}

			public IList<RM_NetLink> LinksAt(object v)
			{
				return links.At(v);
			}
		}

		// ---------------------------------------------------------------- topology revisions (rev 2 §3.1, build step L2)
		private sealed class NetState
		{
			public int revision;
			public readonly RM_NetTopologyCache cache = new RM_NetTopologyCache();
		}

		private static readonly Dictionary<Map, NetState> states = new Dictionary<Map, NetState>();

		private static NetState StateOf(Map map)
		{
			if (!states.TryGetValue(map, out NetState s))
			{
				foreach (Map m in states.Keys.Where(k => !Find.Maps.Contains(k)).ToList())
				{
					states.Remove(m);
				}
				s = states[map] = new NetState();
			}
			return s;
		}

		/// <summary>State read: revision bumps this session (probe perf row).</summary>
		public static int Bumps;

		/// <summary>The topology changed on <paramref name="map"/> (a pipe, tank or machine spawned or despawned; a hose link
		/// appeared, went or changed an end): the next query builds new components. Cheap; never builds anything itself.</summary>
		public static void Bump(Map map)
		{
			if (map == null)
			{
				return;
			}
			StateOf(map).revision++;
			Bumps++;
		}

		/// <summary>The map's components for the current revision (RM_HoseLinks' backstop signature runs first, so a link change
		/// nobody announced still bumps the revision).</summary>
		public static RM_NetComponents Components(Map map)
		{
			RM_HoseLinks links = RM_HoseLinks.For(map);
			NetState s = StateOf(map);
			long key = RM_LiquidNetKernel.RevisionKey(s.revision, RM_MachinerySettings.universalPipesEnabled, RM_HoseSettings.enabled, RM_MachinerySettings.liquidTheftEnabled);
			return s.cache.Get(key, () => new RM_NetComponents(new MapGraph(map, links)));
		}

		/// <summary>Defs whose things change the topology when they spawn or despawn (pipes, tanks, machines), by def.</summary>
		private static readonly Dictionary<ThingDef, bool> topoDefs = new Dictionary<ThingDef, bool>();

		internal static bool ChangesTopology(Thing t)
		{
			if (t?.def == null)
			{
				return false;
			}
			if (!topoDefs.TryGetValue(t.def, out bool b))
			{
				topoDefs[t.def] = b = RoleOfKind(t) != RM_NetRole.None;
			}
			return b;
		}

		/// <summary>A member's store this revision: its tanks (touching first, then by hoses crossed, then by id) and routes.</summary>
		public static RM_NetResult Store(Thing origin)
		{
			return origin?.Map == null ? new RM_NetResult() : Components(origin.Map).StoreOf(origin);
		}

		/// <summary>A component this member touches is over the cap: it is refused and the member reads "network too large".</summary>
		public static bool TooLarge(Thing origin)
		{
			return origin?.Map != null && Components(origin.Map).TooLarge(origin);
		}

		/// <summary>FINAL §3.5: a tank whose route has a dead link (a hose wound in, dropped or despawned since this revision was
		/// built) is not on the net for this transfer, and the revision is bumped so the next query rebuilds.</summary>
		private static bool RouteLiveOrBump(Thing origin, RM_NetResult r, object tank)
		{
			if (!r.Routes.TryGetValue(tank, out List<RM_NetLink> route) || route.Count == 0)
			{
				return true;
			}
			if (RM_LiquidNetKernel.RouteLive(route, RM_HoseLinks.For(origin.Map).Live))
			{
				return true;
			}
			Bump(origin.Map);
			return false;
		}

		/// <summary>Every liquid tank on <paramref name="origin"/>'s net (its store, rev 2 §3.1): touching tanks first.
		/// Never includes <paramref name="origin"/> itself.</summary>
		public static List<Building_LiquidTank> TanksFor(Thing origin)
		{
			var result = new List<Building_LiquidTank>();
			RM_NetResult r = Store(origin);
			foreach (object t in r.Tanks)
			{
				if (t is Building_LiquidTank tank && tank.Spawned && tank.Map == origin.Map && RouteLiveOrBump(origin, r, t))
				{
					result.Add(tank);
				}
			}
			return result;
		}

		// ---------------------------------------------------------------- fill and draw plans (rev 2 §3.2, build step L3)
		private static List<RM_TankView> Views(List<Building_LiquidTank> tanks, LiquidDef liquid)
		{
			var v = new List<RM_TankView>(tanks.Count);
			foreach (Building_LiquidTank t in tanks)
			{
				v.Add(new RM_TankView(t.thingIDNumber, t.storedUnits, t.Capacity, !t.Empty && t.storedLiquid == liquid, t.Empty));
			}
			return v;
		}

		/// <summary>The store's tanks a machine may put liquid into (<paramref name="fill"/>: every job but Empty) or draw from
		/// (every job but Dump), rev 2 §3.2.</summary>
		private static List<Building_LiquidTank> Candidates(Thing origin, Building_LiquidTank except, bool fill)
		{
			List<Building_LiquidTank> tanks = TanksFor(origin);
			tanks.RemoveAll(t => t == except || (fill ? !t.TakesFromMachines : !t.GivesToMachines));
			return tanks;
		}

		private static List<(Building_LiquidTank tank, int units)> Parts(List<Building_LiquidTank> tanks, List<KeyValuePair<int, int>> plan)
		{
			return plan?.Select(p => (tanks[p.Key], p.Value)).ToList();
		}

		/// <summary>Where <paramref name="units"/> of <paramref name="liquid"/> go on <paramref name="origin"/>'s store: the fullest
		/// tank holding it first, then empty tanks, ties by id, split across tanks (RM_LiquidNetKernel.FillPlan, selftested).
		/// Null when it does not all fit.</summary>
		public static List<(Building_LiquidTank tank, int units)> FillPlan(Thing origin, LiquidDef liquid, int units, Building_LiquidTank except = null)
		{
			if (liquid == null)
			{
				return null;
			}
			List<Building_LiquidTank> tanks = Candidates(origin, except, true);
			return Parts(tanks, RM_LiquidNetKernel.FillPlan(Views(tanks, liquid), units));
		}

		/// <summary>Where <paramref name="units"/> of <paramref name="liquid"/> come from: the emptiest tank holding it first, ties
		/// by id, split across tanks (RM_LiquidNetKernel.DrawPlan). Null when the store holds fewer.</summary>
		public static List<(Building_LiquidTank tank, int units)> DrawPlan(Thing origin, LiquidDef liquid, int units, Building_LiquidTank except = null)
		{
			if (liquid == null)
			{
				return null;
			}
			List<Building_LiquidTank> tanks = Candidates(origin, except, false);
			return Parts(tanks, RM_LiquidNetKernel.DrawPlan(Views(tanks, liquid), units));
		}

		/// <summary>All the room <paramref name="origin"/>'s store has for <paramref name="liquid"/>.</summary>
		public static int Room(Thing origin, LiquidDef liquid, Building_LiquidTank except = null)
		{
			return liquid == null ? 0 : RM_LiquidNetKernel.FillRoom(Views(Candidates(origin, except, true), liquid));
		}

		/// <summary>All the <paramref name="liquid"/> <paramref name="origin"/>'s store holds.</summary>
		public static int Available(Thing origin, LiquidDef liquid, Building_LiquidTank except = null)
		{
			return liquid == null ? 0 : RM_LiquidNetKernel.DrawAvailable(Views(Candidates(origin, except, false), liquid));
		}

		/// <summary>The parts of <paramref name="plan"/> a move of <paramref name="moved"/> units actually committed: a Split leg
		/// puts a short move back from its LAST parts, so the first parts up to <paramref name="moved"/> are what crossed.</summary>
		public static IEnumerable<(Building_LiquidTank tank, int units)> Committed(List<(Building_LiquidTank tank, int units)> plan, int moved)
		{
			int left = moved;
			foreach ((Building_LiquidTank tank, int units) p in plan)
			{
				int u = System.Math.Min(left, p.units);
				if (u <= 0)
				{
					yield break;
				}
				yield return (p.tank, u);
				left -= u;
			}
		}

		private static readonly Dictionary<Map, RM_ConsumerRotation> rotations = new Dictionary<Map, RM_ConsumerRotation>();

		/// <summary>G9: the map's consumer rotation (two machines on one liquid take turns).</summary>
		public static RM_ConsumerRotation Rotation(Map map)
		{
			if (!rotations.TryGetValue(map, out RM_ConsumerRotation r))
			{
				foreach (Map m in rotations.Keys.Where(k => !Find.Maps.Contains(k)).ToList())
				{
					rotations.Remove(m);
				}
				r = rotations[map] = new RM_ConsumerRotation();
			}
			return r;
		}

		// ---------------------------------------------------------------- hose free-end ports (rev 2 §3.3-3.6, build step L6)
		/// <summary>The free ends with <paramref name="role"/> on <paramref name="origin"/>'s networks (refused networks excluded),
		/// in reel-id order: a pump's Intake sources and Outflow destinations.</summary>
		public static List<RM_NetPort> PortsOf(Thing origin, RM_FreeEndRole role)
		{
			var ports = new List<RM_NetPort>();
			if (origin?.Map == null)
			{
				return ports;
			}
			foreach (RM_NetComponent c in Components(origin.Map).ComponentsOf(origin))
			{
				if (c.Refused)
				{
					continue;
				}
				foreach (RM_NetPort p in c.Ports)
				{
					if (p.Role == role && p.Reel is CompHoseReel && !ports.Contains(p))
					{
						ports.Add(p);
					}
				}
			}
			ports.Sort((a, b) => ((CompHoseReel)a.Reel).parent.thingIDNumber.CompareTo(((CompHoseReel)b.Reel).parent.thingIDNumber));
			return ports;
		}

		/// <summary>The hose route from <paramref name="origin"/> to anything attached to one of its networks (a tank, a machine
		/// or a free-end port): the fewest hoses among the networks they share; null when they share none.</summary>
		public static List<RM_NetLink> RouteTo(Thing origin, object target)
		{
			if (origin?.Map == null || target == null)
			{
				return null;
			}
			RM_NetComponents comps = Components(origin.Map);
			List<RM_NetLink> best = null;
			foreach (RM_NetComponent c in comps.ComponentsOf(origin))
			{
				if (c.Refused || !c.Has(target))
				{
					continue;
				}
				List<RM_NetLink> r = comps.RouteIn(c, origin, target);
				if (r != null && (best == null || r.Count < best.Count))
				{
					best = r;
				}
			}
			return best;
		}

		/// <summary>Credit a COMMITTED move over the route to a port or any attached thing (L6: a pump's intake and outflow hoses).
		/// Same lease and tint rules as <see cref="Credit"/>; only inside the block of a Move that returned its units.</summary>
		public static void CreditTo(Thing origin, object target, LiquidDef liquid, int units, int cadence, System.Func<int, int> fillFrom = null)
		{
			if (origin?.Map == null || liquid == null || units <= 0)
			{
				return;
			}
			CreditRoute(origin.Map, RouteTo(origin, target), liquid, units, cadence, fillFrom);
		}

		// ---------------------------------------------------------------- held hose volume (rev 2 §3.7, build step L8)
		/// <summary>A fill source for the hoses a committed move crossed: up to n units out of <paramref name="tank"/> (when it holds
		/// <paramref name="liquid"/>), through the transfer service into the hose's ledger (RM_HoseHold.Fill adds what this returns).
		/// So "less arrives" (or a little more leaves) the first cycle a hose fills: never liquid from nothing.</summary>
		public static System.Func<int, int> FillFrom(Building_LiquidTank tank, LiquidDef liquid)
		{
			return n =>
			{
				if (tank == null || liquid == null || tank.storedLiquid != liquid)
				{
					return 0;
				}
				int k = System.Math.Min(n, tank.storedUnits);
				return k <= 0 ? 0 : RM_LiquidTransfer.Move(k, RM_TransferLeg.Store(j => tank.CanProvide(j), j => tank.TryRemoveLiquid(j), j => tank.TryAddLiquid(liquid, j)), RM_TransferLeg.Sink(null), out _);
			};
		}

		/// <summary>Units the hoses on the routes from <paramref name="origin"/> to <paramref name="targets"/> still need to be full
		/// of <paramref name="liquid"/> (a hose holding another liquid needs its whole capacity).</summary>
		public static int HoseNeed(Thing origin, IEnumerable<object> targets, LiquidDef liquid)
		{
			if (!RM_HoseSettings.hoseHoldsLiquid || origin?.Map == null)
			{
				return 0;
			}
			int need = 0;
			foreach (CompHoseReel r in RouteReels(origin, targets))
			{
				need += System.Math.Max(0, r.HeldCap - (r.heldLiquid == liquid ? r.heldUnits : 0));
			}
			return need;
		}

		private static List<CompHoseReel> RouteReels(Thing origin, IEnumerable<object> targets)
		{
			var reels = new List<CompHoseReel>();
			foreach (object t in targets)
			{
				List<RM_NetLink> route = t == null ? null : RouteTo(origin, t);
				if (route == null)
				{
					continue;
				}
				foreach (RM_NetLink l in route)
				{
					if (l.Reel is CompHoseReel r && !reels.Contains(r))
					{
						reels.Add(r);
					}
				}
			}
			return reels;
		}

		/// <summary>L8 world-to-world: a pump level whose hoses are not yet full goes INTO them (the fill is taken from the move
		/// itself, so nothing arrives this cycle). All <paramref name="units"/> are placed: a remainder past the last hose's room
		/// stays in it (a hose may hold up to one level over its capacity).</summary>
		public static void FillRoutes(Thing origin, IEnumerable<object> targets, LiquidDef liquid, int units)
		{
			int rem = units;
			CompHoseReel last = null;
			foreach (CompHoseReel r in RouteReels(origin, targets))
			{
				FillOne(r, origin.Map, liquid, n => { int g = System.Math.Min(n, rem); rem -= g; return g; });
				if (r.heldLiquid == liquid)
				{
					last = r;
				}
			}
			if (rem > 0 && last != null)
			{
				last.heldUnits += rem;
				rem = 0;
			}
			if (rem > 0)
			{
				// no hose took it (they changed under us): the level must still land somewhere real
				RM_LiquidSpill.Spill(origin.Map, origin.Position, liquid, rem);
			}
		}

		private static void FillOne(CompHoseReel r, Map map, LiquidDef liquid, System.Func<int, int> take)
		{
			object hl = r.heldLiquid;
			int held = r.heldUnits;
			RM_HoseHold.Fill(ref hl, ref held, r.HeldCap, liquid, take, (old, u) =>
			{
				// flush: the old liquid leaves out of the hose's far end first
				r.heldUnits = u;
				RM_LiquidSpill.DrainHeld(r, map, RM_LiquidSpill.DrainCell(r, map));
			});
			r.heldLiquid = hl as LiquidDef;
			r.heldUnits = held;
		}

		/// <summary>The hose links on the route from <paramref name="origin"/> to <paramref name="tank"/> (empty when it is reached by
		/// touch or pipe alone; null when it is not on the net).</summary>
		public static List<RM_NetLink> Route(Thing origin, Building_LiquidTank tank)
		{
			return tank != null && Store(origin).Routes.TryGetValue(tank, out List<RM_NetLink> r) ? r : null;
		}

		/// <summary>
		/// Credit a COMMITTED transfer (hose port step 6, FINAL §3.2; L1: only inside the block of a RM_LiquidTransfer.Move that
		/// returned its units): called once per tank leg at each of the 11 mutation sites
		/// (pump draw x2 and pour, converter input and output, pipe adapter in and out, reactor A, B and product, bath), never on
		/// a lookup, a failed call, venting or item output. Every reel on the route's hoses gets its flow lease extended and
		/// <paramref name="liquid"/> credited for its tint. The route is re-checked first (a hose wound in this tick drops it).
		/// <paramref name="cadence"/> is the crediting machine's cycle (250 for the pump and the rare-tick machines; a bath passes
		/// the hose release window, so one craft is one plump pulse).
		/// </summary>
		public static void Credit(Thing origin, Building_LiquidTank tank, LiquidDef liquid, int units, int cadence)
		{
			if (origin?.Map == null || tank == null || liquid == null || units <= 0)
			{
				return;
			}
			List<RM_NetLink> route = Route(origin, tank);
			CreditRoute(origin.Map, route, liquid, units, cadence, FillFrom(tank, liquid));
		}

		internal static void CreditRoute(Map map, List<RM_NetLink> route, LiquidDef liquid, int units, int cadence, System.Func<int, int> fillFrom = null)
		{
			if (route == null || route.Count == 0)
			{
				return;
			}
			RM_HoseLinks idx = RM_HoseLinks.For(map);
			if (!RM_LiquidNetKernel.RouteLive(route, idx.Live))
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			foreach (RM_NetLink l in route)
			{
				(l.Reel as CompHoseReel)?.CreditFlow(liquid, units, now, cadence);
			}
			// L8 (rev 2 §3.7): each hose the move crossed fills to its capacity out of the move's own tank
			if (RM_HoseSettings.hoseHoldsLiquid && fillFrom != null)
			{
				foreach (RM_NetLink l in route)
				{
					if (l.Reel is CompHoseReel r)
					{
						FillOne(r, map, liquid, fillFrom);
					}
				}
			}
		}

		// ---------------------------------------------------------------- tank jobs: the settle (rev 2 §3.2, build step L4)
		/// <summary>State read (probe, selftests): settles run and tank-to-tank units moved this session.</summary>
		public static int Settles, SettledUnits;

		private static readonly HashSet<Map> toldAboutHoses = new HashSet<Map>();

		/// <summary>Once per pump cycle (RM_PumpMath.CycleTicks): every component holding a Fill or Empty tank settles once
		/// (RM_LiquidNetKernel.SettlePlan, selftested): Empty tanks send to Fill then Store tanks, Fill tanks pull from Empty then
		/// Store tanks, tankUnitsPerCycle each, from the stock present at the start. Owner ruling #9 ("a tank would pass liquid on
		/// to a hose screwed into it, without a pump needed") is met by these jobs: one click on the tank. Off in Mod Settings
		/// (tankModesEnabled): every tank is Store, nothing moves tank to tank. Dump tanks drain through outflow ends (L7).</summary>
		public static void SettleTick(Map map)
		{
			if (map == null || !RM_HoseSettings.tankModesEnabled)
			{
				return;
			}
			var movers = new List<Building_LiquidTank>();
			var dumps = new List<Building_LiquidTank>();
			foreach (Building b in map.listerBuildings.allBuildingsColonist)
			{
				if (b is Building_LiquidTank t && (t.EffectiveMode == RM_TankMode.Fill || t.EffectiveMode == RM_TankMode.Empty))
				{
					movers.Add(t);
				}
				else if (b is Building_LiquidTank d && d.EffectiveMode == RM_TankMode.Dump && !d.Empty)
				{
					dumps.Add(d);
				}
			}
			TellAboutTankHoses(map, movers.Count + dumps.Count);
			if (movers.Count == 0 && dumps.Count == 0)
			{
				return;
			}
			RM_NetComponents comps = Components(map);
			DumpDrain(map, comps, dumps);
			var done = new HashSet<RM_NetComponent>();
			int cycle = Find.TickManager.TicksGame / RM_PumpMath.CycleTicks;
			int per = System.Math.Max(1, RM_HoseSettings.tankUnitsPerCycle);
			foreach (Building_LiquidTank mover in movers)
			{
				foreach (RM_NetComponent c in comps.ComponentsOf(mover))
				{
					if (c.Refused || !done.Add(c))
					{
						continue;
					}
					var tanks = c.Tanks.OfType<Building_LiquidTank>().Where(t => t.Spawned && t.Map == map).ToList();
					var view = tanks.Select(t => new RM_SettleTank(t.thingIDNumber, t.storedUnits, t.Capacity, t.storedLiquid, t.EffectiveMode)).ToList();
					Settles++;
					foreach ((int si, int di, int n) in RM_LiquidNetKernel.SettlePlan(view, per, cycle))
					{
						Building_LiquidTank src = tanks[si], dst = tanks[di];
						LiquidDef liquid = src.storedLiquid;
						List<RM_NetLink> route = comps.RouteIn(c, src, dst);
						// L1 (§4): remove from the source, add to the destination, put back on a refusal; credit only a committed move
						if (RM_LiquidTransfer.Move(n, RM_TransferLeg.Store(k => src.CanProvide(k), k => src.TryRemoveLiquid(k), k => src.TryAddLiquid(liquid, k)),
							RM_TransferLeg.Store(k => dst.CanAccept(liquid, k), k => dst.TryAddLiquid(liquid, k), k => dst.TryRemoveLiquid(k)), out RM_MoveOutcome mv) > 0)
						{
							CreditRoute(map, route, liquid, mv.Moved, RM_PumpMath.CycleTicks, FillFrom(dst, liquid));   // credit site: tank settle
							SettledUnits += mv.Moved;
						}
						if (mv.Lost > 0)
						{
							Log.ErrorOnce("[FlowWorks] tank settle: " + dst.LabelCap + " refused " + n + " " + liquid?.defName + " and " + src.LabelCap +
								" would not take them back", 0x4F5A71);
						}
					}
				}
			}
		}

		/// <summary>State read (probe, selftests): units Dump tanks drained out of Outflow ends this session.</summary>
		public static int DumpedUnits;

		/// <summary>Settle step 3 (rev 2 §3.2, §3.5, build step L7): every Dump tank drains slowly, with no pump, out of the Outflow
		/// ends on its networks (reel-id order; an end takes one drain per settle): a whole level into a channel cell that can take
		/// it, or up to dumpUnitsPerCycle onto dry ground as a cleanable spill (RM_LiquidNetKernel.DumpTake). A blocked end (full or
		/// foreign channel, wall, water) moves nothing. With no Outflow end a Dump tank waits.</summary>
		private static void DumpDrain(Map map, RM_NetComponents comps, List<Building_LiquidTank> dumps)
		{
			if (dumps.Count == 0)
			{
				return;
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			var usedEnds = new HashSet<RM_NetPort>();
			int level = RM_PumpMath.TankUnitsPerLevel;
			foreach (Building_LiquidTank tank in dumps.OrderBy(t => t.thingIDNumber))
			{
				int left = System.Math.Max(0, RM_HoseSettings.dumpUnitsPerCycle);
				foreach (RM_NetComponent c in comps.ComponentsOf(tank))
				{
					if (c.Refused)
					{
						continue;
					}
					foreach (RM_NetPort port in c.Ports.Where(p => p.Role == RM_FreeEndRole.Outflow && p.Reel is CompHoseReel).OrderBy(p => ((CompHoseReel)p.Reel).parent.thingIDNumber))
					{
						if (left <= 0 || tank.Empty || usedEnds.Contains(port) || !(port.Cell is IntVec3 end))
						{
							continue;
						}
						LiquidDef liquid = tank.storedLiquid;
						FluidDef fluid = liquid.canalFluid;
						RM_OutletKind kind = RM_LiquidSpill.Outlet(map, ex, end, liquid, fluid, out IntVec3 cell);
						int n = kind == RM_OutletKind.Blocked ? 0 : RM_LiquidNetKernel.DumpTake(left, tank.storedUnits, level, RM_LiquidSpill.WholeLevels(kind));
						if (n <= 0)
						{
							continue;
						}
						RM_TransferLeg outlet = RM_LiquidSpill.OutletLeg(map, ex, kind, cell, liquid, fluid);
						if (RM_LiquidTransfer.Move(n, RM_TransferLeg.Store(k => tank.CanProvide(k), k => tank.TryRemoveLiquid(k), k => tank.TryAddLiquid(liquid, k)), outlet, out RM_MoveOutcome mv) > 0)
						{
							CreditRoute(map, comps.RouteIn(c, tank, port), liquid, mv.Moved, RM_PumpMath.CycleTicks, FillFrom(tank, liquid));   // credit site: dump drain
							left -= mv.Moved;
							usedEnds.Add(port);
							DumpedUnits += mv.Moved;
						}
					}
				}
			}
		}

		/// <summary>§3.11: a hose between two tanks used to even their levels by itself. Once per map, when such a hose is laid and
		/// no tank has a job, one message says how liquid moves now.</summary>
		private static void TellAboutTankHoses(Map map, int movers)
		{
			if (movers > 0 || toldAboutHoses.Contains(map))
			{
				return;
			}
			foreach (RM_NetLink l in RM_HoseLinks.For(map).All)
			{
				if (l.A is Building_LiquidTank a && l.B is Building_LiquidTank && a.Faction == Faction.OfPlayer)
				{
					toldAboutHoses.Add(map);
					Messages.Message("RMFlow_TankJobsMessage".Translate(), a, MessageTypeDefOf.NeutralEvent, historical: false);
					return;
				}
			}
		}
	}

	/// <summary>
	/// RM_HoseLinks (FINAL §3.1 "Index"; L2: kept per topology revision): every LIVE flexible hose on a map as a net conductor.
	/// A reel R contributes one link inlet(R) - far(R):
	///   inlet(R) = R itself as a RELAY vertex when other hoses end on R's intake (FeedersOf), else R's coupled neighbour when it
	///              has a hydraulic role; the reel footprint otherwise never conducts;
	///   far(R)   = the next reel when R's hose ends on its intake (a relay vertex), else what the free end couples to, when it
	///              has a hydraulic role, else -- a free end with a role (rev 2 §3.4; Capped until build step L5 adds the
	///              gizmo) -- a PORT of the hose's component.
	/// Live = hoses enabled, R Laid (Dropped and every carry/wind state carry nothing), R's lay non-null (a refused lay carries
	/// nothing), both ends spawned.
	/// The link list is rebuilt only when its SIGNATURE changes (each live reel's id, inlet and far identity, read from the
	/// reels' own 60-tick port caches and the relay index): that check is the backstop that bumps the map's topology revision
	/// for any reel state, port or coupling change nobody announced (G11). Nothing else is rebuilt per tick.
	/// </summary>
	public sealed class RM_HoseLinks
	{
		private static readonly Dictionary<Map, RM_HoseLinks> byMap = new Dictionary<Map, RM_HoseLinks>();
		private readonly Map map;
		private int checkedTick = int.MinValue;
		private ulong sig;
		private bool built;
		private readonly List<RM_NetLink> all = new List<RM_NetLink>();
		private readonly Dictionary<object, List<RM_NetLink>> at = new Dictionary<object, List<RM_NetLink>>();
		private static readonly List<RM_NetLink> None = new List<RM_NetLink>();

		/// <summary>State read: link-list rebuilds this session (the probe's perf row); signature checks are not counted.</summary>
		public static int Rebuilds;

		/// <summary>L5 (rev 2 §3.4): the role of a reel's free end in force (Capped with free-end roles off in Mod Settings).</summary>
		public static RM_FreeEndRole FreeEndRole(CompHoseReel r) => RM_HoseSettings.freeEndRolesEnabled ? r.freeEndRole : RM_FreeEndRole.Capped;

		private RM_HoseLinks(Map map)
		{
			this.map = map;
		}

		public static RM_HoseLinks For(Map map)
		{
			if (!byMap.TryGetValue(map, out RM_HoseLinks l))
			{
				// drop indexes of maps that are gone
				foreach (Map m in byMap.Keys.Where(k => !Find.Maps.Contains(k)).ToList())
				{
					byMap.Remove(m);
				}
				l = byMap[map] = new RM_HoseLinks(map);
			}
			l.Refresh();
			return l;
		}

		public IReadOnlyList<RM_NetLink> All => all;

		public IList<RM_NetLink> At(object v)
		{
			return v != null && at.TryGetValue(v, out List<RM_NetLink> l) ? l : None;
		}

		/// <summary>The eligibility predicate, re-run on a route's links at transfer time (FINAL §3.5).</summary>
		public bool Live(RM_NetLink l)
		{
			return l?.Reel is CompHoseReel r && Eligible(r) && Spawned(l.A) && Spawned(l.B);
		}

		private static bool Spawned(object v)
		{
			if (v is Thing t)
			{
				return t.Spawned;
			}
			if (v is CompHoseReel r)
			{
				return r.parent.Spawned;
			}
			return v is IntVec3 || v is RM_NetPort;
		}

		internal static bool Eligible(CompHoseReel r)
		{
			return RM_HoseSettings.enabled && r?.parent != null && r.parent.Spawned && r.carry == HoseCarryState.Laid && r.lay != null;
		}

		private static long IdOf(object v)
		{
			if (v is Thing t)
			{
				return t.thingIDNumber;
			}
			if (v is CompHoseReel r)
			{
				return -1L - r.parent.thingIDNumber;
			}
			if (v is IntVec3 c)
			{
				return ((long)c.x << 40) ^ ((long)c.z << 20) ^ 0x5A5AL;
			}
			if (v is RM_NetPort p)
			{
				return ((long)(p.Cell is IntVec3 pc ? pc.x * 7919 + pc.z : 0) << 8) ^ (long)p.Role ^ 0x7E57L;
			}
			return 0;
		}

		/// <summary>The (inlet, far) of reel r if it forms a live link now, else false.</summary>
		private static bool Ends(RM_MapComponent_Hoses comp, CompHoseReel r, out object inlet, out object far)
		{
			inlet = far = null;
			if (!Eligible(r))
			{
				return false;
			}
			if (comp.IsFed(r))
			{
				inlet = r;
			}
			else
			{
				Thing p = r.Port();
				if (p != null && RM_LiquidNet.RoleOfThing(p) != RM_NetRole.None)
				{
					inlet = RM_LiquidNet.VertexOf(p);
				}
			}
			CompHoseReel relay = comp.FeedsInto(r);
			if (relay != null)
			{
				far = relay;
			}
			else
			{
				HoseFreeEnd e = r.FreeEnd();
				if (e.Port != null && RM_LiquidNet.RoleOfThing(e.Port) != RM_NetRole.None)
				{
					far = RM_LiquidNet.VertexOf(e.Port);
				}
				else if (e.Port == null)
				{
					RM_FreeEndRole role = FreeEndRole(r);
					if (role != RM_FreeEndRole.Capped)
					{
						far = new RM_NetPort { Reel = r, Cell = r.far, Role = role };
					}
				}
			}
			return inlet != null && far != null && Spawned(inlet) && Spawned(far) && !Equals(inlet, far);
		}

		private void Refresh()
		{
			int now = Find.TickManager?.TicksGame ?? 0;
			if (built && checkedTick == now)
			{
				return;
			}
			checkedTick = now;
			RM_MapComponent_Hoses comp = map.GetComponent<RM_MapComponent_Hoses>();
			ulong h = RM_LiquidNetKernel.SigSeed ^ (RM_HoseSettings.enabled ? 1UL : 0UL);
			// a copy: IsFed / FeedsInto may rebuild the relay index (and its order list) mid-loop
			List<CompHoseReel> reels = comp != null && RM_HoseSettings.enabled ? new List<CompHoseReel>(comp.OrderedReels()) : null;
			if (reels != null)
			{
				foreach (CompHoseReel r in reels)
				{
					if (Ends(comp, r, out object inlet, out object far))
					{
						h = RM_LiquidNetKernel.SigStep(h, r.parent.thingIDNumber, IdOf(inlet), IdOf(far));
					}
				}
			}
			if (built && h == sig)
			{
				return;
			}
			sig = h;
			built = true;
			Rebuilds++;
			all.Clear();
			at.Clear();
			if (reels != null)
			{
				foreach (CompHoseReel r in reels)
				{
					if (!Ends(comp, r, out object inlet, out object far))
					{
						continue;
					}
					var l = new RM_NetLink { Id = all.Count, A = inlet, B = far, Reel = r };
					all.Add(l);
					Add(inlet, l);
					Add(far, l);
				}
			}
			RM_LiquidNet.Bump(map);
		}

		private void Add(object v, RM_NetLink l)
		{
			if (!at.TryGetValue(v, out List<RM_NetLink> list))
			{
				at[v] = list = new List<RM_NetLink>();
			}
			list.Add(l);
		}
	}

	/// <summary>L2 (rev 2 §3.1): a pipe, tank or machine spawning or despawning bumps its map's topology revision. Building is
	/// patched (not Thing), so the cost is one cached per-def lookup per building spawn.</summary>
	[HarmonyLib.HarmonyPatch(typeof(Building), nameof(Building.SpawnSetup))]
	[RimMandrake.Shared.PatchFeature("Universal pipes", typeof(RM_MachinerySettings), "universalPipesEnabled")]
	public static class RM_Patch_NetTopologySpawn
	{
		public static void Postfix(Building __instance, Map map)
		{
			if (RM_LiquidNet.ChangesTopology(__instance))
			{
				RM_LiquidNet.Bump(map);
			}
		}
	}

	/// <summary>L9: a tank or machine changing hands (claimed, captured) changes whether it joins (liquid theft off): bump.</summary>
	[HarmonyLib.HarmonyPatch(typeof(Thing), nameof(Thing.SetFaction))]
	[RimMandrake.Shared.PatchFeature("Universal pipes", typeof(RM_MachinerySettings), "universalPipesEnabled")]
	public static class RM_Patch_NetTopologyFaction
	{
		public static void Postfix(Thing __instance)
		{
			if (__instance is Building && __instance.Spawned && RM_LiquidNet.ChangesTopology(__instance))
			{
				RM_LiquidNet.Bump(__instance.Map);
			}
		}
	}

	[HarmonyLib.HarmonyPatch(typeof(Building), nameof(Building.DeSpawn))]
	[RimMandrake.Shared.PatchFeature("Universal pipes", typeof(RM_MachinerySettings), "universalPipesEnabled")]
	public static class RM_Patch_NetTopologyDespawn
	{
		public static void Prefix(Building __instance, out Map __state)
		{
			__state = __instance.Map;
		}

		public static void Postfix(Building __instance, Map __state)
		{
			if (RM_LiquidNet.ChangesTopology(__instance))
			{
				RM_LiquidNet.Bump(__state);
			}
		}
	}
}
