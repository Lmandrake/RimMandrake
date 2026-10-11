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
		/// <summary>Search cap: a pipe run longer than this is not followed further (PROVISIONAL).</summary>
		public const int MaxPipeCells = RM_LiquidNetKernel.MaxVisits;

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

		// ---------------------------------------------------------------- the graph the kernel walks
		internal sealed class MapGraph : IRM_NetGraph
		{
			private readonly Map map;
			private readonly RM_HoseLinks links;

			public MapGraph(Map map)
			{
				this.map = map;
				links = RM_HoseLinks.For(map);
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
				return RoleOfThing(v as Thing);
			}

			private IEnumerable<object> TanksIn(IEnumerable<IntVec3> cells, object exclude)
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
						if (things[i] is Building_LiquidTank tank && tank != exclude)
						{
							yield return tank;
						}
					}
				}
			}

			public IEnumerable<object> OriginTanks(object origin)
			{
				return origin is Thing t ? TanksIn(GenAdj.CellsAdjacent8Way(t), t) : Enumerable.Empty<object>();
			}

			public IEnumerable<object> OriginPipeCells(object origin)
			{
				if (!(origin is Thing t))
				{
					yield break;
				}
				foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(t))
				{
					if (c.InBounds(map) && HasPipe(c, map))
					{
						yield return c;
					}
				}
				// A machine standing on a pipe (pipes are under-floor-ish) also joins that run.
				foreach (IntVec3 c in t.OccupiedRect())
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
				foreach (object t in TanksIn(GenAdj.CellsAdjacentCardinal(c, Rot4.North, IntVec2.One), null))
				{
					yield return t;
				}
				foreach (object t in TanksIn(new[] { c }, null))
				{
					yield return t;
				}
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

		private static readonly Dictionary<Map, RM_NetCache> caches = new Dictionary<Map, RM_NetCache>();

		/// <summary>The per-tick cache of a map's walks (hose port step 7).</summary>
		public static RM_NetCache CacheOf(Map map)
		{
			if (!caches.TryGetValue(map, out RM_NetCache c))
			{
				foreach (Map m in caches.Keys.Where(k => !Find.Maps.Contains(k)).ToList())
				{
					caches.Remove(m);
				}
				c = caches[map] = new RM_NetCache();
			}
			return c;
		}

		/// <summary>The kernel's walk from <paramref name="origin"/> on its map, once per origin per tick (RM_NetCache).</summary>
		public static RM_NetResult Walk(Thing origin)
		{
			if (origin?.Map == null)
			{
				return new RM_NetResult();
			}
			Map map = origin.Map;
			return CacheOf(map).Get(origin.thingIDNumber, Find.TickManager.TicksGame, () => RM_LiquidNetKernel.Walk(new MapGraph(map), origin));
		}

		/// <summary>FINAL §3.5: a tank whose route has a dead link (a hose wound in, dropped or despawned since this tick's walk) is
		/// not on the net for this transfer, and the origin's walk is redone on its next use.</summary>
		private static bool RouteLiveOrDirty(Thing origin, RM_NetResult r, object tank)
		{
			if (!r.Routes.TryGetValue(tank, out List<RM_NetLink> route) || route.Count == 0)
			{
				return true;
			}
			if (RM_LiquidNetKernel.RouteLive(route, RM_HoseLinks.For(origin.Map).Live))
			{
				return true;
			}
			CacheOf(origin.Map).MarkDirty(origin.thingIDNumber);
			return false;
		}

		/// <summary>Every liquid tank on <paramref name="origin"/>'s net, nearest-first (adjacent tanks lead).
		/// Never includes <paramref name="origin"/> itself.</summary>
		public static List<Building_LiquidTank> TanksFor(Thing origin)
		{
			var result = new List<Building_LiquidTank>();
			RM_NetResult r = Walk(origin);
			foreach (object t in r.Tanks)
			{
				if (t is Building_LiquidTank tank && tank.Spawned && RouteLiveOrDirty(origin, r, t))
				{
					result.Add(tank);
				}
			}
			return result;
		}

		/// <summary>First tank on the net that can take <paramref name="units"/> of <paramref name="liquid"/>,
		/// preferring one already holding it (so a run fills one tank before opening the next).</summary>
		public static Building_LiquidTank TankToFill(Thing origin, LiquidDef liquid, int units, Building_LiquidTank except = null)
		{
			Building_LiquidTank empty = null;
			foreach (Building_LiquidTank t in TanksFor(origin))
			{
				if (t == except || !t.CanAccept(liquid, units))
				{
					continue;
				}
				if (!t.Empty)
				{
					return t;
				}
				empty = empty ?? t;
			}
			return empty;
		}

		/// <summary>The hose links on the route from <paramref name="origin"/> to <paramref name="tank"/> (empty when it is reached by
		/// touch or pipe alone; null when it is not on the net).</summary>
		public static List<RM_NetLink> Route(Thing origin, Building_LiquidTank tank)
		{
			return tank != null && Walk(origin).Routes.TryGetValue(tank, out List<RM_NetLink> r) ? r : null;
		}

		/// <summary>
		/// Credit a SUCCESSFUL transfer (hose port step 6, FINAL §3.2): called once per tank leg at each of the 11 mutation sites
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
		/// hose to the emptiest compatible tank it reaches on the other side (another tank, a pipe run's tanks, or further along a
		/// relay chain), toward an equal fill, at most one pump level (5 units) per cycle (RM_LiquidNetKernel.TankFeedUnits). A
		/// tank is still never a conductor: the tanks of a pipe run the feeding tank stands in are not reached through it.</summary>
		public static void TankFeedTick(Map map)
		{
			if (map == null || !RM_HoseSettings.enabled)
			{
				return;
			}
			RM_HoseLinks idx = RM_HoseLinks.For(map);
			var graph = new MapGraph(map);
			int units = RM_PumpMath.TankUnitsPerLevel;
			foreach (RM_NetLink l in idx.All)
			{
				foreach (object end in new[] { l.A, l.B })
				{
					if (!(end is Building_LiquidTank src) || src.Empty || RoleOfThing(src) != RM_NetRole.Tank)
					{
						continue;
					}
					RM_NetResult across = RM_LiquidNetKernel.Across(graph, l, src);
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
					if (n > 0 && src.TryRemoveLiquid(n))
					{
						dst.TryAddLiquid(liquid, n);
						CreditRoute(map, across.Routes[dst], liquid, n, RM_PumpMath.CycleTicks);
					}
				}
			}
		}
	}

	/// <summary>
	/// RM_HoseLinks (FINAL §3.1 "Index"): every LIVE flexible hose on a map as a net link, rebuilt in full at most once per tick
	/// on first use, from the reels' existing 60-tick port caches and the relay index -- so a port that changes (none -> X,
	/// X -> Y) is always seen. A reel R contributes one link inlet(R) - far(R):
	///   inlet(R) = R itself as a RELAY vertex when other hoses end on R's intake (FeedersOf), else R's coupled neighbour when it
	///              has a hydraulic role; the reel footprint otherwise never conducts;
	///   far(R)   = the next reel when R's hose ends on its intake (a relay vertex), else what the free end couples to, when it
	///              has a hydraulic role.
	/// Live = hoses enabled, R Laid (Dropped and every carry/wind state carry nothing), R's lay non-null (a refused lay carries
	/// nothing), both ends spawned.
	/// </summary>
	public sealed class RM_HoseLinks
	{
		private static readonly Dictionary<Map, RM_HoseLinks> byMap = new Dictionary<Map, RM_HoseLinks>();
		private readonly Map map;
		private int builtTick = int.MinValue;
		private readonly List<RM_NetLink> all = new List<RM_NetLink>();
		private readonly Dictionary<object, List<RM_NetLink>> at = new Dictionary<object, List<RM_NetLink>>();
		private static readonly List<RM_NetLink> None = new List<RM_NetLink>();

		/// <summary>State read: index rebuilds this session (the probe's perf row).</summary>
		public static int Rebuilds;

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
			return v is IntVec3;
		}

		internal static bool Eligible(CompHoseReel r)
		{
			return RM_HoseSettings.enabled && r?.parent != null && r.parent.Spawned && r.carry == HoseCarryState.Laid && r.lay != null;
		}

		private void Refresh()
		{
			int now = Find.TickManager?.TicksGame ?? 0;
			if (builtTick == now)
			{
				return;
			}
			builtTick = now;
			Rebuilds++;
			all.Clear();
			at.Clear();
			RM_MapComponent_Hoses comp = map.GetComponent<RM_MapComponent_Hoses>();
			if (comp == null || !RM_HoseSettings.enabled)
			{
				return;
			}
			// the relay adjacency is the map component's shared index (G1.17, review S1): built once in O(reels), read here O(1)
			var reels = new List<CompHoseReel>(comp.OrderedReels());
			foreach (CompHoseReel r in reels)
			{
				if (!Eligible(r))
				{
					continue;
				}
				object inlet = null;
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
				object far = null;
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
				}
				if (inlet == null || far == null || !Spawned(inlet) || !Spawned(far) || Equals(inlet, far))
				{
					continue;
				}
				var l = new RM_NetLink { Id = all.Count, A = inlet, B = far, Reel = r };
				all.Add(l);
				Add(inlet, l);
				Add(far, l);
			}
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
}
