using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // RETIRED_MUTATORS_PORT (owner, 2026-10-19: "Reproduce the mutators into our own code, then proceed
    // with deprecation of the donors."). The C# half of our own TileMutatorDefs that replace the Alpha
    // Biomes (sarg.alphabiomes) world-tile mutators the Ash'karr save carries. Mapping and per-row notes:
    // design/RimMandrake/retired_mutators_port_2026-10-19.md. Every class here is written from the
    // behaviour the donor's DESCRIPTION and def fields promise plus vanilla's own workers (read through
    // RimSage); no donor code was read or copied. Each mechanic reads its own Mod Settings toggle.

    /// <summary>Data a ported mutator carries for the workers below. Unused fields stay at their defaults.</summary>
    public class RM_TileMutatorPortExtension : DefModExtension
    {
        /// <summary>RM_TileMutatorWorker_AncientVent: the vent building it places (vanilla vent layout).</summary>
        public ThingDef ventDef;

        /// <summary>RM_TileMutatorWorker_ExtraAnimals: the animal that infests the tile.</summary>
        public PawnKindDef pawnKind;
        /// <summary>Size of the group placed when the map is generated.</summary>
        public IntRange pawnCountRange = new IntRange(3, 6);
        /// <summary>Mean days between later groups wandering in from the edge (0 or less = never).</summary>
        public float arrivalMtbDays = 15f;
        /// <summary>No later group arrives while the map already holds this many of the kind.</summary>
        public int maxOnMap = 12;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (ventDef == null && pawnKind == null)
            {
                yield return "RM_TileMutatorPortExtension sets neither ventDef nor pawnKind; the worker reading it does nothing.";
            }
        }
    }

    /// <summary>Vanilla's ancient-vent layout (5-9 vents on a ring of ancient megastructure floor, one map-wide
    /// on/off cycle) for a vent building named in the def's RM_TileMutatorPortExtension, so one class serves the
    /// freezing, gray-pall, blood-rain and death-pall vents.</summary>
    public class RM_TileMutatorWorker_AncientVent : TileMutatorWorker_AncientVent
    {
        public RM_TileMutatorWorker_AncientVent(TileMutatorDef def)
            : base(def)
        {
        }

        protected override ThingDef AncientVentDef => def.GetModExtension<RM_TileMutatorPortExtension>()?.ventDef;

        public override void GenerateNonCriticalStructures(Map map)
        {
            if (!RM_EnvironmentalHazardsSettings.worldMutatorStructuresEnabled || AncientVentDef == null)
            {
                return;
            }
            base.GenerateNonCriticalStructures(map);
        }
    }

    /// <summary>"This area is infested with X": a wild group of the kind is placed when the map is generated, and
    /// further groups wander in from the map edge over time while the map holds fewer than maxOnMap of them.</summary>
    public class RM_TileMutatorWorker_ExtraAnimals : TileMutatorWorker
    {
        private const int CheckInterval = 2500;

        public RM_TileMutatorWorker_ExtraAnimals(TileMutatorDef def)
            : base(def)
        {
        }

        private RM_TileMutatorPortExtension Ext => def.GetModExtension<RM_TileMutatorPortExtension>();

        public override void GeneratePostFog(Map map)
        {
            if (!RM_EnvironmentalHazardsSettings.worldMutatorAnimalsEnabled || Ext?.pawnKind == null)
            {
                return;
            }
            if (CellFinder.TryFindRandomCell(map, c => c.Standable(map) && !c.GetTerrain(map).IsWater && !c.Roofed(map), out IntVec3 center))
            {
                SpawnGroup(map, center);
            }
        }

        public override void Tick(Map map)
        {
            RM_TileMutatorPortExtension ext = Ext;
            if (ext?.pawnKind == null || ext.arrivalMtbDays <= 0f || !map.IsHashIntervalTick(CheckInterval))
            {
                return;
            }
            if (!RM_EnvironmentalHazardsSettings.worldMutatorAnimalsEnabled)
            {
                return;
            }
            if (!Rand.MTBEventOccurs(ext.arrivalMtbDays, GenDate.TicksPerDay, CheckInterval))
            {
                return;
            }
            int present = map.mapPawns.AllPawnsSpawned.Count(p => p.kindDef == ext.pawnKind);
            if (present >= ext.maxOnMap)
            {
                return;
            }
            if (RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 entry, map, CellFinder.EdgeRoadChance_Animal))
            {
                SpawnGroup(map, entry);
            }
        }

        private void SpawnGroup(Map map, IntVec3 center)
        {
            RM_TileMutatorPortExtension ext = Ext;
            int n = ext.pawnCountRange.RandomInRange;
            for (int i = 0; i < n; i++)
            {
                IntVec3 cell = CellFinder.RandomClosewalkCellNear(center, map, 6);
                Pawn pawn = PawnGenerator.GeneratePawn(ext.pawnKind);
                GenSpawn.Spawn(pawn, cell, map);
            }
        }
    }

    /// <summary>Low background radiation: now and then (mean every ~15 days per map) one free colonist on the
    /// map takes a random non-archite xenogene they do not already carry. Biotech is assumed (all DLC are).</summary>
    public class RM_GameCondition_AmbientRadiation : GameCondition
    {
        private const int CheckInterval = 2500;
        private const float MutationMtbDays = 15f;

        public override void GameConditionTick()
        {
            base.GameConditionTick();
            if (Find.TickManager.TicksGame % CheckInterval != 0 || !ModsConfig.BiotechActive)
            {
                return;
            }
            if (!RM_EnvironmentalHazardsSettings.ambientRadiationMutationsEnabled)
            {
                return;
            }
            foreach (Map map in AffectedMaps)
            {
                if (Rand.MTBEventOccurs(MutationMtbDays, GenDate.TicksPerDay, CheckInterval))
                {
                    TryMutateOne(map);
                }
            }
        }

        private void TryMutateOne(Map map)
        {
            if (!map.mapPawns.FreeColonistsSpawned.Where(p => p.genes != null).TryRandomElement(out Pawn pawn))
            {
                return;
            }
            if (!DefDatabase<GeneDef>.AllDefsListForReading
                    .Where(g => g.biostatArc == 0 && g.canGenerateInGeneSet && g.endogeneCategory == EndogeneCategory.None
                                && g.prerequisite == null && pawn.genes.GetGene(g) == null)
                    .TryRandomElement(out GeneDef gene))
            {
                return;
            }
            pawn.genes.AddGene(gene, true);
            Messages.Message("RM_AmbientRadiationMutation".Translate(pawn.Named("PAWN"), gene.LabelCap.Named("GENE")),
                pawn, MessageTypeDefOf.NegativeEvent);
        }
    }

    /// <summary>A mood thought that holds while the ThoughtDef's gameCondition is active on the pawn's map and the
    /// pawn stands under open sky (the "moldy environment": being outdoors is the cost).</summary>
    public class RM_ThoughtWorker_OutdoorsDuringCondition : ThoughtWorker
    {
        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            if (!RM_EnvironmentalHazardsSettings.moldyEnvironmentMoodEnabled || def.gameCondition == null || !p.Spawned)
            {
                return ThoughtState.Inactive;
            }
            if (!p.Map.gameConditionManager.ConditionIsActive(def.gameCondition))
            {
                return ThoughtState.Inactive;
            }
            return p.Position.Roofed(p.Map) ? ThoughtState.Inactive : ThoughtState.ActiveAtStage(0);
        }
    }

    /// <summary>On a buildable ThingDef: it may only be placed on a map whose world tile carries one of these
    /// mutators (the geothermal-hotspot plant, the micro-fungi collector).</summary>
    public class RM_RequiresTileMutatorExtension : DefModExtension
    {
        public List<TileMutatorDef> mutators = new List<TileMutatorDef>();
    }

    public class RM_PlaceWorker_RequiresTileMutator : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            RM_RequiresTileMutatorExtension ext = checkingDef.GetModExtension<RM_RequiresTileMutatorExtension>();
            if (ext == null || ext.mutators.NullOrEmpty() || !RM_EnvironmentalHazardsSettings.worldMutatorBuildingGatesEnabled)
            {
                return true;
            }
            IList<TileMutatorDef> here = map.TileInfo?.Mutators;
            if (here != null && ext.mutators.Any(m => here.Contains(m)))
            {
                return true;
            }
            return new AcceptanceReport("RM_RequiresTileMutator".Translate(
                string.Join(", ", ext.mutators.Select(m => m.label)).Named("FEATURES")));
        }
    }

    public class RM_CompProperties_MagmaVent : CompProperties
    {
        public float eruptionMtbDays = 2f;
        public float radius = 3.9f;
        public int damage = 12;

        public RM_CompProperties_MagmaVent()
        {
            compClass = typeof(RM_CompMagmaVent);
        }
    }

    /// <summary>A magma vent: between eruptions it is warm ground; an eruption (mean every eruptionMtbDays) is a
    /// burst of fire and searing gas around the vent.</summary>
    public class RM_CompMagmaVent : ThingComp
    {
        private RM_CompProperties_MagmaVent Props => (RM_CompProperties_MagmaVent)props;

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (!parent.Spawned || !RM_EnvironmentalHazardsSettings.magmaVentEruptionsEnabled)
            {
                return;
            }
            if (Rand.MTBEventOccurs(Props.eruptionMtbDays, GenDate.TicksPerDay, GenTicks.TickRareInterval))
            {
                Erupt();
            }
        }

        public void Erupt()
        {
            Map map = parent.Map;
            IntVec3 center = parent.OccupiedRect().CenterCell;
            for (int i = 0; i < 6; i++)
            {
                FleckMaker.ThrowSmoke(center.ToVector3Shifted() + Gen.RandomHorizontalVector(1.5f), map, Rand.Range(2f, 3.5f));
                FleckMaker.ThrowMicroSparks(center.ToVector3Shifted() + Gen.RandomHorizontalVector(1.5f), map);
            }
            GenExplosion.DoExplosion(center, map, Props.radius, DamageDefOf.Flame, parent,
                damAmount: Mathf.Max(1, Mathf.RoundToInt(Props.damage * RM_EnvironmentalHazardsSettings.hazardDamageMultiplier)),
                chanceToStartFire: 0.6f, ignoredThings: new List<Thing> { parent });
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            if (DebugSettings.ShowDevGizmos)
            {
                yield return new Command_Action
                {
                    defaultLabel = "DEV: Erupt",
                    action = Erupt
                };
            }
        }
    }
}
