using UnityEngine;
using Verse;

namespace RimMandrake.Warcasket
{
    // WARCASKET_SUIT_CLASS_1. MOD_OPTIONS_RETROFIT_1 doctrine: every
    // mechanic toggles independently, defaults = shipped behavior, off
    // degrades gracefully and never strands or harms anyone.
    public class RM_WarcasketSettings : ModSettings
    {
        public static bool masterEnabled = true;

        // The compound-failure mechanic (RM_CompWarcasketIntegrity). Off:
        // the suit still carries all its stats, it simply never fails.
        public static bool compoundFailureEnabled = true;

        // The general terrain-immersion hazard (RM_MapComponent_
        // HazardousTerrainImmersion). Off: deep/non-walkable water is
        // ordinary (if impassable-feeling) terrain again for everyone —
        // no RM_TerrainImmersionHazard is ever applied, and any already on
        // a saved map simply stops accruing/decays as normal.
        public static bool terrainImmersionEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref compoundFailureEnabled, "compoundFailureEnabled", true);
            Scribe_Values.Look(ref terrainImmersionEnabled, "terrainImmersionEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Warcasket mechanics enabled", ref masterEnabled,
                "Master switch. Off: warcaskets keep their base apparel stats (armor, insulation, "
              + "vacuum/toxin resistance) but neither of this mod's two active mechanics run at all.");

            if (masterEnabled)
            {
                list.Gap();
                list.CheckboxLabeled("Compound-failure rolls", ref compoundFailureEnabled,
                    "Shipped default: ON. Once two or more hazard classes (vacuum, extreme temperature, "
                  + "toxic terrain) are active against a warcasket's wearer at once, the suit can fail: "
                  + "its own HP takes damage and the wearer takes a tendable warcasket-breach injury. A "
                  + "single hazard alone never triggers this. Off: the suit's stat coverage is unchanged, "
                  + "it simply never fails.");

                list.Gap();
                list.CheckboxLabeled("Hazardous water/brine terrain", ref terrainImmersionEnabled,
                    "Shipped default: ON. Standing in deep or brine water too deep to walk through — not "
                  + "an ordinary ford or shallow margin, which is always safe — is dangerous without "
                  + "enough hazardous-terrain protection from worn apparel (a warcasket, or anything else "
                  + "carrying that stat). This is TERRAIN survival only: it never grants access to a sea "
                  + "floor, which stays reachable only through a gravship. Off: deep water is ordinary "
                  + "terrain again for everyone; nothing already accrued is affected beyond continuing to "
                  + "decay normally.");
            }

            list.End();
        }
    }

    public class RM_WarcasketMod : Mod
    {
        public static RM_WarcasketSettings settings;

        public RM_WarcasketMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WarcasketSettings>();
        }

        public override string SettingsCategory()
        {
            return "Warcasket";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
