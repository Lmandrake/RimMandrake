using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Ninefold
{
    // ════════════════════════════════════════════════════════════════════
    // NINEFOLD_FAVOUR_ODDS_BUILD_1 — the Nine Faults rite's engine.
    // Spec: design/Jawa/nine_faults_permanent_rite_2026-10-01.md §2.
    //
    // RM tier, names no faith: the precept/pattern/behaviour/outcome DEFS
    // are campaign data in mandrake.rut.rites (Defs/RUT_NineFaults.xml),
    // the same split as UtinniPatches' RUT_TheReturn over Stillsand's
    // workers. Tunables ride on RM_NineFaultsExtension on the outcome def.
    //
    //  * target: a fresh find (Offerings.cs) on this map.
    //  * outcome: the ninth fault burns the machine out — destroyed, a hulk
    //    of slag left where it stood. Poor: a real fire and a smaller
    //    offering. Fair: full. Good: + memory (outcome <memory> in XML).
    //    Excellent: + an art tale.
    //  * favour: Rekko loses what Zizzik gains, sized by market value
    //    (Small 3 .. Large 15) and scaled by outcome quality.
    //  * No letter text names a god as a cause.
    // ════════════════════════════════════════════════════════════════════

    public class RM_NineFaultsExtension : DefModExtension
    {
        public ThingDef hulkDef;
        public TaleDef excellentTale;
        public float poorFireSize = 0.6f;
        // Transfer scale by outcome positivityIndex: <0 / 1 / 2 / >=3.
        public float poorFactor = 0.5f;
        public float fairFactor = 1f;
        public float goodFactor = 1.25f;
        public float excellentFactor = 1.5f;
    }

    public class RM_RitualObligationTargetWorker_FreshFind : RitualObligationTargetFilter
    {
        public RM_RitualObligationTargetWorker_FreshFind() { }

        public RM_RitualObligationTargetWorker_FreshFind(RitualObligationTargetFilterDef def) : base(def) { }

        public override IEnumerable<TargetInfo> GetTargets(RitualObligation obligation, Map map)
        {
            var comp = MapComponent_NinefoldOfferings.For(map);
            if (comp == null) yield break;
            foreach (Building b in comp.FreshBuildings())
                yield return b;
        }

        protected override RitualTargetUseReport CanUseTargetInternal(TargetInfo target, RitualObligation obligation)
        {
            if (!target.HasThing) return false;
            var comp = MapComponent_NinefoldOfferings.For(target.Map);
            if (comp == null) return false;
            // Plain false (no reason) for everything else: a fail REASON makes
            // vanilla show a disabled ritual gizmo on that thing
            // (RitualTargetUseReport.ShouldShowGizmo), i.e. on every building.
            return comp.IsFresh(target.Thing);
        }

        public override IEnumerable<string> GetTargetInfos(RitualObligation obligation)
        {
            yield return "a machine found on this ground and never run (claimed, or installed from a find)";
        }
    }

    public class RM_RitualOutcomeEffectWorker_NineFaults : RitualOutcomeEffectWorker_FromQuality
    {
        public RM_RitualOutcomeEffectWorker_NineFaults() { }

        public RM_RitualOutcomeEffectWorker_NineFaults(RitualOutcomeEffectDef def) : base(def) { }

        protected override void ApplyExtraOutcome(Dictionary<Pawn, int> totalPresence, LordJob_Ritual jobRitual,
            RitualOutcomePossibility outcome, out string extraOutcomeDesc, ref LookTargets letterLookTargets)
        {
            extraOutcomeDesc = null;
            RM_NineFaultsExtension ext = def.GetModExtension<RM_NineFaultsExtension>() ?? new RM_NineFaultsExtension();
            Map map = jobRitual?.Map;
            Thing machine = jobRitual?.selectedTarget.Thing;
            if (map == null || machine == null || machine.Destroyed) return;

            var sb = new StringBuilder();
            IntVec3 at = machine.Position;
            string label = machine.LabelNoCount;
            float amount = OfferingUtility.TransferFor(machine);

            float factor = outcome.positivityIndex < 0 ? ext.poorFactor
                : outcome.positivityIndex <= 1 ? ext.fairFactor
                : outcome.positivityIndex == 2 ? ext.goodFactor
                : ext.excellentFactor;

            // The ninth fault: burnt out, lost forever, readable on the ground.
            MapComponent_NinefoldOfferings.For(map)?.ClearFresh(machine, "given the nine faults");
            machine.Destroy(DestroyMode.Vanish);
            if (ext.hulkDef != null)
            {
                Thing hulk = GenSpawn.Spawn(ThingMaker.MakeThing(ext.hulkDef), at, map);
                letterLookTargets = new LookTargets(hulk);
            }
            FleckMaker.ThrowSmoke(at.ToVector3Shifted(), map, 2.5f);
            FleckMaker.ThrowMicroSparks(at.ToVector3Shifted(), map);
            sb.Append("The nine bulbs failed one by one, and the ").Append(label)
              .Append(" burnt out where it stood. Nothing is left of it but a slag hulk.");

            if (outcome.positivityIndex < 0)
            {
                // Poor: the miswiring caught early.
                IEnumerable<IntVec3> cells = GenAdj.CellsAdjacent8Way(new TargetInfo(at, map))
                    .Where(c => c.InBounds(map) && c.Standable(map));
                if (cells.TryRandomElement(out IntVec3 fireCell))
                    FireUtility.TryStartFireIn(fireCell, map, ext.poorFireSize, null);
                sb.Append(" The miswiring caught early, and fire took hold.");
            }
            else
            {
                sb.Append(" The smoke curled against the draft.");
            }

            OfferingUtility.Transfer(God.Rekko, God.Zizzik, amount * factor,
                "Nine Faults (" + outcome.label + "): " + label);

            if (outcome.positivityIndex >= 3 && ext.excellentTale != null)
            {
                Pawn teller = jobRitual.Organizer ?? totalPresence.Keys.FirstOrDefault();
                if (teller != null)
                    TaleRecorder.RecordTale(ext.excellentTale, teller);
            }

            extraOutcomeDesc = sb.ToString();
        }
    }
}
