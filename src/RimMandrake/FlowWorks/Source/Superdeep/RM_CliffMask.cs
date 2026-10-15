using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Unity.Collections;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS — per-band connectivity masks with a per-request swap (design/RimMandrake/
	/// relative_depth_climb_design_2026-10-12.md §8.5 step 2, Alternative A). The pathfinder learns where the walls are, so
	/// the staged planner (AvoidPits / StayInPit / PlanRoute) is retired while the relative rule is on.
	///
	/// RimWorld 1.6's Burst A* reads one byte per cell of allowed directions (ConnectivitySource, handed to every path job by
	/// PathFinderMapData.ParameterizePathJob). We keep one derived array per climb band K = 1..MaxDepth-1: vanilla's byte AND
	/// RM_CliffMaskMath.AllowedBits (the same StepAllowed / DiagonalAllowed the pocket grid labels with), with ramp and
	/// structural-ladder edges restored. Vanilla's array is never written.
	///
	/// WHEN THE MASKS MOVE: only inside PathFinderMapData.GatherData, exactly when vanilla moves its own array (postfixes on
	/// ConnectivitySource.ComputeAll / UpdateIncrementally; GatherData runs after the previous tick's path jobs completed and
	/// before this tick's are scheduled). A cell delta re-derives its 3×3; a moved climb generation (dig, fill, bed recede,
	/// cover, ladder raised/lowered, ramp), a climb setting or the rule's on/off re-derives every cell within one of a hole.
	///
	/// THE SWAP: a prefix on the private PathFinder.ParameterizePathJob(…, request) notes the requesting pawn; the postfix on
	/// PathFinderMapData.ParameterizePathJob, which runs next on the same thread, points job.connectivity at that pawn's band.
	/// Flyers and K ≥ MaxDepth keep vanilla's array; a pawnless request gets the person band (K = 2).
	///
	/// Ladders: a LOWERED ladder is structural here (its edges are restored for everyone); the prison-door rule is per pawn,
	/// closed per request by RM_PitPathing's ladder offset grid and, as a backstop, by the per-step floor.
	/// </summary>
	public static class RM_CliffMask
	{
		private sealed class Masks
		{
			public NativeArray<CellConnection>[] band; // index K, 1..MaxDepth-1
			public bool derived;     // the bands hold a derivation (false: never derived, or no hole: vanilla is right)
			public long key = long.MinValue;
			public bool disposed;
		}

		private static readonly Dictionary<Map, Masks> masks = new Dictionary<Map, Masks>();
		private static readonly object gate = new object();

		/// <summary>Bumped by a climb setting change (RM_PocketGrid.SettingsChanged).</summary>
		internal static int settingsSalt;

		/// <summary>Full re-derive count, for the bridge proof.</summary>
		public static int FullDerives { get; private set; }

		public static bool On => RimMandrakeFlowWorksSettings.superdeepCaptureEnabled && RM_PocketGrid.Relative && RM_SuperdeepTrap.RuleOn;

		private static Masks For(Map map)
		{
			lock (gate)
			{
				return map != null && masks.TryGetValue(map, out Masks m) && !m.disposed ? m : null;
			}
		}

		// ── lifecycle (main thread) ───────────────────────────────────────

		internal static void Allocate(Map map)
		{
			if (map == null)
			{
				return;
			}
			int n = map.cellIndices.NumGridCells;
			var m = new Masks { band = new NativeArray<CellConnection>[RM_ExcavationDepth.MaxDepth] };
			for (int k = 1; k < m.band.Length; k++)
			{
				m.band[k] = new NativeArray<CellConnection>(n, Allocator.Persistent);
			}
			lock (gate)
			{
				if (masks.TryGetValue(map, out Masks old))
				{
					Free(old);
				}
				masks[map] = m;
			}
		}

		internal static void Release(Map map)
		{
			lock (gate)
			{
				if (map != null && masks.TryGetValue(map, out Masks m))
				{
					Free(m);
					masks.Remove(map);
				}
			}
		}

		private static void Free(Masks m)
		{
			if (m.disposed)
			{
				return;
			}
			m.disposed = true;
			for (int k = 1; k < m.band.Length; k++)
			{
				if (m.band[k].IsCreated)
				{
					m.band[k].Dispose();
				}
			}
		}

		// ── derivation (inside GatherData; may be a worker thread, main thread blocked) ─────

		private static long KeyFor(RM_MapComponent_Excavation eng)
		{
			long k = eng == null ? 0 : eng.ClimbGeneration;
			k = k * 31 + settingsSalt;
			k = k * 2 + (On ? 1 : 0);
			k = k * 2 + (RimMandrakeFlowWorksSettings.ladderRaiseLowerEnabled ? 1 : 0);
			k = k * 2 + (RimMandrakeFlowWorksSettings.pondBedHollowEnabled ? 1 : 0);
			k = k * 2 + (RimMandrakeFlowWorksSettings.pitRampsEnabled ? 1 : 0);
			k = k * 4 + RM_PitRamp.MaxSpan;
			return k;
		}

		/// <summary>ConnectivitySource.ComputeAll ran: vanilla's whole array is new.</summary>
		internal static void AfterComputeAll(Map map, NativeArray<CellConnection>.ReadOnly vanilla)
		{
			Masks m = For(map);
			if (m == null)
			{
				return;
			}
			FullDerive(map, m, vanilla);
		}

		/// <summary>ConnectivitySource.UpdateIncrementally ran over these deltas.</summary>
		internal static void AfterIncremental(Map map, NativeArray<CellConnection>.ReadOnly vanilla, List<IntVec3> deltas)
		{
			Masks m = For(map);
			if (m == null)
			{
				return;
			}
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			if (KeyFor(eng) != m.key)
			{
				FullDerive(map, m, vanilla);
				return;
			}
			if (!m.derived || deltas == null || deltas.Count == 0)
			{
				return;
			}
			CellIndices ci = map.cellIndices;
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
							DeriveCell(map, eng, m, vanilla, c, null);
						}
					}
				}
			}
		}

		private static void FullDerive(Map map, Masks m, NativeArray<CellConnection>.ReadOnly vanilla)
		{
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			m.key = KeyFor(eng);
			FullDerives++;
			if (!On || eng == null || eng.ClimbCellCount == 0)
			{
				m.derived = false; // no hole (or the rule is off): vanilla's array is the answer, the swap hands it out
				return;
			}
			int n = map.cellIndices.NumGridCells;
			for (int k = 1; k < m.band.Length; k++)
			{
				NativeArray<CellConnection> a = m.band[k];
				for (int i = 0; i < n; i++)
				{
					a[i] = vanilla[i];
				}
			}
			byte[] depth = RM_PocketGrid.EffectiveDepth(map, eng);
			CellIndices ci = map.cellIndices;
			int w = map.Size.x, h = map.Size.z;
			var done = new HashSet<int>();
			for (int i = 0; i < n; i++)
			{
				if (depth[i] == 0)
				{
					continue;
				}
				IntVec3 c = ci.IndexToCell(i);
				for (int dz = -1; dz <= 1; dz++)
				{
					for (int dx = -1; dx <= 1; dx++)
					{
						int x = c.x + dx, z = c.z + dz;
						if (x < 0 || z < 0 || x >= w || z >= h)
						{
							continue;
						}
						int j = z * w + x;
						if (done.Add(j))
						{
							DeriveCell(map, eng, m, vanilla, new IntVec3(x, 0, z), depth);
						}
					}
				}
			}
			m.derived = true;
		}

		private static void DeriveCell(Map map, RM_MapComponent_Excavation eng, Masks m, NativeArray<CellConnection>.ReadOnly vanilla,
			IntVec3 c, byte[] depth)
		{
			int w = map.Size.x, h = map.Size.z;
			var d9 = new int[9];
			for (int dz = -1; dz <= 1; dz++)
			{
				for (int dx = -1; dx <= 1; dx++)
				{
					int x = c.x + dx, z = c.z + dz;
					int v = 0;
					if (x >= 0 && z >= 0 && x < w && z < h)
					{
						var cc = new IntVec3(x, 0, z);
						v = depth != null ? depth[z * w + x] : RM_SuperdeepTrap.StepDepthAt(map, eng, cc);
					}
					d9[RM_CliffMaskMath.N9(dx, dz)] = v;
				}
			}
			int idx = map.cellIndices.CellToIndex(c);
			byte van = (byte)vanilla[idx];
			for (int k = 1; k < m.band.Length; k++)
			{
				byte allowed = RM_CliffMaskMath.AllowedBits(d9, k, b =>
				{
					var o = new IntVec3(c.x + RM_CliffMaskMath.Dx[b], 0, c.z + RM_CliffMaskMath.Dz[b]);
					return o.InBounds(map) && RM_ClimbJoins.Structural(map, eng, c, o, d9[4], d9[RM_CliffMaskMath.N9(RM_CliffMaskMath.Dx[b], RM_CliffMaskMath.Dz[b])]);
				});
				m.band[k][idx] = (CellConnection)RM_CliffMaskMath.Derive(van, allowed);
			}
		}

		// ── the swap (main thread) ────────────────────────────────────────

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
			if (!On)
			{
				return;
			}
			Masks m = For(map);
			if (m == null || !m.derived)
			{
				return;
			}
			// PIT_REACH_VERIFY_FLYERS_AND_GIANTS (GPT C3-F5): a pawn too wide for the pocket it stands in is not held there, so
			// it routes on vanilla's connectivity, as a flyer does, and the step floor lets it out (RelativeStepAllowed).
			if (p != null && (RM_PocketGrid.CanFly(p) || RM_SuperdeepTrap.InOwnPocketTooNarrow(p)))
			{
				return;
			}
			int k = p == null ? RM_PocketGrid.PersonBand : RM_PocketGrid.ClimbLimitOf(p);
			int band = RM_PocketGridMath.BandFor(k, RM_ExcavationDepth.MaxDepth);
			if (band <= 0 || band >= m.band.Length)
			{
				return;
			}
			job.connectivity = m.band[band].AsReadOnly();
		}

		/// <summary>Bridge/proof read: "CLIFF k=K bits=0x.. vanilla=0x.. derived=b derives=N".</summary>
		public static string ProofMask(Map map, IntVec3 c, int k)
		{
			Masks m = For(map);
			if (m == null || !c.InBounds(map))
			{
				return "REFUSED: no masks or out of bounds";
			}
			int i = map.cellIndices.CellToIndex(c);
			byte van = (byte)map.pathFinder.MapData.CellConnectionsAt(i);
			int band = RM_PocketGridMath.BandFor(k, RM_ExcavationDepth.MaxDepth);
			byte bits = band > 0 && band < m.band.Length && m.derived ? (byte)m.band[band][i] : van;
			return "CLIFF k=" + k + " bits=0x" + bits.ToString("X2") + " vanilla=0x" + van.ToString("X2") + " derived=" + m.derived
				+ " derives=" + FullDerives;
		}
	}

	/// <summary>Who joins two cardinal neighbours whatever their depth difference (design §8.4): a ramp (anyone), a ladder.</summary>
	public static class RM_ClimbJoins
	{
		/// <summary>The lowered ladder in this cell, if any (raised counts only while the raise/lower setting is off).</summary>
		public static bool LoweredLadderAt(Map map, IntVec3 c)
		{
			ThingDef ladderDef = RimMandrakeFlowWorks_DefOf.RM_Ladder;
			if (ladderDef == null || !c.InBounds(map))
			{
				return false;
			}
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i].def == ladderDef)
				{
					RM_CompLadder comp = things[i].TryGetComp<RM_CompLadder>();
					return comp == null || !comp.EffectivelyRaised;
				}
			}
			return false;
		}

		/// <summary>Structural join for the masks: a ramp, or a lowered ladder in the deeper cell (any pawn; the prison-door
		/// rule is per request). aD / bD: the step depths of a and b.</summary>
		public static bool Structural(Map map, RM_MapComponent_Excavation eng, IntVec3 a, IntVec3 b, int aD, int bD)
		{
			if (aD == bD)
			{
				return false;
			}
			if (RampJoins(map, eng, a, b, aD, bD))
			{
				return true;
			}
			return aD > bD ? LoweredLadderAt(map, a) : LoweredLadderAt(map, b);
		}

		/// <summary>The per-pawn join (the step floor, step cost): a ramp, or a ladder in the deeper cell THIS pawn may climb.</summary>
		public static bool ForPawn(Map map, RM_MapComponent_Excavation eng, IntVec3 a, IntVec3 b, int aD, int bD, Pawn p,
			out bool viaLadder, out bool viaRamp)
		{
			viaLadder = viaRamp = false;
			if (aD == bD || a.x != b.x && a.z != b.z)
			{
				return false;
			}
			if (RampJoins(map, eng, a, b, aD, bD))
			{
				viaRamp = true;
				return true;
			}
			IntVec3 deep = aD > bD ? a : b;
			if (RM_LadderRules.LadderLetsOut(map, deep, p))
			{
				viaLadder = true;
				return true;
			}
			return false;
		}

		/// <summary>Terrain cost per level of a ladder climb: "Ladder slowness" (default 2, PROVISIONAL) normal climbs per level
		/// (design §8.4: "twice a normal climb per level"), so a ladder is always slower than a ramp, which walks flat.</summary>
		public static int LadderCostPerLevel(int climbCost)
		{
			return Mathf.RoundToInt(climbCost * Mathf.Max(1f, RimMandrakeFlowWorksSettings.pitLadderSlowness));
		}

		/// <summary>A ramp joins a and b: PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS (RM_PitRamp). False until a ramp stands there.</summary>
		public static bool RampJoins(Map map, RM_MapComponent_Excavation eng, IntVec3 a, IntVec3 b, int aD, int bD)
		{
			return RM_PitRamp.Joins(map, a, b, aD, bD);
		}
	}

	// ── Harmony ────────────────────────────────────────────────────────────

	[HarmonyPatch(typeof(ConnectivitySource), MethodType.Constructor, new[] { typeof(Map) })]
	// Label only, no settings field: the masks must exist for every map, so turning the feature on later finds them.
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap: cliff-mask bookkeeping")]
	public static class RM_Patch_ConnectivitySource_Allocate
	{
		[HarmonyPostfix]
		public static void Postfix(Map map)
		{
			RM_CliffMask.Allocate(map);
		}
	}

	[HarmonyPatch(typeof(ConnectivitySource), nameof(ConnectivitySource.ComputeAll))]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_ConnectivitySource_ComputeAll
	{
		[HarmonyPostfix]
		public static void Postfix(ConnectivitySource __instance, Map ___map)
		{
			RM_CliffMask.AfterComputeAll(___map, __instance.Data);
		}
	}

	[HarmonyPatch(typeof(ConnectivitySource), nameof(ConnectivitySource.UpdateIncrementally))]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_ConnectivitySource_Incremental
	{
		[HarmonyPostfix]
		public static void Postfix(ConnectivitySource __instance, Map ___map, List<IntVec3> cellDeltas)
		{
			RM_CliffMask.AfterIncremental(___map, __instance.Data, cellDeltas);
		}
	}

	[HarmonyPatch(typeof(PathFinderMapData), nameof(PathFinderMapData.Dispose))]
	// Label only, no settings field: the masks must exist for every map, so turning the feature on later finds them.
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap: cliff-mask bookkeeping")]
	public static class RM_Patch_PathFinderMapData_Dispose
	{
		[HarmonyPostfix]
		public static void Postfix(Map ___map)
		{
			RM_CliffMask.Release(___map);
		}
	}

	[HarmonyPatch(typeof(PathFinder), "ParameterizePathJob")]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_PathFinder_NoteRequest
	{
		[HarmonyPrefix]
		public static void Prefix(PathRequest request)
		{
			RM_CliffMask.NoteRequest(request);
		}
	}

	[HarmonyPatch(typeof(PathFinderMapData), nameof(PathFinderMapData.ParameterizePathJob))]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_PathFinderMapData_SwapMask
	{
		[HarmonyPostfix]
		public static void Postfix(Map ___map, ref PathFinderJob job)
		{
			RM_CliffMask.Swap(___map, ref job);
		}
	}
}
