// Pure decision kernel of JawaIonWeapons (mandrake.rsw.ionweapons): no Verse, no RimWorld, no UnityEngine. The damage worker, the third-party
// stat part and the vehicle postfix call these with the same expressions they used inline and keep the engine half (hediffs, EMP damage infos,
// stunner calls). `internal` on purpose: the main assembly and the vehicle-tier assembly each compile this one file, so neither exports it.
using System;

namespace RimMandrake.StarWars.JawaIonWeapons
{
    internal static class RSW_IonBuildupKernel
    {
        public const float StunTicksPerEmpPoint = 30f;

        /// <summary>What a target's body size divides ion buildup by: size ^ exponent (size squared by default), 1 for a size or an exponent of 0 or less.</summary>
        public static float BodySizeDivisor(float bodySize, float exponent)
        {
            if (bodySize <= 0f) return 1f;
            if (exponent <= 0f) return 1f;
            if (exponent == 2f) return bodySize * bodySize;
            return (float)Math.Pow(bodySize, exponent);
        }

        /// <summary>The stat part other mods' stun weapons opt into. The engine itself multiplies the severity by 1 / body size afterwards, so this part
        /// supplies the remaining 1 / size ^ (exponent - 1), which composes to the same 1 / BodySizeDivisor. Off, a non-pawn, or a size of 0 or less
        /// leaves the value alone.</summary>
        public static float InverseSizeValue(bool thirdPartyScaling, bool isPawn, float bodySize, float exponent, float val)
        {
            if (!thirdPartyScaling) return val;
            if (isPawn && bodySize > 0f)
            {
                float scaled = (float)Math.Pow(bodySize, exponent - 1f);
                if (scaled > 0f) return 1f / scaled;
            }
            return val;
        }

        /// <summary>Flesh and droid buildup: the mechanic is on, a living pawn with health that is not a mechanoid, and the damage def lists hediffs.</summary>
        public static bool FleshBuildupApplies(bool enabled, bool isPawn, bool dead, bool hasHealth, bool hasRaceProps, bool mechanoid, bool hasEntries)
        {
            if (!enabled) return false;
            if (!isPawn || dead || !hasHealth) return false;
            if (!hasRaceProps || mechanoid) return false;
            return hasEntries;
        }

        /// <summary>Severity added for one hediff entry: the fixed amount when positive, else per-damage x damage dealt; x the strength slider; divided
        /// by the body-size divisor. At or under zero adds nothing.</summary>
        public static float FleshSeverity(float severityFixed, float severityPerDamageDealt, float damageAmount, float strength, float divisor)
        {
            float severity = severityFixed > 0f ? severityFixed : severityPerDamageDealt * damageAmount;
            severity *= strength;
            severity /= divisor;
            return severity;
        }

        /// <summary>The EMP a machine takes on top: mechanoids and drones the machine amount, droids and other non-flesh the droid amount, x the slider,
        /// divided by the divisor. Zero means none. Flesh never takes it; only the ion damage def carries the amounts.</summary>
        public static float MachineAmount(bool enabled, bool pawnLiveSpawned, bool hasRaceProps, bool isFlesh, bool isIonDef, bool machine,
                                          float empAmountMachine, float empAmountDroid, float tierMultiplier, float divisor)
        {
            if (!enabled) return 0f;
            if (!pawnLiveSpawned || !hasRaceProps) return 0f;
            if (isFlesh) return 0f;
            if (!isIonDef) return 0f;
            float amount = machine ? empAmountMachine : empAmountDroid;
            if (amount <= 0f) return 0f;
            amount *= tierMultiplier;
            amount /= divisor;
            return amount > 0f ? amount : 0f;
        }

        /// <summary>The 1-point EMP that breaks a shield: any live spawned pawn when the mechanic is on.</summary>
        public static bool ShieldBreaks(bool enabled, bool isPawn, bool dead, bool spawned) { return enabled && isPawn && !dead && spawned; }

        /// <summary>Vehicle stun length in ticks: the droid EMP spread over the vehicle's footprint, x the slider, 30 ticks per point. Only an absorbed
        /// ion hit on a vehicle with a stunner, with the mechanic on, stuns; zero means no stun.</summary>
        public static int VehicleStunTicks(bool absorbed, bool enabled, bool isIonDef, bool hasHandlers, bool hasStunner, float empAmountDroid, int sizeX, int sizeZ, float tierMultiplier)
        {
            if (!absorbed || !enabled || !isIonDef) return 0;
            if (!hasHandlers || !hasStunner) return 0;
            if (empAmountDroid <= 0f) return 0;
            float area = Math.Max(1, sizeX * sizeZ);
            float amount = empAmountDroid / area;
            amount *= tierMultiplier;
            if (amount <= 0f) return 0;
            int ticks = (int)Math.Round(amount * StunTicksPerEmpPoint);
            return ticks > 0 ? ticks : 0;
        }
    }
}
