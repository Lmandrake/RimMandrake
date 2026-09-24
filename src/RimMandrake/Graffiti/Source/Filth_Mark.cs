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

        // Tier-A rendering cache (design §3.1): built lazily from
        // ModExtension_Graffiti.sigilTierA + sigilFrameTexPath + makerIdeo.
        // Never Scribed - rebuilt from the (Scribed) fields above every
        // load, same as any other Material/Graphic cache in vanilla.
        private Material cachedFrameMat;
        private Material cachedIconMat;
        private bool sigilMatsBuilt;

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
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
        // Going-over (design §1.6 / fork F7, "going-over in v1"): a rival
        // mark already at the cell is destroyed first, never thickened
        // alongside the new one - two different marks papering over each
        // other, not one filth pile growing. "Rival" = any other
        // Filth_Mark whose def differs from markDef; thickening the SAME
        // def (the vanilla FilthMaker behaviour) is left alone.
        public static Filth_Mark MakeMark(IntVec3 cell, Map map, ThingDef markDef, Pawn maker, Pawn subject = null)
        {
            if (cell.IsValid && map != null)
            {
                foreach (Thing t in cell.GetThingList(map).ToArray())
                {
                    if (t is Filth_Mark rival && rival.def != markDef)
                    {
                        rival.Destroy();
                    }
                }
            }
            if (!FilthMaker.TryMakeFilth(cell, map, markDef, out Filth outFilth))
            {
                return null;
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
        public override void Print(SectionLayer layer)
        {
            if (!sigilMatsBuilt)
            {
                RebuildSigilMats();
            }
            if (cachedFrameMat == null && cachedIconMat == null)
            {
                base.Print(layer);
                return;
            }
            Vector3 basePos = DrawPos;
            if (cachedFrameMat != null)
            {
                Printer_Plane.PrintPlane(layer, basePos, Vector2.one, cachedFrameMat);
            }
            if (cachedIconMat != null)
            {
                Vector3 iconPos = basePos + new Vector3(0f, 0.01f, 0f);
                Printer_Plane.PrintPlane(layer, iconPos, new Vector2(0.62f, 0.62f), cachedIconMat);
            }
        }
    }
}
