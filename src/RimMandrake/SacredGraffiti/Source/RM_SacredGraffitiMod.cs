using UnityEngine;
using Verse;

namespace RimMandrake.SacredGraffiti
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for SacredGraffiti.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // The one runtime mechanism this assembly ships is
    // RitualOutcomeEffectWorker_PlaceSacredMark.ApplyExtraOutcome, which
    // spawns def.filthCountToSpawn.RandomInRange sacred-mark filth on a
    // POSITIVE ritual outcome. Two things worth exposing: a master on/off
    // (a favorable ritual just grants its ordinary vanilla outcome, no mark),
    // and a count multiplier on however many marks a god's own
    // RitualOutcomeEffectDef asks for.
    // ════════════════════════════════════════════════════════════════════
    public class RM_SacredGraffitiSettings : ModSettings
    {
        public static bool sacredMarkEnabled = true;
        public static float markCountMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref sacredMarkEnabled, "sacredMarkEnabled", true);
            Scribe_Values.Look(ref markCountMultiplier, "markCountMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Sacred marks from rituals", ref sacredMarkEnabled,
                "A favorable ritual outcome can leave a devotional wall-mark behind. "
              + "Off: the ritual's ordinary reward still happens, just never a mark.");
            list.Label("Mark count: " + markCountMultiplier.ToString("0.00") + "x how many a ritual would place");
            markCountMultiplier = list.Slider(markCountMultiplier, 0.25f, 3f);

            list.End();
        }
    }

    public class RM_SacredGraffitiMod : Mod
    {
        public static RM_SacredGraffitiSettings settings;

        public RM_SacredGraffitiMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_SacredGraffitiSettings>();
        }

        public override string SettingsCategory()
        {
            return "Sacred Graffiti";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
