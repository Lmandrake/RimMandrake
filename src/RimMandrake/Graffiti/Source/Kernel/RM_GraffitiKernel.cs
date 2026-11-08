// Verse-free kernel of Graffiti: the social tables (who paints what, who reacts how, what they do), the weighted mark pick and its three eligibility gates, the relation-keyed reaction priority, the
// clan-only veto, scrub protection, the raid-exit gate, the wall-cell candidate gathering, the paint cadence clamp, the breach-lure
// choice and the wall-plane draw (which face, its polygons, the hand). GraffitiPool, ThoughtWorker_ViewedGraffitiMark, AutoCleanProtection, RaidExitTagger, GraffitiJobUtility, JobDriver_PaintGraffiti,
// Filth_Mark and BreachBiasHook call these with the same expressions; SelfTest/GraffitiFuzz.cs compiles this file (and the two plain enum
// files GraffitiForm.cs / GraffitiCategory.cs) alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib (a `using Verse;` here breaks
// the self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.Graffiti
{
    /// <summary>Which of a mark's reaction ThoughtDefs a viewer gets, in priority order (first match wins).</summary>
    public enum RM_ReactionSlot { Subject, OwnFaction, SameIdeo, HostileMaker, OtherIdeo, Flat }

    /// <summary>What a mark says about somebody or something. None is a plain tag: it says only who was here.</summary>
    public enum RM_Meaning { None, Mockery, Tribute, Memorial, Jest, Beauty, Devotion, Insult }

    /// <summary>What reading a mark does to one pawn.</summary>
    public enum RM_Reaction { None, Humiliated, ShrugsOff, FriendDefends, Gleeful, LostFace, Disapproves, Honored, Jealous, Scoffs, Warmed, Mourning, Amused, Moved, Uplifted, Offended, RivalTag, FriendTag, Uneasy, Defiant, WorkDestroyed }

    /// <summary>What a pawn does about a mark: wipe it, cross it out, paint back at the painter, or go and have it out.</summary>
    public enum RM_Answer { None, Scrub, Deface, Reply, Confront }

    /// <summary>The temperament table's answer column: what a person would rather do about a mark than what the answer table says.</summary>
    public enum RM_Lean { None, Scrub, Reply, Nothing }

    /// <summary>One person's temperament toward marks, or one row of the table (Defs/TemperamentDefs_Graffiti.xml). Multipliers default 1.</summary>
    public struct RM_Temper
    {
        public bool numb;
        public float bad, good, fine, ugly, temper, paint, offended;
        public int neat;
        public RM_Lean lean;

        public static RM_Temper Plain => new RM_Temper { bad = 1f, good = 1f, fine = 1f, ugly = 1f, temper = 1f, paint = 1f, offended = 1f };
    }

    /// <summary>A viewer's standing to a mark, read off the pawns by GraffitiSocial.</summary>
    public struct RM_Viewer
    {
        public bool isMaker, isSubject, ownFaction, hostileMaker, loverOfSubject, loverOfMaker;
        public int opinionOfMaker, opinionOfSubject;
        public bool kind, hot, psychopath;
        public bool hasIdeo, makerHasIdeo, sameIdeoAsMaker;
    }

    /// <summary>A plain colour, here where UnityEngine isn't.</summary>
    public struct RM_Rgb
    {
        public float r, g, b;
        public RM_Rgb(float r, float g, float b) { this.r = r; this.g = g; this.b = b; }
    }

    /// <summary>A point of a mark on a wall: screen position in cells, and where on the mark's art it is.</summary>
    public struct RM_PlaneVert
    {
        public float x, z, u, v;
        public RM_PlaneVert(float x, float z, float u = 0f, float v = 0f) { this.x = x; this.z = z; this.u = u; this.v = v; }
        public static RM_PlaneVert Lerp(RM_PlaneVert a, RM_PlaneVert b, float f)
        {
            return new RM_PlaneVert(a.x + (b.x - a.x) * f, a.z + (b.z - a.z) * f, a.u + (b.u - a.u) * f, a.v + (b.v - a.v) * f);
        }
    }

    /// <summary>The part of a mark on one surface of one wall cell, k cells along from its anchor: a convex counter-clockwise polygon, on the face or bent over onto the wall's top.</summary>
    public struct RM_MarkPiece
    {
        public int k;
        public List<RM_PlaneVert> poly;
        public bool onTop;
        public RM_MarkPiece(int k, List<RM_PlaneVert> poly, bool onTop = false) { this.k = k; this.poly = poly; this.onTop = onTop; }
    }

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

        /// <summary>The joy pool is what a calm hand chooses to make: everything the spree pool has, and the slower, planned forms.</summary>
        public static bool JoyForm(GraffitiForm form)
        {
            return SpreeForm(form) || form == GraffitiForm.Stencil || form == GraffitiForm.Paste || form == GraffitiForm.Sigil || form == GraffitiForm.Piece;
        }

        /// <summary>Ticks of work for one mark at the slider's default pace (250): a scrawl is seconds, a piece an afternoon.</summary>
        public static int PaintTicksBase(GraffitiForm form)
        {
            switch (form)
            {
                case GraffitiForm.Scrawl: return 300;
                case GraffitiForm.Stencil: return 300;
                case GraffitiForm.Paste: return 300;
                case GraffitiForm.Glyph: return 400;
                case GraffitiForm.Tag: return 500;
                case GraffitiForm.ThrowUp: return 1200;
                case GraffitiForm.Sigil: return 1200;
                case GraffitiForm.Piece: return 2800;
                default: return 500;
            }
        }

        /// <summary>Work ticks for one mark: the form's base scaled by the pace setting (clamped).</summary>
        public static int PaintTicks(GraffitiForm form, int paceSetting)
        {
            int t = PaintTicksBase(form) * PaintInterval(paceSetting) / 250;
            return t < 30 ? 30 : t;
        }

        public const int MaxMarksPerJoySitting = 4;
        public const float JoySittingFull = 0.95f;

        /// <summary>A spree job always moves on down the wall; a joy sitting moves on until the pawn is satisfied or has made its few marks.</summary>
        public static bool SittingContinues(int marksMade, bool frenzied, float joyLevel)
        {
            if (frenzied) return true;
            return marksMade < MaxMarksPerJoySitting && joyLevel < JoySittingFull;
        }

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

        /// <summary>A raid turns to leave when its lord moves from a toil that was not leaving onto one that is (GRAFFITI_V1_LIVE_PROOF_1):
        /// once per departure, never for a lord already leaving that switches between leaving toils.</summary>
        public static bool TurnsToLeave(bool wasLeaving, bool nowLeaving) { return nowLeaving && !wasLeaving; }

        /// <summary>A raid-exit tag goes only on an EXTERIOR face (GRAFFITI_V1_LIVE_PROOF_1 A2): the standing cell is unroofed and its
        /// room is known and psychologically outdoors, so a raider who turned to leave from inside the base never tags an interior wall.</summary>
        public static bool ExteriorFace(bool roofed, bool roomKnown, bool outdoors) { return !roofed && roomKnown && outdoors; }

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

        /// <summary>An idle colonist reaches for the can on one think in this many: a few times a day for someone with truly nothing to do.</summary>
        public const float IdleTagChance = 0.02f;

        public static bool IdleHandTags(float roll) { return roll < IdleTagChance; }

        /// <summary>A hand's own pull toward the brush, by its Artistic passion (0 none, 1 minor, 2 burning; a modded passion past 2 counts as
        /// burning) and level. Live 2026-11-07, before this: the two weakest hands in an 8-pawn colony made 7 of its 8 marks, all ugly, and the
        /// level-15 artist none, because who painted was blind to art. Now the colony's walls are mostly written by the people who care.</summary>
        /// <summary>A mourner who hasn't yet painted their dead reaches for the brush this much more often.</summary>
        public const float GriefUrge = 1.75f;

        public static float HandUrge(int passion, int level)
        {
            float p = passion <= 0 ? 0.4f : (passion == 1 ? 1f : 1.6f);
            return p + 0.04f * Clamp(level, 0, 20);
        }

        /// <summary>Has a room its share of a calm painter's marks? One, and one more for every 15 cells of floor.</summary>
        public static bool RoomHoldsEnough(int marks, int floorCells) { return marks >= 1 + floorCells / 15; }

        /// <summary>Open ground (outdoors, or a room bigger than any building's) is capped by stretch of wall, not by room: two marks within
        /// StretchRadius cells, so an outer wall reads as written on with bare wall between, not painted solid.</summary>
        public static bool StretchHoldsEnough(int marksNear) { return marksNear >= 2; }

        public const float StretchRadius = 4.5f;
        public const int OpenGroundCells = 400;

        /// <summary>Feelings that come again with every mark of the kind (a rival's tags, a friend's pieces, a creed, a memorial): logged once a day
        /// per reader and painter. Events about someone (a mockery, a tribute, a faction insult) log every time.</summary>
        public static bool LogsOncePerDay(RM_Reaction r)
        {
            return r == RM_Reaction.RivalTag || r == RM_Reaction.Moved || r == RM_Reaction.Offended || r == RM_Reaction.Mourning;
        }

        /// <summary>Two marks on one line of wall, centres `distance` cells apart with half-widths a and b, cover each other.</summary>
        public static bool WallMarksOverlap(float distance, float halfWidthA, float halfWidthB)
        {
            return Math.Abs(distance) < halfWidthA + halfWidthB - 0.15f;
        }

        // ---------------------------------------------------------------- the wall plane
        // Owner, 2026-11-07: "Make the art look like it's on the WALLS in perspective correctly". A wall tile is a fake box, read off
        // the atlases (art_source/wallgeom.py is the offline twin of this, same numbers): a dark cap; a front face at the cell's south
        // edge when no wall stands south; a side face at the east or west edge when no wall stands there; mitred where they meet. No
        // north face exists: seen from this camera, the side of a wall away from us is simply not there to paint.
        // A mark stays on the floor cell where the painter stood and records the side its wall is on. Sides are Rot4 integers:
        // 0 north (+z), 1 east (+x), 2 south (-z), 3 west (-x).

        public const int NoWall = -1;
        public const int LinkN = 1, LinkE = 2, LinkS = 4, LinkW = 8;    // MaterialAtlasPool's bits
        public const int FaceNone = -1, FaceFront = 0, FaceEast = 1, FaceWest = 2, FaceHidden = 3;

        /// <summary>A wall's height in cells, on the wall's own plane: the visible band of a face is this tall foreshortened. It
        /// sets how squashed a mark is: at a 0.4-cell band a square mark comes out half as tall as it is wide.</summary>
        public const float WallWorldHeight = 0.8f;
        /// <summary>Owner's option D, 2026-11-07: a full-size mark is this many world cells tall, its whole face and then over the crease onto the wall's top.</summary>
        public const float ClimbHeight = 1.2f;
        /// <summary>A wall's top faces the camera, so a world cell of it is a screen cell. The face is foreshortened, the top is not: that kink at the crease is the bend.</summary>
        public const float TopRate = 1f;
        /// <summary>Bare wall top the paint leaves at the far edge, screen cells; bare face under the lowest mark, world cells.</summary>
        public const float TopLip = 0.08f, MarkFoot = 0.04f;
        /// <summary>Atlas outline: the art stops this far short of the cell's edge.</summary>
        public const float RimX = 0.03f, RimZ = 0.02f;
        /// <summary>The Core atlases measured (crease 0.40, side 0.22), for a wall whose atlas can't be read.</summary>
        public const float DefaultCrease = 0.40f, DefaultSideWidth = 0.22f;

        /// <summary>The wall a mark is painted on, from which cardinal neighbours are walls. North first (the face the camera sees
        /// whole), then east, west (the side faces), and south last: only an old save's mark ever gets that one.</summary>
        public static int WallSide(bool north, bool east, bool south, bool west)
        {
            if (north) return 0;
            if (east) return 1;
            if (west) return 3;
            if (south) return 2;
            return NoWall;
        }

        /// <summary>Which face of its wall a mark on `side` lies on. A wall to the floor's north shows its front to the camera.</summary>
        public static int FaceOfSide(int side)
        {
            switch (side)
            {
                case 0: return FaceFront;
                case 1: return FaceWest;
                case 3: return FaceEast;
                case 2: return FaceHidden;
                default: return FaceNone;
            }
        }

        /// <summary>A painter can't be seen to have painted the far side of a wall, so nobody chooses it.</summary>
        public static bool SidePaintable(int side) { return side == 0 || side == 1 || side == 3; }

        /// <summary>A wall seen edge-on: the camera shows only the strip of its top, and a mark there is drawn turned along it.</summary>
        public static bool EdgeOn(int face) { return face == FaceEast || face == FaceWest; }

        /// <summary>Can this drawing go on a wall seen edge-on and still read? Turned along the strip, letters and strokes read as a tag or a
        /// tally on its side; a picture (a fist, a face, a sigil, a poster, someone's head) becomes a blot. Option D's "a side face stays a
        /// scrap": a scrap, not a smear. Live pass 14: a third of Ashgate's marks were on such walls, and a fist, a mockery and a memorial
        /// each came out as a red or green blot that read at play zoom as blood or mould. edgeOn from the def: -1 by form, 0 never, 1 always.</summary>
        public static bool ReadsEdgeOn(GraffitiForm form, int edgeOn, bool hasSubject)
        {
            if (edgeOn >= 0) return edgeOn > 0;
            if (hasSubject) return false;
            return form == GraffitiForm.Tag || form == GraffitiForm.ThrowUp || form == GraffitiForm.Scrawl;
        }

        /// <summary>Chance a calm hand picks a whole front face over a side's sliver when it has both within reach.</summary>
        public const float FrontFaceBias = 0.85f;

        /// <summary>The widest mark a face may carry: a side face is a sliver, three cells of piece would be a stripe.</summary>
        public static float MaxWidthOnFace(int face) { return face == FaceFront ? float.MaxValue : 2f; }

        /// <summary>Where the walk along a wall goes for each cell of `s`, the painter's right: x, z.</summary>
        public static void AlongOf(int face, out int dx, out int dz)
        {
            dx = face == FaceFront ? 1 : 0;
            dz = face == FaceEast ? 1 : (face == FaceWest ? -1 : 0);
        }

        /// <summary>Does a wall cell with these links show this face?</summary>
        public static bool FaceExists(int links, int face)
        {
            if (links < 0) return false;
            switch (face)
            {
                case FaceFront: return (links & LinkS) == 0;
                case FaceEast: return (links & LinkE) == 0;
                case FaceWest: return (links & LinkW) == 0;
                default: return false;
            }
        }

        /// <summary>The face's outline in cell coordinates (x east, z north, 0..1), convex and counter-clockwise; null if not shown.</summary>
        public static List<RM_PlaneVert> FacePoly(int links, int face, float crease, float sideW)
        {
            if (!FaceExists(links, face)) return null;
            var p = new List<RM_PlaneVert>(4);
            if (face == FaceFront)
            {
                bool w = (links & LinkW) != 0, e = (links & LinkE) != 0;
                p.Add(new RM_PlaneVert(w ? 0f : RimX, RimZ));
                p.Add(new RM_PlaneVert(e ? 1f : 1f - RimX, RimZ));
                p.Add(new RM_PlaneVert(e ? 1f : 1f - sideW, crease));
                p.Add(new RM_PlaneVert(w ? 0f : sideW, crease));
                return p;
            }
            bool south = (links & LinkS) != 0;
            float top = (links & LinkN) != 0 ? 1f : 1f - RimX - RimZ;
            float footOut = south ? 0f : RimZ, footIn = south ? 0f : crease;
            if (face == FaceEast)
            {
                p.Add(new RM_PlaneVert(1f - RimX, footOut));
                p.Add(new RM_PlaneVert(1f - RimX, top));
                p.Add(new RM_PlaneVert(1f - sideW, top));
                p.Add(new RM_PlaneVert(1f - sideW, footIn));
            }
            else
            {
                p.Add(new RM_PlaneVert(sideW, footIn));
                p.Add(new RM_PlaneVert(sideW, top));
                p.Add(new RM_PlaneVert(RimX, top));
                p.Add(new RM_PlaneVert(RimX, footOut));
            }
            return p;
        }

        /// <summary>The wall's plane (s along the wall to the painter's right from the anchor cell's centre, t up from the wall's foot,
        /// both in world cells) -> screen cell coordinates relative to the anchor cell.</summary>
        public static void PlaneToCell(int face, float s, float t, float crease, float sideW, out float x, out float z)
        {
            if (face == FaceFront)
            {
                x = 0.5f + s;
                z = RimZ + t * (crease - RimZ) / WallWorldHeight;
            }
            else if (face == FaceEast)
            {
                x = 1f - RimX - t * (sideW - RimX) / WallWorldHeight;
                z = 0.5f + s;
            }
            else
            {
                x = RimX + t * (sideW - RimX) / WallWorldHeight;
                z = 0.5f - s;
            }
        }

        /// <summary>Sutherland-Hodgman: `subject` clipped to the convex counter-clockwise `edge`, keeping u and v interpolated.</summary>
        public static List<RM_PlaneVert> ClipConvex(List<RM_PlaneVert> subject, List<RM_PlaneVert> edge)
        {
            List<RM_PlaneVert> output = subject;
            for (int i = 0; i < edge.Count && output.Count > 0; i++)
            {
                RM_PlaneVert a = edge[i], b = edge[(i + 1) % edge.Count];
                List<RM_PlaneVert> input = output;
                output = new List<RM_PlaneVert>(input.Count + 2);
                for (int j = 0; j < input.Count; j++)
                {
                    RM_PlaneVert p = input[j], q = input[(j + input.Count - 1) % input.Count];
                    float sp = (b.x - a.x) * (p.z - a.z) - (b.z - a.z) * (p.x - a.x);
                    float sq = (b.x - a.x) * (q.z - a.z) - (b.z - a.z) * (q.x - a.x);
                    if ((sp >= 0f) != (sq >= 0f))
                    {
                        output.Add(RM_PlaneVert.Lerp(q, p, sq / (sq - sp)));
                    }
                    if (sp >= 0f)
                    {
                        output.Add(p);
                    }
                }
            }
            return output;
        }

        /// <summary>The top of a wall cell in cell coordinates, convex and counter-clockwise: above the crease (the whole depth where
        /// no front shows), inside the side faces, to the far edge where the wall runs on north. Null with no wall.</summary>
        public static List<RM_PlaneVert> TopPoly(int links, float crease, float sideW)
        {
            if (links < 0) return null;
            float x0 = (links & LinkW) != 0 ? 0f : sideW;
            float x1 = (links & LinkE) != 0 ? 1f : 1f - sideW;
            float z0 = (links & LinkS) != 0 ? 0f : crease;
            float z1 = (links & LinkN) != 0 ? 1f : 1f - RimX - RimZ;
            return new List<RM_PlaneVert> { new RM_PlaneVert(x0, z0), new RM_PlaneVert(x1, z0), new RM_PlaneVert(x1, z1), new RM_PlaneVert(x0, z1) };
        }

        /// <summary>How high a mark can reach in world cells: its whole face, then the top up to the lip. A side face is a bevel the camera
        /// sees almost edge-on, so a mark there is painted high, over the edge, and carried most of the way across the top: that is the
        /// only way it reads (owner, 2026-11-07: "A side face stays a scrap unless you find better"; measured offline and live, a side
        /// mark kept to its bevel and half the cap was about 20 px across at play zoom, carried across the top about 38).</summary>
        public static float ClimbMax(int face, float crease, float sideW)
        {
            float over = face == FaceFront ? 1f - RimX - RimZ - TopLip - crease : 1f - 2f * sideW - SideTopLip;
            return WallWorldHeight + over / TopRate;
        }

        /// <summary>Of a side face's mark, this much (world cells) is on the bevel; the rest is on the top. Bare top a side mark leaves at the far edge.</summary>
        public const float SideFaceShare = 0.22f, SideTopLip = 0.05f;

        /// <summary>The lowest a mark's paint starts on this face, world cells up from the foot.</summary>
        public static float FootOf(int face) { return face == FaceFront ? MarkFoot : WallWorldHeight - SideFaceShare; }

        /// <summary>The wall's plane -> screen cell coordinates: below the crease on the foreshortened face (PlaneToCell), above it on the top.</summary>
        public static void BentToCell(int face, float s, float t, float crease, float sideW, out float x, out float z)
        {
            if (t <= WallWorldHeight)
            {
                PlaneToCell(face, s, t, crease, sideW, out x, out z);
                return;
            }
            float over = (t - WallWorldHeight) * TopRate;
            if (face == FaceFront) { x = 0.5f + s; z = crease + over; }
            else if (face == FaceEast) { x = 1f - sideW - over; z = 0.5f + s; }
            else { x = sideW + over; z = 0.5f - s; }
        }

        /// <summary>Where a mark's middle sits on the wall's plane (world cells up from the foot) for its size and hand. A sigil's emblem and
        /// a caricature's head are placed against this so they stay inside their frame.</summary>
        public static float MarkCenterT(int face, float crease, float sideW, float width, float height, float slope, float lift)
        {
            float room = Math.Abs(slope) * width / 2f;
            float top = ClimbMax(face, crease, sideW);
            float foot = FootOf(face);
            float hh = Math.Min(height, top - foot - 2f * room);
            return foot + room + hh / 2f + (top - foot - hh - 2f * room) * lift;
        }

        /// <summary>One mark laid in its wall's plane, bent at the crease onto the wall's top, and cut to what the wall shows, cell by cell.
        /// `linksAt(k)` gives the links of the wall k cells along from the anchor (negative for no wall). The walk stops at the first cell
        /// without this face, so a corner, door or wall end ends the mark there, on the face and on the top alike. Polygon coordinates are
        /// relative to the anchor cell's south-west corner. `slope` shears the baseline (rise per cell along the wall): the hand's tilt,
        /// which leaves every run hanging straight down. `centerT` places the middle of the mark: negative for the hand's own lift.</summary>
        public static List<RM_MarkPiece> MarkPieces(Func<int, int> linksAt, int face, float crease, float sideW, float width, float height, float slide, float slope, float lift, bool flip, float centerT = -1f)
        {
            var pieces = new List<RM_MarkPiece>();
            if (face != FaceFront && face != FaceEast && face != FaceWest) return pieces;
            AlongOf(face, out int ax, out int az);
            float halfW = width / 2f;
            float room = Math.Abs(slope) * halfW;
            float top = ClimbMax(face, crease, sideW);
            float hh = Math.Min(height, top - FootOf(face) - 2f * room);
            float tc = centerT >= 0f ? centerT : MarkCenterT(face, crease, sideW, width, height, slope, lift);
            // In the plane: x = s, z = t. Cut at the crease there, where the map from plane to screen bends.
            var plane = new List<RM_PlaneVert>(4);
            foreach (float[] c in QuadCorners)
            {
                float s = slide + (c[0] - 0.5f) * width;
                plane.Add(new RM_PlaneVert(s, tc + (c[1] - 0.5f) * hh + slope * (s - slide), flip ? 1f - c[0] : c[0], c[1]));
            }
            List<RM_PlaneVert> below = ToScreen(ClipT(plane, WallWorldHeight, true), face, crease, sideW);
            List<RM_PlaneVert> above = ToScreen(ClipT(plane, WallWorldHeight, false), face, crease, sideW);
            foreach (int dir in new[] { 1, -1 })
            {
                for (int k = dir > 0 ? 0 : -1; Math.Abs(k) <= MaxReachCells; k += dir)
                {
                    float s0 = k - 0.5f;
                    if (s0 + 1f < slide - halfW || s0 > slide + halfW) break;
                    int links = linksAt(k);
                    List<RM_PlaneVert> edge = FacePoly(links, face, crease, sideW);
                    if (edge == null) break;
                    if (below.Count >= 3)
                    {
                        List<RM_PlaneVert> poly = ClipConvex(below, Shifted(edge, ax * k, az * k));
                        if (poly.Count >= 3) pieces.Add(new RM_MarkPiece(k, poly));
                    }
                    if (above.Count >= 3)
                    {
                        List<RM_PlaneVert> poly = ClipConvex(above, Shifted(TopPoly(links, crease, sideW), ax * k, az * k));
                        if (poly.Count >= 3) pieces.Add(new RM_MarkPiece(k, poly, true));
                    }
                }
            }
            return pieces;
        }

        private static List<RM_PlaneVert> Shifted(List<RM_PlaneVert> poly, int dx, int dz)
        {
            var shifted = new List<RM_PlaneVert>(poly.Count);
            foreach (RM_PlaneVert e in poly) shifted.Add(new RM_PlaneVert(e.x + dx, e.z + dz));
            return shifted;
        }

        /// <summary>A polygon whose z is the plane's t, cut at t = limit: the part below it, or the part above it.</summary>
        private static List<RM_PlaneVert> ClipT(List<RM_PlaneVert> poly, float limit, bool keepBelow)
        {
            var output = new List<RM_PlaneVert>(poly.Count + 2);
            for (int j = 0; j < poly.Count; j++)
            {
                RM_PlaneVert p = poly[j], q = poly[(j + poly.Count - 1) % poly.Count];
                bool pIn = keepBelow ? p.z <= limit : p.z > limit;
                bool qIn = keepBelow ? q.z <= limit : q.z > limit;
                if (pIn != qIn) output.Add(RM_PlaneVert.Lerp(q, p, (limit - q.z) / (p.z - q.z)));
                if (pIn) output.Add(p);
            }
            return output;
        }

        /// <summary>Plane polygon -> screen, kept counter-clockwise: a side face runs its plane mirrored.</summary>
        private static List<RM_PlaneVert> ToScreen(List<RM_PlaneVert> poly, int face, float crease, float sideW)
        {
            var output = new List<RM_PlaneVert>(poly.Count);
            float area = 0f;
            foreach (RM_PlaneVert v in poly)
            {
                // A point exactly on the crease belongs to either map: both give the same screen point.
                BentToCell(face, v.x, v.z, crease, sideW, out float x, out float z);
                output.Add(new RM_PlaneVert(x, z, v.u, v.v));
            }
            for (int i = 0; i < output.Count; i++)
            {
                RM_PlaneVert a = output[i], b = output[(i + 1) % output.Count];
                area += a.x * b.z - b.x * a.z;
            }
            if (area < 0f) output.Reverse();
            return output;
        }

        private const int MaxReachCells = 5;
        private static readonly float[][] QuadCorners = { new[] { 0f, 0f }, new[] { 1f, 0f }, new[] { 1f, 1f }, new[] { 0f, 1f } };

        /// <summary>Where a profile running from a tile's cap toward its face crosses two thirds of the way from the cap's value to the
        /// face's own (face taken as the median of [faceLo, faceHi)): the crease, not the cap's soft border or the tile's outline.
        /// Index of the crossing, -1 with none.</summary>
        public static int CreaseCrossing(float[] profile, int capAt, int faceLo, int faceHi)
        {
            int n = faceHi - faceLo;
            if (n <= 0 || capAt < 0 || capAt >= profile.Length || faceLo < 0 || faceHi > profile.Length) return -1;
            var sorted = new float[n];
            Array.Copy(profile, faceLo, sorted, 0, n);
            Array.Sort(sorted);
            float face = sorted[n / 2], cap = profile[capAt];
            for (int i = capAt; i < profile.Length; i++)
            {
                if (Math.Abs(profile[i] - cap) >= Math.Abs(face - cap) * 2f / 3f && Math.Abs(face - cap) > 4f) return i;
            }
            return -1;
        }

        /// <summary>A measured crease or side width, or the default if it's outside anything a wall draws (rock's torn edge and odd atlases).</summary>
        public static float SaneOr(float measured, float lo, float hi, float fallback)
        {
            return measured >= lo && measured <= hi ? measured : (measured > hi ? hi : fallback);
        }

        /// <summary>
        /// Every hand is different: from a mark's id, a stable baseline slope, size, slide along the wall, height on the face and
        /// which way round. A wide mark stays nearly level and at full size (it is planned, and it needs its wall).
        /// </summary>
        public static void HandOf(int id, float width, out float slope, out float scale, out float slide, out float lift, out bool flip)
        {
            uint h = (uint)id * 2654435761u;
            float a = ((h >> 4) & 255) / 255f, b = ((h >> 12) & 255) / 255f, c = ((h >> 20) & 255) / 255f;
            uint h2 = h * 2654435761u + 40503u;
            bool wide = width > 1.01f;
            slope = (a - 0.5f) * (wide ? 0.05f : 0.12f);
            scale = wide ? 1f : 0.82f + 0.18f * b;
            slide = wide ? 0f : (c - 0.5f) * 0.2f;
            lift = ((h2 >> 6) & 255) / 255f;
            flip = ((h2 >> 17) & 1) == 1;
        }

        /// <summary>Pigments a tag can be written in (multiplied onto a pale drawing): dull colours a colony could mix, none neon.</summary>
        public static readonly RM_Rgb[] Pigments =
        {
            new RM_Rgb(0.74f, 0.27f, 0.20f), new RM_Rgb(0.82f, 0.60f, 0.27f), new RM_Rgb(0.92f, 0.90f, 0.83f), new RM_Rgb(0.20f, 0.19f, 0.19f),
            new RM_Rgb(0.42f, 0.52f, 0.33f), new RM_Rgb(0.36f, 0.48f, 0.58f), new RM_Rgb(0.54f, 0.37f, 0.56f), new RM_Rgb(0.86f, 0.46f, 0.22f),
        };
        public static int PigmentCount => Pigments.Length;
        public static RM_Rgb PigmentColor(int index) { return Pigments[Math.Abs(index) % Pigments.Length]; }

        /// <summary>Does this pigment stand off a wall face of this colour? By colour, not value: rust reads on grey stone as well as chalk does.</summary>
        public static bool PigmentReads(int index, float wallR, float wallG, float wallB)
        {
            RM_Rgb p = PigmentColor(index);
            float dr = p.r - wallR, dg = p.g - wallG, db = p.b - wallB;
            return dr * dr + dg * dg + db * db >= 0.09f;
        }

        /// <summary>What an inspecting player reads off a mark's Beauty, so the stat and the picture can be held side by side.</summary>
        public static string BeautyWord(float beauty)
        {
            if (beauty <= -12f) return "a filthy eyesore";
            if (beauty <= -6f) return "ugly scrawl";
            if (beauty < 0f) return "rough, but somebody meant it";
            if (beauty < 1f) return "just a mark";
            if (beauty < 6f) return "decent work";
            if (beauty < 15f) return "real craft";
            if (beauty < 25f) return "a fine piece of work";
            return "a masterpiece, on a wall";
        }

        /// <summary>Picks from `count` choices one that `taken` doesn't hold, as evenly as a roll in 0..1 goes; with all taken, any.</summary>
        public static int PickFree(int count, ICollection<int> taken, float roll)
        {
            if (count <= 0) return 0;
            var free = new List<int>(count);
            for (int i = 0; i < count; i++)
            {
                if (!taken.Contains(i)) free.Add(i);
            }
            if (free.Count == 0) return Math.Min(count - 1, (int)(roll * count));
            return free[Math.Min(free.Count - 1, (int)(roll * free.Count))];
        }

        /// <summary>The pool's weight for a mark already on this stretch of wall: posters and tags rarely repeat side by side.</summary>
        public const float NearbySameMarkWeight = 0.08f;

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

        // ---------------------------------------------------------------- what a mark does between people
        // Owner, 2026-11-07: "did you test the social implications of the mod? It's more than just art display." Every decision the social
        // layer takes is here as a table, so it can be fuzzed without the game. GraffitiSocial.cs reads the pawns and acts on the answers.

        public const int SightRadiusSq = 49;
        /// <summary>Owner, card 2026-11-07: "Seeing the same mark repeatedly SHOULD repeatedly affect you, but no more than once per day."
        /// A pawn reads a standing mark again after a day. Mood comes again; opinion and grudges only came the first time.</summary>
        public const int ReadAgainTicks = 60000;
        /// <summary>A mark read again is an old sting, not a new one: its mood comes back at this share of the first reading. A memory
        /// still running at full strength is left alone (GraffitiTemperament.Give keeps the stronger), so a standing mockery is a
        /// steady reminder once the shock has worn off, not a permanent first-day blow.</summary>
        public const float RereadFactor = 0.6f;
        /// <summary>A pawn answers one mark at a time, and has cooled off this long before taking on another.</summary>
        public const int AnswerCooldownTicks = 60000;
        /// <summary>A grudge not answered in this long is borne.</summary>
        public const int GrudgeExpiryTicks = 120000;

        public const int EnemyOpinion = -15, FriendOpinion = 20, CloseOpinion = 50, HatedOpinion = -30, HeldDearOpinion = 40;

        /// <summary>What a pawn's hand wants to say when it picks up the brush.</summary>
        public static RM_Meaning WantsToPaint(bool spree, bool kind, int worstOpinion, bool hasEnemy, bool hasBeloved, bool hasMourned, float roll)
        {
            float mock = 0f, mourn = 0f, love = 0f;
            if (hasEnemy && worstOpinion <= EnemyOpinion && !kind)
            {
                mock = spree ? 0.65f : (worstOpinion <= HatedOpinion ? 0.4f : 0.2f);
            }
            // Live 2026-11-07: at 0.35 Lark, whose lover had died, painted once in two days and it was tallies. Grief that reaches for the
            // brush mostly says the one thing.
            if (hasMourned) mourn = spree ? 0.15f : 0.6f;
            if (hasBeloved && !spree) love = 0.2f;
            if (roll < mock) return RM_Meaning.Mockery;
            if (roll < mock + mourn) return RM_Meaning.Memorial;
            if (roll < mock + mourn + love) return RM_Meaning.Tribute;
            return RM_Meaning.None;
        }

        /// <summary>A kind hand won't paint cruelty, ordered or not.</summary>
        public static bool RefusesToPaint(RM_Meaning meaning, bool kind) { return kind && (meaning == RM_Meaning.Mockery || meaning == RM_Meaning.Insult); }

        /// <summary>What this viewer feels on reading this mark. First match wins, top to bottom.</summary>
        public static RM_Reaction ReactionOf(RM_Meaning meaning, RM_Viewer v)
        {
            if (v.isMaker) return RM_Reaction.None;
            if (v.hostileMaker)
            {
                return v.hot ? RM_Reaction.Defiant : RM_Reaction.Uneasy;
            }
            switch (meaning)
            {
                case RM_Meaning.Mockery:
                    if (v.isSubject) return v.kind ? RM_Reaction.ShrugsOff : RM_Reaction.Humiliated;
                    if (v.loverOfSubject || v.opinionOfSubject >= FriendOpinion) return RM_Reaction.FriendDefends;
                    if (v.opinionOfSubject <= EnemyOpinion) return RM_Reaction.Gleeful;
                    if (v.kind) return RM_Reaction.Disapproves;
                    return RM_Reaction.LostFace;
                case RM_Meaning.Tribute:
                    if (v.isSubject) return RM_Reaction.Honored;
                    if (v.loverOfMaker) return RM_Reaction.Jealous;
                    if (v.opinionOfSubject <= HatedOpinion) return RM_Reaction.Scoffs;
                    return v.opinionOfSubject >= FriendOpinion ? RM_Reaction.Warmed : RM_Reaction.None;
                case RM_Meaning.Memorial:
                    if (v.psychopath) return RM_Reaction.None;
                    return v.loverOfSubject || v.opinionOfSubject >= FriendOpinion ? RM_Reaction.Mourning : RM_Reaction.None;
                case RM_Meaning.Jest:
                    if (v.psychopath || v.opinionOfMaker <= HatedOpinion) return RM_Reaction.None;
                    return RM_Reaction.Amused;
                case RM_Meaning.Beauty:
                    return v.psychopath ? RM_Reaction.None : RM_Reaction.Moved;
                case RM_Meaning.Devotion:
                    if (!v.hasIdeo || !v.makerHasIdeo) return RM_Reaction.None;
                    return v.sameIdeoAsMaker ? RM_Reaction.Uplifted : RM_Reaction.Offended;
                case RM_Meaning.Insult:
                    return v.kind ? RM_Reaction.Disapproves : RM_Reaction.Gleeful;
                default:
                    if (!v.ownFaction) return RM_Reaction.None;
                    if (v.opinionOfMaker <= HatedOpinion) return RM_Reaction.RivalTag;
                    return v.loverOfMaker || v.opinionOfMaker >= HeldDearOpinion ? RM_Reaction.FriendTag : RM_Reaction.None;
            }
        }

        /// <summary>What they do about it. The roll is in 0..1. A hot head goes for the painter; a good hand answers in paint; anyone can wipe a
        /// wall. The bands don't overlap, so a skilled hothead can still answer in paint (the first version's confront band hid the reply).
        /// `lean` is the temperament table's: a Kind or Neurotic hand would rather scrub than shout, a tortured artist answers in paint,
        /// and Nothing is somebody who lets it go.</summary>
        public static RM_Answer AnswerOf(RM_Reaction reaction, bool hot, bool canFight, bool makerHere, bool goodHand, float roll, RM_Lean lean = RM_Lean.None)
        {
            RM_Answer a = BaseAnswer(reaction, hot, canFight && makerHere, goodHand && makerHere, roll);
            if (a == RM_Answer.None || lean == RM_Lean.None) return a;
            if (lean == RM_Lean.Nothing) return RM_Answer.None;
            if (lean == RM_Lean.Scrub && (a == RM_Answer.Confront || a == RM_Answer.Deface || a == RM_Answer.Reply)) return ScrubbableReaction(reaction) ? RM_Answer.Scrub : RM_Answer.None;
            if (lean == RM_Lean.Reply && goodHand && makerHere && (a == RM_Answer.Confront || a == RM_Answer.Deface)) return RM_Answer.Reply;
            return a;
        }

        private static RM_Answer BaseAnswer(RM_Reaction reaction, bool hot, bool confront, bool reply, float roll)
        {
            switch (reaction)
            {
                case RM_Reaction.Humiliated:
                    if (hot && confront && roll < 0.4f) return RM_Answer.Confront;
                    if (reply && roll < 0.65f) return RM_Answer.Reply;
                    if (!hot && confront && roll < 0.2f) return RM_Answer.Confront;
                    return roll < 0.85f ? RM_Answer.Scrub : RM_Answer.Deface;
                case RM_Reaction.FriendDefends:
                    if (hot && confront && roll < 0.25f) return RM_Answer.Confront;
                    return roll < 0.45f ? RM_Answer.Scrub : (roll < 0.65f ? RM_Answer.Deface : RM_Answer.None);
                case RM_Reaction.Defiant:
                    return roll < 0.6f ? RM_Answer.Deface : RM_Answer.Scrub;
                case RM_Reaction.Uneasy:
                    return roll < 0.2f ? RM_Answer.Scrub : RM_Answer.None;
                case RM_Reaction.RivalTag:
                    if (hot && confront && roll < 0.2f) return RM_Answer.Confront;
                    return roll < 0.4f ? RM_Answer.Deface : RM_Answer.None;
                case RM_Reaction.WorkDestroyed:
                    // Nothing left to cross out: the work is under someone else's paint.
                    if (hot && confront && roll < 0.3f) return RM_Answer.Confront;
                    if (reply && roll < 0.6f) return RM_Answer.Reply;
                    return RM_Answer.None;
                case RM_Reaction.Offended:
                    return hot && roll < 0.35f ? RM_Answer.Deface : RM_Answer.None;
                default:
                    return RM_Answer.None;
            }
        }

        /// <summary>Is there still a mark to wipe? Work painted over is gone already.</summary>
        private static bool ScrubbableReaction(RM_Reaction reaction) { return reaction != RM_Reaction.WorkDestroyed; }

        /// <summary>Owner's pick, 2026-11-07: an answer waits its turn. Hungry, tired, with enemies about or the target across the map, it waits.</summary>
        public static bool AnswerWaits(bool hungry, bool tired, bool enemiesNear, float distance)
        {
            return hungry || tired || enemiesNear || distance > AnswerReach;
        }

        /// <summary>Cells a pawn will walk to answer a mark.</summary>
        public const float AnswerReach = 45f;
        /// <summary>An answer that couldn't be started (blocked, unreachable) is tried again after this, not dropped.</summary>
        public const int AnswerRetryTicks = 2500;

        // ---------------------------------------------------------------- temperament (personality pass, owner by card 2026-11-07)

        /// <summary>Owner's pick, "Scale it with temper": the chance a confrontation over a mark comes to blows. `vanilla` is the confronter's own
        /// chance of a fight over an insult, the game's whole formula (his opinion of the painter, his traits, capacities, age gap, both pawns'
        /// genes); `temper` is the table's column for him. Three insults' worth, because a named slur on a wall is more than an insult.</summary>
        public static float ConfrontFightChance(float vanilla, float temper)
        {
            float t = Clamp(temper, 0f, 4f);
            float c = Clamp(vanilla, 0f, 1f);
            return Math.Min(ConfrontFightCap, ConfrontInsults * c * t);
        }

        public const float ConfrontInsults = 3f, ConfrontFightCap = 0.85f;
        /// <summary>At most one fight the walls caused in this long, for the whole game: a confrontation always happens as a row, a fight is rare.</summary>
        public const int FightCooldownTicks = 15 * 60000;

        /// <summary>A painter's next mockery of the same person waits this long, whatever brings it on (GameComponent_Graffiti.MockeryDue).</summary>
        public const int MockeryCooldownTicks = 6 * 60000;
        /// <summary>At most one Graffiti break (spree or compulsive cleaning) in this long, for the whole game.</summary>
        public const int BreakCooldownTicks = 15 * 60000;

        /// <summary>A hot head: whose temper, times the game's own social-fight factors on his traits and genes, is half again an ordinary man's.</summary>
        public static bool IsHot(float temper, float vanillaFactors) { return temper * vanillaFactors >= 1.5f; }

        /// <summary>One person's temperament, multiplied up from the table's rows (Defs/TemperamentDefs_Graffiti.xml) and clamped.</summary>
        public static RM_Temper Combine(IList<RM_Temper> rows)
        {
            RM_Temper t = RM_Temper.Plain;
            foreach (RM_Temper r in rows)
            {
                t.numb |= r.numb;
                t.bad *= r.bad; t.good *= r.good; t.fine *= r.fine; t.ugly *= r.ugly;
                t.temper *= r.temper; t.paint *= r.paint; t.offended *= r.offended;
                if (r.neat > t.neat) t.neat = r.neat;
                if (r.lean != RM_Lean.None) t.lean = r.lean;
            }
            t.bad = Clamp(t.bad, 0f, 1.5f); t.good = Clamp(t.good, 0f, 1.5f); t.fine = Clamp(t.fine, 0f, 1.5f); t.ugly = Clamp(t.ugly, 0f, 1.5f);
            t.temper = Clamp(t.temper, 0f, 4f); t.paint = Clamp(t.paint, 0f, 2f); t.offended = Clamp(t.offended, 0f, 1.5f);
            if (t.numb)
            {
                t.bad = t.good = t.fine = t.ugly = t.offended = 0f;
                t.lean = RM_Lean.Nothing;
                t.neat = 0;
            }
            return t;
        }

        /// <summary>A memory's strength after the pawn's own budget for Graffiti feelings of that sign: `already` is what Graffiti memories of that
        /// sign already add up to (absolute), `offset` the new one at full strength (absolute), `budget` the most they may add up to. Positives
        /// never pay for negatives. Returns the factor (0..1) the new memory keeps.</summary>
        public static float FitBudget(float already, float offset, float budget)
        {
            if (offset <= 0f) return 1f;
            float room = budget - already;
            if (room <= 0.05f) return 0f;
            return room >= offset ? 1f : room / offset;
        }

        /// <summary>Mood budgets (each times the pawn's bad or good): what Graffiti memories may add up to; the named victim of a mockery more.</summary>
        public const float BadMoodBudget = 8f, VictimMoodBudget = 12f, GoodMoodBudget = 6f;
        /// <summary>Inside the good budget, what walls about nobody in particular may add up to: a funny doodle, good work, our sign, a friend's
        /// tag, having left a mark. Owner, card 2026-11-07, after the +4 to +6 most pawns took from ordinary wall art: "Graffiti is flavour, not a
        /// mood engine ... about +2 to +3 total and cap it." The cap is absolute: a sensitive pawn feels each mark more and so reaches it sooner,
        /// but never passes it; a cold one stops lower (AmbientBudget). A tribute painted to you, a memorial and a mockery are stories about
        /// someone, not ordinary wall art, and stand outside it under the good budget.</summary>
        public const float AmbientMoodBudget = 3f;

        /// <summary>The ambient budget for a pawn whose good is `good`: times the pawn's good up to the owner's absolute +3.</summary>
        public static float AmbientBudget(float good)
        {
            float b = AmbientMoodBudget * (good > 0.5f ? good : 0.5f);
            return b < AmbientMoodBudget ? b : AmbientMoodBudget;
        }
        /// <summary>A memorial softens grief and never turns it into a gain (owner, card 2026-11-07): everything the walls give a pawn about one
        /// dead pawn adds up to at most this share of the grief that pawn still feels for them.</summary>
        public const float GriefEaseShare = 0.5f;

        /// <summary>How much of `raw` (a grief-easing memory at full strength) stands, when the grief it eases is `grief` (absolute) and the eases
        /// before it about the same dead pawn already take `before`.</summary>
        public static float EaseShare(float grief, float raw, float before)
        {
            float room = grief * GriefEaseShare - before;
            if (room <= 0f || raw <= 0f) return 0f;
            return raw < room ? raw : room;
        }
        /// <summary>Opinion caps for Graffiti's social memories of one pawn about another; the named victim's of the painter more.</summary>
        public const float BadOpinionCap = 30f, VictimOpinionCap = 45f, GoodOpinionCap = 30f;

        // ---------------------------------------------------------------- art skill (owner, 2026-11-07)
        // "A poor artist will paint such a bad graffiti mark that it is ugly, harms a room's beauty, and gives mood debuffs. But a highly
        // skilled artist is actually making art." Quality as the game's QualityCategory: 0 Awful .. 6 Legendary.

        public const int Awful = 0, Poor = 1, Normal = 2, Good = 3, Excellent = 4, Masterwork = 5, Legendary = 6;

        /// <summary>The most a form can be worth as art. Live 2026-11-07: a level-15 hand rolled "excellent" scratches worth +8 Beauty, which no
        /// player would believe. A tally or a scratch is a tally however good the hand; a tag can have style; a throw-up can be very good;
        /// a stencil, a poster, a sigil or a piece can be a masterwork. A scrawl is never better than poor work: it is the ugliest thing on the
        /// wall, so it is drawn smeared and muddy and its Beauty is below a tally's whoever holds the can (pass 9: a scrawl by a steady hand had
        /// been worth 0, the same as a tally, while its picture was the loudest on the wall).</summary>
        public static int CraftCeiling(GraffitiForm form)
        {
            switch (form)
            {
                case GraffitiForm.Scrawl: return Poor;
                case GraffitiForm.Glyph: return Normal;
                case GraffitiForm.Tag: return Good;
                case GraffitiForm.ThrowUp: return Excellent;
                default: return Legendary;
            }
        }

        /// <summary>How much a hand of this Artistic level favours a form when it picks what to paint: beginners tally, scratch and tag; artists
        /// paint throw-ups, stencils, posters and pieces. Multiplies the def's poolWeight.</summary>
        public static float FormAffinity(GraffitiForm form, int level)
        {
            int l = level < 0 ? 0 : (level > 20 ? 20 : level);
            switch (form)
            {
                case GraffitiForm.Glyph: return l < 8 ? 1f : 0.35f;
                case GraffitiForm.Tag: return l < 12 ? 1f : 0.6f;
                case GraffitiForm.ThrowUp: return 0.6f + 0.06f * l;
                case GraffitiForm.Stencil:
                case GraffitiForm.Paste: return 0.5f + 0.05f * l;
                case GraffitiForm.Piece: return l < 6 ? 0.1f : 0.15f * l;
                default: return 1f;
            }
        }

        /// <summary>A mark's net beauty in its cell by craft, wherever it is (Filth_Mark.GetBeauty undoes the roof's 0.3 on filth).</summary>
        public static float CraftBeauty(int quality)
        {
            switch (quality)
            {
                case Awful: return -6f;
                case Poor: return -2.5f;
                case Normal: return 0f;
                case Good: return 3f;
                case Excellent: return 8f;
                case Masterwork: return 18f;
                default: return quality > Masterwork ? 30f : -6f;
            }
        }

        /// <summary>How far a mark's meaning reaches, by craft: a clumsy insult is laughed off and a great one sticks.</summary>
        public static float CraftReach(int quality)
        {
            switch (quality)
            {
                case Awful: return 0.75f;
                case Poor: return 0.85f;
                case Normal: return 1f;
                case Good: return 1.1f;
                case Excellent: return 1.2f;
                case Masterwork: return 1.35f;
                default: return quality > Masterwork ? 1.5f : 0.75f;
            }
        }

        /// <summary>The craft thought a reader takes from it: -1 none, else the stage of RM_Graffiti_UglyMark (ugly true) or RM_Graffiti_FineArt.</summary>
        public static int CraftStage(int quality, out bool ugly)
        {
            ugly = quality <= Poor;
            if (quality == Awful) return 1;
            if (quality == Poor) return 0;
            if (quality <= Normal) return -1;
            return Math.Min(quality, Legendary) - Good;
        }

        /// <summary>How the craft shows on the wall. through: more of the wall shows through a thin, patchy coat; wobble: a shaky hand's tilt;
        /// mud: how far the pigment slides toward the muddy brown of a cheap mix.</summary>
        public static void CraftLook(int quality, out float through, out float wobble, out float mud)
        {
            switch (quality)
            {
                case Awful: through = 0.2f; wobble = 3f; mud = 0.4f; return;
                case Poor: through = 0.1f; wobble = 2f; mud = 0.2f; return;
                case Good: through = -0.04f; wobble = 0.8f; mud = 0f; return;
                case Excellent: through = -0.08f; wobble = 0.6f; mud = 0f; return;
                case Masterwork: through = -0.12f; wobble = 0.4f; mud = 0f; return;
                case Legendary: through = -0.15f; wobble = 0.3f; mud = 0f; return;
                default: through = 0f; wobble = 1f; mud = 0f; return;
            }
        }

        /// <summary>Pass 13's mud, kept only so a proof can put the old look beside the new on one wall (RM_GraffitiStage.smearOver). Live 2026-11-08:
        /// at 0.65 an awful mark's pigment went the brown of the ground, and the ugliest marks read as grime, not as paint.</summary>
        public static void CraftLookBefore(int quality, ref float mud)
        {
            if (quality == Awful) mud = 0.65f;
            else if (quality == Poor) mud = 0.35f;
        }

        /// <summary>The thin coat of a clumsy hand's first go, as a share of the paint's opacity. It lies under two coats on a face, so it shows at
        /// about twice this.</summary>
        public const float SmearAlpha = 0.28f;

        /// <summary>How far a clumsy hand slipped and went over its own mark again, off true: 0 for anyone who can paint. Live 2026-11-07: an
        /// awful piece and a legendary one side by side differed only by which drawing each was, so the owner's "a poor artist will paint
        /// such a bad graffiti mark that it is ugly" wasn't on the wall.</summary>
        public static float CraftSmear(int quality)
        {
            return quality == Awful ? 1f : quality == Poor ? 0.5f : 0f;
        }

        /// <summary>What a writer who can paint adds that a beginner doesn't: the piece's 3D block, its letters' shadow cast down and along
        /// the wall, deeper the better the hand (drop in world cells, in `steps` coats so it reads as a solid block, not a ghost); and from
        /// masterwork, the white shine glints a finished piece carries. Live, pass 11: a masterwork and a normal piece side by side differed
        /// by a little show-through, so the owner's "a highly skilled artist is actually making art" wasn't on the wall.</summary>
        public static void CraftDepth(int quality, out float drop, out int steps, out int glints)
        {
            switch (quality)
            {
                case Good: drop = 0.03f; steps = 1; glints = 0; return;
                case Excellent: drop = 0.045f; steps = 2; glints = 0; return;
                case Masterwork: drop = 0.06f; steps = 3; glints = 2; return;
                case Legendary: drop = 0.075f; steps = 3; glints = 3; return;
                default: drop = 0f; steps = 0; glints = 0; return;
            }
        }

        /// <summary>A point of the drawing (u across, v up, 0..1 of the texture) as it lies on the wall's plane: s along the wall, t up it,
        /// for the mark MarkPieces would lay with the same arguments. Lets a glint or a head be put on the paint, not beside it.</summary>
        public static void MarkPoint(int face, float crease, float sideW, float width, float height, float slide, float slope, float lift, bool flip, float u, float v, out float s, out float t)
        {
            float halfW = width / 2f;
            float room = Math.Abs(slope) * halfW;
            float top = ClimbMax(face, crease, sideW);
            float hh = Math.Min(height, top - FootOf(face) - 2f * room);
            float tc = MarkCenterT(face, crease, sideW, width, height, slope, lift);
            float c0 = flip ? 1f - u : u;
            s = slide + (c0 - 0.5f) * width;
            t = tc + (v - 0.5f) * hh + slope * (s - slide);
        }

        /// <summary>Where shine glints go on a drawing: cells of an alpha grid (cols x rows, row 0 at the bottom, values 0..1) that are solid
        /// paint with open wall right above them, the top edges of letters where a writer puts his highlights. Spread across the width, picked
        /// by seed; fewer than `n` if the drawing has fewer edges. Each point is (u, v) at the cell's middle.</summary>
        public static List<float[]> ShinePoints(float[] alpha, int cols, int rows, int n, int seed)
        {
            var found = new List<float[]>();
            if (n <= 0 || alpha == null || alpha.Length < cols * rows) return found;
            uint h = (uint)seed * 2654435761u + 977u;
            for (int band = 0; band < n; band++)
            {
                int c0 = cols * band / n, c1 = cols * (band + 1) / n;
                var candidates = new List<int>();
                for (int c = Math.Max(c0, 1); c < Math.Min(c1, cols - 1); c++)
                {
                    for (int r = rows / 3; r < rows - 2; r++)
                    {
                        float here = alpha[r * cols + c];
                        float below = alpha[(r - 1) * cols + c];
                        float left = alpha[r * cols + c - 1], right = alpha[r * cols + c + 1];
                        float above = alpha[(r + 2) * cols + c];
                        if (here > 0.6f && below > 0.6f && left > 0.45f && right > 0.45f && above < 0.25f) candidates.Add(r * cols + c);
                    }
                }
                if (candidates.Count == 0) continue;
                h = h * 2654435761u + 40503u;
                int pick = candidates[(int)((h >> 8) % (uint)candidates.Count)];
                found.Add(new[] { (pick % cols + 0.5f) / cols, (pick / cols + 0.5f) / rows });
            }
            return found;
        }

        // ---------------------------------------------------------------- weather

        /// <summary>Days a mark lasts on its wall before it has weathered away. Live, pass 12: Ashgate's walls reached their caps on day 11 and
        /// nobody painted again for the next three and a half days, because nothing but the player or an answer ever took our own marks down.
        /// Paint weathers: out in the rain twice as fast, paper posters fastest, a gouge slowest, a good writer's paint longer than a beginner's.
        /// The owner's later Luminous Pigments make a mark permanent (Filth_Mark.permanent), so ordinary paint isn't. Each mark +-25% by id.</summary>
        public static float WeatherDays(GraffitiForm form, int craft, bool outdoors, int id)
        {
            float days = outdoors ? 22f : 44f;
            if (form == GraffitiForm.Paste) days *= 0.5f;
            else if (form == GraffitiForm.Stencil) days *= 1.3f;
            else if (form == GraffitiForm.Scrawl) days *= 0.8f;
            days *= craft <= Awful ? 0.75f : craft == Poor ? 0.85f : craft == Normal ? 1f : craft == Good ? 1.1f : craft == Excellent ? 1.2f : 1.35f;
            uint h = (uint)id * 2246822519u + 3266489917u;
            return days * (0.75f + 0.5f * ((h >> 9) & 1023) / 1023f);
        }

        /// <summary>How far gone a mark is, 0 fresh to 1 gone: nothing shows for the first 60% of its life, then it fades steadily.</summary>
        public static float WeatherFade(float ageDays, float lifeDays)
        {
            if (lifeDays <= 0f) return 0f;
            float f = (ageDays / lifeDays - 0.6f) / 0.4f;
            return f < 0f ? 0f : (f > 1f ? 1f : f);
        }

        /// <summary>The fade as a few steps, so a mark's mesh is rebuilt a handful of times in its life, not every check.</summary>
        public static int WeatherStep(float fade) { return fade <= 0f ? 0 : (int)Math.Ceiling(fade * 4f); }

        /// <summary>The muddy brown a cheap, overmixed paint goes.</summary>
        public static readonly RM_Rgb Mud = new RM_Rgb(0.36f, 0.30f, 0.24f);

        // ---------------------------------------------------------------- visitors

        /// <summary>A visit, for goodwill: one faction's party on the map within this long of its first read is one visit.</summary>
        public const int VisitTicks = 3 * 60000;
        /// <summary>Most goodwill one visit can lose or gain off the walls.</summary>
        public const int VisitLossCap = 12, VisitGainCap = 3;

        /// <summary>What a visitor's read may still move, given what this visit has already moved: the delta clipped to the caps.</summary>
        public static int VisitCharge(int delta, int lostSoFar, int gainedSoFar)
        {
            if (delta < 0) return -Math.Min(-delta, Math.Max(0, VisitLossCap - lostSoFar));
            if (delta > 0) return Math.Min(delta, Math.Max(0, VisitGainCap - gainedSoFar));
            return 0;
        }

        private static float Clamp(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

        /// <summary>Is this reaction said out loud, so the player's told? The ones that start something between people.</summary>
        public static bool Announces(RM_Reaction reaction)
        {
            return reaction == RM_Reaction.Humiliated || reaction == RM_Reaction.Honored || reaction == RM_Reaction.Mourning || reaction == RM_Reaction.Jealous || reaction == RM_Reaction.WorkDestroyed;
        }

        /// <summary>Stage of the colony's unease at enemy marks standing on its walls: none, then -1, -2, -4 by how many.</summary>
        public static int TerritoryStage(int standing) { return standing <= 0 ? -1 : (standing <= 2 ? 0 : (standing <= 5 ? 1 : 2)); }

        /// <summary>A crossed-out mark has lost its power: only its maker still cares.</summary>
        public static bool StillSpeaks(bool defaced, bool viewerIsMaker) { return !defaced || viewerIsMaker; }

        /// <summary>A visitor reads a mark on a host's wall: the faction's goodwill moves by this much. The named insult is the lever the player pulls on purpose.</summary>
        public static int GoodwillOf(RM_Meaning meaning, bool namesViewersFaction, bool isTaunt, bool sameIdeo)
        {
            // An insult is about the faction it names: live pass 13, a Berro Pact visitor lost goodwill over the insult to Hatlencaora,
            // through the taunt rule below. Someone else's insult is no business of theirs.
            if (meaning == RM_Meaning.Insult) return namesViewersFaction ? -12 : 0;
            if (isTaunt) return -1;
            if (meaning == RM_Meaning.Devotion && sameIdeo) return 1;
            return 0;
        }

        /// <summary>A painter's own tag: the same drawing and pigment each time, from the pawn's id, so a wall shows whose hand is whose.</summary>
        public static int HandChoice(int id, int count, int salt)
        {
            if (count <= 0) return 0;
            uint h = ((uint)id + (uint)salt * 40503u) * 2654435761u;
            return (int)((h >> 11) % (uint)count);
        }
    }
}
