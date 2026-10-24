using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    // ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 1 settings (spec §5). Defaults = shipped behaviour. INSTANCE fields reached
    // through Cur, never public statics: the bridge's settings setter refuses a static field (Pits pilot, 2026-09-12).
    // Only switches that gate something built exist here; the sound channel, default scheme, group selection, showcase
    // and bed volume arrive with the phases that build them.
    public class RM_AtmosphericBaseSettings : ModSettings
    {
        public bool lightChannel = true;
        public bool playerTakeoverButton = true;
        public bool compositor = true;      // Phase 2: animate held lights at all
        public bool defaultMood = true;     // Phase 2: the gentle default (Lamplight) when nothing has pushed a mood
        public int defaultMoodGroup = 0;    // index into RM_SchemeKernel.DefaultGroups: ship, rooms, halls, exterior
        // Phase 3: territory. Only ever acts when TWO OR MORE claimants have pushed moods; the shipped default (one gentle
        // mood, nothing pushed) never reaches it, so none of these changes what an install with no consumer looks like.
        public bool territory = true;                 // the second-loudest mood holds ground beside the loudest (L5)
        public float territoryPeriodSeconds = 900f;   // one full turn of the boundary: slow, a front not a show
        public float territoryLeadShare = 0.6f;       // the louder claimant's share of the fixtures
        public float territoryRagged = 0.08f;         // how uneven the front is (0 = a straight line)
        // Phase 4: the tremor. Moods ranked third and below, at most three, brief flickers in their own palette (L6).
        public bool tremor = true;
        public int tremorCap = 3;                     // contributors; L6 caps it at three whatever this says
        public float tremorSlotSeconds = 30f;         // a fixture may flicker once per slot...
        public int tremorOneIn = 4;                   // ...in one slot of this many...
        public float tremorFlickerSeconds = 0.8f;     // ...for this long
        public float tremorMaxFraction = 0.04f;       // never more than this share of the lights at once (ceiling 0.10)

        /// <summary>The territory knobs as the kernel takes them, clamped to the laws' bounds.</summary>
        public RM_TerritoryTuning TerritoryTuning => RM_TerritoryTuning.Clamp(new RM_TerritoryTuning
        {
            periodSeconds = territoryPeriodSeconds, leadShare = territoryLeadShare, ragged = territoryRagged,
        });

        /// <summary>The tremor knobs as the kernel takes them, clamped (L6's cap of three is enforced there).</summary>
        public RM_TremorTuning TremorTuning => RM_TremorTuning.Clamp(new RM_TremorTuning
        {
            cap = tremorCap, slotSeconds = tremorSlotSeconds, oneIn = tremorOneIn,
            flickerSeconds = tremorFlickerSeconds, maxFraction = tremorMaxFraction,
        });

        private static readonly RM_AtmosphericBaseSettings Defaults = new RM_AtmosphericBaseSettings();

        public static RM_AtmosphericBaseSettings Cur => RM_AtmosphericBaseMod.settings ?? Defaults;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lightChannel, "lightChannel", true);
            Scribe_Values.Look(ref playerTakeoverButton, "playerTakeoverButton", true);
            Scribe_Values.Look(ref compositor, "compositor", true);
            Scribe_Values.Look(ref defaultMood, "defaultMood", true);
            Scribe_Values.Look(ref defaultMoodGroup, "defaultMoodGroup", 0);
            Scribe_Values.Look(ref territory, "territory", true);
            Scribe_Values.Look(ref territoryPeriodSeconds, "territoryPeriodSeconds", 900f);
            Scribe_Values.Look(ref territoryLeadShare, "territoryLeadShare", 0.6f);
            Scribe_Values.Look(ref territoryRagged, "territoryRagged", 0.08f);
            Scribe_Values.Look(ref tremor, "tremor", true);
            Scribe_Values.Look(ref tremorCap, "tremorCap", 3);
            Scribe_Values.Look(ref tremorSlotSeconds, "tremorSlotSeconds", 30f);
            Scribe_Values.Look(ref tremorOneIn, "tremorOneIn", 4);
            Scribe_Values.Look(ref tremorFlickerSeconds, "tremorFlickerSeconds", 0.8f);
            Scribe_Values.Look(ref tremorMaxFraction, "tremorMaxFraction", 0.04f);
        }

        private static readonly string[] GroupLabels = { "Every handed-over light", "Rooms only", "Halls only", "Outdoors only" };

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public instance bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            var fresh = new RM_AtmosphericBaseSettings();
            foreach (FieldInfo f in typeof(RM_AtmosphericBaseSettings).GetFields(BindingFlags.Public | BindingFlags.Instance))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(fresh);
            return d;
        }

        public void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_AtmosphericBaseSettings).GetField(n, BindingFlags.Public | BindingFlags.Instance);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(this, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        private bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names)
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
            list.Label(RimMandrake.Shared.SettingsKitCore.ScopeTag(scope) + " changes apply to what is on the map now");
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 400f;

        /// <summary>Owner decision §9.1 (2026-10-23): "hand over every lamp on this map", beside the per-lamp opt-in,
        /// with its reverse. Acts on the map being viewed; shown only where the player may choose
        /// (RM_AtmosphericDesignators.PlayerMayChoose: channel on, buttons on, no scenario deciding).</summary>
        private static void DrawWholeMapButtons(Listing_Standard list)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_AtmosphericBase comp = RM_MapComponent_AtmosphericBase.For(map);
            if (comp == null)
            {
                list.Label("Load a game to hand over every lamp on a map at once.");
                return;
            }
            if (!RM_AtmosphericDesignators.PlayerMayChoose(map))
            {
                list.Label(comp.scenarioDecides ? "This map's scenario decides which lights are handed over."
                                                : "Handing over every lamp needs the light channel and the hand-over buttons on.");
                return;
            }
            int unheld = comp.UnheldEligibleCount();
            if (list.ButtonText("Hand over every lamp on this map (" + unheld + " not yet handed over)"))
                Messages.Message("Atmospheric Base: " + comp.TakeOverAll() + " lights handed over.", MessageTypeDefOf.NeutralEvent, false);
            if (comp.TakenCount > 0 && list.ButtonText("Take glow back from every lamp on this map (" + comp.TakenCount + ")"))
                Messages.Message("Atmospheric Base: " + comp.ReleaseAll() + " lights given back their own glow.", MessageTypeDefOf.NeutralEvent, false);
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            // Scopes audited per read site: both switches are read every frame (map component) and on every button query.
            if (Group(list, "Light channel", RimMandrake.Shared.SettingScope.Now, new[] { "lightChannel" }))
            {
                list.CheckboxLabeled("Atmospheric Base may drive lights", ref lightChannel,
                    "Off: every light handed to Atmospheric Base is given back at once, at exactly the colour it had, "
                  + "and nothing can be handed over. With this off the game is lit as if the mod were absent.");
                list.GapLine();
            }

            if (Group(list, "Hand-over buttons", RimMandrake.Shared.SettingScope.Now, new[] { "playerTakeoverButton" }))
            {
                list.CheckboxLabeled("Show the hand-over buttons on lights", ref playerTakeoverButton,
                    "Selecting a lamp, wall light or floor light you own shows \"Hand glow to Atmospheric Base\" and "
                  + "\"Take glow back\". Off: the buttons are hidden; lights already handed over stay handed over, and "
                  + "scenarios and other mods can still hand lights over. Maps whose scenario decides never show them.");
                DrawWholeMapButtons(list);
                list.GapLine();
            }

            if (Group(list, "Moods", RimMandrake.Shared.SettingScope.Now, new[] { "compositor", "defaultMood", "defaultMoodGroup" }))
            {
                list.CheckboxLabeled("Animate handed-over lights", ref compositor,
                    "On: handed-over lights show the mood running on this map, stepping through a few fixed colours. "
                  + "Off: they keep their own colour (they stay handed over) and nothing animates.");
                list.CheckboxLabeled("Run the gentle default when nothing else does", ref defaultMood,
                    "Lamplight: each room breathes slowly through three warm levels, all bright enough to work under. "
                  + "Runs only on lights you handed over, and only while no scenario or mod has set a mood. "
                  + "Off: with no mood set, handed-over lights keep their own colour.");
                int gi = defaultMoodGroup < 0 || defaultMoodGroup >= GroupLabels.Length ? 0 : defaultMoodGroup;
                if (list.ButtonText("The default runs on: " + GroupLabels[gi]))
                {
                    var opts = new List<FloatMenuOption>();
                    for (int i = 0; i < GroupLabels.Length; i++)
                    {
                        int k = i;
                        opts.Add(new FloatMenuOption(GroupLabels[i], () => defaultMoodGroup = k));
                    }
                    Find.WindowStack.Add(new FloatMenu(opts));
                }
                list.GapLine();
            }

            if (Group(list, "Territory (two moods at once)", RimMandrake.Shared.SettingScope.Now,
                      new[] { "territory", "territoryPeriodSeconds", "territoryLeadShare", "territoryRagged" }))
            {
                list.CheckboxLabeled("Two moods share the lights", ref territory,
                    "Only matters when two or more scenarios or mods have each set a mood. On: the louder holds most of the "
                  + "handed-over lights, the other holds the rest, each in its own colours, and the line between them turns "
                  + "slowly around the ship. Off: only the loudest mood shows. The gentle default never uses this.");
                list.Label("One full turn of the boundary: " + Mathf.RoundToInt(territoryPeriodSeconds) + " s (real time)");
                territoryPeriodSeconds = Mathf.Round(list.Slider(territoryPeriodSeconds, RM_TerritoryKernel.MinPeriodSeconds, 3600f) / 30f) * 30f;
                list.Label("Share of the lights the louder mood holds: " + Mathf.RoundToInt(territoryLeadShare * 100f) + "%");
                territoryLeadShare = Mathf.Round(list.Slider(territoryLeadShare, RM_TerritoryKernel.MinLeadShare, RM_TerritoryKernel.MaxLeadShare) * 20f) / 20f;
                list.Label("How uneven the boundary is: " + Mathf.RoundToInt(territoryRagged * 100f) + "% (0 = a straight line)");
                territoryRagged = Mathf.Round(list.Slider(territoryRagged, 0f, RM_TerritoryKernel.MaxRagged) * 100f) / 100f;
                list.GapLine();
            }

            if (Group(list, "Tremor (third and later moods)", RimMandrake.Shared.SettingScope.Now,
                      new[] { "tremor", "tremorCap", "tremorSlotSeconds", "tremorOneIn", "tremorFlickerSeconds", "tremorMaxFraction" }))
            {
                list.CheckboxLabeled("Quieter moods stir the lights", ref tremor,
                    "Only matters when three or more moods are set. On: up to three quieter moods show as brief, scattered "
                  + "flickers in their own colours, never holding ground. Off: only the two loudest moods show.");
                list.Label("Moods that may stir: " + tremorCap + " (at most " + RM_TremorKernel.LawCap + ")");
                tremorCap = Mathf.RoundToInt(list.Slider(tremorCap, 0f, RM_TremorKernel.LawCap));
                list.Label("A light may flicker once every " + Mathf.RoundToInt(tremorSlotSeconds) + " s, in one of " + tremorOneIn + " such windows");
                tremorSlotSeconds = Mathf.Round(list.Slider(tremorSlotSeconds, RM_TremorKernel.MinSlotSeconds, 120f));
                tremorOneIn = Mathf.RoundToInt(list.Slider(tremorOneIn, 1f, 12f));
                list.Label("One flicker lasts " + tremorFlickerSeconds.ToString("0.0") + " s");
                tremorFlickerSeconds = Mathf.Round(list.Slider(tremorFlickerSeconds, 0.1f, RM_TremorKernel.MaxFlickerSeconds) * 10f) / 10f;
                list.Label("Never more than " + Mathf.RoundToInt(tremorMaxFraction * 100f) + "% of the lights at once (one light at the least)");
                tremorMaxFraction = Mathf.Round(list.Slider(tremorMaxFraction, 0.01f, RM_TremorKernel.MaxFraction) * 100f) / 100f;
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }
}
