using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	/// <summary>
	/// §5's combat-inverting hazard, the design doc's own "riskiest single piece
	/// of C# in either document": "a careful, isolated check at the top of the
	/// ranged-fire-resolution path (not a scattered patch)." One postfix, one
	/// method, gated by the tracker's own table and a settings toggle/intensity
	/// slider so a bad interaction can be dialed down without a mod update.
	///
	/// Melee never calls Verb_LaunchProjectile at all, so it is untouched by
	/// construction — matching §5's "melee... stays safe" without any extra
	/// exclusion logic.
	/// </summary>
	[HarmonyPatch(typeof(Verb_LaunchProjectile), "TryCastShot")]
	public static class Patch_GasSaturationDeflagration
	{
		public static void Postfix(Verb_LaunchProjectile __instance, bool __result)
		{
			if (!__result)
			{
				return;
			}
			if (PropaneLakeMechanicsMod.Settings != null && !PropaneLakeMechanicsMod.Settings.saturationDeflagrationEnabled)
			{
				return;
			}
			Thing caster = __instance.caster;
			if (caster?.Map == null)
			{
				return;
			}
			MapComponent_GasSaturationTracker tracker = caster.Map.GetComponent<MapComponent_GasSaturationTracker>();
			if (tracker == null)
			{
				return;
			}
			float chance = tracker.DeflagrationChanceAt(caster.Position, out bool flashoverTier);
			if (chance <= 0f || !Rand.Chance(chance))
			{
				return;
			}
			if (flashoverTier)
			{
				tracker.TriggerFlashover(caster.Position, caster);
			}
			else
			{
				GenExplosion.DoExplosion(caster.Position, caster.Map, 1.2f, DamageDefOf.Flame, caster, chanceToStartFire: 1f, doSoundEffects: true);
				Messages.Message("RUT_Message_Deflagration".Translate(), new TargetInfo(caster.Position, caster.Map), MessageTypeDefOf.NegativeEvent);
			}
		}
	}
}
