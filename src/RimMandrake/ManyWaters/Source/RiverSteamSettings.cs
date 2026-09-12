using UnityEngine;
using Verse;

namespace RiverSteamHook
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for ManyWaters (river steam).
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs. Namespace/
    // assembly kept as RiverSteamHook — this mod predates the three-tier
    // naming scheme and migrates only under NAMING_SCHEME_EXECUTION_1
    // (CLAUDE.md: "do not rename ahead of it").
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
            return "ManyWaters";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
