using UnityEngine;
using Verse;

namespace RimMandrake.RaidRedesigner
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for RaidRedesigner.
    //
    // What this mod actually runs today (verified by reading every .cs file
    // in this folder before writing this): pure roster bookkeeping. Eight
    // Harmony postfixes (Patch_FledRaiderAndCaptain, Patch_PrisonerEscaped,
    // Patch_PrisonerReleasedOrNamedHunter [x2], Patch_ColonistKidnapped,
    // Patch_CaravanRobbed) all funnel through ONE choke point,
    // GameComponent_OldFriends.RecordEncounter, so that single method is
    // where the master switch and the tuning multiplier are enforced.
    // There is NO Oracle/LLM subprocess call anywhere in this mod yet
    // (grepped for "Oracle"/"claude -p": zero hits) — the roster this mod
    // builds is raw material for a future LLM consumer
    // (PLOT_MECHANISM_MODS_WAVE_1 Part 1), not a caller of one. So there is
    // no LLM on/off or rate/timeout setting to add here; when that consumer
    // lands it gets its own gate against whatever OracleClient becomes.
    //
    // Precedent: src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    // ════════════════════════════════════════════════════════════════════
    public class RaidRedesignerSettings : ModSettings
    {
        // Master switch. Off: RecordEncounter is a no-op (returns null) —
        // no roster entries are created or updated, no pawns get pinned as
        // forced-kept world pawns. Every one of the eight capture hooks
        // already null-checks RecordEncounter's return before using it, so
        // this degrades cleanly to "the roster mechanic doesn't exist."
        public static bool rosterTrackingEnabled = true;

        // Was the hardcoded constant GameComponent_OldFriends.MaxLivingEntries (24).
        public static int maxLivingEntries = 24;

        // Scales every grudgeDelta/notabilityDelta the eight capture hooks
        // pass in. 1.0x = the shipped values (each hook's own hardcoded
        // deltas, e.g. +25 grudge for a kidnapping, +20 notability for a
        // captain fleeing alive).
        public static float grudgeNotabilityMultiplier = 1f;

        // Was the unconditional `if (pin) WorldPawnPinning.PinForever(pawn)`.
        // Off: notable pawns are never force-kept in the world pawn pool —
        // they can still be garbage-collected like any ordinary world pawn,
        // trading "that raider might show up again" for a smaller save/less
        // world-pawn bloat over a long game.
        public static bool pinEncounteredPawns = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref rosterTrackingEnabled, "rosterTrackingEnabled", true);
            Scribe_Values.Look(ref maxLivingEntries, "maxLivingEntries", 24);
            Scribe_Values.Look(ref grudgeNotabilityMultiplier, "grudgeNotabilityMultiplier", 1f);
            Scribe_Values.Look(ref pinEncounteredPawns, "pinEncounteredPawns", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Track old friends and enemies", ref rosterTrackingEnabled,
                "Remembers raiders, escaped prisoners, kidnappers and betrayed traders you've "
              + "met before, with a grudge and notability score for each. Off: nothing is "
              + "recorded and no one is specially remembered.");
            list.Gap();

            if (rosterTrackingEnabled)
            {
                list.Label("Roster size cap: " + maxLivingEntries + " people remembered at once");
                maxLivingEntries = (int)list.Slider(maxLivingEntries, 8f, 48f);
                list.Label("When full, the least notable person is forgotten to make room for a new one.");
                list.Gap();

                list.Label("Grudge/notability strength: " + grudgeNotabilityMultiplier.ToString("0.00") + "x");
                grudgeNotabilityMultiplier = list.Slider(grudgeNotabilityMultiplier, 0f, 3f);
                list.Label("How strongly each encounter changes a person's grudge and notability. "
                  + "0 keeps the roster but freezes every score.");
                list.Gap();

                list.CheckboxLabeled("Remember them permanently", ref pinEncounteredPawns,
                    "Keeps notable people from ever being cleaned up in the background, so they can "
                  + "always come back later. Off: they can still fade away over a very long game.");
            }

            list.End();
        }
    }

    public class RaidRedesignerOptionsMod : Mod
    {
        public static RaidRedesignerSettings settings;

        public RaidRedesignerOptionsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RaidRedesignerSettings>();
        }

        public override string SettingsCategory()
        {
            return "Raid Redesigner";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
