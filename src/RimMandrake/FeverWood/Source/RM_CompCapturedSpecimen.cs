using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.EnvironmentalHazards;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_DIANOGA_PRISON_1. "A prison tank, not a pen: it teaches, it
    // produces, and it can get out" (design sheet §6j/§6m, owner rulings
    // 2026-09-23). Sits alongside a CompRefuelable on the same ThingDef —
    // CompRefuelable IS the feeding mechanism (its fuelFilter is set to
    // MeatRaw in XML, so vanilla's own WorkGiver_Refuel already hauls meat
    // to it with no new job/UI code) and this comp reads its fuel state
    // rather than re-implementing "does it have upkeep".
    //
    //   teaches  -> Notify_Taught() on RUT_MapComponent_TheTenant, once,
    //               the first time the tank produces successfully.
    //   produces -> Props.products, each on its own MTB-days roll, gated on
    //               CompRefuelable.HasFuel.
    //   escapes  -> two independent triggers: sustained neglect (unfed past
    //               neglectDaysBeforeEscapeRisk, then an MTB roll) and
    //               damage (past damageEscapeThresholdFraction lost, then a
    //               flat per-hit chance) — "a neglected OR damaged tank
    //               releases it" (§6j, emphasis the item's own).
    //
    // Escape spawns Props.occupantKindDefName (resolved live, not cached,
    // so the Star Wars swap patch — a PatchOperationReplace on this very
    // string — is picked up without any code change) as a wild, aggressive,
    // water-seeking animal: "it is TOUGH... makes for the nearest water and
    // hurts whatever is between" (§6m stage 1). RM_CompEscapedCaptive (a
    // per-pawn comp on the SPAWNED escapee, not this one) watches for it
    // reaching registered water and handles stage 2/3 from there.
    public class RM_CompCapturedSpecimen : ThingComp
    {
        private const int CheckIntervalTicks = 2500; // 1 in-game hour
        private const float TicksPerDay = 60000f;

        private int unfedSinceTick = -1;
        private bool taught;
        private Dictionary<ThingDef, int> lastProducedTick = new Dictionary<ThingDef, int>();

        public RM_CompProperties_CapturedSpecimen Props => (RM_CompProperties_CapturedSpecimen)props;

        private CompRefuelable Fuel => parent.GetComp<CompRefuelable>();

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!respawningAfterLoad)
            {
                foreach (RM_CapturedSpecimenProduct p in Props.products)
                {
                    if (p.thing != null)
                    {
                        lastProducedTick[p.thing] = Find.TickManager.TicksGame;
                    }
                }
            }
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.Spawned || parent.Map == null)
            {
                return;
            }
            if (!RM_FeverWoodSettings.sekkulaathTankEnabled)
            {
                return; // Mod Settings master off: inert box, per that toggle's own tooltip
            }
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }

            bool fed = Fuel == null || Fuel.HasFuel; // no CompRefuelable at all: treat as always-fed
            TickNeglect(fed);
            if (fed)
            {
                TickProduction();
            }
        }

        private void TickNeglect(bool fed)
        {
            if (fed)
            {
                unfedSinceTick = -1;
                return;
            }
            if (unfedSinceTick < 0)
            {
                unfedSinceTick = Find.TickManager.TicksGame;
                return;
            }

            float daysUnfed = (Find.TickManager.TicksGame - unfedSinceTick) / TicksPerDay;
            if (daysUnfed < Props.neglectDaysBeforeEscapeRisk)
            {
                return;
            }

            float riskMultiplier = Mathf.Max(0.01f, RM_FeverWoodSettings.sekkulaathEscapeRiskMultiplier);
            float effectiveMtbDays = Props.neglectEscapeMtbDays * riskMultiplier; // lower multiplier = shorter MTB = more escape-prone
            if (Rand.MTBEventOccurs(effectiveMtbDays, TicksPerDay, CheckIntervalTicks))
            {
                Escape("neglect");
            }
        }

        private void TickProduction()
        {
            for (int i = 0; i < Props.products.Count; i++)
            {
                RM_CapturedSpecimenProduct p = Props.products[i];
                if (p.thing == null)
                {
                    continue;
                }
                int last = lastProducedTick.TryGetValue(p.thing, out int t) ? t : Find.TickManager.TicksGame;
                int elapsed = Find.TickManager.TicksGame - last;
                if (!Rand.MTBEventOccurs(p.mtbDays, TicksPerDay, elapsed >= CheckIntervalTicks ? CheckIntervalTicks : elapsed))
                {
                    continue;
                }

                lastProducedTick[p.thing] = Find.TickManager.TicksGame;
                Thing produced = ThingMaker.MakeThing(p.thing);
                produced.stackCount = Mathf.Clamp(p.countRange.RandomInRange, 1, p.thing.stackLimit);
                GenPlace.TryPlaceThing(produced, parent.Position, parent.Map, ThingPlaceMode.Near);

                if (!taught && Props.teachesColonyWarning)
                {
                    taught = true;
                    parent.Map.GetComponent<RUT_MapComponent_TheTenant>()?.Notify_Taught();
                    Messages.Message("The tank's occupant has produced enough for the colony to finally learn its" +
                        " name — and the low hum that warns of the real thing beneath the pools.",
                        new TargetInfo(parent.Position, parent.Map), MessageTypeDefOf.PositiveEvent);
                }
            }
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (totalDamageDealt <= 0f || parent.Destroyed || !parent.Spawned)
            {
                return;
            }
            if (!RM_FeverWoodSettings.sekkulaathTankEnabled)
            {
                return;
            }

            float maxHp = parent.MaxHitPoints > 0 ? parent.MaxHitPoints : 1;
            float lostFraction = 1f - (float)parent.HitPoints / maxHp;
            if (lostFraction < Props.damageEscapeThresholdFraction)
            {
                return;
            }

            float riskMultiplier = Mathf.Max(0.01f, RM_FeverWoodSettings.sekkulaathEscapeRiskMultiplier);
            float effectiveChance = Mathf.Clamp01(Props.damageEscapeChancePerHit / riskMultiplier); // lower multiplier = higher chance
            if (Rand.Chance(effectiveChance))
            {
                Escape("damage");
            }
        }

        /// <summary>"A neglected or damaged tank releases it — a disaster
        /// the player built" (§6j). Destroys the tank itself (it is a
        /// breach, not a door) and spawns the occupant kind as a wild,
        /// hostile, water-seeking escapee carrying the captivity marker
        /// (item's ruling 3: "it remembers the tank").</summary>
        private void Escape(string cause)
        {
            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(Props.occupantKindDefName);

            if (!parent.Destroyed)
            {
                parent.Destroy(DestroyMode.Vanish);
            }

            if (kind == null || map == null)
            {
                return; // occupant kind not loaded (e.g. mid-swap misconfiguration) — tank still breaks, nothing to spawn
            }

            IntVec3 spawnCell = CellFinder.RandomClosewalkCellNear(pos, map, 3);
            Pawn escapee = PawnGenerator.GeneratePawn(kind, null);
            GenSpawn.Spawn(escapee, spawnCell, map);

            HediffDef memory = DefDatabase<HediffDef>.GetNamedSilentFail("RM_CaptivityMemory");
            if (memory != null)
            {
                escapee.health.AddHediff(memory);
            }

            // "it is TOUGH... hurts whatever is between it and there" —
            // manhunter while it beelines for water, same lever vanilla
            // manhunter-pack incidents use.
            escapee.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Manhunter,
                reason: "Escaped captivity", forceWake: true, causedByMood: false);

            escapee.GetComp<RM_CompEscapedCaptive>()?.Notify_JustEscaped();

            Messages.Message($"The tank has failed ({cause}) — its occupant has escaped and is heading for water!",
                new TargetInfo(spawnCell, map), MessageTypeDefOf.ThreatBig);
        }

        public override string CompInspectStringExtra()
        {
            if (Fuel == null)
            {
                return null;
            }
            return Fuel.HasFuel
                ? "Occupant fed — producing while stock lasts."
                : "Occupant unfed — containment risk rising.";
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref unfedSinceTick, "unfedSinceTick", -1);
            Scribe_Values.Look(ref taught, "taught", false);
            Scribe_Collections.Look(ref lastProducedTick, "lastProducedTick", LookMode.Def, LookMode.Value);
            if (lastProducedTick == null)
            {
                lastProducedTick = new Dictionary<ThingDef, int>();
            }
        }
    }
}
