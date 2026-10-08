// Verse-free kernel of the flood cycle (RM_MapComponent_CanyonFlood.cs): the Dry / Herald / Warned / Flooding phase machine with its
// five beats and staged chimes, the schedule with jitter, the peakstorm pull, the flood's cell search and the ledger that restores
// what the flood raised. SelfTest/FloodedCanyonFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.FloodedCanyon
{
    public enum FloodPhase : byte { Dry, Warned, Flooding, Herald }

    public sealed class FloodCfg
    {
        public bool Active = true, FiveBeats = true, ChimeStaging = true, PeakstormBias = true;
        public float ChimeLeadHours = 6f, HeraldLeadHours = 12f, FloodPeriodDays = 12f;
    }

    public sealed class FloodState
    {
        public FloodPhase Phase = FloodPhase.Dry;
        public int NextFloodTick = -1, FloodEndTick = -1, LastRecedeTick = -1, ChimeStage, HeraldBeat;
        public bool PeakstormPulled;
    }

    /// <summary>What the caller must now do in the world after one tick of the machine.</summary>
    public sealed class FloodStep
    {
        public bool SweepRefuge, ChooseSeed, StartFlood, Recede;
        public int RingChime = -1;                       // chime stage to ring, or -1
        public readonly List<int> HeraldBeats = new List<int>();
    }

    public static class RM_FloodKernel
    {
        public static readonly float[] ChimeStageFractions = { 1f, 0.5f, 0.15f };
        public const float PeakstormPullChance = 0.6f;
        public const int SweepIntervalTicks = 250;

        public static int HoursToTicks(float hours) { return Math.Max(250, (int)Math.Round(hours * 2500f)); }
        public static int DaysToTicks(float days) { return Math.Max(2500, (int)Math.Round(days * 60000f)); }

        public static bool TarruqSilenced(bool active, bool fiveBeats, FloodPhase phase, int heraldBeat)
        {
            return active && fiveBeats && ((phase == FloodPhase.Herald && heraldBeat > 3) || phase == FloodPhase.Warned || phase == FloodPhase.Flooding);
        }

        // jitterRoll(lo,hi) is Rand.RangeInclusive.
        public static void ScheduleNext(FloodState s, FloodCfg cfg, int now, Func<int, int, int> jitterRoll)
        {
            s.PeakstormPulled = false;
            int period = DaysToTicks(cfg.FloodPeriodDays);
            int jitter = jitterRoll(-period / 3, period / 3);
            s.NextFloodTick = now + Math.Max(2500, period + jitter);
        }

        // A peakstorm can pull the next flood forward once per cycle (never inside the lead the warnings need).
        public static void MaybeFollowPeakstorm(FloodState s, FloodCfg cfg, int now, bool peakstormNow, float chanceRoll, Func<int, int, int> pullRoll)
        {
            if (!cfg.PeakstormBias || s.PeakstormPulled) return;
            if (!peakstormNow) return;
            int period = DaysToTicks(cfg.FloodPeriodDays);
            if (s.LastRecedeTick >= 0 && now - s.LastRecedeTick < period / 2) return;
            if (s.NextFloodTick - now <= 60000) return;
            s.PeakstormPulled = true;
            if (!(chanceRoll < PeakstormPullChance)) return;
            int pulled = now + pullRoll(30000, 120000);
            int minTicks = HoursToTicks(cfg.ChimeLeadHours) + (cfg.FiveBeats ? HoursToTicks(cfg.HeraldLeadHours) : 0) + 2500;
            pulled = Math.Max(pulled, now + minTicks);
            if (pulled < s.NextFloodTick) s.NextFloodTick = pulled;
        }

        // One MapComponentTick. A flood that is under way when the cycle is switched off (or the biome stops qualifying) recedes at
        // once instead of leaving its water on the map for good.
        public static FloodStep Tick(FloodState s, FloodCfg cfg, int now, bool seedPending, bool peakstormNow, float peakChanceRoll,
                                     Func<int, int, int> jitterRoll, Func<int, int, int> pullRoll)
        {
            var step = new FloodStep();
            if (!cfg.Active)
            {
                if (s.Phase == FloodPhase.Flooding)
                {
                    step.Recede = true;
                    s.LastRecedeTick = now;
                    s.Phase = FloodPhase.Dry;
                    ScheduleNext(s, cfg, now, jitterRoll);
                }
                return step;
            }

            if (s.Phase != FloodPhase.Dry && now % SweepIntervalTicks == 0) step.SweepRefuge = true;

            int chimeLead = HoursToTicks(cfg.ChimeLeadHours);
            switch (s.Phase)
            {
                case FloodPhase.Dry:
                    if (s.NextFloodTick < 0) { ScheduleNext(s, cfg, now, jitterRoll); return step; }
                    if (now % 2500 == 0) MaybeFollowPeakstorm(s, cfg, now, peakstormNow, peakChanceRoll, pullRoll);
                    if (cfg.FiveBeats && now >= s.NextFloodTick - chimeLead - HoursToTicks(cfg.HeraldLeadHours))
                    {
                        step.ChooseSeed = true;
                        s.HeraldBeat = 1;
                        s.Phase = FloodPhase.Herald;
                        step.SweepRefuge = true;
                        break;
                    }
                    if (now >= s.NextFloodTick - chimeLead) EnterWarned(s, step, seedPending);
                    break;

                case FloodPhase.Herald:
                    while (s.HeraldBeat <= 3)
                    {
                        int heraldTicks = HoursToTicks(cfg.HeraldLeadHours);
                        int chimeAt = s.NextFloodTick - chimeLead;
                        float frac = 1f - (s.HeraldBeat - 1) / 3f;
                        if (now < chimeAt - (int)(heraldTicks * frac)) break;
                        step.HeraldBeats.Add(s.HeraldBeat);
                        s.HeraldBeat++;
                    }
                    if (now >= s.NextFloodTick - chimeLead) EnterWarned(s, step, seedPending);
                    break;

                case FloodPhase.Warned:
                    if (cfg.ChimeStaging && s.ChimeStage < ChimeStageFractions.Length
                        && now >= s.NextFloodTick - (int)(chimeLead * ChimeStageFractions[s.ChimeStage]))
                    {
                        step.RingChime = s.ChimeStage;
                        s.ChimeStage++;
                    }
                    if (now >= s.NextFloodTick)
                    {
                        step.StartFlood = true;
                        s.Phase = FloodPhase.Flooding;
                    }
                    break;

                case FloodPhase.Flooding:
                    if (now >= s.FloodEndTick)
                    {
                        step.Recede = true;
                        s.LastRecedeTick = now;
                        s.Phase = FloodPhase.Dry;
                        ScheduleNext(s, cfg, now, jitterRoll);
                    }
                    break;
            }
            return step;
        }

        private static void EnterWarned(FloodState s, FloodStep step, bool seedPending)
        {
            if (!seedPending) step.ChooseSeed = true;
            step.RingChime = 0;
            s.ChimeStage = 1;
            s.Phase = FloodPhase.Warned;
            step.SweepRefuge = true;
        }

        // A flood begins: end tick and how long the soil stays soaked afterwards.
        public static void Begin(FloodState s, int now, float durationHours, float soakDecayDays, out int durationTicks, out int soakTicks)
        {
            durationTicks = HoursToTicks(durationHours);
            s.FloodEndTick = now + durationTicks;
            s.HeraldBeat = 0;
            soakTicks = (s.FloodEndTick - now) + DaysToTicks(soakDecayDays);
        }

        public static int TargetCells(int mapArea) { return Math.Max(40, Math.Min(400, mapArea / 20)); }

        // ── the flood's reach: a thinned breadth-first spread over eligible cells from the seed ──
        public static List<long> FloodCells(int target, int seedX, int seedZ, bool seedValid, Func<int, int, bool> inBounds, Func<int, int, bool> eligible, Func<float> roll)
        {
            var result = new List<long>();
            if (!seedValid || !inBounds(seedX, seedZ) || !eligible(seedX, seedZ)) return result;
            var visited = new HashSet<long> { Key(seedX, seedZ) };
            var frontier = new Queue<int[]>();
            frontier.Enqueue(new[] { seedX, seedZ });
            int[] dx = { 0, 1, 0, -1 }, dz = { 1, 0, -1, 0 };
            while (frontier.Count > 0 && result.Count < target)
            {
                int[] c = frontier.Dequeue();
                if (!eligible(c[0], c[1])) continue;
                result.Add(Key(c[0], c[1]));
                for (int i = 0; i < 4; i++)
                {
                    int nx = c[0] + dx[i], nz = c[1] + dz[i];
                    if (inBounds(nx, nz) && visited.Add(Key(nx, nz)))
                        if (roll() < 0.88f) frontier.Enqueue(new[] { nx, nz });
                }
            }
            return result;
        }
        public static long Key(int x, int z) { return ((long)x << 32) ^ (uint)z; }
        public static int KeyX(long k) { return (int)(k >> 32); }
        public static int KeyZ(long k) { return (int)(k & 0xffffffffL); }

        // ── chimes walk from the far corner toward the seed ──
        public static readonly float[] ChimeLinePositions = { 0f, 0.5f, 0.85f };

        public static void FarCorner(int seedX, int seedZ, int maxX, int maxZ, out int cx, out int cz)
        {
            int[] xs = { 0, maxX, 0, maxX }, zs = { 0, 0, maxZ, maxZ };
            int best = 0;
            for (int i = 1; i < 4; i++)
            {
                long di = (long)(xs[i] - seedX) * (xs[i] - seedX) + (long)(zs[i] - seedZ) * (zs[i] - seedZ);
                long db = (long)(xs[best] - seedX) * (xs[best] - seedX) + (long)(zs[best] - seedZ) * (zs[best] - seedZ);
                if (di > db) best = i;
            }
            cx = xs[best]; cz = zs[best];
        }

        public static void ChimePoint(int stage, int seedX, int seedZ, int maxX, int maxZ, out int x, out int z)
        {
            int fx, fz;
            FarCorner(seedX, seedZ, maxX, maxZ, out fx, out fz);
            float f = ChimeLinePositions[Math.Max(0, Math.Min(ChimeLinePositions.Length - 1, stage))];
            x = (int)Math.Round(fx + (seedX - fx) * f);
            z = (int)Math.Round(fz + (seedZ - fz) * f);
            x = Math.Max(0, Math.Min(maxX, x)); z = Math.Max(0, Math.Min(maxZ, z));
        }

        // ── what a flood raised, so the recede can put it back ──
        public sealed class Ledger
        {
            public readonly List<long> Active = new List<long>();
            public readonly List<long> RaisedCells = new List<long>();
            public readonly List<int> RaisedPrior = new List<int>();

            // cells: the flood's reach. A cell dug out of the ground (excavated) is not flooded as terrain: if its driver accepts the
            // flood its prior fill is remembered and restored later, else it is left alone. Every other cell becomes flood terrain.
            public void Begin(List<long> cells, Func<long, bool> excavated, Func<long, int> fillAt, Func<long, bool> tryRaise)
            {
                Active.Clear(); RaisedCells.Clear(); RaisedPrior.Clear();
                foreach (long c in cells)
                {
                    if (excavated(c))
                    {
                        int prior = fillAt(c);
                        if (tryRaise(c)) { RaisedCells.Add(c); RaisedPrior.Add(prior); }
                        continue;
                    }
                    Active.Add(c);
                }
            }

            // Load: replace the ledger with the scribed lists (null = absent in an old save = empty).
            public void Restore(IList<long> active, IList<long> raisedCells, IList<int> raisedPrior)
            {
                Active.Clear(); RaisedCells.Clear(); RaisedPrior.Clear();
                if (active != null) Active.AddRange(active);
                if (raisedCells != null) RaisedCells.AddRange(raisedCells);
                if (raisedPrior != null) RaisedPrior.AddRange(raisedPrior);
            }

            public List<long> Wetted() { var w = new List<long>(Active); w.AddRange(RaisedCells); return w; }

            // The recede: flood terrain back to soil (only where it is still flood terrain), driver cells back to their prior fill.
            public void Recede(Func<long, bool> inBounds, Func<long, bool> stillFloodTerrain, Action<long> toSoil, Action<long, int> restoreFill)
            {
                foreach (long c in Active)
                    if (inBounds(c) && stillFloodTerrain(c)) toSoil(c);
                Active.Clear();
                int n = Math.Min(RaisedCells.Count, RaisedPrior.Count);
                for (int i = 0; i < n; i++)
                    if (inBounds(RaisedCells[i])) restoreFill(RaisedCells[i], RaisedPrior[i]);
                RaisedCells.Clear(); RaisedPrior.Clear();
            }
        }
    }
}
