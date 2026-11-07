#!/usr/bin/env python3
"""selftest_natives_drink_own_water.py — every Baroque Biome native drinks its own environmental water
(NATIVES_DRINK_OWN_WATER_AUDIT_EVERY_BIOME).

Owner, 2026-11-01: "Yes, natives should drink their own environmental water. That's a ruling for all Baroque Biomes,
period, including this one." First instance: RM_Noohm and RM_Shulla standing in the Scald's boil accrued RM_Dehydration
(SCALD_NATIVES_THIRST_PROBE_PARCHED_LAKESIDE): the Scald terrains name RM_Liquid_BoilingWater, a row with no
thirstQuality (use class Never), so RM_ThirstUtility.DrinkLiquidAt returned null for everyone, natives included.

Three halves, all offline:
  A. SOURCE (the thirst code is Verse-bound; the C# SelfTest cannot run it): the production .cs, comments masked, lets a
     native animal find, keep and drink a terrain marked nativeWater, and no one else. Undo mutants must each go RED.
  A2. BEHAVIOUR: the production method text (cut from the .cs at run time) compiled with dotnet against small Verse stubs and
     RUN: a native at home water gets the liquid back, finds it, keeps the job and is hydrated; a humanlike or a stranger
     gets null. Each behaviour mutant must turn a case BAD. No dotnet exits 2 with UNMEASURED, never a pass.
  B. AUDIT over every RM_/RSW_/RUT_ BiomeDef: each Water terrain the biome paints (its def's terrains, plus Water terrains
     named after it) resolves to a liquid its natives may drink: a row the Q12 native rule already allows (any use class
     but Never), or a terrain the patches mark nativeWater. NOT_WATER is the explicit list of Water-tagged terrains that
     are not water at all. Writes Tools/native_water_audit.md; a BLOCKED row fails. The probe mutant (forget the
     nativeWater marks) must turn the Scald BLOCKED, or the audit is blind.

    python3 src/RimMandrake/FlowWorks/selftest_natives_drink_own_water.py
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
THIRST = HERE / "Source" / "Thirst"
UTIL = THIRST / "RM_ThirstUtility.cs"
JOBS = THIRST / "RM_ThirstJobs.cs"
LIQ = HERE / "Source" / "LiquidTypes" / "LiquidDef.cs"
REPORT = HERE / "Tools" / "native_water_audit.md"
sys.path.insert(0, str(HERE / "Tools"))
import selftest_water_terrains_name_liquid as W  # noqa: E402  (terrain loader, Water-tag inheritance)

# Water-tagged for pathing or freezing, not a body anything drinks: the ruling does not reach them.
NOT_WATER = {
    "RM_DeepSand": "deep sand; Water-tagged for wading only (DEEP_SAND_FIX_READS_AS_FRESHWATER)",
    "RM_SolidPropane": "frozen propane, a solid",
}


def mask_comments(text: str) -> str:
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1]); i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j])); i = j
        else:
            out.append(c); i += 1
    return "".join(out)


def body(src: str, sig: str) -> str:
    at = src.find(sig)
    if at < 0:
        return ""
    open_ = src.find("{", at)
    depth = 0
    for k in range(open_, len(src)):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[open_:k + 1]
    return ""


def flat(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def source_faults(util: str, jobs: str, liq: str) -> list[str]:
    f = []
    ext = body(liq, "class RM_DrinkableTerrainExtension")
    if "public bool nativeWater;" not in ext:
        f.append("RM_DrinkableTerrainExtension has no nativeWater field")
    native = flat(body(util, "public static bool NativeHere("))
    if "!pawn.RaceProps.Humanlike" not in native or "CommonalityOfAnimal(pawn.kindDef) > 0f" not in native:
        f.append("NativeHere no longer means a non-humanlike on the map biome's roster")
    home = flat(body(util, "public static bool HomeWater("))
    if "ext.nativeWater" not in home or "NativeHere(pawn)" not in home:
        f.append("HomeWater does not require both the nativeWater mark and NativeHere")
    at = flat(body(util, "public static LiquidDef DrinkLiquidAt(TerrainDef terrain, Pawn pawn)"))
    if "!HomeWater(pawn, terrain)" not in at:
        f.append("DrinkLiquidAt(terrain, pawn) widens past HomeWater")
    find = flat(body(util, "public static bool TryFindDrinkCell(Pawn pawn, float level, out IntVec3 cell, out LiquidDef liquid, out RM_DrinkUse use"))
    if "bool home = !only.HasValue && HomeWater(pawn, t);" not in find:
        f.append("TryFindDrinkCell does not compute home water (or widens the salt break's search)")
    if "!(home || MayDrink(pawn, l, level, only))" not in find:
        f.append("TryFindDrinkCell does not let home water past MayDrink")
    if "RM_DrinkUse u = home && UseOf(l) == RM_DrinkUse.Never ? RM_DrinkUse.LastResort : UseOf(l);" not in find:
        f.append("TryFindDrinkCell lets home water of use class Never rank as Never (or above potable water)")
    if "home ? DrinkLiquidAt(t, pawn) : DrinkLiquidAt(t)" not in find:
        f.append("TryFindDrinkCell does not read the native's liquid at home water")
    drv = flat(body(jobs, "class JobDriver_RM_DrinkFromTerrain"))
    if drv.count("DrinkLiquidAt(Map.terrainGrid.TerrainAt(job.targetA.Cell), pawn)") != 1:
        f.append("the drink job's FailOn drops a native at home water (no pawn passed)")
    if drv.count("DrinkLiquidAt(Map.terrainGrid.TerrainAt(c), pawn)") != 1:
        f.append("the drink job's finish toil drinks nothing at home water (no pawn passed)")
    drink = flat(body(util, "public static void Drink("))
    if "if (!pawn.RaceProps.Humanlike && UseOf(liquid) != RM_DrinkUse.Potable) { return; }" not in drink:
        f.append("Drink no longer spares an animal the effects of non-potable water")
    return f


def check_source() -> list[str]:
    util, jobs, liq = (mask_comments(p.read_text(encoding="utf-8")) for p in (UTIL, JOBS, LIQ))
    faults = source_faults(util, jobs, liq)
    mutants = {
        "no field": (util, jobs, liq.replace("public bool nativeWater;", "")),
        "mark not required": (util.replace("&& ext.nativeWater ", ""), jobs, liq),
        "not native": (util.replace("&& ext.liquid != null && NativeHere(pawn)", "&& ext.liquid != null"), jobs, liq),
        "MayDrink kept": (util.replace("!(home || MayDrink(pawn, l, level, only))", "!MayDrink(pawn, l, level, only)"), jobs, liq),
        "salt break widened": (util.replace("bool home = !only.HasValue && HomeWater", "bool home = HomeWater"), jobs, liq),
        "rank lost": (util.replace("RM_DrinkUse u = home && UseOf(l) == RM_DrinkUse.Never ? RM_DrinkUse.LastResort : UseOf(l);", "RM_DrinkUse u = UseOf(l);"), jobs, liq),
        "driver FailOn": (util, jobs.replace("TerrainAt(job.targetA.Cell), pawn)", "TerrainAt(job.targetA.Cell))"), liq),
        "driver finish": (util, jobs.replace("TerrainAt(c), pawn)", "TerrainAt(c))"), liq),
    }
    for name, m in mutants.items():
        if m == (util, jobs, liq):
            faults.append(f"mutant '{name}' did not apply (the check reads text that is gone)")
        elif not source_faults(*m):
            faults.append(f"mutant '{name}' stayed green: the check cannot fail")
    return faults


# ---- BEHAVIOUR: the production method TEXT, compiled by the real C# compiler against small Verse stubs, then run ----
# Not a mirror: every method below is cut from the .cs at run time, so a change to production changes what runs here. The
# stubs supply only Verse's data shapes. Fixture and cases are one template, compiled once per variant (production, then
# each behaviour mutant) into its own namespace, so all of it costs one dotnet build.
STUBS = r"""
using System; using System.Collections.Generic; using System.Linq;
using RimMandrake.FlowWorks.Thirst;

