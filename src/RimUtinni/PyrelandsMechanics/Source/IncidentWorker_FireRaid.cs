using System.Collections.Generic;
using RimMandrake.Pyrelands;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// PYRELANDS_MECHANICS_1, mechanism 5b — arson-justice
    /// (the_pyrelands.md §8, canonised: "an unplanned burn — a careless camp, a
    /// raider's torch, a player's mistake — is answered as arson-justice: short,
    /// furious Tribes raids against whoever broke the schedule"; §5: "an unplanned
    /// burn is an act of war").
    ///
    /// "UNPLANNED-BURN DETECTION" IS NOT A GUESS. MapComponent_BurnLine attributes
    /// every burning cell through Fire.instigator and accrues arson debt only for
    /// fires the player owns. A lightning burn — the biome's own storm loop —
    /// accrues nothing, so the Tribes never punish the weather. A fire your
    /// colonist lit, or one your TAMED fire-hawk spread, or one your TAMED
    /// furnace-beast smouldered into your pasture, accrues in full. That last
    /// clause is the reversed ban 5 paying its own bill (§8d).
    ///
    /// SHORT AND FURIOUS, mechanically: ImmediateAttack + EdgeWalkIn at a fraction
    /// of the storyteller's threat points. Not a siege, not a drop pod — people
    /// who walked here from the burn-line you ruined.
    ///
    /// The goodwill hit is applied BEFORE the raid and is what flips a neutral
    /// tribe hostile. If it does not flip them (a faction with no goodwill, or one
    /// held friendly by something else), the incident declines to fire rather than
    /// forcing hostility behind the relations system's back — the player still
    /// sees the goodwill message, which is the warning shot.
    /// </summary>
    public class IncidentWorker_FireRaid : IncidentWorker_RaidEnemy
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!PyrelandsMechanicsSettings.arsonJusticeEnabled)
            {
                return false;
            }
            if (!base.CanFireNowSub(parms) || !(parms.target is Map map))
            {
                return false;
            }

            RimMandrake.Pyrelands.MapComponent_BurnLine watch = RimMandrake.Pyrelands.MapComponent_BurnLine.For(map);
            bool pyrelands = watch != null && watch.IsPyrelandsMap;
            Faction tribes = pyrelands ? PyrelandsFactions.TribesOrNull() : null;

            // Debt at the threshold (a threshold above the debt cap counts as the cap: the debt can never exceed it), a
            // Tribes faction already at war, or one that souring would put there.
            return RM_BurnKernel.RaidCanFire(true, true, pyrelands, pyrelands ? watch.ArsonDebt : 0f,
                PyrelandsMechanicsSettings.arsonDebtRaidThreshold, RimMandrake.Pyrelands.PyrelandsTuning.ArsonDebtCap,
                tribes != null, tribes != null && tribes.HostileTo(Faction.OfPlayer), tribes != null && tribes.HasGoodwill);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            if (!(parms.target is Map map))
            {
                return false;
            }

            Faction tribes = PyrelandsFactions.TribesOrNull();
            RM_RaidPlan plan = RM_BurnKernel.RaidPlan(tribes != null, tribes != null && tribes.HostileTo(Faction.OfPlayer),
                tribes != null && tribes.HasGoodwill);
            if (plan == RM_RaidPlan.Refuse)
            {
                return false;
            }

            if (plan == RM_RaidPlan.InsultFirst)
            {
                tribes.TryAffectGoodwillWith(
                    Faction.OfPlayer,
                    RimMandrake.Pyrelands.PyrelandsTuning.FireRaidGoodwillHit,
                    canSendMessage: true,
                    canSendHostilityLetter: true);

                if (!RM_BurnKernel.RaidAfterInsult(tribes.HostileTo(Faction.OfPlayer)))
                {
                    // The insult landed but did not reach war. No raid this time;
                    // the debt stands and the next unplanned burn adds to it.
                    return false;
                }
            }

            parms.faction = tribes;
            parms.raidStrategy = RaidStrategyDefOf.ImmediateAttack;
            parms.raidArrivalMode = PawnsArrivalModeDefOf.EdgeWalkIn;

            parms.points = RM_BurnKernel.RaidPoints(parms.points,
                parms.points <= 0f ? StorytellerUtility.DefaultThreatPointsNow(parms.target) : 0f,
                RimMandrake.Pyrelands.PyrelandsTuning.FireRaidPointsFactor, RimMandrake.Pyrelands.PyrelandsTuning.FireRaidPointsMin);

            if (!base.TryExecuteWorker(parms))
            {
                return false;
            }

            // The debt has been collected. The next raid needs a new burn.
            RimMandrake.Pyrelands.MapComponent_BurnLine.For(map)?.ClearArsonDebt();
            return true;
        }

        protected override string GetLetterLabel(IncidentParms parms)
        {
            return "RUT_FireRaid".Translate();
        }

        protected override string GetLetterText(IncidentParms parms, List<Pawn> pawns)
        {
            // The vanilla raid text still carries the arrival-mode and strategy
            // prose the player needs; this only says WHY, in front of it.
            return "RUT_FireRaidDesc".Translate(parms.faction.Name)
                 + "\n\n"
                 + base.GetLetterText(parms, pawns);
        }
    }
}
