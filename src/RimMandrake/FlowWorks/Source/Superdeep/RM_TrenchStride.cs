using System;
using System.Collections.Generic;
using HarmonyLib;
using Unity.Collections;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// TITAN_TRENCHES_WIRE_MIND_THE_GAP — titans step over trenches narrower than a quarter of their breadth (owner, by card
	/// 2026-10-18; the rule and its numbers are HugeThings': WallsSlots.StepsOverTrench / WidestTrenchSteppedOver). A creature
	/// of stride s (the widest trench it steps over, RM_TrenchStrideMath) sees every dug cell of trench width &lt;= s as ground,
	/// and every judge of a walk agrees, because each reads the SAME stride view:
	///
	///   • A* edges: per-stride cliff masks (this class), derived exactly as RM_CliffMask derives the plain ones but from the
	///     bridged depth, swapped in after RM_CliffMask's own swap for a pawn with a stride. Two views, composed with the
	///     suspension underpass (TRENCH_STRIDE_UNDERPASS_FIX_ONE_BUG): the deck view (decks are ground) and, while a deck the
	///     floor band passes under stands, the floor view (RM_CliffMask's under masks), each bridged over its own trench widths.
	///     A strider in the floor band or down in a hole plans on the floor view; one astride a trench it steps over, on the deck
	///     view (RM_TrenchStrideMath.StriderUsesFloorView), and it steps from there ONTO a deck, never under it.
	///   • Reachability veto and the hold: RM_PocketGrid.ForPawn hands such a pawn the pocket grid labelled on the bridged depth
	///     (RM_SuperdeepTrap.RelativeVeto, IsHeldAtRelative, IsTrapped, InOwnPocketTooNarrow).
	///   • The step floor, the jump drop and the fall detector: <see cref="StepDepthFor"/> (a bridged cell is depth 0 to it), so
	///     walking across never fails the pather and never reads as a falling arrival — it does not fall in, walked or shoved.
	///   • The walked step's cost: RM_Patch_PitStepCost prices a step onto or off a bridged cell as surface walking.
	///   Known limit: route PLANNING still reads the shared per-map path grid, where a dug cell costs its dry terrain (a
	///   pawn-less grid; per-request offsets only add). A titan therefore walks round a short detour and steps over when the way
	///   round is long — it is never refused the crossing. The absolute-rule branch (relative climb off) is unchanged.
	///
	/// CROSS-MOD (no assembly reference either way; each mod loads alone): HugeThings registers a BCL delegate
	/// <c>Func&lt;Pawn, int&gt;</c> in the AppDomain slot <see cref="HookKey"/> (RimMandrake.TitanicCreatures.TrenchStrideHook) from
	/// its [StaticConstructorOnStartup]; this class reads the slot once, lazily, on the first in-game query. HugeThings absent: no
	/// delegate, every stride 0, nothing here runs past a null check, and no stride mask is ever allocated.
	/// </summary>
	public static class RM_TrenchStride
	{
		/// <summary>The registration slot. HugeThings: TrenchStrideHook.Key. Never rename one without the other.</summary>
		public const string HookKey = "RimMandrake.TrenchStride.v1";

		private static Func<Pawn, int> hook;
		private static bool resolved;

		/// <summary>True once HugeThings' delegate was found (bridge/proof read).</summary>
		public static bool Registered
		{
			get
			{
				Resolve();
				return hook != null;
			}
		}

		private static void Resolve()
		{
			if (resolved)
			{
				return;
			}
			resolved = true;
			hook = AppDomain.CurrentDomain.GetData(HookKey) as Func<Pawn, int>;
		}

		/// <summary>The widest trench (cells) this pawn steps over: 0 with HugeThings absent, the rule off, a flyer, or no titan.
		/// Only under the relative rule's cliff masks (the branch this wiring covers).</summary>
		public static int StrideOf(Pawn p)
		{
			if (p == null || !RM_CliffMask.On)
			{
				return 0;
			}
			Resolve();
			if (hook == null)
			{
				return 0;
			}
			int s;
			try
			{
				s = hook(p);
			}
			catch (Exception e)
			{
				Log.ErrorOnce("[RimMandrake.FlowWorks] trench stride hook threw (" + e.GetType().Name + "): titans no longer step over trenches. " + e.Message, 0x7a3c19);
				hook = null;
				return 0;
			}
			return RM_TrenchStrideMath.ClampStride(s);
		}

		// ── per-map trench widths (main thread, or GatherData with the main thread blocked) ─────────────

		/// <summary>TRENCH_STRIDE_UNDERPASS_FIX_ONE_BUG: the two views of the cliff masks a stride composes with. The DECK view
		/// (RM_PocketGrid.EffectiveDepth: every intact deck is ground at its walking height) and the FLOOR view (a suspension deck
		/// the floor band passes under reads as the hole beneath; RM_CliffMask's under masks), each with its own trench widths.</summary>
		public const int DeckView = 0, FloorView = 1, Views = 2;

		private sealed class Runs
		{
			public int generation = int.MinValue;
			public readonly byte[][] runs = new byte[Views][];       // [v]; the floor view's built on first ask
			public bool floorBuilt;
			public bool floorDiffers;                                // the floor view's depth is not the deck view's
			// [v][s]: CanonicalStride(runs[v], s), -1 = not asked yet (a whole-map scan each; ViewStride is asked per path request)
			public readonly int[][] canon = { new int[RM_TrenchStrideMath.MaxStride + 1], new int[RM_TrenchStrideMath.MaxStride + 1] };
		}

		private static readonly Dictionary<Map, Runs> runsByMap = new Dictionary<Map, Runs>();
		private static readonly object gate = new object();

		/// <summary>The current widths of a map, recomputed when the climb generation moves (dig, fill, cover, deck, bed recede).
		/// Call under <see cref="gate"/>.</summary>
		private static Runs Fresh(Map map, RM_MapComponent_Excavation eng)
		{
			if (!runsByMap.TryGetValue(map, out Runs r))
			{
				PruneDeadMaps();
				r = new Runs();
				runsByMap[map] = r;
			}
			if (r.runs[DeckView] == null || r.generation != eng.ClimbGeneration)
			{
				r.generation = eng.ClimbGeneration;
				r.runs[DeckView] = eng.ClimbCellCount == 0 ? new byte[map.cellIndices.NumGridCells]
					: RM_TrenchStrideMath.RunWidths(RM_PocketGrid.EffectiveDepth(map, eng), map.Size.x, map.Size.z);
				r.runs[FloorView] = null;
				r.floorBuilt = false;
				r.floorDiffers = false;
				for (int v = 0; v < Views; v++)
				{
					for (int s = 0; s < r.canon[v].Length; s++)
					{
						r.canon[v][s] = -1;
					}
				}
			}
			return r;
		}

		/// <summary>The floor view's widths (built on first ask; the deck view's when no deck the floor band passes under stands).
		/// Call under <see cref="gate"/>, after <see cref="Fresh"/>.</summary>
		private static void EnsureFloor(Runs r, Map map, RM_MapComponent_Excavation eng)
		{
			if (r.floorBuilt)
			{
				return;
			}
			r.floorBuilt = true;
			if (eng.ClimbCellCount == 0)
			{
				return;
			}
			byte[] floor = RM_PocketGrid.EffectiveDepth(map, eng, true);
			r.floorDiffers = !SameDepth(floor, RM_PocketGrid.EffectiveDepth(map, eng));
			if (r.floorDiffers)
			{
				r.runs[FloorView] = RM_TrenchStrideMath.RunWidths(floor, map.Size.x, map.Size.z);
			}
		}

		private static bool SameDepth(byte[] a, byte[] b)
		{
			if (a.Length != b.Length)
			{
				return false;
			}
			for (int i = 0; i < a.Length; i++)
			{
				if (a[i] != b[i])
				{
					return false;
				}
			}
			return true;
		}

		/// <summary>Each cell's trench width in the DECK view (RM_TrenchStrideMath.RunWidths over RM_PocketGrid.EffectiveDepth),
		/// recomputed when the climb generation moves. Only ever asked for a pawn with a stride.</summary>
		public static byte[] RunsFor(Map map, RM_MapComponent_Excavation eng)
		{
			if (map == null || eng == null)
			{
				return null;
			}
			lock (gate)
			{
				return Fresh(map, eng).runs[DeckView];
			}
		}

		/// <summary>Is <paramref name="c"/> ground to this pawn (a dug cell of a trench it steps over)? The deck view: a strider
		/// stands on the banks, so a deck beside or over the trench is what it walks onto.</summary>
		public static bool SteppedOver(Pawn p, Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			int s = StrideOf(p);
			if (s == 0 || map == null || eng == null || !c.InBounds(map) || eng.ClimbDepthAt(c) == 0)
			{
				return false;
			}
			byte[] runs = RunsFor(map, eng);
			return runs != null && RM_TrenchStrideMath.Bridged(runs[map.cellIndices.CellToIndex(c)], s);
		}

		/// <summary>RM_SuperdeepTrap.StepDepthAt as this pawn sees it: a trench it steps over is ground (0).</summary>
		public static int StepDepthFor(Pawn p, Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			return SteppedOver(p, map, eng, c) ? 0 : RM_SuperdeepTrap.StepDepthAt(map, eng, c);
		}

		/// <summary>The pocket-grid / mask view this pawn uses in the DECK view: 0 = the plain one, else the smallest stride with the
		/// same bridged cells (RM_TrenchStrideMath.CanonicalStride), so one titan size class shares one grid.</summary>
		public static int ViewStride(Pawn p, Map map)
		{
			return ViewStride(p, map, false);
		}

		/// <summary><see cref="ViewStride(Pawn, Map)"/> in the floor view when <paramref name="floorView"/> and the floor view
		/// differs (else the deck view's). Cached per generation, view and stride.</summary>
		public static int ViewStride(Pawn p, Map map, bool floorView)
		{
			int s = StrideOf(p);
			if (s == 0 || map == null)
			{
				return 0;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null || eng.ClimbCellCount == 0)
			{
				return 0;
			}
			lock (gate)
			{
				Runs r = Fresh(map, eng);
				int v = DeckView;
				if (floorView)
				{
					EnsureFloor(r, map, eng);
					v = r.floorDiffers ? FloorView : DeckView;
				}
				int c = r.canon[v][s];
				if (c < 0)
				{
					c = r.canon[v][s] = RM_TrenchStrideMath.CanonicalStride(r.runs[v], s);
				}
				return c;
			}
		}

		/// <summary>MAP_STATICS_PRUNE_GHOST_MAPS: drop the widths of every map that is gone (called on a miss).</summary>
		private static void PruneDeadMaps()
		{
			List<Map> dead = null;
			foreach (Map m in runsByMap.Keys)
			{
				if (Find.Maps == null || !Find.Maps.Contains(m))
				{
					(dead ?? (dead = new List<Map>())).Add(m);
				}
			}
			if (dead != null)
			{
				foreach (Map m in dead)
				{
					runsByMap.Remove(m);
				}
			}
		}

		// ── stride cliff masks: RM_CliffMask's derivation over the bridged depth, per view ───────────────────

		private sealed class StrideMasks
		{
			// [v][s][k]: view v (DeckView, FloorView), stride s = 1..MaxStride, band K = 1..RM_PitTrapMath.MaxClimbLimit;
			// allocated on the first derive that needs (v, s)
			public readonly NativeArray<CellConnection>[][][] band =
				{ new NativeArray<CellConnection>[RM_TrenchStrideMath.MaxStride + 1][], new NativeArray<CellConnection>[RM_TrenchStrideMath.MaxStride + 1][] };
			public readonly byte[][][] depth = { new byte[RM_TrenchStrideMath.MaxStride + 1][], new byte[RM_TrenchStrideMath.MaxStride + 1][] };
			public readonly bool[][] derived = { new bool[RM_TrenchStrideMath.MaxStride + 1], new bool[RM_TrenchStrideMath.MaxStride + 1] };
			public bool floorDerived; // the floor view differs from the deck view (a deck the floor band passes under stands)
			public int seenFullDerives = -1;
			public int seenGeneration = int.MinValue;
			public bool disposed;
		}

		/// <summary>One cell's 3×3 depths and the structural-join probe AllowedBits asks, reused across a derive (no int[9] and no
		/// closure per cell).</summary>
		private sealed class CellProbe
		{
			public readonly int[] d9 = new int[9];
			public readonly Func<int, bool> joins;
			private readonly Map map;
			private readonly RM_MapComponent_Excavation eng;
			public IntVec3 c;

			public CellProbe(Map map, RM_MapComponent_Excavation eng)
			{
				this.map = map;
				this.eng = eng;
				joins = Joins;
			}

			private bool Joins(int b)
			{
				int dx = RM_CliffMaskMath.Dx[b], dz = RM_CliffMaskMath.Dz[b];
				var o = new IntVec3(c.x + dx, 0, c.z + dz);
				return o.InBounds(map) && RM_ClimbJoins.Structural(map, eng, c, o, d9[4], d9[RM_CliffMaskMath.N9(dx, dz)]);
			}
		}

		private static readonly Dictionary<Map, StrideMasks> masks = new Dictionary<Map, StrideMasks>();

		/// <summary>Full stride re-derives, for the bridge proof.</summary>
		public static int StrideDerives { get; private set; }

		private static StrideMasks MasksFor(Map map, bool create)
		{
			lock (gate)
			{
				if (map == null)
				{
					return null;
				}
				if (!masks.TryGetValue(map, out StrideMasks m) || m.disposed)
				{
					if (!create)
					{
						return null;
					}
					m = new StrideMasks();
					masks[map] = m;
				}
				return m;
			}
		}

		internal static void Release(Map map)
		{
			lock (gate)
			{
				if (map != null && masks.TryGetValue(map, out StrideMasks m))
				{
					Free(m);
					masks.Remove(map);
				}
				if (map != null)
				{
					runsByMap.Remove(map);
				}
			}
		}

		private static void Free(StrideMasks m)
		{
			if (m.disposed)
			{
				return;
			}
			m.disposed = true;
			for (int v = 0; v < Views; v++)
			{
				for (int s = 1; s < m.band[v].Length; s++)
				{
					if (m.band[v][s] == null)
					{
						continue;
					}
					for (int k = 1; k < m.band[v][s].Length; k++)
					{
						if (m.band[v][s][k].IsCreated)
						{
							m.band[v][s][k].Dispose();
						}
					}
				}
			}
		}

		/// <summary>After RM_CliffMask's own ComputeAll postfix: re-derive every stride view.</summary>
		internal static void AfterComputeAll(Map map, NativeArray<CellConnection>.ReadOnly vanilla)
		{
			Resolve();
			if (hook == null)
			{
				return; // HugeThings absent: nothing is ever allocated
			}
			FullDerive(map, MasksFor(map, true), vanilla);
		}

		/// <summary>After RM_CliffMask's own UpdateIncrementally postfix: a full re-derive whenever the plain masks did one (or the
		/// climb generation moved); otherwise the 3×3 of each delta, from the bridged depth of the last full derive (depth only
		/// moves with the generation, which forces a full one).</summary>
		internal static void AfterIncremental(Map map, NativeArray<CellConnection>.ReadOnly vanilla, List<IntVec3> deltas)
		{
			Resolve();
			if (hook == null)
			{
				return;
			}
			StrideMasks m = MasksFor(map, true);
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (m.seenFullDerives != RM_CliffMask.FullDerives || m.seenGeneration != (eng?.ClimbGeneration ?? 0))
			{
				FullDerive(map, m, vanilla);
				return;
			}
			if (deltas == null || deltas.Count == 0)
			{
				return;
			}
			CellIndices ci = map.cellIndices;
			var probe = new CellProbe(map, eng);
			var done = new HashSet<int>();
			for (int v = 0; v < Views; v++)
			{
				for (int s = 1; s < m.derived[v].Length; s++)
				{
					if (!m.derived[v][s])
					{
						continue;
					}
					done.Clear();
					foreach (IntVec3 d in deltas)
					{
						for (int dz = -1; dz <= 1; dz++)
						{
							for (int dx = -1; dx <= 1; dx++)
							{
								var c = new IntVec3(d.x + dx, 0, d.z + dz);
								if (c.InBounds(map) && done.Add(ci.CellToIndex(c)))
								{
									DeriveCell(map, probe, m.band[v][s], vanilla, c, m.depth[v][s]);
								}
							}
						}
					}
				}
			}
		}

		private static void FullDerive(Map map, StrideMasks m, NativeArray<CellConnection>.ReadOnly vanilla)
		{
			if (m == null)
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			m.seenFullDerives = RM_CliffMask.FullDerives;
			m.seenGeneration = eng?.ClimbGeneration ?? 0;
			m.floorDerived = false;
			for (int v = 0; v < Views; v++)
			{
				for (int s = 1; s < m.derived[v].Length; s++)
				{
					m.derived[v][s] = false;
				}
			}
			if (!RM_CliffMask.On || eng == null || eng.ClimbCellCount == 0)
			{
				return;
			}
			int w = map.Size.x, h = map.Size.z, n = map.cellIndices.NumGridCells;
			CellIndices ci = map.cellIndices;
			var probe = new CellProbe(map, eng);
			var done = new HashSet<int>();
			byte[] deckDepth = null;
			for (int v = 0; v < Views; v++)
			{
				// TRENCH_STRIDE_UNDERPASS_FIX_ONE_BUG: the floor view only while it differs, as RM_CliffMask derives its under masks
				byte[] depth = RM_PocketGrid.EffectiveDepth(map, eng, v == FloorView);
				if (v == DeckView)
				{
					deckDepth = depth;
				}
				else if (SameDepth(depth, deckDepth))
				{
					break;
				}
				else
				{
					m.floorDerived = true;
				}
				byte[] runs = RM_TrenchStrideMath.RunWidths(depth, w, h);
				int prevCount = 0;
				for (int s = 1; s < m.derived[v].Length; s++)
				{
					int count = RM_TrenchStrideMath.CountBridged(runs, s);
					bool canonical = count > 0 && count != prevCount; // == CanonicalStride(runs, s) == s: bridged sets nest
					prevCount = count;
					if (!canonical)
					{
						continue; // the same view as a smaller stride (or the plain one): Swap hands that out
					}
					if (m.band[v][s] == null)
					{
						m.band[v][s] = new NativeArray<CellConnection>[RM_PitTrapMath.ClimbBands];
						for (int k = 1; k < m.band[v][s].Length; k++)
						{
							m.band[v][s][k] = new NativeArray<CellConnection>(n, Allocator.Persistent);
						}
					}
					byte[] bridged = RM_TrenchStrideMath.BridgedDepth(depth, runs, s);
					m.depth[v][s] = bridged;
					NativeArray<CellConnection>[] bands = m.band[v][s];
					for (int k = 1; k < bands.Length; k++)
					{
						NativeArray<CellConnection> a = bands[k];
						for (int i = 0; i < n; i++)
						{
							a[i] = vanilla[i];
						}
					}
					done.Clear();
					for (int i = 0; i < n; i++)
					{
						if (bridged[i] == 0)
						{
							continue;
						}
						IntVec3 c = ci.IndexToCell(i);
						for (int dz = -1; dz <= 1; dz++)
						{
							for (int dx = -1; dx <= 1; dx++)
							{
								int x = c.x + dx, z = c.z + dz;
								if (x >= 0 && z >= 0 && x < w && z < h && done.Add(z * w + x))
								{
									DeriveCell(map, probe, bands, vanilla, new IntVec3(x, 0, z), bridged);
								}
							}
						}
					}
					m.derived[v][s] = true;
				}
			}
			StrideDerives++;
		}

		/// <summary>RM_CliffMask.DeriveCell over a given depth (kept in step with it: vanilla's byte AND the band's AllowedBits, ramp
		/// and structural-ladder edges restored).</summary>
		private static void DeriveCell(Map map, CellProbe probe, NativeArray<CellConnection>[] bands,
			NativeArray<CellConnection>.ReadOnly vanilla, IntVec3 c, byte[] depth)
		{
			int w = map.Size.x, h = map.Size.z;
			int[] d9 = probe.d9;
			probe.c = c;
			for (int dz = -1; dz <= 1; dz++)
			{
				for (int dx = -1; dx <= 1; dx++)
				{
					int x = c.x + dx, z = c.z + dz;
					d9[RM_CliffMaskMath.N9(dx, dz)] = x >= 0 && z >= 0 && x < w && z < h ? depth[z * w + x] : 0;
				}
			}
			int idx = map.cellIndices.CellToIndex(c);
			byte van = (byte)vanilla[idx];
			for (int k = 1; k < bands.Length; k++)
			{
				bands[k][idx] = (CellConnection)RM_CliffMaskMath.Derive(van, RM_CliffMaskMath.AllowedBits(d9, k, probe.joins));
			}
		}

		// ── the swap (main thread), after RM_CliffMask's ─────────────────────────────

		private static bool noted;
		private static Pawn notedPawn;

		internal static void NoteRequest(PathRequest request)
		{
			noted = true;
			notedPawn = request?.pawn;
		}

		/// <summary>TRENCH_STRIDE_UNDERPASS_FIX_ONE_BUG: the stride view COMPOSES with the view RM_CliffMask.Swap chose. A strider
		/// in the floor band, or down in a hole it does not step over, plans on the floor view with that view's narrow trenches
		/// bridged; one standing astride a trench it steps over is at ground, so it plans on the deck view (decks are decks to it).
		/// No stride view differs from the chosen plain one: RM_CliffMask's array stands.</summary>
		internal static void Swap(Map map, ref PathFinderJob job)
		{
			if (!noted)
			{
				return;
			}
			noted = false;
			Pawn p = notedPawn;
			notedPawn = null;
			if (StrideOf(p) == 0)
			{
				return;
			}
			StrideMasks m = MasksFor(map, false);
			if (m == null)
			{
				return;
			}
			// RM_CliffMask.Swap's own exceptions, which keep vanilla's array: a flyer, a pawn too wide for its pocket.
			if (RM_PocketGrid.CanFly(p) || RM_SuperdeepTrap.InOwnPocketTooNarrow(p))
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			bool floor = m.floorDerived && RM_TrenchStrideMath.StriderUsesFloorView(Pits.RM_SuspensionUnderpass.UsesFloorView(p), Pits.RM_SuspensionUnderpass.InFloorBand(p),
				p.Spawned && SteppedOver(p, map, eng, p.Position));
			int v = floor ? FloorView : DeckView;
			int s = ViewStride(p, map, floor);
			if (s == 0 || !m.derived[v][s])
			{
				return; // no stride view here, or not derived yet (the next GatherData derives it): RM_CliffMask's array holds
			}
			int band = RM_PocketGridMath.BandFor(RM_PocketGrid.ClimbLimitOf(p), RM_PitTrapMath.ClimbBands);
			if (band <= 0 || band >= m.band[v][s].Length)
			{
				return;
			}
			job.connectivity = m.band[v][s][band].AsReadOnly();
		}

		/// <summary>Bridge/proof read: "STRIDE s=S view=V floorView=F run=R bridged=b registered=b derives=N".</summary>
		public static string ProofStride(Pawn p, IntVec3 c)
		{
			Map map = p?.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (map == null || eng == null || !c.InBounds(map))
			{
				return "REFUSED: no pawn map, no excavation engine, or out of bounds";
			}
			byte[] runs = RunsFor(map, eng);
			int run = runs == null ? 0 : runs[map.cellIndices.CellToIndex(c)];
			return "STRIDE s=" + StrideOf(p) + " view=" + ViewStride(p, map) + " floorView=" + ViewStride(p, map, true) + " run=" + run + " bridged=" + SteppedOver(p, map, eng, c)
				+ " registered=" + Registered + " derives=" + StrideDerives;
		}
	}

	// ── Harmony: each runs AFTER its RM_CliffMask twin (Priority.Low), on the same vanilla seams ─────

	[HarmonyPatch(typeof(ConnectivitySource), nameof(ConnectivitySource.ComputeAll))]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap: titans step over narrow trenches", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_ConnectivitySource_ComputeAll_Stride
	{
		[HarmonyPostfix]
		[HarmonyPriority(Priority.Low)]
		public static void Postfix(ConnectivitySource __instance, Map ___map)
		{
			RM_TrenchStride.AfterComputeAll(___map, __instance.Data);
		}
	}

	[HarmonyPatch(typeof(ConnectivitySource), nameof(ConnectivitySource.UpdateIncrementally))]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap: titans step over narrow trenches", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_ConnectivitySource_Incremental_Stride
	{
		[HarmonyPostfix]
		[HarmonyPriority(Priority.Low)]
		public static void Postfix(ConnectivitySource __instance, Map ___map, List<IntVec3> cellDeltas)
		{
			RM_TrenchStride.AfterIncremental(___map, __instance.Data, cellDeltas);
		}
	}

	[HarmonyPatch(typeof(PathFinderMapData), nameof(PathFinderMapData.Dispose))]
	// Label only, no settings field: masks allocated while the feature was on must be freed after it is turned off.
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap: stride-mask bookkeeping")]
	public static class RM_Patch_PathFinderMapData_Dispose_Stride
	{
		[HarmonyPostfix]
		public static void Postfix(Map ___map)
		{
			RM_TrenchStride.Release(___map);
		}
	}

	[HarmonyPatch(typeof(PathFinder), "ParameterizePathJob")]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap: titans step over narrow trenches", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_PathFinder_NoteRequest_Stride
	{
		[HarmonyPrefix]
		public static void Prefix(PathRequest request)
		{
			RM_TrenchStride.NoteRequest(request);
		}
	}

	[HarmonyPatch(typeof(PathFinderMapData), nameof(PathFinderMapData.ParameterizePathJob))]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap: titans step over narrow trenches", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_PathFinderMapData_SwapMask_Stride
	{
		[HarmonyPostfix]
		[HarmonyPriority(Priority.Low)]
		public static void Postfix(Map ___map, ref PathFinderJob job)
		{
			RM_TrenchStride.Swap(___map, ref job);
		}
	}
}
