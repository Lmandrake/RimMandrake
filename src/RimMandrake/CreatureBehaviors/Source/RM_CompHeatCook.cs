using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// WASTELAND_RADIOTHERMAL_SOLITARY_1. The "or cook each other" half of
    /// the spacing law: if RM_JobGiver_AvoidOwnKind fails to keep this pawn
    /// outside RM_SpeciesSpacingExtension.cookRadiusCells of another member
    /// of its own PawnKindDef (a pen, a cage, a cornered map — the
    /// avoidance JobGiver is meant to prevent this, not guarantee it never
    /// happens), this comp burns it a little every interval. Reads all its
    /// tuning off the same RM_SpeciesSpacingExtension the JobGiver uses —
    /// this comp's own CompProperties carries none of its own.
    /// </summary>
    public class RM_CompHeatCook : ThingComp
    {
        private int ticksUntilCheck;

        public override void CompTick()
        {
            base.CompTick();

            if (!RM_CreatureBehaviorsSettings.speciesSpacingEnabled)
            {
                return;
            }
            if (!(parent is Pawn self) || !self.Spawned || self.Dead || self.Map == null)
            {
                return;
            }
            RM_SpeciesSpacingExtension ext = self.def?.GetModExtension<RM_SpeciesSpacingExtension>();
            if (ext == null)
            {
                return;
            }

            ticksUntilCheck--;
            if (ticksUntilCheck > 0)
            {
                return;
            }
            ticksUntilCheck = UnityEngine.Mathf.Max(1, ext.cookIntervalTicks);

            float mult = UnityEngine.Mathf.Max(0f, RM_CreatureBehaviorsSettings.speciesSpacingCookDamageMultiplier);
            float amount = ext.cookDamagePerInterval * mult;
            if (amount <= 0f)
            {
                return;
            }

            float cookRadiusSq = ext.cookRadiusCells * ext.cookRadiusCells;
            bool crowded = false;
            IReadOnlyList<Pawn> pawns = self.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn other = pawns[i];
                if (other == self || other.Dead || other.kindDef != self.kindDef)
                {
                    continue;
                }
                if ((other.Position - self.Position).LengthHorizontalSquared <= cookRadiusSq)
                {
                    crowded = true;
                    break;
                }
            }
            if (!crowded)
            {
                return;
            }

            BodyPartRecord core = self.RaceProps?.body?.corePart;
            DamageDef def = ext.cookDamageDef ?? DamageDefOf.Burn;
            self.TakeDamage(new DamageInfo(def, amount, 0f, -1f, self, core));
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksUntilCheck, "ticksUntilCheck", 0);
        }
    }
}
