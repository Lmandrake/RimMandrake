using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1 (owner's own words: "Give it great strength to
    // Hold someone with its pincer and slowly crush them each round"). The
    // hediff RM_Grapple_ToolCapacity.xml's DamageDef delivers on a
    // successful pincer hit.
    //
    // Deliberately does NOT call Pawn.TakeDamage on any tick: this hediff's
    // own Tick() runs from inside the victim's HediffSet tick loop, and
    // calling TakeDamage from there risks re-entering that same loop mid-
    // iteration (the exact hazard RM_CompWoundLink's own header already
    // flags for a sibling mechanism). The physical crush — Blunt damage to
    // the torso each round — is dealt from the GRABBER's side instead, by
    // RM_CompGrappler's CompTick, which is outside this loop. This hediff's
    // OWN severity climbing each round (capped by <maxSeverity>) is only the
    // tightening gauge that drives its stages. Releasing the hold by removing this
    // hediff from within its own Tick() is the exact mechanism
    // HediffCompProperties_Disappears already relies on for RUT_MatGrip, so
    // it's a proven-safe idiom in this same assembly.
    //
    // Grappler identity comes from Hediff.PostAdd(DamageInfo? dinfo) —
    // dinfo.Instigator is the attacking pincer's owner, confirmed via
    // RimSage against Pawn_HealthTracker.PostApplyDamage this pass (it
    // passes the same dinfo it used to compute this hediff's initial
    // severity straight into AddHediff, which forwards it to PostAdd).
    public class RM_Hediff_Grappled : HediffWithComps
    {
        private Pawn grappler;
        private int ticksUntilRound;

        public RM_HediffDef_Grapple Def => (RM_HediffDef_Grapple)def;

        /// <summary>Who is holding this pawn — read by RM_CompGrappler on the
        /// grappler's side for the per-round crush and the rescue roll.</summary>
        public Pawn Grappler => grappler;

        /// <summary>Ends the hold from outside (RM_CompGrappler's rescue
        /// roll). Safe to call from any tick that is not this pawn's own
        /// HediffSet iteration.</summary>
        public void ReleaseHold()
        {
            Release();
        }

        public override void PostAdd(DamageInfo? dinfo)
        {
            base.PostAdd(dinfo);

            grappler = dinfo?.Instigator as Pawn;
            ticksUntilRound = Def.roundIntervalTicks;

            // Dedup: a second pincer hit while already grappled shouldn't
            // start a SECOND independent hold ticking down in parallel — it
            // refreshes who's holding (the most recent hit) and this new
            // instance stands down, leaving the original's accumulated
            // severity (and its stage progress) intact.
            var hediffs = pawn.health.hediffSet.hediffs;
            for (int i = 0; i < hediffs.Count; i++)
            {
                if (hediffs[i] is RM_Hediff_Grappled other && other != this)
                {
                    other.grappler = grappler;
                    pawn.health.RemoveHediff(this);
                    return;
                }
            }
        }

        public override void Tick()
        {
            base.Tick();

            if (!RM_CreatureBehaviorsSettings.grapplerHoldEnabled)
            {
                Release();
                return;
            }

            if (pawn == null || pawn.Dead || !pawn.Spawned || pawn.health == null)
            {
                return; // dead/despawned pawns don't need releasing — their hediffs stop mattering
            }

            if (!IsGrapplerStillHolding())
            {
                Release();
                return;
            }

            ticksUntilRound--;
            if (ticksUntilRound > 0)
            {
                return;
            }
            ticksUntilRound = Def.roundIntervalTicks;

            if (Rand.Chance(Def.escapeChancePerRound))
            {
                // Literal, not a translation key: this mod ships no
                // Languages/ folder (same posture as RM_CompPlantAlarm's
                // own inspect string).
                Messages.Message(pawn.LabelShortCap + " breaks free of the hold!", pawn, MessageTypeDefOf.PositiveEvent);
                Release();
                return;
            }

            float mult = UnityEngine.Mathf.Max(0f, RM_CreatureBehaviorsSettings.grapplerCrushMultiplier);
            Severity += Def.severityGainPerRoundPerBodySize * grappler.BodySize * mult;
        }

        private bool IsGrapplerStillHolding()
        {
            if (grappler == null || grappler.Dead || grappler.Downed || !grappler.Spawned)
            {
                return false;
            }

            if (grappler.Map != pawn.Map)
            {
                return false;
            }

            float distSq = (grappler.Position - pawn.Position).LengthHorizontalSquared;
            return distSq <= Def.releaseRadius * Def.releaseRadius;
        }

        private void Release()
        {
            if (pawn != null && pawn.health != null && pawn.health.hediffSet.hediffs.Contains(this))
            {
                pawn.health.RemoveHediff(this);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref grappler, "grappler");
            Scribe_Values.Look(ref ticksUntilRound, "ticksUntilRound", 0);
        }
    }
}
