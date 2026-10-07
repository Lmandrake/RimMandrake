// TheRot pure kernel: the hwelgrue's gut and swallow timers, the gut-mother vat's digest clock, the swallowed drive core (who carries it,
// when it pings, how it breaks), the navigator's log, the unjoining draught's sorting, and the biome score. Each used to be an inline
// expression in a comp, a world component or a recipe tangled with Verse/Unity calls; they live here so an offline fuzz (Source/TheRotFuzz)
// can drive the SAME code the game runs. NO `using Verse;` / `using UnityEngine;` may ever land in this file: the fuzz project compiles it on
// plain net8.0 and the build breaks - the guard rail working. Mathf.RoundToInt / Lerp / Clamp01 are restated with their Unity definitions
// (RoundToInt is Math.Round, round-half-even; Lerp clamps t).
using System;
using System.Collections.Generic;

namespace RimMandrake.TheRot
{
    public static class RM_TheRotKernel
    {
        public const int TicksPerHour = 2500;
        public const int TicksPerDay = 60000;

        public static float Clamp01(float v) { return v < 0f ? 0f : (v > 1f ? 1f : v); }
        public static float Lerp(float a, float b, float t) { return a + (b - a) * Clamp01(t); }

        // ================================================================= the hwelgrue's gut

        /// <summary>Ticks between castings: the setting's days, never under 2500.</summary>
        public static int CastingIntervalTicks(float days) { return Math.Max(2500, (int)Math.Round(days * TicksPerDay)); }

        /// <summary>
        /// One sweep (every sweepInterval ticks) of the digest clock. A gut with something in it counts up and a casting is due at the interval;
        /// an empty gut resets the clock. The caller resets the clock itself when it passes the casting.
        /// </summary>
        public static bool GutSweep(ref int ticksDigesting, int gutCount, int sweepInterval, int castingInterval)
        {
            if (gutCount > 0)
            {
                ticksDigesting += sweepInterval;
                return ticksDigesting >= castingInterval;
            }
            ticksDigesting = 0;
            return false;
        }

        /// <summary>A wild hwelgrue past the map cap is removed (a factioned one never is). With the biome or the creature off the cap is 0.</summary>
        public static bool OverCap(bool hasFaction, bool enabled, int cap, int others)
        {
            if (hasFaction) return false;
            return others >= (enabled ? cap : 0);
        }

        /// <summary>Extra rot progress a resting hwelgrue feeds the things around it per sweep: 0 unless the multiplier is above 1.</summary>
        public static float RotBoost(float multiplier, float rotRateAtTemperature, int sweepInterval)
        {
            float extra = multiplier - 1f;
            if (extra <= 0f) return 0f;
            if (rotRateAtTemperature <= 0f) return 0f;
            return rotRateAtTemperature * extra * sweepInterval;
        }

        // ================================================================= the swallow

        public struct SwallowState
        {
            public int ticksInside, ticksToDigest, nextKnockTick;
            public float damageSinceSwallow;

            public static SwallowState Fresh() { return new SwallowState { nextKnockTick = -1 }; }
        }

        public enum SwallowEvent { None, Finish, Knock }
        public enum KnockKind { Scrabbling, Knocking, Weak, Failing }

        /// <summary>Hours to digest by the victim's size, never under the creature's own minimum; in ticks.</summary>
        public static int DigestTicksFor(float minHours, float hoursPerBodySize, float bodySize)
        {
            float hours = Math.Max(minHours, hoursPerBodySize * bodySize);
            return (int)Math.Round(hours * TicksPerHour);
        }

        public static float TimeLeftFraction(in SwallowState s)
        {
            return s.ticksToDigest <= 0 ? 0f : Clamp01(1f - (float)s.ticksInside / s.ticksToDigest);
        }

        public static int TicksLeft(in SwallowState s) { return Math.Max(0, s.ticksToDigest - s.ticksInside); }

        /// <summary>A swallow: clock and damage reset, the first knock 120 ticks out.</summary>
        public static void Begin(ref SwallowState s, int digestTicks, int now)
        {
            s.ticksInside = 0;
            s.damageSinceSwallow = 0f;
            s.ticksToDigest = digestTicks;
            s.nextKnockTick = now + 120;
        }

        /// <summary>A stranger already part-digested: only 2..6 hours (hoursLeftTicks) of it left.</summary>
        public static void BeginStranger(ref SwallowState s, int digestTicks, int now, int ticksLeft)
        {
            s.ticksToDigest = digestTicks;
            s.ticksInside = Math.Max(0, digestTicks - ticksLeft);
            s.damageSinceSwallow = 0f;
            s.nextKnockTick = now + 120;
        }

