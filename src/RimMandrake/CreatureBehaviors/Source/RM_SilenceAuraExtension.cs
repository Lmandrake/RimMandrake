using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1. Attach to a predator race ThingDef to make
	/// RM_MapComponent_SilenceCue hush the map's ambient sustainers while it is
	/// hunting near the player's home area — the Greentide kit's "silence cue"
	/// (owner ruling 2026-09-11: ships in v1, not deferred to v1.1). Generic:
	/// nothing here names a biome, so any predator-heavy content mod can wire
	/// the same cue onto its own apex creature.
	/// </summary>
	public class RM_SilenceAuraExtension : DefModExtension
	{
		/// <summary>Trigger range from any free colonist (RM_MapComponent_SilenceCue.NearAnyColonist) for a carrying pawn's hunt job to start the hush.</summary>
		public float triggerRadius = 20f;

		/// <summary>How long the hush lasts once triggered, in ticks, before ambience is restored.</summary>
		public int hushDurationTicks = 900;
	}
}
