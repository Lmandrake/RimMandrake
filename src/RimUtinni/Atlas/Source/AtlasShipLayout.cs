using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.Atlas
{
    // The Utinni drawn in plain shapes (placeholder until real art exists; art owed
    // is listed in UTINNI_DISCOVERY_ACHIEVEMENTS_1). All coordinates are normalized
    // to the canvas, x 0..1 aft to bow, y 0..1 top to bottom. The silhouette takes
    // its features from design/Jawa/reconciled_lore/06_the_ship.md:
    //   - a long hull with the grav-engine and its carbonite reliquary heart aft;
    //   - two forward mandibles, ASYMMETRIC: the upper arm is visibly from another
    //     wreck (different plating colour), and the lower one is "the dead prong",
    //     a broken stump that is never repaired;
    //   - factory pods slung beneath (Mill, Loom, Galley, ...);
    //   - running lights along the hull that glow only where the ship is restored
    //     (here: they light in proportion to entries found).
    public static class AtlasShipLayout
    {
        public static readonly Vector2[] Hull =
        {
            new Vector2(0.10f, 0.40f), new Vector2(0.16f, 0.30f), new Vector2(0.62f, 0.30f),
            new Vector2(0.72f, 0.38f), new Vector2(0.72f, 0.62f), new Vector2(0.62f, 0.70f),
            new Vector2(0.16f, 0.70f), new Vector2(0.10f, 0.60f),
        };

        public static readonly Vector2[] EngineBlock =
        {
            new Vector2(0.03f, 0.38f), new Vector2(0.10f, 0.36f), new Vector2(0.10f, 0.64f), new Vector2(0.03f, 0.62f),
        };

        // Upper mandible: the arm from another wreck, whole, ending in a point.
        public static readonly Vector2[] UpperMandible =
        {
            new Vector2(0.68f, 0.31f), new Vector2(0.80f, 0.20f), new Vector2(0.97f, 0.24f),
            new Vector2(0.95f, 0.27f), new Vector2(0.82f, 0.27f), new Vector2(0.73f, 0.39f),
        };

        // Lower mandible: the dead prong, a jagged stump.
        public static readonly Vector2[] LowerMandible =
        {
            new Vector2(0.73f, 0.61f), new Vector2(0.82f, 0.73f), new Vector2(0.86f, 0.72f),
            new Vector2(0.84f, 0.75f), new Vector2(0.88f, 0.77f), new Vector2(0.85f, 0.80f),
            new Vector2(0.79f, 0.80f), new Vector2(0.68f, 0.69f),
        };

        public static readonly Vector2[] DorsalSpine =
        {
            new Vector2(0.24f, 0.30f), new Vector2(0.28f, 0.22f), new Vector2(0.58f, 0.22f), new Vector2(0.62f, 0.30f),
        };

        public static readonly Vector2[] VentralPods =
        {
            new Vector2(0.22f, 0.70f), new Vector2(0.60f, 0.70f), new Vector2(0.57f, 0.80f), new Vector2(0.25f, 0.80f),
        };

        public static readonly Vector2 HeartCentre = new Vector2(0.20f, 0.50f);
        public const float HeartRadius = 0.075f; // fraction of canvas HEIGHT

        // Where each category's lamps are laid, and its label anchor.
        public static Rect RegionFor(AtlasCategory c)
        {
            switch (c)
            {
                case AtlasCategory.Creatures: return new Rect(0.76f, 0.215f, 0.17f, 0.05f);
                case AtlasCategory.Giants: return new Rect(0.76f, 0.70f, 0.08f, 0.08f);
                case AtlasCategory.Weather: return new Rect(0.29f, 0.235f, 0.28f, 0.055f);
                case AtlasCategory.Crafts: return new Rect(0.26f, 0.715f, 0.31f, 0.075f);
                case AtlasCategory.Places: return new Rect(0.30f, 0.36f, 0.11f, 0.28f);
                case AtlasCategory.Resources: return new Rect(0.43f, 0.36f, 0.11f, 0.28f);
                case AtlasCategory.Gods: return new Rect(0.56f, 0.38f, 0.14f, 0.24f);
                case AtlasCategory.Ship: return new Rect(0.15f, 0.44f, 0.10f, 0.12f);
            }
            return new Rect(0.4f, 0.4f, 0.2f, 0.2f);
        }

        // Label positions (normalized; the label is drawn centred on this point).
        public static Vector2 LabelAnchor(AtlasCategory c)
        {
            switch (c)
            {
                case AtlasCategory.Creatures: return new Vector2(0.86f, 0.15f);
                case AtlasCategory.Giants: return new Vector2(0.86f, 0.85f);
                case AtlasCategory.Weather: return new Vector2(0.43f, 0.17f);
                case AtlasCategory.Crafts: return new Vector2(0.41f, 0.85f);
                case AtlasCategory.Places: return new Vector2(0.355f, 0.335f);
                case AtlasCategory.Resources: return new Vector2(0.485f, 0.335f);
                case AtlasCategory.Gods: return new Vector2(0.63f, 0.355f);
                case AtlasCategory.Ship: return new Vector2(0.20f, 0.385f);
            }
            return new Vector2(0.5f, 0.5f);
        }

        // Spread n lamps over a region in a grid that keeps lamps square-ish.
        public static List<Vector2> LampCentres(Rect canvas, AtlasCategory c, int n)
        {
            var outList = new List<Vector2>();
            if (n <= 0) return outList;
            Rect r = ToCanvas(canvas, RegionFor(c));
            float aspect = r.width / Mathf.Max(1f, r.height);
            int cols = Mathf.Clamp(Mathf.CeilToInt(Mathf.Sqrt(n * aspect)), 1, n);
            int rows = Mathf.CeilToInt(n / (float)cols);
            float cw = r.width / cols;
            float rh = r.height / rows;
            for (int i = 0; i < n; i++)
            {
                int row = i / cols;
                int col = i % cols;
                int inRow = row == rows - 1 ? n - row * cols : cols;
                float rowOffset = (cols - inRow) * cw * 0.5f;
                outList.Add(new Vector2(r.x + rowOffset + cw * (col + 0.5f), r.y + rh * (row + 0.5f)));
            }
            return outList;
        }

        // Running lights traced along the hull outline.
        public static List<Vector2> RunningLights(Rect canvas, int count)
        {
            var pts = new List<Vector2>();
            Vector2[] poly = Hull;
            float perimeter = 0f;
            for (int i = 0; i < poly.Length; i++)
                perimeter += Vector2.Distance(ToCanvas(canvas, poly[i]), ToCanvas(canvas, poly[(i + 1) % poly.Length]));
            float step = perimeter / count;
            float acc = step * 0.5f;
            for (int i = 0; i < poly.Length && pts.Count < count; i++)
            {
                Vector2 a = ToCanvas(canvas, poly[i]);
                Vector2 b = ToCanvas(canvas, poly[(i + 1) % poly.Length]);
                float len = Vector2.Distance(a, b);
                while (acc <= len && pts.Count < count)
                {
                    pts.Add(Vector2.Lerp(a, b, acc / len));
                    acc += step;
                }
                acc -= len;
            }
            return pts;
        }

        public static Vector2 ToCanvas(Rect canvas, Vector2 p)
            => new Vector2(canvas.x + p.x * canvas.width, canvas.y + p.y * canvas.height);

        public static Rect ToCanvas(Rect canvas, Rect r)
            => new Rect(canvas.x + r.x * canvas.width, canvas.y + r.y * canvas.height, r.width * canvas.width, r.height * canvas.height);

        // ---- drawing primitives (IMGUI has no polygon fill; scanline it) ----

        public static void FillPolygon(Rect canvas, Vector2[] norm, Color color, float step = 2f)
        {
            int n = norm.Length;
            var pts = new Vector2[n];
            float minY = float.MaxValue, maxY = float.MinValue;
            for (int i = 0; i < n; i++)
            {
                pts[i] = ToCanvas(canvas, norm[i]);
                minY = Mathf.Min(minY, pts[i].y);
                maxY = Mathf.Max(maxY, pts[i].y);
            }
            var xs = new List<float>(8);
            for (float y = minY; y < maxY; y += step)
            {
                float sy = y + step * 0.5f;
                xs.Clear();
                for (int i = 0; i < n; i++)
                {
                    Vector2 a = pts[i];
                    Vector2 b = pts[(i + 1) % n];
                    if ((a.y <= sy && b.y > sy) || (b.y <= sy && a.y > sy))
                        xs.Add(a.x + (sy - a.y) / (b.y - a.y) * (b.x - a.x));
                }
                xs.Sort();
                for (int k = 0; k + 1 < xs.Count; k += 2)
                    Widgets.DrawBoxSolid(new Rect(xs[k], y, xs[k + 1] - xs[k], step), color);
            }
        }

        public static void OutlinePolygon(Rect canvas, Vector2[] norm, Color color, float width = 2f)
        {
            for (int i = 0; i < norm.Length; i++)
                Widgets.DrawLine(ToCanvas(canvas, norm[i]), ToCanvas(canvas, norm[(i + 1) % norm.Length]), color, width);
        }

        public static void FillCircle(Vector2 centre, float radius, Color color, float step = 2f)
        {
            for (float dy = -radius; dy < radius; dy += step)
            {
                float yy = dy + step * 0.5f;
                float half = Mathf.Sqrt(Mathf.Max(0f, radius * radius - yy * yy));
                Widgets.DrawBoxSolid(new Rect(centre.x - half, centre.y + dy, half * 2f, step), color);
            }
        }
    }
}
