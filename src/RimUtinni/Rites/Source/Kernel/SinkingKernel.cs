// SUMP_SINKING_RITE_BUILD_1: the Sinking (Sump Rite A, Ishko). Every decision the rite makes lives here, engine-free, so
// the net8.0 selftest (Source/SelfTest, `--sinking`) runs the production file. Do NOT add `using Verse;` / RimWorld /
// UnityEngine / HarmonyLib: src/RimMandrake/Utils/lint_kernel_guards.py fails the build of the selftest otherwise.
// The Verse glue (Source/Sinking/*.cs) gathers facts, calls in here, and applies what comes back.
//
// Rulings carried: the Sinking belongs to Ishko; it NEVER lowers Imperial Heat, it pushes the next Imperial probe/raid
// 5x further out; a non-Empire raid lull sits beside the Empire hold-off.
using System;
using System.Collections.Generic;

namespace RimMandrake.Utinni.Rites
{
    public enum SinkingOfferingKind { Pitch, DigFind, Other, RefusedPawn, RefusedCorpse, RefusedBelowFloor, RefusedDisabled }

    public enum SinkingRider { None, BeastLull, TrapFizzle }

    public enum SinkingWakeCause { Construction, Dig, Pump, Explosion, Damage, Other }

    /// <summary>The Mod Settings the kernel reads, copied out of RM_NinefoldSettings by the glue (and built by hand in the
    /// selftest). Defaults are the shipped values.</summary>
    public sealed class SinkingConfig
    {
        public bool riteEnabled = true;
        public bool holdOffEnabled = true;          // base effect 1: the Empire hold-off
        public bool raidLullEnabled = true;         // base effect 2: the non-Empire raid lull
        public bool ownershipEraseEnabled = true;   // base effect 3: foreign claims wiped
        public bool beastLullEnabled = true;        // rider (pitch): the tar beasts sleep
        public bool trapFizzleEnabled = true;       // rider (dig-find): the next traps fizzle
        public float valueFloor = 50f;
        public float holdOffMultiplier = 5f;
        public float normalHoldOffDays = 1f;        // the M4 placeholder: 60,000 ticks
        public float raidLullDays = 10f;
        public float raidLullStrength = 0.5f;       // 0 = no lull, 1 = no non-Empire raid at all
        public float beastLullDays = 15f;
        public int trapCount = 3;
        public string ownershipExclusions = "Humanlike";

        public SinkingConfig Clone() { return (SinkingConfig)MemberwiseClone(); }
    }

    /// <summary>What the glue knows about the offered thing.</summary>
    public struct SinkingOfferingFacts
    {
        public string defName;
        public bool isPawn;
        public bool isCorpse;
        public bool inLotteryTable;    // a row thingDef of some RM_LotteryTableDef (a dig find)
        public float marketValue;      // of the whole stack
    }

    /// <summary>Everything one Sinking does, decided before anything is touched. Absent effects read false / 0.</summary>
    public sealed class SinkingPlan
    {
        public SinkingOfferingKind kind;
        public bool accepted;
        public string reason;            // the refusal line, or the acceptance line
        public bool holdOff;
        public int holdOffTicks;
        public float holdOffMultiplier;
        public bool raidLull;
        public int raidLullTicks;
        public float raidChanceMultiplier = 1f;
        public bool ownershipErase;
        public SinkingRider rider;
        public int beastLullTicks;
        public int trapCount;
        public float ishkoDelta;

        /// <summary>One line naming every effect, so two plans compare as text in the selftest.</summary>
        public string Signature()
        {
            return string.Format(System.Globalization.CultureInfo.InvariantCulture,
                "kind={0} ok={1} hold={2}:{3}:{4} lull={5}:{6}:{7:0.###} erase={8} rider={9} beast={10} traps={11} ishko={12:0.###}",
                kind, accepted, holdOff, holdOffTicks, holdOffMultiplier, raidLull, raidLullTicks, raidChanceMultiplier,
                ownershipErase, rider, beastLullTicks, trapCount, ishkoDelta);
        }
    }

    public static class SinkingKernel
    {
        public const int TicksPerDay = 60000;
        public const string DeltaTag = "The Sinking";

        /// <summary>The pitch the tar takes as kin (TheSump: Defs/ThingDefs_Items/RM_Bitumen.xml, RM_SumpFloraItems.xml).</summary>
        public static readonly string[] PitchDefs = { "RM_Bitumen", "RM_KorvethPitch" };