public class DefModExtension {}
public class Def { public string defName; public List<DefModExtension> modExtensions = new List<DefModExtension>();
    public T GetModExtension<T>() where T : class { return modExtensions.OfType<T>().FirstOrDefault(); } }
public class ThingDef : Def {}
public class PawnKindDef : Def {}
public class TerrainDef : Def { public bool IsRiver, IsWater, IsOcean; }
public class BiomeDef : Def { public HashSet<PawnKindDef> roster = new HashSet<PawnKindDef>();
    public float CommonalityOfAnimal(PawnKindDef k) { return roster.Contains(k) ? 1f : 0f; } }
public class Thing {}
public class Game {}
public static class Current { public static Game Game = new Game(); }
public class TickManager { public int TicksGame = 1000; }
public static class Find { public static TickManager TickManager = new TickManager(); }
public class RaceProperties { public bool Humanlike; }
public class Need_RM_Thirst { public float CurLevel = 0.1f; }
public class RotationTracker { public void FaceCell(IntVec3 c) {} }
public class Pawn : Thing { public static int next = 1; public Map Map; public PawnKindDef kindDef; public RaceProperties RaceProps = new RaceProperties();
    public IntVec3 Position; public bool Dead; public int thingIDNumber = next++; public Need_RM_Thirst need = new Need_RM_Thirst();
    public int consequences; public RotationTracker rotationTracker = new RotationTracker();
    public bool CanReach(IntVec3 c, PathEndMode m, Danger d) { return true; } }
public struct IntVec3 { public int x; public IntVec3(int x) { this.x = x; } public static readonly IntVec3 Invalid = new IntVec3(-999);
    public bool InBounds(Map m) { return x >= 0 && x < m.cells.Length; } public bool IsForbidden(Pawn p) { return false; } }
public enum PathEndMode { Touch } public enum Danger { Some } public enum TargetIndex { A } public enum ToilCompleteMode { Instant }
public class TerrainGrid { public Map map; public TerrainDef TerrainAt(IntVec3 c) { return map.cells[c.x]; } }
public class RM_MapComponent_Excavation { public object Stock; }
public class Map { public BiomeDef Biome; public TerrainDef[] cells; public TerrainGrid terrainGrid;
    public Map(BiomeDef b, params TerrainDef[] cells) { Biome = b; this.cells = cells; terrainGrid = new TerrainGrid { map = this }; }
    public T GetComponent<T>() where T : class { return null; } }
