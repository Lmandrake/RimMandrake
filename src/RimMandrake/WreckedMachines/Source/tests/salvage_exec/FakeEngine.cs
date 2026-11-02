// The engine as RM_SalvageRule.cs and WreckedMachinesSalvage.cs see it, small enough to run in plain net8.0 so the proof EXECUTES those two
// files unmodified (SALVAGE_YIELD_UNIFY_THREE_RULES_TODAY, selftest_salvage_rule.py). The names and signatures are checked by the real
// build; the behaviour here copies decompiled 1.6 Verse/Thing.cs where it matters: Smeltable, and SmeltProducts' cost entries plus the
// def's fixed smeltProducts. Never part of the mod: no csproj of the mod compiles this directory.
using System;
using System.Collections.Generic;
using System.Linq;

namespace Verse
{
    public struct IntVec3
    {
        public int x;
        public IntVec3(int x) { this.x = x; }
    }

    public class Map { }

    public class ThingDef
    {
        public string defName;
        public bool smeltable = true;
        public bool stuffSmeltable = true;      // stuffProps.smeltable when this def is a stuff
        public bool isStuff;
        public bool MadeFromStuff;
        public int stackLimit = 75;
        public int costStuffCount;
        public List<(ThingDef def, int count)> costList = new List<(ThingDef, int)>();
        public List<(ThingDef def, int count)> smeltProducts = new List<(ThingDef, int)>();
        public override string ToString() => defName;
    }

    public class Thing
    {
        public static Random Rolls;             // null: floor; set: the engine's RoundRandom, which is why a held plan matters
        public static int SmeltCalls;

        public ThingDef def;
        public ThingDef Stuff;
        public int stackCount = 1;
        public bool Destroyed;
        public bool Spawned;
        public IntVec3 PositionHeld;
        public IntVec3 InteractionCell;
        public Map Map;

        public bool Smeltable => def.smeltable && (!def.MadeFromStuff || Stuff.stuffSmeltable);

        public virtual IEnumerable<Thing> SmeltProducts(float efficiency)
        {
            SmeltCalls++;
            var costs = new List<(ThingDef def, int count)>(def.costList);
            if (def.MadeFromStuff) costs.Add((Stuff, def.costStuffCount));
            foreach ((ThingDef material, int count) in costs)
            {
                float owed = count * 0.25f * efficiency;
                int whole = (int)owed;
                if (Rolls != null && Rolls.NextDouble() < owed - whole) whole++;
                if (whole > 0) yield return ThingMaker.MakeThing(material, null, whole);
            }
            foreach ((ThingDef material, int count) in def.smeltProducts) yield return ThingMaker.MakeThing(material, null, count);
        }

        /// <summary>What the oracle compares against, so the only direct caller in src stays the rule (selftest_salvage_rule.py, check_source).</summary>
        public IEnumerable<Thing> EngineYield() => SmeltProducts(1f);

        public void Destroy() { Destroyed = true; }
    }

    public class ThingWithComps : Thing { }

    public static class ThingMaker
    {
        public static Thing MakeThing(ThingDef def, ThingDef stuff = null) => MakeThing(def, stuff, 1);

        internal static Thing MakeThing(ThingDef def, ThingDef stuff, int count)
        {
            if (def.MadeFromStuff && stuff == null) throw new InvalidOperationException("MakeThing: " + def + " needs a stuff");
            if (!def.MadeFromStuff && stuff != null) throw new InvalidOperationException("MakeThing: " + def + " takes no stuff");
            return new ThingWithComps { def = def, Stuff = stuff, stackCount = count };
        }
    }

    public enum ThingPlaceMode { Direct, Near }

    public static class GenPlace
    {
        public static bool Crowded;
        public static List<Thing> Placed = new List<Thing>();

        public static bool TryPlaceThing(Thing thing, IntVec3 center, Map map, ThingPlaceMode mode)
        {
            if (map == null) throw new ArgumentNullException(nameof(map));
            if (Crowded || mode != ThingPlaceMode.Near) return false;
            thing.Spawned = true;
            thing.PositionHeld = center;
            thing.Map = map;
            Placed.Add(thing);
            return true;
        }
    }

    public static class GenSpawn
    {
        public static Thing Spawn(Thing thing, IntVec3 at, Map map)
        {
            if (map == null) throw new ArgumentNullException(nameof(map));
            thing.Spawned = true;
            thing.PositionHeld = at;
            thing.Map = map;
            GenPlace.Placed.Add(thing);
            return thing;
        }
    }

    public class RecipeDef { }

    public class RecipeWorker
    {
        public virtual void ConsumeIngredient(Thing ingredient, RecipeDef recipe, Map map) { ingredient.Destroy(); }
    }

    public class Pawn
    {
        public RimWorld.Pawn_ApparelTracker apparel;
        public RimWorld.Pawn_EquipmentTracker equipment;
        public RimWorld.Pawn_InventoryTracker inventory;
    }
}

namespace RimWorld
{
    using Verse;

    public class Apparel : ThingWithComps { }

    public class Pawn_ApparelTracker { public List<Apparel> WornApparel = new List<Apparel>(); }

    public class Pawn_EquipmentTracker { public List<ThingWithComps> AllEquipmentListForReading = new List<ThingWithComps>(); }

    public class Pawn_InventoryTracker { public List<Thing> innerContainer = new List<Thing>(); }

    public class Corpse : ThingWithComps { public Pawn InnerPawn; }

    public static class GenStuff
    {
        public static ThingDef Default;
        public static ThingDef DefaultStuffFor(ThingDef def) => Default;
    }
}

namespace HarmonyLib
{
    [AttributeUsage(AttributeTargets.Class)]
    public class HarmonyPatch : Attribute { public HarmonyPatch(Type type, string method) { } }
}

namespace RimMandrake.Shared
{
    [AttributeUsage(AttributeTargets.Class)]
    internal sealed class PatchFeatureAttribute : Attribute { public PatchFeatureAttribute(string label, Type settingsType, string field) { } }
}

namespace RimMandrake.WreckedMachines
{
    public static class WreckedMachinesSettings
    {
        public static bool smeltersFollowSalvageRule = true;
        public static bool cremateWithoutStripping = true;
    }
}

namespace PipeSystem
{
    using Verse;

    /// <summary>The donor's cycle, from its IL: asked for result and count, it places one stack unless the hopper is full, and a full hopper
    /// returns before ResetProcess, so the next tick starts the cycle again.</summary>
    public class Process
    {
        public ThingDef Item, ItemStuff;
        public VanillaFurnitureExpandedFactory.ResultWorker_Smelt Worker;

        public ThingDef GetLastStoredIngredient() => Item;
        public ThingDef GetStuffOfLastStoredIngredient() => ItemStuff;

        public void SpawnOrPushToNet(IntVec3 spawnPos, out List<Thing> outThings, object extractor)
        {
            outThings = null;
        }
    }
}

namespace VanillaFurnitureExpandedFactory
{
    using PipeSystem;
    using Verse;

    /// <summary>The donor rule: one material, floor 25%. A path that pays this has left the salvage rule.</summary>
    public class ResultWorker_Smelt
    {
        public virtual ThingDef GetResult(Process process) => process.Item.costList.Count > 0 ? process.Item.costList[0].def : process.ItemStuff;

        public virtual int GetCount(Process process) => 1;
    }
}
