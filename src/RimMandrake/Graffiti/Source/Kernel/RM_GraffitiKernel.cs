// Verse-free kernel of Graffiti: the weighted mark pick and its three eligibility gates, the relation-keyed reaction priority, the
// clan-only veto, scrub protection, the raid-exit gate, the wall-cell candidate gathering, the paint cadence clamp, the breach-lure
// choice and the wall-face draw (side, offset, angle). GraffitiPool, ThoughtWorker_ViewedGraffitiMark, AutoCleanProtection, RaidExitTagger, GraffitiJobUtility, JobDriver_PaintGraffiti,
// Filth_Mark and BreachBiasHook call these with the same expressions; SelfTest/GraffitiFuzz.cs compiles this file (and the two plain enum
// files GraffitiForm.cs / GraffitiCategory.cs) alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib (a `using Verse;` here breaks
// the self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.Graffiti
{
    /// <summary>Which of a mark's reaction ThoughtDefs a viewer gets, in priority order (first match wins).</summary>
    public enum RM_ReactionSlot { Subject, OwnFaction, SameIdeo, HostileMaker, OtherIdeo, Flat }

    /// <summary>One scanned wall-adjacent cell for the mark finder: usable (in the map, standable, walled, reservable) and whether it already carries a mark.</summary>
    public struct RM_MarkCell
    {
        public bool usable, marked;
        public RM_MarkCell(bool usable, bool marked) { this.usable = usable; this.marked = marked; }
    }

    public static class RM_GraffitiKernel
    {
        public const int MinPaintInterval = 60;
        public const int MaxPaintInterval = 1000;
        public const int MaxCandidates = 12;

        /// <summary>The spree / joy pool takes the hand-written forms only (not Stencil, Paste, Sigil, Piece).</summary>
        public static bool SpreeForm(GraffitiForm form)
        {
            return form == GraffitiForm.Scrawl || form == GraffitiForm.Tag || form == GraffitiForm.ThrowUp || form == GraffitiForm.Glyph;
        }

        /// <summary>Paint cadence in ticks. The slider stops at 60..1000, but the file can be edited: 0 would divide by zero in IsHashIntervalTick.</summary>
        public static int PaintInterval(int setting) { return setting < MinPaintInterval ? MinPaintInterval : (setting > MaxPaintInterval ? MaxPaintInterval : setting); }

        /// <summary>A mark with no requiresAnyMeme is ungated; otherwise the placer needs an ideo that holds at least one of them.</summary>
        public static bool MemeGate(bool hasRequirement, bool placerHasIdeo, bool ideoHoldsAny)
        {
            if (!hasRequirement) return true;
            return placerHasIdeo && ideoHoldsAny;
        }

        /// <summary>minArtistic 0 = ungated; a placer with no skill record counts as failing a real requirement.</summary>
        public static bool SkillGate(int minArtistic, bool hasSkillRecord, int level)
        {
            if (minArtistic <= 0) return true;
            return hasSkillRecord && level >= minArtistic;
        }

        /// <summary>
        /// "requires hostile to faction F": open when unnamed, when F's def is unknown or no such faction exists in the game (no Royalty, no
        /// Empire); closed for a placer with no faction or one that IS the target; else the placer's faction must be hostile to it.
        /// </summary>
        public static bool HostilityGate(bool named, bool targetDefExists, bool targetFactionExists, bool placerHasFaction, bool placerIsTarget, bool placerHostileToTarget)
        {
            if (!named) return true;
            if (!targetDefExists) return true;
            if (!targetFactionExists) return true;
            if (!placerHasFaction) return false;
            if (placerIsTarget) return false;
            return placerHostileToTarget;
        }

        /// <summary>A candidate joins the pool when all gates allow it and its weight is positive.</summary>
        public static bool InPool(bool memeOk, bool skillOk, bool hostileOk, float poolWeight)
        {
            return memeOk && skillOk && hostileOk && poolWeight > 0f;
        }

        /// <summary>
        /// Weighted pick by a roll in [0, total]: the first positive-weight entry whose running sum reaches the roll; the last positive entry when float rounding
        /// leaves the roll just above the final sum. -1 for an empty pool or no positive total.
        /// </summary>
        public static int PickIndex(IList<float> weights, float roll)
        {
            float total = Total(weights);
            if (total <= 0f) return -1;
            float cursor = 0f;
            int last = -1;
            for (int i = 0; i < weights.Count; i++)
            {
                if (weights[i] <= 0f) continue;          // a zero or negative weight can never be picked (roll 0 would otherwise land on a leading zero)
                cursor += weights[i];
                last = i;
                if (roll <= cursor) return i;
            }
            return last;
        }

        /// <summary>Sum of the positive weights (the range a roll is drawn from).</summary>
        public static float Total(IList<float> weights)
        {
            float t = 0f;
            for (int i = 0; i < weights.Count; i++) if (weights[i] > 0f) t += weights[i];
            return t;
        }

        /// <summary>
        /// Which reaction a viewer gets from a mark: subject beats own faction beats same ideo beats a hostile maker beats a different ideo,
        /// and the flat reaction is the fallback (also the only one for a mark with no provenance). Each slot needs its own ThoughtDef set.
        /// </summary>
        public static RM_ReactionSlot ReactionSlot(bool hasProvenance,
            bool hasSubjectThought, bool viewerIsSubject,
            bool hasOwnFactionThought, bool makerFactionIsViewerFaction,
            bool hasSameIdeoThought, bool makerIdeoIsViewerIdeo,
            bool hasHostileThought, bool makerFactionHostileToViewer,
            bool hasOtherIdeoThought, bool makerIdeoDiffersFromViewer)
        {
            if (hasProvenance)
            {
                if (hasSubjectThought && viewerIsSubject) return RM_ReactionSlot.Subject;
                if (hasOwnFactionThought && makerFactionIsViewerFaction) return RM_ReactionSlot.OwnFaction;
                if (hasSameIdeoThought && makerIdeoIsViewerIdeo) return RM_ReactionSlot.SameIdeo;
                if (hasHostileThought && makerFactionHostileToViewer) return RM_ReactionSlot.HostileMaker;
                if (hasOtherIdeoThought && makerIdeoDiffersFromViewer) return RM_ReactionSlot.OtherIdeo;
            }
            return RM_ReactionSlot.Flat;
        }

        /// <summary>A clan-only mark withholds its reaction from anyone outside the player's faction.</summary>
        public static bool ClanOnlyBlocks(bool clanOnly, bool viewerIsPlayerFaction) { return clanOnly && !viewerIsPlayerFaction; }

        /// <summary>Do both rooms have to match for a cell to count as "in the viewer's room"? Only when both resolve.</summary>
        public static bool SameRoomOrUnknown(bool viewerRoomKnown, bool cellRoomKnown, bool sameRoom) { return !(viewerRoomKnown && cellRoomKnown && !sameRoom); }

        /// <summary>The situational thought is active only with the setting on, a spawned viewer on a map, and a matching mark nearby.</summary>
        public static bool ThoughtActive(bool settingOn, bool onMap, bool spawned, bool markFound) { return settingOn && onMap && spawned && markFound; }

        /// <summary>
        /// Does the ambient clean scan skip this filth? Never for a forced (player) clean, never with the setting off, never for non-marks or marks
        /// with no extension; else when the extension flags it, its maker was the player's faction, or it is Devotional.
        /// </summary>
        public static bool ProtectsFromAutoClean(bool forced, bool settingOn, bool isMark, bool hasExt, bool flagged, bool ownFaction, bool devotional)
        {
            if (forced || !settingOn) return false;
            if (!isMark || !hasExt) return false;
            return flagged || ownFaction || devotional;
        }

        /// <summary>A departing pawn tags the wall only for a hostile non-player faction, with painting and exit-tagging both on.</summary>
        public static bool RaidExitTags(bool paintingOn, bool exitTaggingOn, bool factionKnown, bool factionIsPlayer, bool hostileToPlayer)
        {
            if (!paintingOn || !exitTaggingOn) return false;
            return factionKnown && !factionIsPlayer && hostileToPlayer;
        }

        /// <summary>Going over: a different mark already on the cell is destroyed first; the same def is thickened, not replaced.</summary>
        public static bool IsRival(bool isMark, bool sameDef) { return isMark && !sameDef; }

        /// <summary>
        /// Candidate gathering for the wall-mark finder, in scan order: bare cells (no mark yet) up to MaxCandidates stop the scan; already-marked
        /// cells are kept only as a fallback, up to MaxCandidates. Returns the indexes of the pool to pick from: the bare ones when there are
        /// any, else the marked ones.
        /// </summary>
        public static List<int> Gather(IList<RM_MarkCell> cells)
        {
            var bare = new List<int>();
            var any = new List<int>();
            for (int i = 0; i < cells.Count; i++)
            {
                if (!cells[i].usable) continue;
                if (!cells[i].marked)
                {
                    bare.Add(i);
                    if (bare.Count >= MaxCandidates) break;
                }
                else if (any.Count < MaxCandidates)
                {
                    any.Add(i);
                }
            }
            return bare.Count > 0 ? bare : any;
        }

        // ---------------------------------------------------------------- wall face (GRAFFITI_WALLFACE)
        // Owner, by card 2026-10-22 ("Q9 → Graffiti floor cell drawn offset facing wall"): a mark stays on the floor cell beside
        // the wall but records which side the wall is on, and is DRAWN offset onto that wall and turned to face it, so it reads as
        // wall art with no new thing class. Sides are Rot4 integers: 0 north (+z), 1 east (+x), 2 south (-z), 3 west (-x).

        /// <summary>How far toward the wall a mark is drawn, in cells: onto the shared edge, half over the wall. [INVENTED; the
        /// owner judges it in game]</summary>
        public const float WallFaceOffsetCells = 0.5f;

        public const int NoWall = -1;

        /// <summary>The wall a mark is painted on, from which cardinal neighbours are full-fillage walls. With several, north first
        /// (the wall face the top-down camera sees, so the mark stays upright), then east, west, south. NoWall with none.</summary>
        public static int WallSide(bool north, bool east, bool south, bool west)
        {
            if (north) return 0;
            if (east) return 1;
            if (west) return 3;
            if (south) return 2;
            return NoWall;
        }

        /// <summary>Draw offset (x, z in cells) toward the wall on `side`; (0, 0) for NoWall or an out-of-range side.</summary>
        public static void WallFaceOffset(int side, float cells, out float dx, out float dz)
        {
            dx = side == 1 ? cells : side == 3 ? -cells : 0f;
            dz = side == 0 ? cells : side == 2 ? -cells : 0f;
        }

        /// <summary>Draw rotation in degrees (RimWorld's clockwise-from-north, as Rot4.AsAngle): the mark's top points into the wall
        /// it is painted on. 0 for NoWall or an out-of-range side, which is the old upright floor draw.</summary>
        public static float WallFaceAngle(int side)
        {
            return side >= 0 && side <= 3 ? side * 90f : 0f;
        }

        /// <summary>
        /// Which luring building the raid heads for: the nearest to the plain pick (squared distance), ties by the lowest key. -1 for none.
        /// (The first version took whichever mark the map's thing list happened to yield first.)
        /// </summary>
        public static int ChooseLure(IList<long> distSqToFallback, IList<int> tieKey)
        {
            int best = -1;
            for (int i = 0; i < distSqToFallback.Count; i++)
            {
                if (best < 0 || distSqToFallback[i] < distSqToFallback[best] || (distSqToFallback[i] == distSqToFallback[best] && tieKey[i] < tieKey[best])) best = i;
            }
            return best;
        }
    }
}
