using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Globalization;
using Verse;
using RimWorld;
using RimMandrake.HugeThings;
using RimMandrake.TitanicCreatures;
using K = RimMandrake.TitanicCreatures.RM_TitanicKernel;
using U = RimMandrake.TitanicCreatures.TitanicTierUtility;

class Program
{
    static int checks;
    static void Check(bool ok, string label) { checks++; if (!ok) throw new Exception(label); }
    static ThingDef Race(float size, params float[] factors) => new ThingDef { defName="Local", race=new RaceProperties {
        baseBodySize=size, lifeStageAges=factors?.Select(f=>new LifeStageAge { def=new LifeStageDef {bodySizeFactor=f} }).ToList() } };
    static void Force(ThingDef race, bool? value) { race.modExtensions = new List<DefModExtension> { new RM_TitanicExtension {forceEnabled=value} }; }
    static int Tier(float size, float[] ladder, int force) => force<0 ? 0 : Math.Max(force>0 ? 1 : 0, ladder.Count(t=>size>=t));
    static bool Gate(int adult, int spacing, int bits) {
        bool[] f=Enumerable.Range(0,8).Select(i=>(bits&(1<<i))!=0).ToArray();
        // Independent rejection list: optout, nontitan lineage, water mismatch, season, hints, occupied supported T3.
        if (f[0] || adult<2 || f[1]!=f[2] || !f[6]) return false;
        if (f[3] && !f[4] || !f[3] && !f[5]) return false;
        return spacing!=3 || !f[7];
    }
    static bool ProductionGate(int adult, int spacing, int bits) {
        bool[] f=Enumerable.Range(0,8).Select(i=>(bits&(1<<i))!=0).ToArray();
        return K.TitanEventEligible(adult,spacing,f[0],f[1],f[2],f[3],f[4],f[5],f[6],f[7]);
    }
    static void Row(ThingDef race, int adult, int spacing, string name) {
        Check((int)U.AdultTier(race)==adult,name+" AdultTier");
        Check((int)U.SpacingTier(race)==spacing,name+" SpacingTier");
        for(int bits=0;bits<256;bits++) {
            bool current=ProductionGate(adult,spacing,bits), old=ProductionGate(adult,adult,bits);
            Check(current==Gate(adult,spacing,bits),name+" gates "+bits);
            if ((bits&128)==0) Check(current==old,name+" unoccupied eligibility changed");
            if (current!=old) Check(!old && adult==3 && spacing<3,name+" unexpected delta");
        }
        Console.WriteLine(name+" AdultTier="+adult+" SpacingTier="+spacing);
    }
    static void MainChecks() {
        DefDatabase<RM_TitanicTierDef>.AllDefsListForReading.Add(new RM_TitanicTierDef());
        var juvenile=Race(32,.2f,.5f); var ordinary=Race(32,.2f,.5f,1); var growth=Race(3,4);
        Row(juvenile,3,2,"juvenile-only"); Row(ordinary,3,3,"ordinary"); Row(growth,2,2,"growth above one");
        Check(U.DefQualifies(Race(6,.2f,.5f)),"conservative comp attachment at base6 versus max3");
        foreach(var race in new[]{juvenile,ordinary,growth}) foreach(var stage in race.race.lifeStageAges) {
            var pawn=new Pawn {def=race,factor=stage.def.bodySizeFactor};
            Check((int)U.GetTier(pawn)==Tier(pawn.BodySize,new float[]{4,8,20},0),"runtime actual size");
        }
        Check((int)U.GetTier(new Pawn {def=ordinary,factor=.2f})==1 && (int)U.AdultTier(ordinary)==3,"normal calf allowance");
        Check(U.GetTier(null)==TitanicTier.None && U.AdultTier(null)==TitanicTier.None && U.SpacingTier(null)==TitanicTier.None && !U.DefQualifies(null),"null inputs");
        Check(U.SpacingTier(new ThingDef())==TitanicTier.None,"not a race");
        Row(Race(32,null),3,3,"missing list"); Row(Race(32),3,3,"empty list");
        foreach(bool missingDef in new[]{false,true}) {
            var malformed=Race(32,.2f,.5f); malformed.race.lifeStageAges.Add(missingDef ? new LifeStageAge() : null);
            Row(malformed,3,3,missingDef?"null stage def":"null entry");
        }
        foreach(float bad in new[]{0f,-1f,float.NaN,float.PositiveInfinity,float.NegativeInfinity}) Row(Race(32,.2f,.5f,bad),3,3,"malformed factor "+bad);
        foreach(bool? force in new bool?[]{null,false,true}) {
            foreach(var race in new[]{Race(32,.2f,.5f),Race(1,.5f),Race(3,4)}) {
                Force(race,force); int f=force==false?-1:force==true?1:0;
                float max=race.race.lifeStageAges.Max(a=>a.def.bodySizeFactor);
                Row(race,Tier(race.race.baseBodySize*Math.Max(1,max),new float[]{4,8,20},f),Tier(race.race.baseBodySize*max,new float[]{4,8,20},f),"force "+f+" size "+race.race.baseBodySize);
                Check(U.DefQualifies(race)==(force==false?false:force==true || race.race.baseBodySize*Math.Max(1,max)>=4),"force comp");
                Check((int)U.GetTier(new Pawn {def=race,factor=max})==Tier(race.race.baseBodySize*max,new float[]{4,8,20},f),"force runtime");
            }
        }
        RM_HugeThingsSettings.tierThresholdsCustom=true;
        foreach(var ladder in new[]{new float[]{4,8,16},new float[]{4,18,30},new float[]{4,8,40},new float[]{4,8,12}}) {
            RM_HugeThingsSettings.tierT1MinBodySize=ladder[0]; RM_HugeThingsSettings.tierT2MinBodySize=ladder[1]; RM_HugeThingsSettings.tierT3MinBodySize=ladder[2];
            Row(juvenile,Tier(32,ladder,0),Tier(16,ladder,0),"custom "+string.Join(",",ladder));
            Row(growth,Tier(12,ladder,0),Tier(12,ladder,0),"growth custom");
            Check((int)U.GetTier(new Pawn{def=juvenile,factor=.5f})==Tier(16,ladder,0),"custom GetTier");
        }
        foreach(var ladder in new[]{new float[]{4,8,8},new float[]{8,4,20},new float[]{0,8,20},new float[]{float.NaN,8,20},new float[]{4,8,float.PositiveInfinity}}) {
            RM_HugeThingsSettings.tierT1MinBodySize=ladder[0]; RM_HugeThingsSettings.tierT2MinBodySize=ladder[1]; RM_HugeThingsSettings.tierT3MinBodySize=ladder[2]; Row(juvenile,3,2,"invalid custom fallback");
        }
        RM_HugeThingsSettings.tierT1MinBodySize=4; RM_HugeThingsSettings.tierT2MinBodySize=18; RM_HugeThingsSettings.tierT3MinBodySize=30;
        RM_HugeThingsSettings.giantAnimalsEnabled=false; Row(juvenile,3,2,"animal toggle disables custom");
        RM_HugeThingsSettings.giantAnimalsEnabled=true; RM_HugeThingsSettings.tierThresholdsCustom=false; Row(juvenile,3,2,"custom toggle disabled");
        // No tier/stage cache: mutate only this local fixture then read again.
        juvenile.race.lifeStageAges[1].def.bodySizeFactor=1; Row(juvenile,3,3,"stage edited in same process");
        juvenile.race.lifeStageAges[1].def.bodySizeFactor=.5f; Row(juvenile,3,2,"stage restored in same process");
        // Shipped definition lookup is cached separately. Verify missing-def fallback is logged once; no live database mutation.
        var field=typeof(U).GetField("cachedThresholds",BindingFlags.NonPublic|BindingFlags.Static);
        int initialErrors=Log.Errors;
        field.SetValue(null,null); DefDatabase<RM_TitanicTierDef>.AllDefsListForReading.Clear();
        Check(U.Thresholds.t3MinBodySize==20 && Log.Errors==initialErrors+1,"missing shipped fallback");
        Check(U.Thresholds.t3MinBodySize==20 && Log.Errors==initialErrors+1,"fallback cache logs once");
    }
    static int Main() { CultureInfo.CurrentCulture=CultureInfo.DefaultThreadCurrentCulture=CultureInfo.InvariantCulture; try { MainChecks(); Console.WriteLine("checks="+checks+" production adapter/kernel controls passed (engine stand-in L0)"); return 0; } catch(Exception e) { Console.WriteLine("FAIL "+e); return 1; } }
}
