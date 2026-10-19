// Verse-free kernel of big creatures against slots, thin walls and roofs (BIG_CREATURES_DESIGN_WALLS_AND_SLOTS, phase 1).
// Design: design/RimMandrake/big_creatures_walls_and_slots_2026-10-18.md §3 (breadth B, passage width P), §4 (squeeze), §5 (the
// recommended combination, built here), exploits X1..X8. Owner answers by card 2026-10-18 (all six §8 questions): package yes;
// thin walls BREAK THROUGH now (walk-over is phase 2); titans step over trenches narrower than B/4; the thrumbo class (B 2) also
// breaks thin walls, default ON (a deviation from §5 item 8, kept as a setting); roofed wall x1.5 HP and 2/3 damage; squeeze x2
// slower at half width.
//
// His words, 2026-10-18: "If a large creature is trapped by thin wooden walls around it, it walks through them effortlessly; if
// the walls were as thick as it is, no longer. I like squeezing through logic if at least half its width: slowing, not a stop."
//
// SelfTest/WallsSlotsFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib.
using System;
using System.Collections.Generic;

namespace RimMandrake.HugeThings
{
    /// <summary>A gap's band against the creature's passage width P (§5.2).</summary>
    public enum GapBand
    {
        /// <summary>S &gt;= P: walked normally.</summary>
        Walk = 0,
        /// <summary>0.5 P &lt;= S &lt; P: squeezed through, slowed, straight only.</summary>
        Squeeze = 1,
        /// <summary>S &lt; 0.5 P: "something way down there"; the gap is ignored and the wall around it is judged as a wall.</summary>
        TooNarrow = 2,
    }

    /// <summary>What a creature does at one crossing of built wall (§5.3, §5.4).</summary>
    public enum CrossVerdict
    {
        /// <summary>Nothing to cross.</summary>
        Open = 0,
        /// <summary>T &gt;= hold line x B: it does not try (any material, roof never changes this).</summary>
        Hold = 1,
        /// <summary>Summed HP within the trample budget: the walls break, it does not stop (x1.5 step).</summary>
        BreakThrough = 2,
        /// <summary>Everything in between: the clearing job, one body-wide blow a second.</summary>
        Smash = 3,
        /// <summary>The route digs natural rock, or a protected building, there: never broken (rock is never damaged, ever).</summary>
        Forbidden = 4,
    }

    /// <summary>One crossing, analysed: thickness, layers, summed HP.</summary>
    public sealed class CrossingInfo
    {
        /// <summary>T: wall layers in the densest B-deep stretch along the chosen axis.</summary>
        public int Thickness;
        /// <summary>The axis the layers are counted on: 0 x, 1 z, 2 x+z, 3 x-z.</summary>
        public int Axis;
        /// <summary>Summed HP: per layer the strongest cell (roofed HP counted x roofHpFactor), over every layer of the crossing.</summary>
        public float HpSum;
        /// <summary>Layers in the whole crossing.</summary>
        public int Layers;
        /// <summary>Layer index of each cell, 0 = nearest the creature.</summary>
        public int[] LayerOf;
    }

    public static class WallsSlots
    {
        // ---- shipped defaults (the owner's card answers and §5's PROVISIONAL numbers); Mod Settings carry each one --------------
        public const float DefaultSqueezeAtHalf = 2f;          // card 6: x2 slower at half width
        public const float DefaultTrampleBudgetPerBreadth = 100f;
        public const float DefaultBlowPerBreadth = 20f;        // final damage a blow, after every multiplier
        public const float DefaultHoldLine = 1f;               // T >= 1.0 B holds
        public const float DefaultRoofHpFactor = 1.5f;         // card 5
        public const float DefaultRoofDamageFactor = 2f / 3f;  // card 5
        public const float ScrapeDamage = 20f;                 // §5.6, final
        public const int ScrapeCellIntervalTicks = 60;         // at most once a second per cell
        public const int SmashIntervalTicks = 60;              // one blow a second
        public const int MaxBlowsPerLayer = 40;
        public const float BreakThroughStepFactor = 1.5f;      // the step through costs x1.5
        public const float TrenchStepFraction = 0.25f;         // card 3: steps over trenches narrower than B/4
        public const int ConfinedAreaPerP2 = 6;                // restless while its district is under 6 x P^2 cells
        public const int MaxSqueezeCells = 30;                 // a squeeze run longer than this is not a gap, it is a tunnel
        public const int CrossingNodeCap = 80;                 // the probe walks at most this many path nodes

