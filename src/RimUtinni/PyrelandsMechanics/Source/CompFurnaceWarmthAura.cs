using System.Collections.Generic;
using Verse;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// PYRELANDS_MECHANICS_1, mechanism 4a — the open-field "walking hearth"
    /// (RUT_ruled_commissions_wave2.md §8b).
    ///
    /// 🔑 WHY THIS IS NOT A HEAT PUSHER. The brief settles it and this comment
    /// exists so nobody re-opens it: vanilla's temperature model spends pushed
    /// heat on the containing ROOM, and outdoors the containing room is the
    /// map-wide outdoor temperature — so CompHeatPusher on a beast walking open
    /// grassland warms nothing a player can feel. The beast ships the vanilla heat
    /// pusher too (one XML node, in RUT_FurnaceBeast_Mechanics.xml) and that node
    /// is what genuinely heats a barn, a canyon room or a walled waystation. THIS
    /// comp is the other half: a hediff aura, radius-limited, for the open field.
    /// Fighting the outdoor model cell by cell was the expensive wrong route and
    /// was rejected at design.
    ///
    /// The hediff does two things, both of them the sheet's own words (§5): a
    /// furnace-beast is "welcome company in the cold and terrible company in the
    /// dry". So RUT_FurnaceWarmth widens cold tolerance AND narrows heat
    /// tolerance. Standing next to a stove in the Pyrelands sun is a mistake.
    ///
    /// Expiry is handled by the hediff's own HediffComp_Disappears, re-stamped
    /// every interval while the pawn is in range: walk away from the herd and the
    /// warmth is gone within a few seconds, with no bookkeeping here.
    /// </summary>
    public class CompProperties_FurnaceWarmthAura : CompProperties
    {
        public float radius = PyrelandsTuning.FurnaceAuraRadius;

        public CompProperties_FurnaceWarmthAura()
        {
            compClass = typeof(CompFurnaceWarmthAura);
        }
    }

    public class CompFurnaceWarmthAura : ThingComp
    {
        public CompProperties_FurnaceWarmthAura Props => (CompProperties_FurnaceWarmthAura)props;

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);

            if (!parent.IsHashIntervalTick(PyrelandsTuning.FurnaceAuraIntervalTicks, delta))
            {
                return;
            }
            if (!(parent is Pawn beast) || !beast.Spawned || beast.Dead)
            {
                return;
            }

            float radiusSq = Props.radius * Props.radius;
            IReadOnlyList<Pawn> pawns = beast.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == beast || p.Dead || p.health == null)
                {
                    continue;
                }
                if ((p.Position - beast.Position).LengthHorizontalSquared > radiusSq)
                {
                    continue;
                }

                ApplyOrRefreshWarmth(p);
            }
        }

        private static void ApplyOrRefreshWarmth(Pawn p)
        {
            HediffDef def = PyrelandsMechanicsDefOf.RUT_FurnaceWarmth;
            Hediff hediff = p.health.hediffSet.GetFirstHediffOfDef(def);
            if (hediff == null)
            {
                hediff = HediffMaker.MakeHediff(def, p);
                p.health.AddHediff(hediff);
            }

            // Re-stamp the countdown rather than stacking severity: two beasts are
            // not twice as warm, they are warm for as long as either is close.
            hediff.TryGetComp<HediffComp_Disappears>()?.ResetElapsedTicks();
        }
    }
}
