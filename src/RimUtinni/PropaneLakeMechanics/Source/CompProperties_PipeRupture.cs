using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	public class CompProperties_PipeRupture : CompProperties
	{
		/// <summary>Chance to rupture per Flame-damage hit (a fire touching the
		/// pipe — the "scripted beat" §4 names is anything else calling
		/// TriggerRupture directly, e.g. a raid-breach or sabotage incident).</summary>
		public float ruptureChanceOnFlameHit = 0.6f;

		/// <summary>Chance to rupture per explosive (Bomb) hit.</summary>
		public float ruptureChanceOnBombHit = 0.35f;

		/// <summary>How often (ticks), while ruptured and pressurized, the jet
		/// refreshes its fire and feeds local saturation.</summary>
		public int jetIntervalTicks = 120;

		public float jetLocalSaturation = 14f;

		public float jetSaturationRadius = 4f;

		/// <summary>Ticks a rupture may run unresolved on a faction-owned map
		/// before it costs goodwill ("huge negative faction relationship").</summary>
		public int goodwillPenaltyDelayTicks = 30000; // half a day

		public int goodwillPenalty = -35;

		public CompProperties_PipeRupture()
		{
			compClass = typeof(CompPipeRupture);
		}
	}
}
