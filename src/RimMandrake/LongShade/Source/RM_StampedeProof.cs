using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.LongShade
{
    /// <summary>static_call probe for LONGSHADE_STAMPEDE_LIVECHECK_1 (driven by LongShade/prove_stampede.py): the
    /// "stampede for your roof" incident on one RM_LongShade map. Every method works on Find.CurrentMap and returns ONE
    /// line of key=value pairs (no spaces inside a value):
    ///   Def("")             "DEF found=B worker=Type biomes=a,b category=X"
    ///   Toggle("field=bool") sets a public static bool of RM_LongShadeSettings: "TOGGLE field=F was=B now=B"
    ///   Stage("n[,kind=X]") a fresh scene: despawns every wild animal (so no herd but ours is on the map), clears the home
    ///                       area, puts home + a built roof (RoofConstructed) on an open 5x5 rect, and spawns n wild
    ///                       animals of one herdAnimal, non-flying kind from map.Biome.AllWildAnimals 30-40 cells away (far enough
    ///                       that a sprinting runner is still on its way a few hundred ticks after the fire).
    ///                       "STAGED kind=X spawned=N failed=N herd=N wildCleared=N roof=x,z roofCells=N biome=X"
    ///   Add("n")            spawns n more of the staged kind at the herd centre: "ADDED spawned=N failed=N herd=N"
    ///   Heat("hot"|"cool")  one Royalty ClimateAdjustment condition (GameCondition_TemperatureOffset) on the map, its
    ///                       tempOffset set so the outdoor temperature becomes safeMax+8 (hot) or the middle of the kind's
    ///                       safe range (cool). The outdoor cache refreshes every 300 ticks: run >= 300 before reading.
    ///                       "HEAT mode=M offset=F target=F safeMax=F"
    ///   Roof("off"|"on")    takes the staged rect out of / back into the home area: "ROOF home=B homeRoofed=N"
    ///   Can("")             the worker's own gate, IncidentWorker_RM_ShadeStampede.CanFireNowSub, called by reflection
    ///                       (IncidentWorker.CanFireNow caches one answer per tick, so two reads in one tick would lie):
    ///                       "CAN sub=B herd=N alive=N hot=N homeRoofed=N running=B best=N bestDef=X outdoor=F amb=F safeMax=F"
    ///   Fire("")            def.Worker.TryExecute on forced parms: "FIRED ok=B letters=N letter=B" + the Runners fields
    ///   Runners("")         the stampede component's own runners (by reflection):
    ///                       "RUNNERS n=N goto=N sprint=N toTarget=N wait=N atTarget=N hot=N alive=N herdHot=N downed=N since=N running=B tick=N
    ///                        target=x,z targetRoofed=B targetHome=B"
    ///   Interrupt("")       every runner is put on a Wait job (InterruptForced): "INTERRUPTED n=N goto=N wait=N tick=N"
    ///   Cleanup("")         ends the heat, despawns what this probe spawned, empties the component's runners.
    /// Nothing here changes the mechanism; it stages the scene and reads it.</summary>
    public static class RM_StampedeProof
    {
        public const string DefName = "RM_ShadeStampede";
        public const string Title = "An overheated herd is bolting for your roof";
        private const string HeatDef = "ClimateAdjustment";
        private static readonly List<Pawn> herd = new List<Pawn>();
        private static readonly List<IntVec3> rect = new List<IntVec3>();
        private static PawnKindDef kind;
        private static IntVec3 herdCentre = IntVec3.Invalid;
        private static GameCondition_TemperatureOffset heat;

        private static string F(float v) => v.ToString("0.##", CultureInfo.InvariantCulture);
        private static string C(IntVec3 c) => c.x + "," + c.z;

        private static IncidentDef Inc => DefDatabase<IncidentDef>.GetNamedSilentFail(DefName);

        // ------------------------------------------------------------------ def + settings
        public static string Def(string _)
        {
            IncidentDef d = Inc;
            if (d == null) return "DEF found=False";
            return "DEF found=True worker=" + (d.workerClass == null ? "null" : d.workerClass.FullName)
                + " biomes=" + string.Join(",", (d.allowedBiomes ?? new List<BiomeDef>()).Select(b => b.defName).ToArray())
                + " category=" + (d.category == null ? "null" : d.category.defName);
        }

        public static string Toggle(string arg)
        {
            string[] kv = (arg ?? "").Split('=');
            if (kv.Length != 2) return "REFUSED: want field=bool";
            FieldInfo f = typeof(RM_LongShadeSettings).GetField(kv[0], BindingFlags.Public | BindingFlags.Static);
            if (f == null || f.FieldType != typeof(bool)) return "REFUSED: no static bool RM_LongShadeSettings." + kv[0];
            bool was = (bool)f.GetValue(null);
            f.SetValue(null, kv[1].Trim().ToLowerInvariant() == "true");
            return "TOGGLE field=" + kv[0] + " was=" + was + " now=" + f.GetValue(null);
        }

        // ------------------------------------------------------------------ staging
        private static bool Flies(PawnKindDef k)
        {
            StatDef flight = DefDatabase<StatDef>.GetNamedSilentFail("MaxFlightTime");
            return flight != null && k.race != null && k.race.GetStatValueAbstract(flight) > 0f;
        }

        private static bool OpenRect(Map map, IntVec3 centre)
        {
            foreach (IntVec3 c in CellRect.CenteredOn(centre, 2))
            {
                if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null || c.Roofed(map) || c.GetFirstPawn(map) != null)
                    return false;
            }
            return centre.x > 12 && centre.z > 12 && centre.x < map.Size.x - 12 && centre.z < map.Size.z - 12;
        }

        private static IntVec3 HerdSpot(Map map, IntVec3 roofCentre)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(roofCentre, 40f, false))
            {
                float d = c.DistanceTo(roofCentre);
                if (d < 30f || !c.InBounds(map) || c.Roofed(map)) continue;
                if (CellRect.CenteredOn(c, 2).Cells.All(x => x.InBounds(map) && x.Standable(map) && !x.Roofed(map)
                    && map.reachability.CanReach(x, roofCentre, PathEndMode.OnCell, TraverseParms.For(TraverseMode.PassDoors))))
                    return c;
            }
            return IntVec3.Invalid;
        }

        private static int SpawnHerd(Map map, int n, out int failed)
        {
            int ok = 0;
            failed = 0;
            for (int i = 0; i < n; i++)
            {
                try
                {
                    IntVec3 at;
                    if (!CellFinder.TryFindRandomCellNear(herdCentre, map, 3, c => c.Standable(map) && !c.Roofed(map) && c.GetFirstPawn(map) == null, out at))
                    {
                        failed++;
                        continue;
                    }
                    Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer, map.Tile));
                    GenSpawn.Spawn(p, at, map);
                    herd.Add(p);
                    ok++;
                }
                catch (Exception)
                {
                    failed++;
                }
            }
            return ok;
        }

        public static string Stage(string arg)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no current map";
            Cleanup("");
            string[] parts = (arg ?? "").Split(',');
            int n;
            if (!int.TryParse(parts[0].Trim(), out n) || n < 1) return "REFUSED: want a count";
            string want = parts.Skip(1).Select(s => s.Trim()).Where(s => s.StartsWith("kind=")).Select(s => s.Substring(5)).FirstOrDefault();
            List<PawnKindDef> roster = map.Biome.AllWildAnimals
                .Where(k => k.RaceProps != null && k.RaceProps.Animal && k.RaceProps.herdAnimal && !Flies(k))
                .OrderBy(k => k.defName).ToList();
            kind = want != null ? roster.FirstOrDefault(k => k.defName == want) : roster.FirstOrDefault();
            string rosterText = string.Join(",", roster.Select(k => k.defName).ToArray());
            if (kind == null) return "STAGED kind=none roster=" + rosterText + " biome=" + map.Biome.defName;

            int cleared = 0;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
            {
                if (p.Faction == null && p.RaceProps.Animal) { p.DeSpawn(); cleared++; }
            }
            map.areaManager.Home.Clear();
            IntVec3 centre = map.AllCells.Where(c => OpenRect(map, c)).OrderBy(c => c.DistanceTo(map.Center)).FirstOrDefault();
            if (!centre.IsValid || !OpenRect(map, centre)) return "REFUSED: no open 5x5 rect for the roof";
            herdCentre = HerdSpot(map, centre);
            if (!herdCentre.IsValid) return "REFUSED: no open reachable herd spot 30-40 cells from the roof";
            foreach (IntVec3 c in CellRect.CenteredOn(centre, 2))
            {
                map.areaManager.Home[c] = true;
                map.roofGrid.SetRoof(c, RoofDefOf.RoofConstructed);
                rect.Add(c);
            }
            int failed;
            int spawned = SpawnHerd(map, n, out failed);
            return "STAGED kind=" + kind.defName + " spawned=" + spawned + " failed=" + failed + " herd=" + herd.Count
                + " wildCleared=" + cleared + " roof=" + C(centre) + " roofCells=" + HomeRoofed(map)
                + " herdAt=" + C(herdCentre) + " biome=" + map.Biome.defName + " roster=" + rosterText;
        }

        public static string Add(string arg)
        {
            Map map = Find.CurrentMap;
            int n;
            if (map == null || kind == null || !herdCentre.IsValid) return "REFUSED: Stage first";
            if (!int.TryParse((arg ?? "").Trim(), out n) || n < 1) return "REFUSED: want a count";
            int failed;
            int spawned = SpawnHerd(map, n, out failed);
            return "ADDED spawned=" + spawned + " failed=" + failed + " herd=" + herd.Count;
        }

        private static FloatRange Safe()
        {
            Pawn p = herd.FirstOrDefault(x => x != null && x.Spawned && !x.Dead);
            return p == null ? new FloatRange(0f, 0f) : p.SafeTemperatureRange();
        }

        public static string Heat(string mode)
        {
            Map map = Find.CurrentMap;
            if (map == null || herd.Count == 0) return "REFUSED: Stage first";
            if (mode != "hot" && mode != "cool") return "REFUSED: want hot or cool";
            if (heat == null || !map.gameConditionManager.ActiveConditions.Contains(heat))
            {
                GameConditionDef d = DefDatabase<GameConditionDef>.GetNamedSilentFail(HeatDef);
                if (d == null) return "REFUSED: no GameConditionDef " + HeatDef;
                heat = GameConditionMaker.MakeCondition(d, 60000 * 5) as GameCondition_TemperatureOffset;
                if (heat == null) return "REFUSED: " + HeatDef + " is not a GameCondition_TemperatureOffset";
                map.gameConditionManager.RegisterCondition(heat);   // Init() resets tempOffset from the def: set it after
            }
            FloatRange safe = Safe();
            float target = mode == "hot" ? safe.max + 8f : (safe.min + safe.max) / 2f;
            // the cached OutdoorTemp may not include this condition yet; rebuild the base from the tile and the OTHER conditions
            float baseTemp = Find.World.tileTemperatures.OutdoorTemperatureAt(map.Tile, Find.TickManager.TicksAbs);
            foreach (GameCondition gc in map.gameConditionManager.ActiveConditions)
            {
                if (gc != heat && gc.CanApplyOnMap(map)) baseTemp += gc.TemperatureOffset();
            }
            foreach (GameCondition gc in Find.World.GameConditionManager.ActiveConditions)
            {
                if (gc.CanApplyOnMap(map)) baseTemp += gc.TemperatureOffset();
            }
            heat.tempOffset = target - baseTemp;
            return "HEAT mode=" + mode + " offset=" + F(heat.tempOffset) + " target=" + F(target) + " safeMax=" + F(safe.max);
        }

        private static int HomeRoofed(Map map)
        {
            int n = 0;
            foreach (IntVec3 c in map.areaManager.Home.ActiveCells)
            {
                if (c.Roofed(map) && c.Standable(map)) n++;
            }
            return n;
        }

        public static string Roof(string mode)
        {
            Map map = Find.CurrentMap;
            if (map == null || rect.Count == 0) return "REFUSED: Stage first";
            foreach (IntVec3 c in rect) map.areaManager.Home[c] = mode == "on";
            return "ROOF home=" + (mode == "on") + " homeRoofed=" + HomeRoofed(map);
        }

        // ------------------------------------------------------------------ reads
        public static string Can(string _)
        {
            Map map = Find.CurrentMap;
            IncidentDef d = Inc;
            if (map == null || d == null) return "REFUSED: no map or no " + DefName;
            IncidentParms parms = StorytellerUtility.DefaultParmsNow(d.category, map);
            MethodInfo sub = AccessTools.Method(d.Worker.GetType(), "CanFireNowSub");
            MethodInfo find = AccessTools.Method(typeof(IncidentWorker_RM_ShadeStampede), "FindHerd");
            if (sub == null || find == null) return "REFUSED: CanFireNowSub or FindHerd not found";
            bool can = (bool)sub.Invoke(d.Worker, new object[] { parms });
            List<Pawn> best = (List<Pawn>)find.Invoke(null, new object[] { map });
            // the herd as FindHerd sees it: spawned, alive, not downed
            List<Pawn> alive = herd.Where(p => p != null && p.Spawned && !p.Dead && !p.Downed).ToList();
            RM_MapComponent_Stampede st = map.GetComponent<RM_MapComponent_Stampede>();
            return "CAN sub=" + can + " herd=" + herd.Count + " alive=" + alive.Count
                + " hot=" + alive.Count(RM_ShadeExtrasTuning.Overheated) + " homeRoofed=" + HomeRoofed(map)
                + " running=" + (st != null && st.Running) + " best=" + (best == null ? 0 : best.Count)
                + " bestDef=" + (best == null ? "none" : best[0].def.defName)
                + " outdoor=" + F(map.mapTemperature.OutdoorTemp)
                + " amb=" + (alive.Count == 0 ? "nan" : F(alive[0].AmbientTemperature)) + " safeMax=" + F(Safe().max)
                + " stampedeEnabled=" + RM_LongShadeSettings.stampedeEnabled + " modEnabled=" + RM_LongShadeSettings.modEnabled;
        }

        private static List<Pawn> Runs(RM_MapComponent_Stampede st)
        {
            return st == null ? new List<Pawn>() : (List<Pawn>)AccessTools.Field(typeof(RM_MapComponent_Stampede), "runners").GetValue(st);
        }

        public static string Runners(string _)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_Stampede st = map == null ? null : map.GetComponent<RM_MapComponent_Stampede>();
            if (st == null) return "REFUSED: no RM_MapComponent_Stampede on the current map";
            List<Pawn> rs = Runs(st);
            IntVec3 target = (IntVec3)AccessTools.Field(typeof(RM_MapComponent_Stampede), "target").GetValue(st);
            int start = (int)AccessTools.Field(typeof(RM_MapComponent_Stampede), "startTick").GetValue(st);
            int now = Find.TickManager.TicksGame;
            int gotoN = 0, sprint = 0, toTarget = 0, wait = 0, hot = 0, alive = 0, atTarget = 0, downed = 0;
            foreach (Pawn p in rs)
            {
                if (p == null || !p.Spawned || p.Dead) continue;
                if (p.Downed) { downed++; continue; }   // kept as a runner, never given a job (Issue skips the downed)
                alive++;
                if (RM_ShadeExtrasTuning.Overheated(p)) hot++;
                if (target.IsValid && p.Position.InHorDistOf(target, 2.5f)) atTarget++;
                Job j = p.CurJob;
                if (j == null) continue;
                if (j.def == JobDefOf.Goto)
                {
                    gotoN++;
                    if (j.locomotionUrgency == LocomotionUrgency.Sprint) sprint++;
                    if (j.targetA.Cell == target) toTarget++;
                }
                if (j.def == JobDefOf.Wait) wait++;
            }
            int herdHot = herd.Count(p => p != null && p.Spawned && !p.Dead && RM_ShadeExtrasTuning.Overheated(p));
            return "RUNNERS n=" + rs.Count + " goto=" + gotoN + " sprint=" + sprint + " toTarget=" + toTarget + " wait=" + wait
                + " atTarget=" + atTarget + " hot=" + hot + " alive=" + alive + " herdHot=" + herdHot + " downed=" + downed + " since=" + (start < 0 ? -1 : now - start)
                + " running=" + st.Running + " tick=" + now + " target=" + (target.IsValid ? C(target) : "none")
                + " targetRoofed=" + (target.IsValid && target.InBounds(map) && target.Roofed(map))
                + " targetHome=" + (target.IsValid && target.InBounds(map) && map.areaManager.Home[target]);
        }

        public static string Fire(string _)
        {
            Map map = Find.CurrentMap;
            IncidentDef d = Inc;
            if (map == null || d == null) return "REFUSED: no map or no " + DefName;
            IncidentParms parms = StorytellerUtility.DefaultParmsNow(d.category, map);
            parms.forced = true;
            int before = Find.LetterStack.LettersListForReading.Count(l => l.Label.RawText == Title);
            bool ok = d.Worker.TryExecute(parms);
            int after = Find.LetterStack.LettersListForReading.Count(l => l.Label.RawText == Title);
            return "FIRED ok=" + ok + " letters=" + (after - before) + " letter=" + (after > before) + " " + Runners("").Substring(8);
        }

        public static string Interrupt(string _)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_Stampede st = map == null ? null : map.GetComponent<RM_MapComponent_Stampede>();
            if (st == null) return "REFUSED: no RM_MapComponent_Stampede";
            int n = 0, gotoN = 0, wait = 0;
            foreach (Pawn p in Runs(st))
            {
                if (p == null || !p.Spawned || p.Dead || p.Downed) continue;
                Job j = JobMaker.MakeJob(JobDefOf.Wait);
                j.expiryInterval = 3000;
                p.jobs.StartJob(j, JobCondition.InterruptForced, null, false, true);
                n++;
                if (p.CurJob != null && p.CurJob.def == JobDefOf.Goto) gotoN++;
                if (p.CurJob != null && p.CurJob.def == JobDefOf.Wait) wait++;
            }
            return "INTERRUPTED n=" + n + " goto=" + gotoN + " wait=" + wait + " tick=" + Find.TickManager.TicksGame;
        }

        public static string Cleanup(string _)
        {
            int ended = 0, gone = 0;
            if (heat != null && heat.gameConditionManager != null && heat.gameConditionManager.ActiveConditions.Contains(heat))
            {
                heat.End();
                ended++;
            }
            heat = null;
            foreach (Pawn p in herd)
            {
                if (p != null && p.Spawned) { p.DeSpawn(); gone++; }
            }
            herd.Clear();
            Map map = Find.CurrentMap;
            if (map != null)
            {
                foreach (IntVec3 c in rect)
                {
                    if (!c.InBounds(map)) continue;
                    map.areaManager.Home[c] = false;
                    map.roofGrid.SetRoof(c, null);
                }
                RM_MapComponent_Stampede st = map.GetComponent<RM_MapComponent_Stampede>();
                if (st != null) Runs(st).Clear();
            }
            rect.Clear();
            herdCentre = IntVec3.Invalid;
            kind = null;
            return "CLEANED heat=" + ended + " despawned=" + gone;
        }
    }
}
