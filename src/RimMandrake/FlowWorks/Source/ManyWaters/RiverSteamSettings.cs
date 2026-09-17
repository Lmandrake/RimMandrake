using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.ManyWaters
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for ManyWaters (river steam).
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs. Merged into
    // FlowWorks 2026-09-16 (FLOWWORKS_BUILD_PROGRAM_1 Phase 1): the bare
    // `RiverSteamHook` namespace became RimMandrake.FlowWorks.ManyWaters and
    // the assembly is RimMandrakeFlowWorks.dll. RimUtinni: UtinniPatches'
    // ManyWaters_RiverSteam_Ashkarr.xml names the modExtension by full type
    // name and was updated in the same change — a modExtension whose Class
    // does not resolve discards the WHOLE def, silently.
    //
    // The one runtime mechanism this mod carries is MapComponent_RiverSteam
    // (see RiverSteamHook.cs) — ambient-only periodic steam puffs over a
    // biome-opted-in river. No gameplay effect either way, so a single
    // master switch plus a rate slider is the whole surface worth exposing.
    // ════════════════════════════════════════════════════════════════════
    public class RiverSteamSettings : ModSettings
    {
        public static bool riverSteamEnabled = true;
        public static float puffRateMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref riverSteamEnabled, "riverSteamEnabled", true);
            Scribe_Values.Look(ref puffRateMultiplier, "puffRateMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("River steam puffs", ref riverSteamEnabled,
                "Purely visual: rivers on a biome that opts in throw periodic steam puffs. "
              + "No gameplay effect either way.");
            list.Label("Puff rate: " + puffRateMultiplier.ToString("0.00") + "x");
            puffRateMultiplier = list.Slider(puffRateMultiplier, 0.25f, 3f);

            list.End();
        }
    }

    public class RiverSteamMod : Mod
    {
        public static RiverSteamSettings settings;

        public RiverSteamMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RiverSteamSettings>();
        }

        public override string SettingsCategory()
        {
            return "FlowWorks: Water effects";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
