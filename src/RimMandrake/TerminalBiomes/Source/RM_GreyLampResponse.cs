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
    // is never answered — "never the ship" — but is re-checked, so a hull left
    // open later is. A failed or interrupted answer retries after a cooldown
    // (GREY_LAMP_ANSWER_RETRY_1).
    public class RM_MapComponent_GreyLampWatch : MapComponent
    {
        public const int Interval = 250;

        private readonly LampWatchBook lamps = new LampWatchBook();
        private Dictionary<int, int> litTicks { get { return lamps.Lit; } }
        private HashSet<int> watched { get { return lamps.Watched; } }
        private HashSet<int> walkedIn = new HashSet<int>();
        private HashSet<int> warnedWatch = new HashSet<int>(); // lamps whose watcher warning was actually delivered
        private int nextWatchOrderTick;
        // GREY_LAMP_ANSWER_RETRY_1: an answer is only final when the lamp is broken (it is then Killed, and the burn
        // book forgets it). Until then: lamp id -> the giant sent (thingIDNumber), and lamp id -> the tick a failed or
        // interrupted answer may be retried.
        private Dictionary<int, int> dispatched = new Dictionary<int, int>();
        private Dictionary<int, int> retryAfter = new Dictionary<int, int>();
        // PROVISIONAL (auto-decided 2026-10-09, GREY_LAMP_ANSWER_RETRY_1): a failed answer retries after 6 in-game hours.
        public const int AnswerRetryCooldownTicks = 6 * 2500;

        public RM_MapComponent_GreyLampWatch(Map map) : base(map)
        {
        }

        public static int ThresholdTicks => LampWatchBook.ThresholdTicks(RM_TerminalBiomesSettings.greyLampGiantBurnHours);

        public static bool IsWorklightClass(Thing t, out CompGlower glower)
        {
            glower = t.TryGetComp<CompGlower>();
            return glower != null
                && t.Faction == Faction.OfPlayer
                && t.TryGetComp<CompPowerTrader>() != null       // never a torch or brazier
                && glower.GlowRadius >= RM_TerminalBiomesSettings.greyLampGiantMinRadius;
        }

        public int LitTicksOf(Thing t) => t != null ? lamps.LitTicksOf(t.thingIDNumber) : 0;

        public bool WalkedIn(Pawn p) => p != null && walkedIn.Contains(p.thingIDNumber);

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % Interval != 0)
            {
                return;
            }
            if (!RM_GreyCrust.IsGreyMap(map))
            {
                return;
            }
            if (!RM_TerminalBiomesSettings.GreyLampWatcherActive && !RM_TerminalBiomesSettings.GreyLampGiantActive)
            {
                // Reset the whole burn book: the kernel only forgets latches of lamps it finds in Lit,
                // so clearing Lit alone would strand Watched/Scraped/Answered across a re-enable.
                lamps.Lit.Clear();
                lamps.Watched.Clear();
                lamps.Scraped.Clear();
                lamps.Answered.Clear();
                warnedWatch.Clear();
                dispatched.Clear();
                retryAfter.Clear();
                return;
            }
            Advance(Interval);
        }

        public void Advance(int ticks)
        {
            var buildings = new Dictionary<int, Building>();
            var glowers = new Dictionary<int, CompGlower>();
            var litNow = new List<int>();
            foreach (Building b in map.listerBuildings.allBuildingsColonist.ToList())
            {
                if (!IsWorklightClass(b, out CompGlower glower) || !glower.Glows)
                {
                    continue;
                }
                buildings[b.thingIDNumber] = b;
                glowers[b.thingIDNumber] = glower;
                litNow.Add(b.thingIDNumber);
            }
            lamps.Advance(litNow, ticks, ThresholdTicks, RM_TerminalBiomesSettings.GreyLampWatcherActive, RM_TerminalBiomesSettings.GreyLampGiantActive,
                id => TryWatch(buildings[id], glowers[id]), id => LayScrapeSign(buildings[id], glowers[id]), id => TryAnswer(buildings[id]));
            PruneAnswerState();
            SendHomeIdleGiants();
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
            watched.Add(lamp.thingIDNumber); // the walk-in latch; the warning has its own latch below
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
            if (warnedWatch.Add(lamp.thingIDNumber))
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
        // Returns true only to latch the lamp as answered for good, which no longer happens: a running break job is
        // waited on, a failed or interrupted one is retried after a cooldown, and success removes the lamp itself.
        private bool TryAnswer(Building lamp)
        {
            ThingDef giantDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Reefback");
            JobDef breakJob = DefDatabase<JobDef>.GetNamedSilentFail("RM_BreakGlow");
            if (giantDef == null || breakJob == null)
            {
                return false;
            }
            int id = lamp.thingIDNumber;
            int now = Find.TickManager.TicksGame;
            if (dispatched.TryGetValue(id, out int giantId))
            {
                Pawn sent = map.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.thingIDNumber == giantId);
                if (sent != null && sent.CurJobDef == breakJob && sent.CurJob.targetA.Thing == lamp)
                {
                    return false; // on its way: wait
                }
                dispatched.Remove(id); // interrupted, killed, or gave up, and the lamp still burns
                retryAfter[id] = now + AnswerRetryCooldownTicks;
                return false;
            }
            if (retryAfter.TryGetValue(id, out int after) && now < after)
            {
                return false;
            }
            if (!ReachableFromOutside(lamp))
            {
                // Inside a closed hull: the light is the ship's, and the ship is never the target. Nothing walks in;
                // checked again each step, so a hull left open later is answered.
                return false;
            }
            Pawn giant = map.mapPawns.AllPawnsSpawned
                .FirstOrDefault(p => p.def == giantDef && p.Faction == null && !p.Downed && !p.Dead && p.CurJobDef != breakJob && p.CanReach(lamp, PathEndMode.Touch, Danger.Deadly));
            if (giant == null)
            {
                giant = WalkIn("RM_Reefback");
                if (giant == null)
                {
                    retryAfter[id] = now + AnswerRetryCooldownTicks;
                    return false;
                }
            }
            if (!giant.CanReach(lamp, PathEndMode.Touch, Danger.Deadly))
            {
                if (WalkedIn(giant))
                {
                    SendAway(giant);
                }
                retryAfter[id] = now + AnswerRetryCooldownTicks;
                return false;
            }
            giant.jobs.StartJob(JobMaker.MakeJob(breakJob, lamp), JobCondition.InterruptForced);
            if (giant.CurJobDef != breakJob)
            {
                retryAfter[id] = now + AnswerRetryCooldownTicks; // the job failed at once
                return false;
            }
            dispatched[id] = giant.thingIDNumber;
            Find.LetterStack.ReceiveLetter("RM_GreyLampGiantLabel".Translate(), "RM_GreyLampGiantText".Translate(lamp.LabelShort),
                LetterDefOf.ThreatSmall, new LookTargets(giant, lamp));
            return false;
        }

        /// <summary>A door-less animal path from the map edge to a cell beside the lamp.</summary>
        private bool ReachableFromOutside(Building lamp)
        {
            TraverseParms tp = TraverseParms.For(TraverseMode.NoPassClosedDoors, Danger.Deadly);
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(lamp))
            {
                if (c.InBounds(map) && c.Standable(map) && map.reachability.CanReachMapEdge(c, tp))
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>Drop retry state of lamps the burn book has forgotten (dark, broken, gone).</summary>
        private void PruneAnswerState()
        {
            if (dispatched.Count == 0 && retryAfter.Count == 0)
            {
                return;
            }
            foreach (int k in dispatched.Keys.ToList())
            {
                if (!lamps.Lit.ContainsKey(k)) dispatched.Remove(k);
            }
            foreach (int k in retryAfter.Keys.ToList())
            {
                if (!lamps.Lit.ContainsKey(k)) retryAfter.Remove(k);
            }
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
            Scribe_Collections.Look(ref lamps.Lit, "litTicks", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref lamps.Watched, "watched", LookMode.Value);
            Scribe_Collections.Look(ref lamps.Scraped, "scraped", LookMode.Value);
            Scribe_Collections.Look(ref lamps.Answered, "answered", LookMode.Value);
            Scribe_Collections.Look(ref walkedIn, "walkedIn", LookMode.Value);
            Scribe_Values.Look(ref nextWatchOrderTick, "nextWatchOrderTick", 0);
            Scribe_Collections.Look(ref warnedWatch, "warnedWatch", LookMode.Value);
            Scribe_Collections.Look(ref dispatched, "answerDispatched", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref retryAfter, "answerRetryAfter", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                lamps.Lit = lamps.Lit ?? new Dictionary<int, int>();
                lamps.Watched = lamps.Watched ?? new HashSet<int>();
                lamps.Scraped = lamps.Scraped ?? new HashSet<int>();
                lamps.Answered = lamps.Answered ?? new HashSet<int>();
                walkedIn = walkedIn ?? new HashSet<int>();
                warnedWatch = warnedWatch ?? new HashSet<int>();
                dispatched = dispatched ?? new Dictionary<int, int>();
                retryAfter = retryAfter ?? new Dictionary<int, int>();
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
            this.FailOn(() => !RM_TerminalBiomesSettings.GreyLampGiantActive); // switched off mid-job: stand down
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
            if (!RM_GreyCrust.IsGreyMap(map))
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
