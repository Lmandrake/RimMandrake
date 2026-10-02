using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// STILLSAND_DUNE_GALE_1 §3, §6 — what a weather does to the senses this mod reads.
    /// Attach to a WeatherDef. A weather without it changes nothing.
    ///
    ///   sunExposureFactor   multiplies a pawn's sun exposure (RM_MapComponent_ShadeGrid.ExposureFor),
    ///                       so a dim sky takes the sun off (heat, glare). 1 = no change.
    ///   swimmerSenseChance  the chance, per evaluation, that a submerged sand swimmer still senses
    ///                       its target. Swimmers appraise by vibration and a storm is all vibration,
    ///                       so below 1 they stay down and strike less. 1 = no change.
    ///   drownsRumble        the swimmers' rumble layer is silent under this weather's roar.
    /// </summary>
    public class RM_WeatherSenseExtension : DefModExtension
    {
        public float sunExposureFactor = 1f;
        public float swimmerSenseChance = 1f;
        public bool drownsRumble;

        /// <summary>The extension on the weather this map is showing now, or null.</summary>
        public static RM_WeatherSenseExtension On(Map map)
        {
            WeatherDef w = map?.weatherManager?.curWeather;
            return w?.GetModExtension<RM_WeatherSenseExtension>();
        }

        public static float SunFactor(Map map)
        {
            RM_WeatherSenseExtension ext = On(map);
            return ext == null ? 1f : UnityEngine.Mathf.Clamp01(ext.sunExposureFactor);
        }
    }
}
