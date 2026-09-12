using UnityEngine;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for TitanicCreatures.
    //
    // Four independently-gateable runtime mechanics, found by reading every
    // .cs file in this mod before writing this:
    //   1. Destruction wake (TitanicWakeProcessor, fired from
    //      CompTitanicWake.Notify_EnteredCell via Patch_Thing_Position_Wake)
    //      — crushing/roof-holing/filth as a titan walks.
    //   2. Thick-roof pathing avoidance (Patch_ThickRoofAvoidance).
    //   3. Sub-linear butcher yield curve on T1/T2 corpses
    //      (Patch_ButcherYieldCurve / YieldCurveUtility).
    //   4. The T3 corpse-site landmark (Patch_Corpse_SpawnSetup_TitanicSite /
    //      Building_TitanicCorpseSite / JobDriver_HarvestTitanicCorpse) —
    //      multi-session harvest with daily spoilage, in place of an
    //      instant butcher.
    //
    // Tiering itself (which bodySize crosses into T1/T2/T3) is already
    // player-tunable via Defs/TitanicTierDefs/RM_TitanicTierDef.xml — not
    // duplicated here.
    //
    // Precedent: src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    // ════════════════════════════════════════════════════════════════════
    public class RM_TitanicCreaturesSettings : ModSettings
    {
        // --- Destruction wake -------------------------------------------------
        public static bool wakeEnabled = true;
        public static float wakeCrushDamageMultiplier = 1f;
        public static float wakeFilthTrailChance = 0.35f;

        // --- Thick-roof avoidance ----------------------------------------------
        public static bool roofAvoidanceEnabled = true;

        // --- Butcher yield curve -------------------------------------------------
        public static bool yieldCurveEnabled = true;
        public static float yieldCurveMinFactor = 0.15f;

        // --- T3 corpse site ------------------------------------------------------
        public static bool corpseSiteEnabled = true;
        public static int corpseSiteHarvestMeatPerSession = 25;
        public static int corpseSiteHarvestLeatherPerSession = 10;
        public static float corpseSiteMeatSpoilagePerDay = 0.15f;
        public static float corpseSiteLeatherSpoilagePerDay = 0.08f;
        // 2500 ticks == 1 in-game hour (GenDate.TicksPerHour).
        public static float corpseSiteWorkHoursPerSession = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref wakeEnabled, "wakeEnabled", true);
            Scribe_Values.Look(ref wakeCrushDamageMultiplier, "wakeCrushDamageMultiplier", 1f);
            Scribe_Values.Look(ref wakeFilthTrailChance, "wakeFilthTrailChance", 0.35f);
            Scribe_Values.Look(ref roofAvoidanceEnabled, "roofAvoidanceEnabled", true);
            Scribe_Values.Look(ref yieldCurveEnabled, "yieldCurveEnabled", true);
            Scribe_Values.Look(ref yieldCurveMinFactor, "yieldCurveMinFactor", 0.15f);
            Scribe_Values.Look(ref corpseSiteEnabled, "corpseSiteEnabled", true);
            Scribe_Values.Look(ref corpseSiteHarvestMeatPerSession, "corpseSiteHarvestMeatPerSession", 25);
            Scribe_Values.Look(ref corpseSiteHarvestLeatherPerSession, "corpseSiteHarvestLeatherPerSession", 10);
            Scribe_Values.Look(ref corpseSiteMeatSpoilagePerDay, "corpseSiteMeatSpoilagePerDay", 0.15f);
            Scribe_Values.Look(ref corpseSiteLeatherSpoilagePerDay, "corpseSiteLeatherSpoilagePerDay", 0.08f);
            Scribe_Values.Look(ref corpseSiteWorkHoursPerSession, "corpseSiteWorkHoursPerSession", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Destruction wake", ref wakeEnabled,
                "A large-enough creature crushes crates, holes thin roofs and leaves rubble as it "
              + "walks. Off: it walks through everything harmlessly.");
            if (wakeEnabled)
            {
                list.Label("  Crush damage: " + wakeCrushDamageMultiplier.ToString("0.00") + "x");
                wakeCrushDamageMultiplier = list.Slider(wakeCrushDamageMultiplier, 0.25f, 3f);
                list.Label("  Rubble trail chance per step: " + (wakeFilthTrailChance * 100f).ToString("0") + "%");
                wakeFilthTrailChance = list.Slider(wakeFilthTrailChance, 0f, 1f);
            }
            list.GapLine();

            list.CheckboxLabeled("Avoids walking under overhead mountain", ref roofAvoidanceEnabled,
                "Off: a titan pathfinds through overhead-mountain roofing exactly like any other pawn.");
            list.GapLine();

            list.CheckboxLabeled("Reduced butcher yield on tiered creatures", ref yieldCurveEnabled,
                "A titan too big to fit the corpse site (T1-T2) still butchers for somewhat less "
              + "meat/leather per body size than a same-mass ordinary animal would. Off: full "
              + "vanilla yield.");
            if (yieldCurveEnabled)
            {
                list.Label("  Minimum yield floor: " + (yieldCurveMinFactor * 100f).ToString("0") + "% of normal");
                yieldCurveMinFactor = list.Slider(yieldCurveMinFactor, 0.05f, 1f);
            }
            list.GapLine();

            list.CheckboxLabeled("T3 corpse becomes a harvest site", ref corpseSiteEnabled,
                "The largest tier's corpse becomes a standing landmark, harvested over several "
              + "work sessions with the yield slowly spoiling, instead of being butchered instantly. "
              + "Off: it butchers like any ordinary corpse.");
            if (corpseSiteEnabled)
            {
                list.Label("  Meat per harvest session: " + corpseSiteHarvestMeatPerSession);
                corpseSiteHarvestMeatPerSession = (int)list.Slider(corpseSiteHarvestMeatPerSession, 5f, 100f);
                list.Label("  Leather per harvest session: " + corpseSiteHarvestLeatherPerSession);
                corpseSiteHarvestLeatherPerSession = (int)list.Slider(corpseSiteHarvestLeatherPerSession, 2f, 50f);
                list.Label("  Work hours per session: " + corpseSiteWorkHoursPerSession.ToString("0.0"));
                corpseSiteWorkHoursPerSession = list.Slider(corpseSiteWorkHoursPerSession, 0.25f, 6f);
                list.Label("  Meat spoilage per day: " + (corpseSiteMeatSpoilagePerDay * 100f).ToString("0") + "%");
                corpseSiteMeatSpoilagePerDay = list.Slider(corpseSiteMeatSpoilagePerDay, 0.02f, 0.5f);
                list.Label("  Leather spoilage per day: " + (corpseSiteLeatherSpoilagePerDay * 100f).ToString("0") + "%");
                corpseSiteLeatherSpoilagePerDay = list.Slider(corpseSiteLeatherSpoilagePerDay, 0.02f, 0.5f);
            }

            list.End();
        }
    }

    public class RM_TitanicCreaturesOptionsMod : Mod
    {
        public static RM_TitanicCreaturesSettings settings;

        public RM_TitanicCreaturesOptionsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_TitanicCreaturesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Titanic Creatures";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
