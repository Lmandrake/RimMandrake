using System.Collections.Generic;
using System.Reflection;
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

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RaidRedesignerSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RaidRedesignerSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts or a save loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 400f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            // Scopes audited per read site: all four settings are read inside GameComponent_OldFriends.RecordEncounter / EnforceCap,
            // which run when an encounter is recorded (a raider flees, a prisoner escapes, a colonist is kidnapped, a caravan is
            // robbed). Nothing is read at map or world generation and nothing on a tick, so every change lands at the next encounter.
            if (Group(list, "Old friends and enemies", RimMandrake.Shared.SettingScope.NextPulse, new[] { "rosterTrackingEnabled" }))
            {
                list.CheckboxLabeled("Track old friends and enemies", ref rosterTrackingEnabled,
                    "Remembers raiders, escaped prisoners, kidnappers and betrayed traders you've "
                  + "met before, with a grudge and notability score for each. Off: nothing is "
                  + "recorded and no one is specially remembered.");
                list.GapLine();
            }

            if (Group(list, "Roster size and grudge strength", RimMandrake.Shared.SettingScope.NextPulse, new[] { "maxLivingEntries", "grudgeNotabilityMultiplier" }))
            {
                list.Label("Roster size cap: " + maxLivingEntries + " people remembered at once");
                maxLivingEntries = (int)list.Slider(maxLivingEntries, 8f, 48f);
                list.Label("When full, the least notable person is forgotten to make room for a new one.");
                list.Label("Grudge/notability strength: " + grudgeNotabilityMultiplier.ToString("0.00") + "x");
                grudgeNotabilityMultiplier = list.Slider(grudgeNotabilityMultiplier, 0f, 3f);
                list.Label("How strongly each encounter changes a person's grudge and notability. "
                  + "0 keeps the roster but freezes every score.");
                list.GapLine();
            }

            if (Group(list, "Remember them permanently", RimMandrake.Shared.SettingScope.NextPulse, new[] { "pinEncounteredPawns" }))
            {
                list.CheckboxLabeled("Remember them permanently", ref pinEncounteredPawns,
                    "Keeps notable people from ever being cleaned up in the background, so they can "
                  + "always come back later. Off: they can still fade away over a very long game. "
                  + "People already kept stay kept.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
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