        /// <summary>Lottery rows that are spoil, not a find: the placeholder chunks in RM_DigStratumTable.</summary>
        public static readonly string[] PlaceholderFinds = { "ChunkSlagSteel", "ChunkMechanoidSlag", "ShipChunk" };

        public static bool IsPitch(string defName)
        {
            return defName != null && Array.IndexOf(PitchDefs, defName) >= 0;
        }

        public static bool IsPlaceholderFind(string defName)
        {
            if (string.IsNullOrEmpty(defName)) return true;
            return Array.IndexOf(PlaceholderFinds, defName) >= 0 || defName.StartsWith("Chunk", StringComparison.Ordinal);
        }

        public static SinkingOfferingKind Classify(SinkingOfferingFacts f, SinkingConfig cfg, out string reason)
        {
            if (!cfg.riteEnabled)
            {
                reason = "The Sinking is switched off in Mod Settings.";
                return SinkingOfferingKind.RefusedDisabled;
            }
            if (f.isPawn)
            {
                reason = "The tar takes no living thing. Offer pitch, a find from the dig, or goods.";
                return SinkingOfferingKind.RefusedPawn;
            }
            if (f.isCorpse)
            {
                reason = "The tar keeps its own dead. A corpse cannot be sunk.";
                return SinkingOfferingKind.RefusedCorpse;
            }
            if (f.marketValue < cfg.valueFloor)
            {
                reason = string.Format(System.Globalization.CultureInfo.InvariantCulture,
                    "Worth {0:0} silver; the tar takes nothing under {1:0}.", f.marketValue, cfg.valueFloor);
                return SinkingOfferingKind.RefusedBelowFloor;
            }
            if (IsPitch(f.defName))
            {
                reason = "Pitch, given back to the pitch.";
                return SinkingOfferingKind.Pitch;
            }
            if (f.inLotteryTable && !IsPlaceholderFind(f.defName))
            {
                reason = "A find from the dig, returned to the depth it came from.";
                return SinkingOfferingKind.DigFind;
            }
            reason = "Goods, given to the tar.";
            return SinkingOfferingKind.Other;
        }

        public static bool IsRefusal(SinkingOfferingKind k)
        {
            return k == SinkingOfferingKind.RefusedPawn || k == SinkingOfferingKind.RefusedCorpse
                || k == SinkingOfferingKind.RefusedBelowFloor || k == SinkingOfferingKind.RefusedDisabled;
        }

        public static SinkingRider RiderFor(SinkingOfferingKind k, SinkingConfig cfg)
        {
            if (k == SinkingOfferingKind.Pitch && cfg.beastLullEnabled) return SinkingRider.BeastLull;
            if (k == SinkingOfferingKind.DigFind && cfg.trapFizzleEnabled) return SinkingRider.TrapFizzle;
            return SinkingRider.None;
        }

        public static int DaysToTicks(float days)
        {
            double t = Math.Round((double)Math.Max(0f, days) * TicksPerDay);
            return t >= int.MaxValue ? int.MaxValue : (int)t;
        }

        /// <summary>The hold-off condition's length: multiplier x the normal hold-off interval.</summary>
        public static int HoldOffTicks(SinkingConfig cfg)
        {
            return DaysToTicks(Math.Max(0f, cfg.holdOffMultiplier) * cfg.normalHoldOffDays);
        }

        /// <summary>A scheduled Imperial incident at absolute tick <paramref name="scheduled"/> moved out by the
        /// multiplier, measured from now: now + m x (scheduled - now). A tick already past (or now) is left alone.</summary>
        public static int MoveOut(int now, int scheduled, float multiplier)
        {
            if (scheduled <= now || multiplier <= 1f) return scheduled;
            double moved = now + (double)multiplier * ((double)scheduled - now);
            return moved >= int.MaxValue ? int.MaxValue : (int)Math.Round(moved);
        }

        /// <summary>The warning rung must not come after the raid it warns of.</summary>
        public static int MoveOutWarning(int now, int warning, int movedRaid, float multiplier)
        {
            return Math.Min(MoveOut(now, warning, multiplier), movedRaid);
        }

        /// <summary>The chance a non-Empire raid roll keeps while the lull holds.</summary>
        public static float RaidChanceMultiplier(SinkingConfig cfg, bool lullActive)
        {
            if (!lullActive || !cfg.raidLullEnabled) return 1f;
            return Clamp01(1f - cfg.raidLullStrength);
        }

