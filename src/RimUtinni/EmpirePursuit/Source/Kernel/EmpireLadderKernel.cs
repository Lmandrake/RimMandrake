/* EMPIRE_ESCALATION_LADDER_1 - the ladder's state machine with every engine call taken out. The map component
 * (MapComponent_EmpireSearch), the game component, the scenario part's hourly tick and the spacing patch call these
 * with the same expressions; SelfTest/Fuzz/EmpirePursuitFuzz.cs compiles this file with EmpireLadderMath.cs alone.
 * Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib: a using of those here breaks the fuzz build, which is the
 * guard rail. All numbers PROVISIONAL (see EmpireLadderMath). */
using System;

namespace RuthlessPursuingMechanoids
{
    public enum EmpireRungKind
    {
        Probe,
        Spotter,
        Strike,
        Cordon,
        Breach,
        Bombardment,
    }

    /// <summary>What the contact tick decided.</summary>
    public enum ContactOutcome { Continue, EmpireSucceeds, EmpireFails }

    /// <summary>The rung table as the ladder sees it (RUT_EmpireRungDef.ForIndex in the game).</summary>
    public interface IEmpireRungTable
    {
        bool TryGetRung(int index, out EmpireRungKind kind);
    }

    /// <summary>The settings that gate which rungs may fire.</summary>
    public struct EmpireRungGates
    {
        public bool cordonEnabled, bombardmentEnabled, probesOpen;
    }

    /// <summary>One map's ladder state (the scalar half of MapComponent_EmpireSearch).</summary>
    public sealed class EmpireLadderState
    {
        public const int NoTick = -9999999;
        public const int TicksPerDay = 60000;
        public const int StorytellerSpacingTicks = 2 * TicksPerDay;
        public const int CheckInterval = 250;

        public int nextRung = -1;           // -1 = not initialised on this map
        public bool terminal;               // top rung reached: endless waves may run
        public bool lastProbeBlind;
        public int lastLadderFireTick = NoTick;
        public int lastStorytellerRaidTick = NoTick;
        public int contactStartTick = -1;
        public int progressTicks;
        public bool anyProbeDestroyed;
        public int nextIonTick = -1;
        public int bombardTick = -1;
        public string aftermathOutcome;

        public void EnsureInit(int floor, bool probesOpen, int remembered)
        {
            if (nextRung >= 0) return;
            nextRung = EmpireLadderMath.StartingRung(floor, probesOpen, remembered);
        }

        public static bool RungEnabled(EmpireRungKind kind, EmpireRungGates g)
        {
            if (kind == EmpireRungKind.Cordon && !g.cordonEnabled) return false;
            if (kind == EmpireRungKind.Bombardment && !g.bombardmentEnabled) return false;
            if (kind == EmpireRungKind.Probe && !g.probesOpen) return false;
            return true;
        }

        /// <summary>The first enabled, defined rung at or above nextRung, or -1 when there is none.</summary>
        public int NextRungIndex(IEmpireRungTable table, EmpireRungGates gates)
        {
            int r = nextRung;
            while (r <= EmpireLadderMath.TopRung)
            {
                EmpireRungKind k;
                if (table.TryGetRung(r, out k) && RungEnabled(k, gates)) return r;
                r++;
            }
            return -1;
        }

        /// <summary>The gate in front of a firing. 0 = nothing to do (a contact is live or the ladder is terminal),
        /// n > 0 = postpone by n ticks (a storyteller Empire raid landed inside the spacing), -1 = go ahead.</summary>
        public int FireGate(bool contactLive, int now)
        {
            if (contactLive || terminal) return 0;
            int sinceStoryteller = now - lastStorytellerRaidTick;
            if (sinceStoryteller < StorytellerSpacingTicks) return StorytellerSpacingTicks - sinceStoryteller;
            return -1;
        }

        /// <summary>Nothing enabled is left to fire: the ladder is over.</summary>
        public void MarkExhausted() { terminal = true; }

        /// <summary>A rung begins: its contact state is reset.</summary>
        public void Begin(int rungIndex, int now)
        {
            nextRung = rungIndex;
            contactStartTick = now;
            progressTicks = 0;
            anyProbeDestroyed = false;
            aftermathOutcome = null;
            lastLadderFireTick = now;
        }

