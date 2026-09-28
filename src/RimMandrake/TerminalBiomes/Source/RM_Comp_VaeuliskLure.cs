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
}
