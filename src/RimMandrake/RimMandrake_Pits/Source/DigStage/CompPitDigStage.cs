using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Pits
{
    // Dig-stage lifecycle, section 2 of covered_pit_traps_spec.md: "Dug, not
    // built... Depth tiers by staged digging (each stage = more work, spoil
    // hauled out)." Placement (Blueprint -> Frame, vanilla constructible
    // machinery, ConstructionSpeed) is stage 1. Each further stage is a
    // "Dig Deeper" designation worked by JobDriver_DigPitDeeper
    // (MiningSpeed-scaled, mirroring RimWorld/JobDriver_RemoveBuilding's own
    // pacing). On the final stage the dig site transforms into its
    // Building_OpenPit.
    //
    // OPEN QUESTION (not guessed, flagged here and in the item file): "spoil
    // hauled out" is not implemented - no resource is spawned per stage. The
    // spec does not name a spoil resource/defName, and inventing one (dirt?
    // sand? an existing rubble chunk?) would be exactly the kind of guess
    // CLAUDE.md forbids for a defName. Left for the campaign/balance layer.
    public class CompPitDigStage : ThingComp
    {
        public int stagesCompleted = 1; // placement = stage 1
        public float workLeftThisStage;

        public CompProperties_PitDigStage Props => (CompProperties_PitDigStage)props;

        public int RequiredStages => Props.depthTier.RequiredStages();

        public bool NeedsMoreDigging => stagesCompleted < RequiredStages;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!respawningAfterLoad && NeedsMoreDigging)
            {
                ResetStageWork();
            }
        }

        // A Shallow dig site has RequiredStages == 1, and placement IS stage 1
        // (PitDepthTier: "a Shallow dig site finishes open the moment its frame
        // completes"). Nothing used to implement that: AdvanceStage was the only
        // caller of CompleteToOpenPit, and a Shallow site never advances, so it
        // sat as a dig site forever - measured live 2026-08-30, and it stranded
        // every one of the six Shallow fittings, which is the whole fitting
        // family. Completed here on the first tick rather than in
        // PostSpawnSetup, because that would Destroy the parent from inside its
        // own spawn.
        public override void CompTick()
        {
            base.CompTick();
            if (!NeedsMoreDigging && parent.Spawned)
            {
                CompleteToOpenPit();
            }
        }

        private void ResetStageWork()
        {
            workLeftThisStage = Props.depthTier.WorkPerAdditionalStage();
        }

        // Called by JobDriver_DigPitDeeper as work is spent.
        public void AddDigWork(float amount)
        {
            if (!NeedsMoreDigging) return;
            workLeftThisStage -= amount;
            if (workLeftThisStage <= 0f)
            {
                AdvanceStage();
            }
        }

        private void AdvanceStage()
        {
            stagesCompleted++;
            if (NeedsMoreDigging)
            {
                ResetStageWork();
                return;
            }
            CompleteToOpenPit();
        }

        private void CompleteToOpenPit()
        {
            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            Rot4 rot = parent.Rotation;
            ThingDef openDef = Props.openPitDef;
            if (map == null || openDef == null)
            {
                Log.Error("[RimMandrakePits] CompPitDigStage completed with no map or no openPitDef on " + parent.def.defName);
                return;
            }

            parent.Destroy(DestroyMode.Vanish);
            Thing openPit = ThingMaker.MakeThing(openDef);
            if (openPit is Building_OpenPit pit)
            {
                pit.DepthTier = Props.depthTier;
            }
            GenSpawn.Spawn(openPit, pos, map, rot);
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;

            if (NeedsMoreDigging)
            {
                Map map = parent.Map;
                bool queued = map != null && map.designationManager.DesignationOn(parent, RMPits_DesignationDefOf.RM_DigPitDeeper) != null;

                yield return new Command_Action
                {
                    defaultLabel = queued ? "RMPits_CancelDigDeeper".Translate() : "RMPits_DigDeeper".Translate(),
                    defaultDesc = queued ? "RMPits_CancelDigDeeperDesc".Translate() : "RMPits_DigDeeperDesc".Translate(),
                    icon = TexCommand.Attack, // placeholder icon; art pass owed
                    action = delegate
                    {
                        if (map == null) return;
                        if (queued)
                        {
                            map.designationManager.TryRemoveDesignationOn(parent, RMPits_DesignationDefOf.RM_DigPitDeeper);
                        }
                        else
                        {
                            map.designationManager.AddDesignation(new Designation(parent, RMPits_DesignationDefOf.RM_DigPitDeeper));
                        }
                    },
                };
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!NeedsMoreDigging) return null;
            return "RMPits_DigProgress".Translate(stagesCompleted, RequiredStages);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref stagesCompleted, "stagesCompleted", 1);
            Scribe_Values.Look(ref workLeftThisStage, "workLeftThisStage", 0f);
        }
    }
}