        /// <summary>One tick while holding: finished at the digest length (or when the held one is already dead), else a knock when due.</summary>
        public static SwallowEvent Tick(ref SwallowState s, int now, bool insideMissingOrDead)
        {
            s.ticksInside++;
            if (insideMissingOrDead) return SwallowEvent.Finish;
            if (s.ticksInside >= s.ticksToDigest) return SwallowEvent.Finish;
            if (now >= s.nextKnockTick) return SwallowEvent.Knock;
            return SwallowEvent.None;
        }

        /// <summary>Schedules the next knock (900 ticks while there is time, 180 as it runs out) and returns the time-left fraction it used.</summary>
        public static float KnockNext(ref SwallowState s, int now)
        {
            float f = TimeLeftFraction(s);
            s.nextKnockTick = now + (int)Math.Round(Lerp(900f, 180f, f));
            return f;
        }

        public static float KnockVolume(float timeLeftFraction, float loudness) { return Lerp(0.25f, 1f, timeLeftFraction) * loudness; }

        public static KnockKind KnockKindFor(bool insideHumanlike, float f)
        {
            if (!insideHumanlike) return KnockKind.Scrabbling;
            if (f > 0.66f) return KnockKind.Knocking;
            if (f > 0.33f) return KnockKind.Weak;
            return KnockKind.Failing;
        }

        /// <summary>Acid burn on a released victim: 5 right after the swallow rising to 60 as the time runs out.</summary>
        public static float EarnedAcid(float timeLeftFraction) { return Lerp(60f, 5f, timeLeftFraction); }

        /// <summary>Damage dealt to the hwelgrue while it holds someone: true when the belly opens.</summary>
        public static bool BellyOpens(ref SwallowState s, float totalDamageDealt, float cutThreshold)
        {
            s.damageSinceSwallow += totalDamageDealt;
            return s.damageSinceSwallow >= cutThreshold;
        }

        /// <summary>The victim leaves (released or digested): returns the time-left fraction it left with, and clears the clock and damage.</summary>
        public static float Clear(ref SwallowState s)
        {
            float f = TimeLeftFraction(s);
            s.ticksInside = 0;
            s.ticksToDigest = 0;
            s.damageSinceSwallow = 0f;
            return f;
        }

        // ================================================================= the gut-mother vat

        public static int GutMotherDigestTicks(float hours) { return Math.Max(1, (int)Math.Round(hours * TicksPerHour)); }

        public const int RareTickInterval = 250;

        /// <summary>Fuel burned per rare tick: the def's per-day rate over the rare interval.</summary>
        public static float GutMotherFuelBurn(float consumptionRatePerDay) { return consumptionRatePerDay * RareTickInterval / TicksPerDay; }

        /// <summary>
        /// The vat's rare tick, AFTER its fuel was burned: with a body inside and fuel left it digests; the body is done at the digest length.
        /// dormant (no fuel) halts the clock without losing it.
        /// </summary>
        public static bool GutMotherTick(ref int progressTicks, bool holdsBody, bool dormant, int digestTicks)
        {
            if (!holdsBody || dormant) return false;
            progressTicks += RareTickInterval;
            return progressTicks >= digestTicks;
        }

        public static int RestUntil(int now, float restHours) { return now + (int)Math.Round(restHours * TicksPerHour); }

        public static bool Resting(int now, int restUntilTick) { return now < restUntilTick; }

        public static bool VatBusy(bool holdsBody, bool resting) { return holdsBody || resting; }

        /// <summary>A body is accepted only into an enabled vat that is empty.</summary>
        public static bool VatAccepts(bool enabled, bool corpseUsable, bool holdsBody) { return enabled && corpseUsable && !holdsBody; }

        // ================================================================= the swallowed drive core

        public enum ClaimResult { No, NotMine, Mine, New }

        /// <summary>
        /// Who carries the world's one drive core. Needs a world, an unspent core, and a wild hwelgrue; once someone carries it only that one is
        /// ever the carrier. A first claimant must not be over the map cap and must be on the campaign tile when one is set (tile &gt;= 0).
        /// </summary>
        public static ClaimResult Claim(bool haveWorld, bool spent, bool hasFaction, string carrierId, string myId, bool overCap, int campaignTile, int mapTile)
        {
            if (!haveWorld || spent || hasFaction) return ClaimResult.No;
            if (!string.IsNullOrEmpty(carrierId)) return carrierId == myId ? ClaimResult.Mine : ClaimResult.NotMine;
            if (overCap) return ClaimResult.No;
            if (campaignTile >= 0 && mapTile != campaignTile) return ClaimResult.No;
            return ClaimResult.New;
        }

