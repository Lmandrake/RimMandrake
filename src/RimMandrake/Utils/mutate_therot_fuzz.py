#!/usr/bin/env python3
"""Mutation proof for the TheRot fuzz: plants each defect in the kernel (RM_TheRotKernel.cs), demands the fuzz FAILS, restores the file
byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_therot_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/TheRot/Source/RM_TheRotKernel.cs"
MUTATIONS = [
    ("lerp unclamped", "public static float Lerp(float a, float b, float t) { return a + (b - a) * Clamp01(t); }", "public static float Lerp(float a, float b, float t) { return a + (b - a) * t; }"),
    ("clamp01 lower edge", "return v < 0f ? 0f : (v > 1f ? 1f : v);", "return v < 0f ? 0.1f : (v > 1f ? 1f : v);"),
    ("casting interval floor gone", "return Math.Max(2500, (int)Math.Round(days * TicksPerDay)); }\n\n        /// <summary>\n        /// One sweep", "return (int)Math.Round(days * TicksPerDay); }\n\n        /// <summary>\n        /// One sweep"),
    ("gut sweep counts an empty gut", "            ticksDigesting = 0;\n            return false;", "            ticksDigesting += sweepInterval;\n            return false;"),
    ("gut sweep casts one sweep late", "return ticksDigesting >= castingInterval;", "return ticksDigesting > castingInterval;"),
    ("gut sweep never resets", "            ticksDigesting = 0;\n            return false;", "            return false;"),
    ("a factioned hwelgrue is culled", "if (hasFaction) return false;", ""),
    ("cap ignores the off switch", "return others >= (enabled ? cap : 0);", "return others >= cap;"),
    ("cap is exclusive", "return others >= (enabled ? cap : 0);", "return others > (enabled ? cap : 0);"),
    ("rot boost in the cold", "if (rotRateAtTemperature <= 0f) return 0f;", ""),
    ("rot boost ignores the sweep length", "return rotRateAtTemperature * extra * sweepInterval;", "return rotRateAtTemperature * extra;"),
    ("digest ignores body size", "float hours = Math.Max(minHours, hoursPerBodySize * bodySize);", "float hours = minHours;"),
    ("digest has no minimum", "float hours = Math.Max(minHours, hoursPerBodySize * bodySize);", "float hours = hoursPerBodySize * bodySize;"),
    ("time left fraction unclamped", "return s.ticksToDigest <= 0 ? 0f : Clamp01(1f - (float)s.ticksInside / s.ticksToDigest);", "return s.ticksToDigest <= 0 ? 0f : 1f - (float)s.ticksInside / s.ticksToDigest;"),
    ("time left of an empty belly is full", "return s.ticksToDigest <= 0 ? 0f :", "return s.ticksToDigest <= 0 ? 1f :"),
    ("ticks left can go negative", "return Math.Max(0, s.ticksToDigest - s.ticksInside);", "return s.ticksToDigest - s.ticksInside;"),
    ("a swallow keeps old damage", "            s.ticksInside = 0;\n            s.damageSinceSwallow = 0f;\n            s.ticksToDigest = digestTicks;\n            s.nextKnockTick = now + 120;", "            s.ticksInside = 0;\n            s.ticksToDigest = digestTicks;\n            s.nextKnockTick = now + 120;"),
    ("first knock 121 ticks out", "            s.damageSinceSwallow = 0f;\n            s.ticksToDigest = digestTicks;\n            s.nextKnockTick = now + 120;", "            s.damageSinceSwallow = 0f;\n            s.ticksToDigest = digestTicks;\n            s.nextKnockTick = now + 121;"),
    ("stranger starts with the full time", "s.ticksInside = Math.Max(0, digestTicks - ticksLeft);", "s.ticksInside = 0;"),
    ("stranger time left can go negative", "s.ticksInside = Math.Max(0, digestTicks - ticksLeft);", "s.ticksInside = digestTicks - ticksLeft;"),
    ("tick never counts", "            s.ticksInside++;\n            if (insideMissingOrDead)", "            if (insideMissingOrDead)"),
    ("dead victim keeps being held", "if (insideMissingOrDead) return SwallowEvent.Finish;", ""),
    ("digest finishes a tick late", "if (s.ticksInside >= s.ticksToDigest) return SwallowEvent.Finish;", "if (s.ticksInside > s.ticksToDigest) return SwallowEvent.Finish;"),
    ("knock before it is due", "if (now >= s.nextKnockTick) return SwallowEvent.Knock;", "if (now >= s.nextKnockTick - 1) return SwallowEvent.Knock;"),
    ("knocks slow as time runs out", "Lerp(900f, 180f, f)", "Lerp(180f, 900f, f)"),
    ("knock volume constant", "return Lerp(0.25f, 1f, timeLeftFraction) * loudness;", "return loudness;"),
    ("knock kind threshold", "if (f > 0.66f) return KnockKind.Knocking;", "if (f > 0.7f) return KnockKind.Knocking;"),
    ("scrabbling for humanlikes", "if (!insideHumanlike) return KnockKind.Scrabbling;", ""),
    ("acid falls as time runs out", "Lerp(60f, 5f, timeLeftFraction)", "Lerp(5f, 60f, timeLeftFraction)"),
    ("belly opens early", "return s.damageSinceSwallow >= cutThreshold;", "return s.damageSinceSwallow > cutThreshold;"),
    ("belly damage not accumulated", "s.damageSinceSwallow += totalDamageDealt;", "s.damageSinceSwallow = totalDamageDealt;"),
    ("clear keeps the clock", "            s.ticksInside = 0;\n            s.ticksToDigest = 0;\n            s.damageSinceSwallow = 0f;\n            return f;", "            s.ticksToDigest = 0;\n            s.damageSinceSwallow = 0f;\n            return f;"),
    ("clear keeps the damage", "            s.ticksToDigest = 0;\n            s.damageSinceSwallow = 0f;\n            return f;", "            s.ticksToDigest = 0;\n            return f;"),
    ("vat digest can be zero", "return Math.Max(1, (int)Math.Round(hours * TicksPerHour));", "return (int)Math.Round(hours * TicksPerHour);"),
    ("vat fuel burn per day", "return consumptionRatePerDay * RareTickInterval / TicksPerDay;", "return consumptionRatePerDay * RareTickInterval / TicksPerHour;"),
    ("vat digests while dormant", "if (!holdsBody || dormant) return false;", "if (!holdsBody) return false;"),
    ("vat digests nothing", "if (!holdsBody || dormant) return false;", "if (dormant) return false;"),
    ("vat finishes late", "return progressTicks >= digestTicks;", "return progressTicks > digestTicks;"),
    ("rest ends a tick late", "public static bool Resting(int now, int restUntilTick) { return now < restUntilTick; }", "public static bool Resting(int now, int restUntilTick) { return now <= restUntilTick; }"),
    ("vat busy only when holding", "return holdsBody || resting;", "return holdsBody;"),
    ("vat accepts when full", "return enabled && corpseUsable && !holdsBody;", "return enabled && corpseUsable;"),
    ("vat accepts when off", "return enabled && corpseUsable && !holdsBody;", "return corpseUsable && !holdsBody;"),
    ("a factioned hwelgrue carries the core", "if (!haveWorld || spent || hasFaction) return ClaimResult.No;", "if (!haveWorld || spent) return ClaimResult.No;"),
    ("a spent core is claimed", "if (!haveWorld || spent || hasFaction) return ClaimResult.No;", "if (!haveWorld || hasFaction) return ClaimResult.No;"),
    ("second carrier allowed", "return carrierId == myId ? ClaimResult.Mine : ClaimResult.NotMine;", "return ClaimResult.Mine;"),
    ("over-cap hwelgrue claims", "if (overCap) return ClaimResult.No;", ""),
    ("campaign tile ignored", "if (campaignTile >= 0 && mapTile != campaignTile) return ClaimResult.No;", ""),
    ("campaign tile zero ignored", "if (campaignTile >= 0 && mapTile != campaignTile)", "if (campaignTile > 0 && mapTile != campaignTile)"),
    ("ping interval floor gone", "public static int PingIntervalTicks(float hours) { return Math.Max(2500, (int)Math.Round(hours * TicksPerHour)); }", "public static int PingIntervalTicks(float hours) { return (int)Math.Round(hours * TicksPerHour); }"),
    ("engine appearing does not ping", "if (engineNow && !engineSeen) nextPingTick = now;", ""),
    ("engine memory not kept", "engineSeen = engineNow;", ""),
    ("ping interval not applied", "nextPingTick = now + interval;", "nextPingTick = now;"),
    ("integrity can go negative", "return Math.Max(0f, integrity - damage * factor);", "return integrity - damage * factor;"),
    ("ruin threshold inclusive", "return integrity < ruinThreshold;", "return integrity <= ruinThreshold;"),
    ("range bonus applied when off", "return enabled ? 1f + bonus * integrity / 100f : 1f;", "return 1f + bonus * integrity / 100f;"),
    ("range bonus ignores integrity", "1f + bonus * integrity / 100f", "1f + bonus"),
    ("entries exceed the log", "return Math.Min(entryCount, pings / Math.Max(1, perEntry));", "return pings / Math.Max(1, perEntry);"),
    ("entries per ping zero divides", "pings / Math.Max(1, perEntry)", "pings / perEntry"),
    ("log reads when cut", "return haveWorld && haveDef && !spent && !logCut;", "return haveWorld && haveDef && !spent;"),
    ("log reads when spent", "return haveWorld && haveDef && !spent && !logCut;", "return haveWorld && haveDef && !logCut;"),
    ("log cut twice", "if (logCut || entriesRead >= entryCount) return false;", "if (entriesRead >= entryCount) return false;"),
    ("finished log cut", "if (logCut || entriesRead >= entryCount) return false;", "if (logCut) return false;"),
    ("letter even if never heard", "return entriesRead > 0;", "return true;"),
    ("campaign tile index off by one", "return tileCount > 0 && sitesRevealed < tileCount ? sitesRevealed : -1;", "return tileCount > 0 && sitesRevealed <= tileCount ? sitesRevealed : -1;"),
    ("symbiont only by name", "bool symbiont = inSymbionts || (hasMarker && markerIsSymbiont);", "bool symbiont = inSymbionts;"),
    ("parasite only by name", "bool parasite = inParasites || hasMarker;", "bool parasite = inParasites;"),
    ("symbiont leaves no husk", "husk = symbiont", "husk = false"),
    ("parasite leaves a husk", "husk = symbiont", "husk = symbiont || parasite"),
    ("purge floor gone", "public static int PurgeTicks(float hours) { return Math.Max(2500, (int)Math.Round(hours * TicksPerHour)); }", "public static int PurgeTicks(float hours) { return (int)Math.Round(hours * TicksPerHour); }"),
    ("scar can destroy the part", "return Math.Min(defSeverity, partHealth - 1f);", "return defSeverity;"),
    ("water-covered tile scores", "if (tileNull || waterCovered) return -100f;", "if (tileNull) return -100f;"),
    ("temperature range exclusive", "if (temperature < r.tempMin || temperature > r.tempMax) return 0f;", "if (temperature <= r.tempMin || temperature >= r.tempMax) return 0f;"),
    ("rainfall max inclusive", "if (rainfall < r.rainMin || rainfall >= r.rainMax) return 0f;", "if (rainfall < r.rainMin || rainfall > r.rainMax) return 0f;"),
    ("impassable tile scores", "if (impassable) return 0f;", ""),
    ("rainfall divisor zero divides", "float divisor = (r.rainfallDivisor > 0.0001f) ? r.rainfallDivisor : 1f;", "float divisor = r.rainfallDivisor;"),
    ("warmer scores higher", "(r.tempMax - temperature) * r.degreeWeight", "(temperature - r.tempMin) * r.degreeWeight"),
]

if __name__ == "__main__":
    # `mutate_therot_fuzz.py [name-substring]`; or `--part K/N` runs the K-th of N slices (a full pass outlasts one 10-minute tool call)
    muts = MUTATIONS
    only = None
    if len(sys.argv) > 2 and sys.argv[1] == "--part":
        k, n = (int(x) for x in sys.argv[2].split("/"))
        muts = MUTATIONS[(k - 1) * len(MUTATIONS) // n: k * len(MUTATIONS) // n]
    elif len(sys.argv) > 1:
        only = sys.argv[1]
    sys.exit(run_mutations(KERNEL, "selftest_therot_fuzz.py", muts, only))
