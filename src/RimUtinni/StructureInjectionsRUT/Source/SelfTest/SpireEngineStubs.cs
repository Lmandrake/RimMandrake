using System;
using System.Collections.Generic;

// SPIRE_DUNGEONS_MERGE_DARK_TOWER: just enough engine for the real SpireEntry.cs to compile and run
// offline. Nothing here ships. The stand-in attitude component below follows the real GetStage, which
// selftest_spire_one_building.py pins in the Rust Cathedral source.
namespace Verse
{
    public class Map
    {
        public int uniqueID;
        public List<MapComponent> components = new List<MapComponent>();
    }

    public abstract class MapComponent
    {
    }

    public class Game
    {
        public readonly List<GameComponent> components = new List<GameComponent>();

        public T GetComponent<T>() where T : GameComponent
        {
            foreach (GameComponent comp in components)
            {
                if (comp is T found)
                {
                    return found;
                }
            }
            return null;
        }
    }

    public static class Current
    {
        public static Game Game;
    }

    public abstract class GameComponent
    {
        public virtual void ExposeData()
        {
        }

        public virtual void GameComponentTick()
        {
        }
    }

    public class TickManager
    {
        public int TicksGame;
    }

    public static class Find
    {
        public static readonly List<Map> Maps = new List<Map>();
        public static readonly TickManager TickManager = new TickManager();
    }

    public static class Scribe_Values
    {
        public static readonly Dictionary<string, object> Saved = new Dictionary<string, object>();

        public static void Look<T>(ref T value, string label, T defaultValue = default(T), bool forceSave = false)
        {
            if (Saved.TryGetValue(label, out object stored))
            {
                value = (T)stored;
            }
            else
            {
                Saved[label] = value;
            }
        }
    }

    public struct IntVec3
    {
    }

    public struct TargetInfo
    {
        public TargetInfo(IntVec3 cell, Map map)
        {
        }
    }

    public struct DamageInfo
    {
    }

    public enum DestroyMode
    {
        Vanish,
    }

    public class Thing
    {
        public bool Spawned = true;
        public Map Map;
        public IntVec3 Position;

        public bool IsHashIntervalTick(int interval)
        {
            return Find.TickManager.TicksGame % interval == 0;
        }

        public void Destroy(DestroyMode mode)
        {
            Spawned = false;
        }
    }

    public abstract class CompProperties
    {
        public Type compClass;
    }

    public abstract class ThingComp
    {
        public Thing parent;

        public virtual void PostPreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
        {
            absorbed = false;
        }

        public virtual void CompTick()
        {
        }
    }

    public class MessageTypeDef
    {
    }

    public static class Messages
    {
        public static void Message(string text, TargetInfo target, MessageTypeDef type, bool historical)
        {
        }
    }
}

namespace RimWorld
{
    public static class MessageTypeDefOf
    {
        public static Verse.MessageTypeDef NeutralEvent = new Verse.MessageTypeDef();
    }
}

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    public static class StructureInjectionsRUTSettings
    {
        public static bool spireEntryGated = true;
    }
}

namespace RimMandrake.RustCathedral.Hum
{
    // On every map, like the real one (Map.FillComponents); the biome decides what it answers.
    public class RM_MapComponent_BiomeAttitude : Verse.MapComponent
    {
        public bool cathedralGround;
        public int stage;

        public static int GetStage(Verse.Map map)
        {
            foreach (Verse.MapComponent comp in map.components)
            {
                if (comp is RM_MapComponent_BiomeAttitude attitude)
                {
                    return attitude.cathedralGround ? attitude.stage : -1;
                }
            }
            return -1;
        }
    }
}
