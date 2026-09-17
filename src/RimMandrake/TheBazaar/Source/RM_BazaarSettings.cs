using UnityEngine;
using Verse;

namespace RimMandrake.Bazaar
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 / "every mod ships Mod Settings" -- BUT this
    // slice (BAZAAR_WINDOW_GRID_1, slice 1) ships zero player-visible
    // mechanic: no Harmony intercept, no grid, no economy, no haggle duel,
    // no banter. RimMandrakeFlowWorksMod.cs's own comment on this exact
    // point stands: "a slider that moves nothing is worse than an absent
    // one." So this is a real settings screen with no toggles yet rather
    // than a screen full of toggles wired to nothing -- every field design
    // §7 lists (dynamic economy, per-layer intel, haggling, crit spoils,
    // banter, broker tab, wishlist flash, grid density) belongs here ONLY
    // once its mechanic exists to gate, added in the same slice as that
    // mechanic, never ahead of it.
    // ════════════════════════════════════════════════════════════════════
    public class RM_BazaarSettings : ModSettings
    {
        public override void ExposeData()
        {
            base.ExposeData();
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard();
            list.Begin(inRect);
            Text.Font = GameFont.Medium;
            list.Label("The Bazaar");
            Text.Font = GameFont.Small;
            list.Label("Nothing to configure yet. This slice ships only the plugin def "
                     + "scaffolding (columns, badges, tabs, intel layers) and an inert "
                     + "Dialog_Trade subclass -- the trade window itself is not replaced "
                     + "until the WindowStack.Add intercept lands. Settings for the grid, "
                     + "economy, haggling and banter arrive with each of those, not before.");
            list.End();
        }
    }

    public class RM_BazaarMod : Mod
    {
        public static RM_BazaarSettings settings;

        public RM_BazaarMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_BazaarSettings>();
        }

        public override string SettingsCategory() => "The Bazaar";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
