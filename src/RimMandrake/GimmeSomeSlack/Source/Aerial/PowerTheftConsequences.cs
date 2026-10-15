using System;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    [DefOf]
    public static class TheftDefOf
    {
        public static HistoryEventDef RM_PowerTheftCaught;
        static TheftDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(TheftDefOf));
    }

    /// <summary>
    /// POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK. Owner 2026-10-10, typed: "If caught, steady goodwill drain (like living too
    /// close to a settlement)". The one subscriber to TapEvents.Drained (raised every 250 ticks per draining clamp):
    /// * CAUGHT: a member of the victim faction -- humanlike, awake, not downed, not our prisoner -- within
    ///   AerialSettings.theftSightRange cells with line of sight to a player clamp. Once per clamp per victim faction; a
    ///   letter says who saw it. Remembered on the clamp (CompPowerTap.caughtFactions, saved; GPT pre-release C8: every
    ///   faction that caught it, not only the last).
    /// * DRAIN: a caught clamp accrues the ticks it actually spends draining that faction (GPT pre-release C7: the ticks that
    ///   drained, not the whole 250-tick event window); every whole day costs theftGoodwillPerDay goodwill
    ///   (vanilla TryAffectGoodwillWith, reason RM_PowerTheftCaught -- vanilla's own message, and its hostility letter if
    ///   relations break). Like vanilla's settlement-proximity leak, a faction already at -100 or permanently hostile is
    ///   skipped. Removing the clamp stops the drain (no draining, no accrual). The clamp has no on/off switch (no
    ///   CompFlickable; GPT pre-release C5), so the letter says remove, not switch off.
    /// Defaults (2/day, 12 cells) CONFIRMED by the owner 2026-10-11 by question card (gss_flowworks_rulings_2026-10-11.md #7);
    /// both stay Mod Settings numbers.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class PowerTheftConsequences
    {
        public const int EventInterval = 250;
        public static int caughtCount, charges, goodwillCharged;

        static PowerTheftConsequences()
        {
            TapEvents.Drained -= OnDrained;
            TapEvents.Drained += OnDrained;
        }

        internal static void OnDrained(Thing tap, Thing victimTransmitter, float wd)
        {
            if (!AerialSettings.theftGoodwill || tap == null || !tap.Spawned || tap.Faction != Faction.OfPlayer) return;
            Faction victim = victimTransmitter?.Faction;
            if (victim == null || victim.IsPlayer || victim.defeated) return;
            CompPowerTap comp = tap.TryGetComp<CompPowerTap>();
            if (comp == null) return;
            int ci = comp.CaughtIndex(victim);
            if (ci < 0)
            {
                Pawn witness = Witness(tap, victim);
                if (witness == null) return;
                comp.MarkCaught(victim);
                caughtCount++;
                Find.LetterStack.ReceiveLetter("Power theft discovered",
                    witness.LabelShortCap + " of " + victim.Name + " has spotted your power-tap clamp on their grid. Every day it keeps draining " +
                    "them now costs " + AerialSettings.theftGoodwillPerDay + " goodwill with " + victim.Name +
                    ", like living too close to their settlement. " + StopAdvice,
                    LetterDefOf.NegativeEvent, new LookTargets(tap, witness));
                return;
            }
            comp.caughtBy = victim;
            int acc = comp.caughtTicks[ci];
            int change = AerialMath.TheftGoodwillAccrue(ref acc, comp.drainTicksSinceEvent, wd > 0f,
                AerialSettings.theftGoodwillPerDay, GenDate.TicksPerDay);
            comp.caughtTicks[ci] = acc;
            if (change >= 0 || victim.PlayerGoodwill <= -100 || victim.def.permanentEnemy) return;
            if (Faction.OfPlayer.TryAffectGoodwillWith(victim, change, canSendMessage: true, canSendHostilityLetter: true,
                    TheftDefOf.RM_PowerTheftCaught, new GlobalTargetInfo(tap)))
            {
                charges++;
                goodwillCharged += change;
            }
        }

        /// <summary>What the discovery letter tells the player to do. The clamp has no CompFlickable (GPT pre-release C5), so
        /// removing it is the one way to stop the drain; the offline row O7 checks this text against the clamp's def.</summary>
        public const string StopAdvice = "Remove the clamp to stop it.";

        /// <summary>The first victim-faction pawn that can see the clamp, or null.</summary>
        public static Pawn Witness(Thing tap, Faction victim)
        {
            Map map = tap.Map;
            float range = AerialSettings.theftSightRange;
            foreach (Pawn p in map.mapPawns.SpawnedPawnsInFaction(victim))
            {
                if (p.RaceProps == null || !p.RaceProps.Humanlike) continue;
                float d = (p.Position - tap.Position).LengthHorizontal;
                if (d > range) continue;
                bool up = !p.Downed && !p.Dead && RestUtility.Awake(p);
                bool held = p.IsPrisonerOfColony || p.HostFaction == Faction.OfPlayer;
                bool los = GenSight.LineOfSight(p.Position, tap.Position, map);
                if (AerialMath.TheftSpotted(d, range, los, up, held)) return p;
            }
            return null;
        }
    }
}
