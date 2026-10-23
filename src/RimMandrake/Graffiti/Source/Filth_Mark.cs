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
        // first spawn (a mark from an older save has none and reads it then), kept if that wall later goes: the paint
        // was put there. Print draws the mark offset onto that wall and turned to face it.
        public int wallSide = RM_GraffitiKernel.NoWall;

        // Tier-A rendering cache (design §3.1): built lazily from
        // ModExtension_Graffiti.sigilTierA + sigilFrameTexPath + makerIdeo.
        // Never Scribed - rebuilt from the (Scribed) fields above every
        // load, same as any other Material/Graphic cache in vanilla.
        private Material cachedFrameMat;
        private Material cachedIconMat;
        private bool sigilMatsBuilt;

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
            }
            if (!FilthMaker.TryMakeFilth(cell, map, markDef, out Filth outFilth))
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
                cachedFrameMat = MaterialPool.MatFrom(ext.sigilFrameTexPath, ShaderDatabase.Cutout);
            }
            Texture2D icon = makerIdeo.Icon;
            if (icon != null)
            {
                cachedIconMat = MaterialPool.MatFrom(icon, ShaderDatabase.Cutout, makerIdeo.Color);
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
            float angle = RM_GraffitiKernel.WallFaceAngle(wallSide);
            if (cachedFrameMat == null && cachedIconMat == null)
            {
                if (wallSide == RM_GraffitiKernel.NoWall)
                {
                    base.Print(layer);
                    return;
                }
                PrintPlainOnWall(layer, angle);
                return;
            }
            Vector3 basePos = WallFacePos();
            if (cachedFrameMat != null)
            {
                Printer_Plane.PrintPlane(layer, basePos, Vector2.one, cachedFrameMat, angle);
            }
            if (cachedIconMat != null)
            {
                Vector3 iconPos = basePos + new Vector3(0f, 0.01f, 0f);
                Printer_Plane.PrintPlane(layer, iconPos, new Vector2(0.62f, 0.62f), cachedIconMat, angle);
            }
        }

        /// <summary>DrawPos pushed RM_GraffitiKernel.WallFaceOffsetCells toward the recorded wall (DrawPos itself for none).</summary>
        private Vector3 WallFacePos()
        {
            RM_GraffitiKernel.WallFaceOffset(wallSide, RM_GraffitiKernel.WallFaceOffsetCells, out float dx, out float dz);
            return DrawPos + new Vector3(dx, 0f, dz);
        }

        /// <summary>The plain (non-sigil) mark on its wall: vanilla Graphic.Print's plane (Graphic_Random's sub-graphic for this
        /// thing, its drawSize, its material at North, the def's drawOffset) at the wall-face position and angle. The atlas
        /// replacement Graphic.Print also does is skipped: it only re-points the same texture into a shared atlas.</summary>
        private void PrintPlainOnWall(SectionLayer layer, float angle)
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
            Vector3 center = WallFacePos() + g.DrawOffset(Rot4.North);
            Printer_Plane.PrintPlane(layer, center, g.drawSize, g.MatAt(Rot4.North, this), angle);
        }

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
