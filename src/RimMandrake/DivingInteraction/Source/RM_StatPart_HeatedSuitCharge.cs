using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_HEATED_SUIT_1 — the charge-gated half of the suit's cold
    // protection. Added to StatDefOf.ComfyTemperatureMin's own <parts>
    // (Defs/Core/Stats/Stats_Pawns_General.xml already carries one part
    // there, StatPart_GearStatOffset for Insulation_Cold — this is a
    // second part alongside it, RM_ComfyTemperatureMin_HeatedSuit.xml
    // Patches file) so the suit's protection is computed as part of the
    // PAWN's own ComfyTemperatureMin, exactly like vanilla apparel
    // insulation, rather than needing any bespoke temperature-tracking of
    // its own.
    //
    // An ABSOLUTE FLOOR (Mathf.Min), not an additive offset — deliberately.
    // An offset would stack with whatever apparel/genes/hediffs already
    // contributed and be fragile to double-counting; a floor just says
    // "however cold-hardy this pawn already is, a charged suit is AT LEAST
    // this good," which is what "full charge: pawn works outside safely"
    // actually means. It wins regardless of what order StatParts run in.
    // ════════════════════════════════════════════════════════════════════
    public class RM_StatPart_HeatedSuitCharge : StatPart
    {
        // -140C comfortably covers the Chill seabed's -110C ambient
        // (RM_SeaDiveGenerators.xml, CHILL_THERMAL_ENGINE_1) with a real
        // margin — SafeTemperatureRange is ComfyTemperatureMin - 10, so
        // this clears -110 by 20C of buffer even accounting for that.
        public const float ChargedComfyTemperatureMinC = -140f;

        public override void TransformValue(StatRequest req, ref float val)
        {
            if (!IsWearingChargedSuit(req, out _))
            {
                return;
            }
            if (val > ChargedComfyTemperatureMinC)
            {
                val = ChargedComfyTemperatureMinC;
            }
        }

        public override string ExplanationPart(StatRequest req)
        {
            if (!IsWearingChargedSuit(req, out Apparel suit))
            {
                return null;
            }
            return suit.LabelCap + " (charged): " + ChargedComfyTemperatureMinC.ToStringTemperature();
        }

        private static bool IsWearingChargedSuit(StatRequest req, out Apparel suitFound)
        {
            suitFound = null;
            if (!req.HasThing || !(req.Thing is Pawn pawn) || pawn.apparel == null)
            {
                return false;
            }
            List<Apparel> worn = pawn.apparel.WornApparel;
            for (int i = 0; i < worn.Count; i++)
            {
                Apparel a = worn[i];
                if (a?.def == null || a.def.defName != "RM_ChillHeatedSuit")
                {
                    continue;
                }
                RM_CompHeatedSuitBattery battery = a.TryGetComp<RM_CompHeatedSuitBattery>();
                if (battery != null && battery.IsCharged)
                {
                    suitFound = a;
                    return true;
                }
            }
            return false;
        }
    }
}
