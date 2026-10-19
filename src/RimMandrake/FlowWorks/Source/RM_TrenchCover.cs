using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	// ════════════════════════════════════════════════════════════════════
	// TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT (design/RimMandrake/canal_cover_design_2026-10-17.md §3, §4, §7, §10).
	// LAW 2 as replaced by the owner 2026-10-18: depth affects movement, liquid AND COVER; never sight or height
	// advantage. A pawn standing in a dug hole, wet or dry, is covered by each neighbour whose ground is higher than its
	// floor, read like a vanilla sandbag (RM_TrenchCoverMath, selftested). No blast cover (Q7): explosions never read
	// CoverUtility. Raiders read it through vanilla's own cover readers; the cage guard (Q5) keeps them out of pockets
	// they could not climb out of.
	//
	// Engine facts (RimSage, 1.6, read 2026-10-18): CoverUtility.CalculateOverallBlockChance(LocalTargetInfo, IntVec3,
	// Map) is read by ShotReport.HitReportFor, CastPositionFinder.CastPositionPreference (target = the CANDIDATE cell,
	// the occupant is CastPositionFinder.req.caster), AttackTargetFinder (target = a cell) and JobGiver_AIFightEnemy.
	// ShotReport's private fields coversOverallBlockChance / factorFromCoveringGas / target. Verb_LaunchProjectile
	// fires a cover miss AT a CoverInfo.Thing, so trench cover never enters ShotReport's cover field (the null-cover
	// trap, §2): HitReportFor gets vanilla's block back and the trench share as an aim factor (a wild miss).
	// ════════════════════════════════════════════════════════════════════

	public static class RM_TrenchCover
	{
		public static bool On => RimMandrakeFlowWorksSettings.trenchCoverEnabled;

		/// <summary>Set while CalculateOverallBlockChance must answer vanilla only (HitReportFor's fold).</summary>
		[System.ThreadStatic] internal static bool suppress;

		/// <summary>The would-be occupant of the cell CastPositionPreference is scoring (its target is a bare cell).</summary>
		[System.ThreadStatic] internal static Pawn castCandidateOccupant;

		/// <summary>The square depth trench cover reads (notches): the hollow depth (dug, or a dry pond bed with hollows
		/// on; natural water 0), an intact pit cover read as ground; -1 out of bounds.</summary>
		public static int GroundDepthAt(Map map, RM_MapComponent_Excavation eng, int x, int z)
		{
			var c = new IntVec3(x, 0, z);
			if (!c.InBounds(map))
			{
				return -1;
			}
			int h = eng.HollowDepthAt(c);
			return RM_TrenchCoverMath.GroundDepth(h, h > 0 && Pits.RM_PitCoverUtility.IsCovered(map, c));
		}

		/// <summary>Who stands (or would stand) on the target square: the target pawn, the cast-position candidate's
		/// caster, else the first pawn there; null = a person.</summary>
		private static Pawn OccupantOf(LocalTargetInfo target, Map map)
		{
			if (target.HasThing)
			{
				return target.Thing as Pawn;
			}
			if (castCandidateOccupant != null)
			{
				return castCandidateOccupant;
			}
			return target.Cell.InBounds(map) ? target.Cell.GetFirstPawn(map) : null;
		}

		/// <summary>The trench block chance for this target against a shooter at <paramref name="shooterLoc"/>; 0 when
		/// off, when nothing is dug, when the target is not a standing, walking pawn on a hollow, or when it is a swimmer.</summary>
		public static float BlockFor(LocalTargetInfo target, IntVec3 shooterLoc, Map map)
		{
			if (!On || map == null || !target.IsValid)
			{
				return 0f;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepShooting.EngineFor(map);
			if (eng == null || eng.ClimbCellCount == 0)
			{
				return 0f;
			}
			IntVec3 cell = target.Cell;
			if (GroundDepthAt(map, eng, cell.x, cell.z) <= 0)
			{
				return 0f;
			}
			if (target.HasThing && !(target.Thing is Pawn))
			{
				return 0f;
			}
			Pawn p = OccupantOf(target, map);
			float size = 1f;
			if (p != null)
			{
				// §3.1: on its feet, not swimming, not flying.
				if (p.Flying || p.GetPosture() != PawnPosture.Standing || p.Downed || !p.def.CanBenefitFromCover)
				{
					return 0f;
				}
				size = p.BodySize;
			}
			if (eng.IsDugSwimCell(cell))
			{
				return 0f;
			}
			return RM_TrenchCoverMath.TrenchBlock((x, z) => GroundDepthAt(map, eng, x, z), cell.x, cell.z, shooterLoc.x,
				shooterLoc.z, RM_TrenchCoverMath.HeightMetres(size), RimMandrakeFlowWorksSettings.trenchCoverStrength);
		}

		/// <summary>Vanilla's block (suppressed) for the fold.</summary>
		public static float VanillaBlock(LocalTargetInfo target, IntVec3 shooterLoc, Map map)
		{
			bool was = suppress;
			suppress = true;
			try
			{
				return CoverUtility.CalculateOverallBlockChance(target, shooterLoc, map);
			}
			finally
			{
				suppress = was;
			}
		}

		// ── the HitReportFor fold, remembered for the readout of the same report ──
		[System.ThreadStatic] internal static IntVec3 lastFoldCell;
		[System.ThreadStatic] internal static float lastFoldGas;
		[System.ThreadStatic] internal static float lastFoldFactor;

		/// <summary>Q5: a square the caster could not climb out of (a pocket of its climb band with no way out for it).
		/// Its own pocket never counts: a caster already down there may still choose where to stand.</summary>
		public static bool IsCageFor(Pawn caster, IntVec3 c)
		{
			if (caster == null || !caster.Spawned || !RM_PocketGrid.Relative || !RM_SuperdeepTrap.RuleOn)
			{
				return false;
			}
			Map map = caster.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepShooting.EngineFor(map);
			if (eng == null || eng.ClimbCellCount == 0 || !c.InBounds(map) || eng.ClimbDepthAt(c) == 0
				|| Pits.RM_PitCoverUtility.IsCovered(map, c) || RM_PocketGrid.CanFly(caster) || !RM_SuperdeepTrap.Captures(caster))
			{
				return false;
			}
			int k = RM_PocketGrid.ClimbLimitOf(caster);
			RM_PocketGrid g = RM_PocketGrid.For(map);
			int comp = g.ComponentOf(k, c);
			if (comp < 0 || !g.ComponentIsPocket(k, comp) || g.ComponentOf(k, caster.Position) == comp)
			{
				return false;
			}
			return g.TrappedIn(k, comp, caster);
		}

		private static Pawn PawnById(Map map, string id)
		{
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				if (p.ThingID == id || p.thingIDNumber.ToString() == id)
				{
					return p;
				}
			}
			return null;
		}

		/// <summary>Bridge/proof read (jawa/static_call, northstar/trench_cover_proof.py): arg "targetId;shooterId".
		/// "TRENCH trench=t vanilla=v combined=c hit=h hitNoTrench=h0 cage=b target=x,z shooter=x,z", where hitNoTrench is
		/// the same report with trench cover switched off for the read (restored at once), or "REFUSED: ...".</summary>
		public static string ProofTrenchCover(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length != 2)
			{
				return "REFUSED: arg must be targetId;shooterId on the current map";
			}
			Pawn t = PawnById(map, a[0]), s = PawnById(map, a[1]);
			if (t == null || s == null)
			{
				return "REFUSED: no spawned pawn " + (t == null ? a[0] : a[1]);
			}
			Verb verb = s.TryGetAttackVerb(t, false);
			if (verb == null || verb.IsMeleeAttack)
			{
				return "REFUSED: shooter has no ranged verb";
			}
			float trench = BlockFor(t, s.Position, map);
			float vanilla = VanillaBlock(t, s.Position, map);
			float combined = CoverUtility.CalculateOverallBlockChance(t, s.Position, map);
			float hit = ShotReport.HitReportFor(s, verb, t).TotalEstimatedHitChance;
			bool was = RimMandrakeFlowWorksSettings.trenchCoverEnabled;
			float hit0;
			try
			{
				RimMandrakeFlowWorksSettings.trenchCoverEnabled = false;
				hit0 = ShotReport.HitReportFor(s, verb, t).TotalEstimatedHitChance;
			}
			finally
			{
				RimMandrakeFlowWorksSettings.trenchCoverEnabled = was;
			}
			return "TRENCH trench=" + trench.ToString("F3") + " vanilla=" + vanilla.ToString("F3") + " combined="
				+ combined.ToString("F3") + " hit=" + hit.ToString("F3") + " hitNoTrench=" + hit0.ToString("F3") + " cage="
				+ IsCageFor(t, t.Position) + " target=" + t.Position.x + "," + t.Position.z + " shooter=" + s.Position.x + ","
				+ s.Position.z;
		}
	}

	/// <summary>§10 step 2: trench cover joins vanilla cover for every reader (hit chance, AI cast squares, target choice,
	/// "stay and fire").</summary>
	[HarmonyPatch(typeof(CoverUtility), nameof(CoverUtility.CalculateOverallBlockChance))]
	[RimMandrake.Shared.PatchFeature("Trench cover", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "trenchCoverEnabled")]
	public static class RM_Patch_CoverUtility_CalculateOverallBlockChance
	{
		[HarmonyPostfix]
		public static void Postfix(LocalTargetInfo target, IntVec3 shooterLoc, Map map, ref float __result)
		{
			if (RM_TrenchCover.suppress || !RM_TrenchCover.On)
			{
				return;
			}
			float t = RM_TrenchCover.BlockFor(target, shooterLoc, map);
			if (t > 0f)
			{
				__result = RM_TrenchCoverMath.Combine(__result, t, RimMandrakeFlowWorksSettings.trenchCoverCap);
			}
		}
	}

	/// <summary>§10 step 3: vanilla's block back into the cover field, the trench share folded into the aim (so the
	/// projectile code never looks for a cover Thing that does not exist).</summary>
	[HarmonyPatch(typeof(ShotReport), nameof(ShotReport.HitReportFor))]
	[RimMandrake.Shared.PatchFeature("Trench cover", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "trenchCoverEnabled")]
	public static class RM_Patch_ShotReport_HitReportFor
	{
		internal static readonly AccessTools.StructFieldRef<ShotReport, float> Cover =
			AccessTools.StructFieldRefAccess<ShotReport, float>("coversOverallBlockChance");

		internal static readonly AccessTools.StructFieldRef<ShotReport, float> Gas =
			AccessTools.StructFieldRefAccess<ShotReport, float>("factorFromCoveringGas");

		[HarmonyPostfix]
		public static void Postfix(Thing caster, LocalTargetInfo target, ref ShotReport __result)
		{
			if (!RM_TrenchCover.On || caster == null || caster.Map == null)
			{
				return;
			}
			ref float cover = ref Cover(ref __result);
			float vanilla = RM_TrenchCover.VanillaBlock(target, caster.Position, caster.Map);
			if (!(cover > vanilla + 1e-6f))
			{
				return;
			}
			float f = RM_TrenchCoverMath.PassFactor(vanilla, cover);
			cover = vanilla;
			ref float gas = ref Gas(ref __result);
			gas *= f;
			RM_TrenchCover.lastFoldCell = target.Cell;
			RM_TrenchCover.lastFoldGas = gas;
			RM_TrenchCover.lastFoldFactor = f;
		}
	}

	/// <summary>The readout line: "Trench wall: blocks N%". The fold lives in the smoke factor, so for the text the smoke
	/// factor is put back to vanilla's while vanilla writes, and the total line is corrected afterwards.</summary>
	[HarmonyPatch(typeof(ShotReport), nameof(ShotReport.GetTextReadout))]
	[RimMandrake.Shared.PatchFeature("Trench cover", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "trenchCoverEnabled")]
	public static class RM_Patch_ShotReport_GetTextReadout
	{
		private static readonly AccessTools.StructFieldRef<ShotReport, TargetInfo> TargetField =
			AccessTools.StructFieldRefAccess<ShotReport, TargetInfo>("target");

		public struct State
		{
			public float factor;
			public string shownTotal;
			public string trueTotal;
		}

		[HarmonyPrefix]
		public static void Prefix(ref ShotReport __instance, out State __state)
		{
			__state = new State { factor = 1f };
			if (!RM_TrenchCover.On || RM_TrenchCover.lastFoldFactor <= 0f || RM_TrenchCover.lastFoldFactor >= 1f)
			{
				return;
			}
			ref float gas = ref RM_Patch_ShotReport_HitReportFor.Gas(ref __instance);
			if (TargetField(ref __instance).Cell != RM_TrenchCover.lastFoldCell || System.Math.Abs(gas - RM_TrenchCover.lastFoldGas) > 1e-6f)
			{
				return;
			}
			__state.factor = RM_TrenchCover.lastFoldFactor;
			__state.trueTotal = __instance.TotalEstimatedHitChance.ToStringPercent();
			gas /= __state.factor;
			__state.shownTotal = __instance.TotalEstimatedHitChance.ToStringPercent();
		}

		[HarmonyPostfix]
		public static void Postfix(ref ShotReport __instance, State __state, ref string __result)
		{
			if (__state.factor >= 1f || __result == null)
			{
				return;
			}
			RM_Patch_ShotReport_HitReportFor.Gas(ref __instance) *= __state.factor;
			if (__state.shownTotal != null && __result.StartsWith(__state.shownTotal))
			{
				__result = __state.trueTotal + __result.Substring(__state.shownTotal.Length);
			}
			string line = "   Trench wall: blocks " + (1f - __state.factor).ToStringPercent();
			string noCover = "   (" + "NoCoverLower".Translate() + ")";
			int at = __result.IndexOf(noCover, System.StringComparison.Ordinal);
			__result = at >= 0
				? __result.Substring(0, at) + line + __result.Substring(at + noCover.Length)
				: __result.TrimEnd() + "\n" + line + "\n";
		}
	}

	/// <summary>§10 step 5 (Q5): CastPositionFinder's request caster, held for the search (CastPositionPreference reads a
	/// private static <c>req</c>; one ThreadStatic set here beats a reflection read per candidate square).</summary>
	[HarmonyPatch(typeof(CastPositionFinder), nameof(CastPositionFinder.TryFindCastPosition))]
	[RimMandrake.Shared.PatchFeature("Trench cover AI", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "trenchCoverEnabled")]
	public static class RM_Patch_CastPositionFinder_TryFindCastPosition
	{
		[System.ThreadStatic] internal static Pawn searching;

		[HarmonyPrefix]
		public static void Prefix(CastPositionRequest newReq, out Pawn __state)
		{
			__state = searching;
			searching = newReq.caster;
		}

		[HarmonyFinalizer]
		public static void Finalizer(Pawn __state)
		{
			searching = __state;
		}
	}

	/// <summary>The occupant read for the candidate square, and the cage guard (Q5): a square in a pocket the caster could
	/// not climb out of scores 0 (CastPositionFinder keeps only scores over 0.001).</summary>
	[HarmonyPatch(typeof(CastPositionFinder), "CastPositionPreference")]
	[RimMandrake.Shared.PatchFeature("Trench cover AI", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "trenchCoverEnabled")]
	public static class RM_Patch_CastPositionFinder_CastPositionPreference
	{
		[HarmonyPrefix]
		public static void Prefix(out Pawn __state)
		{
			__state = RM_TrenchCover.castCandidateOccupant;
			RM_TrenchCover.castCandidateOccupant = RM_TrenchCover.On ? RM_Patch_CastPositionFinder_TryFindCastPosition.searching : null;
		}

		[HarmonyFinalizer]
		public static void Finalizer(IntVec3 c, Pawn __state, ref float __result)
		{
			Pawn caster = RM_TrenchCover.castCandidateOccupant;
			RM_TrenchCover.castCandidateOccupant = __state;
			if (__result > 0f && RM_TrenchCover.On && RimMandrakeFlowWorksSettings.trenchAiAvoidsCages
				&& RM_TrenchCover.IsCageFor(caster, c))
			{
				__result = 0f;
			}
		}
	}
}