        // PROVISIONAL (BENCH draft): restlessness rates per in-game day (60000 ticks).
        public const float RestlessRisePerDayPerCause = 1f;    // confined, or hungry: full in a day; both: half a day
        public const float RestlessFallPerDay = 0.5f;
        public const int TicksPerDay = 60000;

        public static bool Finite(float v) => !float.IsNaN(v) && !float.IsInfinity(v);

        /// <summary>The rule is a sub-behaviour of titan clearing (the same path-start hook): master, wake, clearing and its own.</summary>
        public static bool Active(bool giantAnimals, bool wake, bool clearing, bool wallsSlots) => giantAnimals && wake && clearing && wallsSlots;

        /// <summary>§3: B = max(1, round(sqrt(body size))), halves rounding up (the pit's width rule); a positive per-def override wins.</summary>
        public static int Breadth(float bodySize, int overrideCells)
        {
            if (overrideCells > 0) return overrideCells;
            if (!Finite(bodySize) || bodySize <= 0f) return 1;
            int b = (int)Math.Floor(Math.Sqrt(bodySize) + 0.5);
            return b < 1 ? 1 : b;
        }

        /// <summary>§1: P = max(B, the collision footprint edge): breadth for rules, never narrower than the body that collides.</summary>
        public static int PassageWidth(int breadth, int footprintEdge) => Math.Max(Math.Max(1, breadth), Math.Max(1, footprintEdge));

        /// <summary>The narrowest gap a creature of passage width P squeezes: ceil(P / 2).</summary>
        public static int MinSqueeze(int p) => (Math.Max(1, p) + 1) / 2;

        public static GapBand Gap(int slot, int p)
        {
            p = Math.Max(1, p);
            if (slot >= p) return GapBand.Walk;
            if (slot >= 1 && 2 * slot >= p) return GapBand.Squeeze;
            return GapBand.TooNarrow;
        }

        /// <summary>§4: cost x (1 + (k - 1) x 2 x (1 - S/P)) with k the slowdown at half width (2 by his card): x2 at half width,
        /// x1.5 at three quarters, x1 at full width. Never a stop; a gap below half width has no squeeze cost (it is not a gap).</summary>
        public static float SqueezeCost(int slot, int p, float atHalf)
        {
            p = Math.Max(1, p);
            float k = SaneSqueezeAtHalf(atHalf);
            if (slot >= p) return 1f;
            if (Gap(slot, p) != GapBand.Squeeze) return float.PositiveInfinity;
            return 1f + (k - 1f) * 2f * (1f - (float)slot / p);
        }

        public static float SaneSqueezeAtHalf(float k) => !Finite(k) ? DefaultSqueezeAtHalf : (k < 1f ? 1f : (k > 4f ? 4f : k));

        /// <summary>The hold line in layers for breadth B: ceil(holdLine x B), at least 1.</summary>
        public static int HoldThickness(int breadth, float holdLine)
        {
            float h = !Finite(holdLine) ? DefaultHoldLine : Math.Max(0.25f, holdLine);
            int t = (int)Math.Ceiling(h * Math.Max(1, breadth) - 1e-4);
            return t < 1 ? 1 : t;
        }

        /// <summary>The widest creature a wall run of this thickness holds (the wall's own inspect line).</summary>
        public static int StopsUpTo(int thickness, float holdLine)
        {
            int b = 0;
            for (int cand = 1; cand <= 64; cand++)
                if (thickness >= HoldThickness(cand, holdLine)) b = cand; else break;
            return b;
        }

        public static float TrampleBudget(int breadth, float perBreadth) => Math.Max(0f, Finite(perBreadth) ? perBreadth : DefaultTrampleBudgetPerBreadth) * Math.Max(1, breadth);

        /// <summary>Final damage of one smash blow on one wall cell: blowPerBreadth x B, a roofed wall takes the roof factor of it.</summary>
        public static float BlowDamage(int breadth, bool roofed, float perBreadth, float roofDamageFactor)
        {
            float d = Math.Max(0f, Finite(perBreadth) ? perBreadth : DefaultBlowPerBreadth) * Math.Max(1, breadth);
            return roofed ? d * SaneRoofDamage(roofDamageFactor) : d;
        }

