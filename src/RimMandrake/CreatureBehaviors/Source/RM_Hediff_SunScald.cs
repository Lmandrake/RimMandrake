using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHOKK_RSW_MOD_1 / WEBWORK_MECHANICS_1 §4. Generic sun-exposure hediff:
	/// mirrors the shape of vanilla's Anomaly-gated Verse.Hediff_LightExposure
	/// (Noctol helplessness-in-light), but (a) carries no Anomaly dependency —
	/// any species on any map can hold it — and (b) is keyed to the SAME
	/// primitive the vanilla UV-sensitivity gene uses
	/// (RimWorld.SanguophageUtility.InSunlight: unroofed AND
	/// map.skyManager.CurSkyGlow &gt; 0.1), not to any light source. A wall
	/// lamp never substitutes for the sun; on a world with no night cycle
	/// (Ash'karr's tidally-locked dayside) only weather ever turns this off;
	/// on an ordinary planet CurSkyGlow already falls at night with no
	/// special-casing needed here — the primitive generalizes for free
	/// (owner canon note, 2026-09-11).
	///
	/// Severity climbs while exposed and decays in shade or under roof; a
	/// content mod's HediffDef supplies the stages/capMods that turn rising
	/// severity into gameplay (SHOKK_RSW_MOD_1 caps it at a cripple —
	/// postFactor only, never a capacity floor of zero — per the owner's
	/// "cripple, never down" ruling; this class itself makes no such
	/// guarantee and a future consumer's stages are its own responsibility).
	/// </summary>
	public class RM_Hediff_SunScald : Hediff
	{
		private const float SeverityPerSecond_Exposed = 0.6f;

		private const float SeverityPerSecond_Shaded = -0.3f;

		public override bool ShouldRemove => false;

		public override void TickInterval(int delta)
		{
			base.TickInterval(delta);
			if (!RM_CreatureBehaviorsSettings.sunScaldEnabled)
			{
				return; // mod option: sun-scald buildup disabled — severity frozen in place
			}
			if (!pawn.SpawnedOrAnyParentSpawned || pawn.Dead || !pawn.IsHashIntervalTick(60, delta))
			{
				return;
			}
			float mult = Mathf.Max(0f, RM_CreatureBehaviorsSettings.sunScaldSeverityMultiplier);
			// WEBWORK_HEAT_SHADE_BUILD_1: vanilla InSunlight ignores trees, so on a dayside biome with no night
			// the scald hit every unroofed cell of its own jungle. Re-key to the shade grid when it runs here
			// and the setting is on; otherwise exactly the old behaviour.
			bool inSun = pawn.PositionHeld.InSunlight(pawn.MapHeld);
			RM_MapComponent_ShadeGrid grid = pawn.MapHeld?.GetComponent<RM_MapComponent_ShadeGrid>();
			bool gridUsable = grid != null && grid.SunHeatActive;
			bool exposed = RM_SunHeatMath.ScaldExposed(RM_CreatureBehaviorsSettings.sunScaldReadsShade, gridUsable,
				gridUsable ? grid.ShadeAt(pawn.PositionHeld) : 0f,
				RM_CreatureBehaviorsSettings.sunScaldShadeThreshold, inSun);
			Severity += (exposed ? SeverityPerSecond_Exposed : SeverityPerSecond_Shaded) * mult;
		}
	}
}
