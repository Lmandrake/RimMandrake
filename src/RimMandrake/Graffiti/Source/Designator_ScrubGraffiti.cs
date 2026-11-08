using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Graffiti
{
    // Design §1.7 / fork F7 (ruled 2026-10-09): "own-faction and Devotional marks protected from home-area auto-clean, a scrub designator
    // overrides." A right-click "Clean" was the only override, one mark at a time and only inside the Home area, so after a spree the
    // player clicked thirty marks. Drag this over a wall (or the floor in front of it) and every mark painted there is marked for
    // scrubbing; WorkGiver_ScrubGraffitiDesignated hands the job out under Cleaning. A mark's Position is the floor cell before its wall
    // (Filth_Mark.wallSide), so a cell answers for the marks on it and for the marks drawn on it from a neighbour.
    public class Designator_ScrubGraffiti : Designator_Cells
    {
        public Designator_ScrubGraffiti()
        {
            defaultLabel = "Scrub graffiti";
            defaultDesc = "Mark graffiti on a wall to be scrubbed off by a colonist doing cleaning work, even your own colony's work, which the cleaning rounds leave alone. Drag over the walls. Your colonists leave a scrubbed wall alone for ten days. Someone who hates the person an insult is about won't scrub it.";
            icon = ContentFinder<Texture2D>.Get("UI/Designators/RemovePaint", reportFailure: false);
            useMouseIcon = true;
            soundDragSustain = SoundDefOf.Designate_DragStandard;
            soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
            soundSucceeded = SoundDefOf.Designate_RemovePaint;
        }

        public override DrawStyleCategoryDef DrawStyleCategory => DrawStyleCategoryDefOf.FilledRectangle;

        public override bool DragDrawMeasurements => true;

        protected override DesignationDef Designation => RMGraffitiDefOf.RM_ScrubGraffiti;

        public override AcceptanceReport CanDesignateCell(IntVec3 c)
        {
            if (!c.InBounds(Map) || c.Fogged(Map)) return false;
            foreach (Filth_Mark m in MarksAt(c, Map))
            {
                if (CanDesignateThing(m).Accepted) return true;
            }
            return "Drag over graffiti on a wall.";
        }

        public override void DesignateSingleCell(IntVec3 c)
        {
            foreach (Filth_Mark m in MarksAt(c, Map))
            {
                if (CanDesignateThing(m).Accepted) DesignateThing(m);
            }
        }

        public override AcceptanceReport CanDesignateThing(Thing t)
        {
            return t is Filth_Mark m && m.Spawned && Map.designationManager.DesignationOn(m, Designation) == null;
        }

        public override void DesignateThing(Thing t)
        {
            Map.designationManager.AddDesignation(new Designation(t, Designation));
        }

        public override void SelectedUpdate()
        {
            GenUI.RenderMouseoverBracket();
        }

        /// <summary>The marks on this cell's floor and the marks drawn on this cell's wall from the floor beside it.</summary>
        internal static IEnumerable<Filth_Mark> MarksAt(IntVec3 c, Map map)
        {
            List<Thing> here = c.GetThingList(map);
            for (int i = 0; i < here.Count; i++)
            {
                if (here[i] is Filth_Mark m) yield return m;
            }
            for (int side = 0; side < 4; side++)
            {
                IntVec3 floor = c - new Rot4(side).FacingCell;
                if (!floor.InBounds(map)) continue;
                List<Thing> there = floor.GetThingList(map);
                for (int i = 0; i < there.Count; i++)
                {
                    if (there[i] is Filth_Mark m && m.wallSide == side) yield return m;
                }
            }
        }
    }
}
