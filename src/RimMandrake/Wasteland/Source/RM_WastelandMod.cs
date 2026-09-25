using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Wasteland
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Wasteland. Pattern copied
    // from RM_GreentideSettings / RM_TheRotSettings (static fields read from
    // everywhere, Scribe_Values in ExposeData, a DoWindowContents helper
    // called from the Mod subclass). Defaults = shipped behavior throughout.
    //
    // Wasteland is a plain standalone biome (WASTELAND_RM_MOD_BUILD_1 §8: "no
    // kits/*.md spec exists for it") — its only owned mechanic is the brine
    // mining archetype (three GenStepDefs scattering RM_BrineDeposit_Tekk/
    // Drazz/BrinePlate). Both toggles below are scaffolding, same posture
    // RM_TheRotSettings documents for its own not-yet-wired switches: the
    // scatter GenStepDefs are plain XML with no C# gate today, so toggling
    // "off" here does not yet stop them from generating — wiring a runtime
    // check into a GenStep_ScatterThings subclass is owed, not built in this
    // pass (creature content was explicitly out of scope; this is the same
    // "ships now, hooks later" posture the source content's own header used
    // for the dose/geiger layer).
    // ════════════════════════════════════════════════════════════════════
    public class RM_WastelandSettings : ModSettings
    {
        public static bool wastelandEnabled = true;
        public static bool brineDepositsEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref wastelandEnabled, "wastelandEnabled", true);
            Scribe_Values.Look(ref brineDepositsEnabled, "brineDepositsEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Wasteland enabled", ref wastelandEnabled,
                "Master switch. Off: the biome and its defs still load (nothing here is "
              + "worldgen-affecting — RM_Wasteland ships generatesNaturally=false, placed only "
              + "by hand or by another mod/scenario), but every per-feature toggle below is "
              + "ignored as off.");
            list.GapLine();

            list.CheckboxLabeled("Brine deposit mining", ref brineDepositsEnabled,
                "Tekk/drazz/spent-electrode-plate deposits scatter into any generated map's "
              + "hypersaline brine water (RM_WastelandBrineShallow terrain). NOT YET WIRED — "
              + "the scatter is plain XML with no runtime gate, so this toggle is scaffolding "
              + "until a GenStep_ScatterThings subclass reads it.");

            list.End();
        }
    }

    public class RM_WastelandMod : Mod
    {
        public static RM_WastelandSettings settings;

        public RM_WastelandMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WastelandSettings>();
        }

        public override string SettingsCategory()
        {
            return "Wasteland";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
