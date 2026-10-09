// Verse-free kernel of the Twilight Sea's drifting light wells (RM_MapComponent_WellLedger): the well lifecycle (opening ->
// standing -> waning -> closed), the glow factor and colour step per stage, the delayed re-opening of a closed well, the
// gardener's advance and the lid-dark aging. The mod supplies the engine half (site finding, the skylight Thing, glow, letters)
// through delegates. SelfTest/TerminalBiomesFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.TerminalBiomes
{
    public enum WellStage { Opening, Standing, Waning, Closed }

    public class WellRec
    {
        public int id, x, z;
        public WellStage stage = WellStage.Opening;
        public int ageTicks, lifespanTicks;
        public bool warningLetterFired;
        public int TicksRemaining { get { return Math.Max(0, lifespanTicks - ageTicks); } }
    }

    public static class RM_WellKernel
    {
        public const int TickInterval = 250;
        public const int TicksPerDay = 60000;
        public const int OpeningTicks = TicksPerDay / 2;
        public const int WaningTicks = (int)(TicksPerDay * 1.5f);
        public const float WaningStepFraction = 0.2f;
        // TWILIGHT_WELL_LIGHT_STATE_1: four steps (0..3) spread across the 1.5-day waning window, so a well reaches
        // its last step (0.4 radius, fully cool-dead colour) before it closes. With half-day steps step 3 fell exactly
        // at close and was never seen. PROVISIONAL (auto-decided 2026-10-09, TWILIGHT_WELL_LIGHT_STATE_1): equal quarters.
        public const int WaningStepTicks = WaningTicks / 4;
        public const float BaseRadius = 6f;

        public static int TargetWellCount(int mapSizeX) { return Math.Min(6, Math.Max(3, 3 + mapSizeX / 125)); }

        // 5..9 days (a lifespan roll of 0..4), doubled on the slow cadence.
        public static int Lifespan(int roll0to4, int cadenceSetting) { return (5 + roll0to4) * TicksPerDay * (cadenceSetting == 2 ? 2 : 1); }

        public static WellStage StageOf(int ageTicks, int lifespanTicks)
        {
            int remaining = lifespanTicks - ageTicks;
            if (ageTicks < OpeningTicks) return WellStage.Opening;
            if (remaining <= 0) return WellStage.Closed;
            if (remaining <= WaningTicks) return WellStage.Waning;
            return WellStage.Standing;
        }

        // 0..3: how many quarters into the waning window.
        public static int WaningStep(int ageTicks, int lifespanTicks)
        {
            int into = WaningTicks - (lifespanTicks - ageTicks);
            int s = into / WaningStepTicks;
            return s < 0 ? 0 : (s > 3 ? 3 : s);
        }

        // Glow radius factor: ramps up while opening, full while standing, steps down 20% per waning quarter (never under 0.2).
        public static float GlowFactor(WellStage stage, int ageTicks, int lifespanTicks)
        {
            switch (stage)
            {
                case WellStage.Opening: { float f = (float)ageTicks / OpeningTicks; return f < 0f ? 0f : (f > 1f ? 1f : f); }
                case WellStage.Waning: return Math.Max(0.2f, 1f - WaningStepFraction * WaningStep(ageTicks, lifespanTicks));
                default: return 1f;
            }
        }

        // Gold -> cool-dead blend position: 0 outside waning, step/3 inside.
        public static float ColourT(WellStage stage, int ageTicks, int lifespanTicks) { return stage == WellStage.Waning ? WaningStep(ageTicks, lifespanTicks) / 3f : 0f; }
        public static float Radius(float factor) { return Math.Max(0.5f, BaseRadius * factor); }
    }

    public delegate bool WellSiteFinder(out int x, out int z);

    public sealed class WellBook<T> where T : WellRec, new()
    {
        public List<T> Wells = new List<T>();
        public List<int> Pending = new List<int>();
        public int NextId = 1;

        private readonly WellSiteFinder findSite;
        private readonly Action<T> opened, visual, closed;
        private readonly Func<T, bool> warn;
        private readonly Func<int, int> randBelow;
        private readonly Func<int> cadence;

        public WellBook(WellSiteFinder findSite, Action<T> opened, Action<T> visual, Func<T, bool> warn, Action<T> closed, Func<int, int> randBelow, Func<int> cadence)
        {
            this.findSite = findSite; this.opened = opened; this.visual = visual; this.warn = warn; this.closed = closed; this.randBelow = randBelow; this.cadence = cadence;
        }

        public T OpenNew(int x, int z)
        {
            var w = new T { id = NextId++, x = x, z = z, stage = WellStage.Opening, ageTicks = 0, lifespanTicks = RM_WellKernel.Lifespan(randBelow(5), cadence()) };
            opened(w);
            Wells.Add(w);
            return w;
        }

        // First tick: scatter the starting wells, each at a random age that is not yet waning.
        public void Initialize(int mapSizeX)
        {
            int target = RM_WellKernel.TargetWellCount(mapSizeX);
            for (int i = 0; i < target; i++)
            {
                if (!findSite(out int x, out int z)) continue;
                T w = OpenNew(x, z);
                w.ageTicks = randBelow(w.lifespanTicks - RM_WellKernel.WaningTicks);
                w.stage = RM_WellKernel.StageOf(w.ageTicks, w.lifespanTicks);
                visual(w);
            }
        }

        // A pending re-opening whose time has come opens a well at a fresh site; with no site it WAITS for the next pass
        // rather than being forgotten (a lost entry shrinks the sea's wells for good).
        public void ProcessPending(int now)
        {
            for (int i = Pending.Count - 1; i >= 0; i--)
            {
                if (now < Pending[i]) continue;
                if (!findSite(out int x, out int z)) continue;
                OpenNew(x, z);
                Pending.RemoveAt(i);
            }
        }

        public void Age(T well, int delta, int now)
        {
            if (well.stage == WellStage.Closed) return;
            well.ageTicks += delta;
            WellStage before = well.stage;
            well.stage = RM_WellKernel.StageOf(well.ageTicks, well.lifespanTicks);
            if (before != WellStage.Waning && well.stage == WellStage.Waning) well.warningLetterFired = false;
            // Retried through the whole waning window: someone who starts working near the well later still gets warned.
            if (well.stage == WellStage.Waning && !well.warningLetterFired && warn(well)) well.warningLetterFired = true;
            if (well.stage == WellStage.Opening || well.stage == WellStage.Waning) visual(well);
            else if (before == WellStage.Opening && well.stage == WellStage.Standing) visual(well);
            if (before != WellStage.Closed && well.stage == WellStage.Closed)
            {
                closed(well);
                Pending.Add(now + randBelow(RM_WellKernel.TicksPerDay));
                Wells.Remove(well);
            }
        }

        // One rare tick: pending openings first, then every well ages.
        public void Tick(int now)
        {
            ProcessPending(now);
            foreach (T w in new List<T>(Wells)) Age(w, RM_WellKernel.TickInterval, now);
        }

        // The gardener's pass: close the well nearest its end, else bring the first pending opening forward to now.
        public void GardenerAdvance(int now)
        {
            // TWILIGHT_WELL_LIGHT_STATE_1: on the frozen cadence wells never age, so the gardener closes nothing; it
            // may still bring a pending opening forward (pending openings run while frozen too).
            // PROVISIONAL (auto-decided 2026-10-09, TWILIGHT_WELL_LIGHT_STATE_1).
            bool frozen = cadence() == 0;
            // No empty-ledger early-out: an all-dark map is exactly when bringing a pending opening forward matters.
            T candidate = null;
            foreach (T w in Wells)
                if (w.stage == WellStage.Waning && (candidate == null || w.TicksRemaining < candidate.TicksRemaining)) candidate = w;
            if (candidate != null && !frozen)
            {
                candidate.ageTicks = candidate.lifespanTicks;
                Age(candidate, 0, now);
                return;
            }
            if (Pending.Count > 0)
            {
                Pending[0] = now;
                ProcessPending(now);
            }
        }

        // The lid-dark lifting heals wells unevenly: a little extra age each.
        public void LidDarkEnded(int now)
        {
            if (cadence() == 0) return; // frozen: wells never age (TWILIGHT_WELL_LIGHT_STATE_1)
            foreach (T w in new List<T>(Wells)) Age(w, randBelow(RM_WellKernel.TicksPerDay / 4), now);
        }
    }
}
