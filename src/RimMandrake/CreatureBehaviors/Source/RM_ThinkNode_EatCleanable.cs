using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// RUST_CATHEDRAL_MECHANICS_1 §6. Generic "forage a cleanable target"
	/// JobGiver, inserted globally the same way as RM_JobGiver_GnawTargets
	/// (see that class's header and RM_ThinkTree_VerminBehaviors.xml) — a
	/// no-op for any pawn whose race lacks RM_EatCleanableExtension. Named
	/// ThinkNode_ (not JobGiver_) to mirror the donor mechanism this
	/// generalizes, per RUST_CATHEDRAL_MECHANICS_1's kit spec §6.
	/// </summary>
	public class RM_ThinkNode_EatCleanable : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			if (!RM_CreatureBehaviorsSettings.eatCleanableBehaviorEnabled)
			{
				return null; // mod option: foraging/eating cleanable items disabled
			}
			RM_EatCleanableExtension ext = pawn.def?.GetModExtension<RM_EatCleanableExtension>();
			if (ext == null || pawn.Map == null)
			{
				return null;
			}
			if (!Rand.Chance(ext.seekChance))
			{
				return null;
			}

			Thing target = FindNamedCleanable(pawn, ext) ?? FindFilth(pawn, ext);
			if (target == null)
			{
				return null;
			}
			return JobMaker.MakeJob(RM_JobDefOf.RM_EatCleanable, target);
		}

		private static Thing FindNamedCleanable(Pawn pawn, RM_EatCleanableExtension ext)
		{
			if (ext.cleanableThingDefNames.NullOrEmpty())
			{
				return null;
			}
			return GenClosest.ClosestThingReachable(pawn.Position, pawn.Map, ThingRequest.ForGroup(ThingRequestGroup.HaulableEver),
				PathEndMode.Touch, TraverseParms.For(pawn), ext.searchRadius,
				(Thing t) => ext.cleanableThingDefNames.Contains(t.def.defName) && !t.IsForbidden(pawn));
		}

		private static Thing FindFilth(Pawn pawn, RM_EatCleanableExtension ext)
		{
			if (!ext.eatsFilth)
			{
				return null;
			}
			return GenClosest.ClosestThingReachable(pawn.Position, pawn.Map, ThingRequest.ForGroup(ThingRequestGroup.Filth),
				PathEndMode.Touch, TraverseParms.For(pawn), ext.searchRadius,
				(Thing t) => !t.IsForbidden(pawn));
		}
	}
}