        /// <summary>Whether a raid roll of <paramref name="roll"/> (uniform 0..1) still fires under the multiplier.</summary>
        public static bool RaidRollFires(float roll, float chanceMultiplier)
        {
            return chanceMultiplier >= 1f || roll < chanceMultiplier;
        }

        /// <summary>The trap counter a dig-find Sinking sets (0 when the rider is off).</summary>
        public static int TrapCounterStart(SinkingConfig cfg)
        {
            return cfg.trapFizzleEnabled ? Math.Max(0, cfg.trapCount) : 0;
        }

        /// <summary>One armed trap roll: true = the trap fizzles (disarmed) and the counter drops by one; false = it arms
        /// normally. At 0, or with the rider switched off, traps arm normally.</summary>
        public static bool FizzleTrap(ref int remaining, bool riderEnabled)
        {
            if (!riderEnabled || remaining <= 0) return false;
            remaining--;
            return true;
        }

        /// <summary>The beast-lull wake filter: while the lull holds, construction, dig and pump causes are refused;
        /// an explosion (or any damage) still wakes the beast.</summary>
        public static bool WakeAllowed(SinkingWakeCause cause, bool lullActive, bool riderEnabled)
        {
            if (!lullActive || !riderEnabled) return true;
            return !(cause == SinkingWakeCause.Construction || cause == SinkingWakeCause.Dig || cause == SinkingWakeCause.Pump);
        }

        /// <summary>Ishko's favour for an offering of <paramref name="value"/> silver, lerped like OfferingUtility.TransferFor
        /// (valueAtSmall..valueAtLarge onto magSmall..magLarge, clamped).</summary>
        public static float IshkoDelta(float value, float valueAtSmall, float valueAtLarge, float magSmall, float magLarge)
        {
            float k = valueAtLarge > valueAtSmall ? Clamp01((value - valueAtSmall) / (valueAtLarge - valueAtSmall)) : (value >= valueAtLarge ? 1f : 0f);
            return magSmall + (magLarge - magSmall) * k;
        }

        public static SinkingPlan Plan(SinkingOfferingFacts f, SinkingConfig cfg,
                                       float valueAtSmall, float valueAtLarge, float magSmall, float magLarge)
        {
            var p = new SinkingPlan();
            string why;
            p.kind = Classify(f, cfg, out why);
            p.reason = why;
            if (IsRefusal(p.kind)) return p;
            p.accepted = true;
            p.ishkoDelta = IshkoDelta(f.marketValue, valueAtSmall, valueAtLarge, magSmall, magLarge);
            if (cfg.holdOffEnabled)
            {
                p.holdOff = true;
                p.holdOffTicks = HoldOffTicks(cfg);
                p.holdOffMultiplier = Math.Max(1f, cfg.holdOffMultiplier);
            }
            if (cfg.raidLullEnabled)
            {
                p.raidLull = true;
                p.raidLullTicks = DaysToTicks(cfg.raidLullDays);
                p.raidChanceMultiplier = RaidChanceMultiplier(cfg, true);
            }
            p.ownershipErase = cfg.ownershipEraseEnabled;
            p.rider = RiderFor(p.kind, cfg);
            if (p.rider == SinkingRider.BeastLull) p.beastLullTicks = DaysToTicks(cfg.beastLullDays);
            if (p.rider == SinkingRider.TrapFizzle) p.trapCount = TrapCounterStart(cfg);
            return p;
        }

        /// <summary>The ownership exclusion list: comma/space separated tokens among Humanlike, Animal, Mech, Building,
        /// Item (case-insensitive; unknown tokens are kept and match nothing).</summary>
        public static HashSet<string> ParseExclusions(string list)
        {
            var set = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            if (string.IsNullOrEmpty(list)) return set;
            foreach (string raw in list.Split(new[] { ',', ';', ' ' }, StringSplitOptions.RemoveEmptyEntries))
                set.Add(raw.Trim());
            return set;
        }

        /// <summary>Whether a colony-owned thing of <paramref name="category"/> on the rite's map has its foreign claims
        /// wiped. Faction suspicion is a different record and is never touched by this.</summary>
        public static bool EraseCandidate(string category, bool colonyOwned, bool onRiteMap, HashSet<string> exclusions)
        {
            if (!colonyOwned || !onRiteMap) return false;
            return exclusions == null || !exclusions.Contains(category ?? "");
        }

        private static float Clamp01(float v) { return v < 0f ? 0f : (v > 1f ? 1f : v); }
    }
}
