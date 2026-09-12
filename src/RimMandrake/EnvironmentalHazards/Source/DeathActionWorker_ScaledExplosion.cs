using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 5. One worker replacing the donor family's
    // three near-identical scaled-explosion classes, which differed only in
    // DamageDef and effect set. See DeathActionProperties_ScaledExplosion for
    // the XML surface.
    public class DeathActionWorker_ScaledExplosion : DeathActionWorker
    {
        public DeathActionProperties_ScaledExplosion Props => (DeathActionProperties_ScaledExplosion)props;

        public override RulePackDef DeathRules => RulePackDefOf.Transition_DiedExplosive;

        public override bool DangerousInMelee => Props == null || Props.dangerousInMelee;

        public override void PawnDied(Corpse corpse, Lord prevLord)
        {
            if (!RM_EnvironmentalHazardsSettings.scaledExplosionsEnabled)
            {
                return; // mod option: scaled death explosions disabled — the pawn just dies
            }
            DeathActionProperties_ScaledExplosion p = Props;
            if (p == null || p.damageDef == null)
            {
                return;
            }

            if (corpse == null || corpse.Map == null)
            {
                return;
            }

            Pawn pawn = corpse.InnerPawn;
            float radius = RadiusFor(pawn, p);
            if (radius <= 0f)
            {
                return;
            }

            IntVec3 center = corpse.Position;
            Map map = corpse.Map;

            // -1 is DoExplosion's own sentinel for "use damageDef.defaultDamage" —
            // only a real configured amount is scaled by the mod option.
            int damageAmount = p.damageAmount >= 0
                ? Mathf.RoundToInt(p.damageAmount * Mathf.Max(0f, RM_EnvironmentalHazardsSettings.hazardDamageMultiplier))
                : p.damageAmount;

            GenExplosion.DoExplosion(
                center,
                map,
                radius,
                p.damageDef,
                pawn,
                damageAmount,
                p.armorPenetration,
                p.explosionSound,
                p.weaponForFlash,
                null,
                null,
                p.postExplosionSpawnThingDef,
                p.postExplosionSpawnChance,
                p.postExplosionSpawnThingCount,
                null,
                null,
                255,
                false,
                null,
                0f,
                1,
                p.chanceToStartFire,
                p.damageFalloff);

            SpawnFilth(center, map, radius, p);
        }

        // Life-stage index, clamped to the configured ladder. A race with
        // more life stages than entries keeps the last (largest) radius
        // rather than falling off the end of the list — the failure mode
        // that a fixed "three floats" signature would have had.
        internal static float RadiusFor(Pawn pawn, DeathActionProperties_ScaledExplosion p)
        {
            if (p.radiusByLifeStageIndex == null || p.radiusByLifeStageIndex.Count == 0)
            {
                return p.flatRadius;
            }

            int index = 0;
            if (pawn != null && pawn.ageTracker != null)
            {
                index = pawn.ageTracker.CurLifeStageIndex;
            }

            index = Mathf.Clamp(index, 0, p.radiusByLifeStageIndex.Count - 1);
            return p.radiusByLifeStageIndex[index];
        }

        private static void SpawnFilth(IntVec3 center, Map map, float radius, DeathActionProperties_ScaledExplosion p)
        {
            if (p.postExplosionFilth == null || p.postExplosionFilthChance <= 0f)
            {
                return;
            }

            foreach (IntVec3 cell in GenRadial.RadialCellsAround(center, radius, useCenter: true))
            {
                if (!cell.InBounds(map))
                {
                    continue;
                }

                if (!Rand.Chance(p.postExplosionFilthChance))
                {
                    continue;
                }

                FilthMaker.TryMakeFilth(cell, map, p.postExplosionFilth, p.postExplosionFilthCount);
            }
        }
    }
}
