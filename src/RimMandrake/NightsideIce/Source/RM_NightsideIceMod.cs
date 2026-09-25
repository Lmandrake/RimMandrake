using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.NightsideIce
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Nightside Ice.
    //
    // Precedent: src/RimMandrake/FeverWood/Source/RM_FeverWoodMod.cs.
    //
    // Deliberately thin, and that is a finding, not a shortcut:
    // NIGHTSIDEICE_RM_MOD_BUILD_1 steps 1-4 ship only the BiomeDef itself.
    // No kit spec exists for this biome (§8 of the item: grepped
    // src/RimMandrake, src/RimUtinni, src/RimStarWars for "tunneler",
    // "one-move", "landform catalyst", "catalytic sheet" — zero hits outside
    // prose), and workerClass stays the vanilla Core BiomeWorker_IceSheet, so
    // there is no natural-placement scoring toggle either (unlike
    // RM_FeverWoodSettings.naturalPlacementEnabled, which gates a real
    // RM_BiomeWorker_FeverWood this biome does not have). A per-mechanic
    // toggle for content this mod does not ship would be a settings screen
    // that lies, so only a master switch is built.
    // ════════════════════════════════════════════════════════════════════
    public class RM_NightsideIceSettings : ModSettings
    {
        /// <summary>Master switch. Off: this mod's def still loads (nothing
        /// on a saved game silently disappears) — there is currently nothing
        /// else for this toggle to gate, since the biome ships no kit
        /// mechanic and no custom worker of its own. Reserved for whichever
        /// mechanic (tunnelers, icy insects, landform catalysts — all
        /// unbuilt, see the item's §8) lands here first.</summary>
        public static bool masterEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Nightside Ice");
            list.CheckboxLabeled("Mod enabled", ref masterEnabled,
                "Off: RM_NightsideIce still loads and can be assigned to a tile directly. "
              + "No kit mechanic exists yet for this toggle to gate — the biome is deliberately "
              + "near-empty by design (no photosynthesis, almost no animal life), not a build "
              + "gap.");
            list.GapLine();
            list.Label("No per-mechanic settings exist yet: this biome ships no kit spec "
              + "(tunnelers, icy insects and landform catalysts are unbuilt, separate authoring "
              + "work) and its BiomeWorker is vanilla Core's own BiomeWorker_IceSheet.");

            list.End();
        }
    }

    public class RM_NightsideIceMod : Mod
    {
        public static RM_NightsideIceSettings settings;

        public RM_NightsideIceMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_NightsideIceSettings>();
        }

        public override string SettingsCategory()
        {
            return "Nightside Ice";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
