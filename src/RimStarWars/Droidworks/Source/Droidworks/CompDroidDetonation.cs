using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Droidworks
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
            // MOD_OPTIONS_RETROFIT_1: off = droids never explode. Nothing else
            // hangs off this hook (heads and parts drop from their own comps), so
            // the coarse early return is the whole gate.
            if (!RSW_DroidworksSettings.detonation) return;
            Pawn pawn = parent as Pawn;
            if (pawn == null) return;
            // NOT pawn.def.GetModExtension<T>() (FirstOrDefault): RimWorld's XML
            // inheritance APPENDS a child's <modExtensions> entries after the
            // parent's rather than replacing them (measured live,
            // DROIDWORKS_DETONATION_REVIEW_1 — a JDS Battle-family race carrying
            // its own deliberateDenyModule=true override still resolved false via
            // GetModExtension, because the family abstract's inherited copy sorts
            // FIRST in the concatenated list). The race's own, more specific
            // declaration is always the LAST DroidworksExtension in the list.
            DroidworksExtension ext = pawn.def.modExtensions?.OfType<DroidworksExtension>().LastOrDefault();
            float density = ext?.energyDensity ?? 0f;
            // Deliberate deny-your-parts modules (design/Jawa/droid_system_build_spec.md
            // line ~99: "Deliberate deny-your-parts modules and Gonk/KX-12 nature raise
            // density") raise the EFFECTIVE density to at least 1 — a battle-family race
            // with no base density (0) still gets a floor detonation once fitted with the
            // module; a race whose family density already exceeds 1 is unaffected. This is
            // additive headroom only, never a bypass of the charge guard below: a module
            // cannot make a drained wreck explode ("a wreck has no power" is unconditional).
            if (ext != null && ext.deliberateDenyModule)
                density = Mathf.Max(density, 1f);
            if (density <= 0f) return;
            float charge = pawn.needs?.TryGetNeed<Need_Power>()?.CurLevel ?? 0f;
            if (charge <= 0.05f) return;          // a wreck has no power
            float scale = charge * density * RSW_DroidworksSettings.detonationSize;
            float radius = Props.baseRadius * Mathf.Sqrt(scale);
            int damage = Mathf.RoundToInt(50f * scale);
            GenExplosion.DoExplosion(
                pawn.PositionHeld, prevMap, radius,
                Props.damageDef ?? DamageDefOf.Bomb,
                pawn, damage);
        }
    }
}
