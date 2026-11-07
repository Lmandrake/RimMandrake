using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 mechanism 4's Designator placer
    // (design §2.2's "Designator" placer column). Marks a wall cell for
    // graffiti the way vanilla marks a cell for mining or planting - a
    // DesignationDef the pawn later fulfils. Fork F6 (ruled 2026-10-09,
    // "full designator + bill - choose mark, choose wall";
    // GRAFFITI_DESIGNATOR_MARK_CHOICE_1): clicking the gizmo opens a float
    // menu of every designatorEligible mark plus "any", the same shape as
    // vanilla Designator_Build's stuff menu. The choice is stored per cell in
    // MapComponent_GraffitiOrders; "any" (null) leaves the pick to
    // GraffitiPool.PickForDesignator at paint time.
    public class Designator_PaintGraffitiMark : Designator_Cells
    {
        private ThingDef chosenMark;
        private Pawn chosenSubject;
        private Faction chosenFaction;
        public Designator_PaintGraffitiMark()
        {
            // Plain string literals, matching this mod's existing
            // convention (RM_GraffitiMod.cs's settings labels) - no
            // Languages/ keyed-string infra exists here yet to route
            // .Translate() through.
            defaultLabel = "Paint graffiti here";
            defaultDesc = "Mark a wall cell for a colonist to paint graffiti on, next time one is free.";
            icon = ContentFinder<Texture2D>.Get("Things/Filth/Art/RM_Graffiti_Vandal/vandal_0", reportFailure: false);
            useMouseIcon = true;
            soundDragSustain = SoundDefOf.Designate_DragStandard;
            soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
            soundSucceeded = SoundDefOf.Designate_Claim;
            hotKey = KeyBindingDefOf.Misc2;
        }

        protected override DesignationDef Designation => RMGraffitiDefOf.RM_PaintGraffitiHere;

        public override AcceptanceReport CanDesignateCell(IntVec3 loc)
        {
            if (!loc.InBounds(Map))
            {
                return false;
            }
            if (Map.designationManager.DesignationAt(loc, RMGraffitiDefOf.RM_PaintGraffitiHere) != null)
            {
                return false;
            }
            // Coarse but honest: reuse the same "is there a cardinal wall
            // nearby" search the job itself later uses, so this refuses a
            // designation nowhere near any wall at all rather than
            // accepting it and letting it sit unworked forever.
            // GPT deep review 2026-10-22 #5: the job paints the CLICKED cell, so that cell itself must stand against a wall
            // (a wall merely "nearby" accepted orders that painted open floor)
            if (!loc.Standable(Map) || !GraffitiJobUtility.HasCardinalWall(loc, Map))
            {
                return "Mark a floor cell right against a wall.";
            }
            return true;
        }

        public override void ProcessInput(Event ev)
        {
            if (!CheckCanInteract())
            {
                return;
            }
            List<FloatMenuOption> options = new List<FloatMenuOption>
            {
                new FloatMenuOption("Any mark (painter's pick)", delegate
                {
                    chosenMark = null;
                    chosenSubject = null;
                    chosenFaction = null;
                    base.ProcessInput(ev);
                })
            };
            foreach (ThingDef d in GraffitiPool.AllDesignatorEligible().OrderBy(d => d.label))
            {
                ThingDef local = d;
                options.Add(new FloatMenuOption(local.LabelCap, delegate
                {
                    chosenMark = local;
                    chosenSubject = null;
                    chosenFaction = null;
                    ModExtension_Graffiti ext = local.GetModExtension<ModExtension_Graffiti>();
                    if (ext != null && ext.hasSubject)
                    {
                        ChooseWhom(ev, ext);
                    }
                    else if (ext != null && ext.meaning == RM_Meaning.Insult)
                    {
                        ChooseFaction(ev);
                    }
                    else
                    {
                        base.ProcessInput(ev);
                    }
                }, local));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        /// <summary>A mark about someone asks who: the colonists, or for a memorial the colony's dead.</summary>
        private void ChooseWhom(Event ev, ModExtension_Graffiti ext)
        {
            IEnumerable<Pawn> who = ext.meaning == RM_Meaning.Memorial
                ? Find.WorldPawns.AllPawnsDead.Concat(Map.mapPawns.AllPawns.Where(p => p.Dead)).Where(p => p.Faction == Faction.OfPlayer && p.RaceProps.Humanlike)
                : Map.mapPawns.FreeColonists;
            List<FloatMenuOption> options = who.OrderBy(p => p.LabelShort).Select(p => new FloatMenuOption(p.LabelShort, delegate
            {
                chosenSubject = p;
                base.ProcessInput(ev);
            })).ToList();
            if (options.Count == 0)
            {
                options.Add(new FloatMenuOption("Nobody to paint", null));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        private void ChooseFaction(Event ev)
        {
            List<FloatMenuOption> options = Find.FactionManager.AllFactionsVisibleInViewOrder.Where(f => !f.IsPlayer && !f.Hidden).Select(f => new FloatMenuOption(f.Name, delegate
            {
                chosenFaction = f;
                base.ProcessInput(ev);
            })).ToList();
            if (options.Count == 0)
            {
                options.Add(new FloatMenuOption("Nobody to insult", null));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        public override void DesignateSingleCell(IntVec3 c)
        {
            Map.designationManager.AddDesignation(new Designation(c, RMGraffitiDefOf.RM_PaintGraffitiHere));
            MapComponent_GraffitiOrders.For(Map)?.SetOrder(c, chosenMark, chosenSubject, chosenFaction);
        }
    }
}
