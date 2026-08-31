using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Ninefold
{
    // The safe core of the divine-satiation engine
    // (design/Jawa/divine_satiation_engine.md §9): "the vector, all
    // event-driven deltas, the fickle-Mood random walk, the ritual scoring,
    // and ALL voice narration -- pure read/compute/text. No live mutation."
    //
    // This class ships the VECTOR + BAND LADDER + MOOD WALK only. It does
    // NOT ship: the five event hooks, first-contact chains, or narrator
    // corpus letters (NINEFOLD_ENGINE_M0_1's other named pieces) -- those
    // need real event-binding research and owner-reviewed voice text, not a
    // solo pass. See infrastructure/state/items/NINEFOLD_ENGINE_M0_1.md.
    public class GameComponent_Ninefold : GameComponent
    {
        // Satiation: -100..100, signed, free-floating, moves ONLY by
        // ApplyDelta (colony events). No drift to baseline (§1).
        private float[] satiation = new float[GodExtensions.Count];

        // Mood: -100..100, self-driven, fickle; wanders on its own clock
        // (§1, §2). NEVER surfaced as a UI number (F8) -- read only through
        // ambient gesture/narration callers, never printed.
        private float[] mood = new float[GodExtensions.Count];

        // Per-god Mood walk amplitude, 0..1 relative scale, encoded from
        // §2's qualitative personality column (Ishko "steady, low-amplitude"
        // through Sh'kaar/Zizzik "high-amplitude... never trust his calm").
        // 🔴 UNTUNED -- §10 explicitly defers real tuning to a throwaway-save
        // test rig. These are a first-pass ordering, not measured values.
        private static readonly float[] MoodAmplitude =
        {
            /* Ishko    */ 0.15f,
            /* Ohm      */ 0.65f, // tied to ship state per §4; this walk component is the fallback-random half only
            /* Oomo     */ 0.45f,
            /* MobUnloo */ 0.20f,
            /* Rekko    */ 0.35f,
            /* TaBaa    */ 0.40f,
            /* Zizzik   */ 0.80f,
            /* Shkaar   */ 0.55f,
            /* Ozzik    */ 0.70f,
        };

        private const int MoodWalkIntervalTicks = 2500; // one in-game hour

        public GameComponent_Ninefold(Game game)
        {
        }

        public float GetSatiation(God god) => satiation[(int)god];

        public float GetMood(God god) => mood[(int)god];

        public SatiationBand GetBand(God god) => SatiationBandUtility.BandFor(satiation[(int)god]);

        // The additive raise/lower hook every event-driven delta routes
        // through (§9 safe core: "all event-driven deltas... pure
        // read/compute/text. No live mutation"). `reason` is for logging/
        // debug only -- it does not branch behavior.
        public void ApplyDelta(God god, float amount, string reason = null)
        {
            int i = (int)god;
            satiation[i] = Mathf.Clamp(satiation[i] + amount, -100f, 100f);
            if (reason != null)
                Log.Message("[Ninefold] " + god + " satiation " +
                            (amount >= 0 ? "+" : "") + amount.ToString("F1") +
                            " (" + reason + ") -> " + satiation[i].ToString("F1") +
                            " [" + GetBand(god) + "]");
        }

        public override void GameComponentTick()
        {
            base.GameComponentTick();
            int ticks = Find.TickManager.TicksGame;
            if (ticks % MoodWalkIntervalTicks != 0) return;
            StepMoodWalk();
        }

        private void StepMoodWalk()
        {
            for (int i = 0; i < GodExtensions.Count; i++)
            {
                float amp = MoodAmplitude[i];
                // bounded random walk: small step scaled by amplitude, softly
                // pulled back toward 0 so a god does not wander to a rail and
                // stick there forever with no event ever moving it back.
                float step = (Rand.Value - 0.5f) * 10f * amp;
                float pullback = -mood[i] * 0.02f;
                mood[i] = Mathf.Clamp(mood[i] + step + pullback, -100f, 100f);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref satiationList, "ninefoldSatiation", LookMode.Value);
            Scribe_Collections.Look(ref moodList, "ninefoldMood", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                FromLists();
            }
            if (Scribe.mode == LoadSaveMode.Saving)
            {
                ToLists();
            }
        }

        // Scribe_Collections wants List<T>, not a fixed array -- these are
        // save/load-only views over the real arrays.
        private List<float> satiationList;
        private List<float> moodList;

        private void ToLists()
        {
            satiationList = new List<float>(satiation);
            moodList = new List<float>(mood);
        }

        private void FromLists()
        {
            if (satiationList != null && satiationList.Count == GodExtensions.Count)
                satiationList.CopyTo(satiation);
            if (moodList != null && moodList.Count == GodExtensions.Count)
                moodList.CopyTo(mood);
        }
    }
}
