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

        // WARCASKET_CASK_BAY_AND_SARCOPHAGI_1 (RM_Sarcophagus.cs). Off: a dead
        // wearer's sarcophagus suit is never sealed and no crack-open option
        // is offered; the suit strips like any apparel.
        public static bool sarcophagiEnabled = true;

        // RM_CompCaskShielding (RM_CaskBay.cs). Off: the cask bay is ordinary
        // cask-only storage; stored wastepacks dissolve and cores dose as
        // they would anywhere.
        public static bool caskBayShieldingEnabled = true;

        // RM_CompCoreDose. Off: a half-extracted core is inert cargo.
        public static bool coreDoseEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref compoundFailureEnabled, "compoundFailureEnabled", true);
            Scribe_Values.Look(ref terrainImmersionEnabled, "terrainImmersionEnabled", true);
            Scribe_Values.Look(ref sarcophagiEnabled, "sarcophagiEnabled", true);
            Scribe_Values.Look(ref caskBayShieldingEnabled, "caskBayShieldingEnabled", true);
            Scribe_Values.Look(ref coreDoseEnabled, "coreDoseEnabled", true);
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1200f;

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);

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

                list.Gap();
                list.CheckboxLabeled("Warcasket sarcophagi", ref sarcophagiEnabled,
                    "Shipped default: ON. A sarcophagus-variant warcasket (the adjusted warcasket) seals "
                  + "onto its wearer at death: ordinary stripping leaves it on the body, and a colonist "
                  + "must crack it open (right-click the corpse) to recover the suit, its welded tools "
                  + "and the half-extracted core. Off: the suit strips like any apparel and no salvage "
                  + "is added.");

                list.Gap();
                list.CheckboxLabeled("Cask bay shielding", ref caskBayShieldingEnabled,
                    "Shipped default: ON. The lead-lined cask bay (a gravship hardpoint) stops stored "
                  + "toxic wastepacks from dissolving and stored half-extracted cores from dosing anyone. "
                  + "Off: the bay is ordinary cask-only storage.");

                list.Gap();
                list.CheckboxLabeled("Half-extracted core dose", ref coreDoseEnabled,
                    "Shipped default: ON. A loose half-extracted core doses nearby pawns with toxic "
                  + "buildup (toxic resistance and a warcasket's toxin rating both apply). Off: the "
                  + "core is inert cargo.");
            }

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
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