        public static float SaneRoofHp(float f) => !Finite(f) ? DefaultRoofHpFactor : (f < 1f ? 1f : (f > 3f ? 3f : f));
        public static float SaneRoofDamage(float f) => !Finite(f) ? DefaultRoofDamageFactor : (f < 0.25f ? 0.25f : (f > 1f ? 1f : f));

        /// <summary>HP a wall cell counts against the trample budget: its HP, x the roof factor when it really holds a roof.</summary>
        public static float CountedHp(float hp, bool roofed, float roofHpFactor) => Math.Max(0f, Finite(hp) ? hp : 0f) * (roofed ? SaneRoofHp(roofHpFactor) : 1f);

        /// <summary>
        /// §1 "roofed": a wall that really holds a roof: on at least one side, at least half of the cells within 2 of it are roofed
        /// (one roofed corner cell is not a load path, X4). Each side is given as (roofed cells, cells in bounds).
        /// </summary>
        public static bool RoofedWall(int roofedA, int totalA, int roofedB, int totalB)
        {
            bool a = totalA > 0 && 2 * roofedA >= totalA;
            bool b = totalB > 0 && 2 * roofedB >= totalB;
            return a || b;
        }

        /// <summary>
        /// §5.3 / §5.4: the verdict on one crossing. Hold first (physical thickness, any material, roof never changes it), then rock
        /// or a protected building on the route (never broken there), then the thrumbo-class switch (card 4: B 2 breaks too unless
        /// turned off), then the trample budget (summed counted HP) decides break through or smash.
        /// </summary>
        public static CrossVerdict Decide(int breadth, int thickness, float hpSum, bool forbiddenCell, bool breadth2Breaks,
                                          float holdLine, float budgetPerBreadth)
        {
            if (thickness <= 0) return CrossVerdict.Open;
            if (breadth <= 1) return CrossVerdict.Hold;                 // B 1 is vanilla: the rule never applies
            if (thickness >= HoldThickness(breadth, holdLine)) return CrossVerdict.Hold;
            if (forbiddenCell) return CrossVerdict.Forbidden;
            if (breadth == 2 && !breadth2Breaks) return CrossVerdict.Hold;
            if (!Finite(hpSum) || hpSum < 0f) return CrossVerdict.Smash;
            return hpSum <= TrampleBudget(breadth, budgetPerBreadth) ? CrossVerdict.BreakThrough : CrossVerdict.Smash;
        }

        /// <summary>Does a creature break through or smash at all (vs hold): the verdicts that start a clearing job.</summary>
        public static bool Breaks(CrossVerdict v) => v == CrossVerdict.BreakThrough || v == CrossVerdict.Smash;

        /// <summary>Projection of a cell on axis a: 0 x, 1 z, 2 x+z, 3 x-z.</summary>
        public static int Project(int axis, int x, int z)
        {
            switch (axis)
            {
                case 0: return x;
                case 1: return z;
                case 2: return x + z;
                default: return x - z;
            }
        }

        /// <summary>
        /// The axes a crossing may be measured on: those within 45 degrees of the travel direction (dx, dz), so a wall is never
        /// measured along its own length (a corridor's flanks count deep) and a diagonal approach is measured across the wall,
        /// not along the diagonal (X8); a diagonal axis only for a diagonal approach (within 22.5 degrees). A zero direction allows
        /// every axis.
        /// </summary>
        public static bool AxisAllowed(int axis, int dx, int dz)
        {
            if (dx == 0 && dz == 0) return true;
            double ang = Math.Atan2(dz, dx);
            double axisAng = axis == 0 ? 0 : axis == 1 ? Math.PI / 2 : axis == 2 ? Math.PI / 4 : -Math.PI / 4;
            double d = Math.Abs(ang - axisAng) % Math.PI;
            if (d > Math.PI / 2) d = Math.PI - d;
            // An orthogonal axis within 45 degrees (a diagonal approach is measured across the wall it meets); a diagonal axis only
            // within 22.5 degrees (a straight approach is never measured on the diagonal, which reads a narrow deep strip thin).
            return d <= (axis >= 2 ? Math.PI / 8 : Math.PI / 4) + 1e-6;
        }

