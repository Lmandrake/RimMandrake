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
    // ⚠️ UNLIKE Greentide/Pyrelands, this biome ships NO scripted hazard of
    // its own. The two mechanics its own native content touches — shade-
    // seeking wander (RM_JobGiver_WanderInShadeGrid, read by the ShadeWhale's
    // extension over in the Star Wars cast) and contact venom
    // (CompContactVenom, read by RM_Venomvine) — are owned, toggled and
    // globally gated by mandrake.rm.creaturebehaviors' own
    // RM_CreatureBehaviorsSettings (shadeGridEnabled / shadeSeekingWanderEnabled
    // / staggerEnabled) and mandrake.rm.environmentalhazards' own
    // RM_EnvironmentalHazardsSettings, per biome_mod_architecture.md §6b-3:
    // "the Utinni layer gets no settings of its own for biomes... a kit
    // mechanic somewhere other than its home biome is a shipped DEFAULT... not
    // a copy of the mechanic." The same rule makes this mod's own screen the
    // wrong place to re-toggle a kit it merely uses (loadAfter only, no hard
    // modDependency) — that would be a second, redundant gate that could
    // silently disagree with the kit's own switch.
    //
    // So the only thing genuinely this mod's OWN to gate is the master
    // switch itself (§6a's "Master" row: "the mod on/off — the biome def
    // still loads; the mechanics stop"). With nothing scripted here to stop,
    // turning it off is a no-op beyond the label below — §6c's "all-off
    // degrades gracefully" bar is met trivially, not faked: the biome still
    // loads, generates and plays as terrain + plants + weather either way.
    // ════════════════════════════════════════════════════════════════════
    public class RM_LongShadeSettings : ModSettings
    {
        public static bool modEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref modEnabled, "modEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Long Shade content enabled", ref modEnabled,
                "Master switch, kept for parity with every other RimMandrake biome mod. "
              + "This mod ships no scripted hazard of its own — the biome def, its two "
              + "native creatures (landopus, cephalope) and its native flora (the vorrel) "
              + "are plain content either way, so there is nothing further this switch stops.");
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
