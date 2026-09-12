using UnityEngine;
using Verse;

namespace RimMandrake.StructureInjections
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for StructureInjections.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // This mod's only live mechanism is GenStep_RimplacePlan.Generate() -
    // it replays a compiled rimplace BuildPlan onto a freshly generated
    // map (foundation/terrain/things/runs/roof/pawns). There is exactly
    // one master switch worth exposing: whether the whole replay runs at
    // all. It is inherently WORLDGEN-AFFECTING (mapgen time only) - there
    // is no live-play tick or patch in this assembly to gate separately.
    // No other tunable number exists in the mechanism: SeedPart is a fixed
    // RNG-stream identifier, not a gameplay magnitude, and every placement
    // coordinate/defName comes from the plan file itself, not a hardcoded
    // constant here.
    // ════════════════════════════════════════════════════════════════════
    public class RM_StructureInjectionsSettings : ModSettings
    {
        public static bool enabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Structure injection templates enabled (affects new maps only)", ref enabled,
                "Replays authored building templates (foundation, terrain, machines, roofs, and "
              + "sometimes a pawn/corpse) onto freshly generated maps that call for one - things "
              + "like the moisture farm layout. Off: those maps generate with none of the template "
              + "applied, as if this mod's templates did not exist. Never affects a map that has "
              + "already been generated.");

            list.End();
        }
    }

    public class RM_StructureInjectionsMod : Mod
    {
        public static RM_StructureInjectionsSettings settings;

        public RM_StructureInjectionsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_StructureInjectionsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Structure Injections";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
