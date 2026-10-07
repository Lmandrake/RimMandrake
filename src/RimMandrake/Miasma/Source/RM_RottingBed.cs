using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Miasma
{
    // MIASMA_ROTTING_BED_CORPSES_1 (owner typed 2026-10-02: "That rotting bed could also be used to corpse dispose as
    // well... and produce skulls and bones!"). The spent decay cell is a corpse store: haulers bring corpses to it
    // like any storage (its filter takes flesh corpses only, one per cell), and it rots them down one at a time.
    // When one is done it is stripped (gear drops beside the bed), destroyed, and leaves RM_Bones by body size and,
    // for a humanlike with its head, a vanilla Skull naming whose it was (CompHasSources, as JobDriver_ExtractSkull
    // does). Building_Storage.Accepts is not virtual, so the switch cannot stop the hauling: with it off the bed
    // still holds corpses and nothing rots down.
    public class RM_RottingBedExtension : DefModExtension
    {
        /// <summary>RM_Bones per unit of body size (a human is 1.0). // INVENTED</summary>
        public float bonesPerBodySize = 8f;
        public ThingDef bonesDef;
    }

    public class RM_Building_RottingBed : Building_Storage
    {
        private Corpse rotting;
        private int rotTicks;

        public RM_RottingBedExtension Ext => def.GetModExtension<RM_RottingBedExtension>() ?? new RM_RottingBedExtension();

        public static int RotDownTicks => RM_MiasmaKernel.RotDownTicks(RM_MiasmaSettings.rottingBedRotDays, GenDate.TicksPerDay);

        public Corpse Rotting => rotting;
        public int RotTicks => rotTicks;

        public static bool CanRot(Thing t)
        {
            return t is Corpse c && c.InnerPawn != null && c.InnerPawn.RaceProps.IsFlesh;
        }

        public override void TickRare()
        {
            base.TickRare();
            if (!Spawned || !RM_MiasmaSettings.rottingBedCorpsesEnabled)
            {
                return;
            }
            // the clock (restart on a new corpse, +250 per rare tick, done at the setting's length) is RM_MiasmaKernel.RotStep, offline-fuzzed
            bool valid = rotting != null && !rotting.Destroyed && rotting.Spawned && this.OccupiedRect().Contains(rotting.Position);
            Corpse candidate = valid ? null : slotGroup.HeldThings.FirstOrDefault(CanRot) as Corpse;
            int target = rotting != null ? 0 : -1;       // the kernel only needs to know whether a corpse is being rotted
            int candidateId = candidate != null ? 0 : -1;
            RM_MiasmaKernel.RotStep(ref target, ref rotTicks, valid, candidateId, RotDownTicks, out bool done);
            if (!valid) rotting = candidate;
            if (done)
            {
                RotDown(rotting);
                rotting = null;
            }
        }

        /// <summary>Consume the corpse now and leave its bones and skull. Public for the proof hook.</summary>
        public List<Thing> RotDown(Corpse corpse)
        {
            var made = new List<Thing>();
            Map map = Map;
            IntVec3 at = corpse.Position;
            Pawn inner = corpse.InnerPawn;
            corpse.Strip(false);
            ThingDef skull = DefDatabase<ThingDef>.GetNamedSilentFail("Skull");
            if (skull != null && inner.RaceProps.Humanlike
                && inner.health.hediffSet.GetNotMissingParts().Any(p => p.def == BodyPartDefOf.Head))
            {
                Thing s = ThingMaker.MakeThing(skull);
                s.TryGetComp<CompHasSources>()?.AddSource(inner.LabelShort);
                made.Add(s);
            }
            ThingDef bones = Ext.bonesDef ?? DefDatabase<ThingDef>.GetNamedSilentFail("RM_Bones");
            if (bones != null)
            {
                foreach (int stack in RM_MiasmaKernel.StackSplit(RottingBedMath.BonesFor(inner.BodySize, Ext.bonesPerBodySize), bones.stackLimit))
                {
                    Thing b = ThingMaker.MakeThing(bones);
                    b.stackCount = stack;
                    made.Add(b);
                }
            }
            string label = corpse.LabelShortCap;
            corpse.Destroy(DestroyMode.Vanish);
            foreach (Thing t in made)
            {
                GenPlace.TryPlaceThing(t, at, map, ThingPlaceMode.Near);
            }
            Messages.Message(label + " has rotted down in the rotting bed.", new LookTargets(made.Count > 0 ? made[0] : this),
                MessageTypeDefOf.NeutralEvent, false);
            return made;
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string mine;
            if (!RM_MiasmaSettings.rottingBedCorpsesEnabled)
            {
                mine = "Corpse rot-down switched off in Mod Settings.";
            }
            else if (rotting != null && !rotting.Destroyed)
            {
                mine = "Rotting down: " + rotting.LabelShortCap + " (" + ((float)rotTicks / RotDownTicks).ToStringPercent() + ")";
            }
            else
            {
                mine = "Rots corpses down to bones, one at a time.";
            }
            return s.NullOrEmpty() ? mine : s + "\n" + mine;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref rotting, "rotting");
            Scribe_Values.Look(ref rotTicks, "rotTicks", 0);
        }
    }

    public static class RottingBedMath
    {
        /// <summary>Bones left by a body this size: body size x per-size, at least 1.</summary>
        public static int BonesFor(float bodySize, float perBodySize)
        {
            return RM_MiasmaKernel.BonesFor(bodySize, perBodySize);
        }
    }

    /// <summary>Proof hook for the decay_cells chain (static_call): spawns a rotting bed and a dead human, stores
    /// the corpse in it, rots it down at once, and reports what came out.</summary>
    public static class RM_RottingBedProof
    {
        public static string ProofCorpse(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef bedDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_RottingBed");
            if (map == null || bedDef == null)
            {
                return "ERROR no map or no RM_RottingBed";
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 30,
                    c => GenAdj.OccupiedRect(c, Rot4.North, bedDef.size).All(x => x.InBounds(map) && x.Standable(map)
                         && x.GetFirstBuilding(map) == null && x.GetFirstItem(map) == null), out IntVec3 cell))
            {
                return "ERROR no clear 2x2 cell";
            }
            var bed = (RM_Building_RottingBed)GenSpawn.Spawn(ThingMaker.MakeThing(bedDef), cell, map);
            bed.SetFaction(Faction.OfPlayer);
            // An ADULT baseliner: a generated colonist can be a child or teen (Biotech life stages scale BodySize
            // below 1), which left 6 bones where the proof wanted 8 (run17 Miasma, 2026-10-03). The curve was right.
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDefOf.Colonist, Faction.OfPlayer,
                fixedBiologicalAge: 30f, fixedChronologicalAge: 30f, forceBaselinerChance: 1f));
            GenSpawn.Spawn(p, cell, map);
            p.Kill(null);
            Corpse corpse = p.Corpse;
            bool accepts = corpse != null && bed.Accepts(corpse);
            string name = p.LabelShort;
            float size = p.BodySize;
            List<Thing> made = corpse != null ? bed.RotDown(corpse) : new List<Thing>();
            Thing skull = made.FirstOrDefault(t => t.def.defName == "Skull");
            string src = skull == null ? "" : skull.Label + " " + skull.TryGetComp<CompHasSources>()?.CompInspectStringExtra();
            return "accepts=" + accepts + " corpseGone=" + (corpse == null || corpse.Destroyed)
                   + " bones=" + made.Where(t => t.def.defName == "RM_Bones").Sum(t => t.stackCount)
                   + " skull=" + (skull != null) + " skullNamesSource=" + (skull != null && src.Contains(name))
                   + " bodySize=" + size.ToString("0.00") + " expectBones=" + RottingBedMath.BonesFor(size, bed.Ext.bonesPerBodySize);
        }
    }
}