        public static int PingIntervalTicks(float hours) { return Math.Max(2500, (int)Math.Round(hours * TicksPerHour)); }

        /// <summary>
        /// The carrier's ping clock (every 250 ticks): a grav engine appearing pings at once; otherwise every interval. Returns true when a ping
        /// is due (the ping itself only sounds with an engine on the map).
        /// </summary>
        public static bool PingDue(ref int nextPingTick, ref bool engineSeen, int now, bool engineNow, int interval)
        {
            if (engineNow && !engineSeen) nextPingTick = now;
            engineSeen = engineNow;
            if (nextPingTick < 0) nextPingTick = now;
            if (now >= nextPingTick)
            {
                nextPingTick = now + interval;
                return true;
            }
            return false;
        }

        /// <summary>The ship's own guns break the core: integrity falls by damage x factor, never under 0.</summary>
        public static float IntegrityAfterHit(float integrity, float damage, float factor) { return Math.Max(0f, integrity - damage * factor); }

        /// <summary>A core that came out under the ruin threshold is ruined, otherwise intact at its integrity.</summary>
        public static bool DropsRuined(float integrity, float ruinThreshold) { return integrity < ruinThreshold; }

        /// <summary>Gravship range multiplier of a linked core: 1 + bonus x integrity%, and 1 with the option off.</summary>
        public static float RangeFactor(bool enabled, float bonus, float integrity) { return enabled ? 1f + bonus * integrity / 100f : 1f; }

        // ================================================================= the navigator's log

        /// <summary>Entries earned by now: one per `perEntry` pings (at least 1), no more than the log holds.</summary>
        public static int EntriesDue(int pings, int perEntry, int entryCount) { return Math.Min(entryCount, pings / Math.Max(1, perEntry)); }

        /// <summary>The log reads on a ping only while the core is unspent and the log uncut.</summary>
        public static bool LogReads(bool haveWorld, bool haveDef, bool spent, bool logCut) { return haveWorld && haveDef && !spent && !logCut; }

        /// <summary>
        /// The carrier died: the rest of the log is cut (if any was left); a letter says so only if the player ever heard an entry. Returns
        /// true when the letter should be sent.
        /// </summary>
        public static bool CutLogOnDeath(ref bool logCut, int entriesRead, int entryCount)
        {
            if (logCut || entriesRead >= entryCount) return false;
            logCut = true;
            return entriesRead > 0;
        }

        /// <summary>Which campaign tile the next revealed site takes: the one at index sitesRevealed, or -1 to let the quest choose.</summary>
        public static int CampaignTileIndex(int sitesRevealed, int tileCount) { return tileCount > 0 && sitesRevealed < tileCount ? sitesRevealed : -1; }

        // ================================================================= the unjoining draught

        public struct Sorting { public bool removed, husk; }

        /// <summary>
        /// A hediff the draught meets: a symbiont (named in the targets list or marked) is removed and leaves a husk; a parasite (named, or
        /// carrying the marker at all) is removed; anything else stays.
        /// </summary>
        public static Sorting Sort(bool inParasites, bool inSymbionts, bool hasMarker, bool markerIsSymbiont)
        {
            bool symbiont = inSymbionts || (hasMarker && markerIsSymbiont);
            bool parasite = inParasites || hasMarker;
            return new Sorting { removed = symbiont || parasite, husk = symbiont };
        }

        public static int PurgeTicks(float hours) { return Math.Max(2500, (int)Math.Round(hours * TicksPerHour)); }

        /// <summary>The organ scar's severity: the def's, but never enough to destroy the part (health - 1). A non-positive result means no scar.</summary>
        public static float ScarSeverity(float defSeverity, float partHealth) { return Math.Min(defSeverity, partHealth - 1f); }

        // ================================================================= the biome worker

        public struct BiomeRanges
        {
            public float tempMin, tempMax, rainMin, rainMax, elevMin, elevMax, baseScore, degreeWeight, rainfallDivisor;
        }

        public static float BiomeScore(bool tileNull, bool waterCovered, bool impassable, float temperature, float rainfall, float elevation, in BiomeRanges r)
        {
            if (tileNull || waterCovered) return -100f;
            if (temperature < r.tempMin || temperature > r.tempMax) return 0f;
            if (rainfall < r.rainMin || rainfall >= r.rainMax) return 0f;
            if (elevation < r.elevMin || elevation > r.elevMax) return 0f;
            if (impassable) return 0f;
            float divisor = (r.rainfallDivisor > 0.0001f) ? r.rainfallDivisor : 1f;
            return r.baseScore + (r.tempMax - temperature) * r.degreeWeight + (r.rainMax - rainfall) / divisor;
        }
    }
}
