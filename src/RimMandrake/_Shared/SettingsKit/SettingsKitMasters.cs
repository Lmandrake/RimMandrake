// SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST - master switches and reset-all for a SettingsKit screen, with NO Verse type in
// it, so the offline selftest (src/RimMandrake/_Shared/SettingsKit/SelfTest) compiles THIS file. OPT-IN: a separate file
// from SettingsKitCore.cs on purpose. Every committed kit DLL's .srchash hashes the kit files it compiles, so a change to
// SettingsKitCore.cs would force a rebuild of every mod that links the kit; a mod that wants master switches links this
// file (and SettingsKitMastersDrawer.cs) with <Compile Include> and nothing else changes for the rest.
using System;
using System.Collections.Generic;

namespace RimMandrake.Shared
{
    /// <summary>
    /// Which setting is the master switch of which. A dependent is LIVE only while every master it was declared under is on,
    /// and each of those masters is itself live (chains: tapsEnabled -> tapEvents -> theftGoodwill -> theftGoodwillPerDay).
    /// A setting kept live on purpose (read even with the master off) is declared Independent, so an audit can tell
    /// "decided: independent" from "forgotten". A screen that never builds one of these draws exactly as before.
    /// </summary>
    internal sealed class SettingDependencies
    {
        private readonly Dictionary<string, List<string>> mastersOf = new Dictionary<string, List<string>>();
        private readonly HashSet<string> independent = new HashSet<string>();
        private readonly Dictionary<string, string> names = new Dictionary<string, string>();

        /// <summary>Declare master as a switch of each dependent (a dependent may have several masters: all must be on).
        /// Refuses a self-dependency or a cycle (either would make a setting unreachable).</summary>
        public SettingDependencies Declare(string master, params string[] dependents)
        {
            if (string.IsNullOrEmpty(master)) throw new ArgumentException("master key is empty");
            foreach (string d in dependents)
            {
                if (d == master || DependsOn(master, d)) throw new ArgumentException("master cycle: " + master + " <-> " + d);
                if (!mastersOf.TryGetValue(d, out List<string> l)) mastersOf[d] = l = new List<string>();
                if (!l.Contains(master)) l.Add(master);
            }
            return this;
        }

        /// <summary>Mark settings as deliberately live whatever the masters say (read even with the master off).</summary>
        public SettingDependencies Independent(params string[] keys) { foreach (string k in keys) independent.Add(k); return this; }

        /// <summary>A reader-facing name for a master, used in the "greyed because" tooltip. Optional.</summary>
        public SettingDependencies Name(string key, string label) { names[key] = label; return this; }

        public string NameOf(string key) { return names.TryGetValue(key, out string n) ? n : key; }
        public IList<string> MastersOf(string key) { return mastersOf.TryGetValue(key, out List<string> l) ? l : (IList<string>)new string[0]; }
        public bool IsDependent(string key) { return mastersOf.ContainsKey(key); }
        public bool IsMaster(string key) { foreach (List<string> l in mastersOf.Values) if (l.Contains(key)) return true; return false; }
        public bool IsIndependent(string key) { return independent.Contains(key); }
        public bool IsClassified(string key) { return IsDependent(key) || IsMaster(key) || IsIndependent(key); }

        /// <summary>True when key is (transitively) under master.</summary>
        public bool DependsOn(string key, string master)
        {
            var seen = new HashSet<string>();
            var stack = new Stack<string>();
            stack.Push(key);
            while (stack.Count > 0)
            {
                string k = stack.Pop();
                if (!seen.Add(k)) continue;
                foreach (string m in MastersOf(k)) { if (m == master) return true; stack.Push(m); }
            }
            return false;
        }

        /// <summary>Live = every master up the chain reads on. isOn reads a master's CURRENT value (see SettingsKitMasters.IsOn).</summary>
        public bool IsLive(string key, Func<string, bool> isOn) { return OffMasters(key, isOn).Count == 0; }

        /// <summary>The masters (direct or up the chain) that are currently off; empty = live. Used by the tooltip.</summary>
        public List<string> OffMasters(string key, Func<string, bool> isOn)
        {
            var r = new List<string>();
            var seen = new HashSet<string>();
            var stack = new Stack<string>();
            stack.Push(key);
            while (stack.Count > 0)
            {
                string k = stack.Pop();
                if (!seen.Add(k)) continue;
                foreach (string m in MastersOf(k)) { if (!isOn(m) && !r.Contains(m)) r.Add(m); stack.Push(m); }
            }
            return r;
        }

        /// <summary>Of the given keys, those neither master, dependent nor Independent (an audit's "forgotten" list).</summary>
        public List<string> Unclassified(IEnumerable<string> keys)
        {
            var r = new List<string>();
            foreach (string k in keys) if (!IsClassified(k)) r.Add(k);
            return r;
        }
    }

    internal static class SettingsKitMasters
    {
        /// <summary>A master's value read as a switch: bool as is; an enum is off only when named "Off" or "None"; a number
        /// is on above zero; a string when non-blank; null is off.</summary>
        public static bool IsOn(object v)
        {
            if (v == null) return false;
            if (v is bool b) return b;
            if (v is Enum) { string n = v.ToString(); return n != "Off" && n != "None"; }
            if (v is int i) return i > 0;
            if (v is float f) return f > 0f;
            if (v is double d) return d > 0d;
            if (v is string s) return !string.IsNullOrWhiteSpace(s);
            return true;
        }

        /// <summary>
        /// One Dependent scope's state (the drawer's whole decision, here so it is selftested). dead[i] is true for each key
        /// whose masters are off: that key's value is restored after drawing. Returns true (grey the block) only when NO key
        /// is live, so a scope holding a sub-switch with its own dependents stays drawable while the sub-switch is off.
        /// offMasters: the off masters that are not themselves keys of this scope (the tooltip's "switch on ...").
        /// </summary>
        public static bool ScopeGreyed(SettingDependencies deps, string[] keys, Func<string, bool> isOn, out bool[] dead, out List<string> offMasters)
        {
            dead = new bool[keys == null ? 0 : keys.Length];
            offMasters = new List<string>();
            if (deps == null || keys == null || keys.Length == 0) return false;
            bool anyLive = false;
            for (int i = 0; i < keys.Length; i++)
            {
                List<string> o = deps.OffMasters(keys[i], isOn);
                if (o.Count == 0) { anyLive = true; continue; }
                dead[i] = true;
                foreach (string m in o) if (!offMasters.Contains(m) && Array.IndexOf(keys, m) < 0) offMasters.Add(m);
            }
            return !anyLive;
        }

        public const string ResetAllLabel = "Reset all to defaults";

        /// <summary>The question the Reset-all button asks before it writes anything.</summary>
        public static string ResetAllConfirmText(string scopeName)
        {
            return "Reset every " + (string.IsNullOrWhiteSpace(scopeName) ? "" : scopeName + " ") +
                   "setting to its shipped default? Every change you made here is lost. This cannot be undone.";
        }

        /// <summary>Restores every control of every section to its shipped default; returns how many were written.</summary>
        public static int ResetAll(IEnumerable<SettingSection> sections, IDictionary<string, object> values)
        {
            int n = 0;
            foreach (SettingSection sec in sections) n += SettingsKitCore.ResetSection(sec, values);
            return n;
        }
    }
}