public static class GenRadial { public static IEnumerable<IntVec3> RadialCellsAround(IntVec3 p, float r, bool self) { for (int i = 0; i < 60; i++) yield return new IntVec3(i); } }
public static class RM_Volume { public static int Units(float l) { return (int)(l * 10f); } }
public static class RM_ThirstProvider { public static bool OursLive = true; }
public static class RM_ThirstSettings { public static bool waterQualityEffects = true, lastResortDrinking = true; }
public static class RM_LiquidBottleUtility {
    public static Dictionary<TerrainDef, LiquidDef> registry = new Dictionary<TerrainDef, LiquidDef>(); public static int debits;
    public static LiquidDef LiquidAt(TerrainDef t) { LiquidDef l; return t != null && registry.TryGetValue(t, out l) ? l : null; }
    public static bool CanDebitTerrain(Map m, IntVec3 c, int u) { return true; }
    public static bool TryDebitTerrain(Map m, IntVec3 c, int u) { debits++; return true; } }
public class LocalTargetInfo { public IntVec3 Cell; }
public class Job { public LocalTargetInfo targetA; }
public class Toil { public Action initAction; public ToilCompleteMode defaultCompleteMode;
    public Toil WithProgressBarToilDelay(TargetIndex i) { return this; } public void FailOnCannotTouch(TargetIndex i, PathEndMode m) {} }
public static class ToilMaker { public static Toil MakeToil(string n) { return new Toil(); } }
public static class Toils_Goto { public static Toil GotoCell(TargetIndex i, PathEndMode m) { return new Toil(); } }
public static class Toils_General { public static Toil Wait(int t) { return new Toil(); } }
public abstract class JobDriver { public Pawn pawn; public Job job; public Map Map { get { return pawn.Map; } }
    public List<Func<bool>> fails = new List<Func<bool>>(); public void FailOn(Func<bool> f) { fails.Add(f); }
    public abstract bool TryMakePreToilReservations(bool e); protected abstract IEnumerable<Toil> MakeNewToils(); }
