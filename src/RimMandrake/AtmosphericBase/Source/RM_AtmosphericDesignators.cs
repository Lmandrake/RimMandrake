// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 1 -- the per-thing opt-in button, with no Harmony and no def edit.
//
// GizmoGridDrawer.DrawGizmoGridFor (Verse, RimSage 1.6) asks every designator in Find.ReverseDesignatorDatabase
// .AllDesignators for CreateReverseDesignationGizmo(selectedThing) and shows the ones that accept -- that is how
// Deconstruct and Open appear on a selected thing. AllDesignators returns the database's own list, so adding to it
// adds a button to every selected thing our CanDesignateThing accepts. The database rebuilds that list on
// Reinit() (GameRules change, MapInterface), which hands back a NEW list; EnsureRegistered compares references every
// frame from MapComponentUpdate and re-adds when the list was replaced.
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    public static class RM_AtmosphericDesignators
    {
        private static List<Designator> registeredIn;

        public static void EnsureRegistered()
        {
            List<Designator> list = Find.ReverseDesignatorDatabase?.AllDesignators;
            if (list == null || ReferenceEquals(list, registeredIn)) return;
            bool hasTake = false, hasRelease = false;
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i] is RM_Designator_TakeOverGlow) hasTake = true;
                if (list[i] is RM_Designator_ReleaseGlow) hasRelease = true;
            }
            if (!hasTake) list.Add(new RM_Designator_TakeOverGlow());
            if (!hasRelease) list.Add(new RM_Designator_ReleaseGlow());
            registeredIn = list;
        }

        /// <summary>The player may press either button on this map at all.</summary>
        public static bool PlayerMayChoose(Map map)
        {
            RM_AtmosphericBaseSettings s = RM_AtmosphericBaseSettings.Cur;
            RM_MapComponent_AtmosphericBase c = RM_MapComponent_AtmosphericBase.For(map);
            return s.lightChannel && s.playerTakeoverButton && c != null && !c.scenarioDecides;
        }
    }

    public class RM_Designator_TakeOverGlow : Designator
    {
        public RM_Designator_TakeOverGlow()
        {
            defaultLabel = "Hand glow to Atmospheric Base";
            defaultDesc = "Let Atmospheric Base drive this light's colour. Take it back at any time and it returns to exactly the colour it has now. Its radius is never changed.";
            icon = ContentFinder<Texture2D>.Get("UI/Commands/ChangeColor");
            soundSucceeded = SoundDefOf.Tick_High;
        }

        public override AcceptanceReport CanDesignateCell(IntVec3 loc)
        {
            return false;
        }

        public override AcceptanceReport CanDesignateThing(Thing t)
        {
            if (!RM_AtmosphericDesignators.PlayerMayChoose(Map)) return false;
            return RM_MapComponent_AtmosphericBase.For(Map).TakeOverRefusal(t) == null;
        }

        public override void DesignateThing(Thing t)
        {
            RM_MapComponent_AtmosphericBase.For(Map)?.TakeOver(t);
        }
    }

    public class RM_Designator_ReleaseGlow : Designator
    {
        public RM_Designator_ReleaseGlow()
        {
            defaultLabel = "Take glow back";
            defaultDesc = "Atmospheric Base stops driving this light. It returns to exactly the colour it had when it was handed over.";
            icon = ContentFinder<Texture2D>.Get("UI/Commands/ChangeColor");
            soundSucceeded = SoundDefOf.Tick_Low;
        }

        public override AcceptanceReport CanDesignateCell(IntVec3 loc)
        {
            return false;
        }

        public override AcceptanceReport CanDesignateThing(Thing t)
        {
            if (!RM_AtmosphericDesignators.PlayerMayChoose(Map)) return false;
            return RM_MapComponent_AtmosphericBase.For(Map).IsTaken(t);
        }

        public override void DesignateThing(Thing t)
        {
            RM_MapComponent_AtmosphericBase.For(Map)?.Release(t);
        }
    }
}
