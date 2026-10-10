using System.Reflection;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Sarlacc
{
    // ════════════════════════════════════════════════════════════════════
    // SARLACC_HABITAT_BUILD_1 — Mod Settings, per CLAUDE.md's standing rule
    // ("Every mod ships superb Mod Settings") and the draft's own §8 ruling
    // ("Mod Settings per MOD_OPTIONS_RETROFIT_1 (feature toggles incl.
    // rooting-in-play, changed-return hediffs, breach consequences)").
    //
    // STATIC fields, read from comps that have no Mod instance handy — same
    // shape as RSW_JawaIonWeaponsSettings (src/RimStarWars/JawaIonWeapons).
    //
    // ALL-OFF DEGRADES GRACEFULLY: with rootingInPlayEnabled off, a swimmer
    // just never roots (an ordinary, if unusual, wild predator forever). With
    // anchoredTitheEnabled off, an anchored sarlacc is inert scenery. With
    // changedReturnHediffsEnabled off, swallow-and-survive works exactly as
    // vanilla CompDevourer already does, with no hediff granted. Nothing NREs
    // and no def fails to resolve with every toggle off.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_SarlaccSettings : ModSettings
    {
        /// <summary>Fork 1: a swimmer that finds a seep or runs dry anchors visibly on the map.</summary>
        public static bool rootingInPlayEnabled = true;

        /// <summary>Multiplier on how fast a swimmer's water reserve drains (lower = swimmers live longer before rooting).</summary>
        public static float reserveDrainMultiplier = 1f;

        /// <summary>Show a message when a swimmer roots.</summary>
        public static bool rootingMessagesEnabled = true;

        /// <summary>Stage II: the anchored sarlacc's rare mouth-strike ("it strikes rarely, and only to tithe").</summary>
        public static bool anchoredTitheEnabled = true;

        /// <summary>Grant one of the seven changed-return hediffs (draft §4.5) to a pawn that survives being swallowed.</summary>
        public static bool changedReturnHediffsEnabled = true;

        /// <summary>Chance a survivor is granted a SECOND hediff on top of the first ("usually one, sometimes two").</summary>
        public static float secondHediffChance = 0.2f;

        /// <summary>Stage III: the breach flood's real (DBH-thirst-fillable, self-reverting)
        /// water terrain around a breached cistern. See MapComponent_SarlaccBreachFlood.</summary>
        public static bool breachFloodVisualEnabled = true;

        /// <summary>LONGSHADE_BEDAZZLE_MECHANICS_1 part 3 (tranche 1): every swallow leaves a
        /// readable sign — a disturbed patch of sand where the prey went under, and a
        /// message naming what was taken (vanilla already messages for the player's own).</summary>
        public static bool takeSignsEnabled = true;

        /// <summary>LONGSHADE_BEDAZZLE_MECHANICS_1 tranche 2, the swimmer's road: the
        /// once-per-map incident (Long Shade maps) in which one young swimmer swims rim
        /// to rim toward the biggest dew ring and roots there. Needs Creature Behaviors'
        /// shade-patch graph.</summary>
        public static bool swimmerRoadEnabled = true;

        /// <summary>When a road swimmer roots, every wild animal sheltering in that
        /// patch of shade breaks from it at once.</summary>
        public static bool rootingEvacuatesPatch = true;

        /// <summary>The road/seep swimmer's under-sand grinding (vanilla FleshbeastDigging) while it moves.</summary>
        public static bool swimmerGrindSoundEnabled = true;

        /// <summary>STILLSAND_EVENT_CREATURES_REMAINDER_1: the once-per-map incident (Stillsand maps)
        /// in which one swimmer swims for the largest buried seep and roots there.</summary>
        public static bool swimmerSeepEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref rootingInPlayEnabled, "rootingInPlayEnabled", true);
            Scribe_Values.Look(ref reserveDrainMultiplier, "reserveDrainMultiplier", 1f);
            Scribe_Values.Look(ref rootingMessagesEnabled, "rootingMessagesEnabled", true);
            Scribe_Values.Look(ref anchoredTitheEnabled, "anchoredTitheEnabled", true);
            Scribe_Values.Look(ref changedReturnHediffsEnabled, "changedReturnHediffsEnabled", true);
            Scribe_Values.Look(ref secondHediffChance, "secondHediffChance", 0.2f);
            Scribe_Values.Look(ref breachFloodVisualEnabled, "breachFloodVisualEnabled", true);
            Scribe_Values.Look(ref takeSignsEnabled, "takeSignsEnabled", true);
            Scribe_Values.Look(ref swimmerRoadEnabled, "swimmerRoadEnabled", true);
            Scribe_Values.Look(ref rootingEvacuatesPatch, "rootingEvacuatesPatch", true);
            Scribe_Values.Look(ref swimmerGrindSoundEnabled, "swimmerGrindSoundEnabled", true);
            Scribe_Values.Look(ref swimmerSeepEnabled, "swimmerSeepEnabled", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_SarlaccSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_SarlaccSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1200f;
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
                ? " changes take effect the next time the game starts"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards" : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Stage I to II: rooting in play", RimMandrake.Shared.SettingScope.Now, new[] { "rootingInPlayEnabled", "reserveDrainMultiplier", "rootingMessagesEnabled" }))
            {
                list.CheckboxLabeled("Swimmers root in play", ref rootingInPlayEnabled,
                    "A sarlacc swimmer that finds a buried seep, or spends its whole birth-water reserve, anchors on the spot and becomes Stage II (the anchored sarlacc). Off: swimmers never root and behave as an ordinary wild predator forever.");
                list.Label((TaggedString)("Reserve drain speed: " + reserveDrainMultiplier.ToString("0.00") + "x"), -1f, "Higher means swimmers root sooner; lower lets them roam longer before running dry.");
                reserveDrainMultiplier = list.Slider(reserveDrainMultiplier, 0.25f, 4f);
                list.CheckboxLabeled("Announce rooting", ref rootingMessagesEnabled,
                    "Show a message the moment a swimmer roots.");
                list.GapLine();
            }

            if (Group(list, "Stage II: the anchored sarlacc's tithe", RimMandrake.Shared.SettingScope.Now, new[] { "anchoredTitheEnabled", "takeSignsEnabled" }))
            {
                list.CheckboxLabeled("Anchored sarlaccs strike", ref anchoredTitheEnabled,
                    "An anchored sarlacc rarely strikes whatever stands beside its mouth. Off: it is inert scenery.");
                list.CheckboxLabeled("Swallows leave a sign", ref takeSignsEnabled,
                    "When a swimmer swallows anything, the sand where it went under is left churned and a message names what was taken. Off: only your own colonists' and animals' swallows are announced, and wild prey goes under without a trace until it is spat out.");
                list.GapLine();
            }

            if (Group(list, "The swimmer's road (Long Shade)", RimMandrake.Shared.SettingScope.Now, new[] { "swimmerRoadEnabled", "rootingEvacuatesPatch", "swimmerGrindSoundEnabled" }))
            {
                list.CheckboxLabeled("Swimmer's road incident", ref swimmerRoadEnabled,
                    "Once per map, ever, on a Long Shade map: one young swimmer swims shade to shade toward the biggest dew ring on soft ground and roots there. Needs Creature Behaviors. Off: the incident is never picked, and a swimmer already on the road wanders like any other. Read when the storyteller rolls and every job step, so it is not a world-generation setting.");
                list.CheckboxLabeled("Rooting empties the patch", ref rootingEvacuatesPatch,
                    "When the road swimmer roots, every wild animal sheltering in that shade breaks from it at once. Off: they stay until the mouth takes one.");
                list.CheckboxLabeled("Swimmer grinds under the sand", ref swimmerGrindSoundEnabled,
                    "While the road or seep swimmer is moving you hear it grinding under the sand. Off: it moves silently. Sound only.");
                list.GapLine();
            }

            if (Group(list, "The swimmer comes to root (Stillsand)", RimMandrake.Shared.SettingScope.Now, new[] { "swimmerSeepEnabled" }))
            {
                list.CheckboxLabeled("Seep-rooting incident", ref swimmerSeepEnabled,
                    "Once per map, ever, on a Stillsand map with a sarlacc seep: one swimmer swims for the largest buried seep and roots over it for good. Needs no other mod. Off: the incident is never picked, and a swimmer already on its way wanders like any other.");
                list.GapLine();
            }

            if (Group(list, "Changed on return", RimMandrake.Shared.SettingScope.Now, new[] { "changedReturnHediffsEnabled", "secondHediffChance" }))
            {
                list.CheckboxLabeled("Grant changed-return hediffs", ref changedReturnHediffsEnabled,
                    "A pawn who is swallowed by a sarlacc and survives to be spat free is permanently changed by it (one of seven effects). Off: swallow-and-survive works as the underlying swallow mechanic already does, with no lasting effect.");
                list.Label((TaggedString)("Chance of a second effect: " + secondHediffChance.ToStringPercent("0")), -1f, "Only used while changed-return hediffs are on.");
                secondHediffChance = list.Slider(secondHediffChance, 0f, 1f);
                list.GapLine();
            }

            if (Group(list, "Stage III: breaching a cistern", RimMandrake.Shared.SettingScope.Now, new[] { "breachFloodVisualEnabled" }))
            {
                list.CheckboxLabeled("Flood the surface on breach", ref breachFloodVisualEnabled,
                    "Breaching a cistern turns the surrounding sand into real shallow water for a few days, a drinkable source while it lasts, then dry again. Off: the breach still ends the cistern, without the flood.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RSW_SarlaccMod : Mod
    {
        public static RSW_SarlaccSettings settings;

        public RSW_SarlaccMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_SarlaccSettings>();
        }

        public override string SettingsCategory()
        {
            return "Sarlacc — Native Habitat";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
