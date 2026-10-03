using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // REACTION_MECHANISM_GENERALISE_1 step 5: "suppression is part of the
    // mechanism, not a grenade feature." A cell can be marked
    // reaction-suppressed for a while; inside a suppressed zone:
    //   - a reaction source does not trigger (RM_CompReactionSource),
    //   - an in-flight event does not propagate into a responder standing there
    //     (both propagation rules),
    //   - a responder standing there does not answer (every response rule,
    //     including the migrated plant alarm's wake response),
    //   - a pawn already in RM_MentalState_ScopedAggression (swarming wasps,
    //     a rallied hive) gives up when it is in a zone or one is laid on it.
    // The stench grenade (mandrake.rm.greentide, RM_Proj_GrenadeStenchSmoke)
    // is the first CALLER of Suppress; any future counter-tool calls the same
    // static and gets the same behaviour, never a special case.
    //
    // Zones are center+radius+expiry, Scribed, pruned lazily. Cheap enough to
    // ask per responder: a map rarely holds more than a couple at once.
    public class RM_SuppressionZone : IExposable
    {
        public IntVec3 center;
        public float radius;
        public int expiresTick;

        public void ExposeData()
        {
            Scribe_Values.Look(ref center, "center");
            Scribe_Values.Look(ref radius, "radius");
            Scribe_Values.Look(ref expiresTick, "expiresTick");
        }
    }

    public class RM_MapComponent_ReactionSuppression : MapComponent
    {
        public List<RM_SuppressionZone> zones = new List<RM_SuppressionZone>();

        public RM_MapComponent_ReactionSuppression(Map map) : base(map)
        {
        }

        public bool IsSuppressed(IntVec3 cell)
        {
            if (zones.Count == 0)
            {
                return false;
            }

            int now = Find.TickManager.TicksGame;
            for (int i = zones.Count - 1; i >= 0; i--)
            {
                RM_SuppressionZone z = zones[i];
                if (z.expiresTick <= now)
                {
                    zones.RemoveAt(i);
                    continue;
                }

                if ((cell - z.center).LengthHorizontalSquared <= z.radius * z.radius)
                {
                    return true;
                }
            }
            return false;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref zones, "rmReactionSuppressionZones", LookMode.Deep);
            if (zones == null)
            {
                zones = new List<RM_SuppressionZone>();
            }
        }
    }

    public static class RM_ReactionSuppression
    {
        /// <summary>
        /// Mark a disc reaction-suppressed for `durationTicks` (scaled by the
        /// mod's duration dial), and end any scoped aggression already running
        /// inside it. Returns false when the mechanism is switched off.
        /// </summary>
        public static bool Suppress(Map map, IntVec3 center, float radius, int durationTicks)
        {
            if (!RM_CreatureBehaviorsSettings.reactionSuppressionEnabled || map == null || radius <= 0f)
            {
                return false;
            }

            int ticks = Mathf.RoundToInt(durationTicks * Mathf.Max(0f, RM_CreatureBehaviorsSettings.reactionSuppressionDurationMultiplier));
            if (ticks <= 0)
            {
                return false;
            }

            RM_MapComponent_ReactionSuppression comp = map.GetComponent<RM_MapComponent_ReactionSuppression>();
            if (comp == null)
            {
                return false;
            }

            comp.zones.Add(new RM_SuppressionZone
            {
                center = center,
                radius = radius,
                expiresTick = Find.TickManager.TicksGame + ticks,
            });

            float radiusSq = radius * radius;
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p != null && !p.Dead && p.MentalState is RM_MentalState_ScopedAggression state
                    && (p.Position - center).LengthHorizontalSquared <= radiusSq)
                {
                    state.RecoverFromState();
                }
            }
            return true;
        }

        /// <summary>True if `cell` sits in a live suppression zone. Always false with the mechanism off.</summary>
        public static bool IsSuppressed(Map map, IntVec3 cell)
        {
            if (!RM_CreatureBehaviorsSettings.reactionSuppressionEnabled || map == null)
            {
                return false;
            }
            RM_MapComponent_ReactionSuppression comp = map.GetComponent<RM_MapComponent_ReactionSuppression>();
            return comp != null && comp.IsSuppressed(cell);
        }
    }
}
