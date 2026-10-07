using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.LanternDeeps
{
    /// <summary>
    /// The Sippers' glow-radius accounting, with no Verse type in it so the offline fuzz compiles THIS file. A glower (G) has a
    /// radius several writers touch: its own def, the aurora (<see cref="AuroraWant"/>), and the sippers drinking from it
    /// (<see cref="Pass"/>). The ledger remembers what it wrote and how much it took, and gives it back only if nobody has
    /// written the radius since; if someone has, whatever is there now is the new base.
    /// </summary>
    public sealed class SipperLedger<G> where G : class
    {
        public const float Floor = 0.25f;
        public const float WrittenTolerance = 0.01f;
        public const float ChangeTolerance = 0.05f;

        public sealed class Entry { public float written; public float reduction; }

        public readonly Dictionary<G, Entry> drunk = new Dictionary<G, Entry>();

        public int DrunkCount => drunk.Count;

        /// <summary>
        /// One pass. <paramref name="counts"/> is how many sippers sit on each lit glower. Glowers with sippers are dimmed (never
        /// below Floor of their base); glowers the ledger holds that lost their sippers get their radius back if untouched.
        /// <paramref name="registered"/> is told after a glower's radius is written so the engine can re-register it; for a
        /// restored glower it is only told when it is spawned and <paramref name="glows"/> says it is lit. Returns how many radii changed.
        /// </summary>
        public int Pass(Dictionary<G, int> counts, float cellsPerSipper, Func<G, float> radiusOf, Action<G, float> setRadius,
            Func<G, bool> spawned, Func<G, bool> glows, Action<G> registered)
        {
            int changed = 0;
            foreach (KeyValuePair<G, int> kv in counts)
            {
                G g = kv.Key;
                drunk.TryGetValue(g, out Entry e);
                // base: the radius the glower would have undrunk. If nobody else touched it since we wrote it, add our
                // reduction back; otherwise whatever it is now (the aurora's x1.75, a reset) is the new base.
                float baseR = (e != null && Math.Abs(radiusOf(g) - e.written) < WrittenTolerance) ? e.written + e.reduction : radiusOf(g);
                float red = Math.Min(baseR * (1f - Floor), kv.Value * cellsPerSipper);
                float want = baseR - red;
                if (e == null) { e = new Entry(); drunk[g] = e; }
                if (Math.Abs(radiusOf(g) - want) > ChangeTolerance)
                {
                    setRadius(g, want);
                    registered(g);
                    changed++;
                }
                // what we TOOK is the difference actually left on the glower. A reduction below the change tolerance (the
                // setting goes down to 0.02) writes nothing, and recording `red` anyway made the restore hand back light that
                // was never taken: the radius ratcheted upward on every sipper visit.
                e.written = radiusOf(g);
                e.reduction = baseR - e.written;
            }
            foreach (G g in drunk.Keys.ToList())
            {
                if (counts.ContainsKey(g)) continue;
                Entry e = drunk[g];
                drunk.Remove(g);
                // An unspawned glower (minified, carried) is restored too, just not re-registered: dropping its entry
                // unrestored left it dimmed for good when it was put down again.
                if (Math.Abs(radiusOf(g) - e.written) < WrittenTolerance)
                {
                    setRadius(g, e.written + e.reduction);
                    if (spawned(g) && glows(g)) registered(g);
                    changed++;
                }
            }
            return changed;
        }

        /// <summary>The aurora's write: the def's own radius times the multiplier while it storms, the def's radius otherwise. False when the glower is already there.</summary>
        public static bool AuroraWant(float current, float defRadius, float multiplier, bool on, out float want)
        {
            want = on ? defRadius * multiplier : defRadius;
            return Math.Abs(current - want) > 0.01f;
        }
    }
}
