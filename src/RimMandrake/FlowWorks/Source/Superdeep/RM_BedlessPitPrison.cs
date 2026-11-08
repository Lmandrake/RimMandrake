using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// DRAINED_HOLE_IS_A_PRISON (owner card 2026-11-05, "Drained moat is a prison": capture from the rim works with NO bed,
	/// and the hole is the prison). The rules are pure and selftested (RM_PitRoomMath.BedlessPrison, BedlessHeld,
	/// FoodEnoughInPocket, DropCell); this is the Verse half.
	///
	/// WHY THIS FILE EXISTS: capture-down (RM_PitRooms.CaptureDownVerdict) used to want a prisoner bed in a pit room. With
	/// bedlessPitPrisonEnabled a pawn the hole holds (HoleHolds: trapped, not under a lid) is captured where it stands. From
	/// then on vanilla's wardens cannot serve him: every warden work giver asks CanReserveAndReach(OnCell) first
	/// (WorkGiver_Warden.ShouldTakeCareOfPrisoner) and our reach veto (RM_Patch_Reachability_SuperdeepVeto) says no to the
	/// pocket; DeliverFood also wants a prison cell (IsInPrisonCell) and drops at SpotToChewStandingNear, which can be the middle
	/// of the hole. Without this file he would starve with nobody told.
	///
	/// WHY THESE THREE PATCHES AND NOT AN IsInPrisonCell POSTFIX: making the hole "a prison cell" everywhere has eight vanilla
	/// callers (SocialProperness among them, which is hot), works per cell where the prisoner's pocket is per pawn, and would
	/// still leave DeliverFood's room compare and FoodAvailableInRoomTo wrong. The narrowest set that works:
	///  1. WorkGiver_Scanner.AllowUnreachable (getter), postfix: true for the five warden givers that can work from the lip
	///     (chat/recruit, convert, enslave, interrogate, deliver food), and only while some prisoner is served from the lip;
	///     else JobGiver_Work never even offers them the unreachable prisoner. Their own gate (2) still decides.
	///  2. WorkGiver_Warden.ShouldTakeCareOfPrisoner, postfix: for those five only, the reach check is replaced by "a lip cell
	///     exists" (talk: RM_PitRooms.TryFindLipCell, Interact kind; food: a rim drop cell with a lip beside it). Every other
	///     warden giver (take to bed, release, execute, feed) keeps vanilla's "no": nobody walks into the hole.
	///  3. WorkGiver_Warden_DeliverFood.JobOnThing, postfix: for a lip-served prisoner the warden cannot reach, or one held in
	///     no prison cell, the job drops the food on a rim cell of HIS pocket, in his room (SocialProperness: a prisoner eats
	///     only food in his room), next to a lip cell the warden can stand on. The walk itself is the existing lip service
	///     (RM_Patch_PathFollower_LipService via RM_PitRooms.ShouldServeFromLipFor, which asks ServesJobAt here).
	///
	/// THE PRISON-DOOR RULE: nothing here builds, installs, lowers or orders a ladder, and the warden givers left alone above
	/// are the ones that would walk a prisoner out. With LADDER_PARITY_BUILD_NO_KEYS_REQUIRED a lowered ladder is a held-open
	/// door, so the only way a warden keeps the door shut is never to bring one. (The colonist rescue ladder,
	/// RM_MapComponent_PitRescueLadder, is queued for free colonists only.) SelfTest BedlessPitPrisonChecks reads this file for
	/// any ladder word.
	///
	/// QUIET: the prisoner shows nothing. Vanilla has no prisoner alert; the pit-stuck alert is for free colonists; his escape
	/// think node finds no exit spot through the reach veto and gives up without a log line. Every search here is memoised
	/// (MemoTicks), so nothing runs each tick.
	///
	/// NOT here: a DOWNED prisoner on the bare floor is not fed (vanilla Feed needs a bed; food dropped beside him cannot be
	/// eaten); tending reaches him only where he lies against the wall (a Touch lip); hemogen delivery is vanilla's.
	/// </summary>
	public static class RM_BedlessPitPrison
	{
		/// <summary>How far from the prisoner a rim drop cell is looked for (the pocket can be a long moat).</summary>
		public const float DropSearchRadius = 20f;

		/// <summary>Rim cells tried for a lip before the search gives up (each costs a few reach queries).</summary>
		public const int DropLipTries = 12;

		/// <summary>How long a lip / drop answer is kept for one warden and one prisoner.</summary>
		public const int MemoTicks = 250;

		/// <summary>How long a "the hole serves him" answer and the food count are kept.</summary>
		public const int ServedTicks = 60;

		private static Game memoGame;
		private static int anyTick = -99999;
		private static bool anyServed;
		private static readonly Dictionary<int, (int tick, bool v)> served = new Dictionary<int, (int, bool)>();
		private static readonly Dictionary<int, (int tick, bool v)> fedMemo = new Dictionary<int, (int, bool)>();
		private static readonly Dictionary<(int w, int p, int kind), (int tick, bool ok, IntVec3 cell)> lipMemo =
			new Dictionary<(int, int, int), (int, bool, IntVec3)>();

		private static int Now => Find.TickManager?.TicksGame ?? 0;

		/// <summary>The memos die with the game they were made in.</summary>
		private static void Fresh()
		{
			if (!ReferenceEquals(memoGame, Current.Game))
			{
				memoGame = Current.Game;
				served.Clear();
				fedMemo.Clear();
				lipMemo.Clear();
				anyTick = -99999;
			}
		}

		private static bool Live(int tick, int now, int ttl)
		{
			return now >= tick && now - tick < ttl;
		}

		/// <summary>Does the hole hold this pawn by itself: trapped where it stands (RM_SuperdeepTrap.IsTrapped), not sealed
		/// under a lid (PIT_COVER_FIX_OCCUPANT_STAYS_BELOW: nobody serves a pawn through a lid)? The capture verdict, the float
		/// menu and the wardens all ask this one question.</summary>
		public static bool HoleHolds(Pawn p)
		{
			return p != null && p.Spawned && !Pits.RM_PitCoverBeneath.IsBeneath(p) && RM_SuperdeepTrap.IsTrapped(p);
		}

		/// <summary>A prisoner of the colony the hole holds, served from the lip (setting wardenFromLipEnabled). Not tied to
		/// bedlessPitPrisonEnabled: turning that off stops new bedless captures, it does not starve the ones already taken.</summary>
		public static bool LipServed(Pawn p)
		{
			if (!RimMandrakeFlowWorksSettings.wardenFromLipEnabled || p == null || !p.Spawned || !p.IsPrisonerOfColony)
			{
				return false;
			}
			Fresh();
			int now = Now;
			if (served.TryGetValue(p.thingIDNumber, out (int tick, bool v) m) && Live(m.tick, now, ServedTicks))
			{
				return m.v;
			}
			bool v = HoleHolds(p);
			served[p.thingIDNumber] = (now, v);
			return v;
		}

		/// <summary>Any lip-served prisoner on any map (gate of the AllowUnreachable patch; kept ServedTicks).</summary>
		public static bool AnyLipServed()
		{
			if (!RimMandrakeFlowWorksSettings.wardenFromLipEnabled)
			{
				return false;
			}
			Fresh();
			int now = Now;
			if (Live(anyTick, now, ServedTicks))
			{
				return anyServed;
			}
			bool any = false;
			List<Map> maps = Find.Maps;
			for (int i = 0; maps != null && i < maps.Count && !any; i++)
			{
				List<Pawn> list = maps[i].mapPawns.PrisonersOfColonySpawned;
				for (int j = 0; j < list.Count; j++)
				{
					if (LipServed(list[j]))
					{
						any = true;
						break;
					}
				}
			}
			anyTick = now;
			anyServed = any;
			return any;
		}

		/// <summary>The cells this pawn is held in: its band component (relative climb), its trap region (absolute rule).</summary>
		public readonly struct Pocket
		{
			private readonly RM_PocketGrid grid;
			private readonly int k;
			private readonly int comp;
			private readonly HashSet<IntVec3> region;
			public readonly bool valid;

			public Pocket(RM_PocketGrid grid, int k, int comp, HashSet<IntVec3> region)
			{
				this.grid = grid;
				this.k = k;
				this.comp = comp;
				this.region = region;
				valid = grid != null || region != null;
			}

			public bool Contains(IntVec3 c)
			{
				if (region != null)
				{
					return region.Contains(c);
				}
				return grid != null && grid.ComponentOf(k, c) == comp;
			}

			/// <summary>Every cell of the pocket (map cell indices for the grid; the region's cells for the absolute rule).</summary>
			public IEnumerable<IntVec3> Cells(Map map)
			{
				if (region != null)
				{
					foreach (IntVec3 c in region)
					{
						yield return c;
					}
					yield break;
				}
				if (grid == null)
				{
					yield break;
				}
				List<int> cells = grid.CellsOf(k, comp);
				for (int i = 0; i < cells.Count; i++)
				{
					yield return map.cellIndices.IndexToCell(cells[i]);
				}
			}
		}

		public static Pocket PocketOf(Pawn p)
		{
			if (p == null || !p.Spawned)
			{
				return default;
			}
			if (!RM_PocketGrid.Relative)
			{
				return RM_SuperdeepTrap.TryGetTrapRegion(p, out HashSet<IntVec3> region) ? new Pocket(null, 0, 0, region) : default;
			}
			int k = RM_PocketGrid.ClimbLimitOf(p);
			RM_PocketGrid g = RM_PocketGrid.ForPawn(p.Map, p);
			int comp = g.ComponentOf(k, p.Position);
			return comp >= 0 && g.ComponentIsPocket(k, comp) ? new Pocket(g, k, comp, null) : default;
		}

		/// <summary>RM_PitRooms.ShouldServeFromLipFor's second question (the first is "is it pit floor"): is this walk of a
		/// lip-kind job going to a lip-served prisoner's pocket from outside it? The prisoner is the destination itself (talk,
		/// tend, capture) or the job's B / A target (DeliverFood walks to its drop cell C, B is the deliveree).</summary>
		public static bool ServesJobAt(Pawn worker, LocalTargetInfo dest, IntVec3 cell)
		{
			if (worker == null || !RimMandrakeFlowWorksSettings.wardenFromLipEnabled)
			{
				return false;
			}
			Pawn prisoner = dest.Thing as Pawn;
			if (!LipServed(prisoner))
			{
				Job job = worker.CurJob;
				prisoner = job?.targetB.Thing as Pawn;
				if (!LipServed(prisoner))
				{
					prisoner = job?.targetA.Thing as Pawn;
					if (!LipServed(prisoner))
					{
						return false;
					}
				}
			}
			if (prisoner.Map != worker.Map)
			{
				return false;
			}
			Pocket pocket = PocketOf(prisoner);
			return pocket.valid && (cell == prisoner.Position || pocket.Contains(cell)) && !pocket.Contains(worker.Position);
		}

		/// <summary>The warden givers that can do their job from the lip (talking is Interact, food is Drop).</summary>
		public static RM_PitRoomMath.LipKind GiverKind(WorkGiver_Scanner g)
		{
			if (g is WorkGiver_Warden_DeliverFood)
			{
				return RM_PitRoomMath.LipKind.Drop;
			}
			if (g is WorkGiver_Warden_Chat || g is WorkGiver_Warden_Convert || g is WorkGiver_Warden_Enslave
				|| g is WorkGiver_Warden_InterrogateIdentity)
			{
				return RM_PitRoomMath.LipKind.Interact;
			}
			return RM_PitRoomMath.LipKind.None;
		}

		/// <summary>Vanilla's ShouldTakeCareOfPrisoner with the reach check left out (the lip check stands in for it).</summary>
		public static bool CareWithoutReach(Pawn warden, Pawn p, bool forced)
		{
			return p != null && p.IsPrisonerOfColony && p.guest != null && p.guest.PrisonerIsSecure && p.Spawned
				&& !p.InAggroMentalState && !p.IsForbidden(warden) && !RimWorld.Planet.CaravanFormingUtility.IsFormingCaravan(p)
				&& warden.CanReserve(p, 1, -1, null, forced);
		}

		/// <summary>A lip cell this warden can talk to the prisoner from (memoised per warden and prisoner).</summary>
		public static bool TryTalkLip(Pawn warden, Pawn p, out IntVec3 lip)
		{
			Fresh();
			int now = Now;
			var key = (warden.thingIDNumber, p.thingIDNumber, (int)RM_PitRoomMath.LipKind.Interact);
			if (lipMemo.TryGetValue(key, out (int tick, bool ok, IntVec3 cell) m) && Live(m.tick, now, MemoTicks))
			{
				lip = m.cell;
				return m.ok;
			}
			bool ok = RM_PitRooms.TryFindLipCell(warden, p.Position, RM_PitRoomMath.LipKind.Interact, out lip);
			lipMemo[key] = (now, ok, lip);
			return ok;
		}

		/// <summary>Where to drop food for this prisoner: the cell of HIS pocket nearest him that is in his room (food is
		/// proper for a prisoner only in his room), free to stand on and empty, on the rim (a neighbour outside the pocket),
		/// with a lip cell beside it this warden can stand on (RM_PitRooms.TryFindLipCell, Drop kind). Memoised per warden
		/// and prisoner; a remembered cell that has since filled is looked for again.</summary>
		public static bool TryDropSpot(Pawn warden, Pawn p, out IntVec3 drop)
		{
			drop = IntVec3.Invalid;
			if (warden == null || p == null || !p.Spawned || warden.Map != p.Map)
			{
				return false;
			}
			Fresh();
			int now = Now;
			Map map = p.Map;
			var key = (warden.thingIDNumber, p.thingIDNumber, (int)RM_PitRoomMath.LipKind.Drop);
			if (lipMemo.TryGetValue(key, out (int tick, bool ok, IntVec3 cell) m) && Live(m.tick, now, MemoTicks)
				&& (!m.ok || m.cell.GetFirstItem(map) == null))
			{
				drop = m.cell;
				return m.ok;
			}
			bool found = FindDropSpot(warden, p, map, out drop);
			lipMemo[key] = (now, found, drop);
			return found;
		}

		private static bool FindDropSpot(Pawn warden, Pawn p, Map map, out IntVec3 drop)
		{
			drop = IntVec3.Invalid;
			Pocket pocket = PocketOf(p);
			if (!pocket.valid)
			{
				return false;
			}
			Room room = p.GetRoom();
			int n = GenRadial.NumCellsInRadius(DropSearchRadius);
			int tries = 0;
			for (int i = 0; i < n && tries < DropLipTries; i++)
			{
				IntVec3 c = p.Position + GenRadial.RadialPattern[i];
				if (!c.InBounds(map))
				{
					continue;
				}
				bool inPocket = pocket.Contains(c);
				if (!RM_PitRoomMath.DropCell(inPocket, inPocket && c.GetRoom(map) == room,
					inPocket && c.Standable(map) && c.GetFirstItem(map) == null, inPocket && OnRim(pocket, c, map)))
				{
					continue;
				}
				tries++;
				if (RM_PitRooms.TryFindLipCell(warden, c, RM_PitRoomMath.LipKind.Drop, out _))
				{
					drop = c;
					return true;
				}
			}
			return false;
		}

		private static bool OnRim(Pocket pocket, IntVec3 c, Map map)
		{
			for (int i = 0; i < 8; i++)
			{
				IntVec3 n = c + GenAdj.AdjacentCells[i];
				if (n.InBounds(map) && !pocket.Contains(n))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Vanilla FoodAvailableInRoomTo, counted over the prisoner's pocket instead of his room: what he carries,
		/// what lies down there that he will eat, against what the hungry prisoners down there want (kept ServedTicks).</summary>
		public static bool FoodInPocket(Pawn p)
		{
			Fresh();
			int now = Now;
			if (fedMemo.TryGetValue(p.thingIDNumber, out (int tick, bool v) m) && Live(m.tick, now, ServedTicks))
			{
				return m.v;
			}
			bool v = CountFood(p);
			fedMemo[p.thingIDNumber] = (now, v);
			return v;
		}

		private static float NutritionFor(Pawn p, Thing t)
		{
			return t.def.IsNutritionGivingIngestible && p.WillEat(t) ? t.GetStatValue(StatDefOf.Nutrition) * t.stackCount : 0f;
		}

		private static bool CountFood(Pawn p)
		{
			Thing carried = p.carryTracker?.CarriedThing;
			bool carrying = carried != null && NutritionFor(p, carried) > 0f;
			if (carrying)
			{
				return RM_PitRoomMath.FoodEnoughInPocket(true, 0f, 0f);
			}
			Pocket pocket = PocketOf(p);
			if (!pocket.valid)
			{
				return false;
			}
			Map map = p.Map;
			float have = 0f;
			foreach (IntVec3 c in pocket.Cells(map))
			{
				List<Thing> things = map.thingGrid.ThingsListAtFast(c);
				for (int i = 0; i < things.Count; i++)
				{
					Thing t = things[i];
					if (!ThingRequestGroup.FoodSourceNotPlantOrTree.Includes(t.def))
					{
						continue;
					}
					if (!t.def.IsIngestible || (int)t.def.ingestible.preferability > 3)   // vanilla's own filter
					{
						have += NutritionFor(p, t);
					}
				}
			}
			float want = 0f;
			List<Pawn> prisoners = map.mapPawns.PrisonersOfColonySpawned;
			for (int i = 0; i < prisoners.Count; i++)
			{
				Pawn o = prisoners[i];
				Need_Food f = o.needs?.food;
				if (f == null || !pocket.Contains(o.Position) || f.CurLevelPercentage >= f.PercentageThreshHungry + 0.02f)
				{
					continue;
				}
				Thing oc = o.carryTracker?.CarriedThing;
				if (oc == null || !o.WillEat(oc))
				{
					want += f.NutritionWanted;
				}
			}
			return RM_PitRoomMath.FoodEnoughInPocket(false, have, want);
		}

		/// <summary>DeliverFood for a lip-served prisoner: vanilla's gates (can be brought food, hungry, not one to be fed by
		/// hand), then not when he is downed (he cannot get up to it), not when enough lies in his pocket, a drop cell, and
		/// vanilla's own food search. The food lands on the drop cell (JobDriver_FoodDeliver drops at target C).</summary>
		public static Job BuildFoodJob(Pawn warden, Pawn p)
		{
			Need_Food f = p.needs?.food;
			if (p.guest == null || !p.guest.CanBeBroughtFood || f == null || p.Downed
				|| f.CurLevelPercentage >= f.PercentageThreshHungry + 0.02f || WardenFeedUtility.ShouldBeFed(p)
				|| FoodInPocket(p) || !TryDropSpot(warden, p, out IntVec3 drop))
			{
				return null;
			}
			if (!FoodUtility.TryFindBestFoodSourceFor(warden, p, f.CurCategory == HungerCategory.Starving, out Thing food,
				out ThingDef foodDef, canRefillDispenser: false, canUseInventory: true, canUsePackAnimalInventory: false,
				allowForbidden: false, allowCorpse: false, allowSociallyImproper: false, allowHarvest: false,
				forceScanWholeMap: false, ignoreReservations: false, calculateWantedStackCount: true))
			{
				return null;
			}
			if (food.Spawned && PocketOf(p).Contains(food.Position))
			{
				return null;   // already down there: his own food job eats it
			}
			float nutrition = FoodUtility.GetNutrition(p, food, foodDef);
			Job job = JobMaker.MakeJob(JobDefOf.DeliverFood, food, p);
			job.count = FoodUtility.WillIngestStackCountOf(p, foodDef, nutrition);
			job.targetC = drop;
			return job;
		}
	}

	/// <summary>DRAINED_HOLE_IS_A_PRISON patch 1: JobGiver_Work offers a warden only prisoners he can reach unless the
	/// giver allows the unreachable. The five lip-capable warden givers allow it while a lip-served prisoner exists; their
	/// own ShouldTakeCareOfPrisoner (patch 2) still refuses anyone without a lip.</summary>
	[HarmonyPatch(typeof(WorkGiver_Scanner), nameof(WorkGiver_Scanner.AllowUnreachable), MethodType.Getter)]
	[RimMandrake.Shared.PatchFeature("Wardens work from the lip", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "wardenFromLipEnabled")]
	public static class RM_Patch_WorkGiverScanner_LipUnreachable
	{
		[HarmonyPostfix]
		public static void Postfix(WorkGiver_Scanner __instance, ref bool __result)
		{
			if (__result || !RimMandrakeFlowWorksSettings.wardenFromLipEnabled
				|| RM_BedlessPitPrison.GiverKind(__instance) == RM_PitRoomMath.LipKind.None)
			{
				return;
			}
			__result = RM_BedlessPitPrison.AnyLipServed();
		}
	}

	/// <summary>DRAINED_HOLE_IS_A_PRISON patch 2: for the five lip-capable warden givers, a lip-served prisoner the warden
	/// cannot reach is still his to care for when a lip cell will do (talk) or a rim drop cell has one (food). Every other
	/// warden giver keeps vanilla's answer.</summary>
	[HarmonyPatch(typeof(WorkGiver_Warden), "ShouldTakeCareOfPrisoner")]
	[RimMandrake.Shared.PatchFeature("Wardens work from the lip", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "wardenFromLipEnabled")]
	public static class RM_Patch_Warden_CareFromLip
	{
		[HarmonyPostfix]
		public static void Postfix(WorkGiver_Warden __instance, Pawn warden, Thing prisoner, bool forced, ref bool __result)
		{
			if (__result || !RimMandrakeFlowWorksSettings.wardenFromLipEnabled || warden == null)
			{
				return;
			}
			RM_PitRoomMath.LipKind kind = RM_BedlessPitPrison.GiverKind(__instance);
			if (kind == RM_PitRoomMath.LipKind.None || !(prisoner is Pawn p) || !RM_BedlessPitPrison.LipServed(p)
				|| p.Map != warden.Map || !RM_BedlessPitPrison.CareWithoutReach(warden, p, forced))
			{
				return;
			}
			RM_BedlessPitPrison.Pocket pocket = RM_BedlessPitPrison.PocketOf(p);
			if (!pocket.valid || pocket.Contains(warden.Position))
			{
				return;
			}
			__result = kind == RM_PitRoomMath.LipKind.Interact
				? RM_BedlessPitPrison.TryTalkLip(warden, p, out _)
				: RM_BedlessPitPrison.TryDropSpot(warden, p, out _);
		}
	}

	/// <summary>DRAINED_HOLE_IS_A_PRISON patch 3: food for a lip-served prisoner lands on a rim cell of his pocket. Acts when
	/// the hole is not a prison cell (vanilla stopped at IsInPrisonCell) or the warden cannot reach him (vanilla's chew spot
	/// may be in the middle of the hole, where no lip serves it).</summary>
	[HarmonyPatch(typeof(WorkGiver_Warden_DeliverFood), nameof(WorkGiver_Warden_DeliverFood.JobOnThing))]
	[RimMandrake.Shared.PatchFeature("Wardens work from the lip", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "wardenFromLipEnabled")]
	public static class RM_Patch_DeliverFood_FromLip
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, Thing t, bool forced, ref Job __result)
		{
			if (!RimMandrakeFlowWorksSettings.wardenFromLipEnabled || pawn == null || !(t is Pawn p)
				|| !RM_BedlessPitPrison.LipServed(p) || p.Map != pawn.Map)
			{
				return;
			}
			bool inCell = p.Position.IsInPrisonCell(p.Map);
			bool reaches = pawn.CanReach(p, PathEndMode.OnCell, pawn.NormalMaxDanger());
			if (inCell && reaches)
			{
				return;   // a prison cell he can walk into: vanilla's job, served from the lip by the path patch when it can be
			}
			if (__result != null)
			{
				// a prison cell he cannot reach: vanilla's food, our drop cell
				if (RM_BedlessPitPrison.TryDropSpot(pawn, p, out IntVec3 drop)
					&& !(__result.targetA.Thing is Thing food && food.Spawned && RM_BedlessPitPrison.PocketOf(p).Contains(food.Position)))
				{
					__result.targetC = drop;
				}
				else
				{
					__result = null;
				}
				return;
			}
			if (!RM_BedlessPitPrison.CareWithoutReach(pawn, p, forced))
			{
				return;
			}
			__result = RM_BedlessPitPrison.BuildFoodJob(pawn, p);
		}
	}
}
