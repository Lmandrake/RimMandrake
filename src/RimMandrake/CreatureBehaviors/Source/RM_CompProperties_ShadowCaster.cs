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

		/// <summary>
		/// LONGSHADE_GPT_ENRICHMENT_1 §2 ("the gloomcast moves shade"). When
		/// above 0 the host's body is a real MOVING shade caster in
		/// RM_MapComponent_ShadeGrid: its footprint and its shadow along the
		/// sun count as shade for ShadeAt and for sun exposure, so every
		/// shade-reading creature (seek-shade, shade-seeking wander, the sun
		/// heat) finds it, not only tagged commensals. Height is on the
		/// staticSunShadowHeight scale (a rock or wall is 1.0). 0 (default) =
		/// a follow-only host, exactly as before.
		/// </summary>
		public float castShadeHeight = 0f;

		/// <summary>Half-width in cells of the shaded body footprint round
		/// the host's cell (0 = its one cell). Only read when
		/// castShadeHeight &gt; 0.</summary>
		public int castShadeRadius = 0;

		/// <summary>Depth (0..1) of the body's shade. Only read when
		/// castShadeHeight &gt; 0.</summary>
		public float castShadeDepth = 1f;

		public RM_CompProperties_ShadowCaster()
		{
			compClass = typeof(RM_Comp_ShadowCaster);
		}
	}
}
