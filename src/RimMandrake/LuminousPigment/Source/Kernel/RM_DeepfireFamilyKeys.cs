// DEEPFIRE_FAMILY_SETTINGS_KEYED_1 / DEEPFIRE_FAMILY_SETTINGS_SAVE_LOAD_1. Verse-free kernel of how the Cuisine family
// toggles are saved: by stable family key (the DISABLED ones), so adding, removing or reordering families never resets or
// moves a toggle. An older settings file holds a positional bool list instead; it is read only to migrate, never written.
// LuminousPigmentSettings.ExposeData calls these two functions around the Scribe calls; SelfTest/LuminousPigmentFuzz.cs
// compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System.Collections.Generic;

namespace RimMandrake.LuminousPigment
{
    public static class RM_DeepfireFamilyKeys
    {
        // What is saved: the key of every family switched off, in family order.
        public static List<string> DisabledKeys(bool[] enabled, IList<string> keys)
        {
            var off = new List<string>();
            for (int i = 0; enabled != null && i < enabled.Length && i < keys.Count; i++)
            {
                if (!enabled[i]) off.Add(keys[i]);
            }
            return off;
        }

        // What is loaded. disabledKeys null = the file predates keyed saving; then a positional legacy list of exactly the
        // current family count migrates as-is (any other length cannot be mapped and is ignored). Neither present = the
        // current array is kept. Unknown keys (a family since removed) are ignored. Returns the array to use.
        public static bool[] Load(IList<string> disabledKeys, IList<bool> legacy, IList<string> keys, bool[] current)
        {
            if (disabledKeys != null)
            {
                var loaded = new bool[keys.Count];
                for (int i = 0; i < loaded.Length; i++) loaded[i] = true;
                foreach (string key in disabledKeys)
                {
                    int idx = keys.IndexOf(key);
                    if (idx >= 0) loaded[idx] = false;
                }
                return loaded;
            }
            if (legacy != null && legacy.Count == keys.Count)
            {
                var migrated = new bool[keys.Count];
                for (int i = 0; i < migrated.Length; i++) migrated[i] = legacy[i];
                return migrated;
            }
            return current;
        }
    }
}
