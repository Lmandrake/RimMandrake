// What the salvage rule owes, run against the real files (or a mutant of them) through the generated Variants.cs. Prints one line per
// variant: `VARIANT <name> GREEN` or `VARIANT <name> RED <first broken clause>`. selftest_salvage_rule.py reads those lines.
using System;
using System.Collections.Generic;
using System.Linq;
using PipeSystem;
using RimMandrake.WreckedMachines;
using RimWorld;
using Verse;

namespace SalvageExec
{
    public abstract class Paths
    {
        public abstract List<Thing> YieldOfThing(Thing item);
        public abstract List<Thing> YieldOfDef(ThingDef def, ThingDef stuff);
        public abstract void Place(Thing stack, IntVec3 cell, Map map);
        public abstract VanillaFurnitureExpandedFactory.ResultWorker_Smelt Worker();
        public abstract void Postfix(Process process, ThingWithComps machine, List<Thing> outThings);
        public abstract void Cremate(Thing ingredient, Map map);
    }

    public static class Oracle
    {
        private static readonly ThingDef Steel = Material("Steel", 75), Cloth = Material("Cloth", 75), Devilstrand = Material("DevilstrandCloth", 75),
            Components = Material("ComponentIndustrial", 10), Wood = new ThingDef { defName = "WoodLog", stackLimit = 75, isStuff = true, stuffSmeltable = false };

        private static readonly ThingDef Parka = new ThingDef { defName = "Apparel_Parka", MadeFromStuff = true, costStuffCount = 80, stackLimit = 1 },
            Armor = new ThingDef { defName = "Apparel_Flak", costList = { (Steel, 60), (Cloth, 40) }, smeltProducts = { (Components, 13) }, stackLimit = 1 },
            Rifle = new ThingDef { defName = "Gun_Rifle", costList = { (Steel, 400) }, stackLimit = 1 },
            Slag = new ThingDef { defName = "ChunkSlag", costList = { (Steel, 8) }, stackLimit = 20 },
            Sculpture = new ThingDef { defName = "Sculpture", smeltable = false, costList = { (Steel, 80) }, stackLimit = 1 };

        private static ThingDef Material(string name, int limit) => new ThingDef { defName = name, stackLimit = limit, isStuff = true };

        private static void Check(bool ok, string clause)
        {
            if (!ok) throw new Exception(clause);
        }

        private static Dictionary<ThingDef, int> Sum(IEnumerable<Thing> stacks)
        {
            var totals = new Dictionary<ThingDef, int>();
            foreach (Thing t in stacks) totals[t.def] = totals.GetValueOrDefault(t.def) + t.stackCount;
            return totals;
        }

        private static bool Same(Dictionary<ThingDef, int> a, Dictionary<ThingDef, int> b) => a.Count == b.Count && a.All(kv => b.GetValueOrDefault(kv.Key) == kv.Value);

        private static string Show(Dictionary<ThingDef, int> t) => string.Join(",", t.OrderBy(kv => kv.Key.defName).Select(kv => kv.Key + "=" + kv.Value));

        /// <summary>What vanilla pays for this item: the engine's method over every unit.</summary>
        private static Dictionary<ThingDef, int> Vanilla(Thing item)
        {
            var all = new List<Thing>();
            if (item.Smeltable) for (int i = 0; i < item.stackCount; i++) all.AddRange(item.EngineYield());
            return Sum(all);
        }

        private static Thing Item(ThingDef def, ThingDef stuff, int count = 1) => new ThingWithComps { def = def, Stuff = stuff, stackCount = count };

        private static Apparel Worn(ThingDef def, ThingDef stuff) => new Apparel { def = def, Stuff = stuff };

        private static void Reset()
        {
            Thing.Rolls = null;
            GenPlace.Placed.Clear();
            GenPlace.Crowded = false;
            GenStuff.Default = Cloth;
            WreckedMachinesSettings.smeltersFollowSalvageRule = true;
            WreckedMachinesSettings.cremateWithoutStripping = true;
        }

