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
    static Building_TitanicCorpseSite Site(Map map)
        => map.Cells.Values.SelectMany(ts=>ts).OfType<Building_TitanicCorpseSite>().Distinct().SingleOrDefault();

    static void CheckPlacement(string scenario)
    {
        var map = new Map();
        bool edge = scenario == "edge", loading = scenario == "load", crush = scenario == "crush";
        if (crush) map.Width = 4;
        var corpse = Place(map, edge || crush ? 0 : 20, edge || crush ? 0 : 20);
        Thing obstacle = null;
        if (crush || scenario == "wall")
        {
            obstacle = new Thing { Edifice = true };
            obstacle.def.Crushable = crush;
            GenSpawn.Spawn(obstacle, new IntVec3(crush ? 1 : 21, crush ? 1 : 21), map, WipeMode.VanishOrMoveAside);
        }
        if (loading)
        {
            Scribe.mode = LoadSaveMode.PostLoadInit;
            map.Component.ExposeData();
            Scribe.mode = LoadSaveMode.Inactive;
            map.Component.FinalizeInit();
        }
        else
        {
            map.Component.Enqueue(corpse);
            Tick(map, 0);
        }
        Check(Site(map) != null && corpse.Destroyed, scenario + ": T3 corpse did not become a site");
        Check(GenAdj.OccupiedRect(Site(map).Position, Rot4.North, new IntVec3(4,4)).All(cell => cell.InBounds(map)),
            scenario + ": site overhangs map");
        Check(obstacle == null || (crush ? obstacle.Destroyed : obstacle.Spawned && !obstacle.Destroyed),
            scenario + ": wrong crush-table decision");
    }

    static void CheckRot()
    {
        var map = new Map { Temperature = -5f };
        map.Component.Enqueue(Place(map));
        Tick(map, 0);
        var site = Site(map);
        AdvanceRot(site, 60000);
        Check(site.MeatRemaining == 10000, "frozen remains lost meat");
        map.Temperature = 5f;
        AdvanceRot(site, 120000);
        Check(site.MeatRemaining == 10000, "refrigerated meat spoiled before its vanilla threshold");
        map.Temperature = 21f;
        AdvanceRot(site, 209750);
        Check(site.MeatRemaining == 10000, "warm meat spoiled before its vanilla threshold");
        AdvanceRot(site, 210000);
        Check(site.MeatRemaining == 0 && site.MakeSessionProducts().Sum(t => t.stackCount) == 100 && !site.Destroyed,
            "meat did not rot at the vanilla threshold or leather was lost");
    }

    static void AdvanceRot(Building_TitanicCorpseSite site, int end)
    {
        while (Find.TickManager.TicksGame < end)
        {
            Find.TickManager.TicksGame += 250;
            site.TickRare();
        }
    }

    static int Main(string[] args)
    {
        try
        {
            if (args.Length != 0)
            {
                if (args[0] == "rot") CheckRot(); else CheckPlacement(args[0]);
                Console.WriteLine("PASS corpse-site " + args[0]);
                return 0;
            }
            foreach (string scenario in new[] { "edge", "wall", "crush", "load" }) CheckPlacement(scenario);
            CheckRot();

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
                var map=new Map { Width = 4 }; var corpse=Place(map,edge?0:1,edge?0:1);
                var obstacle=new Thing{Edifice=true};
                GenSpawn.Spawn(obstacle,new IntVec3(2,2),map,WipeMode.VanishOrMoveAside);
                map.Component.Enqueue(corpse); Tick(map,0);
                Check(corpse.Spawned && !corpse.Destroyed,"failed placement lost corpse");
                Check(!obstacle.Destroyed && obstacle.Spawned,"surrounding edifice wiped");
                Scribe.mode=LoadSaveMode.Saving; map.Component.ExposeData();
                Check(Scribe_Collections.Saved.Contains(corpse),"failed placement dropped pending state");
                map.Component=new MapComponent_TitanicCorpseSites(map);
                Scribe.mode=LoadSaveMode.LoadingVars; map.Component.ExposeData();
                Scribe.mode=LoadSaveMode.PostLoadInit; map.Component.ExposeData();
                Scribe.mode=LoadSaveMode.Inactive;
                map.Component.FinalizeInit();
                Check(corpse.Spawned && !corpse.Destroyed,"load lost corpse on a fully blocked map");
                obstacle.Destroy();
                Tick(map,251);
                Check(corpse.Destroyed,"pending conversion did not resume after load and clear space");
                var site=map.Cells.Values.SelectMany(ts=>ts).OfType<Building_TitanicCorpseSite>().Distinct().Single();
                Check(site.MeatRemaining==10000 && site.MakeSessionProducts().Single(t => t.def == corpse.InnerPawn.RaceProps.leatherDef).stackCount==100,"conversion changed source pools");
            }
            foreach(bool after in new[]{false,true})
            {
                var map=new Map(); var corpse=Place(map,0,0); GenSpawn.ThrowBefore=!after; GenSpawn.ThrowAfter=after;
                map.Component.Enqueue(corpse); Tick(map,0);
                Check(corpse.Spawned && !corpse.Destroyed && corpse.Position.x == 0 && corpse.Position.z == 0,"spawn exception lost or moved original corpse");
                Check(!map.Cells.Values.SelectMany(ts=>ts).OfType<Building_TitanicCorpseSite>().Any(),"failed transaction left duplicate pool");
                GenSpawn.ThrowBefore=GenSpawn.ThrowAfter=false; Tick(map,251);
                Check(corpse.Destroyed,"failed spawn not retried");
            }
            // A non-edifice item in any site cell must also survive preflight unchanged.
            {
                var map=new Map(); var corpse=Place(map); var item=new Thing();
                GenSpawn.Spawn(item,new IntVec3(21,21),map,WipeMode.VanishOrMoveAside);
                map.Component.Enqueue(corpse); Tick(map,0);
                Check(item.Spawned && !item.Destroyed && corpse.Destroyed && Site(map) != null,"non-edifice Thing was wiped or prevented relocation");
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
