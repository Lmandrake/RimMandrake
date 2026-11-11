using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Verse;
using RimMandrake.HugeThings;
class Program
{
    static int checks;
    static void Check(bool condition,string why) { checks++; if(!condition) throw new Exception(why); }
    static Map Map()
    {
        var m=new Map(); Find.Maps.Add(m);
        typeof(MapComponent_HugeFootprints).GetField("initialized",BindingFlags.Instance|BindingFlags.NonPublic).SetValue(m.Component,true);
        return m;
    }
    static CompHugeFootprint Add(Map m,int id,int side,bool blocking,int? grid=null)
    {
        int x=grid.HasValue?20+(grid.Value%20)*20:200,z=grid.HasValue?20+(grid.Value/20)*20:200;
        var mask=new HugeMask{MeasuredSize=side};
        for(int dz=0;dz<=side;dz++) for(int dx=-side;dx<=side;dx++) mask.Contact.Add(RM_HugeFootprintKernel.Key(dx,dz));
        var c=new CompHugeFootprint{parent=new Plant{thingIDNumber=id,Map=m,Position=new IntVec3(x,0,z),def=new ThingDef{category=ThingCategory.Plant}},Mask=mask,
            Sig=new FootprintSignature{RootX=x,RootZ=z,DrawX=side,Visual=1,BlockScale=1,Blocking=blocking,OldEnough=true}};
        m.Component.Register(c); return c;
    }
    static void Reset() { Current.Game=new object(); Find.Maps.Clear(); CompHugeFootprint.Completion.Clear(); }
    static void Tick(int tick,params Map[] maps)
    {
        Find.TickManager.TicksGame=tick;
        foreach(var map in maps)
        {
            map.Component.MapComponentTick();
            string report=MapComponent_HugeFootprints.DebugCounts(map);
            int used=int.Parse(report.Split(" work=")[1].Split('/')[0]);
            int visits=int.Parse(report.Split(" ownersVisited=")[1].Split(' ')[0]);
            Check(used<=MapComponent_HugeFootprints.WorkUnitsPerTick,"global per-tick cap exceeded");
            Check(visits<=MapComponent_HugeFootprints.RefreshesPerTick,"owner budget exceeded");
        }
    }
    static int[] Schedule()
    {
        Reset(); var map=Map(); var owners=new List<CompHugeFootprint>();
        for(int i=0;i<257;i++)
        {
            var c=Add(map,500+i*250,2,true,i); // every owner had the SAME phase in the old scheduler
            owners.Add(c);
            // Non-movable items keep every candidate pending so this exercises repeated retries, not only refreshes.
            foreach(long key in c.DesiredKeys()) GenSpawn.Spawn(new Thing{def=new ThingDef{category=ThingCategory.Item}},
                new IntVec3(RM_HugeFootprintKernel.KeyX(key),0,RM_HugeFootprintKernel.KeyZ(key)),map,WipeMode.Vanish);
        }
        var previous=new Dictionary<int,int>(); var events=new List<int>(); var retries=new Dictionary<int,int>();
        for(int tick=0;tick<550;tick++)
        {
            Tick(tick,map);
            retries=(Dictionary<int,int>)typeof(MapComponent_HugeFootprints).GetField("retryAt",BindingFlags.Instance|BindingFlags.NonPublic).GetValue(map.Component);
            foreach(var pair in retries.OrderBy(p=>p.Key))
                if(!previous.TryGetValue(pair.Key,out int due) || due!=pair.Value)
                { previous[pair.Key]=pair.Value; events.Add(tick*1000000+pair.Key); }
        }
        Check(owners.All(c=>c.Taken>0),"same-phase refresh owner starved");
        Check(retries.Count==owners.Count && retries.Values.All(due=>due>500),"same-phase pending owner was not retried");
        return events.ToArray();
    }
    static int Main()
    {
        try
        {
            Check(Schedule().SequenceEqual(Schedule()),"schedule was not reproducible");
            Reset(); var map=Map(); var huge=Add(map,1,120,true);
            Tick(0,map); Check(huge.Taken==0,"large geometry was not sliced across ticks");
            for(int tick=1;tick<100 && huge.Taken==0;tick++) Tick(tick,map);
            Check(huge.Taken==1,"large mask never completed under budget");
            int claims=CountClaims(map,huge.OwnerId); Check(claims>10000,"large-mask fixture did not exercise enough claims");
            int labels=Building_TrunkBlocker.LabelWrites;
            map.Component.Deregister(huge);
            Check(Building_TrunkBlocker.LabelWrites==labels,"death hook relabelled remaining blockers");
            Check(CountClaims(map,huge.OwnerId)==claims,"death hook performed synchronous footprint cleanup");
            for(int tick=101;tick<2200 && CountClaims(map,huge.OwnerId)>0;tick++) Tick(tick,map);
            Check(CountClaims(map,huge.OwnerId)==0,"mass-removal queue did not drain");
            Reset(); var a=Map(); var b=Map();
            var ca=Add(a,1,120,true); var cb=Add(b,2,120,true);
            for(int tick=0;tick<150 && (ca.Taken==0 || cb.Taken==0);tick++) Tick(tick,a,b);
            Check(ca.Taken==1 && cb.Taken==1,"loaded map starved under shared budget");
            // A moved/minified plant can re-register with its old id before queued removal drains.
            Reset(); map=Map(); var moved=Add(map,7,4,true);
            for(int tick=0;tick<10 && moved.Taken==0;tick++) Tick(tick,map);
            map.Component.Deregister(moved); map.Component.Register(moved);
            for(int tick=11;tick<30;tick++) Tick(tick,map);
            Check(CountClaims(map,moved.OwnerId)>0,"queued removal erased re-registered plant claims");
            // Changed-cell removal preserves overlapping owners and does no work on unrelated claims.
            var ledger=new ClaimLedger();
            for(int owner=0;owner<1000;owner++) ledger.AddCell(owner,RM_HugeFootprintKernel.Key(owner,0));
            ledger.AddCell(1001,0); int affected=0;
            while(ledger.RemoveNext(0,out long cell,out bool freed))
            { affected++; Check(cell==0 && !freed && ledger.PrimaryOwner(cell)==1001,"shared primary owner lost"); }
            Check(affected==1 && ledger.ClaimedCount==1000,"removal work was not proportional to affected claims");
            // Tiny read budgets must abort before returning an unsafe partial plan or unbounded geometry result.
            foreach(int limit in new[]{0,1,10,16})
            {
                var budget=new FootprintWorkBudget(limit); bool exhausted=false;
                try { Planner.Plan(new List<long>{0},k=>CellFlags.Passable,new CellBox(-4,-4,4,4),budget:budget); }
                catch(FootprintBudgetExhausted) { exhausted=true; }
                Check(exhausted && budget.Used<=limit,"planner did not respect tiny budget");
            }
            Console.WriteLine("PASS footprint work budget: "+checks+" checks; latency UNVERIFIED"); return 0;
        }
        catch(Exception e) { Console.WriteLine("FAIL footprint work budget: "+e); return 1; }
    }
    static int CountClaims(Map map,int id)
    {
        var ledger=(ClaimLedger)typeof(MapComponent_HugeFootprints).GetField("ledger",BindingFlags.Instance|BindingFlags.NonPublic).GetValue(map.Component);
        return ledger.CountOf(id);
    }
}