        /// <summary>
        /// §1 T and X1 / X8: the crossing is the set of wall cells the body's swept area meets along its route, from first contact
        /// until it is clear. Its layers are the distinct projections on an axis; T is the number of layers inside the densest
        /// B-deep window (on a diagonal axis a layer is 1/sqrt2 of a cell, so the window is B sqrt2 layers wide and the count is
        /// scaled back to cells). Gapped layers within the creature's own length add up; a deep wall of anything reaches B. The
        /// axis is the allowed one (AxisAllowed) giving the thinnest reading; HP sums the strongest cell of each layer over the
        /// whole crossing. Layers are numbered from the creature (cx, cz) outward.
        /// </summary>
        public static CrossingInfo Analyze(int breadth, int[] xs, int[] zs, float[] countedHp, int dx, int dz, int cx, int cz)
        {
            var info = new CrossingInfo { LayerOf = new int[xs?.Length ?? 0] };
            if (xs == null || zs == null || countedHp == null || xs.Length == 0 || xs.Length != zs.Length || xs.Length != countedHp.Length)
                return info;
            int b = Math.Max(1, breadth);
            int bestT = int.MaxValue, bestAxis = -1;
            for (int axis = 0; axis < 4; axis++)
            {
                if (!AxisAllowed(axis, dx, dz)) continue;
                int t = AxisThickness(axis, b, xs, zs);
                if (t < bestT) { bestT = t; bestAxis = axis; }
            }
            if (bestAxis < 0) { bestAxis = 0; bestT = AxisThickness(0, b, xs, zs); }
            info.Thickness = bestT;
            info.Axis = bestAxis;
            // layers on the chosen axis, nearest the creature first
            int c = Project(bestAxis, cx, cz);
            var values = new SortedDictionary<int, float>();
            var byDist = new List<int>();
            for (int i = 0; i < xs.Length; i++)
            {
                int v = Project(bestAxis, xs[i], zs[i]);
                float hp = Finite(countedHp[i]) ? Math.Max(0f, countedHp[i]) : 0f;
                if (!values.TryGetValue(v, out float m) || hp > m) values[v] = hp;
            }
            foreach (int v in values.Keys) byDist.Add(v);
            byDist.Sort((p, q) =>
            {
                int dp = Math.Abs(p - c), dq = Math.Abs(q - c);
                return dp != dq ? dp.CompareTo(dq) : p.CompareTo(q);
            });
            var rank = new Dictionary<int, int>();
            for (int i = 0; i < byDist.Count; i++) rank[byDist[i]] = i;
            for (int i = 0; i < xs.Length; i++) info.LayerOf[i] = rank[Project(bestAxis, xs[i], zs[i])];
            float sum = 0f;
            foreach (float hp in values.Values) sum += hp;
            info.HpSum = sum;
            info.Layers = values.Count;
            return info;
        }

        private static int AxisThickness(int axis, int b, int[] xs, int[] zs)
        {
            var set = new SortedSet<int>();
            for (int i = 0; i < xs.Length; i++) set.Add(Project(axis, xs[i], zs[i]));
            var v = new List<int>(set);
            bool diag = axis >= 2;
            int window = diag ? (int)Math.Floor(b * 1.41421356 + 0.5) : b;
            if (window < 1) window = 1;
            int best = 0, lo = 0;
            for (int hi = 0; hi < v.Count; hi++)
            {
                while (v[hi] - v[lo] >= window) lo++;
                best = Math.Max(best, hi - lo + 1);
            }
            if (!diag) return best;
            int scaled = (int)Math.Floor(best / 1.41421356 + 0.5);
            return best > 0 && scaled < 1 ? 1 : scaled;
        }

        /// <summary>A scrape lands on a flanking cell when at least the interval has passed since its last one (or it never had one).
        /// "Once per creature step" is the caller's: it scrapes only from a step.</summary>
        public static bool ScrapeDue(int lastTick, int now) => lastTick < 0 || now < lastTick || now - lastTick >= ScrapeCellIntervalTicks;

