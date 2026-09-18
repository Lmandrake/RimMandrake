using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    public class CompProperties_RedeemRakatanCommandCodes : CompProperties
    {
        public CompProperties_RedeemRakatanCommandCodes()
        {
            compClass = typeof(CompRedeemRakatanCommandCodes);
        }
    }

    // The "quest-item/quest-flag mechanism" ASHFALL_RESEARCH_BASE_1's own
    // filing note asks for, connecting "codes obtained here" to "war lab's
    // shielding unlocks" -- see AshfallCommandCodesFlag's own header for
    // what this deliberately does NOT decide (whether the door check should
    // be possession-based or flag-based, and whether redemption should be
    // location-gated to the war lab itself).
    public class CompRedeemRakatanCommandCodes : ThingComp
    {
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (var gizmo in base.CompGetGizmosExtra())
                yield return gizmo;

            yield return new Command_Action
            {
                defaultLabel = "Redeem command codes",
                defaultDesc = "Key the Rakatan command codes into a lock. This is a one-way "
                    + "action -- the codes are consumed the moment they are used.",
                action = delegate
                {
                    AshfallCommandCodesFlag.Seize();
                    parent.Destroy(DestroyMode.Vanish);
                },
            };
        }
    }
}
