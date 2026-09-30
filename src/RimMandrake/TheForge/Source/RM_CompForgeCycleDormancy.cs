using RimWorld;
using Verse;

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
            return IsSealed ? "Sealed, waiting out the dry." : null;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref awakeSinceTick, "forgeAwakeSinceTick", -1);
            Scribe_Values.Look(ref initialCheckDone, "forgeInitialCheckDone", false);
        }
    }
}
