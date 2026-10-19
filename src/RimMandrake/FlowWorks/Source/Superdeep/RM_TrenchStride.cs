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
	///     bridged depth, swapped in after RM_CliffMask's own swap for a pawn with a stride.
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

		private sealed class Runs
		{
			public int generation = int.MinValue;
			public byte[] runs;
		}

		private static readonly Dictionary<Map, Runs> runsByMap = new Dictionary<Map, Runs>();
		private static readonly object gate = new object();

		/// <summary>Each cell's trench width (RM_TrenchStrideMath.RunWidths over RM_PocketGrid.EffectiveDepth), recomputed when the
		/// climb generation moves (dig, fill, cover, deck, bed recede). Only ever asked for a pawn with a stride.</summary>
		public static byte[] RunsFor(Map map, RM_MapComponent_Excavation eng)
		{
			if (map == null || eng == null)
			{
				return null;
			}
			lock (gate)
			{
				if (!runsByMap.TryGetValue(map, out Runs r))
				{
					PruneDeadMaps();
					r = new Runs();
					runsByMap[map] = r;
				}
				if (r.runs == null || r.generation != eng.ClimbGeneration)
				{
					r.generation = eng.ClimbGeneration;
					r.runs = eng.ClimbCellCount == 0 ? new byte[map.cellIndices.NumGridCells]
						: RM_TrenchStrideMath.RunWidths(RM_PocketGrid.EffectiveDepth(map, eng), map.Size.x, map.Size.z);
				}
				return r.runs;
			}
		}

		/// <summary>Is <paramref name="c"/> ground to this pawn (a dug cell of a trench it steps over)?</summary>
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

		/// <summary>The pocket-grid / mask view this pawn uses: 0 = the plain one, else the smallest stride with the same bridged
		/// cells (RM_TrenchStrideMath.CanonicalStride), so one titan size class shares one grid.</summary>
		public static int ViewStride(Pawn p, Map map)
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
			return RM_TrenchStrideMath.CanonicalStride(RunsFor(map, eng), s);
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

		// ── stride cliff masks: RM_CliffMask's derivation over the bridged depth ──────────────────────────

		private sealed class StrideMasks
		{
			// [s][k]: stride s = 1..MaxStride, band K = 1..RM_PitTrapMath.MaxClimbLimit; allocated on the first derive that needs s
			public readonly NativeArray<CellConnection>[][] band = new NativeArray<CellConnection>[RM_TrenchStrideMath.MaxStride + 1][];
			public readonly byte[][] depth = new byte[RM_TrenchStrideMath.MaxStride + 1][]; // the bridged depth each was derived from
			public readonly bool[] derived = new bool[RM_TrenchStrideMath.MaxStride + 1];
			public int seenFullDerives = -1;
			public int seenGeneration = int.MinValue;
			public bool disposed;
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
			for (int s = 1; s < m.band.Length; s++)
			{
				if (m.band[s] == null)
				{
					continue;
				}
				for (int k = 1; k < m.band[s].Length; k++)
				{
					if (m.band[s][k].IsCreated)
					{
						m.band[s][k].Dispose();
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
			for (int s = 1; s < m.derived.Length; s++)
			{
				if (!m.derived[s])
				{
					continue;
				}
				var done = new HashSet<int>();
				foreach (IntVec3 d in deltas)
				{
					for (int dz = -1; dz <= 1; dz++)
					{
						for (int dx = -1; dx <= 1; dx++)
						{
							var c = new IntVec3(d.x + dx, 0, d.z + dz);
							if (c.InBounds(map) && done.Add(ci.CellToIndex(c)))
							{
								DeriveCell(map, eng, m.band[s], vanilla, c, m.depth[s]);
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
			for (int s = 1; s < m.derived.Length; s++)
			{
				m.derived[s] = false;
			}
			if (!RM_CliffMask.On || eng == null || eng.ClimbCellCount == 0)
			{
				return;
			}
			byte[] depth = RM_PocketGrid.EffectiveDepth(map, eng);
			int w = map.Size.x, h = map.Size.z, n = map.cellIndices.NumGridCells;
			byte[] runs = RM_TrenchStrideMath.RunWidths(depth, w, h);
			for (int s = 1; s < m.derived.Length; s++)
			{
				if (RM_TrenchStrideMath.CanonicalStride(runs, s) != s)
				{
					continue; // the same view as a smaller stride (or the plain one): Swap hands that out
				}
				if (m.band[s] == null)
				{
					m.band[s] = new NativeArray<CellConnection>[RM_PitTrapMath.ClimbBands];
					for (int k = 1; k < m.band[s].Length; k++)
					{
						m.band[s][k] = new NativeArray<CellConnection>(n, Allocator.Persistent);
					}
				}
				byte[] bridged = RM_TrenchStrideMath.BridgedDepth(depth, runs, s);
				m.depth[s] = bridged;
				NativeArray<CellConnection>[] bands = m.band[s];
				for (int k = 1; k < bands.Length; k++)
				{
					NativeArray<CellConnection> a = bands[k];
					for (int i = 0; i < n; i++)
					{
						a[i] = vanilla[i];
					}
				}
				CellIndices ci = map.cellIndices;
				var done = new HashSet<int>();
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
								DeriveCell(map, eng, bands, vanilla, new IntVec3(x, 0, z), bridged);
							}
						}
					}
				}
				m.derived[s] = true;
			}
			StrideDerives++;
		}

		/// <summary>RM_CliffMask.DeriveCell over a given depth (kept in step with it: vanilla's byte AND the band's AllowedBits, ramp
		/// and structural-ladder edges restored).</summary>
		private static void DeriveCell(Map map, RM_MapComponent_Excavation eng, NativeArray<CellConnection>[] bands,
			NativeArray<CellConnection>.ReadOnly vanilla, IntVec3 c, byte[] depth)
		{
			int w = map.Size.x, h = map.Size.z;
			var d9 = new int[9];
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
				byte allowed = RM_CliffMaskMath.AllowedBits(d9, k, b =>
				{
					var o = new IntVec3(c.x + RM_CliffMaskMath.Dx[b], 0, c.z + RM_CliffMaskMath.Dz[b]);
					return o.InBounds(map) && RM_ClimbJoins.Structural(map, eng, c, o, d9[4], d9[RM_CliffMaskMath.N9(RM_CliffMaskMath.Dx[b], RM_CliffMaskMath.Dz[b])]);
				});
				bands[k][idx] = (CellConnection)RM_CliffMaskMath.Derive(van, allowed);
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

		internal static void Swap(Map map, ref PathFinderJob job)
		{
			if (!noted)
			{
				return;
			}
			noted = false;
			Pawn p = notedPawn;
			notedPawn = null;
			int s = ViewStride(p, map);
			if (s == 0)
			{
				return;
			}
			StrideMasks m = MasksFor(map, false);
			if (m == null || !m.derived[s])
			{
				return; // not derived yet (the next GatherData derives it): the plain band holds for that request
			}
			// RM_CliffMask.Swap's own exceptions, which keep vanilla's array: a flyer, a pawn too wide for its pocket.
			if (RM_PocketGrid.CanFly(p) || RM_SuperdeepTrap.InOwnPocketTooNarrow(p))
			{
				return;
			}
			int band = RM_PocketGridMath.BandFor(RM_PocketGrid.ClimbLimitOf(p), RM_PitTrapMath.ClimbBands);
			if (band <= 0 || band >= m.band[s].Length)
			{
				return;
			}
			job.connectivity = m.band[s][band].AsReadOnly();
		}

		/// <summary>Bridge/proof read: "STRIDE s=S view=V run=R bridged=b registered=b derives=N".</summary>
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
			return "STRIDE s=" + StrideOf(p) + " view=" + ViewStride(p, map) + " run=" + run + " bridged=" + SteppedOver(p, map, eng, c)
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
