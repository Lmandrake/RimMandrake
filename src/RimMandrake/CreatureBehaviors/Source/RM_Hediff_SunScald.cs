using RimWorld;
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
			if (!pawn.SpawnedOrAnyParentSpawned || pawn.Dead || !pawn.IsHashIntervalTick(60, delta))
			{
				return;
			}
			bool exposed = pawn.PositionHeld.InSunlight(pawn.MapHeld);
			Severity += exposed ? SeverityPerSecond_Exposed : SeverityPerSecond_Shaded;
		}
	}
}
