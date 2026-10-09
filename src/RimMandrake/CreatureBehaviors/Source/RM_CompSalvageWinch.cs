using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // SHIP_TOW_LINE_1 (design pass X-13 / CB-9). A winch that hooks heavy OBJECTS (wreck chunks, carcasses, a downed
    // beast) and drags them home, cell by cell, until they rest beside it. Built as its own comp rather than by
    // generalising RM_CompTetherPull's `Pawn target`: the tether keeps its save key and its two pawn-only hosts untouched,
    // and this comp owns a Thing target under new keys, so there is no save migration.
    //
    // Ordered, never automatic: a gizmo ("Hook salvage") opens a targeter. The reel is the tether's own forced move, one
    // cell per reel interval toward the host, stopped by a wall, a lost line of sight, or distance. Over the mass cap the
    // hook is refused with a reason. Mod Settings: salvageWinchEnabled / Range / MaxMass / ReelSpeed.
    public class RM_CompProperties_SalvageWinch : CompProperties
    {
        public RM_CompProperties_SalvageWinch() { compClass = typeof(RM_CompSalvageWinch); }
    }

    public class RM_CompSalvageWinch : ThingComp
    {
        private Thing target;
        private int nextReelTick = -1;
        private int hooked;
        private string lastOutcome = "";

        public Thing Target => target;
        public int Hooked => hooked;
        public string LastOutcome => lastOutcome;

        public static bool Enabled => RM_CreatureBehaviorsSettings.salvageWinchEnabled;
        public static int ReelIntervalTicks => RM_CompTetherPull.ReelIntervalTicksFor(RM_CreatureBehaviorsSettings.salvageWinchReelSpeed);

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref target, "salvageTarget");
            Scribe_Values.Look(ref nextReelTick, "salvageNextReelTick", -1);
            Scribe_Values.Look(ref hooked, "salvageHooked");
            Scribe_Values.Look(ref lastOutcome, "salvageLastOutcome", "");
        }

        public string Refusal(Thing t)
        {
            if (t == null || !t.Spawned || t.Map != parent.Map) return "nothing there to hook";
            Pawn p = t as Pawn;
            float mass = t.GetStatValue(StatDefOf.Mass) * (p != null ? 1 : t.stackCount);
            string why = RM_SalvageWinchRules.RefusalFor(t is Corpse, p != null, p != null && p.Downed && !p.Dead && p.RaceProps.Animal,
                t.def.category == ThingCategory.Item, mass, RM_CreatureBehaviorsSettings.salvageWinchMaxMass,
                t.Position.DistanceTo(parent.Position), RM_CreatureBehaviorsSettings.salvageWinchRange);
            if (why == null && !GenSight.LineOfSight(parent.Position, t.Position, parent.Map, skipFirstCell: true)) why = "no clear line to it";
            return why;
        }

        /// <summary>Hook this thing. Returns false and tells the player why when it cannot be hooked.</summary>
        public bool TryHook(Thing t, bool message = true)
        {
            if (!Enabled || !parent.Spawned) return false;
            string why = Refusal(t);
            if (why != null)
            {
                if (message) Messages.Message("The winch cannot hook that: " + why + ".", parent, MessageTypeDefOf.RejectInput, historical: false);
                return false;
            }
            target = t;
            hooked++;
            lastOutcome = "hooked";
            nextReelTick = Find.TickManager.TicksGame + ReelIntervalTicks;
            return true;
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
            if (!Enabled || parent.Faction != Faction.OfPlayer) yield break;
            yield return new Command_Action
            {
                defaultLabel = target == null ? "Hook salvage" : "Cut the line",
                defaultDesc = target == null
                    ? "Hook a wreck chunk, a carcass or a downed beast within reach and drag it home to the winch."
                    : "Let go of what the winch is dragging.",
                icon = TexCommand.Attack,
                action = () =>
                {
                    if (target != null) { Release("cut"); return; }
                    Find.Targeter.BeginTargeting(new TargetingParameters
                    {
                        canTargetItems = true,
                        canTargetPawns = true,
                        canTargetCorpses = true,
                        validator = ti => ti.HasThing && Refusal(ti.Thing) == null,
                    }, ti => TryHook(ti.Thing));
                },
            };
        }

        public override void CompTick()
        {
            base.CompTick();
            if (target == null) return;
            if (!Enabled || !parent.Spawned) { Release("off"); return; }
            if (Find.TickManager.TicksGame >= nextReelTick) ReelStep();
        }

        private void ReelStep()
        {
            Thing t = target;
            Map map = parent.Map;
            if (t == null || t.Destroyed || !t.Spawned || t.Map != map) { Release("lost"); return; }
            if (t is Pawn dp && (dp.Dead || !dp.Downed)) { Release("lost"); return; }
            if (t.Position.AdjacentTo8WayOrInside(parent)) { Release("arrived"); return; }
            if (!GenSight.LineOfSight(parent.Position, t.Position, map, skipFirstCell: true)) { Release("wall"); return; }
            IntVec3 next = RM_CompTetherPull.NextCellToward(t.Position, parent.Position);
            if (!next.IsValid || !next.InBounds(map) || !next.Walkable(map)
                || (next.GetEdifice(map) is Building b && b.def.Fillage == FillCategory.Full))
            {
                Release("obstacle");
                return;
            }
            if (t is Pawn p)
            {
                p.Position = next;
                p.Notify_Teleported(endCurrentJob: true, resetTweenedPos: false);
            }
            else
            {
                t.DeSpawn();
                GenSpawn.Spawn(t, next, map);
            }
            nextReelTick = Find.TickManager.TicksGame + ReelIntervalTicks;
        }

        public void Release(string reasonCode)
        {
            lastOutcome = reasonCode;
            target = null;
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            target = null;
        }

        public override void PostDraw()
        {
            base.PostDraw();
            if (target != null && target.Spawned) GenDraw.DrawLineBetween(parent.DrawPos, target.DrawPos, SimpleColor.Yellow, 0.3f);
        }

        public override string CompInspectStringExtra()
        {
            if (!Enabled) return "Switched off in Mod Settings.";
            return (target != null ? "Dragging " + target.LabelShort + "." : "Ready.") + " Hooked " + hooked + " so far.";
        }

        public override void PostDrawExtraSelectionOverlays()
        {
            base.PostDrawExtraSelectionOverlays();
            GenDraw.DrawRadiusRing(parent.Position, Mathf.Min(RM_CreatureBehaviorsSettings.salvageWinchRange, GenRadial.MaxRadialPatternRadius));
        }
    }
}
