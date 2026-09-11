using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.GelatinousSlime
{
    public class CompProperties_GeneSeeker : CompProperties
    {
        // [INVENTED, spec §5c: "window ~1-2 days"] How long a marked cell
        // stays the right cell before the current moves on.
        public int markLifetimeTicks = 90000;

        // [INVENTED] The vulnerable walk's price, in work ticks on the body.
        public int extractWorkTicks = 4500;

        public CompProperties_GeneSeeker()
        {
            compClass = typeof(CompGeneSeeker);
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // RM_GeneSeeker — the three-state handheld (spec §5).
    //
    // Owner card, round 2, verbatim: "It is a machine you hold that tells you
    // WHERE you must go to extract (a scanner). Then you place it upon the
    // slime, and it expends itself sucking up just the right parts of the
    // slime, becoming an injectible. Then it is used up once used to inject."
    //
    // STATE 1 SCANNER   — this comp on RM_GeneSeeker with targetGene set.
    // STATE 2 EXTRACTOR — JobDriver_ExtractSlimeSample running on the marked
    //                     cell; the def swap happens when it finishes.
    // STATE 3 INJECTABLE — this comp on RM_GeneSeeker_Loaded, carrying the
    //                     target and the rolled rider.
    //
    // 🔑 THE WORLD LAYER IS A READOUT, NOT A SITE SPAWN, AND THAT IS A
    // DELIBERATE NARROWING. Spec §5c offered the long-range mineral scanner
    // precedent (CompLongRangeMineralScanner + site spawn) for "the primed
    // seeker names a world tile", and flagged: "🔴 Build-seat verification
    // owed on both comp names and the site-spawn wiring (never guess a field;
    // RimSage before XML)." The site-spawn wiring could NOT be verified
    // offline to the standard this repo requires, so what ships is the half
    // that could: the primed seeker reads Find.WorldGrid directly and NAMES
    // the nearest gelatinous-slime tile and its distance in its inspect
    // string. The player caravans there themselves. A quest-marker site spawn
    // remains available and unbuilt; it is an addition, not a correction.
    // ════════════════════════════════════════════════════════════════════
    public class CompGeneSeeker : ThingComp
    {
        private GeneDef targetGene;
        private GeneDef riderGene;

        private IntVec3 markedCell = IntVec3.Invalid;
        private int markedMapTile = -1;
        private int markExpiresTick = -1;

        // Cached world-tile readout so the inspect string does not walk the
        // planet every frame.
        private int cachedNearestTile = -1;
        private int cachedNearestDist = -1;
        private int cachedNearestAtTick = -1;

        public CompProperties_GeneSeeker Props
        {
            get { return (CompProperties_GeneSeeker)props; }
        }

        public GeneDef TargetGene { get { return targetGene; } }
        public GeneDef RiderGene { get { return riderGene; } }
        public bool Primed { get { return targetGene != null; } }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Defs.Look(ref targetGene, "targetGene");
            Scribe_Defs.Look(ref riderGene, "riderGene");
            Scribe_Values.Look(ref markedCell, "markedCell", IntVec3.Invalid);
            Scribe_Values.Look(ref markedMapTile, "markedMapTile", -1);
            Scribe_Values.Look(ref markExpiresTick, "markExpiresTick", -1);
        }

        public void SetLoad(GeneDef target, GeneDef rider)
        {
            targetGene = target;
            riderGene = rider;
        }

        // ────────────────────────────────────────────────────────────────
        public override string CompInspectStringExtra()
        {
            if (!Primed)
            {
                return "Not primed. Ask the archive for an entry.";
            }

            System.Text.StringBuilder sb = new System.Text.StringBuilder();
            sb.Append("Seeking: ").Append(targetGene.LabelCap);

            if (parent.def == SlimeDefs.GeneSeekerLoaded)
            {
                sb.Append("\nLoaded and perishing. Inject before it spoils.");
                return sb.ToString();
            }

            Map map = parent.MapHeld;
            if (map != null && map.Biome == SlimeDefs.GelatinousSlime)
            {
                RefreshMarkIfNeeded(map);
                if (markedCell.IsValid)
                {
                    sb.Append("\nExtraction site marked at ").Append(markedCell.ToString())
                      .Append(" (").Append(((markExpiresTick - Find.TickManager.TicksGame)
                                            .ToStringTicksToPeriod())).Append(" left).");
                }
                else
                {
                    sb.Append("\nNo current on this map carries it. Move to open slime.");
                }
            }
            else
            {
                RefreshWorldReadoutIfNeeded();
                if (cachedNearestTile >= 0)
                {
                    sb.Append("\nNearest reading body: ").Append(cachedNearestDist)
                      .Append(" tiles away. Caravan there to extract.");
                }
                else
                {
                    sb.Append("\nNo reading body found anywhere this scanner can hear.");
                }
            }
            return sb.ToString();
        }

        // ────────────────────────────────────────────────────────────────
        // THE MARK. "The primed seeker points to WHERE the current carrying
        // it will pass, with a countdown window" (spec §5c). Liquid slime only
        // — the currents run in the channels.
        // ────────────────────────────────────────────────────────────────
        private void RefreshMarkIfNeeded(Map map)
        {
            int now = Find.TickManager.TicksGame;
            bool stale = !markedCell.IsValid
                         || markedMapTile != map.Tile.tileId
                         || now >= markExpiresTick
                         || !markedCell.InBounds(map)
                         || map.terrainGrid.TerrainAt(markedCell) != SlimeDefs.SlimeLiquid;
            if (!stale)
            {
                return;
            }

            markedCell = IntVec3.Invalid;
            markedMapTile = map.Tile.tileId;
            markExpiresTick = now + Props.markLifetimeTicks;

            if (SlimeDefs.SlimeLiquid == null)
            {
                return;
            }
            // Bounded search rather than a whole-map scan: this runs from an
            // inspect string.
            for (int i = 0; i < 900; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (map.terrainGrid.TerrainAt(c) == SlimeDefs.SlimeLiquid && c.Standable(map))
                {
                    markedCell = c;
                    return;
                }
            }
        }

        private void RefreshWorldReadoutIfNeeded()
        {
            int now = Find.TickManager.TicksGame;
            if (cachedNearestAtTick > 0 && now - cachedNearestAtTick < 30000)
            {
                return;
            }
            cachedNearestAtTick = now;
            cachedNearestTile = -1;
            cachedNearestDist = -1;

            if (SlimeDefs.GelatinousSlime == null || Find.WorldGrid == null)
            {
                return;
            }
            PlanetTile from = parent.MapHeld != null ? parent.MapHeld.Tile : PlanetTile.Invalid;
            if (!from.Valid)
            {
                return;
            }

            PlanetLayer layer = from.Layer;
            List<Tile> tiles = layer.Tiles;
            int best = -1;
            int bestDist = int.MaxValue;
            for (int i = 0; i < tiles.Count; i++)
            {
                if (tiles[i] == null || tiles[i].PrimaryBiome != SlimeDefs.GelatinousSlime)
                {
                    continue;
                }
                PlanetTile candidate = new PlanetTile(i, layer);
                int d = Find.WorldGrid.TraversalDistanceBetween(from, candidate, false, bestDist);
                if (d >= 0 && d < bestDist)
                {
                    bestDist = d;
                    best = i;
                }
            }
            if (best >= 0)
            {
                cachedNearestTile = best;
                cachedNearestDist = bestDist;
            }
        }

        // ────────────────────────────────────────────────────────────────
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            if (parent.def == SlimeDefs.GeneSeekerLoaded)
            {
                yield break;
            }
            if (!parent.Spawned && parent.MapHeld == null)
            {
                yield break;
            }

            if (!Primed)
            {
                Command_Action prime = new Command_Action();
                prime.defaultLabel = "Ask the archive";
                prime.defaultDesc = "Choose which entry this seeker will look for. "
                                    + "The choice locks in and cannot be changed.";
                prime.icon = ContentFinder<Texture2D>.Get("UI/Commands/Rename", false);
                prime.action = delegate
                {
                    GeneArchiveDef archive = GeneArchiveDef.Active;
                    if (archive == null)
                    {
                        Messages.Message("No gene archive is loaded.", MessageTypeDefOf.RejectInput, false);
                        return;
                    }
                    Find.WindowStack.Add(new Dialog_GeneArchive(archive, delegate (GeneDef chosen)
                    {
                        targetGene = chosen;
                        riderGene = archive.RollRider();
                        markedCell = IntVec3.Invalid;
                        markExpiresTick = -1;
                    }));
                };
                yield return prime;
                yield break;
            }

            Map map = parent.MapHeld;
            Command_Action extract = new Command_Action();
            extract.defaultLabel = "Extract sample";
            extract.defaultDesc = "Send a colonist to carry this seeker to the marked "
                                  + "extraction site and hold it there while it drinks. "
                                  + "They will be standing on the body the whole time.";
            extract.icon = ContentFinder<Texture2D>.Get("UI/Commands/Install", false);
            if (map == null || map.Biome != SlimeDefs.GelatinousSlime)
            {
                extract.Disable("Not on a gelatinous slime map.");
            }
            else
            {
                RefreshMarkIfNeeded(map);
                if (!markedCell.IsValid)
                {
                    extract.Disable("No extraction site marked.");
                }
            }
            extract.action = delegate
            {
                StartExtraction(map);
            };
            yield return extract;
        }

        private void StartExtraction(Map map)
        {
            if (map == null || !markedCell.IsValid)
            {
                return;
            }
            JobDef jobDef = DefDatabase<JobDef>.GetNamedSilentFail("RM_ExtractSlimeSample");
            if (jobDef == null)
            {
                return;
            }

            Pawn chosen = null;
            float bestDist = float.MaxValue;
            List<Pawn> colonists = map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < colonists.Count; i++)
            {
                Pawn p = colonists[i];
                if (p.Downed || p.InMentalState)
                {
                    continue;
                }
                if (!p.CanReserveAndReach(parent, PathEndMode.ClosestTouch, Danger.Deadly))
                {
                    continue;
                }
                if (!p.CanReserveAndReach(markedCell, PathEndMode.OnCell, Danger.Deadly))
                {
                    continue;
                }
                float d = p.Position.DistanceToSquared(parent.PositionHeld);
                if (d < bestDist)
                {
                    bestDist = d;
                    chosen = p;
                }
            }

            if (chosen == null)
            {
                Messages.Message("No colonist can reach both the seeker and the extraction site.",
                                 MessageTypeDefOf.RejectInput, false);
                return;
            }

            Job job = JobMaker.MakeJob(jobDef, parent, markedCell);
            job.count = 1;
            chosen.jobs.TryTakeOrderedJob(job, JobTag.Misc);
        }

        public IntVec3 MarkedCell { get { return markedCell; } }
    }

    // ════════════════════════════════════════════════════════════════════
    // THE VULNERABLE WALK (spec §5c). "The carrying pawn walks to the cell and
    // places the seeker — the state-2 job runs its timer in the open on the
    // body, and the pawn walks home carrying the injectable it became."
    //
    // 🔑 THE PAWN IS EXPOSED THE WHOLE TIME AND NOTHING HERE EXEMPTS THEM.
    // MapComponent_SlimeExposure keeps applying and the hediff keeps ticking
    // while this job runs; that is the price the spec designed in, not an
    // oversight.
    // ════════════════════════════════════════════════════════════════════
    public class JobDriver_ExtractSlimeSample : JobDriver
    {
        private const TargetIndex SeekerInd = TargetIndex.A;
        private const TargetIndex SiteInd = TargetIndex.B;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(SeekerInd), job, 1, 1, null, errorOnFailed)
                && pawn.Reserve(job.GetTarget(SiteInd), job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedNullOrForbidden(SeekerInd);

            yield return Toils_Goto.GotoThing(SeekerInd, PathEndMode.ClosestTouch)
                                   .FailOnDespawnedNullOrForbidden(SeekerInd);
            yield return Toils_Haul.StartCarryThing(SeekerInd);
            yield return Toils_Goto.GotoCell(SiteInd, PathEndMode.OnCell);

            int workTicks = 4500;
            Thing carried = job.GetTarget(SeekerInd).Thing;
            if (carried != null)
            {
                CompGeneSeeker comp = carried.TryGetComp<CompGeneSeeker>();
                if (comp != null && comp.Props != null)
                {
                    workTicks = comp.Props.extractWorkTicks;
                }
            }

            Toil drink = Toils_General.Wait(workTicks, SiteInd);
            drink.WithProgressBarToilDelay(SiteInd);
            drink.FailOnCannotTouch(SiteInd, PathEndMode.OnCell);
            drink.AddFinishAction(delegate
            {
                // 🔴 FINISH ACTIONS RUN ON ANY CLEANUP, NOT ONLY ON SUCCESS —
                // a draft, a cancel or a downing one tick after arrival would
                // otherwise complete the extraction for free. The ticksLeft
                // check is what makes this a completion handler.
                if (drink.actor == null || drink.actor.jobs == null) return;
                if (drink.actor.jobs.curDriver != this) return;
                if (ticksLeftThisToil > 0) return;
                CompleteExtraction();
            });
            yield return drink;
        }

        private void CompleteExtraction()
        {
            try
            {
                Thing seeker = pawn.carryTracker.CarriedThing;
                if (seeker == null)
                {
                    return;
                }
                CompGeneSeeker comp = seeker.TryGetComp<CompGeneSeeker>();
                if (comp == null || !comp.Primed)
                {
                    return;
                }
                if (SlimeDefs.GeneSeekerLoaded == null)
                {
                    return;
                }

                GeneDef target = comp.TargetGene;
                GeneDef rider = comp.RiderGene;
                IntVec3 pos = pawn.Position;
                Map map = pawn.Map;

                // 🔑 THE DEF SWAP. "One item transforming" is fiction the
                // engine does not do; two ThingDefs swapped by this job is the
                // honest build of it (spec §5a).
                pawn.carryTracker.DestroyCarriedThing();

                Thing loaded = ThingMaker.MakeThing(SlimeDefs.GeneSeekerLoaded);
                CompGeneSeeker loadedComp = loaded.TryGetComp<CompGeneSeeker>();
                if (loadedComp != null)
                {
                    loadedComp.SetLoad(target, rider);
                }
                if (map != null)
                {
                    GenPlace.TryPlaceThing(loaded, pos, map, ThingPlaceMode.Near);
                    if (SlimeDefs.SlimeSmear != null)
                    {
                        FilthMaker.TryMakeFilth(pos, map, SlimeDefs.SlimeSmear, 2);
                    }
                    if (SlimeSettings.flavorEntryRecorded)
                    {
                        MoteMaker.ThrowText(pos.ToVector3Shifted(), map, "Entry retrieved", 3.5f);
                    }
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake.GelatinousSlime] extraction completion failed: " + e);
            }
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // INJECT -> COMA -> THE RACE (spec §5d).
    //
    // 1. The genes land IMMEDIATELY — target plus the hidden rider — using
    //    exactly the verified primitive: Pawn_GeneTracker.AddGene per gene
    //    (edible_genepack_native_mechanism.md, IL-cited: zero new gene-storage
    //    code). ENDOGENES, per P8: heritable, "the bloodline is a decision
    //    made one coma at a time".
    // 2. The coma: vanilla XenogerminationComa, plus RM_Slimification at
    //    stage 2 with the FAST CLOCK (~3 days, not 7).
    // 3. THE RACE: a friend must administer the antidote before dissolution.
    //    🔴 A LONE PAWN CANNOT DO THIS AND LIVE. That is the social mechanic
    //    the owner specced ("unless they have a friend nearby") and it ships
    //    as-is: no self-administration while comatose, no timer pause. The
    //    one-warning dialog for solo colonies is below.
    // ════════════════════════════════════════════════════════════════════
    public class CompTargetEffect_InjectSlimeGenes : CompTargetEffect
    {
        // [INVENTED, spec §5d] Injection puts the patient at stage 2.
        private const float InjectedStartSeverity = 0.4f;

        public override void DoEffectOn(Pawn user, Thing target)
        {
            Pawn patient = target as Pawn;
            if (patient == null || patient.Dead)
            {
                return;
            }
            CompGeneSeeker comp = parent.TryGetComp<CompGeneSeeker>();
            if (comp == null || !comp.Primed)
            {
                return;
            }
            if (!ModsConfig.BiotechActive || patient.genes == null)
            {
                Messages.Message("Genes cannot be carried by this creature.",
                                 MessageTypeDefOf.RejectInput, false);
                return;
            }

            try
            {
                // P8 — endogenes, not xenogenes: heritable.
                if (comp.TargetGene != null)
                {
                    patient.genes.AddGene(comp.TargetGene, false);
                }
                if (comp.RiderGene != null)
                {
                    patient.genes.AddGene(comp.RiderGene, false);
                }

                if (SlimeDefs.XenogerminationComa != null
                    && !patient.health.hediffSet.HasHediff(SlimeDefs.XenogerminationComa))
                {
                    patient.health.AddHediff(SlimeDefs.XenogerminationComa);
                }

                // The fast clock underneath the coma.
                if (SlimeDefs.Slimification != null)
                {
                    Hediff slim = patient.health.hediffSet.GetFirstHediffOfDef(SlimeDefs.Slimification);
                    if (slim == null)
                    {
                        slim = patient.health.AddHediff(SlimeDefs.Slimification);
                    }
                    if (slim != null && slim.Severity < InjectedStartSeverity)
                    {
                        slim.Severity = InjectedStartSeverity;
                    }
                    HediffComp_Slimification sc = SlimeUtility.GetSlimification(patient);
                    if (sc != null)
                    {
                        sc.StartFastClock();
                    }
                }

                // P7 — the Slime-marked penalty, one point per entry taken.
                if (SlimeDefs.SlimeMarked != null)
                {
                    Hediff marked = patient.health.hediffSet.GetFirstHediffOfDef(SlimeDefs.SlimeMarked);
                    if (marked == null)
                    {
                        patient.health.AddHediff(SlimeDefs.SlimeMarked);
                    }
                    else
                    {
                        marked.Severity += 1f;
                    }
                }

                Find.LetterStack.ReceiveLetter(
                    "Injected",
                    patient.LabelShortCap + " has taken "
                    + (comp.TargetGene != null ? comp.TargetGene.LabelCap.ToString() : "an entry")
                    + " and whatever came with it. They are in a xenogermination coma and "
                    + "converting fast. Someone else must administer a slime antidote before "
                    + "the conversion finishes — they cannot do it themselves.",
                    LetterDefOf.ThreatBig, patient);

                WarnIfNobodyCanSave(patient);

                parent.Destroy();
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.GelatinousSlime] injection failed: " + e);
            }
        }

        // "Solo-colony players get one warning dialog at injection [INVENTED:
        // the warning]." Shown after the fact rather than before, because
        // CompUsable's job has already run by the time this comp fires — the
        // honest shape is a warning the player cannot miss, not a prompt this
        // comp is not positioned to ask.
        private static void WarnIfNobodyCanSave(Pawn patient)
        {
            Map map = patient.MapHeld;
            if (map == null)
            {
                return;
            }
            List<Pawn> colonists = map.mapPawns.FreeColonistsSpawned;
            int able = 0;
            for (int i = 0; i < colonists.Count; i++)
            {
                if (colonists[i] != patient && !colonists[i].Downed)
                {
                    able++;
                }
            }
            if (able == 0)
            {
                Find.WindowStack.Add(new Dialog_MessageBox(
                    "There is nobody here to administer the antidote.\n\n"
                    + patient.LabelShortCap + " is comatose and converting. A comatose "
                    + "patient cannot dose themselves, and the clock does not pause. "
                    + "Unless someone reaches them in time, they will be returned to the "
                    + "flow in their bed.",
                    "OK"));
            }
        }
    }
}
