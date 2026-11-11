using System;
using System.Collections.Generic;
using Verse;
using RimMandrake.Shared.Slack;
using RimMandrake.FlowWorks;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.FlowWorks.LiquidTypes;
class AdapterCases {
 static int failures,checks;
 static void Check(bool ok,string name){checks++;Console.WriteLine((ok?"PASS ":"FAIL ")+name);if(!ok)failures++;}
 static ThingWithComps Thing(Map m,int id,int x,int z,int w,int h,HosePortKind k,bool pump=false){ThingWithComps t=pump?new Building_LiquidPump():new ThingWithComps();t.def=new ThingDef{extension=new HosePortExtension{kind=k}};t.thingIDNumber=id;t.Position=new IntVec3(x,0,z);t.footprint=new CellRect(x,z,w,h);m.Add(t);return t;}
 static CompHoseReel Reel(Map m,int id=100,int x=10,int z=10,int w=3,int h=2){var r=new CompHoseReel{parent=Thing(m,id,x,z,w,h,HosePortKind.None)};r.parent.comp=r;return r;}
 static void Depth(Map m,int x,int z,int d){m.eng.depth[new IntVec3(x,0,z)]=d;}
 static Thing Pick(CompHoseReel r,out Cell s,out Cell c)=>HosePorts.Find(r,out s,out c,out _);
 public static int Main(){
  foreach(var s in new[]{new Cell(1,0),new Cell(0,1),new Cell(-1,0),new Cell(0,-1)}){
   var m=new Map();var r=Reel(m);int x=s.X>0?13:s.X<0?9:11,z=s.Z>0?12:s.Z<0?9:11;
   var t=Thing(m,1,x,z,1,1,HosePortKind.Pipe);Depth(m,x-s.X,z-s.Z,4);Depth(m,x,z,4);
   Check(Pick(r,out var side,out var c)==t&&side.Equals(s)&&c.Equals(new Cell(x,z)),"multicell same-band "+s);
   Depth(m,x,z,8);Check(Pick(r,out _,out _)==null,"multicell sheer-wall "+s);
   m.ramp=true;m.ladder=true;Check(RM_HoseBands.Linked(m,new IntVec3(x-s.X,0,z-s.Z),new IntVec3(x,0,z),4,8),"route linked witness "+s);
   Check(Pick(r,out _,out _)==null,"ramp/ladder route does not authorize cross-band inlet "+s);
   RM_MachinerySettings.lineCrossingRulesEnabled=false;Check(Pick(r,out _,out _)==t,"rules-off "+s);RM_MachinerySettings.lineCrossingRulesEnabled=true;
  }
  {var m=new Map();var r=Reel(m);var t=Thing(m,1,13,10,2,2,HosePortKind.Tank);Depth(m,13,10,8);Check(Pick(r,out var s,out var c)==t&&c.Equals(new Cell(13,11)),"later valid contact of same multi-cell candidate");Depth(m,12,11,8);Check(Pick(r,out _,out _)==null,"contact body cell is not origin/centre");}
  {var m=new Map();var r=Reel(m);var bad=Thing(m,1,13,10,1,1,HosePortKind.Pipe);Depth(m,13,10,8);var good=Thing(m,2,11,12,1,1,HosePortKind.Tank);Check(Pick(r,out _,out _)==good,"invalid preferred pipe falls back to tank");Depth(m,13,10,0);Check(Pick(r,out _,out _)==bad,"pipe rank preserved");}
  {var m=new Map();var r=Reel(m);var high=Thing(m,9,13,10,1,1,HosePortKind.Pipe);var low=Thing(m,2,13,10,1,1,HosePortKind.Pipe);Check(Pick(r,out _,out _)==low,"thing-id tie independent of insertion");Depth(m,13,10,8);var west=Thing(m,3,9,11,1,1,HosePortKind.Pipe);Check(Pick(r,out _,out _)==west,"invalid east falls back west");}
  {var m=new Map();var r=Reel(m);Thing(m,1,13,12,1,1,HosePortKind.Pipe);Thing(m,2,12,11,2,1,HosePortKind.Pipe);Check(Pick(r,out _,out _)==null,"corner and overlap remain refused");}
  {var m=new Map();var r=Reel(m);var p=Thing(m,1,13,10,3,2,HosePortKind.Machine,true);Check(Pick(r,out _,out _)==p,"multi-cell pump proper side");Depth(m,13,10,8);Depth(m,13,11,8);Check(Pick(r,out _,out _)==null,"pump sheer wall refused");}
  {var m=new Map();var p=Thing(m,1,13,10,3,2,HosePortKind.Machine,true);var r=Reel(m);var other=Reel(m,10,10,9,3,2);m.hoses=new RM_MapComponent_Hoses{reels=new List<CompHoseReel>{r,other}};Depth(m,12,9,8);Depth(m,12,10,8);Check(Pick(r,out _,out _)==p,"depth-ineligible lower-id body does not reserve pump side");Depth(m,12,9,0);Depth(m,12,10,0);Check(Pick(r,out _,out _)==null,"eligible lower-id body still reserves pump side");}
  {var m=new Map();var t=Thing(m,1,11,10,1,1,HosePortKind.Pipe);var end=new IntVec3(10,0,10);Depth(m,11,10,8);Check(HosePorts.FindAt(m,end,null,out _,out _)==null,"free end differing band unchanged");Depth(m,11,10,0);Check(HosePorts.FindAt(m,end,null,out _,out _)==t,"free end equal band unchanged");Check(HosePorts.FindAt(m,t.Position,null,out _,out _)==t,"free end on-footprint unchanged");}
  {var m=new Map();var r=Reel(m,w:1,h:1);var t=Thing(m,1,11,10,1,1,HosePortKind.Pipe);Check(Pick(r,out _,out _)==t,"1x1 same band");Depth(m,10,10,8);Check(Pick(r,out _,out _)==null,"1x1 sheer band");}
  {var m=new Map();var r=Reel(m,x:0,z:0,w:2,h:3);Check(Pick(r,out _,out _)==null,"map boundary empty");var t=Thing(m,1,2,1,1,1,HosePortKind.Pipe);Check(Pick(r,out _,out _)==t,"map boundary valid side");}
  {var m=new Map();var r=Reel(m,x:10,z:12,w:2,h:2);Thing(m,1,12,10,3,4,HosePortKind.Machine,true);Check(Pick(r,out _,out _)==null,"pump adjacent wrong lane stays refused");}
  {var m=new Map();var r=Reel(m,x:11,z:10,w:2,h:2);var p=Thing(m,1,13,10,3,2,HosePortKind.Machine,true);p.Position=new IntVec3(14,0,11);
   Check(Pick(r,out _,out var c)==p&&c.Equals(new Cell(13,11)),"real-position pump selects designated port contact");
   Depth(m,13,11,8);Check(Pick(r,out _,out _)==null,"other same-band pump lane cannot bypass fixed port depth");
   Depth(m,13,11,0);Depth(m,13,10,8);Check(Pick(r,out _,out c)==p&&c.Equals(new Cell(13,11)),"invalid nonport lane cannot hide valid pump port");
  }
  Console.WriteLine($"CHECKS {checks} FAILURES {failures}");return failures==0?0:1;
 }
}
