using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.RustCathedral
{
    // ════════════════════════════════════════════════════════════════════
    // RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1 §4 — the borehulk's worn drill, and
    // RUSTCATHEDRAL_WORN_BIT_ARC_1 — the arc that moves it.
    //
    // Worn: every so often (MTB, Mod Settings) while standing still it scrapes
    // the plate — RM_BorehulkGrind plus micro-sparks, no cell mined, and
    // grindCount ticks up. Unbitted and Restored never grind. The arc's saved
    // progress lives here; its world state lives in RM_WornBitGame. A dev-mode
    // gizmo still sets any state so a per-state read needs no arc run.
    //
    // Also records the last harming instigator for
    // RM_JobGiver_BorehulkBackAway (it backs away from that pawn; it never
    // attacks it).
    //
    // NOT BUILT: the per-state body graphic swap. All three states draw the
    // Worn sprite until the Unbitted/Restored edit art exists, so a render node
    // keyed on State is owed WITH that art, not before it.
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

        // RUSTCATHEDRAL_WORN_BIT_ARC_1 stage 1: saved, so a wandering hulk resumes on the next visit.
        public float unbitProgress;

        // Stage 4.
        public float restoreProgress;
        public RM_WornBitChoice choice = RM_WornBitChoice.None;
        public Dictionary<ThingDef, int> delivered = new Dictionary<ThingDef, int>();

        // After restoration.
        public int lastServiceTick;
        public int lastSelfBoreTick;
        public int cellsMined;
        public int sacredCellsMined;
        public string favourLine;

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
            Scribe_Values.Look(ref unbitProgress, "borehulkUnbitProgress", 0f);
            Scribe_Values.Look(ref restoreProgress, "borehulkRestoreProgress", 0f);
            Scribe_Values.Look(ref choice, "borehulkChoice", RM_WornBitChoice.None);
            Scribe_Collections.Look(ref delivered, "borehulkDelivered", LookMode.Def, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && delivered == null)
            {
                delivered = new Dictionary<ThingDef, int>();
            }
            Scribe_Values.Look(ref lastServiceTick, "borehulkLastServiceTick", 0);
            Scribe_Values.Look(ref lastSelfBoreTick, "borehulkLastSelfBoreTick", 0);
            Scribe_Values.Look(ref cellsMined, "borehulkCellsMined", 0);
            Scribe_Values.Look(ref sacredCellsMined, "borehulkSacredCellsMined", 0);
            Scribe_Values.Look(ref favourLine, "borehulkFavourLine");
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
            KeepMechEnergyFull();
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

        // A colony mech grows Need_MechEnergy; the borehulk has no charger in the fiction and stands idle for want of
        // SERVICE instead, never for want of a charge.
        private void KeepMechEnergyFull()
        {
            if (parent is Pawn { needs: { energy: not null } } pawn)
            {
                pawn.needs.energy.CurLevelPercentage = 1f;
            }
        }

        public bool Kept => state == RM_BorehulkDrillState.Restored && parent.Faction == Faction.OfPlayer;

        public bool FreedWild => state == RM_BorehulkDrillState.Restored && parent.Faction == null;

        public float MaintenanceLeft => Kept && RM_RustCathedralSettings.wornBitMaintenanceEnabled
            ? RM_WornBitKernel.MaintenanceLeft(Find.TickManager.TicksGame, lastServiceTick, MaintenanceIntervalTicks)
            : 1f;

        public static int MaintenanceIntervalTicks => Mathf.RoundToInt(RM_RustCathedralSettings.wornBitMaintenanceDays * GenDate.TicksPerDay);

        public bool MayDigKept => Kept && RM_WornBitKernel.KeptMayDig(RM_RustCathedralSettings.wornBitMaintenanceEnabled,
            Find.TickManager.TicksGame, lastServiceTick, MaintenanceIntervalTicks);

        public int Delivered(ThingDef def)
        {
            return delivered.TryGetValue(def, out int n) ? n : 0;
        }

        public void Deliver(ThingDef def, int count)
        {
            delivered[def] = Delivered(def) + count;
        }

        public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
        {
            foreach (FloatMenuOption o in base.CompFloatMenuOptions(selPawn))
            {
                yield return o;
            }
            foreach (FloatMenuOption o in RM_WornBit.Options(this, selPawn))
            {
                yield return o;
            }
        }

        public override void PostDrawExtraSelectionOverlays()
        {
            base.PostDrawExtraSelectionOverlays();
            if (Kept && parent.Spawned)
            {
                RM_WornBit.DigArea(parent.Map)?.MarkForDraw();
            }
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
            return RM_WornBit.InspectLines(this, InspectLine());
        }

        private string InspectLine()
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
            foreach (Gizmo g in RM_WornBit.Gizmos(this))
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
