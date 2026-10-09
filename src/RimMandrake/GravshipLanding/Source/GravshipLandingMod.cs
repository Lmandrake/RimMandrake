using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.GravshipLanding
{
    public class GravshipLandingSettings : ModSettings
    {
        public static bool revealOutdoorsBeforeLanding = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref revealOutdoorsBeforeLanding, "revealOutdoorsBeforeLanding", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);
            list.CheckboxLabeled("Reveal the outdoors before choosing a landing spot", ref revealOutdoorsBeforeLanding,
                "When a gravship arrives at a tile with no map, unfog every outdoor area of the new map "
              + "before the landing picker appears. Roofed interiors stay hidden. Off: vanilla behaviour, "
              + "which reveals only the flood-fill from the reserved landing spot.");
            list.End();
        }
    }

    public class GravshipLandingMod : Mod
    {
        public const string HarmonyId = "mandrake.rm.gravshiplanding";
        public static GravshipLandingSettings settings;

        public GravshipLandingMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<GravshipLandingSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony(HarmonyId), Assembly.GetExecutingAssembly(), "RimMandrake.GravshipLanding");
            Log.Message("[RimMandrake.GravshipLanding] ready.");
        }

        public override string SettingsCategory()
        {
            return "Gravship Landing Reveal";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
