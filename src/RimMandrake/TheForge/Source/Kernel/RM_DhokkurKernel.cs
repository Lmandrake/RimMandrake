// Verse-free kernel of the dhokkur's ways (FORGE_DHOKKUR_WAYS_1): the sealed/awake transition, the path-wear book (passes,
// cooldown, polish, fade) and the wall-shove fall-back chain. RM_ForgeDhokkurWays.cs calls these with the same expressions;
// SelfTest/TheForgeFuzz.cs compiles this file alone (no Verse/RimWorld/UnityEngine).
using System;
using System.Collections.Generic;

namespace RimMandrake.TheForge
{
    public enum DhokkurTransition { None = 0, Wake = 1, Seal = 2 }
    public enum ShoveOutcome { None = 0, Moved = 1, Minified = 2, Damaged = 3 }

    public static class RM_DhokkurKernel
    {
        public const float TicksPerDay = 60000f;

        // Compares this check's sealed state with the last one seen. The very first check only records.
        public static DhokkurTransition Transition(bool seenState, bool wasSealed, bool sealedNow, bool rainingNow)
        {
            if (!seenState || sealedNow == wasSealed) return DhokkurTransition.None;
            if (!sealedNow && rainingNow) return DhokkurTransition.Wake;
            if (sealedNow) return DhokkurTransition.Seal;
            return DhokkurTransition.None;
        }

        public static int Passes(int setting) { return Math.Max(1, setting); }
        public static int FadePeriodTicks(float days) { return Math.Max(1, (int)Math.Round(days * TicksPerDay)); }

        // Mode 0 = move intact, falling back to 1 = minify-and-drop, falling back to 2 = damage. The setting picks where the
        // chain starts. move / minify / damage are the world's doing; minify returns false when the building cannot be minified.
        public static ShoveOutcome Shove(int modeSetting, bool is1x1, bool canReceiveTarget, bool minifiable, Func<bool> minify,
            float damagePctSetting, Action move, Action<float> damage)
        {
            int mode = Math.Min(2, Math.Max(0, modeSetting));
            if (mode == 0 && is1x1 && canReceiveTarget)
            {
                move();
                return ShoveOutcome.Moved;
            }
            if (mode <= 1 && minifiable && minify())
            {
                return ShoveOutcome.Minified;
            }
            float pct = Math.Min(1f, Math.Max(0f, damagePctSetting));
            if (pct <= 0f) return ShoveOutcome.None;
            damage(pct);
            return ShoveOutcome.Damaged;
        }
    }

    /// <summary>Cell index -> wear passes, and the tick each cell was last worn.</summary>
    public sealed class RM_WearBook
    {
        // Plain fields (not properties) so the component can hand them straight to Scribe_Collections by ref.
        public Dictionary<int, int> Wear = new Dictionary<int, int>();
        public Dictionary<int, int> LastWorn = new Dictionary<int, int>();

        // A step on cell i: at most one pass per cooldown. Returns true when the cell should now be polished.
        public bool Walked(int i, int now, int cooldownTicks, int passesSetting, Func<bool> canPolishNow)
        {
            if (LastWorn.TryGetValue(i, out int last) && now - last < cooldownTicks) return false;
            LastWorn[i] = now;
            Wear.TryGetValue(i, out int w);
            Wear[i] = ++w;
            return w >= RM_DhokkurKernel.Passes(passesSetting) && canPolishNow();
        }

        // One pass lost per fade period unwalked; unpolish(i) is asked for every cell that dropped under the threshold while
        // polished (returns nothing, the world removes the terrain). Returns the number of passes lost.
        public int Fade(int now, int periodTicks, int passesSetting, Func<int, bool> isPolished, Action<int> unpolish, out int unpolished)
        {
            unpolished = 0;
            int lost = 0;
            var keys = new List<int>(Wear.Keys);
            foreach (int i in keys)
            {
                int last = LastWorn.TryGetValue(i, out int l) ? l : 0;
                if (now - last < periodTicks) continue;
                LastWorn[i] = now; // the next pass is lost one period later
                int w = Wear[i] - 1;
                lost++;
                if (w < RM_DhokkurKernel.Passes(passesSetting) && isPolished(i))
                {
                    unpolish(i);
                    unpolished++;
                }
                if (w <= 0)
                {
                    Wear.Remove(i);
                    LastWorn.Remove(i);
                }
                else
                {
                    Wear[i] = w;
                }
            }
            return lost;
        }
    }
}
