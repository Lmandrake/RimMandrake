using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Stillsand.
    //
    // Precedent: src/RimMandrake/FeverWood/Source/RM_FeverWoodMod.cs.
    //
    // Deliberately thin, and that is a finding, not a shortcut. This build
    // (STILLSAND_RM_MOD_BUILD_1 steps 1-4) ships only the BiomeDef itself,
    // reusing vanilla Core's own `RimWorld.BiomeWorker_ExtremeDesert`
    // unchanged (the item's own MEASURED STATE: the donor twin never named
    // a third-party workerClass, so no RM_BiomeWorker_Stillsand exists to
    // gate). FeverWood's own toggle gates ITS custom worker's score; there
    // is no equivalent class here to gate without authoring one the item
    // explicitly found unowed. A checkbox wired to nothing is a settings
    // screen that lies, so none is added — only an informational panel.
    // ════════════════════════════════════════════════════════════════════
    public class RM_StillsandSettings : ModSettings
    {
        public override void ExposeData()
        {
            base.ExposeData();
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Stillsand");
            list.Label("This build ships biome data only (terrain, weather, disease "
              + "profile, and the placement wiring for its wild animals, wild plants and "
              + "pack animals, all patched in from mandrake.rut.patches). It reuses "
              + "vanilla Core's own BiomeWorker_ExtremeDesert unchanged, so there is no "
              + "natural-placement score of this mod's own to toggle. No mechanic here "
              + "is gated — nothing to configure yet.");

            list.End();
        }
    }

    public class RM_StillsandMod : Mod
    {
        public static RM_StillsandSettings settings;

        public RM_StillsandMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_StillsandSettings>();
        }

        public override string SettingsCategory()
        {
            return "Stillsand";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
