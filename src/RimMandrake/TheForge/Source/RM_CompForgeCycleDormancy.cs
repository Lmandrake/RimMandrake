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
        // Scuttle tick while awake: every runSoundIntervalTicks, stretched up to
        // runSoundSlowFactor times across the slowing window.
        public SoundDef runSound;
        public int runSoundIntervalTicks = 70;
        public float runSoundSlowFactor = 4f;

        public CompProperties_ForgeCycleDormancy()
        {
            compClass = typeof(RM_CompForgeCycleDormancy);
        }
    }

    public class RM_CompForgeCycleDormancy : ThingComp
    {
        private int awakeSinceTick = -1;
        private int nextScuttleTick;
        private static readonly Dictionary<int, int> lastSwarmLogTick = new Dictionary<int, int>();
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
            if (Props.runSound != null && ClockOn && parent.Spawned)
            {
                Scuttle();
            }
            if (!parent.Spawned || !parent.IsHashIntervalTick(Props.checkIntervalTicks))
            {
                return;
            }
            Check();
        }

        private void Scuttle()
        {
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.dhuvvoxRunSoundEnabled) || IsSealed)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (now < nextScuttleTick)
            {
                return;
            }
            nextScuttleTick = now + RM_DormancyKernel.ScuttleDelay(Props.runSoundIntervalTicks, RunEndTick(), now, Props.slowFinalHours,
                Props.runSoundSlowFactor, Rand.Range(0.7f, 1.3f));
            if (!parent.Position.Fogged(parent.Map))
            {
                Props.runSound.PlayOneShot(SoundInfo.InMap(new TargetInfo(parent.Position, parent.Map)));
            }
        }

        // Debug-log data for the swarm-aggregation question: how many awake per map.
        private void LogSwarm(Map map)
        {
            int now = Find.TickManager.TicksGame;
            if (lastSwarmLogTick.TryGetValue(map.uniqueID, out int last) && now - last < 2500)
            {
                return;
            }
            lastSwarmLogTick[map.uniqueID] = now;
            int n = 0;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p.def == parent.def && p.TryGetComp<CompCanBeDormant>() is CompCanBeDormant c && c.Awake) n++;
            }
            Log.Message("[TheForge] dhuvvox awake on map " + map.uniqueID + ": " + n);
        }

        public bool ShouldBeAwakeNow()
        {
            Map map = parent.Map;
            return RM_DormancyKernel.ShouldBeAwake(map != null,
                Props.awakeDuringRain, map != null && Props.awakeDuringRain && RM_ForgeCycleUtility.RainingNow(map),
                Props.awakeDuringFlashWindow, map != null && Props.awakeDuringFlashWindow && RM_ForgeCycleUtility.FlashWindowNow(map));
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
            bool wantAwake = RM_DormancyKernel.WantAwake(enabled, ShouldBeAwakeNow());
            int now = Find.TickManager.TicksGame;

            // The decision (wake, seal, or stay) is Kernel/RM_DormancyKernel.cs; this applies it. A fresh pawn's first check
            // issues the initial seal with no minimum-awake wait (with jobDormancy, startsDormant alone never puts it to sleep:
            // Awake reads the job and a fresh pawn has none, RM_CompPanSleeper's note); a pawn woken by something else, stock
            // wake-on-damage included, is stamped now and gets the full minimum awake time.
            DormancyState st = new DormancyState { awakeSinceTick = awakeSinceTick, initialCheckDone = initialCheckDone };
            bool canSeal = CanSeal(pawn);
            DormancyResult res = RM_DormancyKernel.Check(ref st, d.Awake, wantAwake, canSeal, now, Props.minAwakeHours);
            awakeSinceTick = st.awakeSinceTick;
            initialCheckDone = st.initialCheckDone;

            if (res.action == DormancyAction.WakeUp)
            {
                d.WakeUp();
                DirtyGraphics(pawn);
                if (wantAwake && ClockOn && pawn.Spawned)
                {
                    Props.wakeSound?.PlayOneShot(SoundInfo.InMap(new TargetInfo(pawn.Position, pawn.Map)));
                    FleckMaker.ThrowMicroSparks(pawn.DrawPos, pawn.Map);
                    LogSwarm(pawn.Map);
                }
                if (enabled && !Props.wakeMessage.NullOrEmpty() && !pawn.Position.Fogged(pawn.Map))
                {
                    Messages.Message(Props.wakeMessage.Formatted(pawn.LabelShort).CapitalizeFirst(),
                        pawn, MessageTypeDefOf.NeutralEvent, historical: false);
                }
                return;
            }
            if (res.slowingUpdate)
            {
                UpdateSlowing(pawn, wantAwake);
            }
            if (res.action == DormancyAction.ToSleep)
            {
                d.ToSleep();
                DirtyGraphics(pawn);
                if (res.curlBack)
                {
                    CurlBack(pawn);
                }
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
            bool flashOpen = Props.awakeDuringFlashWindow && RM_ForgeCycleUtility.FlashWindowNow(map);
            int flashEnd = -1;
            if (flashOpen)
            {
                RM_MapComponent_FlashCycle flash = map.GetComponent<RM_MapComponent_FlashCycle>();
                flashEnd = flash != null ? FlashWindowEnd(flash) : -1;
            }
            int phaseEnd = -1;
            bool raining = false;
            if (!flashOpen && Props.awakeDuringRain)
            {
                RM_GameCondition_ForgeCycle cycle = RM_ForgeCycleUtility.CycleOn(map);
                raining = cycle != null && RM_GameCondition_ForgeCycle.CycleActive && cycle.Phase == ForgeCyclePhase.Rain;
                phaseEnd = raining ? cycle.PhaseEndTick : -1;
            }
            return RM_DormancyKernel.RunEnd(true, Props.awakeDuringFlashWindow, flashOpen, flashEnd, Props.awakeDuringRain, raining, phaseEnd);
        }

        private void UpdateSlowing(Pawn pawn, bool wantAwake)
        {
            HediffDef slow = Props.slowHediff;
            if (slow == null || pawn.health == null)
            {
                return;
            }
            bool want = ClockOn && wantAwake
                && RM_DormancyKernel.SlowWanted(true, true, RunEndTick(), Find.TickManager.TicksGame, Props.slowFinalHours);
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
            return RM_DormancyKernel.CanSeal(pawn.Faction == null, pawn.Downed, pawn.InMentalState,
                pawn.drafter != null && pawn.Drafted, pawn.mindState != null && pawn.mindState.enemyTarget != null);
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
