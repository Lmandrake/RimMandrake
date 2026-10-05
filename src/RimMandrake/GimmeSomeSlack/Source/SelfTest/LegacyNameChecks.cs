// GIMMESOMESLACK_RENAME_1 (2026-10-05): the Messy Conduit -> Gimme Some Slack rename keeps old saves and old settings.
// Load-bearing: saved Class names map to the renamed types, settings files are carried over once to Verse's new file
// names (Mod_<folder>_<Mod class>.xml) with their Class attribute rewritten, an existing new file is never overwritten,
// and the old file is never deleted.
using System;
using System.IO;
using RimMandrake.GimmeSomeSlack.Core;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class LegacyNameChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "legacy-name: " + msg);

        internal static void Run()
        {
            Check(LegacyName.MapTypeName("RimMandrake.MessyConduit.RM_MapComponent_CordGraph") == "RimMandrake.GimmeSomeSlack.RM_MapComponent_CordGraph",
                  "a saved map component name maps into the new namespace");
            Check(LegacyName.MapTypeName("RimMandrake.MessyConduit.Hose.Jobs.JobDriver_CarryHoseEnd") == "RimMandrake.GimmeSomeSlack.Hose.Jobs.JobDriver_CarryHoseEnd",
                  "a nested-namespace job driver keeps its sub-namespace");
            Check(LegacyName.MapTypeName("RimMandrake.MessyConduit.MessyConduitSettings") == "RimMandrake.GimmeSomeSlack.GimmeSomeSlackSettings",
                  "a renamed type maps to its new short name");
            Check(LegacyName.MapTypeName("RimMandrake.MessyConduitX.Foo") == null && LegacyName.MapTypeName("Verse.Map") == null
                  && LegacyName.MapTypeName(null) == null && LegacyName.MapTypeName("RimMandrake.GimmeSomeSlack.RM_MapComponent_Hoses") == null,
                  "names that are not ours-and-old are left alone");

            string old = "﻿<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<SettingsBlock>\n\t<ModSettings Class=\"RimMandrake.MessyConduit.MessyConduitSettings\">\n\t\t<slack>1.5</slack>\n\t</ModSettings>\n</SettingsBlock>";
            string mig = LegacyName.MigrateSettingsText(old);
            Check(mig.Contains("Class=\"RimMandrake.GimmeSomeSlack.GimmeSomeSlackSettings\"") && mig.Contains("<slack>1.5</slack>")
                  && !mig.Contains("MessyConduit"), "settings text: Class rewritten, values kept");

            string dir = Path.Combine(Path.GetTempPath(), "gss_legacy_" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(dir);
            try
            {
                File.WriteAllText(Path.Combine(dir, "Mod_MessyConduit_MessyConduitMod.xml"), old);
                File.WriteAllText(Path.Combine(dir, "Mod_MessyConduit_AerialLinesMod.xml"),
                    "<SettingsBlock><ModSettings Class=\"RimMandrake.MessyConduit.Aerial.AerialSettings\"><x>7</x></ModSettings></SettingsBlock>");
                string keep = "<SettingsBlock><ModSettings Class=\"RimMandrake.GimmeSomeSlack.Hose.HoseSettings\"><y>NEW</y></ModSettings></SettingsBlock>";
                File.WriteAllText(Path.Combine(dir, "Mod_MessyConduit_FireHosesMod.xml"), "<SettingsBlock><y>OLD</y></SettingsBlock>");
                File.WriteAllText(Path.Combine(dir, "Mod_GimmeSomeSlack_FireHosesMod.xml"), keep);

                var w = LegacyName.MigrateSettingsFiles(dir, "GimmeSomeSlack");
                Check(w.Count == 2, $"two files carried over (got {w.Count})");
                string main = File.ReadAllText(Path.Combine(dir, "Mod_GimmeSomeSlack_GimmeSomeSlackMod.xml"));
                Check(main.Contains("GimmeSomeSlackSettings") && main.Contains("<slack>1.5</slack>"), "main settings landed under the new Mod class name");
                Check(File.ReadAllText(Path.Combine(dir, "Mod_GimmeSomeSlack_AerialLinesMod.xml")).Contains("RimMandrake.GimmeSomeSlack.Aerial.AerialSettings"),
                      "aerial settings landed with the Class rewritten");
                Check(File.ReadAllText(Path.Combine(dir, "Mod_GimmeSomeSlack_FireHosesMod.xml")) == keep, "an existing new file is never overwritten");
                Check(File.Exists(Path.Combine(dir, "Mod_MessyConduit_MessyConduitMod.xml")), "the old file stays (rollback)");
                Check(LegacyName.MigrateSettingsFiles(dir, "GimmeSomeSlack").Count == 0, "a second run writes nothing");
                Check(LegacyName.MigrateSettingsFiles(dir, "MessyConduit").Count == 0, "an old-folder deploy migrates nothing onto itself");
            }
            finally { Directory.Delete(dir, true); }
        }
    }
}
