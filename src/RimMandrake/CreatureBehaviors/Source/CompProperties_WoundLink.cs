using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// ROT_HEALTH_SHARING_1. Bare wiring for RM_CompWoundLink — every tunable
	/// value it needs (tag/radius/shareFraction/severityGate) lives on the
	/// race's own RM_WoundLinkExtension (see that file's header for why one
	/// extension serves both this comp and RM_HediffComp_KinMending), so this
	/// class carries no fields of its own. Kept as a real CompProperties
	/// subclass rather than bare `Verse.CompProperties` in XML purely for
	/// convention with every other ThingComp in this assembly
	/// (CompProperties_AquaticAmbusher, RM_CompProperties_VerminBreeder).
	/// </summary>
	public class CompProperties_WoundLink : CompProperties
	{
		public CompProperties_WoundLink()
		{
			compClass = typeof(RM_CompWoundLink);
		}
	}
}
