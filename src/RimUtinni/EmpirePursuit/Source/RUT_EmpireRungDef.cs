/* EMPIRE_ESCALATION_LADDER_1 P1 — one rung of the Imperial search ladder, as data.
 * Design §3. The rung's mechanics are chosen by `kind`; everything a player reads
 * (letters) and every tunable number lives here in XML, never in the runner. */
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RuthlessPursuingMechanoids
{
    // EmpireRungKind lives in Kernel/EmpireLadderKernel.cs (it is the kernel's vocabulary).

    public class RUT_EmpireRungDef : Def
    {
        public int rungIndex = 1;
        public EmpireRungKind kind = EmpireRungKind.Strike;

        /* Arrival + strategy for the raid-shaped rungs (Strike, Cordon, Breach). */
        public PawnsArrivalModeDef arrivalMode;
        public RaidStrategyDef raidStrategy;
        /* Breach only: the second, simultaneous group. */
        public PawnsArrivalModeDef secondArrivalMode;
        public RaidStrategyDef secondRaidStrategy;
        public float secondPointsFactor = 0.5f;

        /* Probe: the pawn kinds tried in order (defName strings, resolved silently, so a
         * missing droid mod degrades to the faction's own smallest combat pawn). */
        public List<string> pawnKinds = new List<string>();
        public IntRange pawnCount = new IntRange(1, 1);

        public float pointsFactor = 1f;
        public float minPoints = 0f;

        /* Hours of warning letter before the rung lands (0 = the arrival letter is the warning). */
        public float warningHours = 0f;

        /* Bombardment only: hours between the telegraph letter and the strike (the marked area). */
        public float telegraphHours = 24f;

        /* Hours the Empire needs for success (probe sighting, spotter call, cordon standing). */
        public float successHours = 0f;
        /* Hours after which an unresolved contact is judged a failure and the rung holds. */
        public float timeoutHours = 72f;

        [MustTranslate] public string arrivalLetterLabel;
        [MustTranslate] public string arrivalLetterText;
        [MustTranslate] public string warningLetterLabel;
        [MustTranslate] public string warningLetterText;
        [MustTranslate] public string successLetterLabel;
        [MustTranslate] public string successLetterText;
        [MustTranslate] public string failLetterLabel;
        [MustTranslate] public string failLetterText;

        public static RUT_EmpireRungDef ForIndex(int index)
        {
            foreach (RUT_EmpireRungDef d in DefDatabase<RUT_EmpireRungDef>.AllDefsListForReading)
            {
                if (d.rungIndex == index) return d;
            }
            return null;
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (rungIndex < 1 || rungIndex > EmpireLadderMath.TopRung)
                yield return "rungIndex " + rungIndex + " outside 1.." + EmpireLadderMath.TopRung;
            if ((kind == EmpireRungKind.Strike || kind == EmpireRungKind.Cordon || kind == EmpireRungKind.Breach)
                && (arrivalMode == null || raidStrategy == null))
                yield return kind + " rung needs arrivalMode and raidStrategy";
            if (arrivalLetterLabel.NullOrEmpty())
                yield return "no arrivalLetterLabel";
        }
    }
}