        /// <summary>The contact is over. Climb on an Empire success, hold on a failure. firedIndex is -1 when no rung
        /// was live. Returns true when the next rung should be scheduled (the ladder is not terminal).</summary>
        public bool Resolve(int firedIndex, bool empireSucceeded, int floor)
        {
            if (firedIndex >= 0)
            {
                nextRung = EmpireLadderMath.NextRungAfter(firedIndex, empireSucceeded, floor);
                if (firedIndex >= EmpireLadderMath.TopRung && empireSucceeded) terminal = true;
            }
            contactStartTick = -1;
            progressTicks = 0;
            nextIonTick = -1;
            aftermathOutcome = null;
            return !terminal;
        }

        // ---- the live contact, one 250-tick check -------------------------------------------------------------

        /// <summary>Probe: a sighting accumulates while any probe sees the colony; success at successTicks; failure when
        /// every probe is dead or gone, or a day past the timeout. visibilityDelta is the Visibility adjustment to apply.</summary>
        public ContactOutcome ProbeStep(bool anySees, int successTicks, bool allGone, int elapsed, int timeoutTicks, out float visibilityDelta)
        {
            visibilityDelta = 0f;
            if (anySees) progressTicks += CheckInterval;
            if (progressTicks >= successTicks)
            {
                visibilityDelta = 8f;
                lastProbeBlind = false;
                return ContactOutcome.EmpireSucceeds;
            }
            if (allGone || elapsed > timeoutTicks + TicksPerDay)
            {
                if (anyProbeDestroyed) visibilityDelta = -3f;
                lastProbeBlind = !anyProbeDestroyed;
                return ContactOutcome.EmpireFails;
            }
            return ContactOutcome.Continue;
        }

        public ContactOutcome SpotterStep(bool spotterGone, bool sees, int successTicks, int elapsed, int timeoutTicks, out float visibilityDelta)
        {
            visibilityDelta = 0f;
            if (spotterGone) return ContactOutcome.EmpireFails;
            if (sees) progressTicks += CheckInterval;
            if (progressTicks >= successTicks)
            {
                visibilityDelta = 8f;
                return ContactOutcome.EmpireSucceeds;
            }
            if (elapsed > timeoutTicks) return ContactOutcome.EmpireFails;
            return ContactOutcome.Continue;
        }

        /// <summary>Cordon: an ion volley falls when the cordon stands and its timer is due; the cordon fails when nothing
        /// stands, and succeeds once it has stood for successTicks.</summary>
        public ContactOutcome CordonStep(bool standing, int now, int volleyIntervalTicks, int elapsed, int successTicks, out bool volley)
        {
            volley = false;
            if (standing && nextIonTick > 0 && now >= nextIonTick)
            {
                volley = true;
                nextIonTick = now + volleyIntervalTicks;
            }
            if (!standing) return ContactOutcome.EmpireFails;
            if (elapsed >= successTicks) return ContactOutcome.EmpireSucceeds;
            return ContactOutcome.Continue;
        }

        /// <summary>Strike / Breach: Aftermath's verdict if it classified the battle, else the raiders' own count.</summary>
        public ContactOutcome StrikeStep(bool allDown, int elapsed, int timeoutTicks, int raiders, int deadOrDowned)
        {
            if (aftermathOutcome != null)
                return aftermathOutcome != "Repelled" ? ContactOutcome.EmpireSucceeds : ContactOutcome.EmpireFails;
            if (allDown || elapsed > timeoutTicks)
                return !EmpireLadderMath.Repelled(raiders, deadOrDowned) ? ContactOutcome.EmpireSucceeds : ContactOutcome.EmpireFails;
            return ContactOutcome.Continue;
        }

        /// <summary>Bombardment: due at bombardTick; the strike lands once, ends the ladder and counts as success.</summary>
        public bool BombardmentDue(int now)
        {
            return bombardTick > 0 && now >= bombardTick;
        }
        public void BombardmentLanded() { bombardTick = -1; terminal = true; }

        // ---- editing the rung from outside --------------------------------------------------------------------

        /// <summary>RaiseFloor on one live map: its next rung is lifted to at least the floor.</summary>
        public void ApplyFloor(int floor)
        {
            if (nextRung >= 0) nextRung = EmpireLadderMath.Clamp(nextRung, floor);
        }

