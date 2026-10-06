using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.RustCathedral
{
    // ════════════════════════════════════════════════════════════════════
    // RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1 §4 — the borehulk's worn drill.
    //
    // Three saved states. Only Worn is reachable in play from this item:
    // Unbitted and Restored are entered by RUSTCATHEDRAL_WORN_BIT_ARC_1 (not
    // built), which calls SetState. A dev-mode gizmo sets any state so the
    // criteria's per-state reads can run before the arc exists.
    //
    // Worn: every so often (MTB, Mod Settings) while standing still it scrapes
    // the plate — RM_BorehulkGrind plus micro-sparks, no cell mined, and
    // grindCount ticks up (the criteria's "comp counter"). Unbitted and
    // Restored never grind. Restored's mining is the arc's work; nothing here
    // mines anything in any state.
    //
    // Also records the last harming instigator for
    // RM_JobGiver_BorehulkBackAway (it backs away from that pawn; it never
    // attacks it).
    //
    // NOT BUILT: the per-state body graphic swap. The item says all three
    // states draw the Worn sprite until the Unbitted/Restored edit art exists,
    // so a render node keyed on State is owed WITH that art, not before it.
    // ════════════════════════════════════════════════════════════════════
    public enum RM_BorehulkDrillState
    {
        Worn,
        Unbitted,
        Restored
    }

    public class RM_CompProperties_BorehulkDrill : CompProperties
    {
        public SoundDef grindSound;

        // How often the grind check runs, in ticks.
        public int checkIntervalTicks = 250;

        public RM_CompProperties_BorehulkDrill()
        {
            compClass = typeof(RM_CompBorehulkDrill);
        }
    }

    public class RM_CompBorehulkDrill : ThingComp
    {
        private RM_BorehulkDrillState state = RM_BorehulkDrillState.Worn;

        public int grindCount;

        public Pawn lastAttacker;

        public int lastAttackedTick = -99999;

        public RM_CompProperties_BorehulkDrill Props => (RM_CompProperties_BorehulkDrill)props;

        public RM_BorehulkDrillState State => state;

        public void SetState(RM_BorehulkDrillState newState)
        {
            state = newState;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref state, "borehulkDrillState", RM_BorehulkDrillState.Worn);
            Scribe_Values.Look(ref grindCount, "borehulkGrindCount", 0);
            Scribe_References.Look(ref lastAttacker, "borehulkLastAttacker");
            Scribe_Values.Look(ref lastAttackedTick, "borehulkLastAttackedTick", -99999);
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (dinfo.Instigator is Pawn attacker && attacker != parent)
            {
                lastAttacker = attacker;
                lastAttackedTick = Find.TickManager.TicksGame;
            }
        }

        public override void CompTick()
        {
            base.CompTick();
            int interval = Mathf.Max(1, Props.checkIntervalTicks);
            if (!parent.IsHashIntervalTick(interval))
            {
                return;
            }
            if (state != RM_BorehulkDrillState.Worn || !RM_RustCathedralSettings.borehulkGrindEnabled)
            {
                return;
            }
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed)
            {
                return;
            }
            if (pawn.pather != null && pawn.pather.Moving)
            {
                return;
            }
            float mtbTicks = Mathf.Max(0.01f, RM_RustCathedralSettings.borehulkGrindMtbHours) * GenDate.TicksPerHour;
            if (!Rand.MTBEventOccurs(mtbTicks, 1f, interval))
            {
                return;
            }
            Grind(pawn);
        }

        private void Grind(Pawn pawn)
        {
            Map map = pawn.Map;
            Props.grindSound?.PlayOneShot(SoundInfo.InMap(new TargetInfo(pawn.Position, map)));
            IntVec3 front = pawn.Position + pawn.Rotation.FacingCell;
            Vector3 loc = front.InBounds(map) ? front.ToVector3Shifted() : pawn.DrawPos;
            for (int i = 0; i < 3; i++)
            {
                FleckMaker.ThrowMicroSparks(loc, map);
            }
            grindCount++;
        }

        public override string CompInspectStringExtra()
        {
            switch (state)
            {
                case RM_BorehulkDrillState.Worn:
                    return "Its drill head is worn to a stub.";
                case RM_BorehulkDrillState.Unbitted:
                    return "Its drill head is gone.";
                case RM_BorehulkDrillState.Restored:
                    return "A refurbished drill head is fitted.";
            }
            return null;
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (!DebugSettings.ShowDevGizmos)
            {
                yield break;
            }
            yield return new Command_Action
            {
                defaultLabel = "DEV: drill state " + state + " -> next",
                action = delegate
                {
                    state = (RM_BorehulkDrillState)(((int)state + 1) % 3);
                }
            };
            yield return new Command_Action
            {
                defaultLabel = "DEV: grind now (count " + grindCount + ")",
                action = delegate
                {
                    if (parent is Pawn p && p.Spawned)
                    {
                        Grind(p);
                    }
                }
            };
        }
    }
}
