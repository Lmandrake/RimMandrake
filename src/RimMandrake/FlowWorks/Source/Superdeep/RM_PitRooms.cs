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
			if (eng == null)
			{
				return false;
			}
			// PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP (design §8.5 step 7): a pit room is a person-band POCKET — pawn-independent
			// (GPT #11); a gentle bowl is no enclosure. PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER (owner card 2026-10-18): the pocket's
			// floor is at least the room depth for a person (default 3.0 m); taller creatures are checked per pawn
			// (HoldsBySize). Capture-down and lip service read the SAME test
			// (IsPitFloor), so rooms and the jobs done into them never disagree. The grid never rebuilds mid-flood.
			if (RM_PocketGrid.Relative)
			{
				return RM_RelativeRulesMath.PitRoomCell(RM_PocketGrid.IsPersonPocketCell(map, c), eng.ExcavatedDepthRaw(c), MinRoomNotches);
			}
			return eng.IsSuperdeepRaw(c);
		}

		/// <summary>The setting "a pit room's floor is at least N m down (for a person)", in notches (0 = any depth).</summary>
		public static int MinRoomNotches => RM_RelativeRulesMath.Notches(RimMandrakeFlowWorksSettings.pitRoomMinDepthMetres, 0);

		/// <summary>PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE: "down a pit" for everything that used to ask "is this cell dug 2 m":
		/// lip service, capture-down, exposure, the pit-room temperature coupling, liquid fire's trapped occupant and the
		/// knock-back exemption. Relative climb on: an uncovered dug square in a person-band pocket deep enough for a pit room
		/// (the room test, with or without the rooms setting). Off: the old absolute rule, an uncovered dug 2 m square.</summary>
		public static bool IsPitFloor(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			if (map == null || eng == null || !c.InBounds(map))
			{
				return false;
			}
			if (RM_PocketGrid.Relative)
			{
				int d = eng.ExcavatedDepthAt(c);
				return d > 0 && RM_RelativeRulesMath.PitRoomCell(RM_PocketGrid.IsPersonPocketCell(map, c), d, MinRoomNotches)
					&& !Pits.RM_SpanUtility.DeckedAt(map, c);
			}
			return eng.IsSuperdeepExcavation(c) && !Pits.RM_SpanUtility.DeckedAt(map, c);
		}

		/// <summary>The cheap "could any cell be a pit floor" early-out for IsPitFloor's callers.</summary>
		public static bool AnyPitFloor(RM_MapComponent_Excavation eng)
		{
			return eng != null && (RM_PocketGrid.Relative ? eng.ExcavatedCellCount > 0 : eng.SuperdeepCellCount > 0);
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

		private delegate void WalkabilityChangedFn(RegionDirtyer dirtyer, IntVec3 c, bool newWalkability);

		// r15 fix 3: an open delegate, not MethodInfo.Invoke (an object[] and two boxes per square). Harmony's patches on the
		// method still run: they detour the method itself.
		private static WalkabilityChangedFn walkabilityChanged;
		private static bool walkabilityLooked;

		/// <summary>A cell crossed into or out of D = 4: its regions (and neighbours') re-form.</summary>
		public static void NotifyPitnessChanged(Map map, IntVec3 c)
		{
			if (!RoomsOn || map?.regionDirtyer == null || !c.InBounds(map))
			{
				return;
			}
			if (!walkabilityLooked)
			{
				walkabilityLooked = true;
				MethodInfo m = AccessTools.Method(typeof(RegionDirtyer), "Notify_WalkabilityChanged");
				walkabilityChanged = m == null ? null : AccessTools.MethodDelegate<WalkabilityChangedFn>(m);
			}
			walkabilityChanged?.Invoke(map.regionDirtyer, c, c.Walkable(map));
		}

		/// <summary>A cut or fill crossed the pit-room depth (a setting other than 0 or 2 m; the 2 m crossing is already notified,
		/// and pocket flips are notified by the pocket grid's rebuild).</summary>
		public static void NotifyDepthCrossed(Map map, IntVec3 c, int before, int after)
		{
			int m = MinRoomNotches;
			if (m <= 0 || m == RM_ExcavationDepth.Superdeep || (before >= m) == (after >= m))
			{
				return;
			}
			NotifyPitnessChanged(map, c);
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

		/// <summary>Capture down's lip: one touching the held pawn (nearest the warden), else the reachable lip cell NEAREST THE
		/// HELD PAWN within talking range, to wait at until it comes close (RM_PitRoomMath.CaptureLipPick).</summary>
		public static RM_PitRoomMath.CaptureLip FindCaptureLip(Pawn warden, IntVec3 victimPos, out IntVec3 lip)
		{
			bool touch = TryFindLipCell(warden, victimPos, RM_PitRoomMath.LipKind.Touch, out lip);
			bool near = false;
			if (!touch)
			{
				Map map = warden?.Map;
				RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
				float radius = RM_PitRoomMath.RadiusFor(RM_PitRoomMath.LipKind.Interact);
				float best = float.MaxValue;
				if (eng != null)
				{
					foreach (IntVec3 c in GenRadial.RadialCellsAround(victimPos, radius, false))
					{
						if (!c.InBounds(map))
						{
							continue;
						}
						float d = c.DistanceToSquared(victimPos);
						if (d >= best || !RM_PitRoomMath.LipCandidate(IsPitFloor(map, eng, c), c.Standable(map), c.DistanceTo(victimPos), radius)
							|| !warden.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
						{
							continue;
						}
						best = d;
						lip = c;
					}
				}
				near = lip.IsValid;
			}
			return RM_PitRoomMath.CaptureLipPick(touch, near);
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
				if (!RM_PitRoomMath.LipCandidate(IsPitFloor(map, eng, c), c.Standable(map),
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
			IntVec3 cell = dest.HasThing ? dest.Thing.Position : dest.Cell;
			if (AnyPitFloor(eng) && IsPitFloor(worker.Map, eng, cell) && !IsPitFloor(worker.Map, eng, worker.Position))
			{
				return true;
			}
			// DRAINED_HOLE_IS_A_PRISON: a prisoner the hole holds (a shallow drained moat is no pit room) is served the same way
			return RM_BedlessPitPrison.ServesJobAt(worker, dest, cell);
		}

		// ── capture down ─────────────────────────────────────────────────

		public static RM_PitRoomMath.CaptureDownVerdict CaptureDownVerdict(Pawn target)
		{
			bool humanlike = target?.RaceProps != null && target.RaceProps.Humanlike && target.guest != null;
			bool ownSide = target != null && (target.Faction == Faction.OfPlayer || target.HostFaction == Faction.OfPlayer && !target.IsPrisonerOfColony);
			Room room = target != null && target.Spawned ? target.GetRoom() : null;
			bool prison = room != null && room.IsPrisonCell && IsPitRoom(room);
			// DRAINED_HOLE_IS_A_PRISON: with the bedless switch on, a pit that TRAPS the person is held and a prison, bed or not
			bool bedless = RimMandrakeFlowWorksSettings.bedlessPitPrisonEnabled;
			bool trapped = bedless && humanlike && !ownSide && target.Spawned && RM_BedlessPitPrison.HoleHolds(target);
			RM_PitRoomMath.CaptureDownVerdict v = RM_PitRoomMath.CaptureDown(RimMandrakeFlowWorksSettings.captureDownEnabled && RoomsOn,
				humanlike, ownSide, target != null && target.IsPrisonerOfColony,
				RM_PitRoomMath.BedlessHeld(target != null && RM_SuperdeepTrap.IsHeld(target) && HoldsBySize(target), bedless, trapped),
				RM_PitRoomMath.BedlessPrison(prison, bedless, trapped));
			// DRAINED_HOLE_IS_A_PRISON: taken without a bed while downed, he must be fed by hand from a lip touching him
			if (v != RM_PitRoomMath.CaptureDownVerdict.Allowed || prison || !target.Downed)
			{
				return v;
			}
			return RM_PitRoomMath.BedlessDowned(v, true, true, RM_BedlessPitPrison.TouchLipExists(target));
		}

		/// <summary>PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER: the pit room's person depth scaled by this pawn's height (RM_Drowning.HeightOf,
		/// the climb size band), so a tall creature needs a deeper pit before the room holds it. Relative rules off: always true.</summary>
		public static bool HoldsBySize(Pawn p)
		{
			if (p == null || !p.Spawned || !RM_PocketGrid.Relative)
			{
				return true;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(p.Map);
			if (eng == null)
			{
				return false;
			}
			float floorMetres = eng.ExcavatedDepthAt(p.Position) * RM_RelativeRulesMath.MetresPerNotch;
			return RM_PitRoomMath.DeepEnoughFor(floorMetres, RimMandrakeFlowWorksSettings.pitRoomMinDepthMetres, RM_Drowning.HeightOf(p));
		}

		public static string VerdictText(RM_PitRoomMath.CaptureDownVerdict v)
		{
			switch (v)
			{
				case RM_PitRoomMath.CaptureDownVerdict.NotHeld: return "RMFlow_CaptureDownNotHeld".Translate();
				case RM_PitRoomMath.CaptureDownVerdict.NoPrisonBed: return "RMFlow_CaptureDownNoPrisonBed".Translate();
				case RM_PitRoomMath.CaptureDownVerdict.DownedNoLip: return "RMFlow_CaptureDownDownedNoLip".Translate();
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
			// DRAINED_HOLE_IS_A_PRISON: off the pit-room floor, a person the hole traps (bedless switch on) is offered too
			if (eng == null || !RM_PitRooms.IsPitFloor(clickedPawn.Map, eng, clickedPawn.Position)
				&& !(RimMandrakeFlowWorksSettings.bedlessPitPrisonEnabled && clickedPawn.RaceProps.Humanlike
					&& RM_BedlessPitPrison.HoleHolds(clickedPawn)))
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
			if (RM_PitRooms.FindCaptureLip(warden, clickedPawn.Position, out IntVec3 lip) == RM_PitRoomMath.CaptureLip.None)
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

		/// <summary>Walks to a fresh lip so far (the held pawn wanders in the pit; CaptureDownNext bounds it).</summary>
		private int repaths;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref repaths, "rmCaptureRepaths", 0);
		}

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedOrNull(TargetIndex.A);
			this.FailOn(() => RM_PitRooms.CaptureDownVerdict(Victim) != RM_PitRoomMath.CaptureDownVerdict.Allowed);
			// PITCAPTURE_DIAGNOSE_PRISONER_FLAG_BACKSLIDES: after a repath, stand a moment at the lip so the held pawn can move
			// (none before the first walk).
			Toil pause = ToilMaker.MakeToil("RM_CaptureDown_Pause");
			pause.initAction = delegate
			{
				int ticks = RM_PitRoomMath.CapturePauseTicks(repaths);
				if (ticks <= 0)
				{
					ReadyForNextToil();
					return;
				}
				pawn.pather.StopDead();         // the Delay is defaultDuration = CaptureRepathPauseTicks
			};
			pause.defaultCompleteMode = ToilCompleteMode.Delay;
			pause.defaultDuration = RM_PitRoomMath.CaptureRepathPauseTicks;
			yield return pause;
			Toil walk = ToilMaker.MakeToil("RM_CaptureDown_ToLip");
			walk.initAction = delegate
			{
				IntVec3 lip = job.targetB.Cell;
				if (!lip.IsValid || !lip.AdjacentTo8WayOrInside(Victim.Position)
					|| RM_PitRooms.IsPitFloor(pawn.Map, RM_SuperdeepTrap.EngineOf(pawn.Map), lip))
				{
					// a lip touching it, else the lip nearest it to wait at (no lip touches the centre of a 3x3 pit)
					if (RM_PitRooms.FindCaptureLip(pawn, Victim.Position, out lip) == RM_PitRoomMath.CaptureLip.None)
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
			Toil reach = ToilMaker.MakeToil("RM_CaptureDown_Reach");
			reach.initAction = delegate
			{
				// the held pawn is not frozen: the lip can stop touching it while the warden walks (live: 95,167 -> 96,167)
				bool onPit = RM_PitRooms.IsPitFloor(pawn.Map, RM_SuperdeepTrap.EngineOf(pawn.Map), pawn.Position);
				switch (RM_PitRoomMath.CaptureDownNext(pawn.Position.AdjacentTo8WayOrInside(Victim.Position), onPit, repaths))
				{
					case RM_PitRoomMath.CaptureStep.Hold:
						JobDriver_CaptureDownPinned.Pin(Victim, pawn, RM_PitRoomMath.CaptureDownTicks + 30);
						return;
					case RM_PitRoomMath.CaptureStep.Repath:
						repaths++;
						job.targetB = IntVec3.Invalid;      // walk's initAction finds a lip touching where the pawn is now
						JumpToToil(pause);
						return;
					default:
						EndJobWith(JobCondition.Incompletable);
						return;
				}
			};
			reach.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return reach;
			Toil hold = Toils_General.Wait(RM_PitRoomMath.CaptureDownTicks, TargetIndex.A)
				.WithProgressBarToilDelay(TargetIndex.A);
			// PITCAPTURE_DIAGNOSE_PRISONER_FLAG_BACKSLIDES: a held pawn that slips out of reach mid-hold is followed (bounded),
			// not a failed job. PIT_CAPTURE_FIX_WARDEN_HURT_AT_LIP: the swinging that note saw was vanilla's Wait, the old pin.
			hold.AddPreTickIntervalAction(delegate(int delta)
			{
				bool onPit = RM_PitRooms.IsPitFloor(pawn.Map, RM_SuperdeepTrap.EngineOf(pawn.Map), pawn.Position);
				switch (RM_PitRoomMath.CaptureDownNext(pawn.Position.AdjacentTo8WayOrInside(Victim.Position), onPit, repaths))
				{
					case RM_PitRoomMath.CaptureStep.Hold:
						// PIT_CAPTURE_FIX_WARDEN_HURT_AT_LIP: a pin something else ended (damage, its lord) is put back
						JobDriver_CaptureDownPinned.Pin(Victim, pawn, ticksLeftThisToil + 30);
						return;
					case RM_PitRoomMath.CaptureStep.Repath:
						repaths++;
						job.targetB = IntVec3.Invalid;
						JumpToToil(pause);
						return;
					default:
						EndJobWith(JobCondition.Incompletable);
						return;
				}
			});
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
	/// <summary>PIT_CAPTURE_FIX_WARDEN_HURT_AT_LIP: the held pawn's pin while the warden takes it from the lip. It stands
	/// still facing the warden and does nothing else. The old pin was vanilla's PawnUtility.ForceWait, whose
	/// JobDriver_Wait.CheckForAutoAttack melees any hostile in the 9 cells around it every 4 ticks — and the warden at
	/// the lip is one of them (live round 5: Scratch and Crack on the warden, capture stopped). The job's
	/// expiryInterval ends it, as ForceWait's did; it also ends when the warden stops capturing.</summary>
	public class JobDriver_CaptureDownPinned : JobDriver
	{
		/// <summary>Pin <paramref name="victim"/> for <paramref name="ticks"/>, facing <paramref name="warden"/>. A pawn
		/// already pinned is left alone; a downed, sleeping, bedded or shut-down one (it swings at nobody) keeps
		/// vanilla's posture-aware wait.</summary>
		public static void Pin(Pawn victim, Pawn warden, int ticks)
		{
			if (victim == null || victim.jobs == null || !victim.Spawned || ticks <= 0
				|| victim.CurJobDef == RimMandrakeFlowWorks_DefOf.RM_CaptureDownPinned)
			{
				return;
			}
			if (victim.Downed || !victim.Awake() || victim.InBed() || victim.IsDeactivated() || victim.IsSelfShutdown())
			{
				if (victim.CurJobDef != JobDefOf.Wait && victim.CurJobDef != JobDefOf.Wait_MaintainPosture)
				{
					PawnUtility.ForceWait(victim, ticks, warden);
				}
				return;
			}
			Job job = JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_CaptureDownPinned, warden);
			job.expiryInterval = ticks;
			victim.jobs.StartJob(job, JobCondition.InterruptForced, null, resumeCurJobAfterwards: true);
		}

		private Pawn Warden => job.targetA.Thing as Pawn;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return true;
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedOrNull(TargetIndex.A);
			this.FailOn(() => Warden == null || Warden.CurJobDef != RimMandrakeFlowWorks_DefOf.RM_CaptureDown);
			Toil pinned = ToilMaker.MakeToil("RM_CaptureDownPinned");
			pinned.initAction = delegate
			{
				pawn.pather?.StopDead();
			};
			pinned.handlingFacing = true;
			pinned.tickAction = delegate
			{
				pawn.rotationTracker.FaceTarget(job.targetA);
			};
			pinned.defaultCompleteMode = ToilCompleteMode.Never;
			yield return pinned;
		}
	}
}
