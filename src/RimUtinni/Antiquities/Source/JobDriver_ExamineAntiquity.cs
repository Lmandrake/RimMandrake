using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.Antiquities
{
    // The reading loop, design doc section 4.2: haul the piece to the
    // station, spend a day (half a day once LANGUAGE is done) reading it,
    // flip its Catalogued flag, and hand the current stage direct research
    // progress -- Find.ResearchManager.AddProgress, verified against the
    // shipped RimWorld/ResearchManager.cs source, which self-finishes the
    // project when progress reaches cost. No consumption: the piece is
    // dropped back down afterward, "spent for knowledge, intact for silver".
    public class JobDriver_ExamineAntiquity : JobDriver
    {
        private const int FullDayTicks = 60000;
        private const int HalfDayTicks = 30000;

        private Thing Antiquity => TargetThingA;
        private Thing Station => TargetThingB;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(Antiquity, job, 1, 1, null, errorOnFailed)
                && pawn.Reserve(Station, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            // 🔴 TargetIndex.A (the antiquity) is deliberately CARRIED, not left on
            // the map, from the carry toil onward -- StartCarryThing despawns it
            // into the pawn's carryTracker exactly like any vanilla haul job. A
            // DRIVER-WIDE FailOnDespawnedNullOrForbidden(TargetIndex.A) checks
            // Spawned on every tick of every toil, so it fired the instant the
            // carry toil completed and the antiquity correctly went un-spawned --
            // aborting the job before it ever reached the station, silently,
            // every single time (measured 2026-09-04: "started 10 jobs in one
            // tick", JobGiver_Work re-proposing the identical job forever).
            // Fix: only the FIRST toil (walking to a still-on-the-map antiquity)
            // needs that check; chain it there instead of driver-wide.
            this.FailOnDespawnedNullOrForbidden(TargetIndex.B);
            this.FailOn(() => AntiquityUtility.CurrentStage() == null);

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch)
                .FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Haul.StartCarryThing(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.InteractionCell);

            int duration = AntiquityUtility.LanguageDone ? HalfDayTicks : FullDayTicks;
            Toil examine = Toils_General.Wait(duration, TargetIndex.B)
                .FailOnDespawnedOrNull(TargetIndex.B)
                .WithProgressBarToilDelay(TargetIndex.B);
            examine.activeSkill = () => SkillDefOf.Intellectual;
            examine.AddFinishAction(CompleteReading);
            yield return examine;

            Toil drop = ToilMaker.MakeToil("RUT_DropAntiquity");
            drop.initAction = delegate
            {
                if (pawn.carryTracker.CarriedThing != null)
                {
                    pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out _);
                }
            };
            drop.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return drop;
        }

        private void CompleteReading()
        {
            CompAntiquity comp = Antiquity?.TryGetComp<CompAntiquity>();
            if (comp == null || comp.catalogued)
            {
                return;
            }
            ResearchProjectDef stage = AntiquityUtility.CurrentStage();
            if (stage == null)
            {
                return;
            }
            comp.catalogued = true;

            AntiquityStageExtension ext = stage.GetModExtension<AntiquityStageExtension>();
            int required = (ext != null && ext.artifactsRequired > 0) ? ext.artifactsRequired : 1;
            float perRead = stage.baseCost / required;

            bool keyText = false;
            if (AntiquityUtility.LanguageDone)
            {
                float chance = Mathf.Min(0.15f + 0.05f * AntiquityUtility.StagesCompletedBeyondLanguage(), 0.5f);
                keyText = Rand.Chance(chance);
            }
            float amount = keyText ? perRead * 2f : perRead;

            Find.ResearchManager.AddProgress(stage, amount, pawn);
            pawn.skills?.Learn(SkillDefOf.Intellectual, 40f);
            pawn.skills?.Learn(SkillDefOf.Artistic, 40f);

            // Placeholder letter text -- the Narrator's actual intoned register
            // (design doc section 2.1) and the per-god integration reactions are
            // slice 9's job, not this one. This just proves the loop end to end.
            string label = "RUT_Antiquity_LetterLabel".Translate();
            string keyTextNote = keyText ? " " + "RUT_Antiquity_KeyText".Translate() : "";
            string text = "RUT_Antiquity_LetterText".Translate(pawn.LabelShort, Antiquity.LabelCap, stage.LabelCap) + keyTextNote;
            Find.LetterStack.ReceiveLetter(label, text, LetterDefOf.PositiveEvent, Antiquity);
        }
    }
}
