using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.WasteRun
{
    // MOD_OPTIONS_RETROFIT_1 doctrine: independent toggles, defaults = shipped behavior.
    public class WasteRunSettings : ModSettings
    {
        public static bool masterEnabled = true;
        public static bool offerEnabled = true;
        public static bool dropOnEmpireEnabled = true;
        public static bool freezeColdSideEnabled = true;
        public static bool entombAssailantsEnabled = true;
        public static bool propaneLakeEnabled = true;
        public static bool slimeExperimentEnabled = true;
        // THROAT_CASK_ITEM_1 (numbers PROVISIONAL)
        public static bool throatCaskEnabled = true;
        public static bool throatRadiationEnabled = true;
        public static bool throatShipFaultsEnabled = true;
        public static bool throatBurstEnabled = true;
        public static bool throatDecayEnabled = true;

        public static bool DestinationEnabled(WasteDestination d)
        {
            switch (d)
            {
                case WasteDestination.DropOnEmpire: return dropOnEmpireEnabled;
                case WasteDestination.FreezeColdSide: return freezeColdSideEnabled;
                case WasteDestination.EntombAssailants: return entombAssailantsEnabled;
                case WasteDestination.IgnitePropaneLake: return propaneLakeEnabled;
                default: return slimeExperimentEnabled;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref offerEnabled, "offerEnabled", true);
            Scribe_Values.Look(ref dropOnEmpireEnabled, "dropOnEmpireEnabled", true);
            Scribe_Values.Look(ref freezeColdSideEnabled, "freezeColdSideEnabled", true);
            Scribe_Values.Look(ref entombAssailantsEnabled, "entombAssailantsEnabled", true);
            Scribe_Values.Look(ref propaneLakeEnabled, "propaneLakeEnabled", true);
            Scribe_Values.Look(ref slimeExperimentEnabled, "slimeExperimentEnabled", true);
            Scribe_Values.Look(ref throatCaskEnabled, "throatCaskEnabled", true);
            Scribe_Values.Look(ref throatRadiationEnabled, "throatRadiationEnabled", true);
            Scribe_Values.Look(ref throatShipFaultsEnabled, "throatShipFaultsEnabled", true);
            Scribe_Values.Look(ref throatBurstEnabled, "throatBurstEnabled", true);
            Scribe_Values.Look(ref throatDecayEnabled, "throatDecayEnabled", true);
        }

        private static Vector2 scroll;
        private static float viewHeight = 600f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            list.CheckboxLabeled("Waste run enabled", ref masterEnabled,
                "Master switch. Off: no waste-run quest is offered and the cask bay shows no destination commands.");
            if (masterEnabled)
            {
                list.Gap();
                list.CheckboxLabeled("Offer the waste-run quest", ref offerEnabled,
                    "Shipped default: ON. Once a cask bay holds waste, the Junkers' broker may offer the run. Off: no new offers (a quest already accepted still works).");
                list.Gap();
                list.CheckboxLabeled("Destination: drop it on the Empire", ref dropOnEmpireEnabled,
                    "Shipped default: ON. An act of war dressed as sanitation: Empire goodwill collapses.");
                list.CheckboxLabeled("Destination: freeze it on the cold side", ref freezeColdSideEnabled,
                    "Shipped default: ON. The honest coward's option. Costs nothing now.");
                list.CheckboxLabeled("Destination: entomb it on the Assailants", ref entombAssailantsEnabled,
                    "Shipped default: ON. The Rakatan solution, re-enacted. Buys decades; costs a conscience.");
                list.CheckboxLabeled("Destination: the propane lakes", ref propaneLakeEnabled,
                    "Shipped default: ON. A melt that ignites the nightside lake and marks the war lab breached (the lab itself is a stub until ANCIENT_WAR_LAB_1 ships).");
                list.CheckboxLabeled("Destination: the Slime experiment", ref slimeExperimentEnabled,
                    "Shipped default: ON. The only option that is an experiment rather than a verdict. Results are random and provisional.");
            }
            if (masterEnabled)
            {
                list.Gap();
                list.CheckboxLabeled("Throat cask effects enabled", ref throatCaskEnabled,
                    "Shipped default: ON. Off: the Throat cask is inert cargo (all its numbers are provisional).");
                if (throatCaskEnabled)
                {
                    list.CheckboxLabeled("  Constant radiation", ref throatRadiationEnabled, "Shipped default: ON. A bay mutes the dose, never silences it.");
                    list.CheckboxLabeled("  Gravship malfunctions while aboard", ref throatShipFaultsEnabled, "Shipped default: ON. One random system fault about every day.");
                    list.CheckboxLabeled("  Bursts if the carrier is hurt or it burns", ref throatBurstEnabled, "Shipped default: ON.");
                    list.CheckboxLabeled("  Slow armageddon nearby (die-off, mood)", ref throatDecayEnabled, "Shipped default: ON. Escalates the longer it stays.");
                }
            }
            viewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class WasteRunMod : Mod
    {
        public static WasteRunSettings settings;

        public WasteRunMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<WasteRunSettings>();
        }

        public override string SettingsCategory()
        {
            return "Waste Run";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
