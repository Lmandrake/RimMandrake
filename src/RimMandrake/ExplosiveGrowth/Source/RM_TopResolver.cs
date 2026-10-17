using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.ExplosiveGrowth
{
    /// <summary>
    /// The sown ring. Two rules, both ruled (design doc §3):
    ///   respectBuiltGround = true   the CHURN: fields, stockpiles, open dirt;
    ///                               never floors, buildings, or interiors.
    ///   respectBuiltGround = false  the BURST: ignores zones — fields, floors
    ///                               and doorways — stopping only at walls and
    ///                               anything impassable.
    /// Both refuse suppressed ground (Greentide M10: grazing holds the green back).
    /// </summary>
    public static class RM_SproutRing
    {
        public static int Sow(Map map, IntVec3 center, ThingDef plantDef, float radius, int count,
            bool respectBuiltGround, RM_MapComponent_ExplosiveGrowth comp, float growth)
        {
            if (plantDef?.plant == null || count <= 0) return 0;
            int now = Find.TickManager.TicksGame;
            List<IntVec3> cells = GenRadial.RadialCellsAround(center, radius, false)
                .Where(c => CanSprout(map, c, plantDef, respectBuiltGround, comp, now))
                .InRandomOrder()
                .Take(count)
                .ToList();
            foreach (IntVec3 c in cells)
            {
                Plant p = (Plant)GenSpawn.Spawn(plantDef, c, map);
                p.Growth = growth;
                comp?.NoteSeedling(c);   // OQ-11: a seedling on fresh ash restarts its window
            }
            return cells.Count;
        }

        public static bool CanSprout(Map map, IntVec3 c, ThingDef plantDef, bool respectBuiltGround,
            RM_MapComponent_ExplosiveGrowth comp, int now)
        {
            if (!c.InBounds(map)) return false;
            if (comp != null && comp.IsSuppressed(c, now)) return false;
            TerrainDef t = c.GetTerrain(map);
            if (t == null || t.IsWater) return false;
            if (c.GetPlant(map) != null) return false;
            Building edifice = c.GetEdifice(map);

            if (respectBuiltGround)
            {
                if (t.IsFloor || edifice != null || c.GetFirstBuilding(map) != null) return false;
                Room room = c.GetRoom(map);
                if (room != null && !room.PsychologicallyOutdoors) return false;
                return plantDef.CanEverPlantAt(c, map);
            }

            // Burst: zones, floors and doorways are all fair game — only a
            // wall (or anything else impassable) stops a sprout.
            if (edifice != null && !(edifice is Building_Door)) return false;
            return c.Standable(map) || edifice is Building_Door;
        }
    }

    /// <summary>
    /// The six terminal moments (design doc §3). A disabled variant falls back
    /// to the Churn; a disabled Churn makes the plant relax back to normal size.
    /// All counts, radii and chances here are 🄸 INVENTED and are the perf-gate
    /// sitting's to tune.
    /// </summary>
    public static class RM_TopResolver
    {
        private const float ChurnRadius = 1.9f;
        private const float BurstRadius = 2.9f;
        private const float RuptureRadius = 3.9f;
        private const int RuptureCloudTicks = GenDate.TicksPerHour;

        /// <summary>The top of a charge (spec §4; OQ-5, OQ-6, OQ-8, OQ-14, OQ-15). The kernel picks the outcome: a native
        /// crop self-fruits; Slime / Tinder / Rupture / Flush keep their own top; otherwise the Burst roll (1 in 3 for dry
        /// natives by default, 0 for wet natives, 1 for a Burst row), else fruit + many sprouts (dry, the parent dies) or
        /// prolific fruit + wither + a few sprouts (wet). Every outcome then uses the water on the cell (OQ-8).</summary>
        public static void Fire(Plant plant, RM_PlantProfile prof, RM_MapComponent_ExplosiveGrowth comp)
        {
            if (plant == null || !plant.Spawned || prof == null || comp == null) return;
            // A tree never runs the maturity cycle (tree_burst_design §2); a forced top (debug action, API) is its burst.
            if (prof.isTree)
            {
                TreeBurst(plant, prof, comp, waterDriven: false);
                return;
            }
            RM_GrowthTop top = Effective(prof.top);
            Map map = plant.Map;
            IntVec3 c = plant.Position;
            bool nativeCrop = prof.Native && plant.IsCrop;
            RM_Outcome o = RM_ExplosiveGrowthKernel.ResolveOutcome(prof.archetype, (byte)top, prof.ruptureChance,
                ExplosiveGrowthSettings.defaultRuptureChance, Rand.Value, nativeCrop, ExplosiveGrowthSettings.cropSelfFruitEnabled,
                ExplosiveGrowthSettings.burstEnabled);
            LastOutcome = o;
            switch (o)
            {
                case RM_Outcome.SelfFruit: SelfFruit(plant); break;
                case RM_Outcome.Burst: Burst(plant, prof, comp, tinder: false); break;
                case RM_Outcome.Fruit: DryFruit(plant, prof, comp); break;
                case RM_Outcome.Wither: Wither(plant, prof, comp); break;
                case RM_Outcome.OwnTop:
                    switch (top)
                    {
                        case RM_GrowthTop.Tinder: Burst(plant, prof, comp, tinder: true); break;
                        case RM_GrowthTop.Slime: Slime(plant, prof, comp); break;
                        case RM_GrowthTop.Rupture: Rupture(plant, prof, comp); break;
                        case RM_GrowthTop.Flush: Flush(plant, prof, comp); break;
                    }
                    break;
                default: break;
            }
            if (o != RM_Outcome.None && ExplosiveGrowthSettings.waterUseEnabled)
                RM_WetSources.Consume(comp, c, prof.liquids, Find.TickManager.TicksGame);
            comp.Dirty(c);
        }

        /// <summary>The last outcome Fire chose (proof read-out only).</summary>
        public static RM_Outcome LastOutcome;

        public static RM_GrowthTop Effective(RM_GrowthTop top)
        {
            return (RM_GrowthTop)RM_ExplosiveGrowthKernel.EffectiveTop((byte)top,
                ExplosiveGrowthSettings.burstEnabled, ExplosiveGrowthSettings.tinderEnabled, ExplosiveGrowthSettings.slimeEnabled,
                ExplosiveGrowthSettings.ruptureEnabled, ExplosiveGrowthSettings.flushEnabled, ExplosiveGrowthSettings.churnEnabled);
        }

        private const float SproutRadius = 2.9f;
        private static readonly IntRange DrySprouts = new IntRange(4, 7);   // §4.1 "many" (PROPOSED)
        private static readonly IntRange WetSprouts = new IntRange(1, 2);   // §4.2 "a few" (PROPOSED)

        private static int Sprouts(RM_PlantProfile prof, IntRange fallback)
        {
            IntRange r = prof.sproutCount.max > 0 ? prof.sproutCount : fallback;
            return r.RandomInRange;
        }

        // ── DRY CYCLE: fruit, many sprouts, the parent dies (OQ-6: the seedlings carry the cycle). Never over your floor.

        private static void DryFruit(Plant plant, RM_PlantProfile prof, RM_MapComponent_ExplosiveGrowth comp)
        {
            Map map = plant.Map;
            IntVec3 c = plant.Position;
            ThingDef def = plant.def;
            DropProduce(plant, prof.produceFactor, scatter: false);
            RM_ExplosiveGrowthDefOf.RM_EG_Split?.PlayOneShot(new TargetInfo(c, map));
            FilthMaker.TryMakeFilth(c, map, ThingDefOf.Filth_LooseGround);
            SplitAndDie(plant);
            RM_SproutRing.Sow(map, c, def, SproutRadius, Sprouts(prof, DrySprouts), respectBuiltGround: true, comp, growth: 0.05f);
        }

        // ── WET CYCLE: fruit prolifically, wither quietly (no blast), a few sprouts.

        private static void Wither(Plant plant, RM_PlantProfile prof, RM_MapComponent_ExplosiveGrowth comp)
        {
            Map map = plant.Map;
            IntVec3 c = plant.Position;
            ThingDef def = plant.def;
            DropProduce(plant, prof.produceFactor * ExplosiveGrowthSettings.wetFruitFactor, scatter: false);
            if (plant.Spawned) plant.Kill(new DamageInfo(DamageDefOf.Rotting, 99999f));
            if (plant.Spawned && !plant.Destroyed) plant.Destroy(DestroyMode.KillFinalize);
            RM_SproutRing.Sow(map, c, def, SproutRadius, Sprouts(prof, WetSprouts), respectBuiltGround: true, comp, growth: 0.05f);
        }

        // ── CROP SELF-FRUIT (EC3 "A full harvest but the water gets used up"): the full YieldNow IS the harvest; the plant is
        // treated as harvested exactly as vanilla PlantCollected does (dies, or a repeat-harvest def resets to
        // harvestAfterGrowth; RimSage RimWorld/Plant.cs:621-664), so no second pawn harvest of the same growth.

        private static void SelfFruit(Plant plant)
        {
            ThingDef produce = plant.def.plant.harvestedThingDef;
            int n = produce != null ? plant.YieldNow() : 0;   // the jackpot postfix skips crops (OQ-14)
            if (n > 0) SpawnNear(produce, n, plant.Position, plant.Map);
            if (plant.def.plant.HarvestDestroys)
            {
                plant.TrySpawnStump(PlantDestructionMode.Smash);
                if (!plant.Destroyed) plant.Destroy(DestroyMode.KillFinalizeLeavingsOnly);
            }
            else
            {
                plant.Growth = plant.def.plant.harvestAfterGrowth;
                plant.Map.mapDrawer.MapMeshDirty(plant.Position, MapMeshFlagDefOf.Things);
            }
        }

        // ── BURST / TINDER: the rare violent top. Injury+knockdown ceiling.

        private static void Burst(Plant plant, RM_PlantProfile prof, RM_MapComponent_ExplosiveGrowth comp, bool tinder)
        {
            Map map = plant.Map;
            IntVec3 c = plant.Position;
            ThingDef def = plant.def;

            DropProduce(plant, prof.produceFactor * 1.5f, scatter: true); // "premium yield, scattered"
            RM_ExplosiveGrowthDefOf.RM_EG_Pop?.PlayOneShot(new TargetInfo(c, map));
            for (int i = 0; i < 6; i++) FleckMaker.ThrowDustPuff(c.ToVector3Shifted() + Gen.RandomHorizontalVector(1.2f), map, 1.4f);

            // Chaff and husk: hay is vanilla's own dry, flammable plant matter
            // — low-grade fuel, exactly the ruled husk. TINDER leaves more.
            SpawnNear(ThingDefOf.Hay, tinder ? Rand.RangeInclusive(8, 14) : Rand.RangeInclusive(3, 6), c, map);
            foreach (IntVec3 f in GenRadial.RadialCellsAround(c, BurstRadius, true))
            {
                if (f.InBounds(map) && Rand.Chance(0.35f)) FilthMaker.TryMakeFilth(f, map, ThingDefOf.Filth_LooseGround);
            }

            if (ExplosiveGrowthSettings.burstHurtsPawns) HurtPawnsNear(c, map, BurstRadius);

            SplitAndDie(plant);

            ThingDef ring = prof.ringPlant ?? def;
            int n = tinder ? Rand.RangeInclusive(5, 9) : Rand.RangeInclusive(3, 6);
            RM_SproutRing.Sow(map, c, ring, BurstRadius, n, respectBuiltGround: false, comp, growth: Rand.Range(0.25f, 0.45f));

            if (map.IsPlayerHome && MessagesRepeatAvoider.MessageShowAllowed("RM_EG_Burst", 60f))
            {
                Messages.Message("A swollen " + def.label + " burst, sowing the ground around it.",
                    new TargetInfo(c, map), MessageTypeDefOf.NegativeEvent);
            }
        }

        /// <summary>Injury+knockdown ceiling (2026-09-10 ruling 1): a light
        /// blunt hit and a short stun, never on a pawn already downed, and the
        /// hit is skipped if it would down the pawn.</summary>
        private static void HurtPawnsNear(IntVec3 c, Map map, float radius)
        {
            var hit = new List<Pawn>();
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(c, radius, true))
            {
                if (!cell.InBounds(map)) continue;
                List<Thing> things = cell.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    if (things[i] is Pawn p && !p.Dead && !p.Downed && !hit.Contains(p)) hit.Add(p);
                }
            }
            foreach (Pawn p in hit)
            {
                float amount = Rand.Range(2f, 5f);
                if (p.health.summaryHealth.SummaryHealthPercent > 0.5f)
                {
                    p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, amount));
                }
                if (!p.Dead && !p.Downed) p.stances?.stunner?.StunFor(Rand.RangeInclusive(60, 150), null, addBattleLog: false);
            }
        }

        // ── THE TREE BURST (tree_burst_design_2026-10-17.md §4, T4): a tree's end of life, never a maturity cycle. Fired by a
        // water-driven death (Q5/Q6: "Every tree that hits a water-driven death bursts") and by a jungle tree's end of life
        // (Q11). Yields (Q12, Q16/Q17): its logs (its own wood, or WoodLog for a tree whose harvest is not wood), its own
        // product, its own fruit if a roster names one, 2-4 seedlings on ground the player has not built; the Burst's blast.
        // A Contagion tree's contaminated Rupture IS its burst (Q15).

        private static readonly IntRange TreeSeedlings = new IntRange(2, 4);   // Q17

        /// <summary>The last tree burst's yields (proof read-out only): logs, product, fruit, seedlings, waterDriven.</summary>
        public static string LastTreeBurst = "";

        /// <summary>Wood: WoodLog or any Woody-stuff log (RM_OllimWood, RM_SlackwaxTimber...).</summary>
        public static bool IsWood(ThingDef t)
        {
            if (t == null) return false;
            if (t == ThingDefOf.WoodLog) return true;
            List<StuffCategoryDef> cats = t.stuffProps?.categories;
            return cats != null && cats.Contains(StuffCategoryDefOf.Woody);
        }

        public static void TreeBurst(Plant plant, RM_PlantProfile prof, RM_MapComponent_ExplosiveGrowth comp, bool waterDriven)
        {
            if (plant == null || !plant.Spawned || plant.Destroyed || prof == null || comp == null) return;
            Map map = plant.Map;
            IntVec3 c = plant.Position;
            ThingDef def = plant.def;
            if (prof.top == RM_GrowthTop.Rupture && ExplosiveGrowthSettings.ruptureEnabled)
            {
                LastTreeBurst = "rupture=1 waterDriven=" + waterDriven;
                Rupture(plant, prof, comp);
                comp.Dirty(c);
                return;
            }

            ThingDef harvest = def.plant.harvestedThingDef;
            float yield = def.plant.harvestYield;
            bool woodHarvest = IsWood(harvest) && yield > 0f;
            ThingDef logDef = woodHarvest ? harvest : ThingDefOf.WoodLog;
            int logs = woodHarvest ? GenMath.RoundRandom(yield)
                : Mathf.Max(0, prof.burstLogs >= 0 ? prof.burstLogs : ExplosiveGrowthSettings.treeBurstDefaultLogs);
            int product = !woodHarvest && harvest != null && yield > 0f && prof.produceFactor > 0f
                ? GenMath.RoundRandom(yield * prof.produceFactor) : 0;
            int fruit = prof.burstFruit != null ? prof.burstFruitCount : 0;

            Scatter(logDef, logs, c, map);
            if (product > 0) Scatter(harvest, product, c, map);
            if (fruit > 0) Scatter(prof.burstFruit, fruit, c, map);

            RM_ExplosiveGrowthDefOf.RM_EG_Pop?.PlayOneShot(new TargetInfo(c, map));
            for (int i = 0; i < 8; i++) FleckMaker.ThrowDustPuff(c.ToVector3Shifted() + Gen.RandomHorizontalVector(1.6f), map, 1.8f);
            foreach (IntVec3 f in GenRadial.RadialCellsAround(c, BurstRadius, true))
            {
                if (f.InBounds(map) && Rand.Chance(0.35f)) FilthMaker.TryMakeFilth(f, map, ThingDefOf.Filth_LooseGround);
            }
            if (ExplosiveGrowthSettings.burstHurtsPawns) HurtPawnsNear(c, map, BurstRadius);

            SplitAndDie(plant);
            int sown = RM_SproutRing.Sow(map, c, def, SproutRadius, TreeSeedlings.RandomInRange, respectBuiltGround: true, comp, growth: 0.05f);
            LastTreeBurst = string.Format("logs={0} logDef={1} product={2} fruit={3} seedlings={4} waterDriven={5}",
                logs, logDef.defName, product, fruit, sown, waterDriven);

            if (map.IsPlayerHome && MessagesRepeatAvoider.MessageShowAllowed("RM_EG_TreeBurst", 60f))
            {
                Messages.Message(waterDriven
                        ? Find.ActiveLanguageWorker.WithIndefiniteArticle(def.label).CapitalizeFirst() + " drank past the end of its life and burst, throwing logs and seedlings."
                        : "An old " + def.label + " burst at the end of its life, throwing logs and seedlings.",
                    new TargetInfo(c, map), MessageTypeDefOf.NeutralEvent);
            }
            comp.Dirty(c);
        }

        /// <summary>A stack scattered in a few clumps across the burst radius (the Burst's "premium yield, scattered").</summary>
        private static void Scatter(ThingDef def, int count, IntVec3 c, Map map)
        {
            if (def == null || count <= 0) return;
            int clumps = Mathf.Clamp(count / 4, 1, 4);
            for (int i = 0; i < clumps; i++)
            {
                int n = i == clumps - 1 ? count : count / clumps;
                count -= n;
                IntVec3 at = c + GenRadial.RadialPattern[Rand.Range(0, GenRadial.NumCellsInRadius(BurstRadius))];
                SpawnNear(def, n, at.InBounds(map) ? at : c, map);
            }
        }

        // ── SLIME: Churn-shaped; the ring turns to slime, not sprouts.

        private static void Slime(Plant plant, RM_PlantProfile prof, RM_MapComponent_ExplosiveGrowth comp)
        {
            Map map = plant.Map;
            IntVec3 c = plant.Position;
            DropProduce(plant, prof.produceFactor, scatter: false);
            RM_ExplosiveGrowthDefOf.RM_EG_Split?.PlayOneShot(new TargetInfo(c, map));
            SplitAndDie(plant);

            TerrainDef slime = prof.slimeTerrain;
            int now = Find.TickManager.TicksGame;
            foreach (IntVec3 f in GenRadial.RadialCellsAround(c, ChurnRadius, true))
            {
                if (!f.InBounds(map) || comp.IsSuppressed(f, now)) continue;
                TerrainDef t = f.GetTerrain(map);
                if (t == null || t.IsWater || t.IsFloor || f.GetEdifice(map) != null) continue;
                if (slime != null && t != slime && Rand.Chance(0.7f))
                {
                    map.terrainGrid.SetTerrain(f, slime);
                }
                else if (slime == null)
                {
                    FilthMaker.TryMakeFilth(f, map, ThingDefOf.Filth_Slime);
                }
            }
        }

        // ── RUPTURE: the bioweapon at open throttle. Vile.

        private static void Rupture(Plant plant, RM_PlantProfile prof, RM_MapComponent_ExplosiveGrowth comp)
        {
            Map map = plant.Map;
            IntVec3 c = plant.Position;
            ThingDef def = plant.def;
            RM_ExplosiveGrowthDefOf.RM_EG_Rupture?.PlayOneShot(new TargetInfo(c, map));

            // The cloud. Vanilla has no red gas; tox gas is the carrier (Biotech
            // is a hard prerequisite), the red is the filth and the spawn.
            GasUtility.AddGas(c, map, GasType.ToxGas, RuptureRadius);
            foreach (IntVec3 f in GenRadial.RadialCellsAround(c, 2.4f, true))
            {
                if (f.InBounds(map) && Rand.Chance(0.4f)) FilthMaker.TryMakeFilth(f, map, ThingDefOf.Filth_Blood);
            }

            SplitAndDie(plant);

            // "Emits red slimes, occular entities" — the roster's pawn kinds.
            foreach (PawnKindDef kind in RM_ExplosiveGrowthRegistry.RupturePawnKinds)
            {
                if (!Rand.Chance(0.5f)) continue;
                if (!CellFinder.TryFindRandomCellNear(c, map, 3, x => x.Standable(map), out IntVec3 spot)) continue;
                Pawn p = PawnGenerator.GeneratePawn(kind);
                GenSpawn.Spawn(p, spot, map);
            }

            // "and more little sprouts around it".
            RM_SproutRing.Sow(map, c, def, ChurnRadius, Rand.RangeInclusive(2, 4), respectBuiltGround: true, comp, growth: 0.05f);

            comp.AddRupture(c, RuptureRadius, RuptureCloudTicks);
            RuptureExposurePulse(map, new RM_RuptureZone { center = c, radius = RuptureRadius });

            if (map.IsPlayerHome && MessagesRepeatAvoider.MessageShowAllowed("RM_EG_Rupture", 60f))
            {
                Messages.Message("A contaminated " + def.label + " ruptured. Anyone in the cloud without a sealed suit risks mutation.",
                    new TargetInfo(c, map), MessageTypeDefOf.ThreatSmall);
            }
        }

        /// <summary>"Extra mutation hediffs for player caught in this without
        /// 100% vac protection." Vacuum resistance is the Odyssey stat.</summary>
        public static void RuptureExposurePulse(Map map, RM_RuptureZone z)
        {
            List<HediffDef> pool = RM_ExplosiveGrowthRegistry.RuptureMutationHediffs;
            if (pool.Count == 0 || ExplosiveGrowthSettings.ruptureMutationChance <= 0f) return;
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(z.center, z.radius, true))
            {
                if (!cell.InBounds(map)) continue;
                List<Thing> things = cell.GetThingList(map);
                for (int i = things.Count - 1; i >= 0; i--)
                {
                    if (!(things[i] is Pawn p) || p.Dead || !p.RaceProps.IsFlesh) continue;
                    if (p.GetStatValue(StatDefOf.VacuumResistance) >= 0.999f) continue;
                    if (!Rand.Chance(ExplosiveGrowthSettings.ruptureMutationChance)) continue;
                    Mutate(p, pool.RandomElement());
                }
            }
        }

        private static void Mutate(Pawn p, HediffDef def)
        {
            // A random un-missing OUTSIDE LEAF part, never one with children —
            // the Contagion's own Unfinished-spawner rule, so an added-part
            // mutation never amputates anything else — and never an internal
            // organ: a claw budding in place of a heart is a death sentence,
            // which is past this mechanic's brief (mutation, not execution).
            List<BodyPartRecord> leaves = p.health.hediffSet.GetNotMissingParts(depth: BodyPartDepth.Outside)
                .Where(r => r.parts.Count == 0 && !p.health.hediffSet.PartOrAnyAncestorHasDirectlyAddedParts(r))
                .ToList();
            if (leaves.Count == 0) return;
            BodyPartRecord part = leaves.RandomElement();
            Hediff h = HediffMaker.MakeHediff(def, p, part);
            p.health.AddHediff(h, part);
            if (p.Faction == Faction.OfPlayer)
            {
                Messages.Message(p.LabelShort + " was mutated by the rupture cloud: " + h.LabelCap + ".", p, MessageTypeDefOf.NegativeHealthEvent);
            }
        }

        // ── FLUSH: growth runs inside the giant. No surface spectacle.

        private static void Flush(Plant plant, RM_PlantProfile prof, RM_MapComponent_ExplosiveGrowth comp)
        {
            // The giant survives its top: its produce comes out at its foot and
            // it relaxes back to natural size. Bark swelling, boughway re-route
            // and the thornbug nectar glut are the Fever Wood kit's to draw —
            // this engine owns only that the top is silent and non-lethal.
            DropProduce(plant, prof.produceFactor, scatter: false);
        }

        // ── shared pieces ────────────────────────────────────────────────

        private static void SplitAndDie(Plant plant)
        {
            if (!plant.Spawned) return;
            plant.TrySpawnStump(PlantDestructionMode.Smash);
            if (!plant.Destroyed) plant.Destroy(DestroyMode.Vanish);
        }

        private static void DropProduce(Plant plant, float factor, bool scatter)
        {
            ThingDef produce = plant.def.plant.harvestedThingDef;
            // §4.1 / §5.1 (EC1): "Wood is never a cycle drop." Trees no longer cycle (tree_burst_design §4: their burst has its
            // own drop path, TreeBurst); this guard stays for every non-tree outcome.
            if (produce == null || produce == ThingDefOf.WoodLog || plant.def.plant.harvestYield <= 0f || factor <= 0f) return;
            int count = GenMath.RoundRandom(plant.def.plant.harvestYield * factor);
            if (count <= 0) return;
            if (!scatter)
            {
                SpawnNear(produce, count, plant.Position, plant.Map);
                return;
            }
            Scatter(produce, count, plant.Position, plant.Map);
        }

        private static void SpawnNear(ThingDef def, int count, IntVec3 at, Map map)
        {
            while (count > 0)
            {
                Thing t = ThingMaker.MakeThing(def);
                t.stackCount = Mathf.Min(count, def.stackLimit);
                count -= t.stackCount;
                GenPlace.TryPlaceThing(t, at, map, ThingPlaceMode.Near);
            }
        }
    }
}
