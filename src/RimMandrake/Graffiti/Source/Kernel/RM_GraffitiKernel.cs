// Verse-free kernel of Graffiti: the weighted mark pick and its three eligibility gates, the relation-keyed reaction priority, the
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

    /// <summary>The part of a mark on one wall cell, k cells along from its anchor: a convex counter-clockwise polygon.</summary>
    public struct RM_MarkPiece
    {
        public int k;
        public List<RM_PlaneVert> poly;
        public RM_MarkPiece(int k, List<RM_PlaneVert> poly) { this.k = k; this.poly = poly; }
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

        /// <summary>Has a room its share of a calm painter's marks? One, and one more for every 15 cells of floor.</summary>
        public static bool RoomHoldsEnough(int marks, int floorCells) { return marks >= 1 + floorCells / 15; }

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
        /// <summary>A plain painted mark fills this much of the face's height at full size.</summary>
        public const float MarkFillOfFace = 0.92f;
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

        /// <summary>One mark laid in its wall's plane and cut to what the wall shows, cell by cell. `linksAt(k)` gives the links of the
        /// wall k cells along from the anchor (negative for no wall). The walk stops at the first cell without this face, so a corner,
        /// door or wall end ends the mark there. Polygon coordinates are relative to the anchor cell's south-west corner.
        /// `slope` shears the baseline (rise per cell along the wall): the hand's tilt, which leaves every run hanging straight down.</summary>
        public static List<RM_MarkPiece> MarkPieces(Func<int, int> linksAt, int face, float crease, float sideW, float width, float height, float slide, float slope, float lift, bool flip)
        {
            var pieces = new List<RM_MarkPiece>();
            if (face != FaceFront && face != FaceEast && face != FaceWest) return pieces;
            AlongOf(face, out int ax, out int az);
            float halfW = width / 2f;
            float room = Math.Abs(slope) * halfW;
            float hh = Math.Min(height, WallWorldHeight - 2f * room);
            float tc = hh / 2f + room + (WallWorldHeight - hh - 2f * room) * lift;
            var quad = new List<RM_PlaneVert>(4);
            foreach (float[] c in QuadCorners)
            {
                float s = slide + (c[0] - 0.5f) * width;
                float t = tc + (c[1] - 0.5f) * hh + slope * (s - slide);
                PlaneToCell(face, s, t, crease, sideW, out float x, out float z);
                quad.Add(new RM_PlaneVert(x, z, flip ? 1f - c[0] : c[0], c[1]));
            }
            foreach (int dir in new[] { 1, -1 })
            {
                for (int k = dir > 0 ? 0 : -1; Math.Abs(k) <= MaxReachCells; k += dir)
                {
                    float s0 = k - 0.5f;
                    if (s0 + 1f < slide - halfW || s0 > slide + halfW) break;
                    int links = linksAt(k);
                    List<RM_PlaneVert> edge = FacePoly(links, face, crease, sideW);
                    if (edge == null) break;
                    var shifted = new List<RM_PlaneVert>(edge.Count);
                    foreach (RM_PlaneVert e in edge) shifted.Add(new RM_PlaneVert(e.x + ax * k, e.z + az * k));
                    List<RM_PlaneVert> poly = ClipConvex(quad, shifted);
                    if (poly.Count >= 3) pieces.Add(new RM_MarkPiece(k, poly));
                }
            }
            return pieces;
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
            return "real craft";
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
    }
}
