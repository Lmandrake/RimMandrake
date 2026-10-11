using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.Machinery.Kits;
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
			return t == null || !t.Spawned ? RM_NetRole.None : RoleOfKind(t);
		}

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
			long key = RM_LiquidNetKernel.RevisionKey(s.revision, RM_MachinerySettings.universalPipesEnabled, RM_HoseSettings.enabled);
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

		private static List<Building_LiquidTank> Candidates(Thing origin, Building_LiquidTank except)
		{
			List<Building_LiquidTank> tanks = TanksFor(origin);
			if (except != null)
			{
				tanks.Remove(except);
			}
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
			List<Building_LiquidTank> tanks = Candidates(origin, except);
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
			List<Building_LiquidTank> tanks = Candidates(origin, except);
			return Parts(tanks, RM_LiquidNetKernel.DrawPlan(Views(tanks, liquid), units));
		}

		/// <summary>All the room <paramref name="origin"/>'s store has for <paramref name="liquid"/>.</summary>
		public static int Room(Thing origin, LiquidDef liquid, Building_LiquidTank except = null)
		{
			return liquid == null ? 0 : RM_LiquidNetKernel.FillRoom(Views(Candidates(origin, except), liquid));
		}

		/// <summary>All the <paramref name="liquid"/> <paramref name="origin"/>'s store holds.</summary>
		public static int Available(Thing origin, LiquidDef liquid, Building_LiquidTank except = null)
		{
			return liquid == null ? 0 : RM_LiquidNetKernel.DrawAvailable(Views(Candidates(origin, except), liquid));
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
			CreditRoute(origin.Map, route, liquid, units, cadence);
		}

		internal static void CreditRoute(Map map, List<RM_NetLink> route, LiquidDef liquid, int units, int cadence)
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
		}

		// ---------------------------------------------------------------- a tank feeds a hose screwed onto it (owner Q7)
		/// <summary>Owner, typed 2026-10-11: "Yes, a tank would pass liquid on to a hose screwed into it, without a pump needed."
		/// Every <see cref="RM_PumpMath.CycleTicks"/>, each live hose with a TANK at an end passes liquid from that tank across the
		/// hose to the emptiest compatible tank on that hose's component (another tank, a pipe run's tanks, or further along a
		/// relay chain), toward an equal fill, at most one pump level (5 units) per cycle (RM_LiquidNetKernel.TankFeedUnits). A
		/// tank is still never a conductor: the tanks of a pipe run the feeding tank stands in are another component, not reached
		/// through it. (Build step L4 replaces this equalising feed with tank modes.)</summary>
		public static void TankFeedTick(Map map)
		{
			if (map == null || !RM_LiquidNetKernel.TankFeedOn(RM_HoseSettings.enabled, RM_HoseSettings.tanksFeedHoses))
			{
				return;
			}
			RM_HoseLinks idx = RM_HoseLinks.For(map);
			RM_NetComponents comps = Components(map);
			int units = RM_PumpMath.TankUnitsPerLevel;
			foreach (RM_NetLink l in idx.All)
			{
				foreach (object end in new[] { l.A, l.B })
				{
					if (!(end is Building_LiquidTank src) || src.Empty || RoleOfThing(src) != RM_NetRole.Tank)
					{
						continue;
					}
					RM_NetResult across = comps.TanksAcross(l, src);   // L2: the tanks on this hose's component, routes from its tree
					var dsts = new List<Building_LiquidTank>();
					var data = new List<(int units, int cap, bool compatible)>();
					foreach (object o in across.Tanks)
					{
						if (o is Building_LiquidTank d && d != src)
						{
							dsts.Add(d);
							data.Add((d.storedUnits, d.Capacity, d.CanAccept(src.storedLiquid, 1)));
						}
					}
					int pick = RM_LiquidNetKernel.FeedTarget(data, src.storedUnits, src.Capacity, units);
					if (pick < 0)
					{
						continue;
					}
					Building_LiquidTank dst = dsts[pick];
					int n = RM_LiquidNetKernel.TankFeedUnits(src.storedUnits, src.Capacity, dst.storedUnits, dst.Capacity, true, units);
					LiquidDef liquid = src.storedLiquid;
					List<RM_NetLink> route = across.Routes[dst];
					// L1 (§4): remove from the source, add to the destination, put back on a refusal; credit only a committed move
					if (RM_LiquidTransfer.Move(n, RM_TransferLeg.Store(k => src.CanProvide(k), k => src.TryRemoveLiquid(k), k => src.TryAddLiquid(liquid, k)),
						RM_TransferLeg.Store(k => dst.CanAccept(liquid, k), k => dst.TryAddLiquid(liquid, k), k => dst.TryRemoveLiquid(k)), out RM_MoveOutcome mv) > 0)
					{
						CreditRoute(map, route, liquid, mv.Moved, RM_PumpMath.CycleTicks);   // credit site: tank feed (owner Q7)
					}
					if (mv.Lost > 0)
					{
						Log.ErrorOnce("[FlowWorks] tank feed: " + dst.LabelCap + " refused " + n + " " + liquid?.defName + " and " + src.LabelCap +
							" would not take them back", 0x4F5A71);
					}
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

		/// <summary>L5 hook: the role of a reel's free end (Capped until the reel carries rmFreeEndRole).</summary>
		public static System.Func<CompHoseReel, RM_FreeEndRole> FreeEndRole = r => RM_FreeEndRole.Capped;

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
