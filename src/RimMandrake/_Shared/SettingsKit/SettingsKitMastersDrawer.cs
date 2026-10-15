// SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST - the in-game half of SettingsKitMasters.cs (Verse side): the greyed dependent
// scope and the confirmed Reset-all button. OPT-IN, linked by <Compile Include> together with SettingsKitMasters.cs (and the
// existing SettingsKitCore.cs). No UnityEngine.GUI here on purpose: many kit users reference only UnityEngine.CoreModule.
using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Shared
{
    internal static class SettingsKitMastersDrawer
    {
        /// <summary>
        /// A "Reset all to defaults" button that asks first: onConfirmed runs only when the player confirms the dialog.
        /// scopeName names what is reset ("Pyrelands") in the question. Returns true on the frame the button was pressed
        /// (the dialog is open, nothing reset yet).
        /// </summary>
        public static bool ResetAllButton(Listing_Standard list, string scopeName, Action onConfirmed)
        {
            if (!list.ButtonText(SettingsKitMasters.ResetAllLabel)) return false;
            Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(SettingsKitMasters.ResetAllConfirmText(scopeName),
                () => { if (onConfirmed != null) onConfirmed(); }, destructive: true));
            return true;
        }

        /// <summary>
        /// Wrap the drawing of dependent controls:
        /// <c>using (SettingsKitMastersDrawer.Dependent(list, deps, get, set, "keyA", "keyB")) { ...draw them... }</c>.
        /// Every key whose masters are off is non-interactive: its value is snapshotted on entry and written back on exit,
        /// so a click, drag or keystroke on it changes nothing and the player's value survives the master being off. When no
        /// key in the scope is live the block is drawn under a dark shade with a tooltip naming the master that is off. Put
        /// a sub-switch in the same scope as its own dependents (it stays live, so the block stays drawable) and wrap the
        /// dependents again in a nested scope; keep keys with DIFFERENT masters in separate scopes.
        /// get/set read and write the mod's own field by key; get must return a COPY
        /// of a collection-valued setting so the snapshot is not mutated in place.
        /// </summary>
        public static IDisposable Dependent(Listing_Standard list, SettingDependencies deps, Func<string, object> get,
            Action<string, object> set, params string[] keys)
        {
            return new DependentScope(list, deps, get, set, keys);
        }

        private sealed class DependentScope : IDisposable
        {
            private static readonly Color Shade = new Color(0.08f, 0.08f, 0.08f, 0.6f);
            // greyed scopes currently open: a scope nested inside a greyed one draws no second shade or tooltip
            private static int greyDepth;
            private readonly Listing_Standard list;
            private readonly Action<string, object> set;
            private readonly string[] keys;
            private readonly bool[] restore;
            private readonly object[] saved;
            private readonly bool live = true;
            private readonly float startY;
            private readonly string why;

            // Per key: a key whose masters are off is snapshotted and written back (whatever the rest of the scope does).
            // The scope as a whole is greyed only when NO key in it is live: a scope that holds a sub-switch together with
            // that sub-switch's own dependents stays drawable while the sub-switch is off, so the player can turn it back on.
            public DependentScope(Listing_Standard list, SettingDependencies deps, Func<string, object> get,
                Action<string, object> set, string[] keys)
            {
                this.list = list;
                this.set = set;
                this.keys = keys ?? new string[0];
                saved = new object[this.keys.Length];
                restore = new bool[this.keys.Length];
                if (deps == null || this.keys.Length == 0) return;
                Func<string, bool> isOn = k => SettingsKitMasters.IsOn(get(k));
                bool greyed = SettingsKitMasters.ScopeGreyed(deps, this.keys, isOn, out restore, out List<string> off);
                for (int i = 0; i < this.keys.Length; i++) if (restore[i]) saved[i] = get(this.keys[i]);
                if (!greyed) return;
                live = false;
                why = "Greyed out: switch on " + string.Join(" and ", off.ConvertAll(m => "\"" + deps.NameOf(m) + "\"")) +
                      " to change these. Your values are kept.";
                startY = list.CurHeight;
                greyDepth++;
            }

            public void Dispose()
            {
                for (int i = 0; i < keys.Length; i++) if (restore[i]) set(keys[i], saved[i]);
                if (live || --greyDepth > 0) return;
                Rect r = new Rect(0f, startY, list.ColumnWidth, Mathf.Max(0f, list.CurHeight - startY));
                if (r.height <= 0f) return;
                Widgets.DrawBoxSolid(r, Shade);
                TooltipHandler.TipRegion(r, why);
            }
        }
    }
}
