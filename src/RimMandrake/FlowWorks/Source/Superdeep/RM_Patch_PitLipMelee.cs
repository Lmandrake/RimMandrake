using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS: no melee across the lip of a pit room
	/// (RM_PitRooms.MeleeAcrossLipDenied). Pawn_MeleeVerbs.TryMeleeAttack is the one door every hand attack goes through:
	/// the AttackMelee job, vanilla Wait's auto-attack on the 8 squares around a pawn, and a drafted colonist's order.</summary>
	[HarmonyPatch(typeof(Pawn_MeleeVerbs), nameof(Pawn_MeleeVerbs.TryMeleeAttack))]
	[RimMandrake.Shared.PatchFeature("No melee across a pit's edge", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitLipMeleeDeniedEnabled")]
	public static class RM_Patch_MeleeVerbs_PitLip
	{
		[HarmonyPrefix]
		public static bool Prefix(Pawn_MeleeVerbs __instance, Thing target, ref bool __result)
		{
			if (!RimMandrakeFlowWorksSettings.pitLipMeleeDeniedEnabled || target == null)
			{
				return true;
			}
			if (RM_PitRooms.MeleeAcrossLipDenied(__instance.Pawn, target))
			{
				__result = false;
				return false;
			}
			return true;
		}
	}

	/// <summary>The AI half: a melee searcher does not pick a target it cannot strike across the lip, so a held raider does
	/// not walk the pit floor to stand under a colonist it can never hit, and a colonist is not sent to punch down a pit.</summary>
	[HarmonyPatch(typeof(AttackTargetFinder), nameof(AttackTargetFinder.BestAttackTarget))]
	[RimMandrake.Shared.PatchFeature("No melee across a pit's edge", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitLipMeleeDeniedEnabled")]
	public static class RM_Patch_AttackTargetFinder_PitLipMelee
	{
		[HarmonyPrefix]
		public static void Prefix(IAttackTargetSearcher searcher, ref System.Predicate<Thing> validator)
		{
			if (!RimMandrakeFlowWorksSettings.pitLipMeleeDeniedEnabled || searcher == null)
			{
				return;
			}
			Pawn p = searcher.Thing as Pawn;
			Verb verb = searcher.CurrentEffectiveVerb;
			if (p == null || !p.Spawned || verb == null || !verb.IsMeleeAttack)
			{
				return;
			}
			System.Predicate<Thing> inner = validator;
			validator = t => (inner == null || inner(t)) && (t == null || !RM_PitRooms.MeleeAcrossLipDenied(p, t));
		}
	}
}
