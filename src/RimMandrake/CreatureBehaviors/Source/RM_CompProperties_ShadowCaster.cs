using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_GLITTER_BIRDS_COMMENSALS_1. The "tracked shadow-caster component"
	/// half of the shade-follow mechanism this item's own text names as one of
	/// two valid routes (the other being ShadeAt+proximity heuristic, rejected —
	/// see RM_JobGiver_FollowShadowCaster's header for why). Attach to ANY host
	/// race's &lt;comps&gt; to make it a legitimate target for
	/// RM_ShadowFollowerExtension-tagged commensals — RSW_ShadeWhale is the
	/// first consumer, DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1's eventual host
	/// (RM_MirrorGiant) is meant to be the second, by adding this same comp to
	/// its own def with its own tuned radius. Nothing here names a species.
	/// </summary>
	public class RM_CompProperties_ShadowCaster : CompProperties
	{
		/// <summary>
		/// How close (cells) a commensal must stay to count as "riding this
		/// host's shadow" — read by RM_JobGiver_FollowShadowCaster as the
		/// JobDriver_FollowClose follow radius when no follower-side override
		/// is set. A bigger host offers a bigger shadow; tune per host.
		/// </summary>
		public float commensalFollowRadius = 3f;

		public RM_CompProperties_ShadowCaster()
		{
			compClass = typeof(RM_Comp_ShadowCaster);
		}
	}
}