        /// <summary>One smelter cycle, as the donor's process runs it: the worker is asked three times, a full hopper retries, then it pays.</summary>
        private static List<Thing> SmelterCycle(Paths paths, Process process, ThingWithComps machine, int fullHopperRetries)
        {
            var worker = paths.Worker();
            for (int retry = 0; retry < fullHopperRetries; retry++)
            {
                worker.GetResult(process);
                worker.GetCount(process);
                paths.Postfix(process, machine, new List<Thing>());
                Check(GenPlace.Placed.Count == 0, "smelter: a full hopper paid something before the first stack landed");
            }
            var paid = new List<Thing>();
            ThingDef first = worker.GetResult(process);
            int count = worker.GetCount(process);
            Check(first == worker.GetResult(process), "smelter: the worker changed its answer inside one cycle");
            List<Thing> outThings = null;
            if (first != null)
            {
                Thing placed = ThingMaker.MakeThing(first, null, count);
                outThings = new List<Thing> { placed };
                paid.Add(placed);
            }
            paths.Postfix(process, machine, outThings);
            Check(GenPlace.Placed.All(t => t.PositionHeld.x == machine.InteractionCell.x), "smelter: the remainder did not land at the machine");
            Check(GenPlace.Placed.All(t => t.Map == machine.Map), "smelter: the remainder landed on another map");
            paid.AddRange(GenPlace.Placed);
            GenPlace.Placed.Clear();
            return paid;
        }

        private static Dictionary<ThingDef, int> Smelt(Paths paths, ThingDef def, ThingDef stuff, int retries = 0)
        {
            var process = new Process { Item = def, ItemStuff = stuff };
            return Sum(SmelterCycle(paths, process, new ThingWithComps { Spawned = true, InteractionCell = new IntVec3(7), Map = new Map() }, retries));
        }

        private static Corpse CorpseWith(Thing worn, Thing held, Thing carried)
        {
            var pawn = new Pawn { apparel = new Pawn_ApparelTracker(), equipment = new Pawn_EquipmentTracker(), inventory = new Pawn_InventoryTracker() };
            if (worn != null) pawn.apparel.WornApparel.Add((Apparel)worn);
            if (held != null) pawn.equipment.AllEquipmentListForReading.Add((ThingWithComps)held);
            if (carried != null) pawn.inventory.innerContainer.Add(carried);
            return new Corpse { InnerPawn = pawn, PositionHeld = new IntVec3(3) };
        }

        private static Dictionary<ThingDef, int> Burn(Paths paths, Corpse corpse)
        {
            var map = new Map();
            paths.Cremate(corpse, map);
            Check(corpse.Destroyed, "cremation: the corpse was not consumed");
            Check(GenPlace.Placed.All(t => t.Map == map), "cremation: gear landed on another map");
            Check(GenPlace.Placed.All(t => t.PositionHeld.x == 3), "cremation: gear did not land at the corpse's cell");
            Dictionary<ThingDef, int> paid = Sum(GenPlace.Placed);
            GenPlace.Placed.Clear();
            return paid;
        }

