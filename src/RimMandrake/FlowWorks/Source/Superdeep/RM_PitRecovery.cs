using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_DRAINED_MOAT: vanilla's collision recovery ("Unstuck": Pawn_PathFollower.
	/// PatherTick, a standing pawn that shares its square with a blocking one) writes pawn.Position straight to a neighbour from
	/// CellFinder.TryFindBestPawnStandCell(cellByCell). The write never reaches TryEnterNextPathCell, so the per-move floor did
	/// not see it, and the search reads walkability, not pit height: a held raider was set on the bank of a drained 4 m moat.
	///
	/// The SEARCH is filtered, edge by edge, for the length of that one call, so it finds the nearest free square the pawn can
	/// shuffle to; refusing the search's answer afterwards would send a pawn back and forth between two squares. No ladder, no
	/// climbing gear: being crowded off a square is not a climb. The other caller (cellByCell false: something impassable was
	/// put on the pawn, and no cell means death) stays vanilla.
	/// </summary>
	[HarmonyPatch(typeof(CellFinder), nameof(CellFinder.TryFindBestPawnStandCell))]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_PitRecovery
	{
		private static Pawn pawn;
		private static RM_MapComponent_Excavation eng;
		private static bool relative, free, beneath, floorBand, rails;
		private static int k;

		/// <summary>State read for the functional script: recoveries kept off a pit edge the search would have crossed.</summary>
		public static int EdgesRefused;

		[HarmonyPrefix]
		public static void Prefix(Pawn forPawn, bool cellByCell)
		{
			pawn = null;
			if (!RimMandrakeFlowWorksSettings.superdeepCaptureEnabled || !cellByCell || forPawn == null || !forPawn.Spawned)
			{
				return;
			}
			RM_MapComponent_Excavation e = RM_SuperdeepTrap.EngineOf(forPawn.Map);
			if (!RM_SuperdeepTrap.AnyHole(e))
			{
				return;
			}
			relative = RM_PocketGrid.Relative;
			bool freeTraveller = RM_PocketGrid.FreePitTraveller(forPawn);
			rails = RM_FallRails.On && !freeTraveller;
			k = RM_PocketGrid.NaturalClimbLimitOf(forPawn);
			free = freeTraveller || (relative && (!RM_CliffMask.On || RM_PocketGridMath.BandFor(k, RM_PocketGrid.BandCount) == 0
				|| RM_SuperdeepTrap.InOwnPocketTooNarrow(forPawn)));
			beneath = Pits.RM_PitCoverBeneath.IsBeneath(forPawn);
			if (free && !rails && !beneath)
			{
				return;
			}
			floorBand = Pits.RM_SuspensionUnderpass.InFloorBand(forPawn);
			eng = e;
			pawn = forPawn;
		}

		// The Prefix clears the pawn first, so a search that threw leaves nothing a later call reads.
		[HarmonyPostfix]
		public static void Postfix(Pawn forPawn, ref IntVec3 cell, ref bool __result)
		{
			if (pawn == null || pawn != forPawn)
			{
				return;
			}
			IntVec3 from = forPawn.Position;
			// The search was filtered below; this one read keeps the hold true whatever the search became.
			if (__result && cell != from && !EdgeAllowed(from, cell))
			{
				__result = false;
				cell = IntVec3.Invalid;
			}
			// a floor-band pawn crowded along the floor from under a deck did not drop from the deck's walking height
			else if (__result && floorBand && cell != from)
			{
				eng.SuperdeepTrap?.NoteHandledArrival(forPawn, cell);
			}
			pawn = null;
			eng = null;
		}

		/// <summary>The live reading (jawa/static_call; dev surface, nothing in the game calls it). arg "moverId;blockerId": the mover
		/// is put on the blocker's square, both are standing with a job that collides and hostiles near (what a fight gives them),
		/// and the mover's real PatherTick runs once. Answers where it went.</summary>
		public static string ProofRecover(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			Pawn mover = map == null || a.Length != 2 ? null : map.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.ThingID == a[0]);
			Pawn blocker = mover == null ? null : map.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.ThingID == a[1]);
			if (blocker == null || mover == blocker || mover.CurJob == null || blocker.CurJob == null)
			{
				return "REFUSED: want moverId;blockerId, two spawned pawns with jobs: " + arg;
			}
			RM_MapComponent_Excavation e = RM_SuperdeepTrap.EngineOf(map);
			mover.Position = blocker.Position;
			mover.pather.StopDead();
			blocker.pather.StopDead();
			mover.mindState.anyCloseHostilesRecently = blocker.mindState.anyCloseHostilesRecently = true;
			mover.CurJob.collideWithPawns = blocker.CurJob.collideWithPawns = true;
			IntVec3 from = mover.Position;
			bool collides = PawnUtility.AnyPawnBlockingPathAt(from, mover, false, true, false, true);
			int refused = EdgesRefused;
			mover.pather.PatherTick();
			return "RECOVER collides=" + collides + " from=" + from.x + "," + from.z + " fromDepth=" + (e?.ClimbDepthAt(from) ?? 0)
				+ " to=" + mover.Position.x + "," + mover.Position.z + " toDepth=" + (e?.ClimbDepthAt(mover.Position) ?? 0)
				+ " edgesRefused=" + (EdgesRefused - refused);
		}

		internal static bool Filtering(Pawn p)
		{
			return pawn != null && pawn == p;
		}

		/// <summary>May this pawn be shuffled over this cardinal edge?</summary>
		internal static bool EdgeAllowed(IntVec3 from, IntVec3 to)
		{
			Map map = pawn.Map;
			if (eng.ClimbDepthAt(from) == 0 && eng.ClimbDepthAt(to) == 0)
			{
				return true;
			}
			if (beneath && from == pawn.Position)
			{
				return Pits.RM_PitCoverBeneath.StepAllowed(pawn, eng, to);
			}
			if (rails && RM_FallRails.Guards(map, eng, pawn, from, to))
			{
				return false;
			}
			if (free)
			{
				return true;
			}
			return RM_PitTrapMath.RecoveryShuffleAllowed(relative, !relative && RM_SuperdeepTrap.IsHeldAt(pawn, from),
				DepthOf(map, from), DepthOf(map, to), k);
		}

		private static int DepthOf(Map map, IntVec3 c)
		{
			if (!relative)
			{
				return Pits.RM_PitCoverUtility.IsCovered(map, c) ? 0 : eng.ExcavatedDepthAt(c);
			}
			return floorBand ? Pits.RM_SuspensionUnderpass.FloorViewDepthAt(map, eng, c) : RM_TrenchStride.StepDepthFor(pawn, map, eng, c);
		}
	}

	/// <summary>The search's neighbours, pit edges the pawn cannot shuffle over left out.</summary>
	[HarmonyPatch(typeof(CellFinder), "GetAdjacentCardinalCellsForBestStandCell")]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_PitRecoveryNeighbours
	{
		[HarmonyPostfix]
		public static IEnumerable<IntVec3> Postfix(IEnumerable<IntVec3> __result, IntVec3 x, Pawn pawn)
		{
			return RM_Patch_PitRecovery.Filtering(pawn) ? Open(__result, x) : __result;
		}

		private static IEnumerable<IntVec3> Open(IEnumerable<IntVec3> cells, IntVec3 from)
		{
			foreach (IntVec3 c in cells)
			{
				if (RM_Patch_PitRecovery.EdgeAllowed(from, c))
				{
					yield return c;
				}
				else
				{
					RM_Patch_PitRecovery.EdgesRefused++;
				}
			}
		}
	}
}
