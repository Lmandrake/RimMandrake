using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Livestock
{
    // LIVESTOCK_STARTER_TRIO_1 - moornak (grief-eater), the trio's third and
    // last entry (design/Jawa/proposals/ludicrous_livestock_deep_design.md
    // "Moornak - the grief-eater"; owner ruling recorded in the item's
    // ledger 2026-09-10: "the RICHER moornak spec ships - self-tames,
    // arrives grief-loaded, colony-wide unsettled hediff, 30-day release,
    // manhunter on release, sells-never-buys-back"). That richer ruling
    // SUPERSEDES the design doc's own death-triggered "unburdening" valve -
    // this comp implements a data-tuned recurring TIMER release, not a
    // death check, per the ruling's own words ("30-day release... manhunter
    // on release" - no mention of death as the trigger).
    //
    // Zero new job types, same discipline as CompKilnBelly/CompLightAversion:
    // self-taming, the ambient mood effect and the release are all driven
    // off CompTickRare, with no new work-giver or interaction.
    //
    // FULLY HIDDEN per the owner's filing ruling ("moornak's debuff-storage
    // is FULLY HIDDEN - no tell, no research reveal - first loss teaches"):
    // this class deliberately has NO CompInspectStringExtra override and
    // exposes nothing about storedGrief/joinTick anywhere a player can read
    // it. The only visible symptom is the RSW_MoornakUnsettled hediff
    // itself (an ordinary, inspectable mood hediff - the SOURCE ledger
    // behind it is what stays hidden) and, eventually, the release.
    //
    // Self-taming precedent: RimWorld/IncidentWorker_SelfTame.cs's own
    // Candidates() filter (wild, spawned, not fogged, not downed, not in a
    // mental state) confirmed via RimSage search_source - reused here as
    // the per-tick gate for an individual, tunable MTB roll instead of
    // relying on the global SelfTame incident (which fires at most once
    // across the whole map's wild population and is not species-specific).
    //
    // Manhunter-on-release precedent: Verse/Hediff_Scaria.cs calls
    // `pawn.mindState.mentalStateHandler.TryStartMentalState(
    // MentalStateDefOf.ManhunterPermanent)` unconditionally on a pawn that
    // may already be player-owned - confirmed via RimSage read_csharp_symbol
    // that ManhunterPermanent is not gated on Faction, so triggering it on
    // an already-tamed moornak is the same call vanilla itself already uses
    // on a tamed animal.
    //
    // NOT live-verified this pass (offline build only, matching onnik's and
    // karrask's own precedent - see LIVESTOCK_STARTER_TRIO_1's item file).
    public class CompProperties_MoornakGrief : CompProperties
    {
        // Self-taming: "extremely readily" per the owner's original filing
        // note (row 38, ludicrous_livestock_deep_design.md) - a short mean
        // time between rolls while wild, spawned and not already claimed.
        public float selfTameMtbDays = 3f;

        // "Arrives already grief-loaded" - the hidden ledger starts above
        // zero the moment the Thing is created, not at zero waiting to be
        // fed.
        public float initialGriefCharge = 0.4f;
        public float griefChargePerDay = 0.05f;
        public float maxGriefCharge = 1f;

        // Colony-wide "unsettled" while present - refreshed every rare tick
        // toward a target severity so it decays away on its own
        // (HediffCompProperties_SeverityPerDay, on the hediff itself) if the
        // moornak ever leaves or dies.
        public HediffDef unsettledHediffDef;
        public float unsettledTargetSeverity = 0.6f;
        public float unsettledSeverityStep = 0.05f;

        // "Should last 30 days" (row 38) read, per the later and more
        // specific ruling this item actually ships, as a recurring 30-day
        // release timer rather than a one-time post-death duration.
        public int releaseDelayTicks = GenDate.TicksPerDay * 30;
        public float releaseSpikeSeverity = 1f;

        public CompProperties_MoornakGrief() => compClass = typeof(CompMoornakGrief);
    }

    public class CompMoornakGrief : ThingComp
    {
        private CompProperties_MoornakGrief Props => (CompProperties_MoornakGrief)props;

        // Hidden ledger - never exposed via CompInspectStringExtra or any
        // other player-facing string. joinTick < 0 means "timer not
        // running yet" (still wild, or not yet noticed as player-owned).
        private float storedGrief;
        private int joinTick = -1;

        public override void PostPostMake()
        {
            base.PostPostMake();
            storedGrief = Props.initialGriefCharge;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref storedGrief, "storedGrief", 0f);
            Scribe_Values.Look(ref joinTick, "joinTick", -1);
        }

        public override void CompTickRare()
        {
            if (!RSW_LivestockSettings.moornakGriefEnabled) return;
            if (!(parent is Pawn pawn) || !pawn.Spawned) return;

            TrySelfTame(pawn);

            if (joinTick < 0 && pawn.Faction == Faction.OfPlayer)
            {
                joinTick = Find.TickManager.TicksGame;
            }

            if (pawn.Map != null)
            {
                ApplyUnsettled(pawn.Map);
            }

            storedGrief = Mathf.Min(storedGrief + Props.griefChargePerDay
                * (GenTicks.TickRareInterval / (float)GenDate.TicksPerDay), Props.maxGriefCharge);

            int delay = Mathf.RoundToInt(Props.releaseDelayTicks * RSW_LivestockSettings.moornakReleaseDelayMultiplier);
            if (joinTick >= 0 && Find.TickManager.TicksGame - joinTick >= delay)
            {
                Release(pawn);
            }
        }

        // Same wild/spawned/not-fogged/not-downed/not-already-in-a-mental-
        // state gate as vanilla's own IncidentWorker_SelfTame.Candidates(),
        // rolled per individual instead of once map-wide.
        private void TrySelfTame(Pawn pawn)
        {
            if (pawn.Faction != null) return;
            if (pawn.Downed || pawn.InMentalState) return;
            if (pawn.Position.Fogged(pawn.Map)) return;

            if (Rand.MTBEventOccurs(Props.selfTameMtbDays, GenDate.TicksPerDay, GenTicks.TickRareInterval))
            {
                pawn.SetFaction(Faction.OfPlayer);
                // Plain string, not a Keyed translation key - this mod's
                // Livestock source ships no Languages/Keyed table of its
                // own (confirmed by grep before adding this), and per the
                // owner's hidden-mechanism ruling this message must say
                // only that the animal joined, nothing about what it
                // carries.
                Messages.Message(
                    pawn.LabelIndefinite().CapitalizeFirst() + " has quietly joined the colony.",
                    pawn, MessageTypeDefOf.NeutralEvent);
            }
        }

        private void ApplyUnsettled(Map map)
        {
            if (Props.unsettledHediffDef == null) return;

            var colonists = map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < colonists.Count; i++)
            {
                Pawn colonist = colonists[i];
                Hediff hediff = colonist.health.hediffSet.GetFirstHediffOfDef(Props.unsettledHediffDef);
                if (hediff == null)
                {
                    hediff = HediffMaker.MakeHediff(Props.unsettledHediffDef, colonist);
                    hediff.Severity = Props.unsettledSeverityStep;
                    colonist.health.AddHediff(hediff);
                }
                else
                {
                    hediff.Severity = Mathf.Min(hediff.Severity + Props.unsettledSeverityStep,
                        Props.unsettledTargetSeverity);
                }
            }
        }

        // The 30-day discharge: a hard spike of the same unsettled hediff on
        // everyone present (the accrued grief "releasing back onto the
        // colony"), the moornak itself going manhunter, and the ledger
        // re-arming for the next cycle rather than being a one-shot -
        // "keeping one is a slow-growing bomb" per the design doc's own
        // framing, unchanged by which trigger (death vs. timer) fires it.
        private void Release(Pawn pawn)
        {
            if (pawn.Map != null && Props.unsettledHediffDef != null)
            {
                var colonists = pawn.Map.mapPawns.FreeColonistsSpawned;
                for (int i = 0; i < colonists.Count; i++)
                {
                    Pawn colonist = colonists[i];
                    Hediff hediff = colonist.health.hediffSet.GetFirstHediffOfDef(Props.unsettledHediffDef);
                    if (hediff == null)
                    {
                        hediff = HediffMaker.MakeHediff(Props.unsettledHediffDef, colonist);
                        colonist.health.AddHediff(hediff);
                    }
                    hediff.Severity = Props.releaseSpikeSeverity;
                }
            }

            pawn.mindState?.mentalStateHandler?.TryStartMentalState(MentalStateDefOf.ManhunterPermanent);

            storedGrief = Props.initialGriefCharge;
            joinTick = Find.TickManager.TicksGame;
        }
    }
}
