using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.TerminalBiomes
{
    // GREYSEA_LAMP_RESPONSE_BUILD_1 (split from GREYSEA_RULED_CONTENT_1, Q12).
    // Design: the_grey_deep_danger_floor_pass_2026-09-27.md §2.2. Ruling Q12 (a):
    // DETERMINISTIC AND FORGIVING — worklight-class light only (never a torch),
    // only after hours of steady burn, telegraphed by the watcher at the rim and
    // fresh scrape-sign, and dowsing the lamp always resets. The giant breaks
    // the LAMP — never the ship, never the pawns (ruled 2026-09-26).
    //
    // Layer 1 (nissik, sallik, immu drawn in) rides the shared light-brain:
    // RM_SeekGlowExtension mode "drawn" -> RM_BaskInGlow. Layers 2-3 are
    // deterministic, so this component drives them per lamp:
    //   each worklight-class lamp (powered, glow radius >= setting) carries a
    //   continuous-burn clock; dark = clock gone (dowsing resets).
    //   >= 50% of the giant's hours: a fessk comes to the rim and watches
    //       (walks in if the map has none).
    //   >= 75%: fresh scrape-sign in the silt at the light's edge + message.
    //   >= 100%: the reefback answers — the map's own, or one walks in — and
    //       breaks that lamp, then a walked-in giant leaves.
    // A lamp it cannot reach (inside a closed hull: animals do not open doors)
    // is never answered — "never the ship".
    public class RM_MapComponent_GreyLampWatch : MapComponent
    {
        public const int Interval = 250;

        private Dictionary<int, int> litTicks = new Dictionary<int, int>();
        private HashSet<int> watched = new HashSet<int>();
        private HashSet<int> scraped = new HashSet<int>();
        private HashSet<int> answered = new HashSet<int>();
        private HashSet<int> walkedIn = new HashSet<int>();
        private int nextWatchOrderTick;

        public RM_MapComponent_GreyLampWatch(Map map) : base(map)
        {
        }

        public static int ThresholdTicks => Mathf.RoundToInt(RM_TerminalBiomesSettings.greyLampGiantBurnHours * 2500f);

        public static bool IsWorklightClass(Thing t, out CompGlower glower)
        {
            glower = t.TryGetComp<CompGlower>();
            return glower != null
                && t.Faction == Faction.OfPlayer
                && t.TryGetComp<CompPowerTrader>() != null       // never a torch or brazier
                && glower.GlowRadius >= RM_TerminalBiomesSettings.greyLampGiantMinRadius;
        }

        public int LitTicksOf(Thing t) => t != null && litTicks.TryGetValue(t.thingIDNumber, out int v) ? v : 0;

        public bool WalkedIn(Pawn p) => p != null && walkedIn.Contains(p.thingIDNumber);

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % Interval != 0)
            {
                return;
            }
            if (map.Biome == null || map.Biome.defName != RM_GreyCrust.GreyBiome)
            {
                return;
            }
            if (!RM_TerminalBiomesSettings.GreyLampWatcherActive && !RM_TerminalBiomesSettings.GreyLampGiantActive)
            {
                litTicks.Clear();
                return;
            }
            Advance(Interval);
        }

        // One step of every lamp's clock; public for the proof.
        public void Advance(int ticks)
        {
            HashSet<int> seen = new HashSet<int>();
            foreach (Building b in map.listerBuildings.allBuildingsColonist.ToList())
            {
                if (!IsWorklightClass(b, out CompGlower glower) || !glower.Glows)
                {
                    continue;
                }
                int id = b.thingIDNumber;
                seen.Add(id);
                litTicks.TryGetValue(id, out int lit);
                lit += ticks;
                litTicks[id] = lit;
                float f = lit / (float)Mathf.Max(1, ThresholdTicks);
                if (f >= 0.5f && RM_TerminalBiomesSettings.GreyLampWatcherActive)
                {
                    TryWatch(b, glower);
                }
                if (f >= 0.75f && RM_TerminalBiomesSettings.GreyLampWatcherActive && scraped.Add(id))
                {
                    LayScrapeSign(b, glower);
                }
                if (f >= 1f && RM_TerminalBiomesSettings.GreyLampGiantActive && !answered.Contains(id))
                {
                    if (TryAnswer(b))
                    {
                        answered.Add(id);
                    }
                }
            }
            SendHomeIdleGiants();
            // Dowsing always resets: a lamp that is dark (or gone) loses its
            // whole clock and every tell it had earned.
            foreach (int id in litTicks.Keys.Where(k => !seen.Contains(k)).ToList())
            {
                litTicks.Remove(id);
                watched.Remove(id);
                scraped.Remove(id);
                answered.Remove(id);
            }
        }

        // ── Layer 2: the watcher at the rim ─────────────────────────────────
        private void TryWatch(Building lamp, CompGlower glower)
        {
            ThingDef fesskDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Fessk");
            JobDef watchJob = DefDatabase<JobDef>.GetNamedSilentFail("RM_WatchGlow");
            if (fesskDef == null || watchJob == null)
            {
                return;
            }
            Pawn fessk = map.mapPawns.AllPawnsSpawned
                .FirstOrDefault(p => p.def == fesskDef && p.Faction == null && !p.Downed && !p.Dead);
            if (fessk == null)
            {
                if (watched.Contains(lamp.thingIDNumber))
                {
                    return; // one walk-in per lamp; if it left, it left
                }
                fessk = WalkIn("RM_Fessk");
                if (fessk == null)
                {
                    return;
                }
            }
            bool first = watched.Add(lamp.thingIDNumber);
            if (fessk.CurJobDef == watchJob || Find.TickManager.TicksGame < nextWatchOrderTick)
            {
                return;
            }
            if (!TryFindRimCell(lamp, glower, fessk, out IntVec3 rim))
            {
                return;
            }
            nextWatchOrderTick = Find.TickManager.TicksGame + 2500;
            Job job = JobMaker.MakeJob(watchJob, lamp, rim);
            fessk.jobs.StartJob(job, JobCondition.InterruptForced);
            if (first)
            {
                Messages.Message("RM_GreyLampWatcherMsg".Translate(lamp.LabelShort), new TargetInfo(rim, map), MessageTypeDefOf.NeutralEvent);
            }
        }

        private bool TryFindRimCell(Thing lamp, CompGlower glower, Pawn p, out IntVec3 cell)
        {
            float r = glower.GlowRadius;
            for (int i = 0; i < 30; i++)
            {
                float ang = Rand.Range(0f, 360f);
                float dist = r + Rand.Range(1f, 3f);
                IntVec3 c = lamp.Position + (Vector3Utility.FromAngleFlat(ang) * dist).ToIntVec3();
                if (c.InBounds(map) && c.Standable(map) && p.CanReach(c, PathEndMode.OnCell, Danger.Some))
                {
                    cell = c;
                    return true;
                }
            }
            cell = IntVec3.Invalid;
            return false;
        }

        // ── 75%: fresh scrape-sign at the light's edge ──────────────────────
        private void LayScrapeSign(Building lamp, CompGlower glower)
        {
            ThingDef filth = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_ScrapeLine");
            if (filth == null)
            {
                return;
            }
            float ang = Rand.Range(0f, 360f);
            Vector3 dir = Vector3Utility.FromAngleFlat(ang);
            Vector3 along = Vector3Utility.FromAngleFlat(ang + 90f);
            IntVec3 start = lamp.Position + (dir * (glower.GlowRadius + 2f)).ToIntVec3();
            IntVec3 first = IntVec3.Invalid;
            for (int i = -4; i <= 4; i++)
            {
                IntVec3 c = start + (along * i).ToIntVec3();
                if (c.InBounds(map) && c.Standable(map))
                {
                    FilthMaker.TryMakeFilth(c, map, filth);
                    if (!first.IsValid)
                    {
                        first = c;
                    }
                }
            }
            if (first.IsValid)
            {
                Messages.Message("RM_GreyLampScrapeMsg".Translate(lamp.LabelShort), new TargetInfo(first, map), MessageTypeDefOf.CautionInput);
            }
        }

        // ── 100%: the giant answers ─────────────────────────────────────────
        private bool TryAnswer(Building lamp)
        {
            ThingDef giantDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Reefback");
            JobDef breakJob = DefDatabase<JobDef>.GetNamedSilentFail("RM_BreakGlow");
            if (giantDef == null || breakJob == null)
            {
                return false;
            }
            Pawn giant = map.mapPawns.AllPawnsSpawned
                .FirstOrDefault(p => p.def == giantDef && p.Faction == null && !p.Downed && !p.Dead && p.CanReach(lamp, PathEndMode.Touch, Danger.Deadly));
            if (giant == null)
            {
                giant = WalkIn("RM_Reefback");
                if (giant == null)
                {
                    return false;
                }
            }
            if (!giant.CanReach(lamp, PathEndMode.Touch, Danger.Deadly))
            {
                // Inside a closed hull: the light is the ship's, and the ship is
                // never the target. The giant goes back to the murk.
                if (WalkedIn(giant))
                {
                    SendAway(giant);
                }
                return true;
            }
            giant.jobs.StartJob(JobMaker.MakeJob(breakJob, lamp), JobCondition.InterruptForced);
            Find.LetterStack.ReceiveLetter("RM_GreyLampGiantLabel".Translate(), "RM_GreyLampGiantText".Translate(lamp.LabelShort),
                LetterDefOf.ThreatSmall, new LookTargets(giant, lamp));
            return true;
        }

        private Pawn WalkIn(string kindName)
        {
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(kindName);
            if (kind == null || !RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 entry, map, CellFinder.EdgeRoadChance_Animal))
            {
                return null;
            }
            Pawn p = PawnGenerator.GeneratePawn(kind);
            GenSpawn.Spawn(p, entry, map);
            walkedIn.Add(p.thingIDNumber);
            return p;
        }

        // A giant that walked in only ever came for a lamp: once it is not
        // breaking one (done, or the lamp went dark), it goes back.
        private void SendHomeIdleGiants()
        {
            if (walkedIn.Count == 0)
            {
                return;
            }
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
            {
                if (p.def.defName != "RM_Reefback" || !walkedIn.Contains(p.thingIDNumber) || p.Downed || p.InMentalState)
                {
                    continue;
                }
                if (p.CurJobDef?.defName == "RM_BreakGlow" || (p.CurJob != null && p.CurJob.exitMapOnArrival))
                {
                    continue;
                }
                SendAway(p);
            }
        }

        public void SendAway(Pawn p)
        {
            if (p == null || !p.Spawned)
            {
                return;
            }
            if (RCellFinder.TryFindBestExitSpot(p, out IntVec3 spot, TraverseMode.ByPawn))
            {
                Job job = JobMaker.MakeJob(JobDefOf.Goto, spot);
                job.exitMapOnArrival = true;
                p.jobs.StartJob(job, JobCondition.InterruptForced);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref litTicks, "litTicks", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref watched, "watched", LookMode.Value);
            Scribe_Collections.Look(ref scraped, "scraped", LookMode.Value);
            Scribe_Collections.Look(ref answered, "answered", LookMode.Value);
            Scribe_Collections.Look(ref walkedIn, "walkedIn", LookMode.Value);
            Scribe_Values.Look(ref nextWatchOrderTick, "nextWatchOrderTick", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                litTicks = litTicks ?? new Dictionary<int, int>();
                watched = watched ?? new HashSet<int>();
                scraped = scraped ?? new HashSet<int>();
                answered = answered ?? new HashSet<int>();
                walkedIn = walkedIn ?? new HashSet<int>();
            }
        }
    }

    // Layer 1: drawn to the light — go near it, linger, wander off.
    public class RM_JobDriver_BaskInGlow : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => !(TargetThingA.TryGetComp<CompGlower>()?.Glows ?? false));
            Toil pick = ToilMaker.MakeToil("PickBaskCell");
            pick.initAction = delegate
            {
                CompGlower g = TargetThingA.TryGetComp<CompGlower>();
                float r = Mathf.Max(1.5f, (g?.GlowRadius ?? 3f) * 0.7f);
                IntVec3 c;
                if (!CellFinder.TryFindRandomReachableNearbyCell(TargetThingA.Position, pawn.Map, r,
                        TraverseParms.For(pawn), x => x.Standable(pawn.Map), null, out c))
                {
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                job.SetTarget(TargetIndex.B, c);
            };
            yield return pick;
            yield return Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.OnCell);
            yield return Toils_General.Wait(Rand.Range(600, 1500), TargetIndex.A);
        }
    }

    // Layer 2: the fessk at the rim — never enters the light, never attacks,
    // leaves the moment a colonist comes near.
    public class RM_JobDriver_WatchGlow : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => !(TargetThingA.TryGetComp<CompGlower>()?.Glows ?? false));
            this.FailOn(ColonistNear);
            yield return Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.OnCell);
            yield return Toils_General.Wait(5000, TargetIndex.A);
        }

        private bool ColonistNear()
        {
            if (!pawn.IsHashIntervalTick(60))
            {
                return false;
            }
            foreach (Pawn p in pawn.Map.mapPawns.FreeColonistsSpawned)
            {
                if (p.Position.InHorDistOf(pawn.Position, 6f))
                {
                    return true;
                }
            }
            return false;
        }
    }

    // Layer 3: the giant breaks the lamp. Not the ship, not the pawns: the only
    // thing this job ever damages is its target, and dowsing ends it.
    public class RM_JobDriver_BreakGlow : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => !(TargetThingA.TryGetComp<CompGlower>()?.Glows ?? false));
            // A walked-in giant is sent home by RM_MapComponent_GreyLampWatch's
            // next step once this job ends (never from inside a finish action).
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.WaitWith(TargetIndex.A, 300, true, false, false, TargetIndex.A);
            yield return Toils_General.Do(delegate
            {
                Thing lamp = TargetThingA;
                if (lamp != null && lamp.Spawned)
                {
                    Messages.Message("RM_GreyLampBrokenMsg".Translate(lamp.LabelShort), new TargetInfo(lamp.Position, lamp.Map), MessageTypeDefOf.NegativeEvent);
                    lamp.Kill();
                }
            });
        }
    }

    // ── Proof hooks for jawa/static_call (validation.py, grey_lamp_response) ──
    public static class RM_GreyLampProof
    {
        // Burn every lit worklight-class lamp on the current map `hours` hours
        // in one step; returns "lamps=.. maxLitHours=.. fessk=.. scrape=.. reefback=..".
        public static string ProofBurn(string hours)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_GreyLampWatch mc = map?.GetComponent<RM_MapComponent_GreyLampWatch>();
            if (mc == null)
            {
                return "no map";
            }
            if (map.Biome?.defName != RM_GreyCrust.GreyBiome)
            {
                return "not a Grey Sea map: " + map.Biome?.defName;
            }
            float h = float.TryParse(hours, out float parsed) ? parsed : 1f;
            int steps = Mathf.Max(1, Mathf.CeilToInt(h * 10f));
            int per = Mathf.RoundToInt(h * 2500f / steps);
            for (int i = 0; i < steps; i++)
            {
                mc.Advance(per);
            }
            List<Building> lamps = map.listerBuildings.allBuildingsColonist
                .Where(b => RM_MapComponent_GreyLampWatch.IsWorklightClass(b, out CompGlower g) && g.Glows).ToList();
            float maxH = lamps.Count == 0 ? 0f : lamps.Max(b => mc.LitTicksOf(b)) / 2500f;
            ThingDef scrape = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_ScrapeLine");
            return "lamps=" + lamps.Count
                + " maxLitHours=" + maxH.ToString("0.0")
                + " fessk=" + map.mapPawns.AllPawnsSpawned.Count(p => p.def.defName == "RM_Fessk")
                + " scrape=" + (scrape == null ? 0 : map.listerThings.ThingsOfDef(scrape).Count)
                + " reefback=" + map.mapPawns.AllPawnsSpawned.Count(p => p.def.defName == "RM_Reefback")
                + " breaking=" + map.mapPawns.AllPawnsSpawned.Count(p => p.CurJobDef?.defName == "RM_BreakGlow");
        }
    }
}
