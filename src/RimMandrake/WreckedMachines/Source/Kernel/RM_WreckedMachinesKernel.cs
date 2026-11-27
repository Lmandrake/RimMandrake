// Verse-free kernel of Wrecked Machines: the grade ladder's capability ratios (always ordered, never reaching the original), where an upper
// grade may be built, which emanator grade soothes and how strongly, the power-output scaling, the cost / research scalers, and which
// processes a Kludged and a Refurbished level run.
// LadderPatcher, WreckedMachineGrade, PlaceWorker_BuildOverLowerGrade, ThoughtWorker_SalvagedEmanatorSoothe, WreckedMachinesPatcher and
// RM_ProcessLists call
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

        /// <summary>The process list of a Kludged level: the row's part of the donor's processes, then everything on the Kludged def's
        /// own list as the game loaded it. <paramref name="donor"/> is the donor's list as loaded; the row names its part
        /// (<paramref name="rowNamed"/>) or takes the donor's first <paramref name="rowCount"/>; <paramref name="asLoaded"/> holds what
        /// the stamp wrote (the row's part again, or nothing for a donor whose processes are made in code) and what a neighbour mod
        /// patched on. A neighbour's process stays whether or not the donor has it too (the Armoury puts durasteel on the donor forge
        /// and on our Kludged forge). A level never ends with no process while the donor has one.</summary>
        public static List<T> KludgedProcesses<T>(IList<T> donor, IList<T> rowNamed, int rowCount, IList<T> asLoaded) where T : class
        {
            var want = new List<T>();
            AddAll(want, rowNamed, int.MaxValue);
            if (want.Count == 0 && rowCount > 0) AddAll(want, donor, rowCount);
            AddAll(want, asLoaded, int.MaxValue);
            if (want.Count == 0) AddAll(want, donor, 1);
            return want;
        }

        /// <summary>The process list of a Refurbished level: every process of the donor as loaded, then what the Refurbished def's own
        /// loaded list adds (a neighbour's patch).</summary>
        public static List<T> RefurbishedProcesses<T>(IList<T> donor, IList<T> asLoaded) where T : class
        {
            var want = new List<T>();
            AddAll(want, donor, int.MaxValue);
            AddAll(want, asLoaded, int.MaxValue);
            return want;
        }

        /// <summary>Appends the first <paramref name="take"/> entries of a list that are not null and not yet there.</summary>
        private static void AddAll<T>(List<T> to, IList<T> from, int take) where T : class
        {
            if (from == null) return;
            for (int i = 0, n = 0; i < from.Count && n < take; i++)
            {
                T p = from[i];
                if (p == null) continue;
                n++;
                if (!to.Contains(p)) to.Add(p);
            }
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
