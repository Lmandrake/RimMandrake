// FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING: the shared reset helper restores shipped values after they were changed,
// leaves consts, readonly and non-setting types alone, and every screen the item names wires it to a Reset button.
// NOT proven here: the button drawing or being clicked in the window (a live look).
using System;
using System.IO;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class SettingsResetChecks
    {
        private static class Fake
        {
            public static bool on = true;
            public static float rate = 1.5f;
            public static int count = 3;
            public static string label = "x";
            public const int Max = 9;
            public static readonly int Fixed = 4;
        }

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("SettingsReset_restores_shipped_values_and_skips_non_settings", () =>
            {
                var shipped = RM_SettingsReset.Snapshot(typeof(Fake));
                Assert(shipped.Count == 3, "bool, float and int only (no string, const or readonly): " + shipped.Count);
                Fake.on = false; Fake.rate = 9f; Fake.count = 0; Fake.label = "y";
                Assert(RM_SettingsReset.Reset(typeof(Fake), shipped, "rate", "nope") == 1, "one named field reset, the unknown name skipped");
                Assert(Fake.rate == 1.5f && !Fake.on && Fake.count == 0, "can-fail: only the named field moved back");
                Assert(RM_SettingsReset.ResetAll(typeof(Fake), shipped) == 3, "all three");
                Assert(Fake.on && Fake.rate == 1.5f && Fake.count == 3 && Fake.label == "y", "all restored; the string is not a snapshotted setting");
            });

            Case("SettingsReset_every_named_screen_has_a_reset_button", () =>
            {
                string[][] screens = {
                    new[] { "Machinery", "Kits", "RM_KitSettings.cs" }, new[] { "Quarry", "RM_QuarrySettings.cs" },
                    new[] { "Sprinklers", "RM_SprinklerSettings.cs" }, new[] { "Thirst", "RM_ThirstSettings.cs" },
                    new[] { "Pits", "Drawbridge", "RM_DrawbridgeSettings.cs" }, new[] { "Pits", "Suspension", "RM_SuspensionSettings.cs" },
                    new[] { "Superdeep", "RM_WallClimbSettings.cs" }, new[] { "Superdeep", "RM_RaiderTrench.cs" },
                    new[] { "Swimming", "RM_Swim.cs" }, new[] { "MapControls", "RM_MapControlSettings.cs" },
                    new[] { "Rivers", "RM_RiversSettings.cs" }, new[] { "RM_WaterBodyMendGame.cs" } };
                foreach (string[] s in screens)
                {
                    string src = RiverSwitchFlipChecks.Src(Path.Combine(s));
                    Assert(Regex.IsMatch(src, @"RM_SettingsReset\.Snapshot\(typeof\("), string.Join("/", s) + ": snapshots its shipped values");
                    Assert(Regex.IsMatch(src, @"SettingsKitDrawer\.ResetButton\(l(ist)?, "), string.Join("/", s) + ": draws the Reset button");
                }
            });
        }
    }
}
