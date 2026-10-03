using System.Collections.Generic;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.NightsideIce
{
    // NIGHTSIDEICE_SHIVVEN_BUILD_1 (split from NIGHTSIDEICE_HEAT_DIAL_BUILD_1 item 2; design
    // nightsideice_bedazzle_review_2026-10-01.md section 1 and section 4 row 1). Blind, thermal, colonial
    // tunnelers that travel inside the ice.
    //
    // Movement is CreatureBehaviors' sand-swim kit retuned by data (RM_Shivven's RM_SandSwimExtension:
    // swim terrain Ice, own rumble/breach sounds, white wake, confinedToSwimTerrain, breachForAnyTarget).
    // This comp is the only shivven-specific brain: every IntervalTicks it reads the hottest working
    // heater from RM_HeatDial and walks toward the ice cell nearest it, along a path found over ICE
    // CELLS ONLY (so the vanilla pathfinder is never asked to route across a floor), a few cells at a
    // time. Reaching ice beside the heater it starts a melee job on it, which breaches it (the strike).
    // A heater with no ice beside it (inside a floored, walled base) is out of reach: the shivven wait at
    // the nearest ice. That is the hull rule, and the opening the breach cracks
    // (NIGHTSIDEICE_BREACH_CRACKS_1) are for.
    //
    // It leaves a pawn fight alone (a melee threat, or a melee job on a pawn) so a struck shivven fights
    // back like any animal.
    public class RM_CompProperties_ShivvenHeatSeek : CompProperties
    {
        public int intervalTicks = 120;
        /// <summary>Cells along the ice path per leg; the leg is re-planned each interval.</summary>
        public int legCells = 8;
        /// <summary>Ice cells the path search may visit before giving up.</summary>
        public int searchCellBudget = 6000;

        public RM_CompProperties_ShivvenHeatSeek()
        {
            compClass = typeof(RM_CompShivvenHeatSeek);
        }
    }

    public class RM_CompShivvenHeatSeek : ThingComp
    {
        public RM_CompProperties_ShivvenHeatSeek Props => (RM_CompProperties_ShivvenHeatSeek)props;

        /// <summary>What it is doing, for the proofs and the inspect line: idle / seeking / waiting / striking.</summary>
        public string state = "idle";
        public Thing source;
        public IntVec3 goal = IntVec3.Invalid;

        private RM_SandSwimExtension swim;
        private RM_SandSwimExtension Swim => swim ?? (swim = parent.def.GetModExtension<RM_SandSwimExtension>());

        public override void CompTick()
        {
            base.CompTick();
            if (parent.IsHashIntervalTick(Props.intervalTicks))
            {
                Think();
            }
        }

        public void Think()
        {
            if (!(parent is Pawn pawn) || !pawn.Spawned || pawn.Dead || pawn.Downed || Swim == null)
            {
                return;
            }
            // The setting drives the kit's flag; the extension is shared by every shivven.
            Swim.confinedToSwimTerrain = RM_NightsideIceSettings.masterEnabled && RM_NightsideIceSettings.shivvenIceOnly;

            if (!RM_NightsideIceSettings.masterEnabled || !RM_NightsideIceSettings.shivvenHeatSeek
                || pawn.InMentalState || pawn.mindState?.meleeThreat != null || pawn.Faction != null)
            {
                state = "idle";
                return;
            }
            Job cur = pawn.CurJob;
            if (cur != null && cur.def == JobDefOf.AttackMelee && cur.targetA.Thing is Pawn)
            {
                state = "idle";
                return;
            }

            RM_HeatDial dial = RM_HeatDial.For(pawn.Map);
            source = dial?.HottestSource();
            float range = RM_NightsideIceSettings.shivvenSenseRange;
            if (source == null || (source.Position - pawn.Position).LengthHorizontalSquared > range * range)
            {
                state = "idle";
                source = null;
                return;
            }

            Map map = pawn.Map;
            bool onIce = RM_SandSwimUtility.IsSwimTerrain(pawn.Position, map, Swim);
            if (onIce && Touches(pawn.Position, source))
            {
                if (!RM_NightsideIceSettings.shivvenStrikeHeaters)
                {
                    state = "waiting";
                    return;
                }
                state = "striking";
                if (cur == null || cur.def != JobDefOf.AttackMelee || cur.targetA.Thing != source)
                {
                    Job strike = JobMaker.MakeJob(JobDefOf.AttackMelee, source);
                    strike.expiryInterval = 900;
                    strike.checkOverrideOnExpire = true;
                    pawn.jobs.StartJob(strike, JobCondition.InterruptForced);
                }
                return;
            }

            List<IntVec3> path = IcePathToward(pawn, source);
            if (path == null || path.Count == 0)
            {
                state = "waiting"; // already at the closest ice it can reach
                goal = pawn.Position;
                return;
            }
            goal = path[path.Count - 1];
            IntVec3 leg = path[System.Math.Min(Props.legCells, path.Count) - 1];
            state = "seeking";
            if (cur != null && cur.def == JobDefOf.Goto && cur.targetA.Cell == leg)
            {
                return;
            }
            Job go = JobMaker.MakeJob(JobDefOf.Goto, leg);
            go.locomotionUrgency = LocomotionUrgency.Jog;
            go.expiryInterval = Props.intervalTicks * 3;
            go.checkOverrideOnExpire = true;
            pawn.jobs.StartJob(go, JobCondition.InterruptForced);
        }

        private static bool Touches(IntVec3 c, Thing t)
        {
            return t.OccupiedRect().ExpandedBy(1).Contains(c) && !t.OccupiedRect().Contains(c);
        }

        /// <summary>
        /// Breadth-first over standable ice from the shivven (or, when it is off the ice, over any
        /// standable cell until it reaches ice). Returns the cell path to the reached cell nearest the
        /// source, preferring one touching it; empty when it already stands on that cell.
        /// </summary>
        private List<IntVec3> IcePathToward(Pawn pawn, Thing src)
        {
            Map map = pawn.Map;
            IntVec3 start = pawn.Position;
            bool startOnIce = RM_SandSwimUtility.IsSwimTerrain(start, map, Swim);
            var parent = new Dictionary<IntVec3, IntVec3>();
            var queue = new Queue<IntVec3>();
            parent[start] = start;
            queue.Enqueue(start);
            IntVec3 best = start;
            float bestScore = Score(start, src, startOnIce);
            int budget = Props.searchCellBudget;
            while (queue.Count > 0 && budget-- > 0)
            {
                IntVec3 c = queue.Dequeue();
                bool cIce = RM_SandSwimUtility.IsSwimTerrain(c, map, Swim);
                if (!startOnIce && cIce)
                {
                    best = c; // off the ice: the first ice reached is the way home
                    break;
                }
                for (int i = 0; i < 8; i++)
                {
                    IntVec3 n = c + GenAdj.AdjacentCells[i];
                    if (parent.ContainsKey(n) || !n.InBounds(map) || !n.Standable(map))
                    {
                        continue;
                    }
                    if (startOnIce && !RM_SandSwimUtility.IsSwimTerrain(n, map, Swim))
                    {
                        continue;
                    }
                    if (i >= 4 && !DiagonalOk(c, n, map, startOnIce))
                    {
                        continue;
                    }
                    parent[n] = c;
                    queue.Enqueue(n);
                    float s = Score(n, src, startOnIce);
                    if (s < bestScore)
                    {
                        bestScore = s;
                        best = n;
                    }
                }
            }
            var path = new List<IntVec3>();
            for (IntVec3 c = best; c != start; c = parent[c])
            {
                path.Add(c);
            }
            path.Reverse();
            return path;
        }

        // A diagonal step must not cut a corner off the ice (or through a wall).
        private bool DiagonalOk(IntVec3 from, IntVec3 to, Map map, bool iceOnly)
        {
            IntVec3 a = new IntVec3(to.x, 0, from.z);
            IntVec3 b = new IntVec3(from.x, 0, to.z);
            return a.Standable(map) && b.Standable(map)
                && (!iceOnly || (RM_SandSwimUtility.IsSwimTerrain(a, map, Swim) && RM_SandSwimUtility.IsSwimTerrain(b, map, Swim)));
        }

        private static float Score(IntVec3 c, Thing src, bool onIce)
        {
            if (!onIce)
            {
                return 0f;
            }
            return Touches(c, src) ? -1f : (c - src.Position).LengthHorizontalSquared;
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_NightsideIceSettings.masterEnabled || state == "idle" || source == null)
            {
                return null;
            }
            switch (state)
            {
                case "seeking": return "Following the heat of " + source.LabelShort + ".";
                case "waiting": return "Waiting in the ice near " + source.LabelShort + ".";
                case "striking": return "Striking " + source.LabelShort + ".";
                default: return null;
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref state, "rmShivvenState", "idle");
        }
    }

    /// <summary>Bridge proofs (jawa/static_call), chain shivven in validation.py.</summary>
    public static class RM_ShivvenProof
    {
        /// <summary>
        /// Lays a strip of Ice from a player heater outward (natural cells only, never a floor or an
        /// edifice), spawns a shivven at its far end, and runs one Think. Reads back state, job, whether it
        /// is under the ice and the heater it chose. Needs a working player heater on the map.
        /// "state=seeking job=Goto submerged=... source=Heater dist=14".
        /// </summary>
        public static string ProofSeek(Map map)
        {
            RM_HeatDial dial = RM_HeatDial.For(map);
            Thing src = dial?.HottestSource();
            if (src == null)
            {
                return "REFUSED: no working player heater on this map (build and power one first)";
            }
            TerrainDef ice = TerrainDefOf.Ice;
            ThingDef race = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Shivven");
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Shivven");
            if (ice == null || race == null || kind == null)
            {
                return "REFUSED: Ice terrain or RM_Shivven not loaded";
            }
            IntVec3 far = IntVec3.Invalid;
            int laid = 0;
            foreach (IntVec3 dir in new[] { IntVec3.East, IntVec3.West, IntVec3.North, IntVec3.South })
            {
                IntVec3 c = src.Position + dir;
                int run = 0;
                for (int step = 1; step <= 16 && c.InBounds(map); step++, c += dir)
                {
                    if (c.GetEdifice(map) != null || c.GetTerrain(map).layerable || !c.Walkable(map))
                    {
                        break;
                    }
                    map.terrainGrid.SetTerrain(c, ice);
                    laid++;
                    run = step;
                    far = c;
                }
                if (run >= 10)
                {
                    break;
                }
            }
            if (!far.IsValid)
            {
                return "REFUSED: no open natural ground beside " + src.LabelShort;
            }
            Pawn p = PawnGenerator.GeneratePawn(kind);
            GenSpawn.Spawn(p, far, map);
            RM_CompShivvenHeatSeek comp = p.GetComp<RM_CompShivvenHeatSeek>();
            comp?.Think();
            return Read(p) + " laid=" + laid;
        }

        /// <summary>Every shivven on the map: state, job, under the ice, terrain underfoot.</summary>
        public static string ProofState(Map map)
        {
            var parts = new List<string>();
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p.def.defName == "RM_Shivven")
                {
                    parts.Add(Read(p));
                }
            }
            return parts.Count == 0 ? "NONE" : string.Join(" | ", parts);
        }

        private static string Read(Pawn p)
        {
            RM_CompShivvenHeatSeek comp = p.GetComp<RM_CompShivvenHeatSeek>();
            RM_CompSandSwim swim = p.GetComp<RM_CompSandSwim>();
            string dist = comp?.source == null ? "-" : ((int)p.Position.DistanceTo(comp.source.Position)).ToString();
            return "state=" + (comp?.state ?? "-") + " job=" + (p.CurJobDef?.defName ?? "-")
                + " submerged=" + (swim?.Submerged ?? false) + " terrain=" + p.Position.GetTerrain(p.Map)?.defName
                + " source=" + (comp?.source?.def.defName ?? "-") + " dist=" + dist;
        }
    }
}
