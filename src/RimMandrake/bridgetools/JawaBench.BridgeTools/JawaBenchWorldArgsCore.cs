// JawaBenchWorldArgsCore.cs - the Verse-free argument parsing behind the world tools
// (JawaBenchWorldTools.cs): tile-id lists and 'from-to' ranges, plain integer id lists
// (world object ids), and the finite-number check every float argument goes through.
//
// Kept free of RimWorld/Unity references ON PURPOSE: bridgetools/WorldArgsSelfTest compiles
// THIS production file into a plain net8.0 harness (src/RimMandrake/Utils/selftest_world_args_core.py),
// so a `using Verse;` here breaks that build - the guard rail working.
//
// Why it exists (review 2026-10-20, D1/D5/D6): eight tools each hand-rolled
//   for (int i = Math.Min(a, b); i <= Math.Max(a, b); i++) ids.Add(i);
// on the MAIN THREAD. "0-2147483647" never terminated (i++ wraps, i <= int.MaxValue is always
// true) and "0-2000000000" allocated gigabytes before any id was checked - either one froze
// the game. Six of them also dropped a non-numeric token without a word, so a typo'd id
// cleared nothing and still reported success. One parser, bounded by the grid, that says
// what it dropped.

using System;
using System.Collections.Generic;
using System.Globalization;

namespace JawaBench.BridgeTools
{
    public static class JawaBenchWorldArgsCore
    {
        /// <summary>Hard ceiling on ids one call may name, whatever the grid size. The
        /// largest planet RimWorld generates is well under this; it bounds a hostile or
        /// mistaken 'tiles' list the grid clamp alone cannot.</summary>
        public const int MaxIdsPerCall = 250000;

        /// <summary>
        /// Parse a comma-separated id list plus an optional inclusive 'from-to' range into
        /// tile ids on a grid of <paramref name="tilesCount"/> tiles. Order is kept and
        /// duplicates are kept (world_links_set walks the list as a path).
        /// Every id that is dropped is NAMED in <paramref name="errors"/>: a non-numeric
        /// token, an id off the grid, the clipped part of a range, a malformed range, or an
        /// oversize request. Never allocates beyond the grid or <paramref name="maxIds"/>.
        /// Empty tokens ("1,,2", a trailing comma) carry no id and are skipped silently.
        /// </summary>
        public static List<int> ParseTileIds(string tiles, string range, int tilesCount,
                                             List<string> errors, int maxIds = MaxIdsPerCall)
        {
            var ids = new List<int>();
            if (errors == null) errors = new List<string>();
            if (maxIds < 1) maxIds = 1;
            if (tilesCount <= 0)
            {
                errors.Add("The grid has no tiles (TilesCount " + tilesCount + ").");
                return ids;
            }
            int last = tilesCount - 1;

            if (!string.IsNullOrEmpty(tiles))
            {
                foreach (var raw in tiles.Split(','))
                {
                    var part = raw.Trim();
                    if (part.Length == 0) continue;
                    int v;
                    if (!int.TryParse(part, NumberStyles.Integer, CultureInfo.InvariantCulture, out v))
                    { errors.Add("Not a tile id: '" + part + "'"); continue; }
                    if (v < 0 || v > last)
                    { errors.Add("Tile " + v + " out of range 0.." + last + "."); continue; }
                    if (ids.Count >= maxIds)
                    {
                        errors.Add("Too many tile ids: more than " + maxIds + " in one call; the rest were not read.");
                        break;
                    }
                    ids.Add(v);
                }
            }

            if (!string.IsNullOrEmpty(range))
            {
                var bits = range.Split('-');
                int a, b;
                if (bits.Length != 2
                    || !int.TryParse(bits[0].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out a)
                    || !int.TryParse(bits[1].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out b))
                {
                    errors.Add("Bad range '" + range + "', expected 'from-to' with non-negative ids.");
                    return ids;
                }
                int lo = Math.Min(a, b), hi = Math.Max(a, b);
                if (hi < 0 || lo > last)
                {
                    errors.Add("Range " + lo + "-" + hi + " lies entirely outside the grid 0.." + last + "; nothing taken from it.");
                    return ids;
                }
                int clo = Math.Max(lo, 0), chi = Math.Min(hi, last);
                if (clo != lo || chi != hi)
                    errors.Add("Range " + lo + "-" + hi + " clipped to " + clo + "-" + chi + " (grid is 0.." + last + ").");
                // chi <= last < int.MaxValue, so neither the count nor the loop can overflow.
                long count = (long)chi - clo + 1;
                if (ids.Count + count > maxIds)
                {
                    errors.Add("Range " + clo + "-" + chi + " names " + count + " tiles; with the " + ids.Count +
                               " listed ids that exceeds the " + maxIds + "-id limit per call. Nothing taken from the range.");
                    return ids;
                }
                for (int i = clo; i <= chi; i++) ids.Add(i);
            }
            return ids;
        }

        /// <summary>
        /// Parse a comma-separated list of non-tile integer ids (world object ids). Keeps
        /// order and duplicates; names every token that is not an integer in
        /// <paramref name="errors"/>; stops at <paramref name="maxIds"/> with an error.
        /// </summary>
        public static List<int> ParseIntList(string csv, string what, List<string> errors, int maxIds = MaxIdsPerCall)
        {
            var ids = new List<int>();
            if (errors == null) errors = new List<string>();
            if (string.IsNullOrEmpty(csv)) return ids;
            if (maxIds < 1) maxIds = 1;
            foreach (var raw in csv.Split(','))
            {
                var part = raw.Trim();
                if (part.Length == 0) continue;
                int v;
                if (!int.TryParse(part, NumberStyles.Integer, CultureInfo.InvariantCulture, out v))
                { errors.Add("Not " + (what ?? "an id") + ": '" + part + "'"); continue; }
                if (ids.Count >= maxIds)
                {
                    errors.Add("Too many ids: more than " + maxIds + " in one call; the rest were not read.");
                    break;
                }
                ids.Add(v);
            }
            return ids;
        }

        /// <summary>NaN and +/-Infinity pass every `v &lt; lo || v &gt; hi` guard and every
        /// clamp unchanged, then land in the live world. float.IsFinite is not on the
        /// game's runtime, hence the two checks.</summary>
        public static bool IsFinite(float v)
        {
            return !float.IsNaN(v) && !float.IsInfinity(v);
        }

        /// <summary>Invariant-culture float parse that REFUSES "NaN", "Infinity" and
        /// out-of-float-range text ("1e999" parses to Infinity on modern runtimes).</summary>
        public static bool TryParseFiniteFloat(string s, out float v)
        {
            if (!float.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out v)) return false;
            if (!IsFinite(v)) { v = 0f; return false; }
            return true;
        }

        /// <summary>Names the non-finite members of a set of optional float arguments,
        /// e.g. "elevation=NaN"; empty when all are finite or absent.</summary>
        public static List<string> NonFinite(params KeyValuePair<string, float?>[] args)
        {
            var bad = new List<string>();
            if (args == null) return bad;
            foreach (var kv in args)
                if (kv.Value.HasValue && !IsFinite(kv.Value.Value))
                    bad.Add(kv.Key + "=" + kv.Value.Value.ToString(CultureInfo.InvariantCulture));
            return bad;
        }
    }
}
