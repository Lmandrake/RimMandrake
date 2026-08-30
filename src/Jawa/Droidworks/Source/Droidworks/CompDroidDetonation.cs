using RimWorld;
using UnityEngine;
using Verse;

namespace Droidworks
{
    public class CompProperties_DroidDetonation : CompProperties
    {
        public float baseRadius = 3.9f;
        public DamageDef damageDef;

        public CompProperties_DroidDetonation() =>
            compClass = typeof(CompDroidDetonation);
    }

    /// <summary>
    /// State 5: catastrophic detonation, on DEATH only (a downed droid has not
    /// died and never explodes - the ion-capture incentive). Scale reads the
    /// pawn's CURRENT power level, never a def-time maximum: a drained wreck
    /// cannot explode. Suppresses mid-fight chance-detonation entirely (the
    /// vanilla explodeOnKilled path that bypasses MakeCorpse is not used).
    /// </summary>
    public class CompDroidDetonation : ThingComp
    {
        public CompProperties_DroidDetonation Props =>
            (CompProperties_DroidDetonation)props;

        public override void Notify_Killed(Map prevMap, DamageInfo? dinfo = null)
        {
            if (prevMap == null) return;
            Pawn pawn = parent as Pawn;
            if (pawn == null) return;
            DroidworksExtension ext = pawn.def.GetModExtension<DroidworksExtension>();
            float density = ext?.energyDensity ?? 0f;
            if (density <= 0f) return;
            float charge = pawn.needs?.TryGetNeed<Need_Power>()?.CurLevel ?? 0f;
            if (charge <= 0.05f) return;          // a wreck has no power
            float scale = charge * density;
            float radius = Props.baseRadius * Mathf.Sqrt(scale);
            int damage = Mathf.RoundToInt(50f * scale);
            GenExplosion.DoExplosion(
                pawn.PositionHeld, prevMap, radius,
                Props.damageDef ?? DamageDefOf.Bomb,
                pawn, damage);
        }
    }
}
