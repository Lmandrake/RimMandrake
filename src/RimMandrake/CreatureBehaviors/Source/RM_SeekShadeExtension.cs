using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1. Attach to a race ThingDef to make
	/// RM_JobGiver_SeekShade draw it under a roof once ambient temperature at
	/// its position crosses tempThreshold — the Greentide kit's "seek-shade AI"
	/// (owner ruling 2026-09-11: ships in v1, not deferred), written generic so
	/// any hot biome's fauna can opt in the same way RM_SeekTargetExtension
	/// already lets any race seek tagged terrain.
	/// </summary>
	public class RM_SeekShadeExtension : DefModExtension
	{
		/// <summary>Ambient temperature (deg C) at/above which the pawn starts seeking a roofed cell.</summary>
		public float tempThreshold = 40f;

		public float searchRadius = 30f;

		/// <summary>0..1 chance per check that the pawn bothers to seek at all.</summary>
		public float seekChancePerCheck = 0.3f;
	}
}
