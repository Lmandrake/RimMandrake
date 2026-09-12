using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 1, the transmuting sibling. Rewrites the
    // flora standing in the gas into another plant def, preserving growth —
    // the donor's "turns plants alien" mechanic, generalized to "map any
    // plant to any replacement" so it also serves as a visible, spreading
    // ground-corruption tool (source review §5).
    //
    // Configured by a GasTransmuteExtension on the gas ThingDef.
    public class Gas_Transmuting : Gas
    {
        private int ticksUntilScan;

        private GasTransmuteExtension ExtensionInt
        {
            get { return def.GetModExtension<GasTransmuteExtension>(); }
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);

            GasTransmuteExtension ext = ExtensionInt;
            if (ext == null)
            {
                Log.WarningOnce(
                    "[RM EnvironmentalHazards] " + def.defName + " uses Gas_Transmuting but carries no GasTransmuteExtension; it will expire without changing anything.",
                    def.shortHash ^ 0x5A12);
                return;
            }

            if (!respawningAfterLoad)
            {
                ticksUntilScan = Rand.RangeInclusive(1, ext.tickIntervalTicks);
            }
        }

        protected override void TickInterval(int delta)
        {
            base.TickInterval(delta);

            if (Destroyed || !Spawned)
            {
                return;
            }

            GasTransmuteExtension ext = ExtensionInt;
            if (ext == null)
            {
                return;
            }

            ticksUntilScan -= delta;
            if (ticksUntilScan > 0)
            {
                return;
            }

            ticksUntilScan = ext.tickIntervalTicks;
            ApplyEffects(ext);
        }

        public void ApplyEffects(GasTransmuteExtension ext)
        {
            if (!RM_EnvironmentalHazardsSettings.gasEffectsEnabled)
            {
                return; // mod option: gas effects disabled
            }
            Map map = Map;
            if (map == null || ext == null)
            {
                return;
            }

            IntVec3 cell = Position;
            List<Thing> things = new List<Thing>(cell.GetThingList(map));

            for (int i = 0; i < things.Count; i++)
            {
                if (!(things[i] is Plant plant) || plant.Destroyed)
                {
                    continue;
                }

                if (!HazardTargeting.PlantAffected(plant, ext.immuneThingDefs))
                {
                    continue;
                }

                ThingDef replacement = PickReplacement(plant, ext);
                if (replacement == null || replacement == plant.def)
                {
                    continue;
                }

                if (ext.chance < 1f && !Rand.Chance(ext.chance))
                {
                    continue;
                }

                Transmute(plant, replacement, cell, map);
            }
        }

        private static ThingDef PickReplacement(Plant plant, GasTransmuteExtension ext)
        {
            bool isTree = plant.def.plant != null && plant.def.plant.IsTree;

            if (isTree)
            {
                return ext.treeReplacement;
            }

            if (ext.otherReplacements == null || ext.otherReplacements.Count == 0)
            {
                return null;
            }

            // RandomElementByWeight throws on an all-zero weight set, so the
            // degenerate config is filtered rather than crashed on.
            float total = 0f;
            for (int i = 0; i < ext.otherReplacements.Count; i++)
            {
                if (ext.otherReplacements[i].thingDef != null && ext.otherReplacements[i].weight > 0f)
                {
                    total += ext.otherReplacements[i].weight;
                }
            }

            if (total <= 0f)
            {
                return null;
            }

            float roll = Rand.Range(0f, total);
            for (int i = 0; i < ext.otherReplacements.Count; i++)
            {
                WeightedThingDef entry = ext.otherReplacements[i];
                if (entry.thingDef == null || entry.weight <= 0f)
                {
                    continue;
                }

                roll -= entry.weight;
                if (roll <= 0f)
                {
                    return entry.thingDef;
                }
            }

            return null;
        }

        private static void Transmute(Plant original, ThingDef replacement, IntVec3 cell, Map map)
        {
            // Growth is carried across so a mature forest transmutes into a
            // mature forest rather than resetting to saplings — the one
            // behaviour that makes this read as corruption, not replanting.
            float growth = original.Growth;

            original.Destroy(DestroyMode.Vanish);

            Thing spawned = GenSpawn.Spawn(replacement, cell, map);
            if (spawned is Plant newPlant)
            {
                newPlant.Growth = growth;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ticksUntilScan, "ticksUntilScan", 0);
        }
    }
}
