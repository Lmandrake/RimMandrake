// Sparse engine stand-in; the scheduler, geometry, claim ledger and planner are production source.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
namespace RimWorld { }
namespace Verse
{
    public enum ThingCategory { Item, Building, Plant, Other }
    public enum DestroyMode { Vanish }
    public enum WipeMode { Vanish }
    public class ThingDef
    {
        public ThingCategory category; public bool IsBlueprint, IsFrame, destroyable=true, HasSingleOrMultipleInteractionCells;
        public object entityDefToBuild; public List<IntVec3> multipleInteractionCellOffsets;
        public PlantProperties plant=new PlantProperties();
        public bool HasModExtension<T>() => category==ThingCategory.Plant;
    }
    public class PlantProperties { public bool IsTree; }
    public struct Rot4 { }
    public struct IntVec3 : IEquatable<IntVec3>
    {
        public int x,z; public IntVec3(int x,int y,int z) { this.x=x; this.z=z; }
        public bool Equals(IntVec3 c)=>x==c.x && z==c.z;
        public override bool Equals(object o)=>o is IntVec3 c && Equals(c);
        public static bool operator ==(IntVec3 a,IntVec3 b)=>a.Equals(b);
        public static bool operator !=(IntVec3 a,IntVec3 b)=>!a.Equals(b);
        public override int GetHashCode()=>HashCode.Combine(x,z);
        public static IntVec3 operator +(IntVec3 a,IntVec3 b)=>new IntVec3(a.x+b.x,0,a.z+b.z);
        public bool InBounds(Map m)=>x>=0 && z>=0 && x<512 && z<512;
        public List<Thing> GetThingList(Map m)=>m.Cells.TryGetValue(this,out var ts)?ts:new List<Thing>();
        public bool Walkable(Map m)=>InBounds(m) && !GetThingList(m).Any(t=>t is RimMandrake.HugeThings.Building_TrunkBlocker || t.def.category==ThingCategory.Building);
        public bool Standable(Map m)=>Walkable(m);
        public int GetItemCount(Map m)=>GetThingList(m).Count(t=>t.def.category==ThingCategory.Item);
        public int GetMaxItemsAllowedInCell(Map m)=>1;
        public Pawn GetFirstPawn(Map m)=>GetThingList(m).OfType<Pawn>().FirstOrDefault();
        public object GetSlotGroup(Map m)=>null;
    }
    public class CellRect : IEnumerable<IntVec3>
    {
        public int minX,minZ,maxX,maxZ;
        public int Width=>maxX-minX+1; public int Height=>maxZ-minZ+1;
        public static CellRect FromLimits(int x,int z,int x1,int z1)=>new CellRect { minX=x,minZ=z,maxX=x1,maxZ=z1 };
        public CellRect ClipInsideMap(Map m)=>FromLimits(Math.Max(0,minX),Math.Max(0,minZ),Math.Min(511,maxX),Math.Min(511,maxZ));
        public IEnumerator<IntVec3> GetEnumerator() { for(int z=minZ;z<=maxZ;z++) for(int x=minX;x<=maxX;x++) yield return new IntVec3(x,0,z); }
        IEnumerator IEnumerable.GetEnumerator()=>GetEnumerator();
    }
    public class Thing
    {
        public ThingDef def=new ThingDef(); public int thingIDNumber; public bool Destroyed, Spawned=true;
        public IntVec3 Position; public Map Map; public Rot4 Rotation; public List<string> questTags;
        public string ThingID=>thingIDNumber.ToString();
        public T TryGetComp<T>() where T:class=>null;
        public void DeSpawn(DestroyMode mode) { if(Map!=null && Map.Cells.TryGetValue(Position,out var ts)) ts.Remove(this); Spawned=false; }
        public void Destroy(DestroyMode mode) { DeSpawn(mode); Destroyed=true; }
    }
    public class Pawn : Thing
    {
        public int Width=1,Height=1;
        public CellRect OccupiedRect()=>CellRect.FromLimits(Position.x,Position.z,Position.x+Width-1,Position.z+Height-1);
    }
    public class Plant : Thing { }
    public class Building_Door : Thing { }
    public class MapPawns { public List<Pawn> AllPawnsSpawned=new List<Pawn>(); }
    public class Map
    {
        public int uniqueID;
        public MapPawns mapPawns=new MapPawns(); public ListerThings listerThings;
        public Dictionary<IntVec3,List<Thing>> Cells=new Dictionary<IntVec3,List<Thing>>();
        public RimMandrake.HugeThings.MapComponent_HugeFootprints Component;
        public Map() { listerThings=new ListerThings(this); Component=new RimMandrake.HugeThings.MapComponent_HugeFootprints(this); }
        public T GetComponent<T>() where T:class=>Component as T;
    }
    public class ListerThings
    {
        Map m; public ListerThings(Map m) {this.m=m;}
        public List<Thing> ThingsOfDef(ThingDef def)=>m.Cells.Values.SelectMany(ts=>ts).Where(t=>t.def==def).ToList();
    }
    public class MapComponent
    {
        protected Map map; public MapComponent(Map m) {map=m;}
        public virtual void FinalizeInit() {} public virtual void MapComponentTick() {}
    }
    public static class Current { public static object Game=new object(); }
    public static class Find { public static List<Map> Maps=new List<Map>(); public static TickManager TickManager=new TickManager(); }
    public class TickManager { public int TicksGame; }
    public static class Log { public static void ErrorOnce(string m,int id) { throw new Exception(m); } }
    public static class GenAdj { public static IntVec3[] CardinalDirections={new IntVec3(1,0,0),new IntVec3(-1,0,0),new IntVec3(0,0,1),new IntVec3(0,0,-1)}; }
    public static class ThingUtility { public static void InteractionCellsWhenAt(List<IntVec3> cells,ThingDef d,IntVec3 p,Rot4 r,Map m) { cells.Clear(); } }
    public static class ThingMaker { public static Thing MakeThing(ThingDef d)=>new RimMandrake.HugeThings.Building_TrunkBlocker {def=d}; }
    public static class GenSpawn
    {
        public static Thing Spawn(Thing t,IntVec3 p,Map m,WipeMode mode)
        {
            if(!m.Cells.TryGetValue(p,out var ts)) m.Cells[p]=ts=new List<Thing>();
            ts.Add(t); t.Map=m; t.Position=p; t.Spawned=true; return t;
        }
    }
    public static class Extension { public static bool NullOrEmpty<T>(this List<T> list)=>list==null || list.Count==0; }
}
namespace RimMandrake.HugeThings
{
    public class RM_HugePlantExtension {}
    public class Building_TrunkBlocker : Verse.Thing
    {
        Verse.Plant source; public static int LabelWrites;
        public Verse.Plant owner { get=>source; set {source=value; LabelWrites++;} }
    }
    public static class HugeThingsDefOf { public static Verse.ThingDef RM_HugeTrunkBlocker=new Verse.ThingDef{category=Verse.ThingCategory.Building}; }
    public static class RM_HugeThingsSettings { public static bool PlantTrunkActive=true,PlantItemPushActive=false; }
    public class CompHugeFootprint
    {
        public Verse.Thing parent; public Verse.Plant Plant=>parent as Verse.Plant; public int OwnerId=>parent.thingIDNumber;
        public HugeMask Mask; public FootprintSignature Sig; public int Taken;
        public static List<int> Completion=new List<int>();
        public FootprintSignature Signature(out HugeMask mask,FootprintWorkBudget budget=null) { mask=Mask; return Sig; }
        public void MarkTaken() { Taken++; Completion.Add(OwnerId); }
        public void MarkTaken(FootprintSignature s) { Taken++; Completion.Add(OwnerId); }
        public List<long> DesiredKeys(FootprintWorkBudget budget=null)=>RM_HugeFootprintKernel.ContactCells(Sig.RootX,Sig.RootZ,RM_HugeFootprintKernel.Quad(Sig.RootX,Sig.RootZ,Sig.DrawX,Sig.Visual,0,0),1,false,Mask,budget);
        public List<long> MaxKeys()=>new List<long>{RM_HugeFootprintKernel.Key(Sig.RootX,Sig.RootZ)};
        public string DebugDescribe()=>"stand-in";
    }
}
