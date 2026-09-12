using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.JawaRules
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Jawa Rules.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData, DoWindowContents
    // called from the Mod subclass).
    //
    // Named RSW_JawaRulesSettings/RSW_JawaRulesMod rather than
    // JawaRulesSettings/JawaRulesMod because JawaRulesMod is ALREADY the
    // name of this assembly's static Harmony-bootstrap class — colliding
    // with it is not an option — and this tier's naming grammar (owner,
    // 2026-08-30) prefixes new types RSW_ anyway.
    //
    // Five knobs, one per runtime mechanic this assembly's static
    // constructor arms:
    //   1. sowBanEnabled       — Patch_GrowerSow_ExtraRequirements
    //   2. droidRelationsEnabled — Patch_CreateInitialComponents
    //   3. petNamesEnabled     — Patch_GenerateNecessaryName
    //   4/5. worldLabel* — the two transpilers. A transpiler rewrites IL
    //      once, at patch-apply time, so there is no per-frame hook left to
    //      gate — instead each rewritten call site now CALLS
    //      CurrentWorldLabelAlpha()/CurrentWorldLabelLift() instead of
    //      pushing a baked-in literal, so the settings value (or the
    //      vanilla fallback, if the boost is switched off) is read live,
    //      every time WorldFeatures.UpdateAlpha / WrapAroundPlanetSurface
    //      runs — no restart needed to feel a slider move.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_JawaRulesSettings : ModSettings
    {
        public static bool sowBanEnabled = true;
        public static bool droidRelationsEnabled = true;
        public static bool petNamesEnabled = true;

        public static bool worldLabelAlphaBoostEnabled = true;
        public static float worldLabelAlpha = 0.6f;
        public static bool worldLabelLiftEnabled = true;
        public static float worldLabelLift = 1.5f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref sowBanEnabled, "sowBanEnabled", true);
            Scribe_Values.Look(ref droidRelationsEnabled, "droidRelationsEnabled", true);
            Scribe_Values.Look(ref petNamesEnabled, "petNamesEnabled", true);
            Scribe_Values.Look(ref worldLabelAlphaBoostEnabled, "worldLabelAlphaBoostEnabled", true);
            Scribe_Values.Look(ref worldLabelAlpha, "worldLabelAlpha", 0.6f);
            Scribe_Values.Look(ref worldLabelLiftEnabled, "worldLabelLiftEnabled", true);
            Scribe_Values.Look(ref worldLabelLift, "worldLabelLift", 1.5f);
        }

        /// <summary>Called by the transpiled WorldFeatures.UpdateAlpha in place of its old 0.3 literal.</summary>
        public static float CurrentWorldLabelAlpha()
        {
            return worldLabelAlphaBoostEnabled ? worldLabelAlpha : Patch_WorldFeatures_UpdateAlpha.VanillaAlpha;
        }

        /// <summary>Called by the transpiled WrapAroundPlanetSurface in place of its old 0.4 literal.</summary>
        public static float CurrentWorldLabelLift()
        {
            return worldLabelLiftEnabled ? worldLabelLift : Patch_WorldFeatureText_Lift.VanillaLift;
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Colony rules");
            list.CheckboxLabeled("Jawa may not sow", ref sowBanEnabled,
                "Jawa colonists skip planting in grow zones and hydroponics basins (they still "
              + "harvest, cut plants and chop trees). Off: they sow like anyone else.");
            list.CheckboxLabeled("Humanlike droids get a relations tracker", ref droidRelationsEnabled,
                "Fixes a vanilla gap where humanlike droid races generate with no relations "
              + "tracker and anything reaching for it throws. Off: droids generate exactly as "
              + "they did before this mod.");
            list.CheckboxLabeled("Tamed/newborn animals draw names from their race", ref petNamesEnabled,
                "Off: animals fall back to vanilla's numeric names (\"Dromedary 1\") instead of "
              + "their race's name generator.");
            list.GapLine();

            list.Label("World map labels");
            list.CheckboxLabeled("Boost world feature label opacity", ref worldLabelAlphaBoostEnabled,
                "The italic region/sea/range names printed on the planet map. Off: vanilla's "
              + "faint 0.30 opacity.");
            if (worldLabelAlphaBoostEnabled)
            {
                list.Label("  Label opacity: " + worldLabelAlpha.ToString("0.00"));
                worldLabelAlpha = list.Slider(worldLabelAlpha, 0.3f, 1f);
            }
            list.CheckboxLabeled("Lift world feature labels off the surface", ref worldLabelLiftEnabled,
                "Off: labels sit at vanilla's 0.4 height above the terrain, which can clip into it.");
            if (worldLabelLiftEnabled)
            {
                list.Label("  Label height: " + worldLabelLift.ToString("0.00"));
                worldLabelLift = list.Slider(worldLabelLift, 0.4f, 3f);
            }

            list.End();
        }
    }

    public class RSW_JawaRulesMod : Mod
    {
        public static RSW_JawaRulesSettings settings;

        public RSW_JawaRulesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_JawaRulesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Jawa Rules";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
