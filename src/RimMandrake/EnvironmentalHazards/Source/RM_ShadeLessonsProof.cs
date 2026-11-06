using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    /// <summary>static_call probe for SHADE_LESSONS_BUILD_WATCH_THE_HERD_CROSS criterion A7 (driven by
    /// EnvironmentalHazards/prove_shade_lessons.py): on Find.CurrentMap, a colonist studies dewfringe and a herd crossing
    /// is counted. Each method returns ONE line of key=value pairs.
    ///   Toggle("true|false")  sets RM_EnvironmentalHazardsSettings.shadeLessonsEnabled: "TOGGLE was=B now=B"
    ///   Stage("")             resets (Cleanup), then: a studier colonist on an open cell near the map centre, sent to study
    ///                         the nearest RM_Dewfringe (one is spawned grown when none is within 40 cells); a drafted watcher
    ///                         colonist, a landing cell 5 cells from it in line of sight, and a wild Hare 6 cells beyond
    ///                         sent on RM_ShadeDash to that landing cell. Records the colony points of both ideas first.
    ///                         "STAGED plant=x,z spawnedPlant=B wg=B studier=x,z watcher=x,z landing=x,z hare=x,z dew0=F ps0=F"
    ///                         (wg = the vanilla study WorkGiver would take the plant unforced)
    ///   Read("")              "READ dew0=F dew=F ps0=F ps=F lastStudied=N interactions=N hareEvents=N events=N hareAt=B gate=B"
    ///   Cleanup("")           despawns what Stage spawned and drops the probe's event listener.
    /// Nothing here changes the mechanism; it stages the scene and reads it.</summary>
    public static class RM_ShadeLessonsProof
    {
        private static readonly List<Thing> spawned = new List<Thing>();
        private static Pawn hare;
        private static Thing plant;
        private static IntVec3 landing = IntVec3.Invalid;
        private static float dew0, ps0;
        private static int events, hareEvents;
        private static bool listening;

        private static string Xz(IntVec3 c) => c.x + "," + c.z;

        private static ResearchProjectDef Def(string name) => DefDatabase<ResearchProjectDef>.GetNamedSilentFail(name);

        private static float Points(string name)
        {
            RM_FoundTechKnowledge k = RM_FoundTechKnowledge.Get();
            ResearchProjectDef d = Def(name);
            return k == null || d == null ? -1f : k.Points(d);
        }

        public static string Toggle(string arg)
        {
            string v = (arg ?? "").Trim().ToLowerInvariant();
            if (v != "true" && v != "false") return "REFUSED: want true|false";
            bool was = RM_EnvironmentalHazardsSettings.shadeLessonsEnabled;
            // restore-check: ok a setter tool: prove_shade_lessons.py reads `was` from this call and its finally Toggles it back
            RM_EnvironmentalHazardsSettings.shadeLessonsEnabled = v == "true";
            return "TOGGLE was=" + was + " now=" + RM_EnvironmentalHazardsSettings.shadeLessonsEnabled;
        }

        private static void OnCrossing(Pawn p, IntVec3 at)
        {
            events++;
            if (p != null && p == hare && at == landing) hareEvents++;
        }

        private static bool Open(IntVec3 c, Map map)
        {
            return c.InBounds(map) && c.Standable(map) && !c.Roofed(map) && c.GetFirstPawn(map) == null && !c.Fogged(map);
        }

        private static Pawn Colonist(IntVec3 at, Map map, bool drafted)
        {
            Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            GenSpawn.Spawn(p, at, map);
            if (drafted && p.drafter != null) p.drafter.Drafted = true;
            spawned.Add(p);
            return p;
        }

        public static string Stage(string _)
        {
            Cleanup("");
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no current map";
            ResearchProjectDef dew = Def("RM_ShadeIdea_DewOff"), ps = Def("RM_ShadeIdea_PortableShade");
            ThingDef dewfringe = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Dewfringe");
            if (dew == null || ps == null || dewfringe == null) return "REFUSED: shade lesson defs missing";
            if (RM_FoundTechKnowledge.Get() == null) return "REFUSED: no RM_FoundTechKnowledge component";
            IntVec3 centre = map.Center;
            IntVec3 s = CellFinder.RandomClosewalkCellNear(centre, map, 8, c => Open(c, map));
            if (!Open(s, map)) return "REFUSED: no open cell near the centre";

            plant = GenClosest.ClosestThing_Global(s, map.listerThings.ThingsOfDef(dewfringe), 40f);
            bool spawnedPlant = false;
            if (plant == null)
            {
                IntVec3 pc = CellFinder.RandomClosewalkCellNear(s, map, 6, c => Open(c, map) && c.GetPlant(map) == null && c != s);
                Plant fresh = (Plant)ThingMaker.MakeThing(dewfringe);
                fresh.Growth = 1f;
                GenSpawn.Spawn(fresh, pc, map);
                spawned.Add(fresh);
                plant = fresh;
                spawnedPlant = true;
            }

            dew0 = Points("RM_ShadeIdea_DewOff");
            ps0 = Points("RM_ShadeIdea_PortableShade");

            Pawn studier = Colonist(s, map, false);
            bool wg = false;
            foreach (WorkGiverDef w in DefDatabase<WorkGiverDef>.AllDefsListForReading)
            {
                if (w.giverClass == typeof(WorkGiver_StudyInteract) && w.Worker is WorkGiver_Scanner sc)
                {
                    wg |= sc.HasJobOnThing(studier, plant, false);
                }
            }
            studier.jobs.StartJob(JobMaker.MakeJob(JobDefOf.StudyInteract, plant), JobCondition.InterruptForced);

            // the crossing: a watcher, a landing cell in its sight, and a wild hare that dashes there
            IntVec3 w0 = CellFinder.RandomClosewalkCellNear(centre + new IntVec3(18, 0, 0), map, 8, c => Open(c, map));
            IntVec3 l = IntVec3.Invalid, a = IntVec3.Invalid;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(w0, 7f, false))
            {
                if (c.DistanceTo(w0) < 4f || !Open(c, map) || !GenSight.LineOfSight(w0, c, map, skipFirstCell: true)) continue;
                IntVec3 dir = c - w0;
                IntVec3 far = c + new IntVec3(Math.Sign(dir.x) * 6, 0, Math.Sign(dir.z) * 6);
                IntVec3 from = CellFinder.RandomClosewalkCellNear(far, map, 3, x => Open(x, map) && x.DistanceTo(w0) > 8f);
                if (Open(from, map) && map.reachability.CanReach(from, c, PathEndMode.OnCell, TraverseParms.For(TraverseMode.PassDoors)))
                {
                    l = c;
                    a = from;
                    break;
                }
            }
            if (!l.IsValid) return "REFUSED: no landing cell in a watcher's sight";
            Pawn watcher = Colonist(w0, map, true);
            landing = l;
            PawnKindDef hareKind = DefDatabase<PawnKindDef>.GetNamedSilentFail("Hare");
            if (hareKind == null) return "REFUSED: no Hare pawnkind";
            hare = PawnGenerator.GeneratePawn(hareKind, null);
            GenSpawn.Spawn(hare, a, map);
            spawned.Add(hare);
            events = 0;
            hareEvents = 0;
            if (!listening)
            {
                RM_ShadeHop.CrossingLanded += OnCrossing;
                listening = true;
            }
            hare.jobs.StartJob(RM_ShadeHop.MakeDash(a, l, 0), JobCondition.InterruptForced);
            return "STAGED plant=" + Xz(plant.Position) + " spawnedPlant=" + spawnedPlant + " wg=" + wg
                + " studier=" + Xz(studier.Position) + " watcher=" + Xz(watcher.Position) + " landing=" + Xz(l)
                + " hare=" + Xz(a) + " dew0=" + dew0.ToString("0.###") + " ps0=" + ps0.ToString("0.###");
        }

        public static string Read(string _)
        {
            RM_CompFoundTechStudy comp = plant?.TryGetComp<RM_CompFoundTechStudy>();
            int last = comp != null ? comp.lastStudiedTick : -2;
            int inJob = comp != null ? comp.studyInteractions : -1;
            bool hareAt = hare != null && hare.Spawned && hare.Position == landing;
            return "READ dew0=" + dew0.ToString("0.###") + " dew=" + Points("RM_ShadeIdea_DewOff").ToString("0.###")
                + " ps0=" + ps0.ToString("0.###") + " ps=" + Points("RM_ShadeIdea_PortableShade").ToString("0.###")
                + " lastStudied=" + last + " interactions=" + inJob + " hareEvents=" + hareEvents + " events=" + events + " hareAt=" + hareAt
                + " gate=" + RM_MechanicGates.Enabled(RM_ShadeLessons.GateKey);
        }

        public static string Cleanup(string _)
        {
            int n = 0;
            foreach (Thing t in spawned.ToList())
            {
                if (t != null && t.Spawned)
                {
                    t.Destroy(DestroyMode.Vanish);
                    n++;
                }
            }
            spawned.Clear();
            if (listening)
            {
                RM_ShadeHop.CrossingLanded -= OnCrossing;
                listening = false;
            }
            hare = null;
            plant = null;
            landing = IntVec3.Invalid;
            return "CLEANED n=" + n;
        }
    }
}
