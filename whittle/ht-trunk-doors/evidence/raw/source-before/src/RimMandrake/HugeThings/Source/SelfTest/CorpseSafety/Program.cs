using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Verse;
using RimMandrake.TitanicCreatures;
using RimMandrake.HugeThings;
class Program
{
    static int checks;
    static void Check(bool b,string msg) { checks++; if(!b) throw new Exception(msg); }
    static Corpse Place(Map map,int x=20,int z=20)
    {
        var c=new Corpse(); GenSpawn.Spawn(c,new IntVec3(x,z),map,WipeMode.VanishOrMoveAside); return c;
    }
    static void Tick(Map map,int now) { Find.TickManager.TicksGame=now; map.Component.MapComponentTick(); }
    static int Main()
    {
        try
        {
            foreach(bool curve in new[]{false,true})
            foreach(bool sites in new[]{false,true})
            foreach(int tier in new[]{0,1,2,3})
            {
                RM_HugeThingsSettings.CorpseSiteActive=sites; RM_HugeThingsSettings.YieldCurveActive=curve;
                IEnumerable<Thing> result=null; float efficiency=1;
                bool run=Patch_ButcherYieldCurve.Prefix(new Pawn{Tier=tier},ref efficiency,ref result);
                Check(run == !(sites && tier==3),"T3 butcher bypass / disabled-feature regression");
                if(!run) Check(result!=null && !result.Any(),"blocked T3 yielded products");
                if(run) Check(efficiency == (curve && (tier==1 || tier==2) ? 0.5f : 1f),"T1/T2 yield changed");
            }
            RM_HugeThingsSettings.CorpseSiteActive=true;
            foreach(bool edge in new[]{false,true})
            {
                var map=new Map(); var corpse=Place(map,edge?0:20,edge?0:20);
                Thing obstacle=null;
                if(!edge) { obstacle=new Thing{Edifice=true}; GenSpawn.Spawn(obstacle,new IntVec3(21,21),map,WipeMode.VanishOrMoveAside); }
                map.Component.Enqueue(corpse); Tick(map,0);
                Check(corpse.Spawned && !corpse.Destroyed,"failed placement lost corpse");
                Check(obstacle==null || (!obstacle.Destroyed && obstacle.Spawned),"surrounding edifice wiped");
                Scribe.mode=LoadSaveMode.Saving; map.Component.ExposeData();
                Check(Scribe_Collections.Saved.Contains(corpse),"failed placement dropped pending state");
                map.Component=new MapComponent_TitanicCorpseSites(map);
                Scribe.mode=LoadSaveMode.LoadingVars; map.Component.ExposeData();
                Scribe.mode=LoadSaveMode.PostLoadInit; map.Component.ExposeData();
                if(edge) { corpse.DeSpawn(); GenSpawn.Spawn(corpse,new IntVec3(20,20),map,WipeMode.VanishOrMoveAside); }
                else obstacle.Destroy();
                Tick(map,251);
                Check(corpse.Destroyed,"pending conversion did not resume after load and clear space");
                var site=map.Cells.Values.SelectMany(ts=>ts).OfType<Building_TitanicCorpseSite>().Distinct().Single();
                Check(site.Meat==10000 && site.Leather==100,"conversion changed source pools");
            }
            foreach(bool after in new[]{false,true})
            {
                var map=new Map(); var corpse=Place(map); GenSpawn.ThrowBefore=!after; GenSpawn.ThrowAfter=after;
                map.Component.Enqueue(corpse); Tick(map,0);
                Check(corpse.Spawned && !corpse.Destroyed,"spawn exception lost original corpse");
                Check(!map.Cells.Values.SelectMany(ts=>ts).OfType<Building_TitanicCorpseSite>().Any(),"failed transaction left duplicate pool");
                GenSpawn.ThrowBefore=GenSpawn.ThrowAfter=false; Tick(map,251);
                Check(corpse.Destroyed,"failed spawn not retried");
            }
            // A non-edifice item in any site cell must also survive preflight unchanged.
            {
                var map=new Map(); var corpse=Place(map); var item=new Thing();
                GenSpawn.Spawn(item,new IntVec3(21,21),map,WipeMode.VanishOrMoveAside);
                map.Component.Enqueue(corpse); Tick(map,0);
                Check(item.Spawned && !item.Destroyed && corpse.Spawned,"non-edifice Thing wiped");
            }
            // Legacy loaded corpse with no serialized queue must enter through BOTH load reconciliation and SpawnSetup.
            {
                var map=new Map(); var corpse=Place(map);
                map.Component.FinalizeInit(); Tick(map,0); Check(corpse.Destroyed,"legacy corpse skipped");
                corpse=Place(map,10,10);
                typeof(Patch_Corpse_SpawnSetup_TitanicSite).GetMethod("Postfix",BindingFlags.NonPublic|BindingFlags.Static)
                    .Invoke(null,new object[]{corpse,map,true});
                Tick(map,1); Check(corpse.Destroyed,"respawningAfterLoad skipped");
            }
            Console.WriteLine("PASS corpse-site safety: "+checks+" checks against production placement/queue/butcher code");
            return 0;
        }
        catch(Exception e) { Console.WriteLine("FAIL corpse-site safety: "+e); return 1; }
    }
}
