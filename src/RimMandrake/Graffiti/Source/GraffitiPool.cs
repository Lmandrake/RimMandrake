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
        public static ThingDef PickForSpree(Pawn painter, float maxWidth = float.MaxValue, IntVec3? at = null)
        {
            ThingDef pick = WeightedPick(SpreeEligible, painter, maxWidth, at);
            return pick ?? Fallback(maxWidth);
        }

        // Joy: a calm hand with time on its side. Everything a spree reaches
        // for plus the planned forms - the stencil, the poster, the piece and
        // above all the painter's own ideoligion sigil - and no untrained
        // scrawl from a trained artist.
        public static ThingDef PickForJoy(Pawn painter, float maxWidth = float.MaxValue, IntVec3? at = null)
        {
            bool trained = (painter?.skills?.GetSkill(SkillDefOf.Artistic)?.Level ?? 0) >= TrainedHand;
            ThingDef pick = WeightedPick(ext => RM_GraffitiKernel.JoyForm(ext.form) && !(trained && ext.form == GraffitiForm.Scrawl), painter, maxWidth, at);
            return pick ?? Fallback(maxWidth);
        }

        private const int TrainedHand = 6;

        /// <summary>The old scrawl when the pool has nothing, but only if it fits: a mark too wide for its gap would paint over a neighbour.</summary>
        private static ThingDef Fallback(float maxWidth)
        {
            return WidthOf(RMGraffitiDefOf.RM_Graffiti_Vandal) <= maxWidth ? RMGraffitiDefOf.RM_Graffiti_Vandal : null;
        }

        /// <summary>Wall cells a mark's drawing spans.</summary>
        public static float WidthOf(ThingDef markDef) => markDef?.graphicData?.drawSize.x ?? 1f;

        // Live pass 13: on a wall a few weeks old the gaps between marks are about a cell, and only three drawings are a cell wide, so
        // every gap got a tally, a scratch or a rude little man (37 of Ashgate's 70 marks). A writer squeezes a smaller tag into a gap:
        // most drawings may go down to this share of their size to fit one. A piece is planned to its wall and doesn't shrink.
        public const float MinFit = 0.8f;

        /// <summary>The narrowest this drawing may be painted to fit a gap (Filth_Mark.fit).</summary>
        public static float FitWidthOf(ThingDef markDef)
        {
            GraffitiForm form = markDef?.GetModExtension<ModExtension_Graffiti>()?.form ?? GraffitiForm.Scrawl;
            return WidthOf(markDef) * (form == GraffitiForm.Piece ? 1f : MinFit);
        }

        /// <summary>How much of its full size this drawing takes in a gap this wide: 1 if it fits whole, never under MinFit.</summary>
        public static float FitFor(ThingDef markDef, float room)
        {
            float w = WidthOf(markDef);
            return room >= w ? 1f : System.Math.Max(FitWidthOf(markDef) / w, room / w);
        }

        // Designator: only marks the player can deliberately choose
        // (ModExtension_Graffiti.designatorEligible), still weighted so a
        // designated cell doesn't always get the exact same mark.
        public static ThingDef PickForDesignator(Pawn painter, float maxWidth = float.MaxValue, IntVec3? at = null)
        {
            ThingDef pick = WeightedPick(DesignatorEligible, painter, maxWidth, at);
            return pick ?? Fallback(maxWidth);
        }

        // RaidExitTagger: marks a raiding pawn's own gang leaves behind
        // (ModExtension_Graffiti.raidExitEligible), meme-gated ones only
        // offered when the pawn's ideo actually holds a matching meme.
        public static ThingDef PickForRaidExit(Pawn raider, float maxWidth = float.MaxValue, IntVec3? at = null)
        {
            return WeightedPick(RaidExitEligible, raider, maxWidth, at);
        }

        private static bool SpreeEligible(ModExtension_Graffiti ext)
        {
            return RM_GraffitiKernel.SpreeForm(ext.form);
        }

        private static bool DesignatorEligible(ModExtension_Graffiti ext)
        {
            return ext.designatorEligible;
        }

        private static bool RaidExitEligible(ModExtension_Graffiti ext)
        {
            return ext.raidExitEligible;
        }

        // GRAFFITI_DESIGNATOR_MARK_CHOICE_1: a mark the player ordered by
        // name is still painted only by a hand the pool would allow it to -
        // the same meme, skill and hostility gates, never a bypass. A false
        // here sends the job back to PickForDesignator.
        public static bool PainterMayPaint(ThingDef markDef, Pawn painter)
        {
            ModExtension_Graffiti ext = markDef?.GetModExtension<ModExtension_Graffiti>();
            if (ext == null || !ext.designatorEligible) return false;
            if (RM_GraffitiKernel.RefusesToPaint(ext.meaning, painter?.story?.traits?.HasTrait(TraitDefOf.Kind) ?? false)) return false;
            // A mark about someone takes a hand that does art at all; a scrawl doesn't.
            if ((ext.hasSubject || ext.minArtistic > 0) && painter != null && painter.WorkTagIsDisabled(WorkTags.Artistic)) return false;
            // A mark about someone never rolls out of a pool (weight 0), but it can be ordered by name.
            return RM_GraffitiKernel.InPool(MemeGateAllows(ext, painter), SkillGateAllows(ext, painter), HostilityGateAllows(ext, painter), ext.hasSubject || ext.meaning == RM_Meaning.Insult ? 1f : ext.poolWeight);
        }

        public static IEnumerable<ThingDef> AllDesignatorEligible()
        {
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                ModExtension_Graffiti ext = d.GetModExtension<ModExtension_Graffiti>();
                if (ext != null && ext.designatorEligible) yield return d;
            }
        }

        private delegate bool EligibleFilter(ModExtension_Graffiti ext);

        private const float NearbyRadius = 8f;

        /// <summary>The marks already on this bit of wall, so the pool rarely repeats one beside itself.</summary>
        private static HashSet<ThingDef> DefsNear(IntVec3 at, Map map)
        {
            var near = new HashSet<ThingDef>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(at, NearbyRadius, useCenter: true))
            {
                if (!c.InBounds(map)) continue;
                foreach (Thing t in c.GetThingList(map))
                {
                    if (t is Filth_Mark) near.Add(t.def);
                }
            }
            return near;
        }

        private static ThingDef WeightedPick(EligibleFilter filter, Pawn placer, float maxWidth, IntVec3? at)
        {
            HashSet<ThingDef> near = at.HasValue && placer?.Map != null ? DefsNear(at.Value, placer.Map) : null;
            if (at.HasValue && placer?.Map != null && !RM_GraffitiKernel.PaintsEdgeOn(RM_GraffitiKernel.FaceOfSide(Filth_Mark.ReadWallSide(at.Value, placer.Map)))) return null;
            List<ThingDef> defs = new List<ThingDef>();
            List<float> weights = new List<float>();
            int level = placer?.skills?.GetSkill(SkillDefOf.Artistic)?.Level ?? 0;
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                ModExtension_Graffiti ext = d.GetModExtension<ModExtension_Graffiti>();
                if (ext == null || !filter(ext) || FitWidthOf(d) > maxWidth) continue;
                if (!RM_GraffitiKernel.InPool(MemeGateAllows(ext, placer), SkillGateAllows(ext, placer), HostilityGateAllows(ext, placer), ext.poolWeight)) continue;
                defs.Add(d);
                float w = ext.poolWeight * RM_GraffitiKernel.FormAffinity(ext.form, level);
                weights.Add(near != null && near.Contains(d) ? w * RM_GraffitiKernel.NearbySameMarkWeight : w);
            }
            int index = RM_GraffitiKernel.PickIndex(weights, defs.Count == 0 ? 0f : Rand.Range(0f, RM_GraffitiKernel.Total(weights)));
            return index < 0 ? null : defs[index];
        }

        // Tier C gate: a meme-affinity mark is only in the pool for a
        // placer whose Ideo actually holds one of its requiresAnyMeme
        // memes. A mark with no requiresAnyMeme is ungated (every punk mark,
        // tier-A/B sigils).
        private static bool MemeGateAllows(ModExtension_Graffiti ext, Pawn placer)
        {
            bool hasReq = !ext.requiresAnyMeme.NullOrEmpty();
            Ideo ideo = GraffitiJobUtility.IdeoOf(placer);
            // A tier-A sigil is the painter's own faith's icon in a frame: without an ideoligion (classic mode, or Ideology off) it would
            // be an empty frame, so nobody without one paints it.
            if (ext.sigilTierA && ideo == null && placer != null) return false;
            bool holds = false;
            if (hasReq && ideo != null)
            {
                foreach (MemeDef meme in ext.requiresAnyMeme)
                {
                    if (ideo.HasMeme(meme)) { holds = true; break; }
                }
            }
            return RM_GraffitiKernel.MemeGate(hasReq, ideo != null, holds);
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
            SkillRecord skill = ext.minArtistic > 0 ? placer?.skills?.GetSkill(SkillDefOf.Artistic) : null;
            return RM_GraffitiKernel.SkillGate(ext.minArtistic, skill != null, skill != null ? skill.Level : 0);
        }

        // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 wave 2, wiring design §2.2's
        // "requiresHostile to Empire" for RM_Graffiti_Stencil_Crown. See
        // ModExtension_Graffiti.requiresHostileToFactionDef's own comment
        // for the open-on-either-lookup-miss rule - a Royalty-less mod list
        // or a game with no Empire faction never has this gate close.
        private static bool HostilityGateAllows(ModExtension_Graffiti ext, Pawn placer)
        {
            bool named = !string.IsNullOrEmpty(ext.requiresHostileToFactionDef);
            if (!named) return true;
            FactionDef targetDef = DefDatabase<FactionDef>.GetNamedSilentFail(ext.requiresHostileToFactionDef);
            Faction targetFaction = targetDef == null ? null : Find.FactionManager?.FirstFactionOfDef(targetDef);
            Faction placerFaction = placer?.Faction;
            return RM_GraffitiKernel.HostilityGate(true, targetDef != null, targetFaction != null, placerFaction != null,
                placerFaction != null && placerFaction == targetFaction, placerFaction != null && targetFaction != null && placerFaction.HostileTo(targetFaction));
        }
    }
}
