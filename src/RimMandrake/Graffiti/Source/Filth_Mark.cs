using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 mechanism 1: "A Filth subclass
    // carrying provenance (maker pawn, maker faction, maker ideo, subject,
    // placed tick, placer)." Everything else this item adds - relation-keyed
    // reactions, going-over, scrub protection, tier-A sigil rendering -
    // reads these fields. RM_BaseGraffiti's <thingClass> now names this
    // class instead of plain Filth (Defs/ThingDefs_Graffiti.xml).
    //
    // References are Scribe_References, not Scribe_Deep - maker/subject are
    // Pawns and makerFaction/makerIdeo are Factions/Ideos that already exist
    // elsewhere in the save (Pawn, Faction and Ideo are all
    // ILoadReferenceable - Ideo confirmed via RimSage this pass,
    // RimWorld/Ideo.cs:9 "public class Ideo : IExposable,
    // ILoadReferenceable"). A dead maker or a destroyed corpse still
    // resolves fine (Scribe_References tolerates a since-vanished
    // ILoadReferenceable by leaving the field null on load, same as any
    // other cross-reference in this engine).
    public class Filth_Mark : Filth
    {
        public Pawn maker;
        public Faction makerFaction;
        public Ideo makerIdeo;
        public Pawn subject;
        public int placedTick = -1;

        // GRAFFITI_WALLFACE (owner, by card 2026-10-22: "Q9 → Graffiti floor cell drawn offset facing wall"): the side of the
        // floor cell the wall it was painted on stands (RM_GraffitiKernel.WallSide; Rot4 int, NoWall = none). Read at the
        // first spawn (a mark from an older save has none and reads it then). The paint goes with its wall
        // (RaidExitTagger's sibling WallLossPatch): nothing may hang in the air. Print draws the mark on that wall cell and turned to face it.
        public int wallSide = RM_GraffitiKernel.NoWall;

        // Which of the def's drawings this is, and its pigment, chosen when painted to differ from what's already on this stretch of
        // wall. -1 (an older save's mark): the old pick by thing id.
        public int variant = -1;
        public int pigment;

        // Tier-A rendering cache (design §3.1): built lazily from
        // ModExtension_Graffiti.sigilTierA + sigilFrameTexPath + makerIdeo.
        // Never Scribed - rebuilt from the (Scribed) fields above every
        // load, same as any other Material/Graphic cache in vanilla.
        private Material cachedFrameMat;
        private Material cachedIconMat;
        private bool sigilMatsBuilt;

        /// <summary>Test reads (RM_GraffitiProof, GRAFFITI_V1_LIVE_PROOF_1 A3): the tier-A composite's two materials, null when absent.</summary>
        internal Material ProbeFrameMat => cachedFrameMat;
        internal Material ProbeIconMat => cachedIconMat;

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            // Before base.SpawnSetup, which registers the mark for the map mesh that Print then builds.
            if (wallSide == RM_GraffitiKernel.NoWall)
            {
                wallSide = ReadWallSide(Position, map);
            }
            base.SpawnSetup(map, respawningAfterLoad);
            if (placedTick < 0 && !respawningAfterLoad)
            {
                placedTick = Find.TickManager.TicksGame;
            }
            RebuildSigilMats();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref maker, "rmMarkMaker");
            Scribe_References.Look(ref makerFaction, "rmMarkMakerFaction");
            Scribe_References.Look(ref makerIdeo, "rmMarkMakerIdeo");
            Scribe_References.Look(ref subject, "rmMarkSubject");
            Scribe_Values.Look(ref placedTick, "rmMarkPlacedTick", -1);
            Scribe_Values.Look(ref wallSide, "rmMarkWallSide", RM_GraffitiKernel.NoWall);
            Scribe_Values.Look(ref variant, "rmMarkVariant", -1);
            Scribe_Values.Look(ref pigment, "rmMarkPigment", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                sigilMatsBuilt = false;
            }
        }

        // Stamps provenance on a freshly (or already-)made mark. Called by
        // GraffitiPool's placers instead of FilthMaker.TryMakeFilth
        // directly, so every placer (spree, joy, designator, raid-exit)
        // shares one going-over + provenance implementation.
        //
        // Going-over (design §1.6 / fork F4, ruled 2026-10-09: "going-over in v1"): a rival
        // mark already at the cell is destroyed first, never thickened
        // alongside the new one - two different marks papering over each
        // other, not one filth pile growing. "Rival" = any other
        // Filth_Mark whose def differs from markDef; thickening the SAME
        // def (the vanilla FilthMaker behaviour) is left alone.
        public static Filth_Mark MakeMark(IntVec3 cell, Map map, ThingDef markDef, Pawn maker, Pawn subject = null)
        {
            // GPT deep review 2026-10-22 #6: rivals are collected first and destroyed only once the new mark exists, so a
            // refused placement no longer erases the old mark and leaves the wall bare
            var rivals = new System.Collections.Generic.List<Filth_Mark>();
            if (cell.IsValid && map != null)
            {
                foreach (Thing t in cell.GetThingList(map))
                {
                    if (t is Filth_Mark rival && RM_GraffitiKernel.IsRival(true, rival.def == markDef))
                    {
                        rivals.Add(rival);
                    }
                }
                // Going over reaches along the wall: whatever this mark's drawing will lie on top of, on either face of it.
                int side = ReadWallSide(cell, map);
                if (side != RM_GraffitiKernel.NoWall)
                {
                    foreach (Filth_Mark under in MarksOverlapping(cell + new Rot4(side).FacingCell, side, GraffitiPool.WidthOf(markDef) / 2f, map, null))
                    {
                        if (under.Position != cell && !rivals.Contains(under))
                        {
                            rivals.Add(under);
                        }
                    }
                }
            }
            // GRAFFITI_V1_LIVE_PROOF_1 (GPT review): no propagation. Vanilla filth spills onto a neighbour when the cell will not
            // take it; a mark is painted on THIS wall cell or not at all, and a spill elsewhere would let the going-over below erase
            // the rival with nothing painted over it.
            if (!FilthMaker.TryMakeFilth(cell, map, markDef, out Filth outFilth, 1, FilthSourceFlags.None, false) || outFilth == null
                || outFilth.Position != cell)
            {
                return null;
            }
            foreach (Filth_Mark rival in rivals)
            {
                if (!rival.Destroyed) rival.Destroy();
            }
            if (!(outFilth is Filth_Mark mark))
            {
                return null;
            }
            mark.maker = maker;
            mark.makerFaction = maker?.Faction;
            mark.makerIdeo = maker?.Ideo;
            mark.subject = subject;
            if (mark.placedTick < 0)
            {
                mark.placedTick = Find.TickManager.TicksGame;
            }
            mark.sigilMatsBuilt = false;
            mark.RebuildSigilMats();
            mark.ChooseLook(cell, map);
            map.mapDrawer.MapMeshDirty(cell, MapMeshFlagDefOf.Things);
            return mark;
        }

        /// <summary>This mark's drawing and pigment, unlike what's near it on the same line of sight: a second tag on this wall is
        /// the same hand in another colour or another hand, not a stamp.</summary>
        private void ChooseLook(IntVec3 cell, Map map)
        {
            var usedVariants = new System.Collections.Generic.HashSet<int>();
            var usedPigments = new System.Collections.Generic.HashSet<int>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(cell, LookRadius, useCenter: true))
            {
                if (!c.InBounds(map)) continue;
                foreach (Thing t in c.GetThingList(map))
                {
                    if (t is Filth_Mark m && m != this && m.def == def)
                    {
                        usedVariants.Add(m.variant);
                        usedPigments.Add(m.pigment);
                    }
                }
            }
            int count = Graphic is Graphic_Random random ? random.SubGraphicsCount : 1;
            variant = RM_GraffitiKernel.PickFree(count, usedVariants, Rand.Value);
            // A pigment the wall would swallow is no choice at all: chalk on marble, soot on slate.
            Color wallColor = WallPlane.FaceColor(cell + new Rot4(wallSide == RM_GraffitiKernel.NoWall ? 0 : wallSide).FacingCell, map);
            for (int i = 0; i < RM_GraffitiKernel.PigmentCount; i++)
            {
                if (!RM_GraffitiKernel.PigmentReads(i, wallColor.r, wallColor.g, wallColor.b)) usedPigments.Add(i);
            }
            pigment = RM_GraffitiKernel.PickFree(RM_GraffitiKernel.PigmentCount, usedPigments, Rand.Value);
        }

        private const float LookRadius = 9f;

        private static Color PigmentOf(int index)
        {
            RM_Rgb p = RM_GraffitiKernel.PigmentColor(index);
            return new Color(p.r, p.g, p.b);
        }

        public override string GetInspectString()
        {
            string baseText = base.GetInspectString();
            float beauty = this.GetStatValue(StatDefOf.Beauty);
            string line = "Beauty " + beauty.ToString("+0;-0;0") + ": " + RM_GraffitiKernel.BeautyWord(beauty);
            return string.IsNullOrEmpty(baseText) ? line : baseText + "\n" + line;
        }

        private void RebuildSigilMats()
        {
            sigilMatsBuilt = true;
            cachedFrameMat = null;
            cachedIconMat = null;
            ModExtension_Graffiti ext = def.GetModExtension<ModExtension_Graffiti>();
            if (ext == null || !ext.sigilTierA || makerIdeo == null)
            {
                return;
            }
            if (!string.IsNullOrEmpty(ext.sigilFrameTexPath))
            {
                cachedFrameMat = MaterialPool.MatFrom(ext.sigilFrameTexPath, ShaderDatabase.Mote);
            }
            Texture2D icon = WallPlane.PaintedIcon(makerIdeo.Icon) ?? makerIdeo.Icon;
            if (icon != null)
            {
                // Ideoligion colours are clean UI colours; on a wall they are the same hue in a mixed pigment.
                Color pigmentOfIdeo = Color.Lerp(makerIdeo.Color, new Color(0.45f, 0.42f, 0.38f), 0.3f) * 0.9f;
                pigmentOfIdeo.a = 1f;
                cachedIconMat = MaterialPool.MatFrom(icon, ShaderDatabase.Mote, pigmentOfIdeo);
            }
        }

        // A painted mark lies in its wall's plane (WallPlane, RM_GraffitiKernel.MarkPieces): stopped at the crease and the corners,
        // squashed the way the camera squashes that face. Tier-A sigils print the same way, frame then ideo icon. A mark with no
        // wall recorded draws as vanilla filth, flat on its floor.
        public override void Print(SectionLayer layer)
        {
            if (!sigilMatsBuilt)
            {
                RebuildSigilMats();
            }
            if (wallSide == RM_GraffitiKernel.NoWall)
            {
                base.Print(layer);
                return;
            }
            ModExtension_Graffiti ext = def.GetModExtension<ModExtension_Graffiti>();
            Vector2 size = def.graphicData?.drawSize ?? Vector2.one;
            RM_GraffitiKernel.HandOf(thingIDNumber, size.x, out float slope, out float scale, out float slide, out float lift, out bool flip);
            if (ext?.form == GraffitiForm.Scrawl)
            {
                scale = 1f;     // the ugliest thing on the wall gets no modest hand: the picture agrees with its Beauty
            }
            float width = size.x * scale;
            float height = RM_GraffitiKernel.WallWorldHeight * RM_GraffitiKernel.MarkFillOfFace * Mathf.Min(1f, size.y) * scale;
            float through = ThroughOf(ext);
            if (cachedFrameMat == null && cachedIconMat == null)
            {
                Graphic g = Graphic;
                if (g is Graphic_Random random)
                {
                    g = variant >= 0 ? random.SubGraphicAtIndex(variant) : random.SubGraphicFor(this);
                }
                if (g == null) return;
                Material mat = g.MatAt(Rot4.North, this);
                if (ext != null && ext.pigmented && !string.IsNullOrEmpty(g.path))
                {
                    mat = MaterialPool.MatFrom(g.path, g.Shader, PigmentOf(pigment));
                }
                WallPlane.Print(layer, this, mat, width, height, slide, slope, lift, flip, through);
                return;
            }
            if (cachedFrameMat != null)
            {
                WallPlane.Print(layer, this, cachedFrameMat, width, height, slide, slope, lift, flip, cachedIconMat == null ? through : 0f);
            }
            if (cachedIconMat != null)
            {
                // The icon's square in the wall's plane, as tall as the frame leaves room for. An icon may have text-like symmetry, so no flip.
                float iconH = height * 0.86f;
                WallPlane.Print(layer, this, cachedIconMat, iconH, iconH, slide, slope, lift, false, through, 0.001f);
            }
        }

        /// <summary>How much of the wall stays visible through paint: paper hides most of it, a gouge is the wall, spray and a dry brush let it through.</summary>
        private static float ThroughOf(ModExtension_Graffiti ext)
        {
            if (ext == null) return 0.24f;
            return ext.wallThrough >= 0f ? ext.wallThrough : (ext.form == GraffitiForm.Paste ? 0.18f : 0.24f);
        }

        /// <summary>A wall is gone: every mark painted on it goes too.</summary>
        internal static void Notify_WallGone(IntVec3 wall, Map map)
        {
            for (int i = 0; i < 4; i++)
            {
                Rot4 side = new Rot4(i);
                IntVec3 floor = wall - side.FacingCell;
                if (!floor.InBounds(map)) continue;
                foreach (Thing t in floor.GetThingList(map).ToArray())
                {
                    if (t is Filth_Mark m && m.wallSide == i && !m.Destroyed) m.Destroy();
                }
            }
        }

        /// <summary>Marks whose drawing overlaps a width centred on `wall`, a wall cell: looked for along the wall's line, on this one face.
        /// The other side of a one-thick wall is another face and carries its own.</summary>
        internal static System.Collections.Generic.List<Filth_Mark> MarksOverlapping(IntVec3 wall, int side, float halfWidth, Map map, Filth_Mark except)
        {
            var found = new System.Collections.Generic.List<Filth_Mark>();
            Rot4 dir = new Rot4(side);
            IntVec3 along = dir.Rotated(RotationDirection.Clockwise).FacingCell;
            IntVec3 normal = dir.FacingCell;
            for (int k = -WallSearchCells; k <= WallSearchCells; k++)
            {
                IntVec3 onWall = wall + along * k;
                IntVec3 floor = onWall - normal;
                if (!floor.InBounds(map)) continue;
                foreach (Thing t in floor.GetThingList(map))
                {
                    if (!(t is Filth_Mark m) || m == except || m.wallSide != side) continue;
                    if (RM_GraffitiKernel.WallMarksOverlap(k, halfWidth, GraffitiPool.WidthOf(m.def) / 2f) && !found.Contains(m))
                    {
                        found.Add(m);
                    }
                }
            }
            return found;
        }

        private const int WallSearchCells = 4;

        /// <summary>The side of `cell` the wall stands on (RM_GraffitiKernel.WallSide), NoWall with none.</summary>
        internal static int ReadWallSide(IntVec3 cell, Map map)
        {
            if (map == null || !cell.IsValid)
            {
                return RM_GraffitiKernel.NoWall;
            }
            return RM_GraffitiKernel.WallSide(
                GraffitiJobUtility.IsFullWallAt(cell + IntVec3.North, map),
                GraffitiJobUtility.IsFullWallAt(cell + IntVec3.East, map),
                GraffitiJobUtility.IsFullWallAt(cell + IntVec3.South, map),
                GraffitiJobUtility.IsFullWallAt(cell + IntVec3.West, map));
        }

        /// <summary>Test probe (jawa/static_call; GRAFFITI_WALLFACE): every Filth_Mark on the current map ->
        /// "marks=N;onWall=N;sides=n,e,s,w;mismatch=N" where mismatch counts marks whose recorded side no longer has a wall.</summary>
        public static string ProbeWallFaces()
        {
            Map map = Find.CurrentMap;
            if (map == null)
            {
                return "error=no current map";
            }
            int marks = 0, onWall = 0, mismatch = 0;
            int[] sides = new int[4];
            foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Filth))
            {
                if (!(t is Filth_Mark m))
                {
                    continue;
                }
                marks++;
                if (m.wallSide >= 0 && m.wallSide <= 3)
                {
                    onWall++;
                    sides[m.wallSide]++;
                    if (!GraffitiJobUtility.IsFullWallAt(m.Position + new Rot4(m.wallSide).FacingCell, map))
                    {
                        mismatch++;
                    }
                }
            }
            return "marks=" + marks + ";onWall=" + onWall + ";sides=" + sides[0] + "," + sides[1] + "," + sides[2] + "," + sides[3]
                + ";mismatch=" + mismatch;
        }
    }
}