//LIQUIDTEXT//
public static class RimMandrakeFlowWorks_DefOf { public static LiquidDef RM_Liquid_FreshWater = new LiquidDef { defName = "fresh", thirstQuality = LiquidThirstQuality.Potable }; }
public static class Fix {
    public static LiquidDef Boil = new LiquidDef { defName = "boil" }, Other = new LiquidDef { defName = "other" }, Fresh = RimMandrakeFlowWorks_DefOf.RM_Liquid_FreshWater,
        Brine = new LiquidDef { defName = "brine", thirstQuality = LiquidThirstQuality.Fouled };
    public static PawnKindDef Noohm = new PawnKindDef { defName = "noohm" }, Stranger = new PawnKindDef { defName = "stranger" }, Colonist = new PawnKindDef { defName = "colonist" };
    public static BiomeDef Scald = new BiomeDef { defName = "scald", roster = new HashSet<PawnKindDef> { Noohm, Colonist } };
    static TerrainDef T(string n, LiquidDef l, bool mark) { var t = new TerrainDef { defName = n, IsWater = true }; t.modExtensions.Add(new RM_DrinkableTerrainExtension { liquid = l, nativeWater = mark }); return t; }
    public static TerrainDef Home = T("home", Boil, true), Unmarked = T("unmarked", Boil, false), BrineT = T("brine", Brine, false), Hollow = T("hollow", null, true),
        Reg = T("registered", Other, true), FreshT = new TerrainDef { defName = "pond", IsWater = true }, Rock = new TerrainDef { defName = "rock" };
    static Fix() { RM_LiquidBottleUtility.registry[Reg] = Boil; }
    public static Pawn P(PawnKindDef k, bool human, params TerrainDef[] cells) {
        var c = cells.Length > 0 ? cells : new[] { Rock };
        return new Pawn { kindDef = k, RaceProps = new RaceProperties { Humanlike = human }, Map = new Map(Scald, c), Position = new IntVec3(0) }; }
    public static Pawn Native(params TerrainDef[] c) { return P(Noohm, false, c); }
    public static Pawn Foreign(params TerrainDef[] c) { return P(Stranger, false, c); }
    public static Pawn Human(params TerrainDef[] c) { return P(Colonist, true, c); }   // a colonist's kind on the roster: Humanlike alone must refuse
}
"""

VARIANT = r"""
namespace //NS// {
public static class RM_ThirstUtility {
    public const float SearchRadius = 60f;
    internal const int NoTerrainMarkTicks = 600;
    private static readonly Dictionary<int, int> noTerrainUntil = new Dictionary<int, int>();
    private static readonly System.WeakReference<Game> marksGame = new System.WeakReference<Game>(null);
    public static Need_RM_Thirst NeedOf(Pawn p) { return p == null ? null : p.need; }
    public static void QualityEffects(Pawn p, RM_WaterQuality q, Thing s) { p.consequences++; }
    public static void RowEffects(Pawn p, LiquidDef l, Thing s) { p.consequences++; }
    public static void RoughDrink(Pawn p, RM_DrinkSource k) { p.consequences++; }
    //METHODS//
}
//JOBDRIVER//
class Driver : JobDriver_RM_DrinkFromTerrain { public List<Toil> Toils() { return MakeNewToils().ToList(); } }
public static class Cases {
    static bool Find(Pawn p, out IntVec3 c, out LiquidDef l, out RM_DrinkUse u, RM_DrinkUse? only = null) { RM_WaterQuality q; return RM_ThirstUtility.TryFindDrinkCell(p, 0.1f, out c, out l, out u, out q, only); }
    static bool Finds(Pawn p, RM_DrinkUse? only = null) { IntVec3 c; LiquidDef l; RM_DrinkUse u; return Find(p, out c, out l, out u, only); }
    static Driver D(Pawn p) { return new Driver { pawn = p, job = new Job { targetA = new LocalTargetInfo { Cell = new IntVec3(0) } } }; }
    static bool JobDrinks(Pawn p, out bool failed, out int debits) {
        var d = D(p); var toils = d.Toils(); failed = d.fails.Any(f => f()); int before = RM_LiquidBottleUtility.debits; float was = p.need.CurLevel;
        toils.Last().initAction(); debits = RM_LiquidBottleUtility.debits - before; return p.need.CurLevel > was; }
    static void C(string v, string n, Func<bool> f) { bool ok; try { ok = f(); } catch (Exception e) { ok = false; Console.WriteLine("EXC " + n + " " + e.GetType().Name); } Console.WriteLine(v + " " + n + " " + (ok ? "ok" : "BAD")); }
    public static void Run(string v) {
        // the first instance, by name: a native at its boil gets the boil back, nobody else does
        C(v, "liquid_native_at_home_water", () => RM_ThirstUtility.DrinkLiquidAt(Fix.Home, Fix.Native()) == Fix.Boil);
        C(v, "liquid_human_at_home_water_null", () => RM_ThirstUtility.DrinkLiquidAt(Fix.Home, Fix.Human()) == null);
        C(v, "liquid_foreign_at_home_water_null", () => RM_ThirstUtility.DrinkLiquidAt(Fix.Home, Fix.Foreign()) == null);
        C(v, "liquid_native_at_unmarked_null", () => RM_ThirstUtility.DrinkLiquidAt(Fix.Unmarked, Fix.Native()) == null);
        C(v, "liquid_no_pawn_is_no_drink", () => RM_ThirstUtility.DrinkLiquidAt(Fix.Home) == null);
        C(v, "liquid_null_pawn_null", () => RM_ThirstUtility.DrinkLiquidAt(Fix.Home, null) == null);
        C(v, "liquid_pawn_off_map_null", () => { var p = Fix.Native(); p.Map = null; return RM_ThirstUtility.DrinkLiquidAt(Fix.Home, p) == null; });
        C(v, "liquid_registry_row_first", () => RM_ThirstUtility.DrinkLiquidAt(Fix.Reg, Fix.Native()) == Fix.Boil);
        C(v, "liquid_potable_unchanged_for_all", () => RM_ThirstUtility.DrinkLiquidAt(Fix.FreshT, Fix.Foreign()) == Fix.Fresh && RM_ThirstUtility.DrinkLiquidAt(Fix.FreshT, Fix.Native()) == Fix.Fresh);
        C(v, "liquid_rock_null", () => RM_ThirstUtility.DrinkLiquidAt(Fix.Rock, Fix.Native()) == null);
        C(v, "home_true_native_marked", () => RM_ThirstUtility.HomeWater(Fix.Native(), Fix.Home));
        C(v, "home_false_human", () => !RM_ThirstUtility.HomeWater(Fix.Human(), Fix.Home));
        C(v, "home_false_foreign", () => !RM_ThirstUtility.HomeWater(Fix.Foreign(), Fix.Home));
        C(v, "home_false_unmarked", () => !RM_ThirstUtility.HomeWater(Fix.Native(), Fix.Unmarked));
        C(v, "home_false_mark_no_liquid", () => !RM_ThirstUtility.HomeWater(Fix.Native(), Fix.Hollow));
        C(v, "home_false_null_terrain", () => !RM_ThirstUtility.HomeWater(Fix.Native(), null));
        C(v, "native_here_roster_animal", () => RM_ThirstUtility.NativeHere(Fix.Native()));
        C(v, "native_here_not_stranger_or_human", () => !RM_ThirstUtility.NativeHere(Fix.Foreign()) && !RM_ThirstUtility.NativeHere(Fix.Human()));
        // find: the search walks to it, ranks it below potable, and finds it for nobody else
        C(v, "find_native_finds_boil", () => { IntVec3 c; LiquidDef l; RM_DrinkUse u; return Find(Fix.Native(Fix.Rock, Fix.Rock, Fix.Home), out c, out l, out u) && c.x == 2 && l == Fix.Boil && u == RM_DrinkUse.LastResort; });
        C(v, "find_human_finds_nothing", () => !Finds(Fix.Human(Fix.Rock, Fix.Home)));
        C(v, "find_foreign_finds_nothing", () => !Finds(Fix.Foreign(Fix.Rock, Fix.Home)));
        C(v, "find_native_unmarked_nothing", () => !Finds(Fix.Native(Fix.Rock, Fix.Unmarked)));
        C(v, "find_potable_beats_nearer_boil", () => { IntVec3 c; LiquidDef l; RM_DrinkUse u; return Find(Fix.Native(Fix.Home, Fix.Rock, Fix.FreshT), out c, out l, out u) && c.x == 2 && l == Fix.Fresh && u == RM_DrinkUse.Potable; });
        C(v, "find_salt_break_not_widened", () => !Finds(Fix.Native(Fix.Rock, Fix.Home), RM_DrinkUse.BreakOnly));
        C(v, "find_salt_break_still_finds_brine", () => Finds(Fix.Foreign(Fix.Rock, Fix.BrineT), RM_DrinkUse.BreakOnly));
        C(v, "find_native_brine_q12", () => Finds(Fix.Native(Fix.Rock, Fix.BrineT)) && !Finds(Fix.Foreign(Fix.Rock, Fix.BrineT)));
        // keep and drink: the job's own FailOn and finish toil, then the production Drink
        C(v, "job_native_keeps_and_drinks", () => { bool f; int d; bool rose = JobDrinks(Fix.Native(Fix.Home), out f, out d); return rose && !f && d == 1; });
        C(v, "job_native_no_human_consequences", () => { var p = Fix.Native(Fix.Home); bool f; int d; JobDrinks(p, out f, out d); return p.consequences == 0; });
        C(v, "job_human_fails_and_drinks_nothing", () => { bool f; int d; bool rose = JobDrinks(Fix.Human(Fix.Home), out f, out d); return !rose && f && d == 0; });
        C(v, "job_foreign_fails_and_drinks_nothing", () => { bool f; int d; bool rose = JobDrinks(Fix.Foreign(Fix.Home), out f, out d); return !rose && f && d == 0; });
        C(v, "drink_human_potable_has_effects", () => { var p = Fix.Human(); float was = p.need.CurLevel; RM_ThirstUtility.Drink(p, Fix.Fresh, 1.5f, null, RM_DrinkSource.Terrain); return p.consequences > 0 && p.need.CurLevel > was; });
    }
}
}
"""

CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings><LangVersion>latest</LangVersion><WarningLevel>0</WarningLevel>
<TreatWarningsAsErrors>false</TreatWarningsAsErrors><AssemblyName>NativesWater</AssemblyName></PropertyGroup></Project>
"""

