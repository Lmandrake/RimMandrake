using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.LanternDeeps
{
    // ════════════════════════════════════════════════════════════════════
    // LANTERNDEEPS_CREEP_CLEAVERS_BUILD_1. Spec: design/Jawa/worldbuilding/biomes/
    // lanterndeeps_bedazzle_review_2026-10-01.md §4 row 4; the_lantern_deeps.md §4 (crystals AS
    // creatures, never crystal-studded animals). Free tier.
    //
    //  The Creep: "slow accretive predator — grows over what sleeps near it; dissolves and
    //  re-precipitates its way across a cavern over days". It is a crust of non-edifice buildings
    //  (RM_CreepCrust: Standable, so it can grow under a bed) driven by RM_MapComponent_Creep once
    //  an in-game hour: with a sleeper or a downed body within reach it precipitates one cell
    //  toward it; with none it drifts (one new cell at the rim, the oldest dissolves past a cap).
    //  Anything asleep or down on the crust is engulfed (RM_CreepEngulfed, lethal if left) and a
    //  letter names it: nothing vanishes without a sign. Killed by hitting the crust.
    //
    //  The Cleavers: "fragment-life that moves by fracturing — fast, violent, the shatter as
    //  locomotion; the caverns' true danger". RM_CompCleave: moving, it sheds a trail of its own
    //  shards; struck hard, it splits and the shard walks away as a new Cleaver (cleaving is
    //  birth), capped per map.
    // ════════════════════════════════════════════════════════════════════

    public class RM_CreepCrust : Building
    {
        public int bornTick;

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            if (!respawningAfterLoad)
            {
                bornTick = Find.TickManager.TicksGame;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref bornTick, "bornTick", 0);
        }
    }

    public class RM_MapComponent_Creep : CustomMapComponent
    {
        public const string CrustDefName = "RM_CreepCrust";
        public const string EngulfDefName = "RM_CreepEngulfed";
        public const float ReachRadius = 14f;
        public const int DriftCap = 14;
        public const int TotalCap = 160;
        public const int DriftEveryHours = 6;
        public const float EngulfPerHour = 0.12f;

        private int hours;
        private int lastStalkMessageTick = -999999;
        private HashSet<int> engulfedNotified = new HashSet<int>();

        public RM_MapComponent_Creep(Map map) : base(map)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref hours, "hours", 0);
            Scribe_Values.Look(ref lastStalkMessageTick, "lastStalkMessageTick", -999999);
            Scribe_Collections.Look(ref engulfedNotified, "engulfedNotified", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && engulfedNotified == null)
            {
                engulfedNotified = new HashSet<int>();
            }
        }

        public override void MapComponentTick()
        {
            if (!LanternDeepsSettings.creepEnabled || !map.IsHashIntervalTick(GenDate.TicksPerHour))
            {
                return;
            }
            Hour();
        }

        public static ThingDef CrustDef => DefDatabase<ThingDef>.GetNamedSilentFail(CrustDefName);

        private static bool Sleeper(Pawn p)
        {
            return p != null && p.Spawned && !p.Dead && (p.Downed || !p.Awake()) && !(p.def.defName == "RM_Cleaver");
        }

        // One in-game hour of the Creep. Returns a short account (the proof reads it).
        public string Hour()
        {
            ThingDef def = CrustDef;
            if (def == null)
            {
                return "no crust def";
            }
            List<Thing> crust = map.listerThings.ThingsOfDef(def).ToList();
            if (crust.Count == 0)
            {
                return "no crust";
            }
            hours++;
            Engulf(crust);
            int grow = GenMath.RoundRandom(LanternDeepsSettings.creepGrowthMultiplier);
            Pawn target = FindTarget(crust);
            string did = "idle";
            if (target != null)
            {
                for (int i = 0; i < grow && crust.Count < TotalCap; i++)
                {
                    Thing made = GrowToward(crust, target.Position);
                    if (made == null)
                    {
                        break;
                    }
                    crust.Add(made);
                    did = "stalk " + target.LabelShort;
                }
                if (Find.TickManager.TicksGame - lastStalkMessageTick > GenDate.TicksPerDay / 2 && target.Faction == Faction.OfPlayer)
                {
                    lastStalkMessageTick = Find.TickManager.TicksGame;
                    Messages.Message("RM_CreepStalks".Translate(target.LabelShort), new TargetInfo(Nearest(crust, target.Position).Position, map),
                        MessageTypeDefOf.ThreatSmall);
                }
            }
            else if (hours % DriftEveryHours == 0)
            {
                Thing made = GrowRandom(crust);
                if (made != null)
                {
                    crust.Add(made);
                    did = "drift";
                }
                // dissolve the oldest: the Creep re-precipitates its way across the cavern
                while (crust.Count > DriftCap)
                {
                    Thing oldest = crust.OrderBy(t => (t as RM_CreepCrust)?.bornTick ?? 0).First();
                    crust.Remove(oldest);
                    FleckMaker.ThrowDustPuff(oldest.Position, map, 0.6f);
                    oldest.Destroy(DestroyMode.Vanish);
                }
            }
            return did + " crust=" + crust.Count;
        }

        private void Engulf(List<Thing> crust)
        {
            HediffDef engulf = DefDatabase<HediffDef>.GetNamedSilentFail(EngulfDefName);
            if (engulf == null)
            {
                return;
            }
            HashSet<int> seen = new HashSet<int>();
            foreach (Thing c in crust)
            {
                List<Thing> here = c.Position.GetThingList(map);
                for (int i = here.Count - 1; i >= 0; i--)
                {
                    if (!(here[i] is Pawn p) || !Sleeper(p))
                    {
                        continue;
                    }
                    seen.Add(p.thingIDNumber);
                    HealthUtility.AdjustSeverity(p, engulf, EngulfPerHour);
                    // the colony's own (and its prisoners) get a letter; wildlife is the visible crust and the body
                    bool ours = p.Faction == Faction.OfPlayer || p.HostFaction == Faction.OfPlayer;
                    if (ours && !engulfedNotified.Contains(p.thingIDNumber))
                    {
                        engulfedNotified.Add(p.thingIDNumber);
                        Find.LetterStack.ReceiveLetter("RM_CreepEngulfLabel".Translate(), "RM_CreepEngulfText".Translate(p.LabelShort),
                            LetterDefOf.ThreatSmall, p);
                    }
                }
            }
            // a body that got clear is a new event next time
            engulfedNotified.RemoveWhere(id => !seen.Contains(id));
        }

        private Pawn FindTarget(List<Thing> crust)
        {
            Pawn best = null;
            float bestDist = ReachRadius;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (!Sleeper(p) || p.Position.GetFirstThing(map, CrustDef) != null)
                {
                    continue;
                }
                float d = Nearest(crust, p.Position).Position.DistanceTo(p.Position);
                if (d < bestDist)
                {
                    bestDist = d;
                    best = p;
                }
            }
            return best;
        }

        private static Thing Nearest(List<Thing> crust, IntVec3 to)
        {
            Thing best = crust[0];
            float bd = float.MaxValue;
            foreach (Thing t in crust)
            {
                float d = t.Position.DistanceToSquared(to);
                if (d < bd)
                {
                    bd = d;
                    best = t;
                }
            }
            return best;
        }

        private bool CanCrust(IntVec3 c)
        {
            return c.InBounds(map) && c.Walkable(map) && c.GetFirstThing(map, CrustDef) == null;
        }

        private Thing GrowToward(List<Thing> crust, IntVec3 target)
        {
            IntVec3 from = Nearest(crust, target).Position;
            IntVec3 pick = IntVec3.Invalid;
            float bd = float.MaxValue;
            foreach (IntVec3 adj in GenAdj.AdjacentCellsAndInside)
            {
                IntVec3 c = from + adj;
                if (!CanCrust(c))
                {
                    continue;
                }
                float d = c.DistanceToSquared(target);
                if (d < bd)
                {
                    bd = d;
                    pick = c;
                }
            }
            return pick.IsValid ? Precipitate(pick) : null;
        }

        private Thing GrowRandom(List<Thing> crust)
        {
            foreach (Thing t in crust.InRandomOrder())
            {
                foreach (IntVec3 adj in GenAdj.AdjacentCells.InRandomOrder())
                {
                    IntVec3 c = t.Position + adj;
                    if (CanCrust(c))
                    {
                        return Precipitate(c);
                    }
                }
            }
            return null;
        }

        public Thing Precipitate(IntVec3 c)
        {
            Thing t = GenSpawn.Spawn(ThingMaker.MakeThing(CrustDef), c, map);
            FleckMaker.ThrowDustPuff(c, map, 0.5f);
            return t;
        }
    }

    // New Deeps: one Creep, by chance, seeded as a small crust in open floor.
    public class RM_GenStep_Creep : GenStep
    {
        public float chance = 0.6f;
        public IntRange seedCells = new IntRange(5, 9);

        public override int SeedPart => 482119733;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (LanternDeepsSettings.creepEnabled && Rand.Chance(chance))
            {
                Seed(map, seedCells.RandomInRange);
            }
        }

        public static string Seed(Map map, int cells)
        {
            ThingDef def = RM_MapComponent_Creep.CrustDef;
            if (def == null)
            {
                return "no crust def";
            }
            if (!CellFinder.TryFindRandomCell(map, c => c.Standable(map) && c.DistanceToEdge(map) > 10 && c.GetEdifice(map) == null, out IntVec3 root))
            {
                return "no cell";
            }
            int made = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(root, 2.9f, true))
            {
                if (made >= cells)
                {
                    break;
                }
                if (c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null)
                {
                    GenSpawn.Spawn(ThingMaker.MakeThing(def), c, map);
                    made++;
                }
            }
            return "seeded " + made + " at " + root;
        }
    }

    public class RM_CompProperties_Cleave : CompProperties
    {
        public float minDamage = 5f;
        public float chance = 0.5f;
        public int cooldownTicks = 900;
        public float shardAge = 0.3f;
        public ThingDef shardFilth;
        public int trailInterval = 40;
        public float trailChance = 0.35f;

        public RM_CompProperties_Cleave()
        {
            compClass = typeof(RM_CompCleave);
        }
    }

    public class RM_CompCleave : ThingComp
    {
        public int lastCleaveTick = -999999;
        private static int lastMessageTick = -999999;
        public static bool forceForProof;

        private RM_CompProperties_Cleave Props => (RM_CompProperties_Cleave)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastCleaveTick, "lastCleaveTick", -999999);
        }

        // Fracture as locomotion: a moving Cleaver leaves its own shards behind.
        public override void CompTick()
        {
            if (!(parent is Pawn p) || !p.Spawned || Props.shardFilth == null || !p.IsHashIntervalTick(Props.trailInterval))
            {
                return;
            }
            if (p.pather != null && p.pather.Moving && Rand.Chance(Props.trailChance))
            {
                FilthMaker.TryMakeFilth(p.Position, p.Map, Props.shardFilth);
            }
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (!LanternDeepsSettings.cleavingEnabled || !(parent is Pawn p) || p.Dead || !p.Spawned)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (totalDamageDealt < Props.minDamage || now - lastCleaveTick < Props.cooldownTicks)
            {
                return;
            }
            if (!forceForProof && !Rand.Chance(Props.chance))
            {
                return;
            }
            if (p.Map.mapPawns.AllPawnsSpawned.Count(x => x.def == p.def) >= LanternDeepsSettings.cleaverMapCap)
            {
                return;
            }
            Cleave(p);
            lastCleaveTick = now;
        }

        public Pawn Cleave(Pawn p)
        {
            Map map = p.Map;
            if (!CellFinder.TryFindRandomCellNear(p.Position, map, 2, c => c.Standable(map) && c != p.Position, out IntVec3 cell))
            {
                return null;
            }
            Pawn shard = PawnGenerator.GeneratePawn(new PawnGenerationRequest(p.kindDef, null,
                fixedBiologicalAge: Props.shardAge, fixedChronologicalAge: Props.shardAge));
            GenSpawn.Spawn(shard, cell, map);
            if (p.MentalStateDef == MentalStateDefOf.Manhunter || p.MentalStateDef == MentalStateDefOf.ManhunterPermanent)
            {
                shard.mindState.mentalStateHandler.TryStartMentalState(p.MentalStateDef, null, true);
            }
            if (Props.shardFilth != null)
            {
                for (int i = 0; i < 3; i++)
                {
                    FilthMaker.TryMakeFilth(p.Position, map, Props.shardFilth);
                }
            }
            FleckMaker.ThrowDustPuff(p.Position, map, 1f);
            if (Find.TickManager.TicksGame - lastMessageTick > GenDate.TicksPerHour)
            {
                lastMessageTick = Find.TickManager.TicksGame;
                Messages.Message("RM_CleaverSplits".Translate(), new TargetInfo(cell, map), MessageTypeDefOf.ThreatSmall);
            }
            return shard;
        }
    }

    // jawa/static_call proofs (validation.py, creep_cleavers).
    public static class RM_CreepCleaversProof
    {
        // Downs an animal 5 cells from a fresh 3-cell crust, runs the Creep `hours` hours, reports
        // distance before/after and the engulf severity.
        public static string ProofCreep(string hoursArg)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_Creep comp = map?.GetComponent<RM_MapComponent_Creep>();
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("Muffalo");
            if (map == null || comp == null || kind == null)
            {
                return "no map, comp or kind (comp only on a Deep)";
            }
            if (!int.TryParse(hoursArg, out int hours))
            {
                hours = 8;
            }
            if (!CellFinder.TryFindRandomCell(map, c => c.Standable(map) && c.DistanceToEdge(map) > 12
                    && (c + new IntVec3(5, 0, 0)).Standable(map) && (c + new IntVec3(4, 0, 0)).Standable(map), out IntVec3 at))
            {
                return "no cell";
            }
            Pawn victim = PawnGenerator.GeneratePawn(kind);
            GenSpawn.Spawn(victim, at, map);
            HealthUtility.DamageUntilDowned(victim, false);
            for (int i = 4; i <= 6; i++)
            {
                IntVec3 c = at + new IntVec3(i, 0, 0);
                if (c.InBounds(map) && c.Walkable(map))
                {
                    comp.Precipitate(c);
                }
            }
            float before = Dist(map, victim);
            string last = "";
            for (int h = 0; h < hours; h++)
            {
                last = comp.Hour();
            }
            Hediff e = victim.health?.hediffSet?.GetFirstHediffOfDef(DefDatabase<HediffDef>.GetNamedSilentFail(RM_MapComponent_Creep.EngulfDefName));
            return "before=" + before.ToString("0.0") + " after=" + Dist(map, victim).ToString("0.0") + " engulf=" + (e?.Severity ?? 0f).ToString("0.00")
                + " downed=" + victim.Downed + " last=" + last;
        }

        private static float Dist(Map map, Pawn p)
        {
            float best = 999f;
            foreach (Thing t in map.listerThings.ThingsOfDef(RM_MapComponent_Creep.CrustDef))
            {
                best = System.Math.Min(best, t.Position.DistanceTo(p.Position));
            }
            return best;
        }

        // Spawns a Cleaver and strikes it hard three times; reports Cleavers on the map before/after.
        public static string ProofCleave(string unused)
        {
            Map map = Find.CurrentMap;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Cleaver");
            if (map == null || kind == null)
            {
                return "no map or kind";
            }
            if (!CellFinder.TryFindRandomCell(map, c => c.Standable(map) && c.DistanceToEdge(map) > 8, out IntVec3 cell))
            {
                return "no cell";
            }
            Pawn p = PawnGenerator.GeneratePawn(kind);
            GenSpawn.Spawn(p, cell, map);
            int before = map.mapPawns.AllPawnsSpawned.Count(x => x.def == p.def);
            RM_CompCleave comp = p.TryGetComp<RM_CompCleave>();
            forceProof(true);
            try
            {
                for (int i = 0; i < 3 && !p.Dead; i++)
                {
                    if (comp != null)
                    {
                        comp.lastCleaveTick = -999999;
                    }
                    p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, 7f));
                }
            }
            finally
            {
                forceProof(false);
            }
            int after = map.mapPawns.AllPawnsSpawned.Count(x => x.def == p.def);
            return "before=" + before + " after=" + after + " comp=" + (comp != null);
        }

        private static void forceProof(bool on)
        {
            RM_CompCleave.forceForProof = on;
        }
    }
}
