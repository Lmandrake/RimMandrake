// Small engine stand-in: exercises production queue, placement transaction and butcher prefix without a game.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
namespace HarmonyLib { public class HarmonyPatch : Attribute { public HarmonyPatch(Type t, string method) {} } }
namespace UnityEngine { public static class Mathf { public static int Max(int a, int b) => Math.Max(a, b); } }
namespace RimWorld
{
    public static class StatDefOf { public static object MeatAmount = new object(), LeatherAmount = new object(); }
    public class CompProperties_Rottable { public int TicksToRotStart = 120000; }
}
namespace Verse
{
    public struct IntVec3
    {
        public int x, y, z; public IntVec3(int x, int z) : this(x, 0, z) {}
        public IntVec3(int x, int y, int z) { this.x=x; this.y=y; this.z=z; }
        public bool InBounds(Map m) => x >= 0 && z >= 0 && x < m.Width && z < m.Width;
        public Thing GetEdifice(Map m) => GetThingList(m).FirstOrDefault(t => t.Edifice);
        public List<Thing> GetThingList(Map m) => m.Cells.TryGetValue((x,z), out var ts) ? ts : new List<Thing>();
    }
    public class ThingDef
    {
        public IntVec3 size = new IntVec3(1,1);
        public bool destroyable = true, Crushable;
        public RimWorld.CompProperties_Rottable Rot;
        public T GetCompProperties<T>() where T : class => Rot as T;
    }
    public class Thing
    {
        private static int ids;
        public ThingDef def = new ThingDef();
        public int stackCount;
        public int thingIDNumber = ++ids; public bool Destroyed, Spawned, Edifice;
        public IntVec3 Position; public Map Map; public string LabelCap => "test titan";
        public virtual void SpawnSetup(Map map, bool respawningAfterLoad) {}
        public float AmbientTemperature => Map.Temperature;
        public virtual void TickRare() {}
        public virtual void ExposeData() {}
        public virtual string GetInspectString() => "";
        public void DeSpawn() { foreach (var ts in Map.Cells.Values) ts.Remove(this); Spawned=false; }
        public void Destroy(DestroyMode mode = DestroyMode.Vanish) { if (Spawned) DeSpawn(); Destroyed=true; }
    }
    public class Building : Thing { public Building() { Edifice = true; } }
    public enum DestroyMode { Vanish, KillFinalize }
    public class Pawn : Thing
    {
        public bool Dead;
        public int Tier=3; public RaceProperties RaceProps = new RaceProperties();
        public float GetStatValue(object stat) => stat == RimWorld.StatDefOf.MeatAmount ? 10000 : 100;
        public IEnumerable<Thing> ButcherProducts(Pawn butcher, float efficiency) => Array.Empty<Thing>();
    }
    public class RaceProperties { public ThingDef meatDef=new ThingDef { Rot = new RimWorld.CompProperties_Rottable() }, leatherDef=new ThingDef(); }
    public class Corpse : Thing { public Pawn InnerPawn=new Pawn(); }
    public class Map
    {
        public int Width = 40;
        public float Temperature;
        public IntVec3 Size => new IntVec3(Width, Width);
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
            t.SpawnSetup(m, false);
            if(site && ThrowAfter) throw new Exception("planted after-spawn failure");
            return t;
        }
    }
    public static class ThingMaker { public static Thing MakeThing(ThingDef d) => d == RimMandrake.TitanicCreatures.RM_TitanicCreaturesDefOf.RM_TitanicCorpseSite
        ? new RimMandrake.TitanicCreatures.Building_TitanicCorpseSite { def = d } : new Thing { def = d }; }
    public static class GenMath { public static int RoundRandom(float f)=>(int)f; }
    public static class Find { public static TickManager TickManager=new TickManager(); }
    public class TickManager { public int TicksGame; }
    public static class GenTemperature
    {
        public static float RotRateAtTemperature(float temperature) => Math.Clamp(temperature / 10f, 0f, 1f);
    }
    public static class Rand { public static bool Chance(float chance) => false; }
    public static class Translation { public static string Translate(this string s, params object[] args) => s; }
    public static class Scribe_Values { public static void Look<T>(ref T value, string key, T defaultValue = default) {} }
    public static class Scribe_Defs { public static void Look<T>(ref T value, string key) {} }
    public static class Log { public static void ErrorOnce(string message,int id) {} public static void Warning(string message) {} }
    public enum LookMode { Reference }
    public enum LoadSaveMode { Inactive, Saving, LoadingVars, PostLoadInit }
    public static class Scribe { public static LoadSaveMode mode; }
    public static class Scribe_Collections
    {
        public static void Look(ref List<Pawn> list,string key,LookMode mode) {}
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
    public static class RM_HugeThingsSettings
    {
        public static bool CorpseSiteActive=true, YieldCurveActive=true, WakeActive=true, CorpseScavengersActive, CorpseCampsActive;
        public static int corpseSiteVisitorMeatPerDay, corpseSiteScavengerMax, corpseSiteHarvestMeatPerSession = 100,
            corpseSiteHarvestLeatherPerSession = 100;
        public static float corpseSiteScavengerDailyChance, corpseSiteCampDailyChance;
    }
}
namespace RimMandrake.TitanicCreatures
{
    public enum TitanicTier { None=0,T1=1,T2=2,T3=3 }
    public static class TitanicTierUtility { public static TitanicTier GetTier(Verse.Pawn p)=>(TitanicTier)p.Tier; }
    public static class YieldCurveUtility { public static float SubLinearFactor(Verse.Pawn p,TitanicTier t)=>0.5f; }
    public static class RM_TitanicCreaturesDefOf { public static Verse.ThingDef RM_TitanicCorpseSite=new Verse.ThingDef {size=new Verse.IntVec3(4,4)}; }
    public static class CrushTableUtility
    {
        public static bool IsCrushableAtTier(Verse.Thing thing, TitanicTier tier) => thing.def.Crushable && tier == TitanicTier.T3;
    }
    public static class CorpseSiteVisitors
    {
        public static bool AtSite(Verse.Pawn p, Building_TitanicCorpseSite site) => false;
        public static IEnumerable<Verse.Pawn> DrawScavengers(Building_TitanicCorpseSite site, int n) => Array.Empty<Verse.Pawn>();
        public static IEnumerable<Verse.Pawn> MakeCamp(Building_TitanicCorpseSite site) => Array.Empty<Verse.Pawn>();
    }
}
