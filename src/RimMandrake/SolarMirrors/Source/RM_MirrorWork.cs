using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.SolarMirrors
{
    // SOLAR_MIRRORS_BUILD_1: the data and jobs added to the core mirrors.
    //   §3.2 dust      RM_MirrorDustWeathersDef (which weathers dirty a mirror, how much it costs), the cleaning job
    //   §3.4 ancient   the repair job (one component + Construction) that frees a seized ancient mirror
    //   §5 E2          RM_MirrorApertureExtension: a building a beam passes through and under the roof behind it
    //   §5 E3          RM_CompHeliograph: flash a friendly settlement in range by day; opens vanilla comms

    /// <summary>Design §3.2: the weathers that dirty a mirror, by defName so a weather from an absent mod costs
    /// nothing. Numbers are PROVISIONAL. One def ships: RM_MirrorDust.</summary>
    public class RM_MirrorDustWeathersDef : Def
    {
        public List<string> weathers = new List<string>();
        public float maxLoss = 0.6f;    // PROVISIONAL: a fully dusty mirror keeps 40% of its reflectivity
        public float cleanAt = 0.25f;   // PROVISIONAL: dust at which a cleaning job is offered

        private static RM_MirrorDustWeathersDef cached;
        private static bool looked;
        private HashSet<WeatherDef> resolved;

        public static RM_MirrorDustWeathersDef Get
        {
            get
            {
                if (!looked)
                {
                    looked = true;
                    cached = DefDatabase<RM_MirrorDustWeathersDef>.GetNamedSilentFail("RM_MirrorDust");
                }
                return cached;
            }
        }

        public static float MaxLoss => Get?.maxLoss ?? 0.6f;
        public static float CleanAt => Get?.cleanAt ?? 0.25f;

        public static bool IsDusty(WeatherDef w)
        {
            RM_MirrorDustWeathersDef d = Get;
            if (w == null || d == null)
            {
                return false;
            }
            if (d.resolved == null)
            {
                d.resolved = new HashSet<WeatherDef>();
                foreach (string n in d.weathers)
                {
                    WeatherDef wd = DefDatabase<WeatherDef>.GetNamedSilentFail(n);
                    if (wd != null)
                    {
                        d.resolved.Add(wd);
                    }
                }
            }
            return d.resolved.Contains(w);
        }
    }

    /// <summary>Design §5 E2: a glazed aperture. A beam passes through it, and past it a roof no longer stops the
    /// beam (it is inside the room). PROVISIONAL choice between the design's "glass roof or glazed wall": a glazed
    /// wall, because vanilla roofs are not player-choosable defs.</summary>
    public class RM_MirrorApertureExtension : DefModExtension
    {
    }

    [StaticConstructorOnStartup]
    public static class RM_MirrorTex
    {
        public static readonly Texture2D Repair = ContentFinder<Texture2D>.Get("UI/Designators/Claim");
    }

    // ── cleaning (design §3.2) ──────────────────────────────────────────

    public class RM_WorkGiver_CleanMirror : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(pawn.Map);
            if (comp == null)
            {
                yield break;
            }
            IReadOnlyList<RM_CompMirror> list = comp.Mirrors;
            for (int k = 0; k < list.Count; k++)
            {
                if (list[k].NeedsCleaning && list[k].Orderable)
                {
                    yield return list[k].parent;
                }
            }
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(pawn.Map);
            return !RM_SolarMirrorsSettings.dustEnabled || comp == null || comp.MirrorCount == 0;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            RM_CompMirror m = t.TryGetComp<RM_CompMirror>();
            if (m == null || !m.Orderable || !(forced ? m.Dust > 0.01f : m.NeedsCleaning) || t.IsForbidden(pawn) || t.IsBurning())
            {
                return false;
            }
            return pawn.CanReserve(t, 1, -1, null, forced);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return HasJobOnThing(pawn, t, forced) ? JobMaker.MakeJob(RM_SolarMirrorsDefOf.RM_CleanMirror, t) : null;
        }
    }

    public class RM_JobDriver_CleanMirror : JobDriver
    {
        private Thing Mirror => job.targetA.Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            RM_CompMirror m = Mirror.TryGetComp<RM_CompMirror>();
            int ticks = m == null ? 300 : Mathf.Max(1, m.Props.cleanTicks);
            yield return Toils_General.Wait(ticks, TargetIndex.A)
                .FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch)
                .WithProgressBarToilDelay(TargetIndex.A);
            Toil done = ToilMaker.MakeToil("RM_CleanMirror");
            done.initAction = () => Mirror.TryGetComp<RM_CompMirror>()?.Clean();
            done.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return done;
        }
    }

    // ── repairing an ancient mirror (design §3.4) ───────────────────────

    public class RM_WorkGiver_RepairAncientMirror : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(pawn.Map);
            if (comp == null)
            {
                yield break;
            }
            IReadOnlyList<RM_CompMirror> list = comp.Mirrors;
            for (int k = 0; k < list.Count; k++)
            {
                if (list[k].RepairRequested && list[k].Orderable)
                {
                    yield return list[k].parent;
                }
            }
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(pawn.Map);
            return comp == null || comp.MirrorCount == 0;
        }

        private static Thing FindComponent(Pawn pawn)
        {
            return GenClosest.ClosestThingReachable(pawn.Position, pawn.Map, ThingRequest.ForDef(ThingDefOf.ComponentIndustrial),
                PathEndMode.ClosestTouch, TraverseParms.For(pawn), 9999f, t => !t.IsForbidden(pawn) && pawn.CanReserve(t));
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            RM_CompMirror m = t.TryGetComp<RM_CompMirror>();
            if (m == null || !m.RepairRequested || !m.Orderable || t.IsForbidden(pawn) || t.IsBurning())
            {
                return false;
            }
            if (!pawn.CanReserve(t, 1, -1, null, forced))
            {
                return false;
            }
            if (FindComponent(pawn) == null)
            {
                JobFailReason.Is("RM_SolarMirrors_Repair_NoComponent".Translate());
                return false;
            }
            return true;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (!HasJobOnThing(pawn, t, forced))
            {
                return null;
            }
            Job job = JobMaker.MakeJob(RM_SolarMirrorsDefOf.RM_RepairAncientMirror, t, FindComponent(pawn));
            job.count = 1;
            return job;
        }
    }

    public class RM_JobDriver_RepairAncientMirror : JobDriver
    {
        private Thing Mirror => job.targetA.Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed)
                   && pawn.Reserve(job.targetB, job, 1, 1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => Mirror.TryGetComp<RM_CompMirror>()?.RepairRequested != true);
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch)
                .FailOnDespawnedNullOrForbidden(TargetIndex.B);
            yield return Toils_Haul.StartCarryThing(TargetIndex.B, false, true);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            RM_CompMirror m = Mirror.TryGetComp<RM_CompMirror>();
            int ticks = m == null ? 1500 : Mathf.Max(1, Mathf.RoundToInt(m.Props.repairTicks * RM_SolarMirrorsSettings.reAimWorkMultiplier));
            yield return Toils_General.Wait(ticks, TargetIndex.A)
                .FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch)
                .WithProgressBarToilDelay(TargetIndex.A);
            Toil done = ToilMaker.MakeToil("RM_RepairAncientMirror");
            done.initAction = () =>
            {
                Thing carried = pawn.carryTracker.CarriedThing;
                if (carried == null || carried.def != ThingDefOf.ComponentIndustrial)
                {
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                carried.SplitOff(1).Destroy();
                Mirror.TryGetComp<RM_CompMirror>()?.FinishRepair();
            };
            done.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return done;
        }
    }

    // ── the heliograph (design §5 E3) ───────────────────────────────────

    public class RM_CompProperties_Heliograph : CompProperties
    {
        public int flashTicks = 300;     // PROVISIONAL
        public float minSource = 0.5f;   // the mirror must stand in at least this much direct sun

        public RM_CompProperties_Heliograph()
        {
            compClass = typeof(RM_CompHeliograph);
        }
    }

    /// <summary>Design §5 E3: by day, a colonist at a signal mirror in the sun flashes a friendly faction whose nearest
    /// settlement lies within reach (the settings range x daylight), which opens the vanilla comms dialog with that
    /// faction (Faction.TryOpenComms, the comms console's own route). At night, in shadow or out of range: nothing.</summary>
    public class RM_CompHeliograph : ThingComp
    {
        public RM_CompProperties_Heliograph Props => (RM_CompProperties_Heliograph)props;

        /// <summary>Null when it can flash now, else why not.</summary>
        public string WhyNot(out float rangeTiles)
        {
            rangeTiles = 0f;
            if (!RM_SolarMirrorsSettings.heliograph)
            {
                return "RM_SolarMirrors_Helio_Off".Translate();
            }
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(parent.Map);
            if (comp == null || !comp.TrySun(out Vector3 _, out float daylight))
            {
                return "RM_SolarMirrors_Helio_NoSun".Translate();
            }
            RM_CompMirror m = parent.GetComp<RM_CompMirror>();
            if (m != null && m.lastSource < Props.minSource && comp.SourceAt(m) < Props.minSource)
            {
                return "RM_SolarMirrors_Helio_Shadow".Translate();
            }
            rangeTiles = RM_MirrorKernel.HeliographRange(RM_SolarMirrorsSettings.heliographRange, daylight);
            return null;
        }

        public static IEnumerable<Faction> Reachable(Map map, float rangeTiles)
        {
            if (map == null || !map.Tile.Valid || Find.WorldObjects == null)
            {
                yield break;
            }
            HashSet<Faction> seen = new HashSet<Faction>();
            foreach (Settlement s in Find.WorldObjects.Settlements)
            {
                Faction f = s.Faction;
                if (f == null || f.IsPlayer || f.Hidden || f.defeated || f.temporary || !f.def.humanlikeFaction
                    || f.HostileTo(Faction.OfPlayer) || seen.Contains(f))
                {
                    continue;
                }
                if (s.Tile.Layer != map.Tile.Layer)
                {
                    continue;
                }
                if (Find.WorldGrid.ApproxDistanceInTiles(map.Tile, s.Tile) <= rangeTiles)
                {
                    seen.Add(f);
                    yield return f;
                }
            }
        }

        public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
        {
            foreach (FloatMenuOption o in base.CompFloatMenuOptions(selPawn))
            {
                yield return o;
            }
            if (parent.Faction != Faction.OfPlayer || selPawn == null || !selPawn.IsColonistPlayerControlled)
            {
                yield break;
            }
            string why = WhyNot(out float range);
            if (why != null)
            {
                yield return new FloatMenuOption("RM_SolarMirrors_Helio_Cannot".Translate(why), null);
                yield break;
            }
            if (selPawn.WorkTagIsDisabled(WorkTags.Social))
            {
                yield return new FloatMenuOption("RM_SolarMirrors_Helio_Cannot".Translate("RM_SolarMirrors_Helio_NoSocial".Translate()), null);
                yield break;
            }
            bool any = false;
            foreach (Faction f in Reachable(parent.Map, range))
            {
                any = true;
                Faction target = f;
                yield return new FloatMenuOption("RM_SolarMirrors_Helio_Flash".Translate(target.Name), () =>
                {
                    Job job = JobMaker.MakeJob(RM_SolarMirrorsDefOf.RM_FlashHeliograph, parent);
                    job.commTarget = target;
                    selPawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
                });
            }
            if (!any)
            {
                yield return new FloatMenuOption("RM_SolarMirrors_Helio_Cannot".Translate("RM_SolarMirrors_Helio_NoneInRange".Translate(range.ToString("0"))), null);
            }
        }
    }

    public class RM_JobDriver_FlashHeliograph : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => job.targetA.Thing.TryGetComp<RM_CompHeliograph>()?.WhyNot(out _) != null);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            RM_CompHeliograph h = job.targetA.Thing.TryGetComp<RM_CompHeliograph>();
            yield return Toils_General.Wait(h == null ? 300 : Mathf.Max(1, h.Props.flashTicks), TargetIndex.A)
                .FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch)
                .WithProgressBarToilDelay(TargetIndex.A);
            Toil open = ToilMaker.MakeToil("RM_FlashHeliograph");
            open.initAction = () =>
            {
                if (job.commTarget is Faction f && !f.HostileTo(Faction.OfPlayer))
                {
                    f.TryOpenComms(pawn);
                }
            };
            open.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return open;
        }
    }
}