METHOD_SIGS = [
    "public static RM_WaterQuality? QualityOf(", "public static RM_DrinkUse UseOf(", "public static bool NativeHere(",
    "public static bool MayDrink(Pawn pawn, LiquidDef liquid, float level, RM_DrinkUse? only = null)",
    "public static RM_WaterQuality Effective(LiquidDef liquid)", "public static LiquidDef DrinkLiquidAt(TerrainDef terrain)",
    "public static bool HomeWater(", "public static LiquidDef DrinkLiquidAt(TerrainDef terrain, Pawn pawn)",
    "public static void Drink(",
    "public static bool TryFindDrinkCell(Pawn pawn, float level, out IntVec3 cell, out LiquidDef liquid, out RM_DrinkUse use",
]

# (name, old, new): one edit of the production text. Every one must apply, and must turn at least one case BAD.
BEHAVIOUR_MUTANTS = [
    # the checker's two (blind check at 6271cc55), verbatim
    ("final_return_null", "return RM_LiquidBottleUtility.LiquidAt(terrain) ?? terrain.GetModExtension<RM_DrinkableTerrainExtension>().liquid;", "return null;"),
    ("homewater_false", "return terrain != null && terrain.GetModExtension<RM_DrinkableTerrainExtension>() is", "return false && terrain != null && terrain.GetModExtension<RM_DrinkableTerrainExtension>() is"),
    # the same class, one each
    ("homewater_true_everywhere", "&& ext.nativeWater && ext.liquid != null && NativeHere(pawn);", "&& ext.liquid != null;"),
    ("homewater_no_mark", "&& ext.nativeWater ", ""),
    ("homewater_no_liquid_guard", "&& ext.liquid != null && NativeHere(pawn)", "&& NativeHere(pawn)"),
    ("homewater_not_native", "&& NativeHere(pawn);", ";"),
    ("nativehere_humans_too", "!pawn.RaceProps.Humanlike && biome.CommonalityOfAnimal", "biome.CommonalityOfAnimal"),
    ("nativehere_no_roster", "biome.CommonalityOfAnimal(pawn.kindDef) > 0f", "biome.CommonalityOfAnimal(pawn.kindDef) >= 0f"),
    ("liquidat_condition_flipped", "if (l != null || !HomeWater(pawn, terrain))", "if (l == null || !HomeWater(pawn, terrain))"),
    ("liquidat_ignores_home", "if (l != null || !HomeWater(pawn, terrain))", "if (true)"),
    ("liquidat_registry_skipped", "return RM_LiquidBottleUtility.LiquidAt(terrain) ?? terrain.GetModExtension<RM_DrinkableTerrainExtension>().liquid;", "return terrain.GetModExtension<RM_DrinkableTerrainExtension>().liquid;"),
    ("nopawn_widened", "return row.thirstQuality.HasValue ? row : null;", "return row;"),
    ("find_home_off", "bool home = !only.HasValue && HomeWater(pawn, t);", "bool home = false;"),
    ("find_home_on", "bool home = !only.HasValue && HomeWater(pawn, t);", "bool home = !only.HasValue;"),
    ("find_salt_widened", "bool home = !only.HasValue && HomeWater(pawn, t);", "bool home = HomeWater(pawn, t);"),
    ("find_liquid_plain", "LiquidDef l = home ? DrinkLiquidAt(t, pawn) : DrinkLiquidAt(t);", "LiquidDef l = DrinkLiquidAt(t);"),
    ("find_maydrink_kept", "!(home || MayDrink(pawn, l, level, only))", "!MayDrink(pawn, l, level, only)"),
    ("find_rank_lost", "RM_DrinkUse u = home && UseOf(l) == RM_DrinkUse.Never ? RM_DrinkUse.LastResort : UseOf(l);", "RM_DrinkUse u = UseOf(l);"),
    ("job_failon_inverted", "TerrainAt(job.targetA.Cell), pawn) == null", "TerrainAt(job.targetA.Cell), pawn) != null"),
    ("job_failon_no_pawn", "TerrainAt(job.targetA.Cell), pawn)", "TerrainAt(job.targetA.Cell))"),
    ("job_finish_no_pawn", "TerrainAt(c), pawn)", "TerrainAt(c))"),
    ("job_finish_never_drinks", "if (liquid == null || !RM_LiquidBottleUtility.TryDebitTerrain", "if (true || !RM_LiquidBottleUtility.TryDebitTerrain"),
    ("drink_no_hydration", "need.CurLevel += hydrate;", "need.CurLevel += 0f;"),
    ("drink_native_gets_effects", "if (!pawn.RaceProps.Humanlike && UseOf(liquid) != RM_DrinkUse.Potable)", "if (false)"),
    ("drink_human_spared", "if (!pawn.RaceProps.Humanlike && UseOf(liquid) != RM_DrinkUse.Potable)", "if (UseOf(liquid) == RM_DrinkUse.Potable)"),
]


