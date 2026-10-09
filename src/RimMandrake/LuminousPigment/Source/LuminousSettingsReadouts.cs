using System;
using System.Collections.Generic;
using System.Reflection;
using System.Text;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    /// <summary>LUMINOUS_PIGMENT_SETTINGS_READOUTS_1. Read-only readouts for the settings screen, built from the existing
    /// kernel (RM_DeepfireCuisine.SteerChance / WeightedRandom weights) and the live settings, plus a "reset this section"
    /// button per heading. No number here is new: odds come from the same functions the dish roll uses.</summary>
    public static class RM_LuminousSettingsReadouts
    {
        public static readonly int[] ShownCookSkills = { 6, 12, 20 };

        private static readonly Dictionary<string, object> defaults = new Dictionary<string, object>();

        // Field names per settings heading; a field not listed belongs to no resettable section.
        public static readonly Dictionary<string, string[]> Sections = new Dictionary<string, string[]>
        {
            { "Chain", new[] { "shoreMatsEnabled", "matDiscoveryByEyeOrHand", "shoreMatChance", "matLifeDays", "matChillKillTemp" } },
            { "Press", new[] { "pressGate", "pressResearchCost", "pressYield", "pressWorkAmount", "pressPower" } },
            { "Deepfire", new[] { "deepfireMarketValue", "deepfireStackGlows", "deepfireNightVisibility", "deepfireVisibilityPerLight" } },
            { "GlowTank", new[] { "glowTankEnabled", "tankGrowDays", "tankYield", "tankPower", "tankPowerGraceHours", "tankNeedsWater", "tankWaterUnitsPerDay" } },
            { "Painting", new[] { "paintingEnabled", "maxCoats", "coatRadius", "coatIntensity", "glowMinValue", "costWallCell", "costFloorCell",
                "costFurnitureBase", "costFurniturePerExtraCell", "costFurnitureCap", "costArt", "costApparel", "costWeapon", "clusterBlock",
                "floorsPaintable", "wallsPaintable", "furniturePaintable", "apparelPaintable", "weaponsPaintable", "wornLightEnabled",
                "stylingStationLacquer", "wornLightTickInterval", "glowTargetFactor", "glowDodgePenalty", "combatPenaltiesEnabled",
                "artQualityBump", "beautyFlat", "beautyPct", "beautySizeCap", "floorBeautyPerCell", "floorRoomBonusPer10", "floorRoomBonusCap" } },
            { "Cuisine", new[] { "cuisineEnabled", "steerMinSkill", "vermilionMinSkill", "maxFamiliesPerPawn", "hediffGlowEnabled", "hediffGlowFollowsPawn", "hediffGlowInCombat", "familyEnabled" } },
            { "Gods", new[] { "godsReact", "godDeltaLike", "godDeltaAdore", "godDeltaIshko", "godDeltaStatue", "godDeltaDiminishAfter", "ishkoIdolPaintable" } },
            { "Status", new[] { "statusEnabled", "displayCap", "offenceThreshold", "moodScale", "opinionAboveStation", "goodwillPerImpressedVisit" } },
        };

        public static void CaptureDefaults(Type settingsType)
        {
            foreach (KeyValuePair<string, string[]> kv in Sections)
            {
                for (int i = 0; i < kv.Value.Length; i++)
                {
                    FieldInfo f = settingsType.GetField(kv.Value[i], BindingFlags.Public | BindingFlags.Static);
                    if (f != null)
                    {
                        defaults[kv.Value[i]] = Copy(f.GetValue(null));
                    }
                }
            }
        }

        private static object Copy(object v)
        {
            return v is Array a ? a.Clone() : v;
        }

        public static int DefaultCount { get { return defaults.Count; } }

        /// <summary>Restores every field of one section to its shipped default. Returns how many fields were reset.</summary>
        public static int ResetSection(Type settingsType, string section)
        {
            if (!Sections.TryGetValue(section, out string[] names))
            {
                return 0;
            }
            int n = 0;
            for (int i = 0; i < names.Length; i++)
            {
                FieldInfo f = settingsType.GetField(names[i], BindingFlags.Public | BindingFlags.Static);
                if (f != null && defaults.TryGetValue(names[i], out object v))
                {
                    f.SetValue(null, Copy(v));
                    n++;
                }
            }
            return n;
        }

        public static void ResetButton(Listing_Standard list, string section)
        {
            if (list.ButtonText("Reset this section to defaults"))
            {
                ResetSection(typeof(LuminousPigmentSettings), section);
            }
        }

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
