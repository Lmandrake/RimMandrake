// Verse-free kernel of Wrecked Machines: the grade ladder's capability ratios (always ordered, never reaching the original), where an upper
// grade may be built, which emanator grade soothes and how strongly, the power-output scaling, and the cost / research scalers.
// LadderPatcher, WreckedMachineGrade, PlaceWorker_BuildOverLowerGrade, ThoughtWorker_SalvagedEmanatorSoothe and WreckedMachinesPatcher call
// these with the same expressions; SelfTest/WreckedFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib
// (a `using Verse;` here breaks the self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.WreckedMachines
{
    public static class RM_WreckedMachinesKernel
    {
        /// <summary>Grades as ints: Wrecked 0, Kludged 1, Refurbished 2, Original 3.</summary>
        public const int Wrecked = 0, Kludged = 1, Refurbished = 2, Original = 3;
        /// <summary>The settings sliders stop here; nothing the player (or a hand-edited config) sets may reach the original's 1.0.</summary>
        public const float WreckedMax = 0.05f, KludgedMax = 0.6f, RefurbishedMax = 0.95f;

        public struct Ladder { public float wrecked, kludged, refurbished; }

        /// <summary>The ratios the ladder actually uses: each held inside its slider's range and ordered wrecked &lt;= kludged &lt;= refurbished,
        /// so a stale or hand-edited config can never invert the ladder or reach the original.</summary>
        public static Ladder Normalize(float wrecked, float kludged, float refurbished)
        {
            float r = Clamp(refurbished, 0f, RefurbishedMax);
            float k = Math.Min(Clamp(kludged, 0f, KludgedMax), r);
            float w = Math.Min(Clamp(wrecked, 0f, WreckedMax), k);
            return new Ladder { wrecked = w, kludged = k, refurbished = r };
        }

        public static float Clamp(float v, float lo, float hi)
        {
            return v < lo ? lo : v > hi ? hi : v;
        }

        /// <summary>Capability ratio of a grade; the original is exactly 1.</summary>
        public static float RatioFor(int grade, Ladder l)
        {
            switch (grade)
            {
                case Wrecked: return l.wrecked;
                case Kludged: return l.kludged;
                case Refurbished: return l.refurbished;
                default: return 1f;
            }
        }

        /// <summary>May this grade be placed here. Reinstalling an existing machine is always allowed; Wrecked and unlabelled defs are free; an
        /// upper grade needs a lower grade of its own line on the spot (a frame or blueprint counts as the grade it will become).</summary>
        public static bool AllowsPlacing(bool requireLowerGrade, bool isReinstall, bool hasGradeExtension, int grade, string line,
            IList<string> otherLines, IList<int> otherGrades)
        {
            if (!requireLowerGrade || isReinstall) return true;
            if (!hasGradeExtension || grade == Wrecked) return true;
            for (int i = 0; i < otherLines.Count; i++)
                if (otherLines[i] == line && otherGrades[i] < grade) return true;
            return false;
        }

        /// <summary>Soothe stage of an emanator grade (Kludged stage 0, Refurbished stage 1; the original shares the top stage), or -1 for an inert one.</summary>
        public static int EmanatorStage(int grade, int stageCount)
        {
            if (grade == Wrecked) return -1;
            return Math.Min(grade - 1, stageCount - 1);
        }

        /// <summary>A salvaged power producer's output: the original's (negative) draw times the ratio. A consumer or an unpowered original is left alone (null).</summary>
        public static float? ScaledPowerOutput(float originalBase, float ratio)
        {
            if (originalBase >= 0f) return null;
            return originalBase * ratio;
        }

        /// <summary>Mood of a salvaged emanator stage: the vanilla emanator's mood times the grade's ratio.</summary>
        public static float EmanatorMood(float vanillaBaseMood, float ratio)
        {
            return vanillaBaseMood * ratio;
        }

        /// <summary>Material count after the cost slider: scaled, rounded, never below one.</summary>
        public static int ScaledCount(int baseCount, float factor)
        {
            return Math.Max(1, (int)Math.Round(baseCount * factor));
        }

        /// <summary>Research cost after its slider, never below one.</summary>
        public static float ScaledResearch(float baseCost, float factor)
        {
            return Math.Max(1f, baseCost * factor);
        }
    }
}
