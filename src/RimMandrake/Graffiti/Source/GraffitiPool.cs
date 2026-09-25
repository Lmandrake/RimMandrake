using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 mechanism 4: "A data-driven pool
    // selector replacing the hard RM_Graffiti_Vandal reference in
    // JobDriver_PaintGraffiti." Every placer (spree, joy, designator,
    // raid-exit) asks this for a def instead of naming one directly, so a
    // future content pack (RUT/Salvation, RSW) only has to add ThingDefs
    // with ModExtension_Graffiti set - no C# change, no placer touched.
    //
    // Weighted by ModExtension_Graffiti.poolWeight (design default 1). Pool
    // membership is computed fresh each call (small def count, called at
    // most every paintIntervalTicks per painting pawn or once per raid
    // exit/designation - not a hot path worth caching).
    public static class GraffitiPool
    {
        // Spree/Joy: any RM_BaseGraffiti descendant whose form is one of
        // the "written by hand" forms (not a Sigil/Glyph a pawn wouldn't
        // spontaneously reach for, and not Piece - v2/fork F1). Falls back
        // to RM_Graffiti_Vandal if nothing else is registered, so a mod
        // list with only the four GRAFFITI_GENERIC_MARKS_1 defs behaves
        // exactly as it did before this item.
        public static ThingDef PickForSpree(Pawn painter)
        {
            ThingDef pick = WeightedPick(SpreeEligible, painter);
            return pick ?? RMGraffitiDefOf.RM_Graffiti_Vandal;
        }

        // Designator: only marks the player can deliberately choose
        // (ModExtension_Graffiti.designatorEligible), still weighted so a
        // designated cell doesn't always get the exact same mark.
        public static ThingDef PickForDesignator(Pawn painter)
        {
            ThingDef pick = WeightedPick(DesignatorEligible, painter);
            return pick ?? RMGraffitiDefOf.RM_Graffiti_Vandal;
        }

        // RaidExitTagger: marks a raiding pawn's own gang leaves behind
        // (ModExtension_Graffiti.raidExitEligible), meme-gated ones only
        // offered when the pawn's ideo actually holds a matching meme.
        public static ThingDef PickForRaidExit(Pawn raider)
        {
            return WeightedPick(RaidExitEligible, raider);
        }

        private static bool SpreeEligible(ModExtension_Graffiti ext)
        {
            return ext.form == GraffitiForm.Scrawl || ext.form == GraffitiForm.Tag ||
                   ext.form == GraffitiForm.ThrowUp || ext.form == GraffitiForm.Glyph;
        }

        private static bool DesignatorEligible(ModExtension_Graffiti ext)
        {
            return ext.designatorEligible;
        }

        private static bool RaidExitEligible(ModExtension_Graffiti ext)
        {
            return ext.raidExitEligible;
        }

        private delegate bool EligibleFilter(ModExtension_Graffiti ext);

        private static ThingDef WeightedPick(EligibleFilter filter, Pawn placer)
        {
            List<ThingDef> defs = new List<ThingDef>();
            List<float> weights = new List<float>();
            float total = 0f;
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                ModExtension_Graffiti ext = d.GetModExtension<ModExtension_Graffiti>();
                if (ext == null || !filter(ext)) continue;
                if (!MemeGateAllows(ext, placer)) continue;
                if (!SkillGateAllows(ext, placer)) continue;
                if (!HostilityGateAllows(ext, placer)) continue;
                if (ext.poolWeight <= 0f) continue;
                defs.Add(d);
                weights.Add(ext.poolWeight);
                total += ext.poolWeight;
            }
            if (defs.Count == 0 || total <= 0f) return null;
            float roll = Rand.Range(0f, total);
            float cursor = 0f;
            for (int i = 0; i < defs.Count; i++)
            {
                cursor += weights[i];
                if (roll <= cursor) return defs[i];
            }
            return defs[defs.Count - 1];
        }

        // Tier C gate: a meme-affinity mark is only in the pool for a
        // placer whose Ideo actually holds one of its requiresAnyMeme
        // memes. A mark with no requiresAnyMeme is ungated (every punk mark,
        // tier-A/B sigils).
        private static bool MemeGateAllows(ModExtension_Graffiti ext, Pawn placer)
        {
            if (ext.requiresAnyMeme.NullOrEmpty()) return true;
            Ideo ideo = placer?.Ideo;
            if (ideo == null) return false;
            foreach (MemeDef meme in ext.requiresAnyMeme)
            {
                if (ideo.HasMeme(meme)) return true;
            }
            return false;
        }

        // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 wave 2, design §1.2's
        // "minArtistic int - designator/joy gating by skill": 0 (the field's
        // default) is always allowed, so every mark shipped before this
        // wave is unaffected. A pawn with no skills tracker (SkillsHandler)
        // is treated as skill 0, never as an unconditional pass - a raider
        // gang with no Artistic-trained member simply never offers a
        // ThrowUp, exactly per the design's "a Scrawl from a wretch, a
        // ThrowUp from an artist."
        private static bool SkillGateAllows(ModExtension_Graffiti ext, Pawn placer)
        {
            if (ext.minArtistic <= 0) return true;
            SkillRecord skill = placer?.skills?.GetSkill(SkillDefOf.Artistic);
            if (skill == null) return false;
            return skill.Level >= ext.minArtistic;
        }

        // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 wave 2, wiring design §2.2's
        // "requiresHostile to Empire" for RM_Graffiti_Stencil_Crown. See
        // ModExtension_Graffiti.requiresHostileToFactionDef's own comment
        // for the open-on-either-lookup-miss rule - a Royalty-less mod list
        // or a game with no Empire faction never has this gate close.
        private static bool HostilityGateAllows(ModExtension_Graffiti ext, Pawn placer)
        {
            if (string.IsNullOrEmpty(ext.requiresHostileToFactionDef)) return true;
            FactionDef targetDef = DefDatabase<FactionDef>.GetNamedSilentFail(ext.requiresHostileToFactionDef);
            if (targetDef == null) return true;
            Faction targetFaction = Find.FactionManager?.FirstFactionOfDef(targetDef);
            if (targetFaction == null) return true;
            Faction placerFaction = placer?.Faction;
            if (placerFaction == null) return false;
            if (placerFaction == targetFaction) return false;
            return placerFaction.HostileTo(targetFaction);
        }
    }
}
