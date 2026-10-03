using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // GELATINOUSSLIME_VAULT_SEAL_BREACH_1 (Slime-side slice). A titanoslime chunk dissolves any
    // Thing whose def carries RM_SlimeBreachable (the Assailant's flesh seal on the Slough vault is
    // the intended user; the seal def itself belongs to VAULT_DUNGEON_BUILD_1 and parents on
    // RM_SlimeBreachableSealBase). The cost is a drench of slime smear around the door.
    public class RM_SlimeBreachable : DefModExtension
    {
        // [INVENTED] cells of smear around the dissolved thing.
        public float drenchRadius = 3.9f;
    }

    public class CompTargetable_SlimeBreachable : CompTargetable
    {
        protected override bool PlayerChoosesTarget => true;

        protected override TargetingParameters GetTargetingParameters()
        {
            return new TargetingParameters
            {
                canTargetPawns = false,
                canTargetBuildings = true,
                canTargetItems = false,
                validator = (TargetInfo t) => t.HasThing && t.Thing.def.HasModExtension<RM_SlimeBreachable>()
            };
        }

        public override IEnumerable<Thing> GetTargets(Thing targetChosenByPlayer = null)
        {
            yield return targetChosenByPlayer;
        }
    }

    public class CompTargetEffect_SlimeBreach : CompTargetEffect
    {
        public override void DoEffectOn(Pawn user, Thing target)
        {
            if (target == null || target.Destroyed || !target.Spawned) return;
            RM_SlimeBreachable ext = target.def.GetModExtension<RM_SlimeBreachable>();
            if (ext == null) return;
            if (!SlimeSettings.sealBreach)
            {
                Messages.Message("The chunk sits inert against the seal.", target, MessageTypeDefOf.RejectInput, false);
                return;
            }
            Map map = target.Map;
            IntVec3 c = target.Position;
            ThingDef smear = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_SlimeSmear");
            target.Destroy(DestroyMode.Vanish);
            if (smear != null)
            {
                foreach (IntVec3 cell in GenRadial.RadialCellsAround(c, ext.drenchRadius, true))
                {
                    if (cell.InBounds(map) && cell.Walkable(map)) FilthMaker.TryMakeFilth(cell, map, smear);
                }
            }
            Messages.Message("The chunk reads the seal and eats it. The way is open.", new TargetInfo(c, map), MessageTypeDefOf.PositiveEvent, false);
            if (parent != null && !parent.Destroyed) parent.SplitOff(1).Destroy(DestroyMode.Vanish);
        }
    }
}
