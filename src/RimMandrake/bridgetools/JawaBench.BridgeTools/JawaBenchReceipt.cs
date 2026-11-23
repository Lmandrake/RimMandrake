// JawaBenchReceipt.cs - what this process has LOADED, for jawa/running_mods loadedOf=... (the Verse half).
// Page: design/specs/2026-11-23-loaded-receipt/boundary.md. Engine facts read from decompiled 1.6 (RimSage, 2026-11-23):
// ModAssemblyHandler.ReloadAll loads each DLL of "Assemblies/" with Assembly.LoadFrom and keeps it in loadedAssemblies;
// a second file of one identity returns the FIRST assembly (its Location is another mod's folder).
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using RimWorld;
using UnityEngine;
using Verse;
using R = JawaBench.BridgeTools.JawaBenchReceiptCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchReceipt
    {
        internal const string OursPrefix = "mandrake.";

        /// <summary>loadedOf: "ours" (every packageId that starts with mandrake.), or a comma list of exact packageIds.</summary>
        internal static object Build(string loadedOf, List<ModContentPack> all)
        {
            var wanted = loadedOf.Split(',').Select(s => R.NormId(s)).Where(s => s.Length > 0).ToList();
            bool ours = wanted.Contains("ours");
            var picked = all.Where(m => (ours && R.NormId(m.PackageId).StartsWith(OursPrefix, StringComparison.Ordinal))
                                        || wanted.Contains(R.NormId(m.PackageId))).ToList();
            var missing = wanted.Where(w => w != "ours" && !all.Any(m => R.NormId(m.PackageId) == w)).ToList();
            DateTime? started = null;
            try { using (var p = Process.GetCurrentProcess()) started = p.StartTime.ToUniversalTime(); } catch { }

            var mods = picked.Select(m => ModRow(m, started)).ToList();
            string install = null; try { install = Path.GetDirectoryName(Application.dataPath); } catch { }
            string data = null; try { data = GenFilePaths.SaveDataFolderPath; } catch { }
            string machine = null; try { machine = Environment.MachineName; } catch { }
            string version = null; try { version = VersionControl.CurrentVersionStringWithRev; } catch { }
            var self = typeof(JawaBenchReceipt).Assembly;
            string srcHash = null;
            try
            {
                srcHash = self.GetCustomAttributes(typeof(AssemblyMetadataAttribute), false).Cast<AssemblyMetadataAttribute>()
                              .FirstOrDefault(a => a.Key == "JawaBenchSrcHash")?.Value;
            }
            catch { }
            int pid = -1; try { using (var p = Process.GetCurrentProcess()) pid = p.Id; } catch { }
            return new
            {
                schema = "loaded_receipt/1",
                utc = DateTime.UtcNow.ToString("o"),
                gameKey = R.GameKey(machine, data, install),
                machine, installFolder = install, dataFolder = data, pid,
                processStartedUtc = started?.ToString("o"),
                gameVersion = version,
                listFingerprint = R.Fingerprint(all.Select(m => m.PackageId)),
                listCount = all.Count,
                companion = new { mvid = Mvid(self), srcHash, version = self.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion },
                mods,
                notRunning = missing,
                notCovered = "code only: Defs, patches, textures and asset bundles are not identified",
            };
        }

        private static string Mvid(Assembly a) { try { return a.ManifestModule.ModuleVersionId.ToString(); } catch { return null; } }

        private static object ModRow(ModContentPack m, DateTime? started)
        {
            string readError = null;
            List<string> files = null;
            List<Assembly> asms = null;
            try
            {
                files = ModContentPack.GetAllFilesForModPreserveOrder(m, "Assemblies/", e => e.ToLower() == ".dll").Select(t => t.Item2.FullName).ToList();
                asms = m.assemblies == null ? new List<Assembly>() : m.assemblies.loadedAssemblies.ToList();
            }
            catch (Exception e) { readError = e.GetType().Name + ": " + e.Message; }

            var facts = new List<R.AsmFact>();
            var rows = new List<object>();
            foreach (var a in asms ?? new List<Assembly>())
            {
                string loc = null; try { loc = a.Location; } catch { }
                string mvid = Mvid(a), sha = null, err = null, written = null;
                long bytes = -1; bool? holds = null; bool? afterStart = null;
                try
                {
                    if (!string.IsNullOrEmpty(loc))
                    {
                        var raw = File.ReadAllBytes(loc);
                        bytes = raw.Length;
                        using (var h = SHA256.Create()) sha = R.Hex(h.ComputeHash(raw));
                        Guid g;
                        holds = Guid.TryParse(mvid, out g) ? R.HoldsMvid(raw, g) : null;
                        var w = File.GetLastWriteTimeUtc(loc);
                        written = w.ToString("o");
                        if (started.HasValue) afterStart = w > started.Value;
                    }
                }
                catch (Exception e) { err = e.GetType().Name + ": " + e.Message; holds = null; }
                string name; try { name = a.GetName().Name; } catch { name = "?"; }
                string ver = null; try { ver = a.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion; } catch { }
                facts.Add(new R.AsmFact { Name = name, Location = loc, FileHoldsLoaded = holds });
                rows.Add(new { name, location = loc, mvid, informationalVersion = ver, fileHoldsLoadedCode = holds, fileSha256 = sha, fileBytes = bytes,
                               fileWrittenUtc = written, fileWrittenAfterProcessStart = afterStart, fileError = err });
            }
            string why;
            string state = R.JudgeMod(m.RootDir, files, asms == null ? null : facts, out why);
            return new { packageId = m.PackageId, name = m.Name, loadOrder = m.loadOrder, folder = m.RootDir, state, why = readError ?? why,
                         dllFiles = files, assemblies = rows };
        }
    }
}
