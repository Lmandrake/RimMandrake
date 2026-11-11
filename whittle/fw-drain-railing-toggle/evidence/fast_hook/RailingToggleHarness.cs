// RAILING_TOGGLE_FIX_KEEPS_DECONSTRUCT: complete production methods are generated at build time by
// RailingToggleHarness.targets. These are explicit ENGINE doubles, not copies of the toggle algorithm.
using System;
using System.Collections.Generic;
using System.Linq;
namespace RimMandrake.FlowWorks.SelfTest.RailingHarness
{
    internal record struct IntVec3(int x, int z)
    {
        public bool InBounds(Map m) => x >= 0 && z >= 0 && x < 100 && z < 100;
        public List<Thing> GetThingList(Map m) => m.thingGrid.ThingsListAtFast(this);
    }
    internal class ThingDef
    {
        public ThingDef entityDefToBuild;
        public bool IsBlueprint, IsFrame, MadeFromStuff, IsStuff;
        public StuffProperties stuffProps;
        public List<ThingDefCountClass> costList;
    }
    internal class StuffProperties { public bool accepted = true; public bool CanMake(ThingDef d) => accepted; }
    internal class ThingDefCountClass { public ThingDef thingDef; }
    internal enum DestroyMode { Cancel, Vanish }
    internal class Thing
    {
        public ThingDef def, Stuff; public Map Map; public IntVec3 Position;
        public bool Spawned; public DestroyMode? destroyed; public string look; public Faction faction;
        public void Destroy(DestroyMode mode) { destroyed=mode; Spawned=false; Position.GetThingList(Map).Remove(this); }
        public void SetFactionDirect(Faction f) => faction=f;
    }
    internal class Building_SuspensionRailing : Thing { }
    internal class Building_SuspensionDeck : Thing { public bool Collapsed; }
    internal class ThingGrid
    {
        readonly Dictionary<IntVec3,List<Thing>> cells=new();
        public List<Thing> ThingsListAtFast(IntVec3 c) { if (!cells.ContainsKey(c)) cells[c]=new(); return cells[c]; }
    }
    internal class Map
    {
        public ThingGrid thingGrid=new(); public DesignationManager designationManager=new();
        public RM_MapComponent_SuspensionBridges component;
        public T GetComponent<T>() where T:class => component as T;
    }
    internal class DesignationDef { }
    internal static class DesignationDefOf { public static readonly DesignationDef Deconstruct=new(); }
    internal class Designation
    {
        public Thing target; public DesignationDef def; internal DesignationManager manager;
        public Designation(Thing t, DesignationDef d) {target=t;def=d;}
        public void Delete() => manager.RemoveDesignation(this);
    }
    internal class DesignationManager
    {
        public readonly List<Designation> all=new();
        public Designation DesignationOn(Thing t, DesignationDef d) => all.FirstOrDefault(v=>v.target==t && v.def==d);
        public void AddDesignation(Designation d) {d.manager=this;all.Add(d);}
        public void RemoveDesignation(Designation d) => all.Remove(d);
    }
    internal class Faction { public static readonly Faction OfPlayer=new(); }
    internal class Rot4 { public static readonly Rot4 North=new(); }
    internal static class DebugSettings { public static bool godMode; }
    internal static class RM_SuspensionDefOf { public static ThingDef RM_SuspensionRailing; }
    internal static class RM_SpanUtility
    { public static Thing DeckAt(Map m, IntVec3 c) => c.GetThingList(m).OfType<Building_SuspensionDeck>().FirstOrDefault(t=>t.Spawned && !t.Collapsed); }
    internal static class GenStuff { public static ThingDef fallback; public static ThingDef DefaultStuffFor(ThingDef d)=>fallback; }
    internal static class ThingMaker
    { public static Thing MakeThing(ThingDef d,ThingDef s) => new Building_SuspensionRailing {def=d,Stuff=s}; }
    internal static class GenSpawn
    {
        public static void Spawn(Thing t,IntVec3 c,Map m,Rot4 r)
        { t.Map=m;t.Position=c;t.Spawned=true;c.GetThingList(m).Add(t); }
    }
    internal static class RM_SuspensionLooks
    { public static void Apply(Thing t,string look)=>t.look=look; public static string StyleFor(ThingDef d,string look)=>look; }
    internal static class GenConstruct
    {
        public static bool allowed=true;
        public record Acceptance(bool Accepted);
        public static Acceptance CanPlaceBlueprintAt(ThingDef d,IntVec3 c,Rot4 r,Map m)=>new(allowed);
        public static void PlaceBlueprintForBuild(ThingDef d,IntVec3 c,Map m,Rot4 r,Faction f,ThingDef s,object p,string style)
        { var t=new Thing {def=new ThingDef {entityDefToBuild=d,IsBlueprint=true},Stuff=s,look=style,faction=f};GenSpawn.Spawn(t,c,m,r); }
    }
    // Geometry double: two lanes, indices 1..LastDeck are deck sites. Production iteration is extracted intact.
    internal class SuspensionBridgeRecord
    { public bool railings=true; public int width=2,LastDeck=2; public int length=>LastDeck+2; public string look="Industrial"; public IntVec3 Cell(int lane,int i)=>new(lane+10,i+10); }
    internal class Gizmo { }
    internal class Command_Toggle : Gizmo
    { public string defaultLabel,defaultDesc; public object icon; public Func<bool> isActive; public Action toggleAction; }
    internal static class TexCommand { public static object ForbidOff=new(); }
    internal sealed partial class RM_MapComponent_SuspensionBridges
    {
        public Map map; public Dictionary<IntVec3,SuspensionBridgeRecord> index=new();
        public RM_MapComponent_SuspensionBridges(Map m) {map=m;m.component=this;}
        public void PlaceForTest(IntVec3 c) => PlaceRailing(c);
        public void RemoveForTest(IntVec3 c) => RemoveRailing(c);
    }
    internal static class Find { public static Map CurrentMap; }
    internal static partial class RM_SuspensionProofs
    {
        static bool Cell(string s,out IntVec3 c) {var p=s.Split(',');c=new();if(p.Length!=2||!int.TryParse(p[0],out int x)||!int.TryParse(p[1],out int z))return false;c=new(x,z);return true;}
    }
    internal static class RailingToggleChecks
    {
        static void A(bool ok,string why) {if(!ok) throw new Exception(why);}
        sealed class Site
        {
            public Map m=new(); public SuspensionBridgeRecord r=new(); public RM_MapComponent_SuspensionBridges b;
            public ThingDef steel=new() {IsStuff=true,stuffProps=new()},wood=new() {IsStuff=true,stuffProps=new()};
            public ThingDef def=new() {MadeFromStuff=true}; public IntVec3 c=>r.Cell(0,1);
            public Site()
            { b=new(m);RM_SuspensionDefOf.RM_SuspensionRailing=def;GenStuff.fallback=steel;GenConstruct.allowed=true;DebugSettings.godMode=false;
              for(int l=0;l<r.width;l++)for(int i=1;i<=r.LastDeck;i++){var c=r.Cell(l,i);b.index[c]=r;GenSpawn.Spawn(new Building_SuspensionDeck {def=new(),Stuff=wood},c,m,Rot4.North);} }
            public Building_SuspensionRailing Rail(IntVec3? pos=null)
            {var t=new Building_SuspensionRailing {def=def,Stuff=wood,look=r.look};GenSpawn.Spawn(t,pos??c,m,Rot4.North);return t;}
            public bool Decon(Thing t)=>m.designationManager.DesignationOn(t,DesignationDefOf.Deconstruct)!=null;
        }
        public static void Run(Action<string,Action> Case)
        {
            Case("RailingToggle_proof_player_mode",()=>{
                var s=new Site();Find.CurrentMap=s.m;var rail=s.Rail();DebugSettings.godMode=true;
                string off=RM_SuspensionProofs.ProofRails("10,11;off;player");A(off.Contains("on=False")&&s.Decon(rail)&&rail.Spawned&&DebugSettings.godMode,"player proof queues removal and restores god mode");
                string on=RM_SuspensionProofs.ProofRails("10,11;on;player");A(on.Contains("on=True")&&!s.Decon(rail)&&rail.Spawned&&DebugSettings.godMode,"player proof cancels removal and restores mode");
                RM_SuspensionProofs.ProofRails("10,11;on;player");A(!s.Decon(rail)&&rail.Spawned,"repeat player proof safe");
                A(RM_SuspensionProofs.ProofRails("10,11;off;bogus").StartsWith("REFUSED")&&s.r.railings,"unknown proof mode refuses");
                RM_SuspensionProofs.ProofRails("10,11;off");A(!rail.Spawned&&DebugSettings.godMode,"legacy proof still god off");
            });
            Case("RailingToggle_player_off_on_identity",()=>{
                var s=new Site();var rails=new List<Thing>();
                for(int l=0;l<s.r.width;l++)for(int i=1;i<=s.r.LastDeck;i++)rails.Add(s.Rail(s.r.Cell(l,i)));
                var other=new DesignationDef();var keep=new Designation(rails[0],other);s.m.designationManager.AddDesignation(keep);
                var outsider=s.Rail(new(60,60));s.m.designationManager.AddDesignation(new(outsider,DesignationDefOf.Deconstruct));
                var off=(Command_Toggle)RM_MapComponent_SuspensionBridges.RailingGizmo(s.m,s.r);off.toggleAction();off.toggleAction();
                A(!s.r.railings && rails.All(s.Decon) && s.m.designationManager.all.Count==6,"off must mark each actual railing once");
                var on=(Command_Toggle)RM_MapComponent_SuspensionBridges.RailingGizmo(s.m,s.r);on.toggleAction();on.toggleAction();s.b.SetRailings(s.r,true);
                A(s.r.railings && rails.All(t=>t.Spawned && !s.Decon(t)),"on must retain original railing identities and cancel removal");
                A(s.m.designationManager.all.Contains(keep) && s.Decon(outsider),"preserve unrelated designation and outside deconstruct");
                A(rails.All(t=>t.Stuff==s.wood && t.look==s.r.look),"keep original material/style");
                A(rails.All(t=>t.Position.GetThingList(s.m).Count==2),"no duplicate build at existing railings");
            });
            Case("RailingToggle_multiple_railings_one_cell",()=>{
                var s=new Site();var a=s.Rail();var b=s.Rail();s.b.SetRailings(s.r,false);A(s.Decon(a)&&s.Decon(b),"off marks all");
                s.b.SetRailings(s.r,true);A(!s.Decon(a)&&!s.Decon(b)&&a.Spawned&&b.Spawned,"cancel all matched built railings");
            });
            Case("RailingToggle_blueprint_frame_controls",()=>{
                foreach(bool frame in new[]{false,true}){var s=new Site();var t=new Thing {def=new ThingDef{entityDefToBuild=s.def,IsFrame=frame,IsBlueprint=!frame},Stuff=s.wood,look=s.r.look};GenSpawn.Spawn(t,s.c,s.m,Rot4.North);
                s.b.PlaceForTest(s.c);s.b.PlaceForTest(s.c);A(s.c.GetThingList(s.m).Count==2 && t.Spawned,"pending build prevents duplicate");
                var unrelated=new Thing{def=new ThingDef{entityDefToBuild=new(),IsBlueprint=true}};GenSpawn.Spawn(unrelated,s.c,s.m,Rot4.North);
                s.b.RemoveForTest(s.c);A(t.destroyed==DestroyMode.Cancel&&unrelated.Spawned,"off cancels only rail plan");}
            });
            Case("RailingToggle_new_build_material_style_god",()=>{
                foreach(bool god in new[]{false,true}){var s=new Site();DebugSettings.godMode=god;s.r.railings=false;s.b.SetRailings(s.r,true);
                var t=s.c.GetThingList(s.m).Single(x=>x is not Building_SuspensionDeck);A(t.Stuff==s.wood&&t.look==s.r.look&&t.faction==Faction.OfPlayer,"new material/style/faction");
                A(god ? t is Building_SuspensionRailing : t.def.IsBlueprint,"correct placement path");s.b.PlaceForTest(s.c);A(s.c.GetThingList(s.m).Count==2,"repeat no duplicate");s.b.SetRailings(s.r,false);A(!t.Spawned&&t.destroyed==(god?DestroyMode.Vanish:DestroyMode.Cancel),"off destroys/cancels correct mode");}
            });
            Case("RailingToggle_stuff_fallback_and_refusal",()=>{
                var s=new Site();var d=RM_MapComponent_SuspensionBridges.StructuralDeckAt(s.m,s.c);d.Stuff.stuffProps.accepted=false;
                d.def.costList=new(){new(){thingDef=s.steel}};A(RM_MapComponent_SuspensionBridges.RailingStuffFor(s.def,d)==s.steel,"cost-list fallback");d.def.costList=null;A(RM_MapComponent_SuspensionBridges.RailingStuffFor(s.def,d)==s.steel,"default fallback");
                s.def.MadeFromStuff=false;A(RM_MapComponent_SuspensionBridges.RailingStuffFor(s.def,d)==null,"unstuffed rail");GenConstruct.allowed=false;s.b.PlaceForTest(s.c);A(s.c.GetThingList(s.m).Count==1,"placement refusal");
            });
            Case("RailingToggle_missing_def_and_missing_deck",()=>{
                var s=new Site();var rail=s.Rail();s.b.SetRailings(s.r,false);RM_SuspensionDefOf.RM_SuspensionRailing=null;s.b.SetRailings(s.r,true);A(s.Decon(rail)&&rail.Spawned,"missing def keeps original no-op");
                RM_SuspensionDefOf.RM_SuspensionRailing=s.def;s.b.SetRailings(s.r,false);RM_MapComponent_SuspensionBridges.StructuralDeckAt(s.m,s.c).Collapsed=true;s.b.SetRailings(s.r,true);A(s.Decon(rail),"no deck remains untouched");
            });
        }
    }
}
