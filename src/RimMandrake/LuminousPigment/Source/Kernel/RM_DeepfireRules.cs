// Verse-free rules of LuminousPigment: coat caps and the first-coat latch, the sumptuary status engine (display and room
// scores, thought stages, the rank gates), the Beauty bonuses, per-target costs, the crowncarpet mat lifecycle, the god-delta
// tables with anti-pinning, the melee dodge inversion, the worn-glow colour blend and the "dark without our light" test.
// The mod calls these with the same expressions; SelfTest/LuminousPigmentFuzz.cs compiles this file alone, so it must stay
// free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.LuminousPigment
{
    public enum MatFate { Alive, DiedChill, DiedAge }
    public enum PaintClass { Art, Apparel, Weapon, Wall, Furniture }

    public static class RM_DeepfireRules
    {
        // ---- coats ----
        // Spec §7 maxCoats: the slider only ever LOWERS the architecture ceiling.
        public static int CoatCap(int ceiling, int setting) { return Math.Min(ceiling, setting); }
        public static bool CanAddCoat(int coats, int ceiling, int setting) { return coats < CoatCap(ceiling, setting); }
        // Spec §3.5: the first-coat bonus is once per thing, even across strip-and-reapply (bonusApplied is never reset).
        public static bool IsFirstCoat(int coats, bool bonusApplied) { return coats == 0 && !bonusApplied; }
        public static int CoatIndex(int coats, int ceiling) { return coats < 0 ? 0 : (coats > ceiling ? ceiling : coats); }

        // ---- status engine (spec §4.1) ----
        // Deepfire by comp first, then the generic StatusGoodExtension.
        public static int GoodLevel(bool hasComp, int coats, bool hasExt, int extLevel)
        {
            if (hasComp && coats > 0) return coats;
            return hasExt ? extLevel : 0;
        }
        public static int DisplayScore(int sum, int cap) { return Math.Min(sum, cap); }
        // Furniture coats plus one point per `perPoint` coated wall and floor cells (pooled).
        public static int RoomScore(int furnitureCoats, int wallCells, int floorCells, int perPoint) { return furnitureCoats + (wallCells + floorCells) / perPoint; }
        // Wearer thought stage by display score bucket 1-2 / 3-4 / 5+; -1 = inactive.
        public static int ScoreStage(int score) { return score <= 0 ? -1 : (score >= 5 ? 2 : (score >= 3 ? 1 : 0)); }
        // The four wearer/observer thoughts: a worker serves titled XOR common pawns.
        public static int WearerThoughtStage(bool statusEnabled, bool titled, bool requireTitled, int score)
        {
            if (!statusEnabled) return -1;
            if (titled != requireTitled) return -1;
            return ScoreStage(score);
        }
        public static bool WearsAboveStation(bool statusEnabled, bool selfTitled, bool otherTitled, int otherScore, int threshold)
        {
            return statusEnabled && selfTitled && !otherTitled && otherScore >= threshold;
        }
        // RM_DeepfireBedroom: titled only, -1 inactive, 0 low, 1 high.
        public static int BedroomStage(bool statusEnabled, bool titled, int score, int low, int high)
        {
            if (!statusEnabled || !titled) return -1;
            if (score >= high) return 1;
            if (score >= low) return 0;
            return -1;
        }
        // Once per faction per quadrum.
        public static bool CanImpress(bool everImpressed, int lastQuadrum, int currentQuadrum) { return !everImpressed || lastQuadrum != currentQuadrum; }

        // ---- beauty and costs (spec §3.3, §3.5) ----
        public static float BeautyBonus(float flat, float pct, int sizeCap, int sizeX, int sizeZ, float baseBeauty)
        {
            int area = Math.Max(1, sizeX * sizeZ);
            float sizeFactor = Math.Min(area, sizeCap);
            return flat * sizeFactor + pct * baseBeauty;
        }
        // +per10 per 10 coated floor cells in the room, capped.
        public static float FloorRoomBonus(float per10, float cap, int coated) { return Math.Min(per10 * (coated / 10), cap); }

        public static PaintClass ClassOf(bool isArt, bool isApparel, bool isWeapon, bool isWall)
        {
            if (isArt) return PaintClass.Art;
            if (isApparel) return PaintClass.Apparel;
            if (isWeapon) return PaintClass.Weapon;
            return isWall ? PaintClass.Wall : PaintClass.Furniture;
        }
        public static int Cost(PaintClass c, int sizeX, int sizeZ, int art, int apparel, int weapon, int wall, int furnBase, int furnPerExtra, int furnCap)
        {
            switch (c)
            {
                case PaintClass.Art: return art;
                case PaintClass.Apparel: return apparel;
                case PaintClass.Weapon: return weapon;
                case PaintClass.Wall: return wall;
            }
            int cells = Math.Max(1, sizeX * sizeZ);
            if (cells <= 1) return furnBase;
            return Math.Min(furnCap, furnBase + (cells - 1) * furnPerExtra);
        }
        // Targets are classed in the same order as costs, but art follows whichever bucket it would cost as.
        public static PaintClass PaintableClassOf(bool isApparel, bool isWeapon, bool isWall)
        {
            if (isApparel) return PaintClass.Apparel;
            if (isWeapon) return PaintClass.Weapon;
            return isWall ? PaintClass.Wall : PaintClass.Furniture;
        }

        // ---- crowncarpet mat (spec §2.2) ----
        // One rare tick of an alive mat: ages, dies in the cold, otherwise dies of old age.
        public static MatFate MatTick(ref int ticksAlive, float ambient, float chillKill, float lifeDays, int rareInterval, int ticksPerDay)
        {
            ticksAlive += rareInterval;
            if (ambient < chillKill) return MatFate.DiedChill;
            if ((float)ticksAlive >= lifeDays * ticksPerDay) return MatFate.DiedAge;
            return MatFate.Alive;
        }
        public static int HoursLeft(int ticksAlive, float lifeDays, int ticksPerDay)
        {
            float daysLeft = lifeDays - (float)ticksAlive / ticksPerDay;
            if (daysLeft < 0f) daysLeft = 0f;
            return (int)(daysLeft * 24f + 0.5f);
        }

        // ---- god deltas (spec §5.2) ----
        // Every god +like, the trio +adore, Ishko -ishkoPenalty.
        public static Dictionary<string, float> CoatTable(IList<string> gods, IList<string> trio, string ishko, float ishkoPenalty, float adore, float like)
        {
            var t = new Dictionary<string, float>();
            foreach (string g in gods)
            {
                if (g == ishko) t[g] = -ishkoPenalty;
                else if (trio.Contains(g)) t[g] = adore;
                else t[g] = like;
            }
            return t;
        }
        // The statue's god +statue (Ishko's own idol: -statue); Ishko keeps his dislike of any other idol; the rest +like.
        public static Dictionary<string, float> StatueTable(IList<string> gods, string statueGod, string ishko, float statue, float ishkoPenalty, float like)
        {
            var t = new Dictionary<string, float>();
            foreach (string g in gods)
            {
                if (g == statueGod) t[g] = g == ishko ? -statue : statue;
                else if (g == ishko) t[g] = -ishkoPenalty;
                else t[g] = like;
            }
            return t;
        }
        // After `after` first-coat events on one def, every delta shrinks to at most +-magnitude, sign kept; a delta already smaller is never enlarged and 0 stays 0.
        public static float Diminish(float amount, int priorEvents, int after, float magnitude)
        {
            if (priorEvents < after) return amount;
            if (amount == 0f) return 0f;
            float m = Math.Min(Math.Abs(amount), magnitude);
            return amount > 0f ? m : -m;
        }

        // ---- melee dodge (RM_StatPart_GlowingTarget) ----
        // Smallest x whose curve value reaches y, never above current.
        public static float InverseEvaluate(IList<float> xs, IList<float> ys, float y, float current)
        {
            if (y <= ys[0]) return Math.Min(current, xs[0]);
            for (int i = 1; i < xs.Count; i++)
            {
                if (y <= ys[i])
                {
                    if (Math.Abs(ys[i] - ys[i - 1]) < 1e-6f) return Math.Min(current, xs[i - 1]);
                    float x = xs[i - 1] + (y - ys[i - 1]) / (ys[i] - ys[i - 1]) * (xs[i] - xs[i - 1]);
                    return Math.Min(current, x);
                }
            }
            return current;
        }
        // The dodge penalty is taken off the FINAL value (after the stat's curve) then mapped back into the raw domain.
        public static float DodgeAdjust(Func<float, float> eval, IList<float> xs, IList<float> ys, float minValue, float penalty, float val)
        {
            if (xs == null || xs.Count < 2) return val - penalty;
            float final = eval(val);
            float target = Math.Max(minValue, final - penalty);
            return InverseEvaluate(xs, ys, target, val);
        }

        // ---- worn glow (spec §3.4) ----
        // One light per pawn: colour = coat-weighted blend of the glowing items' full-intensity hues, scaled by the brightest
        // coat's intensity; radius index = the highest coat count. False when nothing glows.
        public static bool WornBlend(IList<int> coats, IList<float> r, IList<float> g, IList<float> b, IList<float> intensityByCoats, int ceiling,
            out float outR, out float outG, out float outB, out int maxCoats)
        {
            outR = outG = outB = 0f; maxCoats = 0;
            float sr = 0f, sg = 0f, sb = 0f, weight = 0f;
            for (int i = 0; i < coats.Count; i++)
            {
                if (coats[i] <= 0) continue;
                sr += r[i] * coats[i]; sg += g[i] * coats[i]; sb += b[i] * coats[i];
                weight += coats[i];
                if (coats[i] > maxCoats) maxCoats = coats[i];
            }
            if (maxCoats <= 0) return false;
            float k = intensityByCoats[CoatIndex(maxCoats, ceiling)];
            outR = sr / weight * k; outG = sg / weight * k; outB = sb / weight * k;
            return true;
        }

        // Ground glow from every light but ours: accumulated colour minus our own centre-cell contribution.
        public static float OtherLightAt(bool overlit, float accR, float accG, float accB, float ownR, float ownG, float ownB, float ownRadius,
            float falloffLerp, float groundFactor, float maxNonOverlit)
        {
            if (overlit) return 1f;
            float t = 1f - 1f / Math.Max(ownRadius, 1f);
            float falloff = t + (1f - t) * falloffLerp;
            float r = Math.Max(0f, accR - ownR * falloff);
            float g = Math.Max(0f, accG - ownG * falloff);
            float b = Math.Max(0f, accB - ownB * falloff);
            float v = Math.Max(r, Math.Max(g, b)) / 255f * groundFactor;
            return Math.Min(maxNonOverlit, v);
        }
    }
}
