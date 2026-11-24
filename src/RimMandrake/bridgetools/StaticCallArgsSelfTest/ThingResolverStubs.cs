using System.Collections.Generic;
using Verse;

namespace Verse
{
    internal sealed class Thing
    {
        public string ThingID;
        public int thingIDNumber;
    }

    internal sealed class ListerThings
    {
        public readonly List<Thing> AllThings = new List<Thing>();
    }

    internal sealed class Map
    {
        public readonly ListerThings listerThings = new ListerThings();
        public int Index => 0;
    }

    internal static class Find
    {
        public static Map CurrentMap;
        public static List<Map> Maps;
    }
}

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        internal static Thing ResolveThingForTest(string a, out string foundAt)
        {
            return StaticCallResolveThing(a, out foundAt);
        }
    }
}
