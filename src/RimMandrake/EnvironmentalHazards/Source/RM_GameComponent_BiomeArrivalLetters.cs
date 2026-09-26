using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // BIOME_ARRIVAL_NARRATION_1. Per-save memory of which biomes have already
    // introduced themselves, so a second gravship landing in a biome (a
    // second colony, a relocation) fires nothing -- "never repeated" per the
    // item's own spec. Keyed on BiomeDef.defName rather than the BiomeDef
    // reference itself, same posture as every other Scribe_Collections string
    // set in this repo, so it survives a def-hash reload untouched.
    //
    // Auto-instantiated: Game.FillComponents constructs every non-abstract
    // GameComponent subclass in every loaded assembly (see
    // src/RimMandrake/LoreStages/Source/GameComponent_LoreStage.cs for the
    // same pattern) -- nothing to register, no def to ship.
    public class RM_GameComponent_BiomeArrivalLetters : GameComponent
    {
        private HashSet<string> firedBiomeDefNames = new HashSet<string>();

        public RM_GameComponent_BiomeArrivalLetters(Game game)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref firedBiomeDefNames, "firedBiomeDefNames", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && firedBiomeDefNames == null)
            {
                firedBiomeDefNames = new HashSet<string>();
            }
        }

        // Called from RM_Patch_GravshipArrivalLetter's postfix on the gen step
        // that marks a map as a gravship's landing site -- the one detection
        // signal this item reuses rather than inventing a second (see that
        // file's header). Gated by the kit's own settings toggle FIRST and
        // returns before touching firedBiomeDefNames when it is off, so a
        // disabled feature never marks a biome "seen" and resumes cleanly the
        // moment it is switched back on.
        public void Notify_GravshipLanded(Map map)
        {
            if (map?.Biome == null)
            {
                return;
            }

            if (!RM_EnvironmentalHazardsSettings.biomeArrivalLettersEnabled)
            {
                return;
            }

            RM_BiomeArrivalLetterExtension ext = map.Biome.GetModExtension<RM_BiomeArrivalLetterExtension>();
            if (ext == null || ext.letterLabel.NullOrEmpty() || ext.letterText.NullOrEmpty())
            {
                return; // this biome carries no arrival letter -- most don't yet, and that is fine
            }

            if (!firedBiomeDefNames.Add(map.Biome.defName))
            {
                return; // already introduced itself this save
            }

            Find.LetterStack.ReceiveLetter(ext.letterLabel, ext.letterText, LetterDefOf.NeutralEvent,
                new LookTargets(map.Parent));
        }
    }
}
