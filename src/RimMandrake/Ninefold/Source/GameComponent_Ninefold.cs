using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Ninefold
{
    // The safe core of the divine-satiation engine
    // (design/Jawa/divine_satiation_engine.md §9): "the vector, all
    // event-driven deltas, the fickle-Mood random walk, the ritual scoring,
    // and ALL voice narration -- pure read/compute/text. No live mutation."
    //
    // This class ships the VECTOR + MOOD WALK (the band ladder itself is
    // `SatiationBand.cs`; `GetBand` below just delegates to it), the
    // Harmony-patched event hooks (Patch_*.cs, this same assembly) that bind
    // real RimWorld choke points to its ApplyDelta, AND (2026-09-09) seven of
    // the nine first-contact unveilings (`FirstContactCorpus.cs`) -- see
    // TryFirstContact below for the owner-ruling citation that authorized
    // shipping the corpus text now rather than holding it for a paper
    // redline. Ishko and Oomo's chains remain unwired: they have no existing
    // event hook this mod can bind to without new API research, a genuine
    // mechanical gap, not a voice-text one. See
    // infrastructure/state/items/NINEFOLD_ENGINE_M0_1.md.
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
        // through Zizzik "high-amplitude... never trust his calm").
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

        // NINEFOLD_MISSING_EVENT_HOOKS_1: Ta'Baa's independent clock
        // (divine_satiation_engine.md: "erodes purely with time rooted...
        // each launch/relocation resets his erosion and spikes satiation").
        // UNTUNED first-pass rate, same status as EventMagnitude/MoodAmplitude
        // -- SATIATION_TUNING_RIG (§10) owns real tuning.
        private const float RootedErosionPerHour = 0.4f;
        // UNTUNED first-pass grace window, same status as RootedErosionPerHour above --
        // SATIATION_TUNING_RIG (§10) owns real tuning. Without this, lastLaunchTick was
        // written on every launch and never consulted anywhere, so "each launch resets
        // his erosion" (divine_satiation_engine.md) was false: StepRootedErosion ran on
        // the same flat per-hour clock whether or not Ta'Baa had just launched (found in
        // the 2026-09-05 code review wave).
        private const int RootedErosionGraceTicks = MoodWalkIntervalTicks * 6; // ~6 in-game hours
        private int lastLaunchTick;

        // NINEFOLD_ENGINE_M0_1: first-contact unveilings
        // (design/Jawa/first_contact_chains.md). Owner ruling on record
        // authorizes shipping this pre-authored text now, redlined live
        // in-game rather than on paper (ledger, 2026-09-01: "build the five
        // event hooks + corpus letters with the PROVISIONAL voice text; he
        // redlines letters as they appear in-game. Not held on a paper
        // redline" -- reaffirmed by the 2026-08-31 card session, "Ninefold
        // M0 CALLED -- provisional corpus... emergent first contact", and
        // OPUS5_HANDOFF.md's own "needs the owner's hands only: corpus
        // redline on LIVE M0 text"). This ships narration only (SHOCK +
        // CURIOSITY + REALIZATION, see FirstContactCorpus.cs) -- no DELIGHT
        // one-off mechanical gift, which is a live-mutation piece outside
        // this file's own safe-core scope.
        private bool[] unveiled = new bool[GodExtensions.Count];
        private List<int> pendingFirstContact = new List<int>();
        private int nextFirstContactTick;
        // Approximates first_contact_chains.md ⑧'s "third violent battle"
        // as the third violent death -- this mod has no battle-grouping /
        // incident window for deaths (unlike the fire hook's
        // instigator-keyed rate limiter), so a single battle with multiple
        // deaths could in principle fire early. First-pass simplification,
        // same status as this file's other UNTUNED constants.
        private int violentDeathCount;

        private const int OneDayTicks = 60000;
        // "the fourth or fifth night rooted" (first_contact_chains.md ②) --
        // UNTUNED first-pass reading, same status as this file's other
        // first-pass constants; §10 owns real tuning.
        private const int TaBaaFirstContactRootedTicks = OneDayTicks * 4;
        private const int ShkaarFirstContactViolentDeaths = 3;

        public GameComponent_Ninefold(Game game)
        {
            // NINEFOLD_ENUM_ORDER_SAVE_TRAP_1: cheap, checked once per game
            // instance, before anything reads/writes satiation[(int)god].
            GodExtensions.CheckOrdinalContract();

            // The rooted clock (lastLaunchTick) is NOT read from Find here:
            // this ctor runs inside Game.FillComponents, before Find.TickManager
            // exists, so reading it throws an NRE that fails the whole component
            // (measured 2026-09-05, full-list crash). It is started in
            // FinalizeInit (Find is ready there) for a fresh game, and restored
            // by ExposeData on a load; it defaults to 0 until then.
        }

        // NINEFOLD_MISSING_EVENT_HOOKS_1: a fresh colony has not "sat still" yet,
        // so start Ta'Baa's rooted clock at game start rather than tick 0 (which
        // would erode him from before the game began). FinalizeInit runs after
        // the game is built and Find.TickManager is available, for both a new
        // game and a load; the `== 0` guard leaves a loaded save's own value be.
        public override void FinalizeInit()
        {
            if (lastLaunchTick == 0 && Find.TickManager != null)
                lastLaunchTick = Find.TickManager.TicksGame;
        }

        // Convenience accessor for the event hooks (Patch_*.cs) so every hook
        // does not repeat the null-safe Current.Game?.GetComponent dance.
        // Pure read -- returns null outside Playing (main menu, world screen),
        // and every caller must handle that.
        public static GameComponent_Ninefold Instance =>
            Current.Game?.GetComponent<GameComponent_Ninefold>();

        public float GetSatiation(God god) => satiation[(int)god];

        public float GetMood(God god) => mood[(int)god];

        public SatiationBand GetBand(God god) => SatiationBandUtility.BandFor(satiation[(int)god]);

        // The additive raise/lower hook every event-driven delta routes
        // through (§9 safe core: "all event-driven deltas... pure
        // read/compute/text. No live mutation"). `reason` is for logging/
        // debug only -- it does not branch behavior.
        public void ApplyDelta(God god, float amount, string reason = null)
        {
            // MOD_OPTIONS_RETROFIT_1: the master switch. Every one of the
            // eighteen Patch_*.cs event hooks routes through this one
            // method, so gating it here turns the whole engine's effect
            // off in one place -- satiation simply stops moving, no NREs,
            // no orphaned state.
            if (!RM_NinefoldSettings.engineEnabled) return;

            int i = (int)god;
            amount *= RM_NinefoldSettings.eventMagnitudeMultiplier;
            satiation[i] = Mathf.Clamp(satiation[i] + amount, -100f, 100f);
            if (reason != null && Prefs.DevMode)
                Log.Message("[Ninefold] " + god + " satiation " +
                            (amount >= 0 ? "+" : "") + amount.ToString("F1") +
                            " (" + reason + ") -> " + satiation[i].ToString("F1") +
                            " [" + GetBand(god) + "]");
        }

        public override void GameComponentTick()
        {
            base.GameComponentTick();
            // MOD_OPTIONS_RETROFIT_1: the master switch, coarse-gated at
            // the top of the tick -- with the engine off, the Mood walk,
            // Ta'Baa's rooted erosion and the first-contact queue never
            // step at all.
            if (!RM_NinefoldSettings.engineEnabled) return;
            int ticks = Find.TickManager.TicksGame;
            StepPendingFirstContact();
            if (ticks % MoodWalkIntervalTicks != 0) return;
            StepMoodWalk();
            StepRootedErosion();
        }

        private void StepRootedErosion()
        {
            // Called once per MoodWalkIntervalTicks (one in-game hour), so a
            // flat per-call decrement IS the per-hour erosion rate. lastLaunchTick
            // itself is used only by Notify_Launched below to reset the clock --
            // this step doesn't need to re-derive elapsed hours from it.
            int i = (int)God.TaBaa;
            float erosion = RootedErosionPerHour * RM_NinefoldSettings.eventMagnitudeMultiplier;
            satiation[i] = Mathf.Clamp(satiation[i] - erosion, -100f, 100f);

            if (!unveiled[i] &&
                Find.TickManager.TicksGame - lastLaunchTick >= TaBaaFirstContactRootedTicks)
            {
                TryFirstContact(God.TaBaa);
            }
        }

        public bool IsUnveiled(God god) => unveiled[(int)god];

        // Called by an event hook (Patch_*.cs) the first time that god's
        // trigger condition is met. Safe to call repeatedly/redundantly --
        // no-ops once unveiled or already queued. See the class-level
        // comment above for the owner ruling that authorizes firing this
        // with the pre-authored corpus text.
        public void TryFirstContact(God god)
        {
            // MOD_OPTIONS_RETROFIT_1: engine off, or letters specifically
            // turned off -- no-op entirely (no letter, no `unveiled` write)
            // rather than half-tracking state a disabled option should not
            // be touching.
            if (!RM_NinefoldSettings.engineEnabled) return;
            if (!RM_NinefoldSettings.firstContactLettersEnabled) return;

            int i = (int)god;
            if (unveiled[i]) return;
            if (pendingFirstContact.Contains(i)) return;

            if (pendingFirstContact.Count == 0 &&
                Find.TickManager.TicksGame >= nextFirstContactTick)
            {
                FireFirstContact(god);
            }
            else
            {
                // "two gods never introduce themselves at once" (build note,
                // first_contact_chains.md) -- queue behind whatever is
                // already scheduled rather than firing the same day.
                pendingFirstContact.Add(i);
            }
        }

        // Sh'kaar's trigger is a violent-death counter, not a single event --
        // called from Patch_BattleResolved alongside its existing ApplyDelta.
        public void NotifyViolentDeath()
        {
            if (!RM_NinefoldSettings.engineEnabled) return;
            if (unveiled[(int)God.Shkaar]) return;
            violentDeathCount++;
            if (violentDeathCount >= ShkaarFirstContactViolentDeaths)
                TryFirstContact(God.Shkaar);
        }

        private void FireFirstContact(God god)
        {
            unveiled[(int)god] = true;
            nextFirstContactTick = Find.TickManager.TicksGame + OneDayTicks;
            if (!FirstContactCorpus.GetChain(god, out string title, out string text))
                return; // Ishko/Oomo -- no corpus entry wired yet
            Find.LetterStack.ReceiveLetter(title, text, LetterDefOf.NeutralEvent);
        }

        private void StepPendingFirstContact()
        {
            if (pendingFirstContact.Count == 0) return;
            if (Find.TickManager.TicksGame < nextFirstContactTick) return;
            int nextGod = pendingFirstContact[0];
            pendingFirstContact.RemoveAt(0);
            FireFirstContact((God)nextGod);
        }

        // Harmony hooks call this (Patch_GravshipLaunched.cs) when the colony
        // actually relocates. Resets the rooted clock AND spikes satiation --
        // both halves of "each launch/relocation resets his erosion and
        // spikes satiation" in one call, so a caller cannot do one without
        // the other.
        public void Notify_Launched(string reason)
        {
            lastLaunchTick = Find.TickManager.TicksGame;
            ApplyDelta(God.TaBaa, EventMagnitude.Large, reason);
        }

        private void StepMoodWalk()
        {
            for (int i = 0; i < GodExtensions.Count; i++)
            {
                float amp = MoodAmplitude[i];
                // bounded random walk: small step scaled by amplitude, softly
                // pulled back toward 0 so a god does not wander to a rail and
                // stick there forever with no event ever moving it back.
                float step = (Rand.Value - 0.5f) * 10f * amp * RM_NinefoldSettings.moodWalkMultiplier;
                float pullback = -mood[i] * 0.02f;
                mood[i] = Mathf.Clamp(mood[i] + step + pullback, -100f, 100f);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            // ToLists() MUST run before Scribe_Collections.Look() on the Saving pass --
            // Look() writes whatever satiationList/moodList already hold at the
            // moment it runs, so populating them after would scribe stale data.
            if (Scribe.mode == LoadSaveMode.Saving)
            {
                ToLists();
            }
            Scribe_Collections.Look(ref satiationList, "ninefoldSatiation", LookMode.Value);
            Scribe_Collections.Look(ref moodList, "ninefoldMood", LookMode.Value);
            Scribe_Collections.Look(ref unveiledList, "ninefoldUnveiled", LookMode.Value);
            Scribe_Collections.Look(ref pendingFirstContact, "ninefoldPendingFirstContact", LookMode.Value);
            Scribe_Values.Look(ref nextFirstContactTick, "ninefoldNextFirstContactTick", 0);
            Scribe_Values.Look(ref violentDeathCount, "ninefoldViolentDeathCount", 0);
            Scribe_Values.Look(ref lastLaunchTick, "ninefoldLastLaunchTick", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                FromLists();
                if (pendingFirstContact == null) pendingFirstContact = new List<int>();
                // A save from before NINEFOLD_MISSING_EVENT_HOOKS_1 has no
                // recorded lastLaunchTick (defaults to 0) -- treat that as
                // "just launched now" rather than eroding Ta'Baa for however
                // many ticks the whole save has existed, in one lump, the
                // instant it loads.
                if (lastLaunchTick == 0) lastLaunchTick = Find.TickManager.TicksGame;
            }
        }

        // Scribe_Collections wants List<T>, not a fixed array -- these are
        // save/load-only views over the real arrays.
        private List<float> satiationList;
        private List<float> moodList;
        private List<bool> unveiledList;

        private void ToLists()
        {
            satiationList = new List<float>(satiation);
            moodList = new List<float>(mood);
            unveiledList = new List<bool>(unveiled);
        }

        private void FromLists()
        {
            if (unveiledList != null && unveiledList.Count == GodExtensions.Count)
                unveiledList.CopyTo(unveiled);
            else if (unveiledList != null)
                Log.Warning("[Ninefold] saved unveiled list has " + unveiledList.Count +
                    " entries, expected " + GodExtensions.Count + " -- discarding, all gods reset to veiled.");

            if (satiationList != null && satiationList.Count == GodExtensions.Count)
                satiationList.CopyTo(satiation);
            else if (satiationList != null)
                Log.Warning("[Ninefold] saved satiation list has " + satiationList.Count +
                    " entries, expected " + GodExtensions.Count + " -- discarding, all gods reset to 0.");

            if (moodList != null && moodList.Count == GodExtensions.Count)
                moodList.CopyTo(mood);
            else if (moodList != null)
                Log.Warning("[Ninefold] saved mood list has " + moodList.Count +
                    " entries, expected " + GodExtensions.Count + " -- discarding, all gods reset to 0.");
        }
    }
}
