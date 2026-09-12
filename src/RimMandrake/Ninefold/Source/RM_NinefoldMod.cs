using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Ninefold
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Ninefold.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData, a DoWindowContents
    // helper called from the Mod subclass).
    //
    // Ninefold's own "safe core" doctrine (GameComponent_Ninefold.cs class
    // header, §9: "the vector, all event-driven deltas, the fickle-Mood
    // random walk... pure read/compute/text. No live mutation") means every
    // one of the eighteen Patch_*.cs event hooks funnels through exactly two
    // choke points on GameComponent_Ninefold: ApplyDelta and TryFirstContact
    // (NotifyViolentDeath is the one extra caller of TryFirstContact).
    // Gating those, plus the tick that drives the Mood walk / Ta'Baa's
    // rooted erosion / the first-contact queue, turns the WHOLE engine on
    // and off from one place without touching any of the eighteen patch
    // files — the safest coarse gate available, per this item's own
    // instructions, and it degrades cleanly: no NREs, no orphaned state,
    // the engine just stops moving.
    //
    // Tuning: EventMagnitude.cs and GameComponent_Ninefold's own
    // MoodAmplitude/RootedErosionPerHour constants are explicitly flagged
    // UNTUNED throughout the source ("§10 explicitly defers real tuning to
    // a throwaway-save test rig") — these sliders ARE that rig, letting the
    // owner retune without a rebuild.
    // ════════════════════════════════════════════════════════════════════
    public class RM_NinefoldSettings : ModSettings
    {
        // Master switch. Off: ApplyDelta/TryFirstContact/NotifyViolentDeath
        // all no-op and the per-hour tick step (Mood walk, Ta'Baa's rooted
        // erosion, the first-contact queue) never runs — satiation/mood
        // freeze wherever they are, no letters fire, no log lines, no NREs.
        public static bool engineEnabled = true;

        // Off: the nine-god vector still tracks silently (if the master
        // switch above is on), but the SHOCK/CURIOSITY/REALIZATION letters
        // (FirstContactCorpus) never fire and no god is ever marked
        // unveiled — fully reversible, nothing is lost by leaving it off.
        public static bool firstContactLettersEnabled = true;

        // Scales every ApplyDelta call (all eighteen event hooks route
        // through it) AND Ta'Baa's per-hour rooted erosion — the two
        // hardcoded numbers this engine's own comments call "UNTUNED, a
        // first-pass ordering" (EventMagnitude.cs, GameComponent_Ninefold's
        // RootedErosionPerHour).
        public static float eventMagnitudeMultiplier = 1f;

        // Scales the per-god Mood random-walk step (GameComponent_Ninefold.
        // MoodAmplitude) — the other constant array flagged UNTUNED in the
        // same source comment.
        public static float moodWalkMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref engineEnabled, "engineEnabled", true);
            Scribe_Values.Look(ref firstContactLettersEnabled, "firstContactLettersEnabled", true);
            Scribe_Values.Look(ref eventMagnitudeMultiplier, "eventMagnitudeMultiplier", 1f);
            Scribe_Values.Look(ref moodWalkMultiplier, "moodWalkMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Enable the Ninefold engine", ref engineEnabled,
                "The nine gods' satiation/mood tracking and their event-driven reactions "
              + "to play. Off: completely inert — no tracking, no letters, no log lines, "
              + "as if the mod were not installed.");
            list.Gap();

            if (engineEnabled)
            {
                list.CheckboxLabeled("First-contact letters", ref firstContactLettersEnabled,
                    "Each god sends one narrated letter the first time you meet their "
                  + "trigger condition. Off: the gods still react to play, just silently — "
                  + "no letters, ever.");
                list.GapLine();

                list.Label("Event impact: " + eventMagnitudeMultiplier.ToString("0.00") + "x");
                list.Label("How hard any single event (a birth, a repaired building, a mental "
                  + "break...) moves a god's satiation. 1.0x is the shipped default.");
                eventMagnitudeMultiplier = list.Slider(eventMagnitudeMultiplier, 0.25f, 3f);
                list.Gap();

                list.Label("Mood volatility: " + moodWalkMultiplier.ToString("0.00") + "x");
                list.Label("How much each god's private Mood wanders on its own between events. "
                  + "This never appears as a number in play — it only colors ambient narration "
                  + "elsewhere in the campaign. 1.0x is the shipped default; 0x freezes Mood "
                  + "wherever it last sat.");
                moodWalkMultiplier = list.Slider(moodWalkMultiplier, 0f, 3f);
            }
            else
            {
                list.Label("Every other option below only matters while the engine is enabled.");
            }

            list.End();
        }
    }

    public class RM_NinefoldMod : Mod
    {
        public static RM_NinefoldSettings settings;

        public RM_NinefoldMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_NinefoldSettings>();
        }

        public override string SettingsCategory()
        {
            return "Ninefold";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
