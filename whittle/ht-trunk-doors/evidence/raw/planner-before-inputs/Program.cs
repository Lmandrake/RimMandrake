
using System;
using System.Collections.Generic;
using RimMandrake.HugeThings;
class Program {
 static long K(int x,int z)=>RM_HugeFootprintKernel.Key(x,z);
 static List<long> Wanted=new List<long>{K(-1,1),K(0,1)};
 static List<long> Plan(Func<long,CellFlags> flags) {
#if OLD
 return Planner.Plan(Wanted,new List<long>{K(0,0)},flags,new CellBox(-4,-3,4,7));
#else
 return Planner.Plan(Wanted,flags,new CellBox(-4,-3,4,7));
#endif
 }
 static int Main() {
 var walls=new HashSet<long>();
 for(int x=-3;x<=3;x++){if(x!=0)walls.Add(K(x,2));walls.Add(K(x,6));}
 for(int z=3;z<6;z++){walls.Add(K(-3,z));walls.Add(K(3,z));}
 foreach(var p in new[]{(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(1,1)})walls.Add(K(p.Item1,p.Item2));
 Func<long,CellFlags> flags=k=>walls.Contains(k)?CellFlags.Protected:
  k==K(0,4)?CellFlags.Passable|CellFlags.Pawn:
  k==K(0,2)?CellFlags.Passable|CellFlags.Protected:CellFlags.Passable;
 var actual=Plan(flags);
 Console.WriteLine("entrance contacts accepted="+actual.Count+" of "+Wanted.Count);
 foreach(CellFlags exclusion in new[]{CellFlags.Pawn,CellFlags.Item,CellFlags.Protected}) {
 var negative=Plan(k=>Wanted.Contains(k)?CellFlags.Passable|exclusion:flags(k));
 Console.WriteLine("excluded="+exclusion+" accepted="+negative.Count);
 if(negative.Count!=0)return 2;
 }
 return actual.Count==2?0:1;
 }
}
