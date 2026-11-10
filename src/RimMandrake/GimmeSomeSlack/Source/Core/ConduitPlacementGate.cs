using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>
    /// Verse-free inputs and decision for Place's no-flood fast path.
    /// Bridge conduits can lead to run members while carrying no style themselves.
    /// </summary>
    public static class ConduitPlacementGate
    {
        public readonly struct Neighbour
        {
            public readonly bool HasStoredStyle;
            public readonly bool IsBridgeConduit;

            public Neighbour(bool hasStoredStyle, bool isBridgeConduit)
            {
                HasStoredStyle = hasStoredStyle;
                IsBridgeConduit = isBridgeConduit;
            }
        }

        public static bool CanSkip(string ownLook, IEnumerable<Neighbour> neighbours) =>
            ownLook == null && neighbours.All(n => !n.HasStoredStyle && !n.IsBridgeConduit);
    }
}
