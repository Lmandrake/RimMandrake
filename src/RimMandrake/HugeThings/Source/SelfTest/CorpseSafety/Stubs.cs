// Small engine stand-in: exercises production queue, placement transaction and butcher prefix without a game.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
namespace HarmonyLib { public class HarmonyPatch : Attribute { public HarmonyPatch(Type t, string method) {} } }
namespace RimWorld { public static class StatDefOf { public static object MeatAmount = new object(), LeatherAmount = new object(); } }
namespace Verse
{
    public struct IntVec3
    {
        public int x, z; public IntVec3(int x, int z) { this.x=x; this.z=z; }
        public bool InBounds(Map m) => x >= 0 && z >= 0 && x < 40 && z < 40;
        public Thing GetEdifice(Map m) => GetThingList(m).FirstOrDefault(t => t.Edifice);
        public List<Thing> GetThingList(Map m) => m.Cells.TryGetValue((x,z), out var ts) ? ts : new List<Thing>();
    }
    public class ThingDef { public IntVec3 size = new IntVec3(1,1); }
    public class Thing
    {
        private static int ids;
        public int thingIDNumber = ++ids; public bool Destroyed, Spawned, Edifice;
        public IntVec3 Position; public Map Map; public string LabelCap => "test titan";
        public virtual void SpawnSetup(Map map, bool respawningAfterLoad) {}
        public void DeSpawn() { foreach (var ts in Map.Cells.Values) ts.Remove(this); Spawned=false; }
        public void Destroy() { if (Spawned) DeSpawn(); Destroyed=true; }
    }
    public class Pawn : Thing
    {
        public int Tier=3; public RaceProperties RaceProps = new RaceProperties();
        public float GetStatValue(object stat) => stat == RimWorld.StatDefOf.MeatAmount ? 10000 : 100;
        public IEnumerable<Thing> ButcherProducts(Pawn butcher, float efficiency) => Array.Empty<Thing>();
    }
    public class RaceProperties { public ThingDef meatDef=new ThingDef(), leatherDef=new ThingDef(); }
    public class Corpse : Thing { public Pawn InnerPawn=new Pawn(); }
    public class Map
    {
        public Dictionary<(int,int),List<Thing>> Cells = new Dictionary<(int,int),List<Thing>>();
        public RimMandrake.TitanicCreatures.MapComponent_TitanicCorpseSites Component;
        public ListerThings listerThings;
        public Map() { listerThings=new ListerThings(this); Component=new RimMandrake.TitanicCreatures.MapComponent_TitanicCorpseSites(this); }
        public T GetComponent<T>() where T : class => Component as T;
    }
    public class ListerThings
    {
        Map map; public ListerThings(Map m) { map=m; }
        public List<Thing> ThingsInGroup(ThingRequestGroup g) => map.Cells.Values.SelectMany(x=>x).OfType<Corpse>().Cast<Thing>().Distinct().ToList();
    }
    public enum ThingRequestGroup { Corpse }
    public class MapComponent
    {
        protected Map map; public MapComponent(Map m) { map=m; }
        public virtual void MapComponentTick() {} public virtual void ExposeData() {} public virtual void FinalizeInit() {}
    }
    public struct Rot4 { public static Rot4 North; }
    public class CellRect : IEnumerable<IntVec3>
    {
        IntVec3 p,s; public CellRect(IntVec3 p, IntVec3 s) { this.p=p; this.s=s; }
        public IEnumerator<IntVec3> GetEnumerator() { for(int z=0;z<s.z;z++) for(int x=0;x<s.x;x++) yield return new IntVec3(p.x+x-(s.x-1)/2,p.z+z-(s.z-1)/2); }
        IEnumerator IEnumerable.GetEnumerator()=>GetEnumerator();
    }
    public static class GenAdj { public static CellRect OccupiedRect(IntVec3 p, Rot4 r, IntVec3 s)=>new CellRect(p,s); }
    public enum WipeMode { VanishOrMoveAside }
    public static class GenSpawn
    {
        public static bool ThrowBefore, ThrowAfter;
        public static Thing Spawn(Thing t, IntVec3 p, Map m, WipeMode mode)
        {
            bool site=t is RimMandrake.TitanicCreatures.Building_TitanicCorpseSite;
            if(site && ThrowBefore) throw new Exception("planted before-spawn failure");
            var rect=GenAdj.OccupiedRect(p, Rot4.North, site ? new IntVec3(4,4) : new IntVec3(1,1));
            foreach(var c in rect)
            {
                if(!m.Cells.TryGetValue((c.x,c.z),out var ts)) m.Cells[(c.x,c.z)]=ts=new List<Thing>();
                // Deliberately emulate a destructive spawn: the production preflight must protect every other Thing.
                foreach(var old in ts.ToArray()) old.Destroy();
                ts.Add(t);
            }
            t.Map=m; t.Position=p; t.Spawned=true;
            if(site && ThrowAfter) throw new Exception("planted after-spawn failure");
            return t;
        }
    }
    public static class ThingMaker { public static Thing MakeThing(ThingDef d)=>new RimMandrake.TitanicCreatures.Building_TitanicCorpseSite(); }
    public static class GenMath { public static int RoundRandom(float f)=>(int)f; }
    public static class Find { public static TickManager TickManager=new TickManager(); }
    public class TickManager { public int TicksGame; }
    public static class Log { public static void ErrorOnce(string message,int id) {} }
    public enum LookMode { Reference }
    public enum LoadSaveMode { Saving, LoadingVars, PostLoadInit }
    public static class Scribe { public static LoadSaveMode mode; }
    public static class Scribe_Collections
    {
        public static List<Corpse> Saved;
        public static void Look(ref List<Corpse> list,string key,LookMode mode)
        {
            if(Scribe.mode==LoadSaveMode.Saving) Saved=new List<Corpse>(list);
            if(Scribe.mode==LoadSaveMode.LoadingVars) list=new List<Corpse>(Saved);
        }
    }
}
namespace RimMandrake.HugeThings
{
    public static class RM_HugeThingsSettings { public static bool CorpseSiteActive=true, YieldCurveActive=true; }
}
namespace RimMandrake.TitanicCreatures
{
    public enum TitanicTier { None=0,T1=1,T2=2,T3=3 }
    public static class TitanicTierUtility { public static TitanicTier GetTier(Verse.Pawn p)=>(TitanicTier)p.Tier; }
    public static class YieldCurveUtility { public static float SubLinearFactor(Verse.Pawn p,TitanicTier t)=>0.5f; }
    public static class RM_TitanicCreaturesDefOf { public static Verse.ThingDef RM_TitanicCorpseSite=new Verse.ThingDef {size=new Verse.IntVec3(4,4)}; }
    public class Building_TitanicCorpseSite : Verse.Thing
    {
        public int Meat,Leather;
        public void Setup(string label,Verse.ThingDef meat,int m,Verse.ThingDef leather,int l) { Meat=m; Leather=l; Edifice=true; }
    }
}
