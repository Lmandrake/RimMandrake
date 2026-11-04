// stevetemp.cs - CPU temperature sampler for SteveDesktop's fault watch (STEVE_HEAT_MEASURE_BEFORE_THE_SCREWDRIVER).
// Built ON Steve by `fault_monitor.py deploy-heat` with .NET Framework's csc (C# 5: no interpolation, no ?.), beside
// LibreHardwareMonitorLib.dll, which reads the Intel digital thermal sensors through the PawnIO driver. The ACPI thermal
// zone on that board reads a constant 27.85 C, so it is not a CPU temperature.
//
//   stevetemp <max_seconds> <interval_ms> [stop_file]
// samples every interval until max_seconds pass or stop_file exists, then prints ONE line that watch2.ps1 appends to its
// CYCLE line, and fault_monitor.HEAT_RE parses:
//   pkg_c=<first>/<max> core_max_c=<max> hot_core=<n> cores_max_c=[<c1>,<c2>,...] samples=<n> vcore_v=<max>
// or heat=UNMEASURED(<reason>) with a non-zero exit. Core numbers are LibreHardwareMonitor's physical "CPU Core #n",
// 1-based (measured on Steve 2026-11-04: 9 of them under numproc 18). vcore_v (the "CPU Core" voltage's max) is extra
// cause evidence for a SIMD fault; it is left out when the board does not report it.
//   stevetemp list    every CPU sensor LibreHardwareMonitor sees, one per line (the diagnosis when the sampler is blind).
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Threading;
using LibreHardwareMonitor.Hardware;

class SteveTemp
{
    static readonly CultureInfo CI = CultureInfo.InvariantCulture;

    static int List()
    {
        Console.WriteLine("pawnio installed=" + LibreHardwareMonitor.PawnIo.PawnIo.IsInstalled + " version=" + LibreHardwareMonitor.PawnIo.PawnIo.Version);
        var c = new Computer();
        c.IsCpuEnabled = true;
        c.Open();
        try
        {
            foreach (IHardware hw in c.Hardware)
            {
                hw.Update();
                Console.WriteLine("HW " + hw.HardwareType + " " + hw.Name);
                foreach (ISensor s in hw.Sensors)
                    Console.WriteLine("  " + s.SensorType + " '" + s.Name + "' " + (s.Value.HasValue ? s.Value.Value.ToString(CI) : "null"));
            }
        }
        finally { c.Close(); }
        return 0;
    }

    static int Main(string[] a)
    {
        if (a.Length > 0 && a[0] == "list") return List();
        double secs = a.Length > 0 ? double.Parse(a[0], CI) : 0;
        int iv = a.Length > 1 ? int.Parse(a[1], CI) : 500;
        string stop = a.Length > 2 ? a[2] : null;
        Computer c = null;
        try
        {
            if (!LibreHardwareMonitor.PawnIo.PawnIo.IsInstalled)
            {
                Console.WriteLine("heat=UNMEASURED(pawnio_not_installed)");
                return 2;
            }
            c = new Computer();
            c.IsCpuEnabled = true;
            c.Open();
            double pkgFirst = double.NaN, pkgMax = double.NaN, vcore = double.NaN;
            var cores = new SortedDictionary<int, double>();
            int samples = 0;
            DateTime end = DateTime.UtcNow.AddSeconds(secs);
            while (true)
            {
                bool any = false;
                foreach (IHardware hw in c.Hardware)
                {
                    if (hw.HardwareType != HardwareType.Cpu) continue;
                    hw.Update();
                    foreach (ISensor s in hw.Sensors)
                    {
                        if (!s.Value.HasValue) continue;
                        double v = s.Value.Value;
                        if (s.SensorType == SensorType.Voltage && s.Name == "CPU Core" && v > 0 && v < 2.5)
                        {
                            if (double.IsNaN(vcore) || v > vcore) vcore = v;
                            continue;
                        }
                        if (s.SensorType != SensorType.Temperature) continue;
                        if (double.IsNaN(v) || v <= 0 || v > 150) continue;
                        if (s.Name == "CPU Package")
                        {
                            if (double.IsNaN(pkgFirst)) pkgFirst = v;
                            if (double.IsNaN(pkgMax) || v > pkgMax) pkgMax = v;
                            any = true;
                        }
                        else if (s.Name.StartsWith("CPU Core #", StringComparison.Ordinal) && s.Name.IndexOf("Distance", StringComparison.Ordinal) < 0)
                        {
                            int n;
                            if (!int.TryParse(s.Name.Substring(10).Trim(), NumberStyles.Integer, CI, out n)) continue;
                            double old;
                            if (!cores.TryGetValue(n, out old) || v > old) cores[n] = v;
                            any = true;
                        }
                    }
                }
                if (any) samples++;
                if (DateTime.UtcNow >= end || (stop != null && File.Exists(stop))) break;
                Thread.Sleep(iv);
            }
            if (samples == 0 || cores.Count == 0 || double.IsNaN(pkgMax))
            {
                Console.WriteLine("heat=UNMEASURED(no_cpu_temperature_sensor)");
                return 3;
            }
            double coreMax = double.NaN;
            int hot = -1;
            var parts = new List<string>();
            foreach (var kv in cores)
            {
                parts.Add(Math.Round(kv.Value).ToString(CI));
                if (double.IsNaN(coreMax) || kv.Value > coreMax) { coreMax = kv.Value; hot = kv.Key; }
            }
            Console.WriteLine(string.Format(CI, "pkg_c={0:0}/{1:0} core_max_c={2:0} hot_core={3} cores_max_c=[{4}] samples={5}",
                pkgFirst, pkgMax, coreMax, hot, string.Join(",", parts.ToArray()), samples)
                + (double.IsNaN(vcore) ? "" : string.Format(CI, " vcore_v={0:0.000}", vcore)));
            return 0;
        }
        catch (Exception e)
        {
            string m = (e.GetType().Name + ":" + e.Message).Replace(")", "]").Replace("(", "[").Replace("\r", " ").Replace("\n", " ");
            Console.WriteLine("heat=UNMEASURED(" + (m.Length > 120 ? m.Substring(0, 120) : m) + ")");
            return 4;
        }
        finally
        {
            if (c != null) { try { c.Close(); } catch (Exception) { } }
        }
    }
}
