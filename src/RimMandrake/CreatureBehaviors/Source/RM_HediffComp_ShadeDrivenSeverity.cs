using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_SHADE_GRID_KEYSTONE_1. desert_ecology_feasibility.md §5: real
	/// per-cell outdoor temperature is structurally impossible (§2 — the whole
	/// open map is one Room reading one float), so "cools off faster in shade"
	/// cannot be built on pawn.AmbientTemperature the way vanilla's own
	/// HediffComp_SeverityPerDay/HediffGiver_Heat are. This is that route: the
	/// per-day severity rate is driven by RM_MapComponent_ShadeGrid.ShadeAt at
	/// the pawn's own position instead of a constant, linearly interpolated
	/// between "in full sun" and "in full shade". Subclasses vanilla's own
	/// HediffComp_SeverityModifierBase for the tick cadence and day-rate-to-
	/// per-tick math — identical plumbing to HediffComp_SeverityPerDay, only
	/// the rate varies.
	///
	/// This is the stub consumer named in DESERT_SHADE_GRID_KEYSTONE_1's
	/// ## verify — proof ShadeAt has a real reader beyond the wander JobGiver.
	/// The def this rides (RM_HeatDrivenBurst, GhoulFrenzy-pattern: burst
	/// MoveSpeed/MeleeCooldownFactor stage at high severity, a slowed
	/// heat-fatigue stage below it) supplies only the decay-in-shade half of
	/// "burst, then retreat to cool down" — the trigger (a burst-attack
	/// JobDriver calling pawn.health.AddHediff at job start, the same one-line
	/// idiom GhoulFrenzy itself uses as an AbilityDef effect) belongs to
	/// DESERT_BURST_PREDATOR_FLAGSHIP_1, not built here.
	/// </summary>
	public class RM_HediffComp_ShadeDrivenSeverity : HediffComp_SeverityModifierBase
	{
		private RM_HediffCompProperties_ShadeDrivenSeverity Props => (RM_HediffCompProperties_ShadeDrivenSeverity)props;

		public override float SeverityChangePerDay()
		{
			if (!RM_CreatureBehaviorsSettings.shadeGridEnabled || !RM_CreatureBehaviorsSettings.heatDrivenBurstEnabled)
			{
				return 0f; // mod option: frozen in place, neither climbing nor decaying
			}
			Pawn pawn = base.Pawn;
			if (!pawn.SpawnedOrAnyParentSpawned || pawn.MapHeld == null)
			{
				return 0f;
			}
			RM_MapComponent_ShadeGrid grid = pawn.MapHeld.GetComponent<RM_MapComponent_ShadeGrid>();
			float shade = (grid != null) ? grid.ShadeAt(pawn.PositionHeld) : 0f;
			float perDay = Mathf.Lerp(Props.severityPerDayInSun, Props.severityPerDayInShade, shade);
			return perDay * Mathf.Max(0f, RM_CreatureBehaviorsSettings.heatDrivenBurstDecayMultiplier);
		}
	}
}
