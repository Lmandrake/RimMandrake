// SETTINGS_SCREEN_KIT_1 - the in-game drawer over SettingsKitCore (Verse side). Linked by <Compile Include>
// together with SettingsKitCore.cs. Call from DoSettingsWindowContents inside a Listing_Standard.
// The mod keeps its own fields as the source of truth: values flow through get/set callbacks.
using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Shared
{
    internal static class SettingsKitDrawer
    {
        // Same wording and widget FlowWorks drew in FLOWWORKS_SETTINGS_SCOPE_RESET_1 (FL-5).
        public const string ResetLabel = "Reset this section to defaults";

        /// <summary>The per-section reset button. Returns true on the frame it was pressed (after onReset ran).</summary>
        public static bool ResetButton(Listing_Standard list, Action onReset)
        {
            if (!list.ButtonText(ResetLabel)) return false;
            if (onReset != null) onReset();
            return true;
        }

        /// <summary>Search box (state owned by the caller). Returns the possibly-edited query.</summary>
        public static string SearchBox(Listing_Standard list, string query)
        {
            string q = list.TextEntryLabeled("Search settings", query ?? "");
            return q;
        }

        /// <summary>Scope note under a control, using the same tag text the core defines.</summary>
        public static void ScopeNote(Listing_Standard list, SettingControl c)
        {
            if (c.Scope == SettingScope.Now) return;
            list.Label(SettingsKitCore.ScopeTag(c.Scope));
        }

        /// <summary>
        /// Draws collapsible sections for bool and float controls. get/set read and write the mod's field by key.
        /// collapsed is caller-owned (survives redraw). Float controls draw as a slider in [min,max] from ranges.
        /// </summary>
        public static void Draw(Listing_Standard list, IList<SettingSection> sections, string query,
            HashSet<string> collapsed, Func<string, object> get, Action<string, object> set,
            IDictionary<string, Vector2> ranges)
        {
            foreach (SettingSection sec in sections)
            {
                List<SettingControl> vis = SettingsKitCore.Visible(sec, query);
                if (vis.Count == 0) continue;
                bool open = !collapsed.Contains(sec.Title) || !string.IsNullOrWhiteSpace(query);
                string head = (open ? "- " : "+ ") + sec.Title;
                if (list.ButtonText(head))
                {
                    if (!collapsed.Remove(sec.Title)) collapsed.Add(sec.Title);
                }
                if (!open) continue;
                foreach (SettingControl c in vis)
                {
                    object v = get(c.Key);
                    if (c.Default is bool)
                    {
                        bool b = v is bool bb && bb;
                        list.CheckboxLabeled(SettingsKitCore.TaggedLabel(c), ref b);
                        set(c.Key, b);
                    }
                    else if (c.Default is float)
                    {
                        float f = v is float ff ? ff : (float)c.Default;
                        Vector2 rg = ranges != null && ranges.TryGetValue(c.Key, out Vector2 x) ? x : new Vector2(0f, 10f);
                        list.Label(SettingsKitCore.TaggedLabel(c) + ": " + f.ToString("0.##"));
                        f = list.Slider(f, rg.x, rg.y);
                        set(c.Key, f);
                    }
                }
                ResetButton(list, () =>
                {
                    var tmp = new Dictionary<string, object>();
                    SettingsKitCore.ResetSection(sec, tmp);
                    foreach (KeyValuePair<string, object> kv in tmp) set(kv.Key, kv.Value);
                });
                list.GapLine();
            }
        }
    }
}
