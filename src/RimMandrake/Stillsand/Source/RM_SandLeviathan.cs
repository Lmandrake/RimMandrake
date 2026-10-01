using System.Collections.Generic;
using System.Linq;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_EVENT_CREATURES_1 — the sand leviathan incident: one worker,
    // two consumers, all data.
    //
    //   RM_MuurrokEmergence (this mod, RM tier)  — the free tier's leviathan.
    //   RUT_KraytAttack (mandrake.rut.patches)   — the krayt attack, by XML only;
    //                                               this assembly never names a krayt.
    //
    // Design: design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md
    // §2.5 ("the krayt attack, beat by beat"; "the muurrok, drafted fresh"), turn-4
    // rulings in stillsand_bedazzle_cast_2026-09-30.md §0 (krayts STAY WILD; the
    // attack is on top).
    //
    // Beats:
    //   1. The warning. A letter ("Something vast is moving under the sand.") and a
    //      rumble that grows for warningTicks: camera shake and dust at the edge
    //      cell it will come from (the Listening's sound bed is
    //      STILLSAND_SAND_SWIM_REMAINDER_1 §6, not built yet).
    //   2. The wake. It arrives at the map edge nearest whatever is loudest (a
    //      powered deep drill first, else the colony) and swims in on the sand-swim
    //      kit (RM_CompSandSwim: submerged, dust wake, breach).
    //   3. The breach. Every surfacing throws a dust column and staggers pawns in
    //      breachRingRadius (the kit staggers only the swimmer itself).
    //   4. The hunt. surfaceFighter (the krayt) goes manhunter and fights on the
    //      surface. appraise (the muurrok) picks the wettest body (hydration × body
    //      size), fires its mirror beam (RM_Verb_MirrorBeam) when it can, and strikes
    //      from under for one take.
    //   5. The dive. Once fed, on fire, after hardGroundGiveUpTicks off the sand, or
    //      after maxStayTicks. A fed leviathan takes the body down: a drag line to a
    //      disturbed-sand funnel (the kit already laid the funnel and the letter that
    //      names the taken). The dive itself leaves a funnel and a message, never a
    //      silent vanish (owner, 2026-09-29: no animal vanishes without a sign).
    //
    // Gating: biomes by defName in RM_SandLeviathanExtension.biomes (the Sarlacc
    // RSW_SwimmerRoadExtension pattern, so a consumer in another tier needs no
    // cross-reference to RM_Stillsand), and a per-incident toggle and odds slider
    // in RM_StillsandEventsSettings. Odds are weighted up by vibration (powered deep
    // drills). Unpaid water debt weights them up too (RM_StillsandWater.IncidentChanceFactor,
    // STILLSAND_RETURN_RITUAL_1), and a fresh pour on wet sand is a draw (LoudestCell).
    // ════════════════════════════════════════════════════════════════════

    public class RM_SandLeviathanExtension : DefModExtension
    {
        /// <summary>BiomeDef defNames the incident can fire on.</summary>
        public List<string> biomes = new List<string>();

        /// <summary>The leviathan's PawnKindDef, by name (it may live in another tier's mod).</summary>
        public string pawnKind;

        /// <summary>Rumble/warning time between the letter and the arrival.</summary>
        public int warningTicks = 1500;

        /// <summary>It gives up and dives after this long on the map.</summary>
        public int maxStayTicks = 30000;

        /// <summary>It dives after this many ticks off swim ground.</summary>
        public int hardGroundGiveUpTicks = 900;

        /// <summary>Krayt: manhunter, fights on the surface.</summary>
        public bool surfaceFighter;

        /// <summary>Muurrok: appraises the wettest body and hunts only that one.</summary>
        public bool appraise;

        /// <summary>Cells around a breach whose pawns stagger.</summary>
        public float breachRingRadius = 3.9f;

        public int breachStaggerTicks = 90;

        /// <summary>Odds multiplier per powered deep drill on the map (vibration).</summary>
        public float vibrationFactorPerDrill = 0.5f;

        public float maxVibrationFactor = 3f;

        /// <summary>Minimum ticks between two beams (muurrok).</summary>
        public int beamCooldownTicks = 600;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (pawnKind.NullOrEmpty())
            {
                yield return "RM_SandLeviathanExtension: pawnKind is empty";
            }
            if (biomes.NullOrEmpty())
            {
                yield return "RM_SandLeviathanExtension: biomes is empty, the incident can never fire";
            }
        }
    }

    public class RM_IncidentWorker_SandLeviathan : IncidentWorker
    {
        public RM_SandLeviathanExtension Ext => def.GetModExtension<RM_SandLeviathanExtension>();

        public PawnKindDef Kind => Ext == null ? null : DefDatabase<PawnKindDef>.GetNamedSilentFail(Ext.pawnKind);

        public override float BaseChanceThisGame => base.BaseChanceThisGame * RM_StillsandEventsSettings.OddsFor(def);

        public override float ChanceFactorNow(IIncidentTarget target)
        {
            float f = base.ChanceFactorNow(target);
            if (target is Map map && Ext != null)
            {
                int drills = RM_SandLeviathanUtility.PoweredDrills(map).Count();
                f *= Mathf.Min(1f + Ext.vibrationFactorPerDrill * drills, Ext.maxVibrationFactor);
            }
            if (target is Map m)
            {
                f *= RM_StillsandWater.IncidentChanceFactor(m, def); // STILLSAND_RETURN_RITUAL_1: unpaid debt
            }
            return f;
        }

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms))
            {
                return false;
            }
            Map map = parms.target as Map;
            RM_SandLeviathanExtension ext = Ext;
            if (map == null || ext == null || Kind == null || !RM_StillsandEventsSettings.EnabledFor(def))
            {
                return false;
            }
            if (!RM_SandLeviathanUtility.BiomeAllowed(map, ext))
            {
                return false;
            }
            RM_MapComponent_SandLeviathans comp = RM_MapComponent_SandLeviathans.For(map);
            if (comp == null || comp.HasVisitFrom(def))
            {
                return false;
            }
            return RM_SandLeviathanUtility.TryFindEntryCell(map, RM_SandLeviathanUtility.LoudestCell(map), out _);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            RM_MapComponent_SandLeviathans comp = RM_MapComponent_SandLeviathans.For(map);
            IntVec3 draw = RM_SandLeviathanUtility.LoudestCell(map);
            // The biome gate again: a dev "execute incident" can reach TryExecute without
            // CanFireNowSub, and a leviathan must still refuse a biome it does not belong to.
            if (Ext == null || !RM_SandLeviathanUtility.BiomeAllowed(map, Ext))
            {
                return false;
            }
            if (comp == null || Kind == null || !RM_SandLeviathanUtility.TryFindEntryCell(map, draw, out IntVec3 entry))
            {
                return false;
            }
            comp.Enqueue(def, Kind, entry, Find.TickManager.TicksGame + Mathf.Max(0, Ext.warningTicks));
            SendStandardLetter(parms, new LookTargets(new TargetInfo(entry, map)));
            Find.TickManager.slower.SignalForceNormalSpeedShort();
            return true;
        }
    }

    public static class RM_SandLeviathanUtility
    {
        public static bool BiomeAllowed(Map map, RM_SandLeviathanExtension ext)
        {
            string biome = map?.Biome?.defName;
            return biome != null && ext?.biomes != null && ext.biomes.Contains(biome);
        }

        /// <summary>Vibration: deep drills that are powered and on.</summary>
        public static IEnumerable<Thing> PoweredDrills(Map map)
        {
            if (map == null)
            {
                yield break;
            }
            foreach (Building b in map.listerBuildings.allBuildingsColonist)
            {
                if (b.TryGetComp<CompDeepDrill>() == null)
                {
                    continue;
                }
                CompPowerTrader power = b.TryGetComp<CompPowerTrader>();
                if (power == null || power.PowerOn)
                {
                    yield return b;
                }
            }
        }

        /// <summary>The thing it swims toward: a working drill first, else a fresh pour (wet sand), else the colony.</summary>
        public static IntVec3 LoudestCell(Map map)
        {
            Thing drill = PoweredDrills(map).FirstOrDefault();
            if (drill != null)
            {
                return drill.Position;
            }
            IntVec3 pour = RM_MapComponent_WetSand.For(map)?.LatestPourCell ?? IntVec3.Invalid;
            if (pour.IsValid)
            {
                return pour; // STILLSAND_RETURN_RITUAL_1: the rumble comes to the pour
            }
            Pawn colonist = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (colonist != null)
            {
                return colonist.Position;
            }
            return map.Center;
        }

        /// <summary>An edge cell near the draw, preferring swim ground. Sampled, nearest wins.</summary>
        public static bool TryFindEntryCell(Map map, IntVec3 draw, out IntVec3 entry)
        {
            entry = IntVec3.Invalid;
            float best = float.MaxValue;
            bool bestOnSand = false;
            for (int i = 0; i < 60; i++)
            {
                if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map) && !c.Fogged(map), map, 0f, out IntVec3 c2))
                {
                    continue;
                }
                bool sand = IsSand(c2, map);
                float d = (c2 - draw).LengthHorizontalSquared;
                if ((sand && !bestOnSand) || (sand == bestOnSand && d < best))
                {
                    entry = c2;
                    best = d;
                    bestOnSand = sand;
                }
            }
            return entry.IsValid;
        }

        public static bool IsSand(IntVec3 c, Map map)
        {
            return RM_SandSwimUtility.IsSwimTerrain(c, map, null);
        }

        public static bool IsSand(IntVec3 c, Map map, Pawn swimmer)
        {
            return RM_SandSwimUtility.IsSwimTerrain(c, map, swimmer?.def.GetModExtension<RM_SandSwimExtension>());
        }

        /// <summary>§4 of the turn-3 doc, the water appraisal: hydration × body size. Hydration
        /// is any need whose defName names thirst or hydration (Dubs Bad Hygiene and kin), by
        /// soft lookup; without one every body counts as fully watered.</summary>
        public static float WaterScore(Pawn p)
        {
            float hydration = 1f;
            List<Need> needs = p.needs?.AllNeeds;
            if (needs != null)
            {
                for (int i = 0; i < needs.Count; i++)
                {
                    string n = needs[i].def.defName;
                    if (n.IndexOf("Thirst", System.StringComparison.OrdinalIgnoreCase) >= 0
                        || n.IndexOf("Hydration", System.StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        hydration = Mathf.Max(0.05f, needs[i].CurLevelPercentage);
                        break;
                    }
                }
            }
            return p.BodySize * hydration;
        }

        public static Pawn WettestBody(Pawn hunter)
        {
            Map map = hunter.Map;
            Pawn best = null;
            float bestScore = 0f;
            bool bestPlayer = false;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == hunter || p.Dead || !RM_SandSwimUtility.HasWaterInIt(p) || p.Position.Fogged(map)
                    || p.def == hunter.def)
                {
                    continue;
                }
                bool player = p.Faction == Faction.OfPlayer;
                float s = WaterScore(p);
                if ((player && !bestPlayer) || (player == bestPlayer && s > bestScore))
                {
                    best = p;
                    bestScore = s;
                    bestPlayer = player;
                }
            }
            return best;
        }

        public static void ThrowBreachColumn(Pawn pawn, RM_SandLeviathanExtension ext)
        {
            Map map = pawn.Map;
            Vector3 loc = pawn.DrawPos;
            for (int i = 0; i < 6; i++)
            {
                FleckMaker.ThrowDustPuffThick(loc + new Vector3(Rand.Range(-0.8f, 0.8f), 0f, Rand.Range(-0.3f, 1.6f)),
                    map, 2f + 0.15f * pawn.BodySize, new Color(0.78f, 0.69f, 0.52f, 0.95f));
            }
            if (ext.breachRingRadius <= 0f || ext.breachStaggerTicks <= 0)
            {
                return;
            }
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(pawn.Position, map, ext.breachRingRadius, true))
            {
                if (t is Pawn p && p != pawn && !p.Dead)
                {
                    p.stances?.stagger?.StaggerFor(ext.breachStaggerTicks);
                }
            }
        }
    }

    /// <summary>One leviathan's visit: pending (rumbling at the edge) or on the map.</summary>
    public class RM_LeviathanVisit : IExposable
    {
        public IncidentDef incident;
        public PawnKindDef kind;
        public IntVec3 entryCell = IntVec3.Invalid;
        public int arriveTick;
        public Pawn pawn;
        public int killsAtArrival;
        public int hardGroundTicks;
        public bool diving;
        public int diveStartTick = -1;
        public bool wasSubmerged;
        public int lastBeamTick = -999999;
        public Pawn target;

        public RM_SandLeviathanExtension Ext => incident?.GetModExtension<RM_SandLeviathanExtension>();

        public void ExposeData()
        {
            Scribe_Defs.Look(ref incident, "incident");
            Scribe_Defs.Look(ref kind, "kind");
            Scribe_Values.Look(ref entryCell, "entryCell", IntVec3.Invalid);
            Scribe_Values.Look(ref arriveTick, "arriveTick");
            Scribe_References.Look(ref pawn, "pawn");
            Scribe_Values.Look(ref killsAtArrival, "killsAtArrival");
            Scribe_Values.Look(ref hardGroundTicks, "hardGroundTicks");
            Scribe_Values.Look(ref diving, "diving");
            Scribe_Values.Look(ref diveStartTick, "diveStartTick", -1);
            Scribe_Values.Look(ref wasSubmerged, "wasSubmerged");
            Scribe_Values.Look(ref lastBeamTick, "lastBeamTick", -999999);
            Scribe_References.Look(ref target, "target");
        }
    }

    public class RM_MapComponent_SandLeviathans : MapComponent
    {
        private const int Interval = 30;
        private const int DiveTimeoutTicks = 1250;

        private List<RM_LeviathanVisit> visits = new List<RM_LeviathanVisit>();

        public RM_MapComponent_SandLeviathans(Map map) : base(map)
        {
        }

        public static RM_MapComponent_SandLeviathans For(Map map) => map?.GetComponent<RM_MapComponent_SandLeviathans>();

        public IReadOnlyList<RM_LeviathanVisit> Visits => visits;

        public bool HasVisitFrom(IncidentDef incident) => visits.Any(v => v.incident == incident);

        public void Enqueue(IncidentDef incident, PawnKindDef kind, IntVec3 entry, int arriveTick)
        {
            visits.Add(new RM_LeviathanVisit { incident = incident, kind = kind, entryCell = entry, arriveTick = arriveTick });
        }

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (visits.Count == 0 || now % Interval != 0)
            {
                return;
            }
            for (int i = visits.Count - 1; i >= 0; i--)
            {
                RM_LeviathanVisit v = visits[i];
                if (v.Ext == null || v.kind == null)
                {
                    visits.RemoveAt(i);
                    continue;
                }
                if (v.pawn == null)
                {
                    if (now < v.arriveTick)
                    {
                        Rumble(v, now);
                    }
                    else if (!Arrive(v))
                    {
                        visits.RemoveAt(i);
                    }
                    continue;
                }
                if (v.pawn.Destroyed || v.pawn.Dead || !v.pawn.Spawned || v.pawn.Map != map)
                {
                    // Killed (its corpse stays: the skeleton landmark is §3's), or already gone.
                    visits.RemoveAt(i);
                    continue;
                }
                if (Tick(v, now))
                {
                    visits.RemoveAt(i);
                }
            }
        }

        /// <summary>Beat 1: the rumble on the horizon, growing toward the arrival.</summary>
        private void Rumble(RM_LeviathanVisit v, int now)
        {
            int warn = Mathf.Max(1, v.Ext.warningTicks);
            float t = 1f - Mathf.Clamp01((v.arriveTick - now) / (float)warn);
            if (map == Find.CurrentMap)
            {
                Find.CameraDriver?.shaker?.DoShake(0.02f + 0.18f * t * t); // CameraShaker clamps at 0.2 × prefs
            }
            if (v.entryCell.IsValid && Rand.Chance(0.3f + 0.7f * t))
            {
                FleckMaker.ThrowDustPuffThick(v.entryCell.ToVector3Shifted(), map, 1f + 2f * t,
                    new Color(0.78f, 0.69f, 0.52f, 0.8f));
            }
        }

        /// <summary>Beat 2: it comes in under the sand at the entry cell.</summary>
        private bool Arrive(RM_LeviathanVisit v)
        {
            IntVec3 cell = v.entryCell;
            if (!cell.IsValid || !cell.Standable(map))
            {
                if (!RM_SandLeviathanUtility.TryFindEntryCell(map, RM_SandLeviathanUtility.LoudestCell(map), out cell))
                {
                    return false;
                }
            }
            Pawn p = PawnGenerator.GeneratePawn(v.kind);
            GenSpawn.Spawn(p, cell, map);
            v.pawn = p;
            v.killsAtArrival = p.records?.GetAsInt(RecordDefOf.Kills) ?? 0;
            v.arriveTick = Find.TickManager.TicksGame;
            if (v.Ext.surfaceFighter)
            {
                p.mindState?.mentalStateHandler?.TryStartMentalState(MentalStateDefOf.ManhunterPermanent, forced: true);
            }
            return true;
        }

        /// <summary>Beats 3-5. Returns true when the visit is over.</summary>
        private bool Tick(RM_LeviathanVisit v, int now)
        {
            Pawn p = v.pawn;
            RM_SandLeviathanExtension ext = v.Ext;

            RM_CompSandSwim swim = p.GetComp<RM_CompSandSwim>();
            bool submerged = swim != null && swim.Submerged;
            if (v.wasSubmerged && !submerged && !p.Downed)
            {
                RM_SandLeviathanUtility.ThrowBreachColumn(p, ext); // beat 3
            }
            v.wasSubmerged = submerged;

            if (p.Downed)
            {
                return false; // there for the killing
            }

            bool onSand = RM_SandLeviathanUtility.IsSand(p.Position, map, p);

            if (!v.diving)
            {
                int kills = p.records?.GetAsInt(RecordDefOf.Kills) ?? 0;
                if (kills > v.killsAtArrival)
                {
                    TakeTheBody(v);
                    StartDive(v, now, "fed");
                }
                else if (p.IsBurning())
                {
                    StartDive(v, now, "fire");
                }
                else if (now - v.arriveTick > ext.maxStayTicks)
                {
                    StartDive(v, now, "bored");
                }
                else
                {
                    v.hardGroundTicks = onSand ? 0 : v.hardGroundTicks + Interval;
                    if (v.hardGroundTicks > ext.hardGroundGiveUpTicks)
                    {
                        StartDive(v, now, "hard ground");
                    }
                }
            }

            if (v.diving)
            {
                if (onSand || now - v.diveStartTick > DiveTimeoutTicks)
                {
                    Dive(v);
                    return true;
                }
                if (p.CurJob == null || p.CurJob.def != JobDefOf.Goto)
                {
                    if (CellFinder.TryFindRandomCellNear(p.Position, map, 25,
                            c => RM_SandLeviathanUtility.IsSand(c, map, p) && c.Standable(map)
                                 && p.CanReach(c, PathEndMode.OnCell, Danger.Deadly), out IntVec3 sand))
                    {
                        Job go = JobMaker.MakeJob(JobDefOf.Goto, sand);
                        go.locomotionUrgency = LocomotionUrgency.Sprint;
                        p.jobs.StartJob(go, JobCondition.InterruptForced);
                    }
                }
                return false;
            }

            if (ext.appraise)
            {
                Hunt(v, now);
            }
            else if (ext.surfaceFighter && !p.InMentalState)
            {
                p.mindState?.mentalStateHandler?.TryStartMentalState(MentalStateDefOf.ManhunterPermanent, forced: true);
            }
            return false;
        }

        /// <summary>The muurrok: the wettest body, the beam when it can, then the strike from under.</summary>
        private void Hunt(RM_LeviathanVisit v, int now)
        {
            Pawn p = v.pawn;
            if (v.target == null || v.target.Dead || !v.target.Spawned || v.target.Map != map || now % 250 == 0)
            {
                v.target = RM_SandLeviathanUtility.WettestBody(p);
            }
            if (v.target == null)
            {
                return;
            }
            if (RM_StillsandEventsSettings.mirrorBeamEnabled && now - v.lastBeamTick >= v.Ext.beamCooldownTicks
                && p.stances != null && !p.stances.FullBodyBusy)
            {
                RM_Verb_MirrorBeam beam = p.verbTracker?.AllVerbs?.OfType<RM_Verb_MirrorBeam>().FirstOrDefault();
                if (beam != null && beam.state == VerbState.Idle && beam.Available()
                    && (v.target.Position - p.Position).LengthHorizontal >= beam.verbProps.minRange
                    && beam.CanHitTarget(v.target) && beam.TryStartCastOn(v.target))
                {
                    v.lastBeamTick = now;
                    return;
                }
            }
            Job cur = p.CurJob;
            if (cur == null || cur.def != JobDefOf.AttackMelee || cur.targetA.Thing != v.target)
            {
                Job strike = JobMaker.MakeJob(JobDefOf.AttackMelee, v.target);
                strike.killIncappedTarget = true;
                strike.expiryInterval = 2000;
                p.jobs.StartJob(strike, JobCondition.InterruptForced);
            }
        }

        /// <summary>Beat 5, the take: a drag line from the body to the leviathan, and the body
        /// goes down. Only on sand: a kill on hard ground is an ordinary kill and the body stays.
        /// The funnel and the letter naming the taken are the sand-swim kit's (RM_CompSandSwim.
        /// Notify_SwimmerKilled), laid at the moment of the kill.</summary>
        private void TakeTheBody(RM_LeviathanVisit v)
        {
            Pawn p = v.pawn;
            Corpse corpse = null;
            if (v.target != null && v.target.Dead)
            {
                corpse = v.target.Corpse;
            }
            if (corpse == null)
            {
                foreach (Thing t in GenRadial.RadialDistinctThingsAround(p.Position, map, 6.9f, true))
                {
                    if (t is Corpse c && c.InnerPawn != null && c.Age < 600)
                    {
                        corpse = c;
                        break;
                    }
                }
            }
            if (corpse == null || !corpse.Spawned || !RM_SandLeviathanUtility.IsSand(corpse.Position, map, p))
            {
                return;
            }
            ThingDef drag = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_DragMark");
            if (drag != null)
            {
                foreach (IntVec3 c in GenSight.PointsOnLineOfSight(corpse.Position, p.Position))
                {
                    if (c.InBounds(map) && RM_SandLeviathanUtility.IsSand(c, map, p))
                    {
                        FilthMaker.TryMakeFilth(c, map, drag, 1);
                    }
                }
            }
            ThingDef funnel = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_DisturbedSand");
            if (funnel != null)
            {
                FilthMaker.TryMakeFilth(corpse.Position, map, funnel, 2);
            }
            corpse.Destroy(DestroyMode.Vanish);
        }

        private void StartDive(RM_LeviathanVisit v, int now, string why)
        {
            v.diving = true;
            v.diveStartTick = now;
            Pawn p = v.pawn;
            p.mindState?.mentalStateHandler?.Reset();
            p.jobs?.StopAll();
        }

        /// <summary>It goes down where it stands: a funnel and a message, never a silent vanish.</summary>
        private void Dive(RM_LeviathanVisit v)
        {
            Pawn p = v.pawn;
            IntVec3 at = p.Position;
            ThingDef funnel = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_DisturbedSand")
                              ?? DefDatabase<ThingDef>.GetNamedSilentFail("Filth_Sand");
            if (funnel != null)
            {
                foreach (IntVec3 c in GenRadial.RadialCellsAround(at, 1.5f, true))
                {
                    if (c.InBounds(map))
                    {
                        FilthMaker.TryMakeFilth(c, map, funnel, 1);
                    }
                }
            }
            for (int i = 0; i < 4; i++)
            {
                FleckMaker.ThrowDustPuffThick(p.DrawPos, map, 2.5f, new Color(0.78f, 0.69f, 0.52f, 0.9f));
            }
            Messages.Message("The " + p.KindLabel + " has gone down into the sand. A collapsed funnel marks where it went.",
                new LookTargets(new TargetInfo(at, map)), MessageTypeDefOf.NeutralEvent);
            p.DeSpawn(DestroyMode.Vanish);
            if (!p.Destroyed && !Find.WorldPawns.Contains(p))
            {
                Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Decide);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref visits, "rmSandLeviathanVisits", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && visits == null)
            {
                visits = new List<RM_LeviathanVisit>();
            }
        }
    }
}
