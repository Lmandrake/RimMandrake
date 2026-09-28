using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LongShade
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Long Shade.
    //
    // LONGSHADE_RM_MOD_BUILD_1 step 1. Precedent: RM_GreentideMod.cs,
    // RM_PyrelandsMod.cs (biome_mod_architecture.md §6a's reference list).
    //
    // UNLIKE Greentide/Pyrelands, this biome shipped no scripted hazard of
    // its own until LONGSHADE_RULED_CONTENT_1 Q6 (2026-09-27) — the
    // dewfringe's shade-boundary spawn gate, RM_Patch_DewfringeWildSpawnGate,
    // this mod's own genuinely-owned C#, not a shared-kit toggle. The two
    // OLDER mechanics its own native content touches — shade-seeking wander
    // (RM_JobGiver_WanderInShadeGrid, read by the gloomcast's extension over
    // in the Star Wars cast) and contact venom (CompContactVenom, read by
    // RM_Venomvine) — are still owned, toggled and globally gated by
    // mandrake.rm.creaturebehaviors' own RM_CreatureBehaviorsSettings
    // (shadeGridEnabled / shadeSeekingWanderEnabled / shadeStaggerEnabled)
    // and mandrake.rm.environmentalhazards' own RM_EnvironmentalHazardsSettings,
    // per biome_mod_architecture.md §6b-3: "the Utinni layer gets no settings
    // of its own for biomes... a kit mechanic somewhere other than its home
    // biome is a shipped DEFAULT... not a copy of the mechanic." The same
    // rule makes this mod's own screen the wrong place to re-toggle a kit it
    // merely uses (loadAfter only, no hard modDependency) — that would be a
    // second, redundant gate that could silently disagree with the kit's own
    // switch.
    //
    // So this mod's own screen gates the master switch (§6a's "Master" row)
    // PLUS the one mechanic that is now genuinely this mod's own: the
    // dewfringe's rim gate. Turning modEnabled off does not (and should not)
    // also flip dewfringeShadeLineGateEnabled — that field controls a C#
    // Harmony patch that stays armed regardless (same reason Leachmoss's own
    // gate reads its own bool rather than a shared kit's), so the two are
    // separate checkboxes, not one master collapsing into the other.
    // ════════════════════════════════════════════════════════════════════
    public class RM_LongShadeSettings : ModSettings
    {
        public static bool modEnabled = true;

        public static bool dewfringeShadeLineGateEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref modEnabled, "modEnabled", true);
            Scribe_Values.Look(ref dewfringeShadeLineGateEnabled, "dewfringeShadeLineGateEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Long Shade content enabled", ref modEnabled,
                "Master switch, kept for parity with every other RimMandrake biome mod. "
              + "The biome def, its native creatures and its native flora are plain "
              + "content either way, so this mainly stops the dewfringe's rim gate below.");
            list.CheckboxLabeled("Dewfringe confined to the shade line", ref dewfringeShadeLineGateEnabled,
                "The dewfringe (a new native plant, LONGSHADE_RULED_CONTENT_1 Q6) only ever "
              + "grows on shade-boundary cells — the rim, not the area — enforced by a small "
              + "Harmony patch on wild-plant spawning. Off: it follows plain fertility/terrain "
              + "rules like any other plant and can spread across open ground, breaking the "
              + "design's own 'pale, rim-only, never green in quantity' ceiling — provided as "
              + "an escape hatch, not the intended way to play.");
            list.GapLine();

            list.Label("Shade-seeking wander and contact venom");
            list.Label("Both mechanics this biome's own flora touches (the vorrel's shade "
              + "dispersal; the venomvine's contact venom) are owned and toggled by the mods "
              + "that ship them, not by this one:");
            list.Label("  - Creature Behaviors (mandrake.rm.creaturebehaviors) Mod Settings: "
              + "shade grid / shade-seeking wander / stagger toggles.");
            list.Label("  - Environmental Hazards (mandrake.rm.environmentalhazards) Mod "
              + "Settings: contact venom toggle.");
            list.Label("Turning either off there also turns it off here — this mod loads "
              + "after both and adds no second, possibly-disagreeing switch of its own "
              + "(biome_mod_architecture.md §6b-3).");

            list.End();
        }
    }

    public class RM_LongShadeMod : Mod
    {
        public static RM_LongShadeSettings settings;

        public RM_LongShadeMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_LongShadeSettings>();
        }

        public override string SettingsCategory()
        {
            return "Long Shade";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
