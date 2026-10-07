using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Cauldron
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

        // CAULDRON_GPT_ENRICHMENT_1 part 2: water the vexxiss poisons is
        // announced, never silent. TUNED: at most one letter per vexxiss per
        // in-game day, so a wading giant does not spam the letter stack.
        public int waterLetterCooldownTicks = 60000;

        // CAULDRON_VENT_ENRICHMENT_HOOKS_1 vent drinking. Radii/cooldown are INVENTED tuning.
        public int ventScanIntervalTicks = 250;
        public float ventScanRadius = 40f;
        public float ventGroanRadius = 80f;      // while vents falter or a bloom blows: it follows the groans
        public float ventDrinkChance = 0.6f;     // per scan outside a groan
        public int ventDrinkCooldownTicks = 2500;

        // CAULDRON_ENRICHMENT_VISUALS_1 V4 prints on the footprint grid. PROVISIONAL tuning: a print every
        // 1.5 cells moved (bodySize 6), kept about a day (owner ruling 2026-10-03), printSize 1.0 so the grid's
        // Huge class draws it at ~2.2 cells. printTexPath null = the grid's own large-print sprite until the
        // mineral-ringed vexxiss print art exists.
        public int printCheckIntervalTicks = 30;
        public float printStepCells = 1.5f;
        public int printLifetimeTicks = 60000;
        public float printSize = 1.0f;
        public string printTexPath;

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

            if (RM_CauldronSettings.vexxissPoisonsWater && pawn.IsHashIntervalTick(Props.waterCheckIntervalTicks))
                PoisonWaterAround(pawn);

            if (RM_CauldronSettings.vexxissFireWardenEnabled && pawn.IsHashIntervalTick(Props.fireScanIntervalTicks))
                TryWardFire(pawn);

            if (RM_CauldronSettings.vexxissDrinksVentsEnabled && pawn.IsHashIntervalTick(Props.ventScanIntervalTicks))
                TryDrinkVent(pawn);

            if (RM_CauldronSettings.vexxissPrintsEnabled && pawn.IsHashIntervalTick(Props.printCheckIntervalTicks))
                RM_VexxissPrints.TryStep(pawn, this);
        }

        // V4: the cell of the last print laid (not saved: after a load the next step simply prints).
        public IntVec3 lastPrintCell = IntVec3.Invalid;

        // ── drinks a vent ───────────────────────────────────────────────
        // Wild vexxiss only. Walks to the nearest breathing vent and inhales (RM_VexxissDrinkVent) until the
        // vent falls silent for days; a silenced vent has Output 0 so it is skipped until it recovers.
        private int nextDrinkTick;

        private void TryDrinkVent(Pawn pawn)
        {
            int now = Find.TickManager.TicksGame;
            JobDef cur = pawn.CurJobDef;
            bool busy = cur == JobDefOf.BeatFire || cur == JobDefOf.AttackMelee || cur == RM_CauldronDefOf.RM_VexxissDrinkVent;
            if (!RM_VentKernel.DrinkAllowed(pawn.Faction == null, pawn.Downed, pawn.Awake(), pawn.InMentalState, pawn.jobs != null, now, nextDrinkTick, busy)) return;

            Map map = pawn.Map;
            bool groan = RM_Building_CauldronVent.IsFaltering(map) || RM_Building_CauldronVent.IsBlooming(map);
            if (RM_VentKernel.DrinkRollNeeded(groan) && !Rand.Chance(Props.ventDrinkChance)) return;
            float radius = RM_VentKernel.DrinkRadius(groan, Props.ventScanRadius, Props.ventGroanRadius);

            List<Thing> vents = map.listerThings.ThingsOfDef(RM_CauldronDefOf.RM_CauldronVent);
            var vs = new RM_Building_CauldronVent[vents.Count];
            var distSq = new float[vents.Count];
            var silenced = new bool[vents.Count];
            var output = new float[vents.Count];
            for (int i = 0; i < vents.Count; i++)
            {
                var v = vents[i] as RM_Building_CauldronVent;
                vs[i] = v;
                silenced[i] = v == null || v.IsSilenced;
                output[i] = v == null ? 0f : v.Output;
                distSq[i] = v == null ? float.MaxValue : (v.Position - pawn.Position).LengthHorizontalSquared;
            }
            int bi = RM_VentKernel.NearestDrinkable(distSq, silenced, output, k => pawn.CanReach(vs[k], PathEndMode.Touch, Danger.Deadly), radius);
            RM_Building_CauldronVent best = bi >= 0 ? vs[bi] : null;
            if (best == null) return;
            nextDrinkTick = now + Props.ventDrinkCooldownTicks;
            pawn.jobs.StartJob(JobMaker.MakeJob(RM_CauldronDefOf.RM_VexxissDrinkVent, best), JobCondition.InterruptForced);
        }

        // ── poisons water on touch ──────────────────────────────────────
        private void PoisonWaterAround(Pawn pawn)
        {
            if (Props.waterSwaps == null || Props.waterSwaps.Count == 0) return;
            Map map = pawn.Map;
            if (SwapFor(pawn.Position.GetTerrain(map)) == null) return; // not wading

            int poisoned = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, Props.waterPoisonRadius, true))
            {
                if (!c.InBounds(map)) continue;
                TerrainDef to = SwapFor(c.GetTerrain(map));
                if (to != null) { map.terrainGrid.SetTerrain(c, to); poisoned++; }
            }
            if (poisoned > 0) MaybeWarnPoisonedWater(pawn);
        }

        // The warning letter (CAULDRON_GPT_ENRICHMENT_1 part 2). Only where the
        // player is present (a map with a spawned colonist); throttled per
        // animal; its own Mod Settings toggle.
        private int lastWaterLetterTick = -999999;

        private void MaybeWarnPoisonedWater(Pawn pawn)
        {
            Map map = pawn.Map;
            int now = Find.TickManager.TicksGame;
            if (!RM_VexxissKernel.WarnWater(RM_CauldronSettings.vexxissWaterLetter, map != null, map != null && map.mapPawns.AnyColonistSpawned,
                    now, lastWaterLetterTick, Props.waterLetterCooldownTicks)) return;
            lastWaterLetterTick = now;
            Find.LetterStack.ReceiveLetter(
                "Vexxiss poisoning water",
                "A vexxiss is wading through open water, and every cell it touches is turning to toxic water. "
                + "Toxic water is unsafe to drink from or wade through.",
                LetterDefOf.NegativeEvent,
                new LookTargets(pawn));
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastWaterLetterTick, "rmLastWaterLetterTick", -999999);
            Scribe_Values.Look(ref nextDrinkTick, "rmNextVentDrinkTick", 0);
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
            JobDef cur = pawn.CurJobDef;
            if (!RM_VexxissKernel.WardCanAct(pawn.Downed, pawn.Awake(), pawn.InMentalState, pawn.jobs != null,
                    pawn.Faction != null && pawn.Faction.IsPlayer && pawn.Drafted, cur == JobDefOf.BeatFire || cur == JobDefOf.AttackMelee)) return;

            Fire fire = NearestFire(pawn);
            Pawn igniter = fire != null && RM_CauldronSettings.vexxissAttacksIgniter ? fire.instigator as Pawn : null;
            WardChoice choice = RM_VexxissKernel.Ward(fire != null, RM_CauldronSettings.vexxissAttacksIgniter,
                fire != null && RM_CauldronSettings.vexxissAttacksIgniter && IsAttackableIgniter(pawn, igniter),
                pawn.natives?.BeatFireVerb != null);   // the race may lack the verb
            if (choice == WardChoice.AttackIgniter)
            {
                Job attack = JobMaker.MakeJob(JobDefOf.AttackMelee, igniter);
                attack.killIncappedTarget = false;
                attack.expiryInterval = Props.attackJobExpiryTicks;
                attack.checkOverrideOnExpire = true;
                pawn.jobs.StartJob(attack, JobCondition.InterruptForced);
            }
            else if (choice == WardChoice.BeatFire)
            {
                Job beat = JobMaker.MakeJob(JobDefOf.BeatFire, fire);
                pawn.jobs.StartJob(beat, JobCondition.InterruptForced);
            }
        }

        private Fire NearestFire(Pawn pawn)
        {
            List<Thing> fires = pawn.Map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            if (fires == null || fires.Count == 0) return null;
            var fs = new Fire[fires.Count];
            var distSq = new float[fires.Count];
            var eligible = new bool[fires.Count];
            for (int i = 0; i < fires.Count; i++)
            {
                fs[i] = fires[i] as Fire;
                eligible[i] = fs[i] != null && fs[i].parent == null && fs[i].Spawned;
                if (!eligible[i]) continue;
                distSq[i] = (fs[i].Position - pawn.Position).LengthHorizontalSquared;
            }
            int best = RM_VexxissKernel.NearestFire(distSq, eligible, k => pawn.CanReach(fs[k], PathEndMode.Touch, Danger.Deadly), Props.fireScanRadius);
            return best >= 0 ? fs[best] : null;
        }

        private bool IsAttackableIgniter(Pawn pawn, Pawn igniter)
        {
            if (igniter == null) return false;
            bool near = igniter.Spawned && !igniter.Dead && !igniter.Downed && igniter.Map == pawn.Map
                && (igniter.Position - pawn.Position).LengthHorizontalSquared <= Props.igniterChaseRadius * Props.igniterChaseRadius;
            return RM_VexxissKernel.IgniterAttackable(true, igniter == pawn, igniter.Spawned, igniter.Dead, igniter.Downed, igniter.Map == pawn.Map,
                pawn.Faction != null && igniter.Faction == pawn.Faction, near ? (igniter.Position - pawn.Position).LengthHorizontalSquared : float.MaxValue,
                Props.igniterChaseRadius, near && igniter != pawn && !(pawn.Faction != null && igniter.Faction == pawn.Faction)
                && pawn.CanReach(igniter, PathEndMode.Touch, Danger.Deadly));
        }
    }
}
