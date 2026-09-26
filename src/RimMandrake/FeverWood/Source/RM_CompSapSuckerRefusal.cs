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
    // raises), so it uses RM_CompProperties_PlantAlarm
    // (RimMandrake.CreatureBehaviors, already a hard dependency of this
    // mod) instead of this class — see RM_SapSuckerGuild.xml's header.
    //
    // Trigger: PostPostApplyDamage — verified real, non-ref signature
    // (RimMandrake.CreatureBehaviors.RM_CompPlantAlarm/RM_CompGrappler/
    // RM_CompDefensiveDischarge already ship this exact override in this
    // repo, called from ThingWithComps.PostApplyDamage). Deterministic and
    // cooldown-gated, never a random roll — the design doc's own explicit
    // requirement ("Do not ship a random chance of refusal") — so a
    // rancher who keeps a bothered animal away from further hits sees the
    // refusal exactly once per cooldown window, never at random.
    //
    // What this does NOT do, on purpose: detect "mishandled during a
    // failed taming/training attempt" (§6n's other trigger half, alongside
    // "frightened"). Which job/interaction hook fires on a failed handling
    // attempt is a real engine question this pass could not verify against
    // source (RimSage does not connect from this machine — CLAUDE.md's
    // "engine-internals question is UNMEASURABLE on the laptop") and did
    // not want to guess at. Damage-taken is the trigger this pass could
    // verify and ship for real; FEVERWOOD_SAP_SUCKER_TUNING_1 owns the
    // mishandling half plus every INVENTED number this file and its XML
    // carry.
    public class RM_CompSapSuckerRefusal : ThingComp
    {
        private int lastTriggeredTick = -999999;

        public RM_CompProperties_SapSuckerRefusal Props => (RM_CompProperties_SapSuckerRefusal)props;

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            TryRefuse();
        }

        private void TryRefuse()
        {
            if (!(parent is Pawn pawn) || pawn.Dead || pawn.health == null)
            {
                return;
            }

            int now = Find.TickManager.TicksGame;
            if (now - lastTriggeredTick < Props.cooldownTicks)
            {
                return;
            }
            lastTriggeredTick = now;

            if (Props.refusalHediff == null)
            {
                return;
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
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastTriggeredTick, "lastTriggeredTick", -999999);
        }
    }
}
