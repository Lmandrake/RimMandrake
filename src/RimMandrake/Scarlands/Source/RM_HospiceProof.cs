using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Scarlands
{
    // WARSCAR_HOSPICE_DESERTERS_1 live proof hooks, called through jawa/static_call by Scarlands/hospice_live_proof.py.
    // Each returns one line beginning PASS or FAIL. They build on the CURRENT map (a quicktest map: every save but the
    // canonical world saves is disposable) and never touch the world.
    public static class RM_HospiceProof
    {
        private static IntVec3 FreeSpot(Map map, IntVec2 size)
        {
            IntVec3 c = map.Center;
            for (int r = 0; r < 60; r++)
            {
                foreach (IntVec3 cell in GenRadial.RadialCellsAround(c, r, r + 1))
                {
                    CellRect rect = GenAdj.OccupiedRect(cell, Rot4.North, size).ExpandedBy(2);
                    if (rect.InBounds(map) && rect.Cells.All(x => x.Standable(map) && x.GetEdifice(map) == null && x.GetFirstPawn(map) == null && x.GetFirstItem(map) == null))
                        return cell;
                }
            }
            return IntVec3.Invalid;
        }

        private static Building_HospiceCradle MakeCradle(Map map)
        {
            IntVec3 at = FreeSpot(map, new IntVec2(2, 1));
            if (!at.IsValid) return null;
            Thing c = ThingMaker.MakeThing(RM_HospiceDefOf.RM_HospiceCradle);
            c.SetFaction(Faction.OfPlayer);
            return (Building_HospiceCradle)GenSpawn.Spawn(c, at, map, Rot4.North);
        }

        private static MinifiedThing MakeChassis(Map map, IntVec3 near)
        {
            Thing t = ThingMaker.MakeThing(RM_HospiceDefOf.RM_KneelingChassis_Intact);
            t.TryGetComp<CompDeserterHistory>().Roll();
            MinifiedThing m = MinifyUtility.MakeMinified(t);
            GenPlace.TryPlaceThing(m, near, map, ThingPlaceMode.Near);
            return m;
        }

        // A1: the Warscar biome runs the ring genstep, and that genstep on this map lays rings facing their centre
        // with 0..min(setting,3) intact chassis, each carrying a history that survives a save (its Scribe XML).
        private const int Seeds = 10;

        public static string Rings(Map map)
        {
            BiomeDef warscar = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Warscar");
            if (warscar == null || warscar.extraGenSteps == null || !warscar.extraGenSteps.Any(g => g.defName == "RM_KneelingRings"))
                return "FAIL RM_Warscar does not run RM_KneelingRings live";
            Clear(map);   // start from no ring chassis, so every one counted below is this genstep's
            GenStepDef step = DefDatabase<GenStepDef>.GetNamed("RM_KneelingRings");
            int seeds = 0, intactMax = 0, total = 0;
            List<Thing> intact = null;
            for (int s = 0; s < Seeds; s++)
            {
                Rand.PushState(s * 7919 + 13);
                try { step.genStep.Generate(map, default(GenStepParams)); } finally { Rand.PopState(); }
                seeds++;
                int slagPosed = Count(map, out intact, out int facingBad, out int noHistory);
                if (facingBad > 0) return "FAIL " + facingBad + " ring chassis do not face the ring centre";
                if (noHistory > 0) return "FAIL " + noHistory + " intact chassis carry no history";
                if (intact.Count > System.Math.Min(RM_WarscarSettings.hospiceIntactPerMap, 3)) return "FAIL " + intact.Count + " intact chassis (cap " + RM_WarscarSettings.hospiceIntactPerMap + ")";
                intactMax = System.Math.Max(intactMax, intact.Count);
                total = slagPosed;
                if (intact.Count > 0) break;
                if (s < Seeds - 1) Clear(map);
            }
            if (total <= 0) return "FAIL the genstep placed no ring chassis on this map";
            if (intact.Count == 0 && RM_WarscarSettings.hospiceIntactPerMap > 0)   // P(no intact in 10 seeds) = (1/3)^10 at the default cap of 2
                return "FAIL no intact chassis in " + seeds + " seeds (cap " + RM_WarscarSettings.hospiceIntactPerMap + ")";
            string saved = "no intact (cap 0)";
            if (intact.Count > 0)
            {
                Thing inner = ((MinifiedThing)intact[0]).InnerThing;
                CompDeserterHistory h = inner.TryGetComp<CompDeserterHistory>();
                string xml = Scribe.saver.DebugOutputFor(intact[0]);
                if (xml == null || !xml.Contains("<deserterHistory>" + h.history.defName + "</deserterHistory>") || !xml.Contains(h.unitName))
                    return "FAIL the intact chassis's history is not in its save XML";
                saved = "saved history " + h.history.defName + " (" + h.unitName + ")";
            }
            return "PASS rings: " + total + " slagged/posed facing centre, " + intact.Count + " intact (max " + intactMax + " over " + seeds + " seeds); " + saved;
        }

        private static int Count(Map map, out List<Thing> intact, out int facingBad, out int noHistory)
        {
            intact = new List<Thing>();
            facingBad = 0; noHistory = 0;
            int n = 0;
            UnityEngine.Vector3 centre = GenStep_KneelingRings.RingCentre(map);
            foreach (Thing t in map.listerThings.AllThings.ToList())
            {
                if (t.def == RM_HospiceDefOf.RM_KneelingChassis_Slagged || t.def == RM_HospiceDefOf.RM_KneelingChassis_Posed)
                {
                    n++;
                    if (Rot4.FromAngleFlat((centre - t.Position.ToVector3Shifted()).AngleFlat()) != t.Rotation) facingBad++;
                }
                MinifiedThing m = t as MinifiedThing;
                if (m != null && m.InnerThing != null && m.InnerThing.def == RM_HospiceDefOf.RM_KneelingChassis_Intact)
                {
                    intact.Add(t);
                    CompDeserterHistory h = m.InnerThing.TryGetComp<CompDeserterHistory>();
                    if (h == null || h.history == null || h.unitName.NullOrEmpty()) noHistory++;
                }
            }
            return n;
        }

        private static void Clear(Map map)
        {
            foreach (Thing t in map.listerThings.AllThings.ToList())
            {
                MinifiedThing m = t as MinifiedThing;
                if (t.def == RM_HospiceDefOf.RM_KneelingChassis_Slagged || t.def == RM_HospiceDefOf.RM_KneelingChassis_Posed
                    || (m != null && m.InnerThing != null && m.InnerThing.def == RM_HospiceDefOf.RM_KneelingChassis_Intact))
                    t.Destroy();
            }
        }

        // Feed one input the way the haul job does: the cradle must ask for exactly this def now.
        private static string Feed(Building_HospiceCradle c, Thing t, string what)
        {
            if (!c.Accepts(t)) return "FAIL the cradle at stage " + c.Stage + " refuses " + what;
            c.Accept(t);
            if (t.Spawned) t.Destroy();
            return null;
        }

        private static string FirstHaulJob(Map map, Building_HospiceCradle c, Thing want)
        {
            Pawn hauler = map.mapPawns.FreeColonistsSpawned.FirstOrDefault(p => !p.Downed);
            if (hauler == null) return "no colonist to haul";
            Job j = new WorkGiver_HospiceHaul { def = DefDatabase<WorkGiverDef>.GetNamed("RM_HospiceHaul") }.JobOnThing(hauler, c, true);
            return j != null && c.Accepts(j.targetB.Thing) ? null : "FAIL WorkGiver_HospiceHaul offers " + hauler.LabelShort + " no haul of " + want.LabelShort;
        }

        // A2: an intact chassis hauled to a cradle passes the five stages with their inputs (components, etchant, a core)
        // and wakes as a colony mech that needs no mechanitor and keeps the history's modifications and name.
        public static string Revival(Map map)
        {
            Building_HospiceCradle c = MakeCradle(map);
            if (c == null) return "FAIL no room for a cradle near the map centre";
            MinifiedThing chassis = MakeChassis(map, c.InteractionCell);
            string err = FirstHaulJob(map, c, chassis);
            if (err != null && err.StartsWith("FAIL")) return err;
            string haul = err == null ? "haul offered" : "haul UNCHECKED (" + err + ")";
            CompDeserterHistory h = chassis.InnerThing.TryGetComp<CompDeserterHistory>();
            RM_DeserterHistoryDef hist = h.history;
            string unit = h.unitName;
            if ((err = Feed(c, chassis, "the intact chassis")) != null) return err;
            bool lightsDark = !c.LightsOn;
            c.DebugCompleteStage(false);                                    // diagnosis
            if ((err = Feed(c, ThingMaker.MakeThing(ThingDefOf.ComponentIndustrial), "a component")) != null) return err;
            c.DebugCompleteStage(false);                                    // lights
            bool lightsLit = c.LightsOn && c.GetComp<CompGlower>() != null && c.GetComp<CompGlower>().Glows;
            ThingDef etchant = Building_HospiceCradle.EtchantDef;
            if (etchant != null && (err = Feed(c, ThingMaker.MakeThing(etchant), "etchant")) != null) return err;
            c.DebugCompleteStage(false);                                    // limbs
            if ((err = Feed(c, ThingMaker.MakeThing(RM_HospiceDefOf.RM_ChassisCore), "a chassis core")) != null) return err;
            c.DebugCompleteStage(false);                                    // voice
            if (c.Stage != 5) return "FAIL the cradle is at stage " + c.Stage + " after four stages, not waking";
            c.DebugCompleteStage(false);                                    // waking
            if (c.Stage != 0) return "FAIL the cradle did not empty after waking";
            Pawn p = map.mapPawns.AllPawnsSpawned.FirstOrDefault(x => x.Faction == Faction.OfPlayer && x.Name != null && x.Name.ToStringShort == unit);
            if (p == null) return "FAIL no woken pawn named " + unit;
            List<string> bad = new List<string>();
            if (!p.IsColonyMech) bad.Add("not a colony mech");
            if (p.IsColonyMechRequiringMechanitor()) bad.Add("requires a mechanitor");
            if (p.GetOverseer() != null) bad.Add("has an overseer");
            if (p.GetComp<CompOverseerSubject>() != null) bad.Add("carries CompOverseerSubject");
            if (p.def.race.mechEnabledWorkTypes == null || !p.def.race.mechEnabledWorkTypes.Contains(WorkTypeDefOf.Hauling)) bad.Add("cannot haul");
            if (hist.modifications != null)
                foreach (HediffDef d in hist.modifications)
                    if (!p.health.hediffSet.HasHediff(d)) bad.Add("missing modification " + d.defName);
            if (!lightsDark) bad.Add("lights on during diagnosis");
            if (!lightsLit) bad.Add("lights dark after the lights stage");
            if (bad.Count > 0) return "FAIL woken " + p.kindDef.defName + " " + unit + ": " + string.Join("; ", bad);
            return "PASS " + haul + "; " + unit + " (" + hist.defName + ") woke as " + p.kindDef.defName + ", colony mech, no mechanitor, "
                + (hist.modifications == null ? 0 : hist.modifications.Count) + " modification hediffs present, lights dark->lit, etchant " + (etchant != null ? "fed" : "absent");
        }

        // A3: a forced failure leaves RM_FailedChassis carrying the machine's name.
        public static string Failure(Map map)
        {
            Building_HospiceCradle c = MakeCradle(map);
            if (c == null) return "FAIL no room for a cradle near the map centre";
            MinifiedThing chassis = MakeChassis(map, c.InteractionCell);
            string unit = chassis.InnerThing.TryGetComp<CompDeserterHistory>().unitName;
            string err = Feed(c, chassis, "the intact chassis");
            if (err != null) return err;
            c.DebugCompleteStage(false);
            if ((err = Feed(c, ThingMaker.MakeThing(ThingDefOf.ComponentIndustrial), "a component")) != null) return err;
            c.DebugCompleteStage(true);
            Thing f = map.listerThings.ThingsOfDef(RM_HospiceDefOf.RM_FailedChassis).FirstOrDefault(x => x.TryGetComp<CompDeserterHistory>()?.unitName == unit);
            if (f == null) return "FAIL no RM_FailedChassis named " + unit;
            if (!f.LabelCap.ToString().Contains(unit)) return "FAIL the failed chassis label '" + f.LabelCap + "' lacks " + unit;
            if (c.Stage != 0) return "FAIL the cradle did not empty after the failure";
            return "PASS failed wreck '" + f.LabelCap + "' keeps the name; description: " + Short(f.DescriptionDetailed);
        }

        // A4: the dev-fired walk-in (step 1: fire; the proof script advances time; step 2: read).
        public static string WalkInFire(Map map)
        {
            if (!map.listerThings.ThingsOfDef(RM_HospiceDefOf.RM_HospiceCradle).Any() && MakeCradle(map) == null)
                return "FAIL no cradle and no room for one";
            IncidentDef def = DefDatabase<IncidentDef>.GetNamed("RM_DeserterWalksIn");
            IncidentParms parms = StorytellerUtility.DefaultParmsNow(def.category, map);
            parms.forced = true;
            float pursuer = RM_WarscarSettings.hospicePursuerChance;
            RM_WarscarSettings.hospicePursuerChance = 0f;        // a hostile arrival would stop the proof's time advance
            bool ok;
            try { ok = def.Worker.TryExecute(parms); } finally { RM_WarscarSettings.hospicePursuerChance = pursuer; }
            if (!ok) return "FAIL the incident did not fire";
            Pawn w = map.mapPawns.AllPawnsSpawned.LastOrDefault(p => p.kindDef == RM_HospiceDefOf.RM_AncientServitor && p.TryGetComp<CompDeserterWalker>()?.walking == true);
            if (w == null) return "FAIL no walking servitor spawned";
            return "PASS fired: " + w.Name.ToStringShort;
        }

        public static string WalkInRead(Map map, string unit)
        {
            Pawn w = map.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.Name != null && p.Name.ToStringShort == unit && p.TryGetComp<CompDeserterWalker>() != null);
            if (w != null) return "FAIL " + unit + " is still walking, " + w.Position + " (cradle dist " + Nearest(map, w.Position).ToString("0.0") + ")";
            foreach (Thing t in map.listerThings.AllThings)
            {
                MinifiedThing m = t as MinifiedThing;
                if (m == null || m.InnerThing == null || m.InnerThing.def != RM_HospiceDefOf.RM_KneelingChassis_Intact) continue;
                if (m.InnerThing.TryGetComp<CompDeserterHistory>()?.unitName != unit) continue;
                float d = Nearest(map, t.Position);
                return d <= 6f ? "PASS " + unit + " knelt " + d.ToString("0.0") + " cells from the cradle" : "FAIL " + unit + " knelt " + d.ToString("0.0") + " cells from the cradle";
            }
            return "FAIL " + unit + " is gone and left no chassis";
        }

        private static string Short(string s)
        {
            s = (s ?? "").Replace("\n", " ");
            return s.Length > 120 ? s.Substring(0, 120) : s;
        }

        private static float Nearest(Map map, IntVec3 at)
        {
            float best = 9999f;
            foreach (Thing c in map.listerThings.ThingsOfDef(RM_HospiceDefOf.RM_HospiceCradle)) best = System.Math.Min(best, c.InteractionCell.DistanceTo(at));
            return best;
        }
    }
}