        public static void Run(Paths paths)
        {
            Reset();
            // The rule is SmeltProducts: per-cost materials, fixed products, every unit, stuff read, legal stacks, unspawned and alive.
            foreach (Thing item in new[] { Item(Armor, null), Item(Rifle, null), Item(Parka, Devilstrand), Item(Parka, Steel), Item(Slag, null, 17) })
            {
                Dictionary<ThingDef, int> vanilla = Vanilla(item);
                Check(vanilla.Count > 0, "sanity: the fake pays nothing for " + item.def);
                List<Thing> yielded = paths.YieldOfThing(item);
                Check(Same(Sum(yielded), vanilla), $"rule: {item.def} pays {Show(Sum(yielded))}, SmeltProducts gives {Show(vanilla)}");
                Check(yielded.All(t => t.stackCount >= 1 && t.stackCount <= t.def.stackLimit), "rule: a stack is outside the def's limit");
                Check(yielded.All(t => !t.Spawned && !t.Destroyed), "rule: a yielded stack is already spawned or dead");
            }
            Check(paths.YieldOfThing(Item(Armor, null)).Count(t => t.def == Components) == 2, "rule: 13 components at limit 10 are not two stacks");
            Check(Same(Sum(paths.YieldOfThing(Item(Slag, null, 17))), new Dictionary<ThingDef, int> { [Steel] = 34 }), "rule: a stack of 17 at 2 steel each does not pay 34");

            // Not smeltable: nothing, by the def or by the stuff; and nulls.
            Check(paths.YieldOfThing(null).Count == 0, "rule: a null item pays");
            Check(paths.YieldOfThing(Item(Sculpture, null)).Count == 0, "rule: an unsmeltable def pays");
            Check(paths.YieldOfThing(Item(Parka, Wood)).Count == 0, "rule: an unsmeltable stuff pays");
            Check(paths.YieldOfDef(null, null).Count == 0, "rule: a null def pays");
            Check(paths.YieldOfDef(Parka, Wood).Count == 0, "rule: an unsmeltable stuff pays by def");

            // The def path reads the stuff it is given, defaults only when given none, and takes none for a stuffless def.
            Check(Same(Sum(paths.YieldOfDef(Parka, Devilstrand)), Vanilla(Item(Parka, Devilstrand))), "rule: the def path ignored the stuff it was given");
            Check(Same(Sum(paths.YieldOfDef(Parka, null)), Vanilla(Item(Parka, Cloth))), "rule: the def path did not default the stuff");
            Check(Same(Sum(paths.YieldOfDef(Armor, Steel)), Vanilla(Item(Armor, null))), "rule: a stuffless def was built with a stuff");

            // Place: on the map, at the cell; a crowded spot still spawns it.
            Thing stack = ThingMaker.MakeThing(Steel);
            var here = new Map();
            paths.Place(stack, new IntVec3(5), here);
            Check(stack.Spawned && !stack.Destroyed && stack.PositionHeld.x == 5 && stack.Map == here && GenPlace.Placed.Contains(stack), "place: the stack did not land");
            GenPlace.Placed.Clear();
            GenPlace.Crowded = true;
            stack = ThingMaker.MakeThing(Steel);
            paths.Place(stack, new IntVec3(5), here);
            Check(stack.Spawned && !stack.Destroyed && stack.Map == here && stack.PositionHeld.x == 5, "place: a crowded spot lost the stack");
            Reset();

            // Apparel returns the same on every path: the vanilla smelter (the engine), our smelters, the crematorium worn, held and carried.
            foreach ((ThingDef def, ThingDef stuff) in new[] { (Armor, (ThingDef)null), (Parka, Devilstrand), (Parka, Steel) })
            {
                Dictionary<ThingDef, int> vanilla = Vanilla(Item(def, stuff));
                Dictionary<ThingDef, int> smelted = Smelt(paths, def, stuff);
                Check(Same(smelted, vanilla), $"smelter: {def}/{stuff} pays {Show(smelted)}, the rule gives {Show(vanilla)}");
                Check(Same(Smelt(paths, def, stuff, 3), vanilla), $"smelter: {def}/{stuff} over a full-hopper retry pays differently");
                Dictionary<ThingDef, int> worn = Burn(paths, CorpseWith(Worn(def, stuff), null, null));
                Check(Same(worn, vanilla), $"cremation: worn {def}/{stuff} pays {Show(worn)}, the rule gives {Show(vanilla)}");
                Dictionary<ThingDef, int> carried = Burn(paths, CorpseWith(null, null, Worn(def, stuff)));
                Check(Same(carried, vanilla), $"cremation: carried {def}/{stuff} pays {Show(carried)}, the rule gives {Show(vanilla)}");
            }
            Dictionary<ThingDef, int> rifle = Vanilla(Item(Rifle, null));
            Check(Same(Smelt(paths, Rifle, null), rifle), "smelter: a weapon pays differently from the rule");
            Check(Same(Burn(paths, CorpseWith(null, Item(Rifle, null), null)), rifle), "cremation: a held weapon pays differently from the rule");

            // All three pockets at once, and the corpse goes either way.
            var everything = new Dictionary<ThingDef, int>(Vanilla(Item(Armor, null)));
            foreach (KeyValuePair<ThingDef, int> kv in rifle) everything[kv.Key] = everything.GetValueOrDefault(kv.Key) + kv.Value;
            everything[Slag.costList[0].def] += 2 * 5;
            Check(Same(Burn(paths, CorpseWith(Worn(Armor, null), Item(Rifle, null), Item(Slag, null, 5))), everything), "cremation: worn, held and carried together do not add up");
            Check(Burn(paths, new Corpse { InnerPawn = new Pawn() }).Count == 0, "cremation: a corpse with no trackers pays");
            Check(Burn(paths, CorpseWith(null, null, Item(Sculpture, null))).Count == 0, "cremation: unsmeltable gear pays");
            var meat = new ThingWithComps { def = Slag };
            paths.Cremate(meat, new Map());
            Check(meat.Destroyed && GenPlace.Placed.Count == 0, "cremation: a non-corpse ingredient paid or stayed");

            // Any corpse: random pockets, so no clause holds only for the shapes written above. Each load also smelts alone to the same materials.
            var dice = new Random(5);
            (ThingDef def, ThingDef stuff)[] loads = { (Armor, null), (Rifle, null), (Parka, Devilstrand), (Parka, Steel), (Parka, Wood), (Sculpture, null) };
            for (int i = 0; i < 300; i++)
            {
                var corpse = new Corpse { Spawned = dice.Next(2) == 0, PositionHeld = new IntVec3(3), InnerPawn = new Pawn { apparel = new Pawn_ApparelTracker(), equipment = new Pawn_EquipmentTracker(), inventory = new Pawn_InventoryTracker() } };
                if (dice.Next(4) == 0) corpse.InnerPawn.apparel = null;     // a tracker may be absent, and the other pockets still pay
                if (dice.Next(4) == 0) corpse.InnerPawn.equipment = null;
                if (dice.Next(4) == 0) corpse.InnerPawn.inventory = null;
                var owed = new Dictionary<ThingDef, int>();
                void Owe((ThingDef def, ThingDef stuff) load, int units)
                {
                    foreach (KeyValuePair<ThingDef, int> kv in Vanilla(Item(load.def, load.stuff))) owed[kv.Key] = owed.GetValueOrDefault(kv.Key) + kv.Value * units;
                }
                for (int n = corpse.InnerPawn.apparel == null ? 0 : dice.Next(6); n > 0; n--)
                {
                    (ThingDef def, ThingDef stuff) load = loads[dice.Next(loads.Length)];
                    corpse.InnerPawn.apparel.WornApparel.Add(Worn(load.def, load.stuff));
                    Owe(load, 1);
                }
                for (int n = corpse.InnerPawn.equipment == null ? 0 : dice.Next(3); n > 0; n--)
                {
                    (ThingDef def, ThingDef stuff) load = loads[dice.Next(loads.Length)];
                    corpse.InnerPawn.equipment.AllEquipmentListForReading.Add((ThingWithComps)Item(load.def, load.stuff));
                    Owe(load, 1);
                }
                for (int n = corpse.InnerPawn.inventory == null ? 0 : dice.Next(6); n > 0; n--)
                {
                    (ThingDef def, ThingDef stuff) load = loads[dice.Next(loads.Length)];
                    int units = 1 + dice.Next(4);
                    corpse.InnerPawn.inventory.innerContainer.Add(dice.Next(2) == 0 ? Item(load.def, load.stuff, units) : new Apparel { def = load.def, Stuff = load.stuff, stackCount = units });
                    Owe(load, units);
                }
                Dictionary<ThingDef, int> burned = Burn(paths, corpse);
                Check(Same(burned, owed), $"cremation: corpse {i} pays {Show(burned)}, the rule gives {Show(owed)}");
            }
            foreach ((ThingDef def, ThingDef stuff) load in loads)
                Check(Same(Smelt(paths, load.def, load.stuff, dice.Next(3)), Vanilla(Item(load.def, load.stuff))), $"smelter: {load.def}/{load.stuff} differs from the rule");

            // The toggle: off, the gear stays the corpse's and nothing lands.
            WreckedMachinesSettings.cremateWithoutStripping = false;
            Check(Burn(paths, CorpseWith(Worn(Armor, null), Item(Rifle, null), Item(Slag, null))).Count == 0, "cremation: the toggle off still paid");
            Reset();

            // An unsmeltable load: the process gets nothing to place, resets, and the next load starts clean on the same process.
            var process = new Process { Item = Parka, ItemStuff = Wood };
            var machine = new ThingWithComps { Spawned = true, InteractionCell = new IntVec3(7), Map = new Map() };
            Check(SmelterCycle(paths, process, machine, 0).Count == 0, "smelter: an unsmeltable load paid");
            process.Item = Armor;
            process.ItemStuff = null;
            Check(Same(Sum(SmelterCycle(paths, process, machine, 0)), Vanilla(Item(Armor, null))), "smelter: a process did not recover from an empty cycle");
            Dictionary<ThingDef, int> armor = Vanilla(Item(Armor, null));
            int before = Thing.SmeltCalls;
            Check(Same(Sum(SmelterCycle(paths, process, machine, 0)), armor), "smelter: a second cycle on one process paid differently");
            Check(Thing.SmeltCalls == before + 1, "smelter: a paid plan was kept for the next cycle instead of rolling afresh");

            // The load changed under a held plan: the old plan is gone, and the new load pays.
            var swapped = new Process { Item = Armor };
            paths.Worker().GetResult(swapped);
            swapped.Item = Rifle;
            Check(Same(Sum(SmelterCycle(paths, swapped, machine, 0)), Vanilla(Item(Rifle, null))), "smelter: a plan outlived the load it was made for");
            var restuffed = new Process { Item = Parka, ItemStuff = Devilstrand };
            paths.Worker().GetResult(restuffed);
            restuffed.ItemStuff = Steel;
            Check(Same(Sum(SmelterCycle(paths, restuffed, machine, 0)), Vanilla(Item(Parka, Steel))), "smelter: a plan outlived the stuff it was made for");

            // Smelter off: the donor answers and we place nothing.
            WreckedMachinesSettings.smeltersFollowSalvageRule = false;
            var off = new Process { Item = Armor };
            Check(paths.Worker().GetCount(off) == 1 && paths.Worker().GetResult(off) == Steel, "smelter: the setting off did not hand back to the donor");
            paths.Postfix(off, machine, new List<Thing> { ThingMaker.MakeThing(Steel) });
            Check(GenPlace.Placed.Count == 0, "smelter: the setting off still placed the remainder");

            // Switched off during a retry: the donor paid this cycle, so our held plan pays nothing.
            WreckedMachinesSettings.smeltersFollowSalvageRule = true;
            var midway = new Process { Item = Armor };
            paths.Worker().GetResult(midway);
            WreckedMachinesSettings.smeltersFollowSalvageRule = false;
            paths.Postfix(midway, machine, new List<Thing> { ThingMaker.MakeThing(Steel) });
            Check(GenPlace.Placed.Count == 0, "smelter: a plan held across the switch-off was still paid");
            WreckedMachinesSettings.smeltersFollowSalvageRule = true;
            Check(Same(Sum(SmelterCycle(paths, midway, machine, 0)), Vanilla(Item(Armor, null))), "smelter: a plan dropped at the switch-off poisoned the next load");
            Reset();

            // Random rolls: every question in a cycle sees one plan, so what was reported is what was paid, whatever the rolls.
            Thing.Rolls = new Random(1);
            var fine = new ThingDef { defName = "Apparel_Fine", costList = { (Steel, 7), (Cloth, 9), (Devilstrand, 5) }, stackLimit = 1 };
            for (int i = 0; i < 200; i++)
            {
                var roll = new Process { Item = fine };
                int calls = Thing.SmeltCalls;
                Dictionary<ThingDef, int> paid = Sum(SmelterCycle(paths, roll, machine, i % 3));
                Check(Thing.SmeltCalls == calls + 1, "smelter: one cycle rolled the rule more than once");
                foreach ((ThingDef material, int cost) in fine.costList)
                {
                    int got = paid.GetValueOrDefault(material);
                    Check(got == cost / 4 || got == cost / 4 + 1, $"smelter: {material} paid {got} of a {cost} cost");
                }
            }
            Reset();
        }
    }

    public static class Program
    {
        public static int Main()
        {
            foreach ((string name, Paths paths) in Variants.All)
            {
                try
                {
                    Oracle.Run(paths);
                    Console.WriteLine("VARIANT " + name + " GREEN");
                }
                catch (Exception e)
                {
                    Console.WriteLine("VARIANT " + name + " RED " + e.Message.Replace('\n', ' '));
                }
            }
            return 0;
        }
    }
}
