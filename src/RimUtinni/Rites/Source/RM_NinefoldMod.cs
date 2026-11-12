using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.Rites
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Ninefold, the nine gods'
    // engine inside Salvation Rites (folded in from mandrake.rm.ninefold
    // 2026-10-22; settings saved under the old mod are not carried over).
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData, a DoWindowContents
    // helper called from the Mod subclass).
    //
    // Ninefold's own "safe core" doctrine (GameComponent_Ninefold.cs class
    // header, §9: "the vector, all event-driven deltas, the fickle-Mood
    // random walk... pure read/compute/text. No live mutation") means every
    // one of the nineteen Patch_*.cs event hooks funnels through exactly two
    // choke points on GameComponent_Ninefold: ApplyDelta and TryFirstContact
    // (NotifyViolentDeath is the one extra caller of TryFirstContact).
    // Gating those, plus the tick that drives the Mood walk / Ta'Baa's
    // rooted erosion / the first-contact queue, turns the WHOLE engine on
    // and off from one place without touching any of the nineteen patch
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

        // Scales every ApplyDelta call (all nineteen event hooks route
        // through it) AND Ta'Baa's per-hour rooted erosion — the two
        // hardcoded numbers this engine's own comments call "UNTUNED, a
        // first-pass ordering" (EventMagnitude.cs, GameComponent_Ninefold's
        // RootedErosionPerHour).
        public static float eventMagnitudeMultiplier = 1f;

        // Scales the per-god Mood random-walk step (GameComponent_Ninefold.
        // MoodAmplitude) — the other constant array flagged UNTUNED in the
        // same source comment.
        public static float moodWalkMultiplier = 1f;

        // NINEFOLD_FAVOUR_ODDS_BUILD_1 (design/Jawa/nine_faults_permanent_rite_2026-10-01.md
        // §4/§5): a god's band tilts the odds of a few incidents and
        // weathers in his domain. Off: every tilt reads x1, the vector still
        // moves. Strength scales each tilt's distance from x1 (0 = none,
        // 1 = the ruled table, 2 = double).
        public static bool favourOddsEnabled = true;
        public static float favourStrength = 1f;

        // The two offerings (Nine Faults' fresh-find mark and the Left
        // Behind's "Leave behind" toggle). Off: no gizmo, no mark, the rite
        // finds no eligible machine, departure moves no favour.
        public static bool offeringsEnabled = true;

        // SUMP_SINKING_RITE_BUILD_1: the Sinking (Ishko's rite at the tar). Read through SinkingGlue.Config() into
        // Kernel/SinkingKernel.cs, which decides every effect. The rite never lowers Imperial Heat.
        public static bool sinkingEnabled = true;
        public static bool sinkingHoldOffEnabled = true;
        public static bool sinkingRaidLullEnabled = true;
        public static bool sinkingOwnershipEraseEnabled = true;
        public static bool sinkingBeastLullEnabled = true;
        public static bool sinkingTrapFizzleEnabled = true;
        public static float sinkingValueFloor = 50f;
        public static float sinkingHoldOffMultiplier = 5f;
        public static int sinkingTarRadius = 3;
        public static float sinkingNormalHoldOffDays = 1f;
        public static float sinkingRaidLullDays = 10f;
        public static float sinkingRaidLullStrength = 0.5f;
        public static float sinkingBeastLullDays = 15f;
        public static int sinkingTrapCount = 3;
        public const string SinkingOwnershipExclusionsDefault = "Humanlike";
        public static string sinkingOwnershipExclusions = SinkingOwnershipExclusionsDefault;

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref engineEnabled, "engineEnabled", true);
            Scribe_Values.Look(ref firstContactLettersEnabled, "firstContactLettersEnabled", true);
            Scribe_Values.Look(ref eventMagnitudeMultiplier, "eventMagnitudeMultiplier", 1f);
            Scribe_Values.Look(ref moodWalkMultiplier, "moodWalkMultiplier", 1f);
            Scribe_Values.Look(ref favourOddsEnabled, "favourOddsEnabled", true);
            Scribe_Values.Look(ref favourStrength, "favourStrength", 1f);
            Scribe_Values.Look(ref offeringsEnabled, "offeringsEnabled", true);
            Scribe_Values.Look(ref sinkingEnabled, "sinkingEnabled", true);
            Scribe_Values.Look(ref sinkingHoldOffEnabled, "sinkingHoldOffEnabled", true);
            Scribe_Values.Look(ref sinkingRaidLullEnabled, "sinkingRaidLullEnabled", true);
            Scribe_Values.Look(ref sinkingOwnershipEraseEnabled, "sinkingOwnershipEraseEnabled", true);
            Scribe_Values.Look(ref sinkingBeastLullEnabled, "sinkingBeastLullEnabled", true);
            Scribe_Values.Look(ref sinkingTrapFizzleEnabled, "sinkingTrapFizzleEnabled", true);
            Scribe_Values.Look(ref sinkingValueFloor, "sinkingValueFloor", 50f);
            Scribe_Values.Look(ref sinkingHoldOffMultiplier, "sinkingHoldOffMultiplier", 5f);
            Scribe_Values.Look(ref sinkingTarRadius, "sinkingTarRadius", 3);
            Scribe_Values.Look(ref sinkingNormalHoldOffDays, "sinkingNormalHoldOffDays", 1f);
            Scribe_Values.Look(ref sinkingRaidLullDays, "sinkingRaidLullDays", 10f);
            Scribe_Values.Look(ref sinkingRaidLullStrength, "sinkingRaidLullStrength", 0.5f);
            Scribe_Values.Look(ref sinkingBeastLullDays, "sinkingBeastLullDays", 15f);
            Scribe_Values.Look(ref sinkingTrapCount, "sinkingTrapCount", 3);
            Scribe_Values.Look(ref sinkingOwnershipExclusions, "sinkingOwnershipExclusions", SinkingOwnershipExclusionsDefault);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_NinefoldSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static string[] SinkingSettingNames => new[] {
            "sinkingEnabled", "sinkingHoldOffEnabled", "sinkingRaidLullEnabled", "sinkingOwnershipEraseEnabled",
            "sinkingBeastLullEnabled", "sinkingTrapFizzleEnabled", "sinkingValueFloor", "sinkingHoldOffMultiplier",
            "sinkingNormalHoldOffDays", "sinkingRaidLullDays", "sinkingRaidLullStrength", "sinkingBeastLullDays",
            "sinkingTrapCount", "sinkingOwnershipExclusions", "sinkingTarRadius" };

        public static void ResetFields(string[] names)
        {
            if (System.Array.IndexOf(names, "sinkingOwnershipExclusions") >= 0) sinkingOwnershipExclusions = SinkingOwnershipExclusionsDefault;
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_NinefoldSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            // Scopes audited per read site (GameComponent_Ninefold, GodFavourTilt, Offerings): nothing is read at map or world
            // generation. The engine switch, letters, event impact, mood walk and offerings are read when an event or the hourly
            // tick runs, so they land now; the favour tilt is read only when an incident, trader, find or weather is rolled.
            if (Group(list, "Ninefold engine", RimMandrake.Shared.SettingScope.Now, new[] { "engineEnabled" }))
            {
                list.CheckboxLabeled("Enable the Ninefold engine", ref engineEnabled,
                    "The nine gods' satiation/mood tracking and their event-driven reactions "
                  + "to play. Off: completely inert - no tracking, no letters, no log lines, "
                  + "as if the mod were not installed. The other options only matter while this is on.");
                list.GapLine();
            }

            if (Group(list, "First-contact letters", RimMandrake.Shared.SettingScope.Now, new[] { "firstContactLettersEnabled" }))
            {
                list.CheckboxLabeled("First-contact letters", ref firstContactLettersEnabled,
                    "Each god sends one narrated letter the first time you meet their "
                  + "trigger condition. Off: the gods still react to play, just silently - "
                  + "no letters, ever.");
                list.GapLine();
            }

            if (Group(list, "Event impact and mood", RimMandrake.Shared.SettingScope.Now, new[] { "eventMagnitudeMultiplier", "moodWalkMultiplier" }))
            {
                list.Label("Event impact: " + eventMagnitudeMultiplier.ToString("0.00") + "x");
                list.Label("How hard any single event (a birth, a repaired building, a mental "
                  + "break...) moves a god's satiation. 1.0x is the shipped default.");
                eventMagnitudeMultiplier = list.Slider(eventMagnitudeMultiplier, 0.25f, 3f);
                list.Label("Mood volatility: " + moodWalkMultiplier.ToString("0.00") + "x");
                list.Label("How much each god's private Mood wanders on its own between events. "
                  + "This never appears as a number in play - it only colors ambient narration "
                  + "elsewhere in the campaign. 1.0x is the shipped default; 0x freezes Mood "
                  + "wherever it last sat.");
                moodWalkMultiplier = list.Slider(moodWalkMultiplier, 0f, 3f);
                list.GapLine();
            }

            if (Group(list, "Favour tilts the odds", RimMandrake.Shared.SettingScope.NextPulse, new[] { "favourOddsEnabled", "favourStrength" }))
            {
                list.CheckboxLabeled("Favour tilts the odds", ref favourOddsEnabled,
                    "A pleased or angered god makes a few things in his domain a little more "
                  + "or less likely on your home map: certain incidents, traders, finds and "
                  + "weather. Never labelled. Off: every chance is vanilla.");
                list.Label("Favour strength: " + favourStrength.ToString("0.00") + "x");
                list.Label("How far a god's standing bends the odds. 1.0x is the shipped "
                  + "table (x0.7 to x1.35); 0x is no effect.");
                favourStrength = list.Slider(favourStrength, 0f, 2f);
                list.GapLine();
            }

            if (Group(list, "Offerings (Nine Faults, the Left Behind)", RimMandrake.Shared.SettingScope.Now, new[] { "offeringsEnabled" }))
            {
                list.CheckboxLabeled("Offerings (Nine Faults, the Left Behind)", ref offeringsEnabled,
                    "Machines the clan has just found are marked as fresh finds the Nine Faults "
                  + "rite may burn out, and a working building can be marked to leave behind at "
                  + "gravship departure. Off: no marks, no toggle, no favour moved by either.");
                list.GapLine();
            }

            if (Group(list, "The Sinking (Ishko, at the tar)", RimMandrake.Shared.SettingScope.Now, SinkingSettingNames))
            {
                list.CheckboxLabeled("The Sinking", ref sinkingEnabled,
                    "Ishko's rite: worshippers give an item to the tar. Off: the rite offers no target and does nothing.");
                list.CheckboxLabeled("Imperial hold-off", ref sinkingHoldOffEnabled,
                    "After a Sinking the Empire's next probe or raid on this map comes several times later than it would. "
                  + "It never lowers Imperial Heat.");
                list.Label("Offering must lie within " + sinkingTarRadius + " cells of tar");
                sinkingTarRadius = Mathf.RoundToInt(list.Slider(sinkingTarRadius, 1f, 10f));
                list.Label("Hold-off multiplier: " + sinkingHoldOffMultiplier.ToString("0.0") + "x");
                sinkingHoldOffMultiplier = list.Slider(sinkingHoldOffMultiplier, 1f, 10f);
                list.Label("Normal Empire hold-off: " + sinkingNormalHoldOffDays.ToString("0.0") + " days");
                sinkingNormalHoldOffDays = list.Slider(sinkingNormalHoldOffDays, 0.5f, 10f);
                list.CheckboxLabeled("Raid lull (other factions)", ref sinkingRaidLullEnabled,
                    "For a while, raids by factions other than the Empire are less likely on this map.");
                list.Label("Raid lull: " + sinkingRaidLullDays.ToString("0") + " days, chance x" + (1f - sinkingRaidLullStrength).ToString("0.00"));
                sinkingRaidLullDays = list.Slider(sinkingRaidLullDays, 1f, 30f);
                sinkingRaidLullStrength = list.Slider(sinkingRaidLullStrength, 0f, 1f);
                list.CheckboxLabeled("Ownership erased", ref sinkingOwnershipEraseEnabled,
                    "Foreign claims on the colony's things on this map (stolen, disputed) are wiped. Faction suspicion is not.");
                list.Label("Never erase claims on (Humanlike, Animal, Mech, Building, Item):");
                sinkingOwnershipExclusions = list.TextEntry(sinkingOwnershipExclusions ?? "");
                list.CheckboxLabeled("Pitch offering: the tar beasts sleep", ref sinkingBeastLullEnabled,
                    "Sinking pitch lulls the tar bulges: building, digging and pumping do not wake them. An explosion still does.");
                list.Label("Beast lull: " + sinkingBeastLullDays.ToString("0") + " days");
                sinkingBeastLullDays = list.Slider(sinkingBeastLullDays, 1f, 30f);
                list.CheckboxLabeled("Dig-find offering: the next traps fizzle", ref sinkingTrapFizzleEnabled,
                    "Sinking a find from the dig makes the next dig traps fizzle harmlessly.");
                list.Label("Traps that fizzle: " + sinkingTrapCount);
                sinkingTrapCount = (int)list.Slider(sinkingTrapCount, 0f, 10f);
                list.Label("Value floor: " + sinkingValueFloor.ToString("0") + " silver");
                sinkingValueFloor = list.Slider(sinkingValueFloor, 0f, 1000f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_NinefoldMod : Mod
    {
        public static RM_NinefoldSettings settings;

        public RM_NinefoldMod(ModContentPack content) : base(content)
        {
            // Before any save loads: keeps saves from before the fold (class RimMandrake.Ninefold.*) loading.
            NinefoldLegacyTypeConverter.Register();
            settings = GetSettings<RM_NinefoldSettings>();
        }

        public override string SettingsCategory()
        {
            return "Salvation Rites";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
            RimMandrake.Shared.PatchApplier.ReforceOff();
        }
    }
}
