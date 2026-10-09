using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// SUPERDEEP_PRISON_ROOM_1 — an enclosed superdeep area is a ROOM.
	///
	/// Owner, 2026-09-17: <i>"This defines a "room" if it's enclosed that you can use for prisoner
	/// storage."</i> … <i>"It's just a room until you put a prisoner bed in it."</i>
	///
	/// MEASURED (SUPERDEEP_SEAM_MEASURE_1 item 3, decompiled 1.6): regions split only on
	/// RegionTypeUtility.GetExpectedRegionType, which reads terrain only through walkability, so a
	/// walkable D = 4 cell is the same region type as its lip and an enclosed pit is NOT a room by
	/// itself. LAW 2 exception [D] lets depth bound a room; it is cashed here, at every place vanilla
	/// decides two cells / regions / districts belong together, by adding ONE more equality — both
	/// superdeep or both not (RM_PitRoomMath.SameSide):
	///   1. RegionMaker.FloodFillAndAddCells' cell predicate (postfix on its lambda): a region never
	///      straddles the pit wall.
	///   2. RegionMaker.SweepInTwoDirectionsAndTryToCreateLink (transpiler): a link's edge span stops
	///      where the far side changes pit-ness, so the two regions on each side of a link always
	///      agree on the span (an unmatched span is a one-sided link, i.e. broken pathing).
	///   3. RegionTraverser.FloodAndSetDistricts / FloodAndSetNewRegionIndex (replaced while the rule
	///      is on): a district never straddles the wall.
	///   4. Region.NeighborsOfSameType (filtered): district re-use never adopts across the wall.
	///   5. RegionAndRoomUpdater.ShouldBeInTheSameRoom (narrowed): two Normal districts on opposite
	///      sides of the wall are never one room.
	/// Pathing and reachability are untouched — regions on both sides stay LINKED; only room
	/// membership changes. A pit touching the map edge is still an outdoor room (vanilla
	/// ProperRoom), so it is never a prison.
	///
	/// Re-region triggers: Deepen into D = 4 and FillIn out of it (RM_MapComponent_Excavation), and
	/// the Mod Setting being flipped (every map rebuilt).
	/// </summary>
	public static class RM_PitRooms
	{
		public static bool RoomsOn => RimMandrakeFlowWorksSettings.superdeepRoomsEnabled;

		/// <summary>Pit-ness for room purposes: a DUG superdeep cell. Reads the raw grid (never the
		/// cached superdeep count) because Map.FinalizeInit rebuilds regions before map components'
		/// FinalizeInit has recounted anything.</summary>
		public static bool IsPitCell(Map map, IntVec3 c)
		{
			if (!RoomsOn || map == null)
			{
				return false;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			return eng != null && eng.IsSuperdeepRaw(c);
		}

		private sealed class Side
		{
			public bool pit;
		}

		private static readonly ConditionalWeakTable<Region, Side> regionSide = new ConditionalWeakTable<Region, Side>();

		public static bool IsPitRegion(Region r)
		{
			if (!RoomsOn || r == null)
			{
				return false;
			}
			if (regionSide.TryGetValue(r, out Side s))
			{
				return s.pit;
			}
			return IsPitCell(r.Map, r.AnyCell);
		}

		public static bool IsPitDistrict(District d)
		{
			return d != null && d.RegionCount > 0 && IsPitRegion(d.Regions[0]);
		}

		/// <summary>True when the room is made of superdeep cells (a pit room).</summary>
		public static bool IsPitRoom(Room room)
		{
			if (room == null || !RoomsOn)
			{
				return false;
			}
			foreach (District d in room.Districts)
			{
				if (d.RegionType == RegionType.Normal)
				{
					return IsPitDistrict(d);
				}
			}
			return false;
		}

		internal static void RecordRegionSide(Region r, bool pit)
		{
			regionSide.Remove(r);
			regionSide.Add(r, new Side { pit = pit });
		}

		// ── re-region triggers ─────────────────────────────────────────────

		private static MethodInfo walkabilityChanged;

		/// <summary>A cell crossed into or out of D = 4: its regions (and neighbours') re-form.</summary>
		public static void NotifyPitnessChanged(Map map, IntVec3 c)
		{
			if (!RoomsOn || map?.regionDirtyer == null || !c.InBounds(map))
			{
				return;
			}
			if (walkabilityChanged == null)
			{
				walkabilityChanged = AccessTools.Method(typeof(RegionDirtyer), "Notify_WalkabilityChanged");
			}
			walkabilityChanged?.Invoke(map.regionDirtyer, new object[] { c, c.Walkable(map) });
		}

		/// <summary>The setting was flipped: every map's rooms are re-derived.</summary>
		public static void RebuildAllMaps()
		{
			if (Current.ProgramState != ProgramState.Playing || Find.Maps == null)
			{
				return;
			}
			foreach (Map m in Find.Maps)
			{
				m.regionAndRoomUpdater?.RebuildAllRegionsAndRooms();
			}
		}

		// ── flood state for patches 1 and 2 (region building is single-threaded, never nested) ──
		internal static Map floodMap;
		internal static bool floodPit;
		internal static bool floodActive;

		internal static Map sweepMap;
		internal static bool sweepFirst;
		internal static bool sweepPit;

		/// <summary>An impossible RegionType value, returned so a vanilla equality test fails.</summary>
		internal const RegionType OtherSide = (RegionType)0x4000;

		/// <summary>Patch 2's replacement for GetExpectedRegionType inside the link sweep. The first
		/// call in each sweep is the far cell c2 that fixes the expected type; later calls report a
		/// far cell on the other side of the pit wall as a different type, ending the span there.</summary>
		public static RegionType SweepExpectedType(IntVec3 c, Map map)
		{
			RegionType t = c.GetExpectedRegionType(map);
			if (!RoomsOn)
			{
				return t;
			}
			bool pit = IsPitCell(map, c);
			if (sweepFirst || !ReferenceEquals(map, sweepMap))
			{
				sweepFirst = false;
				sweepMap = map;
				sweepPit = pit;
				return t;
			}
			return RM_PitRoomMath.SameSide(pit, sweepPit) ? t : OtherSide;
		}

		// ── lip service: wardens do pit jobs from the lip ───────────────────

		private static readonly Dictionary<JobDef, RM_PitRoomMath.LipKind> kindCache = new Dictionary<JobDef, RM_PitRoomMath.LipKind>();

		public static RM_PitRoomMath.LipKind KindOf(JobDef def)
		{
			if (def == null)
			{
				return RM_PitRoomMath.LipKind.None;
			}
			if (!kindCache.TryGetValue(def, out RM_PitRoomMath.LipKind k))
			{
				k = RM_PitRoomMath.KindOf(def.defName);
				kindCache[def] = k;
			}
			return k;
		}

		/// <summary>The best cell to do a job on <paramref name="target"/> from WITHOUT standing in
		/// the pit: not superdeep, standable, reachable, within the kind's radius (and, for a social
		/// interaction, in vanilla's interaction position: 6 cells with line of sight). Nearest to the
		/// worker wins.</summary>
		public static bool TryFindLipCell(Pawn worker, IntVec3 target, RM_PitRoomMath.LipKind kind, out IntVec3 lip)
		{
			lip = IntVec3.Invalid;
			Map map = worker?.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null || kind == RM_PitRoomMath.LipKind.None)
			{
				return false;
			}
			float radius = RM_PitRoomMath.RadiusFor(kind);
			float best = float.MaxValue;
			foreach (IntVec3 c in GenRadial.RadialCellsAround(target, radius, false))
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				if (!RM_PitRoomMath.LipCandidate(eng.IsSuperdeepExcavation(c), c.Standable(map),
					c.DistanceTo(target), radius))
				{
					continue;
				}
				if (kind == RM_PitRoomMath.LipKind.Interact && !SocialInteractionUtility.IsGoodPositionForInteraction(c, target, map))
				{
					continue;
				}
				float d = c.DistanceToSquared(worker.Position);
				if (d >= best)
				{
					continue;
				}
				if (!worker.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
				{
					continue;
				}
				best = d;
				lip = c;
			}
			return lip.IsValid;
		}

		/// <summary>Whether a worker's path to <paramref name="dest"/> should be served from the lip.</summary>
		public static bool ShouldServeFromLip(Pawn worker, LocalTargetInfo dest, out RM_PitRoomMath.LipKind kind)
		{
			return ShouldServeFromLipFor(worker, worker?.CurJobDef, dest, out kind);
		}

		/// <summary>The same gate for a named job (the northstar proof asks it without a running job).</summary>
		public static bool ShouldServeFromLipFor(Pawn worker, JobDef job, LocalTargetInfo dest, out RM_PitRoomMath.LipKind kind)
		{
			kind = RM_PitRoomMath.LipKind.None;
			if (!RimMandrakeFlowWorksSettings.wardenFromLipEnabled || worker == null || !worker.Spawned
				|| worker.Faction != Faction.OfPlayer || !dest.IsValid)
			{
				return false;
			}
			kind = KindOf(job);
			if (kind == RM_PitRoomMath.LipKind.None)
			{
				return false;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(worker.Map);
			if (eng == null || eng.SuperdeepCellCount == 0)
			{
				return false;
			}
			IntVec3 cell = dest.HasThing ? dest.Thing.Position : dest.Cell;
			return eng.IsSuperdeepExcavation(cell) && !eng.IsSuperdeepExcavation(worker.Position);
		}

		// ── capture down ─────────────────────────────────────────────────

		public static RM_PitRoomMath.CaptureDownVerdict CaptureDownVerdict(Pawn target)
		{
			bool humanlike = target?.RaceProps != null && target.RaceProps.Humanlike && target.guest != null;
			bool ownSide = target != null && (target.Faction == Faction.OfPlayer || target.HostFaction == Faction.OfPlayer && !target.IsPrisonerOfColony);
			Room room = target != null && target.Spawned ? target.GetRoom() : null;
			bool prison = room != null && room.IsPrisonCell && IsPitRoom(room);
			return RM_PitRoomMath.CaptureDown(RimMandrakeFlowWorksSettings.captureDownEnabled && RoomsOn,
				humanlike, ownSide, target != null && target.IsPrisonerOfColony,
				target != null && RM_SuperdeepTrap.IsHeld(target), prison);
		}

		public static string VerdictText(RM_PitRoomMath.CaptureDownVerdict v)
		{
			switch (v)
			{
				case RM_PitRoomMath.CaptureDownVerdict.NotHeld: return "RMFlow_CaptureDownNotHeld".Translate();
				case RM_PitRoomMath.CaptureDownVerdict.NoPrisonBed: return "RMFlow_CaptureDownNoPrisonBed".Translate();
				default: return null;
			}
		}
	}

	// ══════════════════════════════════════════════════════════════════════
	// Harmony
	// ══════════════════════════════════════════════════════════════════════

	/// <summary>Patch 1a: remember the root's side before the region flood fill runs.</summary>
	[HarmonyPatch(typeof(RegionMaker), "FloodFillAndAddCells")]
	[RimMandrake.Shared.PatchFeature("An enclosed pit is its own room", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepRoomsEnabled")]
	public static class RM_Patch_RegionMaker_FloodSide
	{
		[HarmonyPrefix]
		public static void Prefix(IntVec3 root, Map ___map)
		{
			RM_PitRooms.floodMap = ___map;
			RM_PitRooms.floodPit = RM_PitRooms.IsPitCell(___map, root);
			RM_PitRooms.floodActive = RM_PitRooms.RoomsOn;
		}

		[HarmonyPostfix]
		public static void Postfix(Region ___newReg)
		{
			RM_PitRooms.floodActive = false;
			if (___newReg != null && RM_PitRooms.RoomsOn)
			{
				RM_PitRooms.RecordRegionSide(___newReg, RM_PitRooms.floodPit);
			}
		}
	}

	/// <summary>Patch 1b: the flood fill's cell predicate (a compiler-generated lambda) refuses a
	/// cell on the other side of the pit wall.</summary>
	[HarmonyPatch]
	[RimMandrake.Shared.PatchFeature("An enclosed pit is its own room", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepRoomsEnabled")]
	public static class RM_Patch_RegionMaker_FloodPredicate
	{
		private static MethodBase target;

		private static MethodBase Find()
		{
			if (target != null)
			{
				return target;
			}
			IEnumerable<Type> types = new[] { typeof(RegionMaker) }.Concat(typeof(RegionMaker).GetNestedTypes(AccessTools.all));
			foreach (Type t in types)
			{
				foreach (MethodInfo m in t.GetMethods(AccessTools.allDeclared))
				{
					ParameterInfo[] ps = m.GetParameters();
					if (m.Name.Contains("FloodFillAndAddCells") && m.ReturnType == typeof(bool)
						&& ps.Length == 1 && ps[0].ParameterType == typeof(IntVec3))
					{
						target = m;
						return target;
					}
				}
			}
			return null;
		}

		public static bool Prepare()
		{
			bool ok = Find() != null;
			if (!ok)
			{
				Log.Warning("[RimMandrake.FlowWorks] SUPERDEEP_PRISON_ROOM_1: RegionMaker flood predicate not found; "
					+ "pits will not form their own rooms.");
			}
			return ok;
		}

		public static MethodBase TargetMethod()
		{
			return Find();
		}

		[HarmonyPostfix]
		public static void Postfix(IntVec3 __0, ref bool __result)
		{
			if (__result && RM_PitRooms.floodActive
				&& !RM_PitRoomMath.SameSide(RM_PitRooms.IsPitCell(RM_PitRooms.floodMap, __0), RM_PitRooms.floodPit))
			{
				__result = false;
			}
		}
	}

	/// <summary>Patch 2: link spans stop at the pit wall (see SweepExpectedType).</summary>
	[HarmonyPatch(typeof(RegionMaker), "SweepInTwoDirectionsAndTryToCreateLink")]
	[RimMandrake.Shared.PatchFeature("An enclosed pit is its own room", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepRoomsEnabled")]
	public static class RM_Patch_RegionMaker_LinkSweep
	{
		[HarmonyPrefix]
		public static void Prefix()
		{
			RM_PitRooms.sweepFirst = true;
		}

		[HarmonyTranspiler]
		public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
		{
			MethodInfo vanilla = AccessTools.Method(typeof(RegionTypeUtility), nameof(RegionTypeUtility.GetExpectedRegionType),
				new[] { typeof(IntVec3), typeof(Map) });
			MethodInfo ours = AccessTools.Method(typeof(RM_PitRooms), nameof(RM_PitRooms.SweepExpectedType));
			int swapped = 0;
			foreach (CodeInstruction ci in instructions)
			{
				if (ci.Calls(vanilla))
				{
					ci.opcode = OpCodes.Call;
					ci.operand = ours;
					swapped++;
				}
				yield return ci;
			}
			if (swapped != 3)
			{
				Log.Warning("[RimMandrake.FlowWorks] SUPERDEEP_PRISON_ROOM_1: link sweep had " + swapped
					+ " GetExpectedRegionType calls (expected 3).");
			}
		}
	}

	/// <summary>Patch 3a: a district never straddles the pit wall.</summary>
	[HarmonyPatch(typeof(RegionTraverser), nameof(RegionTraverser.FloodAndSetDistricts))]
	[RimMandrake.Shared.PatchFeature("An enclosed pit is its own room", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepRoomsEnabled")]
	public static class RM_Patch_RegionTraverser_Districts
	{
		[HarmonyPrefix]
		public static bool Prefix(Region root, Map map, District existingRoom, ref District __result)
		{
			if (!RM_PitRooms.RoomsOn)
			{
				return true;
			}
			District flooding = existingRoom ?? District.MakeNew(map);
			root.District = flooding;
			__result = flooding;
			if (!root.type.AllowsMultipleRegionsPerDistrict())
			{
				return false;
			}
			bool rootPit = RM_PitRooms.IsPitRegion(root);
			RegionTraverser.BreadthFirstTraverse(root,
				(Region from, Region r) => r.type == root.type && r.District != flooding
					&& RM_PitRoomMath.SameSide(RM_PitRooms.IsPitRegion(r), rootPit),
				delegate (Region r)
				{
					r.District = flooding;
					return false;
				}, 999999, RegionType.Set_All);
			return false;
		}
	}

	/// <summary>Patch 3b: new-region grouping (the step before districts) honours the wall too.</summary>
	[HarmonyPatch(typeof(RegionTraverser), nameof(RegionTraverser.FloodAndSetNewRegionIndex))]
	[RimMandrake.Shared.PatchFeature("An enclosed pit is its own room", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepRoomsEnabled")]
	public static class RM_Patch_RegionTraverser_NewIndex
	{
		[HarmonyPrefix]
		public static bool Prefix(Region root, int newRegionGroupIndex)
		{
			if (!RM_PitRooms.RoomsOn)
			{
				return true;
			}
			root.newRegionGroupIndex = newRegionGroupIndex;
			if (root.type.AllowsMultipleRegionsPerDistrict())
			{
				bool rootPit = RM_PitRooms.IsPitRegion(root);
				RegionTraverser.BreadthFirstTraverse(root,
					(Region from, Region r) => r.type == root.type && r.newRegionGroupIndex < 0
						&& RM_PitRoomMath.SameSide(RM_PitRooms.IsPitRegion(r), rootPit),
					delegate (Region r)
					{
						r.newRegionGroupIndex = newRegionGroupIndex;
						return false;
					}, 999999, RegionType.Set_All);
			}
			return false;
		}
	}

	/// <summary>Patch 4: "same type" neighbours are also same-side neighbours.</summary>
	[HarmonyPatch(typeof(Region), nameof(Region.NeighborsOfSameType), MethodType.Getter)]
	[RimMandrake.Shared.PatchFeature("An enclosed pit is its own room", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepRoomsEnabled")]
	public static class RM_Patch_Region_NeighborsOfSameType
	{
		[HarmonyPostfix]
		public static IEnumerable<Region> Postfix(IEnumerable<Region> __result, Region __instance)
		{
			if (!RM_PitRooms.RoomsOn)
			{
				foreach (Region r in __result)
				{
					yield return r;
				}
				yield break;
			}
			bool pit = RM_PitRooms.IsPitRegion(__instance);
			foreach (Region r in __result)
			{
				if (RM_PitRoomMath.SameSide(RM_PitRooms.IsPitRegion(r), pit))
				{
					yield return r;
				}
			}
		}
	}

	/// <summary>Patch 5: two districts on opposite sides of the wall are never one room.</summary>
	[HarmonyPatch(typeof(RegionAndRoomUpdater), "ShouldBeInTheSameRoom")]
	[RimMandrake.Shared.PatchFeature("An enclosed pit is its own room", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepRoomsEnabled")]
	public static class RM_Patch_RoomUpdater_SameRoom
	{
		[HarmonyPostfix]
		public static void Postfix(District a, District b, ref bool __result)
		{
			if (__result && RM_PitRooms.RoomsOn
				&& !RM_PitRoomMath.SameSide(RM_PitRooms.IsPitDistrict(a), RM_PitRooms.IsPitDistrict(b)))
			{
				__result = false;
			}
		}
	}

	/// <summary>Lip service: a warden (or doctor) doing a prison job on someone in a pit walks to
	/// the lip, never into the pit ("no you don't have to go down and enter the room").</summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), nameof(Pawn_PathFollower.StartPath))]
	[RimMandrake.Shared.PatchFeature("Wardens work from the lip", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "wardenFromLipEnabled")]
	public static class RM_Patch_PathFollower_LipService
	{
		[HarmonyPrefix]
		public static void Prefix(Pawn ___pawn, ref LocalTargetInfo dest, ref PathEndMode peMode)
		{
			if (!RM_PitRooms.ShouldServeFromLip(___pawn, dest, out RM_PitRoomMath.LipKind kind))
			{
				return;
			}
			IntVec3 cell = dest.HasThing ? dest.Thing.Position : dest.Cell;
			if (RM_PitRooms.TryFindLipCell(___pawn, cell, kind, out IntVec3 lip))
			{
				dest = lip;
				peMode = PathEndMode.OnCell;
			}
		}
	}

	/// <summary>Capture down — the float-menu order.</summary>
	public class FloatMenuOptionProvider_CaptureDown : FloatMenuOptionProvider
	{
		protected override bool Drafted => true;

		protected override bool Undrafted => true;

		protected override bool Multiselect => false;

		protected override bool RequiresManipulation => true;

		protected override FloatMenuOption GetSingleOptionFor(Pawn clickedPawn, FloatMenuContext context)
		{
			Pawn warden = context.FirstSelectedPawn;
			if (clickedPawn == null || warden == null || !clickedPawn.Spawned
				|| !RimMandrakeFlowWorksSettings.captureDownEnabled || !RM_PitRooms.RoomsOn)
			{
				return null;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(clickedPawn.Map);
			if (eng == null || !eng.IsSuperdeepExcavation(clickedPawn.Position))
			{
				return null;
			}
			RM_PitRoomMath.CaptureDownVerdict v = RM_PitRooms.CaptureDownVerdict(clickedPawn);
			string label = "RMFlow_CaptureDown".Translate(clickedPawn.LabelShort);
			if (v == RM_PitRoomMath.CaptureDownVerdict.SettingOff || v == RM_PitRoomMath.CaptureDownVerdict.NotAPerson
				|| v == RM_PitRoomMath.CaptureDownVerdict.OwnSide || v == RM_PitRoomMath.CaptureDownVerdict.AlreadyPrisoner)
			{
				return null;
			}
			if (v != RM_PitRoomMath.CaptureDownVerdict.Allowed)
			{
				return new FloatMenuOption(label + " (" + RM_PitRooms.VerdictText(v) + ")", null);
			}
			if (!RM_PitRooms.TryFindLipCell(warden, clickedPawn.Position, RM_PitRoomMath.LipKind.Touch, out IntVec3 lip))
			{
				return new FloatMenuOption(label + " (" + "RMFlow_CaptureDownNoLip".Translate() + ")", null);
			}
			return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(label, delegate
			{
				Job job = JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_CaptureDown, clickedPawn, lip);
				job.count = 1;
				warden.jobs.TryTakeOrderedJob(job, JobTag.Misc);
			}, MenuOptionPriority.Default, revalidateClickTarget: clickedPawn), warden, clickedPawn);
		}
	}

	/// <summary>Capture down from the lip: walk to a lip cell touching the held pawn, take a moment,
	/// and the pawn is a prisoner of the colony (vanilla CapturedBy — weapons drop, its lord lets go).
	/// The warden never stands on a superdeep cell.</summary>
	public class JobDriver_CaptureDown : JobDriver
	{
		private Pawn Victim => (Pawn)job.targetA.Thing;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedOrNull(TargetIndex.A);
			this.FailOn(() => RM_PitRooms.CaptureDownVerdict(Victim) != RM_PitRoomMath.CaptureDownVerdict.Allowed);
			Toil walk = ToilMaker.MakeToil("RM_CaptureDown_ToLip");
			walk.initAction = delegate
			{
				IntVec3 lip = job.targetB.Cell;
				if (!lip.IsValid || !lip.AdjacentTo8WayOrInside(Victim.Position)
					|| RM_SuperdeepTrap.EngineOf(pawn.Map).IsSuperdeepExcavation(lip))
				{
					if (!RM_PitRooms.TryFindLipCell(pawn, Victim.Position, RM_PitRoomMath.LipKind.Touch, out lip))
					{
						EndJobWith(JobCondition.Incompletable);
						return;
					}
					job.targetB = lip;
				}
				pawn.pather.StartPath(lip, PathEndMode.OnCell);
			};
			walk.defaultCompleteMode = ToilCompleteMode.PatherArrival;
			yield return walk;
			Toil hold = Toils_General.Wait(RM_PitRoomMath.CaptureDownTicks, TargetIndex.A)
				.WithProgressBarToilDelay(TargetIndex.A);
			hold.FailOn(() => !pawn.Position.AdjacentTo8WayOrInside(Victim.Position)
				|| RM_SuperdeepTrap.EngineOf(pawn.Map).IsSuperdeepExcavation(pawn.Position));
			yield return hold;
			yield return Toils_General.Do(delegate
			{
				Pawn v = Victim;
				v.guest.CapturedBy(Faction.OfPlayer, pawn);
				v.jobs?.StopAll();
				Messages.Message("RMFlow_CapturedDown".Translate(pawn.LabelShort, v.LabelShort), v,
					MessageTypeDefOf.PositiveEvent);
			});
		}
	}
}
