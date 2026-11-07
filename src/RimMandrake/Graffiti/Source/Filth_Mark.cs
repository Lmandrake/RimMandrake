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
            return mark;
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
            Texture2D icon = makerIdeo.Icon;
            if (icon != null)
            {
                cachedIconMat = MaterialPool.MatFrom(icon, ShaderDatabase.Mote, makerIdeo.Color);
            }
        }

        // Tier-A composite: frame quad, then the ideo icon quad slightly
        // above it (Printer_Plane's center.y IS the base altitude of all
        // four verts - a small +y on the icon's center keeps it drawn over
        // the frame rather than z-fighting at the same layer). Falls back
        // to the ordinary Filth print (base.Print -> Graphic.Print from the
        // def's own <graphicData>) whenever there is nothing to composite -
        // every non-sigil mark, and a sigil mark whose ideo/icon didn't
        // resolve.
        //
        // GRAFFITI_WALLFACE: both paths draw at WallFacePos / WallFaceAngle, i.e. pushed onto the recorded wall and turned to
        // face it; a mark with no recorded wall draws exactly as before (the plain path then stays vanilla's own print).
        public override void Print(SectionLayer layer)
        {
            if (!sigilMatsBuilt)
            {
                RebuildSigilMats();
            }
            RM_GraffitiKernel.HandOf(thingIDNumber, GraffitiPool.WidthOf(def), out float tilt, out float scale, out float slide);
            if (def.GetModExtension<ModExtension_Graffiti>()?.form == GraffitiForm.Scrawl)
            {
                scale = 1f;     // the ugliest thing on the wall gets no modest hand: the picture agrees with its Beauty
            }
            float angle = RM_GraffitiKernel.WallFaceAngle(wallSide) + tilt;
            if (cachedFrameMat == null && cachedIconMat == null)
            {
                if (wallSide == RM_GraffitiKernel.NoWall)
                {
                    base.Print(layer);
                    return;
                }
                PrintPlainOnWall(layer, angle, scale, slide);
                return;
            }
            Vector3 basePos = WallFacePos(slide);
            Vector2 size = (def.graphicData?.drawSize ?? Vector2.one) * scale;
            if (cachedFrameMat != null)
            {
                Printer_Plane.PrintPlane(layer, basePos, size, cachedFrameMat, angle);
            }
            if (cachedIconMat != null)
            {
                Vector3 iconPos = basePos + new Vector3(0f, 0.01f, 0f);
                Printer_Plane.PrintPlane(layer, iconPos, size * 0.62f, cachedIconMat, angle);
            }
        }

        /// <summary>DrawPos pushed RM_GraffitiKernel.WallFaceOffsetCells toward the recorded wall (DrawPos itself for none), and `slide` cells along it.</summary>
        private Vector3 WallFacePos(float slide)
        {
            RM_GraffitiKernel.WallFaceOffset(wallSide, RM_GraffitiKernel.WallFaceOffsetCells, out float dx, out float dz);
            Vector3 along = wallSide == RM_GraffitiKernel.NoWall ? Vector3.zero : new Rot4(wallSide).Rotated(RotationDirection.Clockwise).FacingCell.ToVector3();
            return DrawPos + new Vector3(dx, 0f, dz) + along * slide;
        }

        /// <summary>The plain (non-sigil) mark on its wall: vanilla Graphic.Print's plane (Graphic_Random's sub-graphic for this
        /// thing, its drawSize, its material at North, the def's drawOffset) at the wall-face position and angle. The atlas
        /// replacement Graphic.Print also does is skipped: it only re-points the same texture into a shared atlas.</summary>
        private void PrintPlainOnWall(SectionLayer layer, float angle, float scale, float slide)
        {
            Graphic g = Graphic;
            if (g is Graphic_Random random)
            {
                g = random.SubGraphicFor(this);
            }
            if (g == null)
            {
                return;
            }
            Vector3 center = WallFacePos(slide) + g.DrawOffset(Rot4.North);
            Printer_Plane.PrintPlane(layer, center, g.drawSize * scale, g.MatAt(Rot4.North, this), angle);
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

        /// <summary>Marks whose drawing overlaps a width centred on `wall`, a wall cell: looked for along the wall's line, on the
        /// floor cells either side of it, since a one-thick wall carries both its faces' marks on one drawn cell.</summary>
        internal static System.Collections.Generic.List<Filth_Mark> MarksOverlapping(IntVec3 wall, int side, float halfWidth, Map map, Filth_Mark except)
        {
            var found = new System.Collections.Generic.List<Filth_Mark>();
            Rot4 dir = new Rot4(side);
            IntVec3 along = dir.Rotated(RotationDirection.Clockwise).FacingCell;
            IntVec3 normal = dir.FacingCell;
            for (int k = -WallSearchCells; k <= WallSearchCells; k++)
            {
                IntVec3 onWall = wall + along * k;
                foreach (IntVec3 floor in new[] { onWall - normal, onWall + normal })
                {
                    if (!floor.InBounds(map)) continue;
                    foreach (Thing t in floor.GetThingList(map))
                    {
                        if (!(t is Filth_Mark m) || m == except || m.wallSide == RM_GraffitiKernel.NoWall) continue;
                        if (m.Position + new Rot4(m.wallSide).FacingCell != onWall) continue;
                        if (RM_GraffitiKernel.WallMarksOverlap(k, halfWidth, GraffitiPool.WidthOf(m.def) / 2f) && !found.Contains(m))
                        {
                            found.Add(m);
                        }
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
