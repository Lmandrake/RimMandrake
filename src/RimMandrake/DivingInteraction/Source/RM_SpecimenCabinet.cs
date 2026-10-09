using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    /// <summary>
    /// SPECIMEN_CABINET_DISPLAY_1 (DI-7). A home shelf for novel finds: instead of selling a creature's corpse or a new
    /// mineral to the Brine Elder, keep it on display. Each distinct kind (RM_ElderTradeUtility.NoveltyKey, the same key
    /// the Elder trades on) adds beauty to its cabinet and, across the colony, a small museum mood. The counting is the
    /// Verse-free RM_ElderEconomyKernel (DistinctKinds / CabinetBeauty / MuseumMoodStage). Toggle: specimenCabinetEnabled.
    /// </summary>
    public class RM_CompSpecimenCabinet : ThingComp
    {
        public static bool Enabled => RM_DivingSettings.masterEnabled && RM_DivingSettings.specimenCabinetEnabled;

        /// <summary>Novelty keys of everything stored in this cabinet.</summary>
        public IEnumerable<string> Keys()
        {
            var shelf = parent as Building_Storage;
            SlotGroup sg = shelf?.GetSlotGroup();
            if (sg == null) yield break;
            foreach (Thing t in sg.HeldThings) yield return RM_ElderTradeUtility.NoveltyKey(t);
        }

        public int Kinds => Enabled ? RM_ElderEconomyKernel.DistinctKinds(Keys()) : 0;

        /// <summary>Distinct kinds across every cabinet on the map (one species in two cabinets counts once).</summary>
        public static int MapKinds(Map map)
        {
            if (map == null || !Enabled) return 0;
            var keys = new List<string>();
            foreach (Thing b in map.listerBuildings.allBuildingsColonist)
            {
                RM_CompSpecimenCabinet c = b.TryGetComp<RM_CompSpecimenCabinet>();
                if (c != null) keys.AddRange(c.Keys());
            }
            return RM_ElderEconomyKernel.DistinctKinds(keys);
        }

        public override string CompInspectStringExtra() => Enabled ? "On display: " + Kinds + " kind(s)" : null;
    }

    /// <summary>Adds the cabinet's display beauty to its Beauty stat (patched onto StatDef Beauty by RM_SpecimenCabinet_Beauty.xml).</summary>
    public class RM_StatPart_SpecimenBeauty : StatPart
    {
        public override void TransformValue(StatRequest req, ref float val)
        {
            RM_CompSpecimenCabinet c = req.Thing?.TryGetComp<RM_CompSpecimenCabinet>();
            if (c != null) val += RM_ElderEconomyKernel.CabinetBeauty(c.Kinds);
        }

        public override string ExplanationPart(StatRequest req)
        {
            RM_CompSpecimenCabinet c = req.Thing?.TryGetComp<RM_CompSpecimenCabinet>();
            int k = c?.Kinds ?? 0;
            return k > 0 ? "Specimens on display (" + k + " kinds): +" + RM_ElderEconomyKernel.CabinetBeauty(k).ToString("0") : null;
        }
    }

    /// <summary>Museum mood: a small lift while the colony's map has specimens on display, stronger with more kinds.</summary>
    public class RM_ThoughtWorker_Museum : ThoughtWorker
    {
        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            int stage = RM_ElderEconomyKernel.MuseumMoodStage(RM_CompSpecimenCabinet.MapKinds(p.MapHeld));
            return stage < 0 ? ThoughtState.Inactive : ThoughtState.ActiveAtStage(stage);
        }
    }
}
