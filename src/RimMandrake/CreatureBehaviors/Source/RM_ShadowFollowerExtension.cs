using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_GLITTER_BIRDS_COMMENSALS_1. Attach to a commensal race's ThingDef
	/// to make RM_JobGiver_FollowShadowCaster steer its idle behavior toward
	/// the nearest spawned pawn carrying RM_Comp_ShadowCaster, instead of a
	/// species-specific host list — this is the "parameterized by host
	/// creature, not hardcoded" requirement: any future host just adds the
	/// comp, any future commensal just adds this extension, and neither side
	/// names the other. First consumer: the desert's glitter-bird, following
	/// RSW_ShadeWhale. Second intended consumer:
	/// DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1's eventual microfauna, following
	/// RM_MirrorGiant once that def also carries RM_CompProperties_ShadowCaster.
	/// </summary>
	public class RM_ShadowFollowerExtension : DefModExtension
	{
		/// <summary>Map-distance (cells) to search for the nearest shadow-caster.</summary>
		public float searchRadius = 40f;

		/// <summary>
		/// 0 (default) = use the found host's own RM_Comp_ShadowCaster.commensalFollowRadius.
		/// &gt;0 overrides it — for a commensal that wants to ride closer/further than the
		/// host's own default offers.
		/// </summary>
		public float followRadiusOverride = 0f;
	}
}
