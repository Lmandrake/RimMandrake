using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    // ════════════════════════════════════════════════════════════════════
    // TREE_BURST_BUILD_LITRES_BUY_YEARS — a tree's life, step by step (design/RimMandrake/tree_burst_design_2026-10-17.md
    // §3, §4, §6a; the owner's card rulings of 2026-10-17, §8).
    //
    // Runs from the Plant.TickLong prefix (every 2000 ticks per plant; Plant only ticks TickLong), BEFORE vanilla adds its
    // own 2000 to the age and checks Dying, so a burst here pre-empts vanilla's death and a natural crossing is left to
    // vanilla ("a natural death that isn't water-driven can just fall over dead").
    //
    //   dry-land tree (dry or fire-adapted native)  DRINKS: a spill on its cell is drunk whole (thickness x litres per spill,
    //       the filth is used up); any other water it accepts (river, mud, a running flood, rain, a channel, a sprinkler)
    //       gives at most treeDrinkLitresPerDay. Every treeLitresPerDayOfLife litres buys one day of life: growth while
    //       immature, then age (Q1/Q4). A drink that carries the age past the lifespan bursts it (Q5/Q6). An unlimited-life
    //       tree only grows (Q14). A tree already dying of age never drinks.
    //   jungle tree (wet native)  does not drink (the jungle is the water); it bursts at its end of life (Q11).
    // ════════════════════════════════════════════════════════════════════
    public static class RM_TreeLife
    {
        public const int Step = 2000;   // one Plant.TickLong
        public const int DefaultLitresPerSpill = 400;   // FlowWorks' litresPerFilth default (liquid_litres_2026-10-16.md)

        private static readonly AccessTools.FieldRef<Plant, int> ageRef = AccessTools.FieldRefAccess<Plant, int>("ageInt");

        /// <summary>The last drink (proof read-out only).</summary>
        public static RM_DrinkResult LastDrink;
        public static float LastDrinkLitres;
        public static bool LastDrinkWasSpill;

        public static int AgeOf(Plant p) => ageRef(p);
        public static void SetAge(Plant p, int age) => ageRef(p) = age;

        private static System.Reflection.FieldInfo spillLitresField;
        private static bool spillLitresResolved;

        /// <summary>Litres one spill filth stands for: FlowWorks' own setting (RM_MachinerySettings.litresPerFilth) when FlowWorks
        /// is loaded, else its default. Read reflection-soft: no FlowWorks dependency.</summary>
        public static int LitresPerSpill
        {
            get
            {
                if (!spillLitresResolved)
                {
                    spillLitresResolved = true;
                    try
                    {
                        System.Type t = AccessTools.TypeByName("RimMandrake.FlowWorks.Machinery.RM_MachinerySettings");
                        spillLitresField = t != null ? AccessTools.Field(t, "litresPerFilth") : null;
                    }
                    catch (System.Exception e)
                    {
                        Log.Warning("[RM ExplosiveGrowth] FlowWorks spill size unreadable; trees take " + DefaultLitresPerSpill + " L a spill: " + e.Message);
                        spillLitresField = null;
                    }
                }
                if (spillLitresField != null)
                {
                    try
                    {
                        if (spillLitresField.GetValue(null) is int v && v > 0) return v;
                    }
                    catch (System.Exception)
                    {
                        spillLitresField = null;
                    }
                }
                return DefaultLitresPerSpill;
            }
        }

        /// <summary>A spill (not a rain puddle: that is the rain's visible reason, read as the rain) of a liquid this tree
        /// accepts, on a cell where water counts.</summary>
        private static Filth SpillOn(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
        {
            if (!ExplosiveGrowthSettings.spillWaterEnabled || accepts == null || comp.NoWaterHere || comp.IsSuppressed(c, now)) return null;
            ThingDef puddle = RM_ExplosiveGrowthDefOf.RM_Filth_RainPuddle;
            List<Thing> things = c.GetThingList(comp.map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Filth f && f.def != puddle && !f.Destroyed
                    && RM_ExplosiveGrowthRegistry.FilthLiquids.TryGetValue(f.def, out string liquid) && accepts.Contains(liquid))
                    return f;
            }
            return null;
        }

        /// <summary>One TickLong of a tree's life. True when the tree burst (the caller skips vanilla's TickLong).</summary>
        public static bool OnTickLong(Plant plant, RM_PlantProfile prof, RM_MapComponent_ExplosiveGrowth comp)
        {
            if (!comp.TreeRulesHere(plant, prof)) return false;
            PlantProperties pp = plant.def.plant;
            bool limited = pp.LimitedLifespan;
            int lifespan = pp.LifespanTicks;

            if (prof.archetype == RM_Archetype.WetNative)
            {
                if (!ExplosiveGrowthSettings.treeBurstEnabled || !RM_ExplosiveGrowthKernel.JungleEndOfLife(ageRef(plant), Step, limited, lifespan))
                    return false;
                RM_TopResolver.TreeBurst(plant, prof, comp, waterDriven: false);
                return plant.Destroyed || !plant.Spawned;
            }

            if (!ExplosiveGrowthSettings.treeDrinkEnabled) return false;
            int age = ageRef(plant);
            if (!limited && plant.Growth >= RM_ExplosiveGrowthKernel.MatureGrowth) return false;   // Q14: grown and immortal
            if (limited && age > lifespan) return false;                                           // dying of age: it falls

            int now = Find.TickManager.TicksGame;
            IntVec3 c = plant.Position;
            // A spill is drunk whole and used up. With water use off nothing is used up, so a spill is read as a continuous
            // source (else the same spill would be drunk every 2000 ticks). Water is read first: most trees stand dry.
            Filth spill = ExplosiveGrowthSettings.waterUseEnabled ? SpillOn(comp, c, prof.liquids, now) : null;
            float litres;
            if (spill != null) litres = spill.thickness * (float)LitresPerSpill;
            else if (RM_WetSources.IsWet(comp, c, prof.liquids, now))
                litres = RM_ExplosiveGrowthKernel.ContinuousDrinkLitres(Step, ExplosiveGrowthSettings.treeDrinkLitresPerDay);
            else return false;
            if (!(litres > 0f)) return false;
            if (!(plant.GrowthRate > 0f)) return false;   // dark, cold, blighted: it cannot take the water up now

            RM_DrinkResult d = RM_ExplosiveGrowthKernel.Drink(plant.Growth, age, pp.growDays, limited, lifespan, litres,
                ExplosiveGrowthSettings.treeLitresPerDayOfLife);
            LastDrink = d;
            LastDrinkLitres = litres;
            LastDrinkWasSpill = spill != null;
            if (spill != null) spill.Destroy();
            if (d.growth != plant.Growth) plant.Growth = d.growth;
            ageRef(plant) = d.age;

            if (spill != null)
            {
                // The swell tell, once per drink event: "it drank and grew".
                FleckMaker.WaterSplash(plant.DrawPos, plant.Map, 1.4f, 2f);
                comp.Dirty(c);
            }

            if (d.waterDeath && ExplosiveGrowthSettings.treeBurstEnabled)
            {
                RM_TopResolver.TreeBurst(plant, prof, comp, waterDriven: true);
                return plant.Destroyed || !plant.Spawned;
            }
            return false;
        }
    }
}
