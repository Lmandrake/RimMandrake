using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FloodedCanyon
{
    // ════════════════════════════════════════════════════════════════════
    // CRACKEDLANDS_MECHANICS_BUILD_1 §4 — THE MUTTAVAQ'S SLEEP CYCLE.
    //
    // The RM_-tier member of the built CompWaterWakeTrigger family
    // (src/RimUtinni/UtinniPatches/Source/RUT_CompWaterWakeTrigger.cs lives in
    // the Utinni tier, which an RM_ mod may not depend on — so this is the
    // same mechanism, re-stated here at giant scale, plus the half the
    // sleeper never needed: going back to sleep).
    //
    //   WAKE    asleep + water terrain (not scalding) within wakeRadius
    //           -> CompCanBeDormant.WakeUp(), the stock wake path. FlowWorks
    //           renders an excavated cell's fill as water terrain, so a
    //           flooded channel wakes it exactly as the flood wall does.
    //   DIG IN  awake + no flood standing on the map + no water within
    //           wakeRadius for dryHoursToDigIn -> CompCanBeDormant.ToSleep()
    //           where it stands ("digs in + seals where it stands at the
    //           dry"). Never while drafted, downed, in a mental state, or
    //           owned by a faction (a tamed/owned one is the player's).
    //   HOLD    the stock dormancy only HOLDS a pawn asleep when
    //           jobDormancy is true (CompCanBeDormant.Awake/ToSleep, read in
    //           RimSage 2026-09-29): ToSleep starts Wait_AsleepDormancy. The
    //           def sets jobDormancy; on first spawn this comp issues the
    //           initial ToSleep that startsDormant alone does not (with
    //           jobDormancy, Awake reads the job, and a fresh pawn has none).
    //           If something else replaces the sleep job while it should be
    //           sealed (wokeUpTick still unset), the next check re-seals it.
    //
    // Mechanics read, not guessed: CompCanBeDormant.WakeUp/ToSleep are
    // public virtual; wokeUpTick is public and is int.MinValue exactly while
    // nothing has woken it; freezeNeeds is honoured by Need.IsFrozen, which is
    // how a years-long sleep does not starve it (set on the def).
    // ════════════════════════════════════════════════════════════════════
    public class CompProperties_PanSleeper : CompProperties
    {
        public float wakeRadius = 2.9f;

        // Coarse on purpose: terrain only changes on a flood/liquid event.
        public int checkIntervalTicks = 500;

        // How long its ground must stay dry (after the flood has ended)
        // before it digs in.
        public float dryHoursToDigIn = 12f;

        // Optional ground-drop on wake (the bible: the sleeper's wake-drop,
        // scaled up). By NAME, resolved silently: crack-wax is a Utinni-tier
        // def (RUT_CrackWax) and this RM_ mod must load without it.
        public string wakeDropDefName;
        public IntRange wakeDropCount = new IntRange(0, 0);

        public CompProperties_PanSleeper()
        {
            compClass = typeof(RM_CompPanSleeper);
        }
    }

    public class RM_CompPanSleeper : ThingComp
    {
        private bool initialSealDone;
        private bool sealedAsleep;
        private int dryAccumTicks;

        public CompProperties_PanSleeper Props => (CompProperties_PanSleeper)props;

        private CompCanBeDormant Dormant => parent.TryGetComp<CompCanBeDormant>();

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.Spawned || !parent.IsHashIntervalTick(Props.checkIntervalTicks))
            {
                return;
            }
            Check();
        }

        private void Check()
        {
            CompCanBeDormant d = Dormant;
            Pawn pawn = parent as Pawn;
            if (d == null || pawn == null || pawn.Dead)
            {
                return;
            }
            // The initial seal is issued from the first check, never from
            // PostSpawnSetup: starting a job while the pawn is still mid-spawn
            // is not something to rely on.
            if (!initialSealDone)
            {
                initialSealDone = true;
                if (d.Props.startsDormant && d.wokeUpTick == int.MinValue && CanSeal(pawn))
                {
                    Seal(d);
                    return;
                }
            }

            bool water = WaterNear();

            if (sealedAsleep)
            {
                if (d.wokeUpTick != int.MinValue)
                {
                    // Woken by something else (the stock wake-on-damage).
                    sealedAsleep = false;
                    dryAccumTicks = 0;
                    return;
                }
                if (water && RM_FloodedCanyonSettings.muttavaqWaterWakeEnabled)
                {
                    Wake(d);
                    return;
                }
                // Should be asleep but the sleep job was replaced — re-seal.
                if (d.Awake && CanSeal(pawn))
                {
                    d.ToSleep();
                }
                return;
            }

            if (!RM_FloodedCanyonSettings.muttavaqDigInEnabled || !d.Awake)
            {
                return;
            }
            RM_MapComponent_CanyonFlood flood = parent.Map.GetComponent<RM_MapComponent_CanyonFlood>();
            if (water || (flood != null && flood.IsFlooding))
            {
                dryAccumTicks = 0;
                return;
            }
            dryAccumTicks += Props.checkIntervalTicks;
            if (dryAccumTicks >= Props.dryHoursToDigIn * 2500f && CanSeal(pawn))
            {
                Seal(d);
            }
        }

        private static bool CanSeal(Pawn pawn)
        {
            return pawn.Faction == null && !pawn.Downed && !pawn.InMentalState
                && (pawn.drafter == null || !pawn.Drafted);
        }

        private bool WaterNear()
        {
            Map map = parent.Map;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(parent.Position, Props.wakeRadius, true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                TerrainDef t = c.GetTerrain(map);
                if (t != null && t.IsWater && !(t.burnDamage > 0f))
                {
                    return true;
                }
            }
            return false;
        }

        private void Seal(CompCanBeDormant d)
        {
            // ToSleep() returns early unless Awake. Clearing a stale wake
            // stamp first is what ToSleep itself does (wokeUpTick = MinValue).
            if (d.Awake)
            {
                d.ToSleep();
            }
            sealedAsleep = true;
            dryAccumTicks = 0;
        }

        private void Wake(CompCanBeDormant d)
        {
            sealedAsleep = false;
            dryAccumTicks = 0;
            d.WakeUp();
            DropOnWake();
            if (parent.Spawned && !parent.Position.Fogged(parent.Map))
            {
                Messages.Message(
                    "The water has reached a " + parent.LabelNoCount + "'s pan — it is standing up.",
                    new TargetInfo(parent.Position, parent.Map),
                    MessageTypeDefOf.NeutralEvent);
            }
        }

        private void DropOnWake()
        {
            if (Props.wakeDropDefName.NullOrEmpty() || Props.wakeDropCount.max <= 0)
            {
                return;
            }
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(Props.wakeDropDefName);
            if (def == null)
            {
                return;
            }
            int count = Props.wakeDropCount.RandomInRange;
            while (count > 0)
            {
                Thing t = ThingMaker.MakeThing(def);
                t.stackCount = System.Math.Min(count, def.stackLimit);
                count -= t.stackCount;
                GenPlace.TryPlaceThing(t, parent.Position, parent.Map, ThingPlaceMode.Near);
            }
        }

        // Verify surface (state read, never a screenshot): the comp's own
        // view plus the stock comp's.
        public override string CompInspectStringExtra()
        {
            if (!Prefs.DevMode)
            {
                return null;
            }
            CompCanBeDormant d = Dormant;
            return "pan sleeper: sealed=" + sealedAsleep + " awake=" + (d?.Awake.ToString() ?? "no dormancy comp")
                + " dryTicks=" + dryAccumTicks;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref initialSealDone, "initialSealDone", false);
            Scribe_Values.Look(ref sealedAsleep, "sealedAsleep", false);
            Scribe_Values.Look(ref dryAccumTicks, "dryAccumTicks", 0);
        }
    }
}
