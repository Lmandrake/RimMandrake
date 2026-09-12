using UnityEngine;
using Verse;

namespace RimMandrake.LoreStages
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for LoreStages.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // This engine's only live mechanism is GameComponent_LoreStage.Apply(),
    // which rewrites a handful of def description/label fields to whatever
    // rung each RM_LoreStageTableDef ladder currently sits at, then clears
    // the two private description caches so the change shows immediately.
    // There is no rate/chance/interval anywhere in this mechanism — a ladder
    // advances only when a debug action or a consumer mod calls SetStage/
    // AdvanceStage — so the one honest control is a master on/off.
    //
    // GATING CHOICE: off makes every ladder read as stage 0 (defs show their
    // shipped, unstaged text) via GameComponent_LoreStage.EffectiveStage.
    // The real per-ladder progress in GameComponent_LoreStage.stages is left
    // completely alone — SetStage/AdvanceStage calls from elsewhere keep
    // recording it — so turning this back on picks up exactly where the
    // colony's progress already was, never resets it.
    // ════════════════════════════════════════════════════════════════════
    public class RM_LoreStagesSettings : ModSettings
    {
        public static bool stagedTextEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stagedTextEnabled, "stagedTextEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            bool before = stagedTextEnabled;
            list.CheckboxLabeled("Staged lore descriptions", ref stagedTextEnabled,
                "Biome, item and hediff descriptions can change wording as your colony learns "
              + "more about a place. Off: everything shows its original, unstaged text — your "
              + "colony's actual progress keeps being tracked in the background and picks back "
              + "up right away if you turn this on again.");

            if (stagedTextEnabled != before)
            {
                GameComponent_LoreStage.Current?.Reapply();
            }

            list.End();
        }
    }

    public class RM_LoreStagesMod : Mod
    {
        public static RM_LoreStagesSettings settings;

        public RM_LoreStagesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_LoreStagesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Lore Stages";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
