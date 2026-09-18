using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for StructureInjectionsRUT.
    //
    // One mechanism (WAR_LAB_CRATER_HOOK_1): destroying the war-lab reactor
    // core permanently mutates every RUT_PropaneLake worldmap tile into
    // RUT_Wasteland, once per save. No hardcoded rate/chance/threshold exists
    // to slider-tune here (it is a one-shot structural event, not a
    // recurring one) — the real, honest option is whether this permanent
    // planet-wide biome change is allowed to happen at all.
    public class StructureInjectionsRUTSettings : ModSettings
    {
        public static bool warLabCraterEnabled = true;
        public static bool ashfallCommandCodesEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref warLabCraterEnabled, "warLabCraterEnabled", true);
            Scribe_Values.Look(ref ashfallCommandCodesEnabled, "ashfallCommandCodesEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("War lab ignition mutates the planet", ref warLabCraterEnabled,
                "Destroying the war lab's reactor core permanently turns every propane-lake "
              + "tile on the planet into wasteland. Off: destroying the core does nothing "
              + "extra to the worldmap.");

            list.CheckboxLabeled("Rakatan command codes unlock the war lab", ref ashfallCommandCodesEnabled,
                "Redeeming the Rakatan command codes from the Ashfall Research Base sets the "
              + "flag whichever war-lab gate check consults to open its shielding. Off: "
              + "redeeming the codes does nothing (the item is still consumed).");

            list.End();
        }
    }

    public class StructureInjectionsRUTMod : Mod
    {
        public static StructureInjectionsRUTSettings settings;

        public StructureInjectionsRUTMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<StructureInjectionsRUTSettings>();
        }

        public override string SettingsCategory()
        {
            return "Structure Injections";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
