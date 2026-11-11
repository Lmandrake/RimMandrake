using System;
using System.Collections.Generic;
using System.Reflection;

namespace RimMandrake.FlowWorks
{
    /// <summary>FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING: the one reset helper every FlowWorks settings class without its own
    /// (Kit, Quarry, Sprinkler, Thirst, Drawbridge, Suspension, WallClimb, RaiderTrench, Swim, MapControl, Rivers) shares.
    /// Verse-free on purpose (compiled into the SelfTest project too). A class snapshots its shipped values with
    /// <see cref="Snapshot"/> in a static field declared BELOW its last public setting field: C# runs static initialisers in
    /// textual order, and the type initialises before any save is read, so a reset restores the shipped value even after
    /// ExposeData overwrote the field. Only public static bool/float/int fields that are not const/readonly are snapshotted.</summary>
    public static class RM_SettingsReset
    {
        private const BindingFlags Flags = BindingFlags.Public | BindingFlags.Static;

        public static Dictionary<string, object> Snapshot(Type t)
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in t.GetFields(Flags))
            {
                if (f.IsLiteral || f.IsInitOnly) continue;
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            }
            return d;
        }

        /// <summary>The named fields back to their snapshot value. Returns how many were reset; a name with no snapshot is skipped.</summary>
        public static int Reset(Type t, Dictionary<string, object> shipped, params string[] names)
        {
            int n = 0;
            foreach (string name in names)
            {
                FieldInfo f = t.GetField(name, Flags);
                if (f != null && shipped.TryGetValue(name, out object v)) { f.SetValue(null, v); n++; }
            }
            return n;
        }

        /// <summary>Every snapshotted field back to its shipped value.</summary>
        public static int ResetAll(Type t, Dictionary<string, object> shipped)
        {
            var names = new List<string>(shipped.Keys);
            return Reset(t, shipped, names.ToArray());
        }
    }
}
