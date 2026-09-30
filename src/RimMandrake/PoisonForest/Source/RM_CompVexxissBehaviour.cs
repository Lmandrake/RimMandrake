using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.PoisonForest
{
    // One water-terrain swap row: <li><from>WaterShallow</from><to>ToxicWaterShallow</to></li>
    public class RM_TerrainSwap
    {
        public TerrainDef from;
        public TerrainDef to;
    }

    public class RM_CompProperties_VexxissBehaviour : CompProperties
    {
        // Fire warden
        public float fireScanRadius = 14f;
        public int fireScanIntervalTicks = 250;
        public float igniterChaseRadius = 30f;
        public int attackJobExpiryTicks = 2500;

        // Poisons water on touch
        public int waterCheckIntervalTicks = 60;
        public float waterPoisonRadius = 1.5f;
        public List<RM_TerrainSwap> waterSwaps = new List<RM_TerrainSwap>();

        public RM_CompProperties_VexxissBehaviour()
        {
            compClass = typeof(RM_CompVexxissBehaviour);
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // CAULDRON_MECHANICS_BUILD_1 part 5 — the vexxiss behaviours that have a
    // real seam today. A pawn comp (pawns tick Normal, so CompTick fires).
    //
    // FIRE WARDEN. Every fireScanIntervalTicks an awake, able vexxiss looks for
    // the nearest free-standing Fire (parent == null, the same filter vanilla's
    // JobDriver_BeatFire uses) within fireScanRadius that it can reach.
    //   - If that fire's Fire.instigator is a live pawn in reach (not itself,
    //     not of its own faction), it attacks them first: a vanilla AttackMelee
    //     job, killIncappedTarget false, bounded by attackJobExpiryTicks.
    //   - Otherwise it smothers the fire with vanilla's BeatFire job. An animal
    //     only owns a beat-fire verb when its race sets
    //     giveNonToolUserBeatFireVerb (Pawn_NativeVerbs.CheckCreateVerbProperties),
    //     which RM_Vexxiss's race now does.
    //   Gas ignition is part 3 (no vent gas exists yet); when it does, a gas
    //   fire is still a Fire and this code covers it unchanged.
    //
    // POISONS WATER ON TOUCH. Every waterCheckIntervalTicks, if the vexxiss is
    // standing on a water terrain named in waterSwaps, that cell and every cell
    // within waterPoisonRadius whose terrain is a swap "from" becomes the swap
    // "to" (vanilla toxic-water terrains — the same TerrainGrid.SetTerrain swap
    // Odyssey's own TileMutatorWorker_ToxicLake does). Terrain-level, not a
    // FlowWorks LiquidDef: plain map water is vanilla terrain, not a FlowWorks
    // liquid cell.
    //
    // NOT BUILT (no seam yet): inhaling a vent to pause its production, and
    // prying at gas-tap scaffolds — both need part 3's vent and scaffold defs.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompVexxissBehaviour : ThingComp
    {
        public RM_CompProperties_VexxissBehaviour Props => (RM_CompProperties_VexxissBehaviour)props;

        private Pawn Pawn => parent as Pawn;

        public override void CompTick()
        {
            base.CompTick();
            Pawn pawn = Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead) return;

            if (RM_PoisonForestSettings.vexxissPoisonsWater && pawn.IsHashIntervalTick(Props.waterCheckIntervalTicks))
                PoisonWaterAround(pawn);

            if (RM_PoisonForestSettings.vexxissFireWardenEnabled && pawn.IsHashIntervalTick(Props.fireScanIntervalTicks))
                TryWardFire(pawn);
        }

        // ── poisons water on touch ──────────────────────────────────────
        private void PoisonWaterAround(Pawn pawn)
        {
            if (Props.waterSwaps == null || Props.waterSwaps.Count == 0) return;
            Map map = pawn.Map;
            if (SwapFor(pawn.Position.GetTerrain(map)) == null) return; // not wading

            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, Props.waterPoisonRadius, true))
            {
                if (!c.InBounds(map)) continue;
                TerrainDef to = SwapFor(c.GetTerrain(map));
                if (to != null) map.terrainGrid.SetTerrain(c, to);
            }
        }

        private TerrainDef SwapFor(TerrainDef t)
        {
            if (t == null) return null;
            List<RM_TerrainSwap> swaps = Props.waterSwaps;
            for (int i = 0; i < swaps.Count; i++)
                if (swaps[i].from == t) return swaps[i].to;
            return null;
        }

        // ── fire warden ─────────────────────────────────────────────────
        private void TryWardFire(Pawn pawn)
        {
            if (pawn.Downed || !pawn.Awake() || pawn.InMentalState) return;
            if (pawn.jobs == null) return;
            if (pawn.Faction != null && pawn.Faction.IsPlayer && pawn.Drafted) return;

            JobDef cur = pawn.CurJobDef;
            if (cur == JobDefOf.BeatFire || cur == JobDefOf.AttackMelee) return;

            Fire fire = NearestFire(pawn);
            if (fire == null) return;

            if (RM_PoisonForestSettings.vexxissAttacksIgniter)
            {
                Pawn igniter = fire.instigator as Pawn;
                if (IsAttackableIgniter(pawn, igniter))
                {
                    Job attack = JobMaker.MakeJob(JobDefOf.AttackMelee, igniter);
                    attack.killIncappedTarget = false;
                    attack.expiryInterval = Props.attackJobExpiryTicks;
                    attack.checkOverrideOnExpire = true;
                    pawn.jobs.StartJob(attack, JobCondition.InterruptForced);
                    return;
                }
            }

            if (pawn.natives?.BeatFireVerb == null) return; // race lacks the verb
            Job beat = JobMaker.MakeJob(JobDefOf.BeatFire, fire);
            pawn.jobs.StartJob(beat, JobCondition.InterruptForced);
        }

        private Fire NearestFire(Pawn pawn)
        {
            List<Thing> fires = pawn.Map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            if (fires == null || fires.Count == 0) return null;
            float maxSq = Props.fireScanRadius * Props.fireScanRadius;
            Fire best = null;
            float bestSq = float.MaxValue;
            for (int i = 0; i < fires.Count; i++)
            {
                if (!(fires[i] is Fire f) || f.parent != null || !f.Spawned) continue;
                float d = (f.Position - pawn.Position).LengthHorizontalSquared;
                if (d > maxSq || d >= bestSq) continue;
                if (!pawn.CanReach(f, PathEndMode.Touch, Danger.Deadly)) continue;
                best = f;
                bestSq = d;
            }
            return best;
        }

        private bool IsAttackableIgniter(Pawn pawn, Pawn igniter)
        {
            if (igniter == null || igniter == pawn) return false;
            if (!igniter.Spawned || igniter.Dead || igniter.Downed || igniter.Map != pawn.Map) return false;
            if (pawn.Faction != null && igniter.Faction == pawn.Faction) return false;
            float max = Props.igniterChaseRadius;
            if ((igniter.Position - pawn.Position).LengthHorizontalSquared > max * max) return false;
            return pawn.CanReach(igniter, PathEndMode.Touch, Danger.Deadly);
        }
    }
}
