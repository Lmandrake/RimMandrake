using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // SEA_DIVE_MAPS_BUILD_1 — Mod Settings, rewritten wholesale.
    // The shore-terrain "dive to hunt/commune" mechanic (SCALD_DIVING_MOD_1)
    // is RETIRED per the SHIP-ONLY ACCESS ruling (owner, 2026-09-26): this
    // mod is now the ship-hatch pocket-map mechanism. Precedent for the
    // pattern: src/RimStarWars/Shokk/Source/RSW_ShokkSettings.cs.
    //
    // MOD_OPTIONS_RETROFIT_1 doctrine (CLAUDE.md "Every mod ships superb Mod
    // Settings"): defaults = shipped, all-off degrades gracefully
    // (masterEnabled false makes every RM_SeaDiveHatch un-enterable
    // everywhere, on any sea, in any biome).
    // ════════════════════════════════════════════════════════════════════
    public class RM_DivingSettings : ModSettings
    {
        public static bool masterEnabled = true;

        // SHIP-ONLY ACCESS RULING enforcement toggle. Default true matches
        // the ruling; off exists purely so a franchise-free/no-DLC install,
        // a modded ruleset, or a debug session can build+test the hatch
        // without also owning a completed gravship — degrades gracefully
        // per MOD_OPTIONS_RETROFIT_1, it does not remove the ruling from
        // About.xml's description of shipped default behavior.
        public static bool requireGravEngine = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref requireGravEngine, "requireGravEngine", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Sea diving enabled", ref masterEnabled,
                "Master switch. Off: no RM_SeaDiveHatch anywhere can be entered — the mod is "
              + "fully inert (existing hatches stay buildable but never open a pocket map).");

            if (masterEnabled)
            {
                list.Gap();
                list.CheckboxLabeled("Require a grav engine to build a dive hatch", ref requireGravEngine,
                    "Shipped default: ON. The owner's ruling is that a gravship is the sole way "
                  + "to reach a sea floor — turning this off lets the hatch be built anywhere, for "
                  + "testing or a different ruleset, but that is not the shipped experience.");
            }

            list.End();
        }
    }

    public class RM_DivingInteractionMod : Mod
    {
        public static RM_DivingSettings settings;

        public RM_DivingInteractionMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_DivingSettings>();
        }

        public override string SettingsCategory()
        {
            return "Deep Diving";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
