using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_DANGER_LIGHTWEB_1 §D4c — "spawns as a plant-like dormant thing
    // carrying the false glower; swaps to pawn on proximity/harvest-job
    // start." The reveal-swap is the one novel mechanism the item calls out.
    //
    // No JobDriver_Harvest patch exists in this assembly to detect "harvest
    // job started" directly. A pawn cannot start a harvest job on this thing
    // without first walking up to it, so a proximity check on CompTickLong
    // fires at essentially the same moment a harvest attempt would begin,
    // and it ALSO covers a pawn who merely walks past — which is correct for
    // an ambush predator, not a gap in the spec's "proximity/harvest-job
    // start" (an "or", not an "and").
    //
    // This attaches to a ThingDef parented on PlantBase, and CLAUDE.md's
    // plant-ticker law means Plant never calls Tick() — only TickLong(). The
    // check runs on CompTickLong with no manual interval gate on top: the
    // engine's own Long-ticker cadence (TickLongInterval) already throttles
    // it, so stacking a countdown on top would either be redundant or (if
    // decremented once per Long-tick call rather than per tick) effectively
    // disable the check for a day of ticks — the exact trap CLAUDE.md warns
    // against.
    //
    // The tell (design D4b, "no breathing pulse... every living lamp in the
    // biome breathes"): this comp attaches to a ThingDef whose <comps> carry
    // a plain CompProperties_Glower and deliberately NO
    // RM_Comp_WarblingGlow — the steady glow IS the tell, read structurally
    // rather than merely described. Thessmoss-ring dressing (design D4b) is
    // OWED, not built: no thessmoss ThingDef exists anywhere in this repo
    // (checked this pass) for the reveal to kill a ring of.
    public class RM_CompProperties_VaeuliskLure : CompProperties
    {
        public RM_CompProperties_VaeuliskLure()
        {
            compClass = typeof(RM_Comp_VaeuliskLure);
        }

        // How close a pawn must come before the disguise drops.
        public float revealRadius = 1.9f;

        // defName of the PawnKindDef the lure becomes. Soft lookup at reveal
        // time (never at load), same posture RM_CompEmergentSpawnOnDestroy
        // already uses in this repo for a species-mod-agnostic spawn.
        public string revealPawnKindDefName = "RM_Vaulisk";

        // "drag two cells toward the dark" (design D4b) — the revealed pawn
        // spawns this many cells off the lure's own position, toward the
        // nearest darker cell it can find, rather than in the exact spot the
        // plant stood. A literal forced-teleport of the DISCOVERING pawn is
        // deliberately not attempted: with no live testing permitted on this
        // item, moving another agent's pawn out from under its own job/path
        // state is the riskier half of this beat and is left for a session
        // with the owner watching, per this repo's flyer-testing precedent.
        public int dragCells = 2;
    }

    public class RM_Comp_VaeuliskLure : ThingComp
    {
        private bool revealed;

        public RM_CompProperties_VaeuliskLure Props => (RM_CompProperties_VaeuliskLure)props;

        // VAULISK_LURE_REVEAL_TRIGGER_1: live lures per map, for the quick proximity check and the job-start trigger.
        internal static readonly Dictionary<Map, HashSet<RM_Comp_VaeuliskLure>> Live = new Dictionary<Map, HashSet<RM_Comp_VaeuliskLure>>();

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!Live.TryGetValue(parent.Map, out var set))
            {
                Live[parent.Map] = set = new HashSet<RM_Comp_VaeuliskLure>();
            }
            set.Add(this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            if (map != null && Live.TryGetValue(map, out var set))
            {
                set.Remove(this);
                if (set.Count == 0) Live.Remove(map);
            }
        }

        /// <summary>The quick check (RM_MapComponent_VauliskWatch) and the job-start trigger land here.</summary>
        public void TryRevealNow(Pawn discoverer)
        {
            if (revealed || !parent.Spawned || !RM_TerminalBiomesSettings.VauliskActive)
            {
                return;
            }
            Pawn d = discoverer ?? FindApproachingPawn(Props.revealRadius);
            if (d != null)
            {
                Reveal(Props, d);
            }
        }

        public override void CompTickLong()
        {
            if (revealed || !parent.Spawned)
            {
                return;
            }
            if (!RM_TerminalBiomesSettings.VauliskActive)
            {
                return; // mod option: the vaulisk disguise disabled
            }

            RM_CompProperties_VaeuliskLure p = Props;
            Pawn discoverer = FindApproachingPawn(p.revealRadius);
            if (discoverer != null)
            {
                Reveal(p, discoverer);
            }
        }

        private Pawn FindApproachingPawn(float radius)
        {
            Map map = parent.Map;
            float radiusSq = radius * radius;
            System.Collections.Generic.IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Dead || p.RaceProps == null)
                {
                    continue;
                }
                if ((p.Position - parent.Position).LengthHorizontalSquared <= radiusSq)
                {
                    return p;
                }
            }
            return null;
        }

        private void Reveal(RM_CompProperties_VaeuliskLure p, Pawn discoverer)
        {
            revealed = true;
            Map map = parent.Map;
            IntVec3 origin = parent.Position;

            PawnKindDef kindDef = DefDatabase<PawnKindDef>.GetNamedSilentFail(p.revealPawnKindDefName);
            if (kindDef == null)
            {
                parent.Destroy(DestroyMode.Vanish);
                return;
            }

            IntVec3 spawnCell = FindDragCell(origin, map, p.dragCells);
            parent.Destroy(DestroyMode.Vanish);

            Pawn vaulisk = PawnGenerator.GeneratePawn(kindDef);
            GenSpawn.Spawn(vaulisk, spawnCell, map);
            if (vaulisk.mindState != null)
            {
                vaulisk.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Manhunter, forceWake: true);
            }
            if (discoverer != null && discoverer.Spawned && vaulisk.jobs != null)
            {
                Job attack = JobMaker.MakeJob(JobDefOf.AttackMelee, discoverer);
                vaulisk.jobs.StartJob(attack, JobCondition.InterruptForced);
            }

            Messages.Message("RM_VauliskRevealed".Translate(), new TargetInfo(spawnCell, map), MessageTypeDefOf.ThreatBig);
        }

        // Picks the darkest standable cell within dragCells of origin, falling
        // back to origin itself if nothing better is found — "toward the
        // dark" per design D4b, using the map's own GlowGrid rather than a
        // hardcoded direction.
        private static IntVec3 FindDragCell(IntVec3 origin, Map map, int dragCells)
        {
            IntVec3 best = origin;
            float bestGlow = map.glowGrid.GroundGlowAt(origin);
            foreach (IntVec3 c in GenRadial.RadialCellsAround(origin, dragCells, useCenter: false))
            {
                if (!c.InBounds(map) || !c.Standable(map))
                {
                    continue;
                }
                float glow = map.glowGrid.GroundGlowAt(c);
                if (glow < bestGlow)
                {
                    bestGlow = glow;
                    best = c;
                }
            }
            return best;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref revealed, "revealed", false);
        }
    }

    /// <summary>VAULISK_LURE_REVEAL_TRIGGER_1: the long-tick check alone (every 2000 ticks) let a pawn walk past, and a
    /// harvest started on the lure was never seen. This checks proximity every QuickIntervalTicks and reveals on any
    /// job a pawn starts that targets the lure (harvest, cut, haul...), deferred one tick so the job tracker is not
    /// mid-StartJob when the plant is destroyed. Off with vauliskQuickReveal: only the long-tick check runs.</summary>
    public class RM_MapComponent_VauliskWatch : MapComponent
    {
        // PROVISIONAL (auto-decided 2026-10-09, VAULISK_LURE_REVEAL_TRIGGER_1): a proximity check once a second.
        public const int QuickIntervalTicks = 60;

        internal static readonly List<KeyValuePair<RM_Comp_VaeuliskLure, Pawn>> PendingJobReveals = new List<KeyValuePair<RM_Comp_VaeuliskLure, Pawn>>();

        public RM_MapComponent_VauliskWatch(Map map) : base(map)
        {
            // A map object from a previous game in this session is never removed explicitly: drop dead keys here.
            var dead = new List<Map>();
            foreach (Map m in RM_Comp_VaeuliskLure.Live.Keys) if (m == null || m.Disposed || Find.Maps == null || !Find.Maps.Contains(m)) dead.Add(m);
            foreach (Map m in dead) RM_Comp_VaeuliskLure.Live.Remove(m);
        }

        public override void MapRemoved()
        {
            base.MapRemoved();
            RM_Comp_VaeuliskLure.Live.Remove(map);
        }

        public override void MapComponentTick()
        {
            if (!RM_TerminalBiomesSettings.vauliskQuickReveal)
            {
                return;
            }
            if (PendingJobReveals.Count > 0)
            {
                for (int i = PendingJobReveals.Count - 1; i >= 0; i--)
                {
                    var kv = PendingJobReveals[i];
                    if (kv.Key?.parent?.Map == map)
                    {
                        PendingJobReveals.RemoveAt(i);
                        kv.Key.TryRevealNow(kv.Value != null && kv.Value.Spawned ? kv.Value : null);
                    }
                    else if (kv.Key?.parent == null || !kv.Key.parent.Spawned)
                    {
                        PendingJobReveals.RemoveAt(i);
                    }
                }
            }
            if (!map.IsHashIntervalTick(QuickIntervalTicks)
                || !RM_Comp_VaeuliskLure.Live.TryGetValue(map, out var set) || set.Count == 0)
            {
                return;
            }
            foreach (RM_Comp_VaeuliskLure lure in new List<RM_Comp_VaeuliskLure>(set))
            {
                lure.TryRevealNow(null);
            }
        }
    }

    [HarmonyPatch(typeof(Pawn_JobTracker), nameof(Pawn_JobTracker.StartJob))]
    public static class RM_Patch_VauliskJobStart
    {
        public static void Postfix(Job newJob, Pawn ___pawn)
        {
            if (newJob == null || ___pawn == null || !RM_TerminalBiomesSettings.vauliskQuickReveal)
            {
                return;
            }
            if (!(newJob.targetA.Thing is Plant plant) || !plant.Spawned)
            {
                return;
            }
            RM_Comp_VaeuliskLure lure = plant.GetComp<RM_Comp_VaeuliskLure>();
            if (lure != null)
            {
                RM_MapComponent_VauliskWatch.PendingJobReveals.Add(new KeyValuePair<RM_Comp_VaeuliskLure, Pawn>(lure, ___pawn));
            }
        }
    }
}
