using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.TheForge
{
    // ════════════════════════════════════════════════════════════════════
    // FORGE_CYCLE_MECHANICS_1 — creatures that keep the mountain's clock.
    //
    // Same shape as RM_CompPanSleeper (FloodedCanyon, CRACKEDLANDS_MECHANICS_
    // BUILD_1 §4), keyed to the Forge's weather instead of water: it drives
    // stock CompCanBeDormant, which the def must also carry with
    // startsDormant + jobDormancy + freezeNeeds (jobDormancy is what HOLDS a
    // pawn asleep: ToSleep starts Wait_AsleepDormancy).
    //
    //   awakeDuringRain         awake while boiling rain falls (grand-cycle
    //                           rain phase or any pulse burst) — the dhokkur.
    //   awakeDuringFlashWindow  awake while RM_MapComponent_FlashCycle's
    //                           window is open — the julmox grazing the moss
    //                           film, the dhuvvox swarm erupting from its
    //                           nodules.
    //   Otherwise it seals where it stands. Never while owned by a faction
    //   (a tamed julmox is the player's and stays awake), drafted, downed or
    //   in a mental state; and not within minAwakeHours of waking, so a
    //   pawn woken by damage (stock CompWakeUpDormant) gets to answer it.
    //
    // The sealed LOOK is RM_PawnRenderNodeWorker_DormantBody, reading
    // IsSealed below. Toggle: RM_TheForgeSettings.cycleDormancyEnabled; off
    // wakes every sealed pawn and never seals again.
    // ════════════════════════════════════════════════════════════════════
    public class CompProperties_ForgeCycleDormancy : CompProperties
    {
        public bool awakeDuringRain = true;
        public bool awakeDuringFlashWindow = false;
        public int checkIntervalTicks = 250;
        public float minAwakeHours = 2f;
        public string wakeMessage;

        // FORGE_GPT_ENRICHMENT_1 §7, the dhuvvox clock. With runClock on, an
        // awake pawn shows a countdown to the end of its run, slows for the
        // run's final slowFinalHours (spec: "the final quarter-hour") under
        // slowHediff, and visibly curls back into its nodule when it seals.
        // wakeSound plays where it opens ("nodules click open").
        public bool runClock = false;
        public float slowFinalHours = 0.25f;
        public HediffDef slowHediff;
        public SoundDef wakeSound;

        public CompProperties_ForgeCycleDormancy()
        {
            compClass = typeof(RM_CompForgeCycleDormancy);
        }
    }

    public class RM_CompForgeCycleDormancy : ThingComp
    {
        private int awakeSinceTick = -1;
        private bool initialCheckDone;

        public CompProperties_ForgeCycleDormancy Props => (CompProperties_ForgeCycleDormancy)props;

        private CompCanBeDormant Dormant => parent.TryGetComp<CompCanBeDormant>();

        // RM_MapComponent_FlashCycle keeps its window end private and lives in
        // the shared EnvironmentalHazards assembly; read it rather than widen
        // that assembly's surface for one consumer.
        private static readonly AccessTools.FieldRef<RM_MapComponent_FlashCycle, int> FlashWindowEnd =
            AccessTools.FieldRefAccess<RM_MapComponent_FlashCycle, int>("windowEndTick");

        // One "curling back" message per map per in-game hour, not one per pawn.
        private static readonly Dictionary<int, int> lastCurlMessageTick = new Dictionary<int, int>();

        private bool ClockOn => Props.runClock && RM_TheForgeSettings.Active(RM_TheForgeSettings.dhuvvoxClockEnabled);

        /// <summary>True while the stock dormancy holds this pawn asleep. The
        /// render worker and state reads use this.</summary>
        public bool IsSealed
        {
            get
            {
                CompCanBeDormant d = Dormant;
                return d != null && !d.Awake;
            }
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.Spawned || !parent.IsHashIntervalTick(Props.checkIntervalTicks))
            {
                return;
            }
            Check();
        }

        public bool ShouldBeAwakeNow()
        {
            Map map = parent.Map;
            if (map == null)
            {
                return true;
            }
            if (Props.awakeDuringRain && RM_ForgeCycleUtility.RainingNow(map))
            {
                return true;
            }
            if (Props.awakeDuringFlashWindow && RM_ForgeCycleUtility.FlashWindowNow(map))
            {
                return true;
            }
            return false;
        }

        private void Check()
        {
            CompCanBeDormant d = Dormant;
            Pawn pawn = parent as Pawn;
            if (d == null || pawn == null || pawn.Dead)
            {
                return;
            }

            bool enabled = RM_TheForgeSettings.Active(RM_TheForgeSettings.cycleDormancyEnabled);
            bool wantAwake = !enabled || ShouldBeAwakeNow();

            if (!d.Awake)
            {
                if (wantAwake || !CanSeal(pawn))
                {
                    d.WakeUp();
                    awakeSinceTick = Find.TickManager.TicksGame;
                    DirtyGraphics(pawn);
                    if (wantAwake && ClockOn && pawn.Spawned)
                    {
                        Props.wakeSound?.PlayOneShot(SoundInfo.InMap(new TargetInfo(pawn.Position, pawn.Map)));
                        FleckMaker.ThrowMicroSparks(pawn.DrawPos, pawn.Map);
                    }
                    if (enabled && !Props.wakeMessage.NullOrEmpty() && !pawn.Position.Fogged(pawn.Map))
                    {
                        Messages.Message(Props.wakeMessage.Formatted(pawn.LabelShort).CapitalizeFirst(),
                            pawn, MessageTypeDefOf.NeutralEvent, historical: false);
                    }
                }
                return;
            }

            // First check on a fresh pawn: with jobDormancy, startsDormant
            // alone never puts it to sleep (Awake reads the job and a fresh
            // pawn has none — RM_CompPanSleeper's note), so the initial seal
            // is issued here, with no minimum-awake wait.
            // (A pawn woken by something else — stock wake-on-damage — also
            // arrives here with no stamp; it is stamped now and gets the
            // full minimum awake time.)
            bool firstCheck = !initialCheckDone;
            initialCheckDone = true;
            if (awakeSinceTick < 0)
            {
                awakeSinceTick = Find.TickManager.TicksGame;
            }
            UpdateSlowing(pawn, wantAwake);
            if (wantAwake || !CanSeal(pawn))
            {
                return;
            }
            if (!firstCheck && Find.TickManager.TicksGame - awakeSinceTick < Props.minAwakeHours * 2500f)
            {
                return;
            }
            d.ToSleep();
            awakeSinceTick = -1;
            DirtyGraphics(pawn);
            if (!firstCheck)
            {
                CurlBack(pawn);
            }
        }

        // ── §7 the dhuvvox clock ─────────────────────────────────────

        /// <summary>The tick this pawn's run ends: the flash window's end
        /// while it is open, else the grand cycle's rain-phase end while the
        /// rain falls. -1 when no end is known (a plain pulse burst).</summary>
        public int RunEndTick()
        {
            Map map = parent.Map;
            if (map == null)
            {
                return -1;
            }
            if (Props.awakeDuringFlashWindow && RM_ForgeCycleUtility.FlashWindowNow(map))
            {
                RM_MapComponent_FlashCycle flash = map.GetComponent<RM_MapComponent_FlashCycle>();
                return flash != null ? FlashWindowEnd(flash) : -1;
            }
            if (Props.awakeDuringRain)
            {
                RM_GameCondition_ForgeCycle cycle = RM_ForgeCycleUtility.CycleOn(map);
                if (cycle != null && RM_GameCondition_ForgeCycle.CycleActive && cycle.Phase == ForgeCyclePhase.Rain)
                {
                    return cycle.PhaseEndTick;
                }
            }
            return -1;
        }

        private void UpdateSlowing(Pawn pawn, bool wantAwake)
        {
            HediffDef slow = Props.slowHediff;
            if (slow == null || pawn.health == null)
            {
                return;
            }
            bool want = false;
            if (ClockOn && wantAwake)
            {
                int end = RunEndTick();
                int left = end - Find.TickManager.TicksGame;
                want = end > 0 && left > 0 && left <= Props.slowFinalHours * 2500f;
            }
            Hediff have = pawn.health.hediffSet.GetFirstHediffOfDef(slow);
            if (want && have == null)
            {
                pawn.health.AddHediff(slow);
            }
            else if (!want && have != null)
            {
                pawn.health.RemoveHediff(have);
            }
        }

        // The run is over: the pawn stays (sealed, drawn as its nodule by
        // RM_PawnRenderNodeWorker_DormantBody); this is only the visible curl.
        private void CurlBack(Pawn pawn)
        {
            if (!ClockOn || !pawn.Spawned)
            {
                return;
            }
            Map map = pawn.Map;
            Hediff slow = Props.slowHediff != null ? pawn.health.hediffSet.GetFirstHediffOfDef(Props.slowHediff) : null;
            if (slow != null)
            {
                pawn.health.RemoveHediff(slow);
            }
            FleckMaker.ThrowDustPuffThick(pawn.DrawPos, map, 0.7f, new Color(0.55f, 0.35f, 0.25f));
            FleckMaker.ThrowMicroSparks(pawn.DrawPos, map);
            if (pawn.Position.Fogged(map))
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (lastCurlMessageTick.TryGetValue(map.uniqueID, out int last) && now - last < 2500)
            {
                return;
            }
            lastCurlMessageTick[map.uniqueID] = now;
            Messages.Message("The " + pawn.def.label + " run is over: they are curling back into their nodules where they stand.",
                pawn, MessageTypeDefOf.NeutralEvent, historical: false);
        }

        private static bool CanSeal(Pawn pawn)
        {
            return pawn.Faction == null && !pawn.Downed && !pawn.InMentalState
                && (pawn.drafter == null || !pawn.Drafted)
                && (pawn.mindState == null || pawn.mindState.enemyTarget == null);
        }

        private static void DirtyGraphics(Pawn pawn)
        {
            if (pawn.Spawned && pawn.Drawer != null && pawn.Drawer.renderer != null)
            {
                pawn.Drawer.renderer.SetAllGraphicsDirty();
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.cycleDormancyEnabled) || Dormant == null)
            {
                return null;
            }
            if (IsSealed)
            {
                return "Sealed, waiting out the dry.";
            }
            if (!ClockOn)
            {
                return null;
            }
            int end = RunEndTick();
            int left = end - Find.TickManager.TicksGame;
            if (end < 0 || left <= 0)
            {
                return null;
            }
            string line = "Run ends in " + left.ToStringTicksToPeriod() + ", then it curls back into its nodule.";
            if (left <= Props.slowFinalHours * 2500f)
            {
                line += " Slowing.";
            }
            return line;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref awakeSinceTick, "forgeAwakeSinceTick", -1);
            Scribe_Values.Look(ref initialCheckDone, "forgeInitialCheckDone", false);
        }
    }
}
