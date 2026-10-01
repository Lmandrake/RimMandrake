using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_SAP_SUCKER_GUILD_1 (fever_wood_deep_and_mud_2026-09-23.md
    // §6/§6g/§6n, fever_wood_fauna_roster_2026-09-23.md §2). The guild's
    // shared rule, generalised from the thornbug's own nectar contract:
    // "clamped to bark, drinks sap, does not flee... they differ only in
    // how they refuse to be bothered." This class is that refusal, in its
    // hediff-based expression — vaulm seals itself (RM_Hediff_SapSealed),
    // drommath swells (RM_Hediff_Swollen). Ollareth's scream carries no
    // hediff at all ("nothing directly" — its value is the alarm it
    // raises), so its scream is RM_CompProperties_PlantAlarm
    // (RimMandrake.CreatureBehaviors, already a hard dependency of this
    // mod); it also carries this comp with NO hediff, solely so the
    // mishandle trigger below can reach its alarm.
    //
    // Trigger 1 — damage: PostPostApplyDamage — verified real, non-ref
    // signature (RimMandrake.CreatureBehaviors.RM_CompPlantAlarm/
    // RM_CompGrappler/RM_CompDefensiveDischarge already ship this exact
    // override in this repo, called from ThingWithComps.PostApplyDamage).
    // Deterministic and cooldown-gated, never a random roll — the design
    // doc's own explicit requirement ("Do not ship a random chance of
    // refusal") — so a rancher who keeps a bothered animal away from further
    // hits sees the refusal exactly once per cooldown window, never at random.
    //
    // Trigger 2 — mishandled (§6n): a FAILED taming attempt calls
    // NotifyMishandled() from RM_Patch_SapSuckerMishandle, a Harmony postfix
    // on Pawn_MindState.CheckStartMentalStateBecauseRecruitAttempted
    // (FEVERWOOD_SAP_SUCKER_MISHANDLE_HOOK_1). Same cooldown, same hediff;
    // and if the same pawn also carries RM_CompPlantAlarm (ollareth), the
    // alarm is rung too — a failed tame is not damage, so PlantAlarm's own
    // PostPostApplyDamage never sees it. Not covered: failed TRAINING of an
    // already-tame animal, which does not pass through that seam.
    public class RM_CompSapSuckerRefusal : ThingComp
    {
        private int lastTriggeredTick = -999999;

        public RM_CompProperties_SapSuckerRefusal Props => (RM_CompProperties_SapSuckerRefusal)props;

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            TryRefuse();
        }

        /// <summary>Called by RM_Patch_SapSuckerMishandle on a failed tame.
        /// <paramref name="tamer"/> is unused today; kept so a future variant
        /// can aim responders at the handler.</summary>
        public void NotifyMishandled(Pawn tamer)
        {
            if (!TryRefuse())
            {
                return;
            }
            parent.GetComp<RimMandrake.CreatureBehaviors.RM_CompPlantAlarm>()?.TriggerAlarm();
        }

        // True when the refusal actually fired (alive, not on cooldown).
        private bool TryRefuse()
        {
            if (!(parent is Pawn pawn) || pawn.Dead || pawn.health == null)
            {
                return false;
            }

            int now = Find.TickManager.TicksGame;
            if (now - lastTriggeredTick < Props.cooldownTicks)
            {
                return false;
            }
            lastTriggeredTick = now;

            if (Props.refusalHediff == null)
            {
                return true; // ollareth: no hediff, its alarm is the refusal
            }

            Hediff hediff = pawn.health.hediffSet.GetFirstHediffOfDef(Props.refusalHediff);
            if (hediff == null)
            {
                hediff = HediffMaker.MakeHediff(Props.refusalHediff, pawn);
                hediff.Severity = Props.refusalSeverity;
                pawn.health.AddHediff(hediff);
            }
            else
            {
                hediff.Severity = Props.refusalSeverity;
            }
            return true;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastTriggeredTick, "lastTriggeredTick", -999999);
        }
    }
}