        /// <summary>Ishko's Unseen Berth and anything like it: drop this map's next rung. false when the map is not initialised.
        /// revived is true when a terminal ladder came back to life (its next rung fell below the top): nothing is scheduled
        /// for it any more (Resolve schedules only while not terminal), so the caller must schedule the next rung or the
        /// ladder is silently dead for good.</summary>
        public bool LowerRung(int by, int floor, out bool revived)
        {
            revived = false;
            if (nextRung < 0) return false;
            bool wasTerminal = terminal;
            nextRung = EmpireLadderMath.Clamp(nextRung - Math.Max(0, by), floor);
            terminal = terminal && nextRung >= EmpireLadderMath.TopRung;
            revived = wasTerminal && !terminal;
            return true;
        }

        /// <summary>The permanent leak floor after a Route 6 leak or the droid line's discovery; it only ever rises.</summary>
        public static int RaisedFloor(int currentFloor, int floor)
        {
            int v = Math.Max(currentFloor, floor);
            return v < 0 ? 0 : v > EmpireLadderMath.TopRung ? EmpireLadderMath.TopRung : v;
        }

        /// <summary>The decayed remembered rung for a tile, or -1.</summary>
        public static int RememberedRung(bool rememberRungs, bool tileValid, bool hasEntry, int rung, int departedTick, int now, int ticksPerSeason, int decayPerSeason)
        {
            if (!rememberRungs || !tileValid || !hasEntry) return -1;
            float seasons = (now - departedTick) / (float)ticksPerSeason;
            return EmpireLadderMath.DecayedRung(rung, seasons, decayPerSeason);
        }

        public static bool ShouldRecordDeparture(bool tileValid, int rung) { return tileValid && rung >= 0; }

        /// <summary>The storyteller-spacing patch: a storyteller Empire raid is refused while a contact is live or inside
        /// two days of a ladder firing.</summary>
        public static bool BlockStorytellerRaid(bool contactLive, int now, int lastLadderFireTick)
        {
            return contactLive || now - lastLadderFireTick < StorytellerSpacingTicks;
        }

        public float NextIntervalFactor(float bandMultiplier, float ladderPace)
        {
            return bandMultiplier * Math.Max(0.05f, ladderPace) * EmpireLadderMath.RungIntervalFactor(nextRung, lastProbeBlind);
        }
    }

    /// <summary>The scenario part's hourly timers, as pure arithmetic.</summary>
    public static class EmpireLadderTimers
    {
        public const int TickInterval = 2500;
        public const int TicksPerHour = 2500;

        public static int TimerIntervalTick(int timer) { return (timer + TickInterval - 1) / TickInterval * TickInterval; }
        public static int TimerInterval(int interval) { return (interval / TickInterval) * TickInterval; }

        /// <summary>ScheduleLadder: the next rung's raid timer (raw delay x factor, never under one hour) and its warning timer
        /// (warningHours before the raid, never earlier than one hour from now; equal to the raid when there is no warning).</summary>
        public static void Schedule(int now, int rawDelay, float factor, float warningHours, out int raidTimer, out int warnTimer)
        {
            int raw = Math.Max(rawDelay, TickInterval);
            raidTimer = now + Math.Max((int)Math.Round(raw * factor), TickInterval);
            warnTimer = warningHours > 0f
                ? Math.Max(now + TickInterval, raidTimer - (int)Math.Round(warningHours * TicksPerHour))
                : raidTimer;
        }

        /// <summary>TickLadder step 1: the warning letter for the coming rung.</summary>
        public static bool ShouldWarn(bool contactLive, bool terminal, int now, int warnTimer, int raidTimer)
        {
            int warnTick = TimerIntervalTick(warnTimer);
            int raidTick = TimerIntervalTick(raidTimer);
            return !contactLive && !terminal && now == warnTick && warnTick != raidTick;
        }

        /// <summary>TickLadder step 2: the rung itself on the raid tick.</summary>
        public static bool ShouldFire(bool contactLive, bool terminal, int now, int raidTimer)
        {
            return !contactLive && !terminal && now == TimerIntervalTick(raidTimer);
        }

        /// <summary>TickLadder step 3: the endless waves, only once the top rung has landed.</summary>
        public static bool ShouldEndless(bool terminal, bool endlessAfterTop, bool disableEndless, int now, int endlessInterval)
        {
            return terminal && endlessAfterTop && !disableEndless && now % TimerInterval(endlessInterval) == 0;
        }
    }
}
