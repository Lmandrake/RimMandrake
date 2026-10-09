using HarmonyLib;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.Abyss
{
    // ABYSS_DARK_MUFFLE_ALL_SOUNDS_1: the Dark swallows EVERY map sound. Sample.Update runs per frame for every
    // live sample (one-shots and sustainers); its postfix low-passes the sample's own AudioSource from the same
    // Dark density SoundParamSource_RM_DarkMuffle feeds our own sounds (22 kHz clear -> 700 Hz full Dark).
    // Only samples placed on an Abyss map (Info.Maker.Map) are touched: on-camera UI sounds and every other map are
    // left alone. A sample whose def already maps the Dark itself is skipped. PROVISIONAL: cutoff range shared with
    // the gust sounds; judged with the owner present.
    [RimMandrake.Shared.PatchFeature("Patch_Sample_DarkMuffle", typeof(RM_AbyssSettings), "darkMuffleAllSounds")]
    [HarmonyPatch(typeof(Sample), nameof(Sample.Update))]
    public static class Patch_Sample_DarkMuffle
    {
        public const float ClearCutoff = 22000f, DarkCutoff = 700f;

        public static float CutoffFor(float dark)
        {
            return Mathf.Lerp(ClearCutoff, DarkCutoff, Mathf.Clamp01(dark));
        }

        public static void Postfix(Sample __instance)
        {
            if (!RM_AbyssSettings.darkMuffleAllSounds) return;
            AudioSource src = __instance.source;
            if (src == null) return;
            if (Current.ProgramState != ProgramState.Playing) return;
            Map map = __instance.Info.Maker.Map;
            if (map == null || map.Biome == null || map.Biome.defName != "RM_Abyss") return;
            var maps = __instance.subDef.paramMappings;
            for (int i = 0; i < maps.Count; i++)
                if (maps[i].inParam is SoundParamSource_RM_DarkMuffle) return;
            float dark = new SoundParamSource_RM_DarkMuffle().ValueFor(__instance);
            var f = src.GetComponent<AudioLowPassFilter>();
            if (f == null)
            {
                if (dark <= 0.001f) return;
                f = src.gameObject.AddComponent<AudioLowPassFilter>();
            }
            f.cutoffFrequency = CutoffFor(dark);
        }
    }
}