def production_text():
    """-> (methods, driver, liquid stubs) cut from the masked production source; a missing piece is a fault, not a pass."""
    util, jobs, liq = (mask_comments(p.read_text(encoding="utf-8")) for p in (UTIL, JOBS, LIQ))
    pieces = []
    for sig in METHOD_SIGS:
        b = body(util, sig)
        if not b:
            raise LookupError("production method gone: " + sig)
        at = util.find(sig)
        pieces.append(util[at:util.find("{", at)] + b)
    drv = body(jobs, "public class JobDriver_RM_DrinkFromTerrain")
    use = body(liq, "public LiquidUseClass UseClass")
    ext = body(liq, "public class RM_DrinkableTerrainExtension")
    enums = [(n, body(liq, "public enum " + n)) for n in ("LiquidThirstQuality", "LiquidUseClass")]
    if not (drv and use and ext and all(e for _, e in enums)):
        raise LookupError("production driver, UseClass, extension or enum gone")
    lq = ("public class LiquidDef : Def { public LiquidThirstQuality? thirstQuality; public LiquidUseClass? useClass;\n"
          "public LiquidUseClass UseClass " + use + " }\n"
          "public class RM_DrinkableTerrainExtension : DefModExtension " + ext + "\n"
          + "\n".join("public enum %s %s" % e for e in enums))
    return "\n\n".join(pieces), "public class JobDriver_RM_DrinkFromTerrain : JobDriver " + drv, lq


def behaviour_source():
    """-> (Program.cs text, variant names, faults). Variant v0 is production; a mutant that does not apply is a fault."""
    methods, driver, lq = production_text()
    faults, variants = [], [("v0_production", methods, driver)]
    for name, old, new in BEHAVIOUR_MUTANTS:
        if old not in methods and old not in driver:
            faults.append(f"behaviour mutant '{name}' did not apply (the text it edits is gone)")
            continue
        variants.append(("m_" + name, methods.replace(old, new), driver.replace(old, new)))
    parts = [STUBS.replace("//LIQUIDTEXT//", lq)]
    for ns, m, d in variants:
        parts.append(VARIANT.replace("//NS//", ns).replace("//METHODS//", m).replace("//JOBDRIVER//", d))
    run = "".join(f'        {ns}.Cases.Run("{ns}");\n' for ns, _, _ in variants)
    parts.append("public static class Program { public static int Main() {\n" + run + '        Console.WriteLine("END");\n        return 0; } }\n')
    return "\n".join(parts), [v[0] for v in variants], faults


