// The smallest fake Verse/RimWorld that ThoughtWorker_ViewedGraffitiMark.cs compiles against: a square map of cells, each with an
// optional room, fog flag and thing list. Only the members the worker reads exist; a new one it starts reading breaks this build,
// which is the signal to extend the fake rather than to test around it. ModExtension_Graffiti, Filth_Mark and RM_GraffitiSettings are
// stand-ins carrying only the fields the worker reads (the real files need the game), so a renamed field there is not seen here.
using System;
using System.Collections.Generic;

namespace Verse
{
    public struct IntVec3 : IEquatable<IntVec3>
    {
        public int x, z;
        public IntVec3(int x, int z) { this.x = x; this.z = z; }
        public bool Equals(IntVec3 o) { return x == o.x && z == o.z; }
        public override bool Equals(object o) { return o is IntVec3 v && Equals(v); }
        public override int GetHashCode() { return x * 7919 + z; }
        public static bool operator ==(IntVec3 a, IntVec3 b) { return a.Equals(b); }
        public static bool operator !=(IntVec3 a, IntVec3 b) { return !a.Equals(b); }
    }

    public class Room
    {
        public string name;
        public Room(string name) { this.name = name; }
    }

    public class Map
    {
        public int size = 30;
        public HashSet<IntVec3> fogged = new HashSet<IntVec3>();
        public Dictionary<IntVec3, Room> rooms = new Dictionary<IntVec3, Room>();
        public Dictionary<IntVec3, List<Thing>> things = new Dictionary<IntVec3, List<Thing>>();
    }

    public static class GridsUtility
    {
        public static bool InBounds(this IntVec3 c, Map m) { return c.x >= 0 && c.z >= 0 && c.x < m.size && c.z < m.size; }
        public static bool Fogged(this IntVec3 c, Map m) { return m.fogged.Contains(c); }
        public static Room GetRoom(this IntVec3 c, Map m) { return m.rooms.TryGetValue(c, out Room r) ? r : null; }
        public static List<Thing> GetThingList(this IntVec3 c, Map m) { return m.things.TryGetValue(c, out List<Thing> l) ? l : new List<Thing>(); }
    }

    public static class GenRadial
    {
        public static IEnumerable<IntVec3> RadialCellsAround(IntVec3 center, float radius, bool useCenter)
        {
            int r = (int)Math.Ceiling(radius);
            for (int dx = -r; dx <= r; dx++)
            {
                for (int dz = -r; dz <= r; dz++)
                {
                    if (!useCenter && dx == 0 && dz == 0) continue;
                    if (dx * dx + dz * dz <= radius * radius) yield return new IntVec3(center.x + dx, center.z + dz);
                }
            }
        }
    }

    public class Def { public string defName; }

    public class DefModExtension { }

    public class ThingDef : Def
    {
        public List<DefModExtension> modExtensions = new List<DefModExtension>();
        public T GetModExtension<T>() where T : DefModExtension
        {
            foreach (DefModExtension e in modExtensions) if (e is T t) return t;
            return null;
        }
    }

    public class Thing { public ThingDef def; }

    public class Pawn : Thing
    {
        public Map Map;
        public bool Spawned;
        public IntVec3 Position;
        public RimWorld.Faction Faction;
        public RimWorld.Ideo Ideo;
    }
}

namespace RimWorld
{
    using Verse;

    public class Faction
    {
        public static Faction OfPlayer = new Faction("player");
        public string name;
        public HashSet<Faction> hostile = new HashSet<Faction>();
        public Faction(string name) { this.name = name; }
        public bool HostileTo(Faction o) { return o != null && (hostile.Contains(o) || o.hostile.Contains(this)); }
    }

    public class Ideo
    {
        public string name;
        public Ideo(string name) { this.name = name; }
    }

    public class ThoughtDef : Def { }

    public struct ThoughtState
    {
        public bool Active;
        public static implicit operator ThoughtState(bool b) { return new ThoughtState { Active = b }; }
    }

    public abstract class ThoughtWorker
    {
        public ThoughtDef def;
        protected abstract ThoughtState CurrentStateInternal(Pawn p);
        public ThoughtState CurrentState(Pawn p) { return CurrentStateInternal(p); }
    }
}

namespace RimMandrake.Graffiti
{
    using RimWorld;
    using Verse;

    public class Filth_Mark : Thing
    {
        public Pawn subject;
        public Faction makerFaction;
        public Ideo makerIdeo;
    }

    public class ModExtension_Graffiti : DefModExtension
    {
        public GraffitiVisibility visibility = GraffitiVisibility.Public;
        public ThoughtDef viewerReactionThought, onViewSubject, onViewOwnFaction, onViewSameIdeo, onViewOtherIdeo, onViewHostileMaker;
    }

    public static class RM_GraffitiSettings
    {
        public static bool paintingEnabled = true;
        public static bool viewerReactionEnabled = true;
    }
}
