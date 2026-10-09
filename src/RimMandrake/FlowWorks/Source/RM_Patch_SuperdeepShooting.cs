using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	// ════════════════════════════════════════════════════════════════════
	// RULING 23 — THE ONE SHOOTING EXCEPTION, AND THE ONLY HARMONY IN THIS MOD.
	//
	// Owner, verbatim: "someone in a pit should really only be able to shoot at
	// others at the edges above them, and those outside should only be able to
	// shoot into the pit from the edge as well. But that's the only mechanic."
	//
	// 🔴 IT IS A RESTRICTION, NEVER A BONUS. Nothing here touches hit chance,
	// cover, accuracy, sight range or projectile arcs. That is the whole reason
	// LAW 2 survives: a restriction is one boolean gate on a check that already
	// exists; a bonus would drag in an elevation model.
	//
	// SUPERDEEP ONLY, and "at the edge" means 8-WAY ADJACENCY TO THE PAWN'S OWN
	// CELL — not adjacency to the excavated region, which would need a flood
	// fill per shot. The check below is two grid reads and an abs-compare.
	// ════════════════════════════════════════════════════════════════════

	/// <summary>Harmony bootstrap for every [HarmonyPatch] class in this assembly, through the shared per-class applier
	/// (src/RimMandrake/_Shared/HarmonyResilience/PatchApplier.cs).</summary>
	[StaticConstructorOnStartup]
	public static class RM_FlowWorksHarmony
	{
		static RM_FlowWorksHarmony()
		{
			// HARMONY_PATCH_RESILIENCE_1: one class at a time, so a game update that breaks one patch switches off
			// that feature (its [PatchFeature] setting) instead of every patch after it. Logs "patched N, missing X".
			RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.flowworks"), typeof(RM_FlowWorksHarmony).Assembly,
				"RimMandrake.FlowWorks");
		}
	}

	/// <summary>The O(1) pair test both patches share.</summary>
	public static class RM_SuperdeepShooting
	{
		private static Map cachedMap;

		private static RM_MapComponent_Excavation cachedEngine;

		/// <summary>One-entry map cache. <c>Map.GetComponent&lt;T&gt;</c> walks the
		/// component list, and <c>CanHitTargetFrom</c> is called constantly — a
		/// list walk per shot-legality check is exactly the framerate defect
		/// ruling 23 warns about.</summary>
		public static RM_MapComponent_Excavation EngineFor(Map map)
		{
			if (map == null)
			{
				return null;
			}
			if (!ReferenceEquals(map, cachedMap))
			{
				cachedMap = map;
				cachedEngine = map.GetComponent<RM_MapComponent_Excavation>();
			}
			return cachedEngine;
		}

		/// <summary>
		/// TRUE when this shooter cell / target cell pair may exchange fire.
		///
		/// 🔴 Deliberately <see cref="RM_MapComponent_Excavation.IsSuperdeepExcavation"/>
		/// and NOT <c>DepthAt</c>. DepthAt is the read-through adapter: natural
		/// liquid terrain reads through it as SUPERDEEP, so using it here would
		/// forbid every shot across every lake, river and ocean on the map. The
		/// ruling is about a dug hole, and only the depth grid knows about those.
		/// </summary>
		public static bool PairAllowed(Map map, IntVec3 shooter, IntVec3 target)
		{
			RM_MapComponent_Excavation engine = EngineFor(map);
			// The overwhelmingly common case on every map ever played: nothing
			// has been dug to SUPERDEEP, so the whole rule costs one int compare.
			if (engine == null || engine.SuperdeepCellCount == 0)
			{
				return true;
			}
			// PIT_COVER_FALL_REWIRE_1: a covered superdeep cell is ground until the cover gives way.
			bool shooterDeep = engine.IsSuperdeepExcavation(shooter) && !Pits.RM_PitCoverUtility.IsCovered(map, shooter);
			bool targetDeep = engine.IsSuperdeepExcavation(target) && !Pits.RM_PitCoverUtility.IsCovered(map, target);
			if (!shooterDeep && !targetDeep)
			{
				return true;
			}
			int dx = shooter.x - target.x;
			if (dx < 0)
			{
				dx = -dx;
			}
			int dz = shooter.z - target.z;
			if (dz < 0)
			{
				dz = -dz;
			}
			return dx <= 1 && dz <= 1;
		}

		/// <summary>Shared guard: the rule applies to RANGED verbs only. A melee
		/// verb already requires adjacency, so gating it would change nothing and
		/// could only ever introduce a bug.</summary>
		public static bool RuleAppliesTo(Verb verb)
		{
			return RimMandrakeFlowWorksSettings.superdeepShootingRuleEnabled
				&& verb != null && verb.verbProps != null && !verb.IsMeleeAttack;
		}
	}

	/// <summary>Phase 0's MEASURED patch point:
	/// <c>public virtual bool Verb.CanHitTargetFrom(IntVec3 root, LocalTargetInfo targ)</c>,
	/// Verse/Verb.cs:710.</summary>
	[HarmonyPatch(typeof(Verb), nameof(Verb.CanHitTargetFrom))]
	[RimMandrake.Shared.PatchFeature("Superdeep shooting rule", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepShootingRuleEnabled")]
	public static class RM_Patch_Verb_CanHitTargetFrom
	{
		[HarmonyPrefix]
		public static bool Prefix(Verb __instance, IntVec3 root, LocalTargetInfo targ, ref bool __result)
		{
			if (!RM_SuperdeepShooting.RuleAppliesTo(__instance))
			{
				return true;
			}
			Thing caster = __instance.caster;
			if (caster == null || !targ.IsValid)
			{
				return true;
			}
			Map map = caster.Map;
			if (map == null)
			{
				return true;
			}
			// `root` and not caster.Position on purpose: CastPositionFinder asks
			// this about CANDIDATE cells, so the rule has to judge the cell the
			// shot would come FROM. That is also what makes a raider walk to the
			// lip instead of standing off and failing — the lip is a legal root.
			if (RM_SuperdeepShooting.PairAllowed(map, root, targ.Cell))
			{
				return true;
			}
			__result = false;
			return false;
		}
	}

	/// <summary>
	/// The AI-selection half, which ruling 23 calls out as the difference
	/// between a mechanic and "broken pathing".
	///
	/// MEASURED before patching (RimSage, 2026-09-16):
	///   Verse/AI/AttackTargetFinder.cs:367 — <c>private static bool
	///   CanShootAtFromCurrentPosition(IAttackTarget, IAttackTargetSearcher, Verb)</c>
	///   is nothing but <c>verb?.CanHitTargetFrom(searcher.Thing.Position,
	///   target.Thing) ?? false</c>. It is the ranged gate at :191 and :207, and
	///   it is also what the debug overlay at :666 draws. So the prefix above
	///   ALREADY removes a SUPERDEEP occupant from the ranged candidate walk —
	///   that half needed no second patch, which is worth knowing rather than
	///   patching twice.
	///
	///   What it does NOT cover is the fallback at :207, reached when nothing is
	///   shootable from where the searcher stands. There `innerValidator` alone
	///   decides, and it never consults the verb — so BestAttackTarget can still
	///   hand back a SUPERDEEP occupant as "closest enemy, go to it". That is the
	///   fixation ruling 23 predicts, and this postfix is the one place to close
	///   it: <c>public static IAttackTarget BestAttackTarget(...)</c> at
	///   AttackTargetFinder.cs:32, which BestShootTargetFromCurrentPosition
	///   (:583) delegates into, so both entry points are covered by one patch.
	///
	/// RANGED SEARCHERS ONLY. A melee searcher keeps the target and walks to the
	/// lip, where it can fight — denying it would be a change to melee, which
	/// ruling 23 does not authorise.
	/// </summary>
	[HarmonyPatch(typeof(AttackTargetFinder), nameof(AttackTargetFinder.BestAttackTarget))]
	[RimMandrake.Shared.PatchFeature("Superdeep shooting rule", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepShootingRuleEnabled")]
	public static class RM_Patch_AttackTargetFinder_BestAttackTarget
	{
		/// <summary>SUPERDEEP_TARGET_VALIDATOR_1: the rule rides the finder's own `validator`, so a forbidden
		/// candidate is skipped and the finder moves on to its next one. A post-selection null (the postfix
		/// below, kept only as a safety net for a caller that bypasses the validator) leaves the searcher
		/// with no target at all even when an allowed one stood next in line.</summary>
		[HarmonyPrefix]
		public static void Prefix(IAttackTargetSearcher searcher, ref System.Predicate<Thing> validator)
		{
			if (searcher == null || !RM_SuperdeepShooting.RuleAppliesTo(searcher.CurrentEffectiveVerb))
			{
				return;
			}
			Thing searcherThing = searcher.Thing;
			if (searcherThing == null || searcherThing.Map == null)
			{
				return;
			}
			Map map = searcherThing.Map;
			IntVec3 from = searcherThing.Position;
			System.Predicate<Thing> inner = validator;
			validator = t => (inner == null || inner(t))
				&& (t == null || RM_SuperdeepShooting.PairAllowed(map, from, t.Position));
		}

		[HarmonyPostfix]
		public static void Postfix(IAttackTargetSearcher searcher, ref IAttackTarget __result)
		{
			if (__result == null || searcher == null)
			{
				return;
			}
			if (!RM_SuperdeepShooting.RuleAppliesTo(searcher.CurrentEffectiveVerb))
			{
				return;
			}
			Thing searcherThing = searcher.Thing;
			Thing targetThing = __result.Thing;
			if (searcherThing == null || targetThing == null || searcherThing.Map == null)
			{
				return;
			}
			if (RM_SuperdeepShooting.PairAllowed(searcherThing.Map, searcherThing.Position, targetThing.Position))
			{
				return;
			}
			__result = null;
		}
	}
}