def read_case_lines(text, variants):
    """-> faults from the program's stdout: production clean, every mutant red, every variant answering the same cases."""
    faults, rows = [], {v: {} for v in variants}
    lines = [ln.strip() for ln in text.replace("\r", "").split("\n") if ln.strip()]
    if not lines or lines[-1] != "END":
        faults.append("behaviour run did not reach END: its output is not a verdict")
    for ln in lines:
        w = ln.split()
        if len(w) == 3 and w[0] in rows and w[2] in ("ok", "BAD"):
            rows[w[0]][w[1]] = w[2]
    prod = rows.get("v0_production", {})
    if len(prod) < 25:
        faults.append(f"instrument blind: only {len(prod)} behaviour cases answered on production")
    faults += [f"production fails behaviour case {c}" for c, r in sorted(prod.items()) if r != "ok"]
    for v in variants[1:]:
        if set(rows[v]) != set(prod):
            faults.append(f"mutant {v} answered {len(rows[v])} cases, production {len(prod)}")
        elif "BAD" not in rows[v].values():
            faults.append(f"mutant {v} stayed green: the behaviour cases cannot see it")
    return faults, rows


def check_behaviour():
    """Compile and run. dotnet missing or a build failure raises SystemExit non-zero: never a pass."""
    import hashlib
    utils = HERE.parent / "Utils"
    sys.path.insert(0, str(utils))
    import winbuild
    from selftest_flowworks_stock import _find_dotnet, _to_windows_path
    dotnet = _find_dotnet()
    if dotnet is None:
        print("UNMEASURED: dotnet.exe not found; the behaviour half cannot run")
        raise SystemExit(2)
    program, variants, faults = behaviour_source()
    stage = Path(winbuild.BUILD_ROOT) / ("selftest_natives_water_" + hashlib.sha1(str(HERE).encode()).hexdigest()[:8])
    stage.mkdir(parents=True, exist_ok=True)
    (stage / "NativesWater.csproj").write_text(CSPROJ, encoding="utf-8")
    (stage / "Program.cs").write_text(program, encoding="utf-8")
    (stage / "RM_ThirstMath.cs").write_text((THIRST / "RM_ThirstMath.cs").read_text(encoding="utf-8"), encoding="utf-8")
    b = winbuild.run_interop_captured([dotnet, "build", _to_windows_path(str(stage / "NativesWater.csproj")), "-c", "Release", "-nologo", "-v", "q",
                                       "-nodeReuse:false", "-p:UseSharedCompilation=false"], capture_output=True, text=True, timeout=300)
    if b.returncode != 0:
        print((b.stdout or "")[-3000:], (b.stderr or "")[-1000:])
        return faults + ["behaviour harness did not compile against the production text"], 0, 0
    r = winbuild.run_interop_captured([dotnet, _to_windows_path(str(stage / "bin" / "Release" / "net8.0" / "NativesWater.dll"))],
                                      capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print((r.stdout or "")[-2000:], (r.stderr or "")[-2000:])
        return faults + [f"behaviour harness exited {r.returncode}"], 0, 0
    more, rows = read_case_lines(r.stdout, variants)
    return faults + more, len(rows["v0_production"]), len(variants) - 1


def load_world():
    terrains, _ = W.load()
    water = {n for n, d in terrains.items() if W.is_water(d, terrains)}
    rows, t2l, marks = {}, {}, set()
    for f in W._globs("Defs"):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for d in root:
            if d.tag.endswith("LiquidDef") and d.findtext("defName"):
                n = d.findtext("defName").strip()
                rows[n] = d
                for k in ("shallow", "deep", "chestDeep"):
                    v = (d.findtext(f"terrainSuite/{k}") or "").strip()
                    if v:
                        t2l[v] = n
    ext = {}
    for f in W._globs("Patches"):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for op in root.iter("match"):
            m = re.search(r'TerrainDef\[defName="([^"]+)"\]', op.findtext("xpath") or "")
            for li in op.iter("li"):
                if m and li.get("Class", "").endswith("RM_DrinkableTerrainExtension"):
                    ext[m.group(1)] = (li.findtext("liquid") or "").strip()
                    if (li.findtext("nativeWater") or "").strip().lower() == "true":
                        marks.add(m.group(1))
    for n, d in terrains.items():
        for li in d.findall("modExtensions/li"):
            if li.get("Class", "").endswith("RM_DrinkableTerrainExtension"):
                ext[n] = (li.findtext("liquid") or "").strip()
                if (li.findtext("nativeWater") or "").strip().lower() == "true":
                    marks.add(n)
    biomes = {}
    for f in sorted(W._globs("Defs")):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for d in root:
            b = (d.findtext("defName") or "").strip()
            if d.tag != "BiomeDef" or not re.match(r"^(RM|RSW|RUT)_", b):
                continue
            wa = d.find("wildAnimals")
            biomes[b] = (f, d, 0 if wa is None else len(list(wa)))
    return terrains, water, rows, t2l, ext, marks, biomes


def liquid_of(t, rows, t2l, ext, water):
    """RM_ThirstUtility.DrinkLiquidAt's order: the registry row (suite), then the terrain adapter, then fresh water only
    for an unadopted water terrain that is not an ocean (vanilla oceans read salt through the registry suite); else
    nothing (None)."""
    lq = t2l.get(t) or ext.get(t)
    if lq:
        return lq
    is_water = t in water or re.match(r"^(Water|Lake|River|Marsh)", t)
    return "RM_Liquid_FreshWater" if is_water and "Ocean" not in t else None


def use_of(row):
    if row is None:
        return "Never"
    u = (row.findtext("useClass") or "").strip()
    if u:
        return u
    q = (row.findtext("thirstQuality") or "").strip()
    return {"": "Never", "Potable": "Potable", "Distilled": "Potable", "Fouled": "BreakOnly"}.get(q, "LastResort")


def audit(marks_override=None):
    terrains, water, rows, t2l, ext, marks, biomes = load_world()
    if marks_override is not None:
        marks = marks_override
    lines, blocked = [], []
    for b, (f, d, roster) in sorted(biomes.items()):
        stem = re.sub(r"^(RM|RSW|RUT)_(The)?", "", b)
        cands = {t.text.strip() for t in d.iter() if t.tag.lower().endswith(("terrain", "terraindef", "terrainshallow", "terraindeep")) and t.text}   # deepTerrain, waterShallowTerrain ...: every field a biome paints water with
        cands |= {n for n in water if len(stem) >= 4 and stem in n}
        for t in sorted(cands):
            if t not in water and not re.match(r"^(Water|Lake|River|Ocean|Marsh)", t):
                continue
            liq = liquid_of(t, rows, t2l, ext, water)
            row = rows.get(liq)
            use = use_of(row)
            drink = row is not None and bool((row.findtext("thirstQuality") or "").strip())  # C#: no quality, no drink
            if t in NOT_WATER:
                v = "not water: " + NOT_WATER[t]
            elif not drink and t in marks:
                v = "drinks (home water, nativeWater)"
            elif not drink:
                v = "BLOCKED"
            elif use == "Potable":
                v = "drinks (potable for everyone)"
            elif use != "Never":
                v = f"drinks (Q12 native rule, {use})"
            elif t in marks:
                v = "drinks (home water, nativeWater)"
            else:
                v = "BLOCKED"
            if v == "BLOCKED":
                if roster:
                    blocked.append(f"{b}: {t} -> {liq}")
                else:
                    v = "BLOCKED (no roster in def; a patch-added cast would hit it)"
                    blocked.append(f"{b}: {t} -> {liq} (patch roster)")
            lines.append(f"| {b} | {roster} | {t} | {liq} | {use} | {v} |")
    return lines, blocked, biomes


def main() -> int:
    faults = check_source()
    more, ncases, nmutants = check_behaviour()
    faults += more
    lines, blocked, biomes = audit()
    # sanity probes: the instrument must see the known Baroque water
    if len(biomes) < 40:
        faults.append(f"instrument blind: only {len(biomes)} of our BiomeDefs seen")
    scald = [l for l in lines if l.startswith("| RM_TheScald |") and "RM_Liquid_BoilingWater" in l]
    if len(scald) < 6:
        faults.append(f"instrument blind: {len(scald)} Scald boil terrains seen, want 6")
    roster = {(k.findtext("animal") or k.tag).strip() for k in biomes["RM_TheScald"][1].find("wildAnimals")} if "RM_TheScald" in biomes else set()
    if not {"RM_Noohm", "RM_Shulla"} <= roster:
        faults.append("the Scald's roster no longer holds RM_Noohm and RM_Shulla: the first instance is gone")
    if not any("RM_GreySea" in l and "RM_Liquid_Brine" in l for l in lines):
        faults.append("instrument blind: the Grey Sea's brine not seen")
    _, probe_blocked, _ = audit(marks_override=set())
    if not any(x.startswith("RM_TheScald:") for x in probe_blocked):
        faults.append("probe mutant (no nativeWater marks) left the Scald drinkable: the audit cannot fail")
    faults += ["BLOCKED " + x for x in blocked]
    REPORT.write_text(
        "# Natives drink their own water: every-biome audit\n\n"
        "Generated by `src/RimMandrake/FlowWorks/selftest_natives_drink_own_water.py` "
        "(NATIVES_DRINK_OWN_WATER_AUDIT_EVERY_BIOME). Owner, 2026-11-01: *\"Yes, natives should drink their own "
        "environmental water. That's a ruling for all Baroque Biomes, period, including this one.\"*\n\n"
        "Each row is a Water terrain the biome paints (its BiomeDef's terrains, or a Water terrain named after it). "
        "`roster` counts the def's own `<wildAnimals>`; RUT twins get their cast by patch. Biomes with no water row "
        "rely on map-generated rivers and lakes, which are fresh water for everyone.\n\n"
        "| biome | roster | terrain | liquid | use class | a native |\n|---|---|---|---|---|---|\n"
        + "\n".join(lines) + "\n", encoding="utf-8")
    if faults:
        print(f"FAIL {len(faults)}:")
        for x in faults:
            print("  ", x)
        return 1
    print(f"PASS source + 8 mutants red; behaviour {ncases} cases on the production text + {nmutants} mutants red; {len(biomes)} biomes, {len(lines)} water rows, 0 blocked; report {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
