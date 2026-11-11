// SETTINGS_SCREEN_KIT_1 - the logic of a settings screen with NO Verse type in it, so the offline selftest
// (src/RimMandrake/_Shared/SettingsKit/SelfTest) compiles THIS file. Linked into a mod by <Compile Include>.
// Model: sections of controls; each control has a key, label, shipped default and a scope tag. Values live
// in a caller-owned dictionary (the mod's own fields stay the source of truth through get/set callbacks).
using System;
using System.Collections.Generic;

namespace RimMandrake.Shared
{
    /// <summary>When a changed setting takes effect. Purely a label: it never alters a stored value.</summary>
    internal enum SettingScope { Now, NextPulse, NewMapsOnly, NewPondsOnly }

    internal sealed class SettingControl
    {
        public string Key;
        public string Label;
        public object Default;
        public SettingScope Scope;
        public SettingControl(string key, string label, object def, SettingScope scope)
        { Key = key; Label = label; Default = def; Scope = scope; }
    }

    internal sealed class SettingSection
    {
        public string Title;
        public List<SettingControl> Controls = new List<SettingControl>();
        public SettingSection(string title) { Title = title; }
        public SettingSection Add(string key, string label, object def, SettingScope scope = SettingScope.Now)
        { Controls.Add(new SettingControl(key, label, def, scope)); return this; }
    }

    internal static class SettingsKitCore
    {
        public static string ScopeTag(SettingScope s)
        {
            switch (s)
            {
                case SettingScope.NextPulse: return "[next pulse]";
                case SettingScope.NewMapsOnly: return "[new maps only]";
                case SettingScope.NewPondsOnly: return "[new ponds only]";
                default: return "[now]";
            }
        }

        /// <summary>Case-insensitive substring match; a null/blank query matches everything.</summary>
        public static bool Matches(string label, string query)
        {
            if (string.IsNullOrWhiteSpace(query)) return true;
            return label != null && label.IndexOf(query.Trim(), StringComparison.OrdinalIgnoreCase) >= 0;
        }

        /// <summary>Controls of a section that pass the search (a section title match shows the whole section).</summary>
        public static List<SettingControl> Visible(SettingSection sec, string query)
        {
            var r = new List<SettingControl>();
            bool titleHit = !string.IsNullOrWhiteSpace(query) && Matches(sec.Title, query);
            foreach (SettingControl c in sec.Controls)
                if (titleHit || Matches(c.Label, query)) r.Add(c);
            return r;
        }

        /// <summary>Restores every control of the section to its shipped default; returns how many were written.</summary>
        public static int ResetSection(SettingSection sec, IDictionary<string, object> values)
        {
            int n = 0;
            foreach (SettingControl c in sec.Controls) { values[c.Key] = c.Default; n++; }
            return n;
        }

        /// <summary>True when any control in the section differs from its shipped default (for a "modified" dot).</summary>
        public static bool IsModified(SettingSection sec, IDictionary<string, object> values)
        {
            foreach (SettingControl c in sec.Controls)
                if (values.TryGetValue(c.Key, out object v) && !Equals(v, c.Default)) return true;
            return false;
        }

        /// <summary>Label as drawn: the text plus its scope tag. Pure; never touches a value.</summary>
        public static string TaggedLabel(SettingControl c) { return c.Label + " " + ScopeTag(c.Scope); }
    }
}
