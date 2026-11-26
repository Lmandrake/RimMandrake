using System.Collections.Generic;
using System.Globalization;

namespace RimMandrake.Biomes
{
    // The per-biome lists of RM_WorldLook, parsed with no engine type in sight, so that
    // BiomesShell/selftest_world_sea_lists.py can compile this file alone and run it.
    //
    // Film overrides (SEA_FILMS_TUNE_PER_SEA_CHILL_UNLIT): "<biome>=off" or "<biome>=<factor>", comma separated. The factor
    // multiplies both sea films' alpha on that biome's water tiles; off = 0 = no films. An unlisted biome reads 1.
    //
    // Swirl and glass lists (TWILIGHT_GLASS_WIRE_INTO_SWIRL_LAYER): "<biome>=<texture>[@<widths>]", comma separated.
    // <widths> = tile widths (centre to centre) per repeat of the texture; without it the entry takes the global swirl scale.
    public static class RM_WorldLookLists
    {
        public struct Entry
        {
            public string biome;
            public string texture;
            public float widthsPerRepeat;   // 0 = use the global scale
        }

        public static float FilmScale(string overrides, string biome)
        {
            if (string.IsNullOrEmpty(overrides) || string.IsNullOrEmpty(biome)) return 1f;
            float scale = 1f;
            foreach (string pair in overrides.Split(','))
            {
                string[] kv = pair.Split('=');
                if (kv.Length != 2 || kv[0].Trim() != biome) continue;
                string v = kv[1].Trim();
                if (v == "off") scale = 0f;
                else if (float.TryParse(v, NumberStyles.Float, CultureInfo.InvariantCulture, out float f) && f >= 0f && !float.IsInfinity(f))
                    scale = f;
                // a malformed value is ignored: the biome keeps the films it had
            }
            return scale;
        }

        public static List<Entry> Entries(string list)
        {
            var outList = new List<Entry>();
            foreach (string pair in (list ?? "").Split(','))
            {
                string[] kv = pair.Split('=');
                if (kv.Length != 2) continue;
                string biome = kv[0].Trim(), tex = kv[1].Trim();
                float widths = 0f;
                int at = tex.IndexOf('@');
                if (at >= 0)
                {
                    if (!float.TryParse(tex.Substring(at + 1).Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out widths)
                        || widths <= 0f || float.IsInfinity(widths))
                        widths = 0f;
                    tex = tex.Substring(0, at).Trim();
                }
                if (biome.Length == 0 || tex.Length == 0) continue;
                outList.Add(new Entry { biome = biome, texture = tex, widthsPerRepeat = widths });
            }
            return outList;
        }

        // Texture repeats per world unit. tileWidth = centre-to-centre width of one tile in world units.
        public static float UvScale(float widthsPerRepeat, float tileWidth, float fallback)
        {
            if (widthsPerRepeat <= 0f || tileWidth <= 0f) return fallback;
            return 1f / (widthsPerRepeat * tileWidth);
        }
    }
}
