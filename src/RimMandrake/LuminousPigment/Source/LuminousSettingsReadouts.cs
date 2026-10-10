using System;
using System.Collections.Generic;
using System.Reflection;
using System.Text;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    /// <summary>LUMINOUS_PIGMENT_SETTINGS_READOUTS_1. Read-only readouts for the settings screen, built from the existing
    /// kernel (RM_DeepfireCuisine.SteerChance / WeightedRandom weights) and the live settings. Per-group reset lives in
    /// LuminousPigmentSettings (SettingsKit). No number here is new: odds come from the same functions the dish roll uses.</summary>
    public static class RM_LuminousSettingsReadouts
    {
        public static readonly int[] ShownCookSkills = { 6, 12, 20 };

        public static float MatLifeHours(float lifeDays)
        {
            return lifeDays * 24f;
        }

        /// <summary>"Steered dish: chance to hit the intended family at cook skill 6 / 12 / 20: 0% / 60% / 100%".</summary>
        public static string SteerOddsLine(string what, int minSkill)
        {
            StringBuilder sb = new StringBuilder(what + ", steer chance at cook skill ");
            for (int i = 0; i < ShownCookSkills.Length; i++)
            {
                sb.Append(i > 0 ? " / " : "").Append(ShownCookSkills[i]);
            }
            sb.Append(": ");
            for (int i = 0; i < ShownCookSkills.Length; i++)
            {
                sb.Append(i > 0 ? " / " : "").Append(Mathf.RoundToInt(RM_DeepfireCuisine.SteerChance(minSkill, ShownCookSkills[i]) * 100f)).Append('%');
            }
            return sb.ToString();
        }

        /// <summary>Plain-dish odds per enabled family, from the same weights the roll uses.</summary>
        public static string PlainOddsLine(bool[] enabled)
        {
            float total = 0f;
            for (int i = 0; i < DeepfireFamilies.All.Count; i++)
            {
                if (RM_DeepfireCuisine.Enabled(enabled, i) && DeepfireFamilies.All[i].key != DeepfireFamilies.VermilionKey && DeepfireFamilies.All[i].baseWeight > 0f)
                {
                    total += DeepfireFamilies.All[i].baseWeight;
                }
            }
            if (total <= 0f)
            {
                return "Plain dish odds: no family is enabled, so a plain dish glows nothing.";
            }
            StringBuilder sb = new StringBuilder("Plain dish odds: ");
            bool first = true;
            for (int i = 0; i < DeepfireFamilies.All.Count; i++)
            {
                DeepfireFamily fam = DeepfireFamilies.All[i];
                if (!RM_DeepfireCuisine.Enabled(enabled, i) || fam.key == DeepfireFamilies.VermilionKey || fam.baseWeight <= 0f)
                {
                    continue;
                }
                sb.Append(first ? "" : ", ").Append(fam.key).Append(' ').Append(Mathf.RoundToInt(fam.baseWeight / total * 100f)).Append('%');
                first = false;
            }
            return sb.ToString();
        }
    }
}
