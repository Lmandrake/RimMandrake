// Engine boundary doubles only. HosePorts, RM_HoseBands, HoseBandMath and geometry compile whole, unchanged.
using System;
using System.Collections.Generic;
using System.Linq;
using Verse;
namespace Verse {
 public class DefModExtension {}
 public enum ThingCategory { Building }
 public class CompProperties { public Type compClass; }
 public class ThingDef { public ThingCategory category; public List<CompProperties> comps; public object extension; public T GetModExtension<T>() where T:class => extension as T; }
 public struct IntVec3 : IEquatable<IntVec3> {
  public int x,y,z; public IntVec3(int a,int b,int c){x=a;y=b;z=c;} public bool IsValid=>x>=0&&z>=0;
  public bool InBounds(Map m)=>m!=null&&x>=0&&z>=0&&x<m.Size.x&&z<m.Size.z;
  public List<Thing> GetThingList(Map m)=>m.grid.TryGetValue(this,out var v)?v:new List<Thing>();
  public bool Equals(IntVec3 o)=>x==o.x&&z==o.z; public override bool Equals(object o)=>o is IntVec3 v&&Equals(v); public override int GetHashCode()=>x*397^z;
  public static bool operator ==(IntVec3 a,IntVec3 b)=>a.Equals(b); public static bool operator !=(IntVec3 a,IntVec3 b)=>!a.Equals(b);
 }
 public struct CellRect { public int minX,minZ,Width,Height; public CellRect(int x,int z,int w,int h){minX=x;minZ=z;Width=w;Height=h;} public bool Contains(IntVec3 c)=>c.x>=minX&&c.x<minX+Width&&c.z>=minZ&&c.z<minZ+Height; }
 public class Thing { public ThingDef def; public Map Map; public IntVec3 Position; public int thingIDNumber; public bool Spawned=true; public CellRect footprint; public CellRect OccupiedRect()=>footprint; public T TryGetComp<T>() where T:class => (this as ThingWithComps)?.GetComp<T>(); }
 public class ThingWithComps:Thing { public object comp; public T GetComp<T>() where T:class=>comp as T; }
 public class Map { public IntVec3 Size=new IntVec3(64,0,64); public Dictionary<IntVec3,List<Thing>> grid=new(); public RimMandrake.FlowWorks.RM_MapComponent_Excavation eng=new(); public object hoses; public bool ramp,ladder; public T GetComponent<T>() where T:class => hoses as T;
  public void Add(Thing t) {t.Map=this;for(int x=t.footprint.minX;x<t.footprint.minX+t.footprint.Width;x++)for(int z=t.footprint.minZ;z<t.footprint.minZ+t.footprint.Height;z++){var c=new IntVec3(x,0,z);if(!grid.ContainsKey(c))grid[c]=new();grid[c].Add(t);}}
 }
 public static class Find { public static List<Map> Maps=new(); }
}
namespace RimMandrake.FlowWorks {
 public class RM_MapComponent_Excavation { public Dictionary<IntVec3,int> depth=new(); public int ClimbCellCount=>depth.Count; public int ClimbDepthAt(IntVec3 c)=>depth.TryGetValue(c,out var v)?v:0; public int HollowDepthAt(IntVec3 c)=>ClimbDepthAt(c); public bool IsExcavated(IntVec3 c)=>ClimbDepthAt(c)>0; }
 public static class RM_SuperdeepTrap { public static RM_MapComponent_Excavation EngineOf(Map m)=>m.eng; public static int StepDepthAt(Map m,RM_MapComponent_Excavation e,IntVec3 c)=>e.ClimbDepthAt(c); }
 public static class RM_PitRamp { public static bool Joins(Map m,IntVec3 a,IntVec3 b,int ad,int bd)=>m.ramp; }
 public class RM_CompLadder {public bool raised;}
 public static class RM_LadderUtility {public static Thing LadderAt(Map m,IntVec3 c)=>m.ladder?new ThingWithComps{comp=new RM_CompLadder()}:null;public static bool HangsToward(Thing t,IntVec3 c)=>true;public static bool Reaches(Thing t)=>true;}
}
namespace RimMandrake.FlowWorks.Pits { public static class RM_PitCoverUtility {public static bool IsCovered(Map m,IntVec3 c)=>false;} public static class RM_SpanUtility {public static Thing DeckAt(Map m,IntVec3 c)=>null;} }
namespace RimMandrake.FlowWorks.Machinery {
 public static class RM_MachinerySettings {public static bool lineCrossingRulesEnabled=true;}
 public static class RM_LineCrossing {public static LineSurface SurfaceAt(Map m,IntVec3 c)=>LineSurface.SolidGround;}
 public static class RM_LiquidNet {public static bool IsPipe(Thing t)=>false;public static RM_NetRole RoleOfKind(Thing t)=>t is RimMandrake.FlowWorks.LiquidTypes.Building_LiquidPump?RM_NetRole.Machine:RM_NetRole.None;}
}
namespace RimMandrake.FlowWorks.LiquidTypes {public class Building_LiquidPump:ThingWithComps {} public class Building_LiquidTank:ThingWithComps {}}
namespace RimMandrake.FlowWorks.Hose {
 public class CompHoseReel {public ThingWithComps parent;public bool laid;public IntVec3 far;public HoseReelRect Rect=>new(parent.footprint.minX,parent.footprint.minZ,parent.footprint.Width,parent.footprint.Height);}
 public class RM_MapComponent_Hoses { public List<CompHoseReel> reels=new(); public IReadOnlyList<CompHoseReel> OrderedReels()=>reels;public CompHoseReel RelayOf(CompHoseReel r)=>null; }
}
