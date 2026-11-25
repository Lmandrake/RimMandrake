// Engine stand-ins for the production work giver. No map or Unity runtime is started.
using System;
using System.Collections.Generic;
using System.Linq;
using Verse;
using Verse.AI;

namespace Verse
{
    public class Thing
    {
        public int thingIDNumber;
        public bool Spawned = true, Destroyed;
        public Map Map;
        public ThingDef def = new ThingDef();
        public bool IsForbidden(Pawn pawn) => false;
    }

    public class ThingDef { public bool destroyable = true; }
    public class Plant : Thing { public float Growth; }
    public class Pawn : Thing { public bool CanReach(Thing t, PathEndMode mode, Danger danger) => false; }
    public enum Danger { Deadly }
    public class Map
    {
        public RimMandrake.HugeThings.MapComponent_HugeFootprints Footprints;
        public DesignationManager designationManager = new DesignationManager();
        public T GetComponent<T>() where T : class => Footprints as T;
    }

    public class DesignationManager
    {
        private readonly List<Designation> designations = new List<Designation>();
        public void Add(Thing thing, DesignationDef def) => designations.Add(new Designation { target = thing, Def = def });
        public IEnumerable<Designation> SpawnedDesignationsOfDef(DesignationDef def)
            => designations.Where(d => d.Def == def && d.target.Thing.Spawned);
        public Designation DesignationOn(Thing thing, DesignationDef def)
            => SpawnedDesignationsOfDef(def).FirstOrDefault(d => d.target.Thing == thing);
    }

    public class DesignationDef { }
    public class Designation { public Target target; public DesignationDef Def; }
    public struct Target
    {
        public Thing Thing;
        public static implicit operator Target(Thing t) => new Target { Thing = t };
    }

    public class ThingRequest { public static ThingRequest ForDef(ThingDef d) => new ThingRequest(); }
    public class WorkGiverDef { public object Worker = new RimWorld.WorkGiver_PlantsCut(); }
    public static class DefDatabase<T> where T : new()
    {
        private static readonly Dictionary<string, T> defs = new Dictionary<string, T>();
        public static T GetNamed(string name)
        {
            if (!defs.TryGetValue(name, out T def)) defs[name] = def = new T();
            return def;
        }
    }
    public static class Log { public static void ErrorOnce(string message, int key) { } }
}

namespace Verse.AI
{
    public enum PathEndMode { Touch }
    public enum TargetIndex { A, B, C }
    public class JobDef { }
    public class Job { public JobDef def; public Target targetA, targetC; public List<Target> targetQueueA; public bool playerForced; }
    public class JobDriver_PlantWork { public Job job; public Pawn pawn; }
    public class Toil
    {
        public TargetIndex GotoTarget;
        public Toil FailOn(Func<bool> fail) => this;
    }
    public static class ToilFailConditions
    {
        public static T FailOnCannotTouch<T>(this T toil, TargetIndex i, PathEndMode m) => toil;
    }

    public static class Toils_Goto
    {
        public static Toil GotoThing(TargetIndex i, PathEndMode m, bool parent) => new Toil { GotoTarget = i };
    }
    public static class JobMaker
    {
        public static void ReturnToPool(Job job) { }
        public static Job MakeJob(JobDef def, Target target) => new Job { def = def, targetA = target };
    }
}

namespace RimWorld
{
    public static class DesignationDefOf
    {
        public static readonly DesignationDef CutPlant = new DesignationDef(), HarvestPlant = new DesignationDef();
    }

    public static class JobDefOf
    {
        public static readonly JobDef CutPlantDesignated = new JobDef(), HarvestDesignated = new JobDef();
    }

    public class WorkGiver_PlantsCut
    {
        public virtual PathEndMode PathEndMode => PathEndMode.Touch;
        public virtual ThingRequest PotentialWorkThingRequest => null;
        public virtual bool ShouldSkip(Pawn pawn, bool forced = false) => false;
        public virtual IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn) => Array.Empty<Thing>();
        public virtual Job JobOnThing(Pawn pawn, Thing thing, bool forced = false)
            => thing is Plant plant && plant.Growth >= 0.40f && pawn.Map.designationManager.DesignationOn(plant, DesignationDefOf.HarvestPlant) != null
                ? new Job { def = JobDefOf.HarvestDesignated, targetA = plant, playerForced = forced }
                : null;
        public virtual string PostProcessedGerund(Job job) => "";
    }

    public class JobDriver_PlantCut_Designated : JobDriver_PlantWork { }
    public class JobDriver_PlantHarvest_Designated : JobDriver_PlantWork { }
}

namespace RimMandrake.HugeThings
{
    public static class RM_HugeThingsSettings { public static bool PlantTrunkActive = true; }
    public static class HugeThingsDefOf { public static ThingDef RM_HugeTrunkBlocker = new ThingDef(); }
    public class Building_TrunkBlocker : Thing { }
    public class MapComponent_HugeFootprints
    {
        private readonly Plant owner;
        private readonly Building_TrunkBlocker trunk;
        public MapComponent_HugeFootprints(Plant owner, Building_TrunkBlocker trunk) { this.owner = owner; this.trunk = trunk; }
        public IEnumerable<Building_TrunkBlocker> CutBlockers(Plant plant) => plant == owner ? new[] { trunk } : Array.Empty<Building_TrunkBlocker>();
        public IEnumerable<Plant> CutOwners(Building_TrunkBlocker blocker) => blocker == trunk ? new[] { owner } : Array.Empty<Plant>();
        public bool HasCutClaim(Plant plant, Building_TrunkBlocker blocker) => plant == owner && blocker == trunk;
    }
}