        /// <summary>X6: confined while its district (doors bound districts whether open or not) is closed off from the map edge and
        /// under 6 x P^2 cells.</summary>
        public static bool Confined(int districtCells, bool touchesMapEdge, int p)
        {
            if (touchesMapEdge || districtCells <= 0) return false;
            int pp = Math.Max(1, p);
            return districtCells < ConfinedAreaPerP2 * pp * pp;
        }

        /// <summary>§5.7: restlessness rises per cause (confined; an unmet need), falls slowly otherwise; always in [0, 1].</summary>
        public static float RestlessStep(float r, bool confined, bool needUnmet, int dtTicks)
        {
            if (!Finite(r)) r = 0f;
            r = r < 0f ? 0f : (r > 1f ? 1f : r);
            float days = Math.Max(0, dtTicks) / (float)TicksPerDay;
            int causes = (confined ? 1 : 0) + (needUnmet ? 1 : 0);
            r += causes > 0 ? causes * RestlessRisePerDayPerCause * days : -RestlessFallPerDay * days;
            return r < 0f ? 0f : (r > 1f ? 1f : r);
        }

        /// <summary>§5.7: the full rule applies at 100% restless, or while fleeing, in a hostile mental state, or hunting; with the
        /// temperament switch off it always applies.</summary>
        public static bool FullRule(bool temperamentOn, float restless, bool fleeing, bool hostileMental, bool hunting)
        {
            return !temperamentOn || restless >= 1f || fleeing || hostileMental || hunting;
        }

        /// <summary>
        /// May a creature break or smash a wall to reach this destination. The full rule: the existing clearing test (unreachable
        /// always; reachable past the detour factor). A calm creature prefers routes that break nothing: never for an unreachable
        /// destination (a calm penned grazer stays penned; restlessness, not wandering, breaks a pen), and for a reachable one only
        /// past the slider's cap (x6).
        /// </summary>
        public static bool MayBreak(bool fullRule, bool reachable, float byPawnCost, float throughCost, float factor)
        {
            if (fullRule) return TitanClearing.Worth(reachable, byPawnCost, throughCost, factor);
            if (!reachable) return false;
            return TitanClearing.Worth(true, byPawnCost, throughCost, TitanClearing.MaxDetourFactor);
        }

        /// <summary>Card 3: a titan steps over a trench narrower than B/4 (a positive width strictly below B x 0.25).</summary>
        public static bool StepsOverTrench(int breadth, int trenchWidth) => trenchWidth > 0 && trenchWidth < Math.Max(1, breadth) * TrenchStepFraction;

        /// <summary>Is the cell run [0..n) of a squeeze straight: every step one cardinal cell in the same direction.</summary>
        public static bool StraightCardinal(int[] xs, int[] zs)
        {
            if (xs == null || zs == null || xs.Length != zs.Length) return false;
            if (xs.Length < 2) return xs.Length == 1;
            int sx = xs[1] - xs[0], sz = zs[1] - zs[0];
            if (Math.Abs(sx) + Math.Abs(sz) != 1) return false;
            for (int i = 2; i < xs.Length; i++)
                if (xs[i] - xs[i - 1] != sx || zs[i] - zs[i - 1] != sz) return false;
            return true;
        }

        /// <summary>
        /// A squeeze plan over a run of cells: the narrowest slot along it must be at least half P (each cell's slot given), the
        /// run straight and cardinal, no longer than MaxSqueezeCells. Returns the ticks the run costs at ticksPerCell, or -1 when
        /// it is not a legal squeeze.
        /// </summary>
        public static float SqueezeRunTicks(int[] slots, int p, float atHalf, float ticksPerCell)
        {
            if (slots == null || slots.Length == 0 || slots.Length > MaxSqueezeCells || !Finite(ticksPerCell) || ticksPerCell < 0f) return -1f;
            float total = 0f;
            for (int i = 0; i < slots.Length; i++)
            {
                if (Gap(slots[i], p) == GapBand.TooNarrow) return -1f;
                total += ticksPerCell * SqueezeCost(slots[i], p, atHalf);
            }
            return total;
        }

        /// <summary>A Scribe-loaded or edited float into its slider range; a non-finite value falls back to the shipped default.</summary>
        public static float Sane(float v, float min, float max, float fallback)
        {
            if (!Finite(v)) v = fallback;
            return v < min ? min : (v > max ? max : v);
        }
    }
}
