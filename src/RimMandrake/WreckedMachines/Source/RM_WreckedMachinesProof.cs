// The proof type (DESIGN.md "The proof type"; the contract is written above the scenes in validation.py). Every method is static,
// takes string arguments only and returns text, one entry a line. It only reads: it changes nothing in the game.
// A thing argument is the thing's id text; the thing is found by the number at its end, so an id read before a repair still names
// the machine after it (the swap keeps the thing id number).
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using PipeSystem;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.WreckedMachines
{
    public static class RM_WreckedMachinesProof
    {
        private const string NotBuilt = "REFUSED not built yet";

        private static string B(bool b) => b ? "true" : "false";

        private static string F(float f) => f.ToString("0.#####", CultureInfo.InvariantCulture);

        private static string N(Def d) => d != null ? d.defName : "none";

        public static string Loaded()
        {
            Version v = typeof(RM_WreckedMachinesProof).Assembly.GetName().Version;
            return "LOADED version " + v.Major + "." + v.Minor + "." + Math.Max(0, v.Build) + " | lines " + RM_MachineLines.All.Count;
        }

        public static string Machines()
        {
            var sb = new StringBuilder();
            foreach (RM_MachineLineDef l in RM_MachineLines.All)
                sb.Append("MACHINE ").Append(l.key).Append(" | on ").Append(B(RM_MachineLines.IsOn(l)))
                  .Append(" | wrecked ").Append(N(l.wrecked)).Append(" | kludged ").Append(N(l.kludged))
                  .Append(" | refurbished ").Append(N(l.refurbished)).Append(" | original ").Append(N(l.original)).Append('\n');
            return sb.ToString().TrimEnd('\n');
        }

        public static string Settings()
        {
            var sb = new StringBuilder();
            foreach (FieldInfo f in typeof(WreckedMachinesSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
            {
                if (f.IsLiteral || f.IsInitOnly) continue;
                sb.Append("SETTING ").Append(f.Name).Append(" | value ").Append(WreckedMachinesSettings.ValueText(f.Name, f.GetValue(null)))
                  .Append(" | shipped ").Append(WreckedMachinesSettings.ShippedText(f.Name)).Append('\n');
            }
            return sb.ToString().TrimEnd('\n');
        }

        public static string Projects()
        {
            var sb = new StringBuilder();
            foreach (RM_MachineLineDef l in RM_MachineLines.All)
                for (int step = 1; step <= 2; step++)
                {
                    ResearchProjectDef p = RM_MachineLines.ProjectFor(l, step);
                    if (p != null) sb.Append("PROJECT ").Append(p.defName).Append(" | line ").Append(l.key).Append(" | step ").Append(step).Append('\n');
                }
            return sb.ToString().TrimEnd('\n');
        }

        /// <summary>The thing whose id number is the digits at the end of `id`: spawned on any map, or inside a minified thing.</summary>
        public static Thing FindThing(string id)
        {
            if (string.IsNullOrEmpty(id) || Find.Maps == null) return null;
            int end = id.Length;
            while (end > 0 && char.IsWhiteSpace(id[end - 1])) end--;
            int start = end;
            while (start > 0 && char.IsDigit(id[start - 1])) start--;
            if (start == end || !int.TryParse(id.Substring(start, end - start), NumberStyles.Integer, CultureInfo.InvariantCulture, out int n))
                return null;
            foreach (Map m in Find.Maps)
                foreach (Thing t in m.listerThings.AllThings)
                {
                    if (t.thingIDNumber == n) return t;
                    if (t is MinifiedThing mt && mt.InnerThing != null && mt.InnerThing.thingIDNumber == n) return mt.InnerThing;
                }
            return null;
        }

        public static string Level(string id)
        {
            Thing t = FindThing(id);
            if (t == null) return "LEVEL none | line none | def none";
            RM_MachineLineDef l = RM_MachineLines.LineOf(t.def, out int level);
            string name = l != null && level >= RM_WreckedMachinesKernel.Wrecked && level <= RM_WreckedMachinesKernel.Refurbished
                ? RM_WreckedMachinesRepair.LevelName(level) : "none";
            return "LEVEL " + name + " | line " + (l != null ? l.key : "none") + " | def " + t.def.defName;
        }

        public static string Repair(string id)
        {
            CompWreckedMachine c = FindThing(id)?.TryGetComp<CompWreckedMachine>();
            return RM_WreckedMachinesRepair.ProofLine(c?.rec);
        }

        public static string SignalLog()
        {
            return string.Join("\n", RM_LevelLog.Lines);
        }

        public static string Placement() => NotBuilt;

        public static string InRuinRoom(string xz) => NotBuilt;

        public static string PlantLighterWrecked(string line) => NotBuilt;

        /// <summary>The applied work speed of a machine against its Original (1). A machine our speed postfix has seen answers the
        /// factor it applied; one it has not seen answers the ratio of its level; anything else answers 1.</summary>
        public static string Speed(string id)
        {
            Thing t = FindThing(id);
            if (t == null) return "SPEED 1";
            return "SPEED " + F(RM_ProcessLists.SpeedFactor(t));
        }

        public static string Onboarding(string line)
        {
            RM_MachineLineDef l = RM_MachineLines.ByKey(line?.Trim());
            if (l == null) return "ROW " + (line ?? "") + " | kludged  | refurbished ";
            RM_ProcessLists.Row(l, out List<string> k, out List<string> r);
            return "ROW " + l.key + " | kludged " + string.Join(",", k) + " | refurbished " + string.Join(",", r);
        }

        /// <summary>What each repair of a line costs now, after the cost sliders: "COST line | step 1|2 | materials def:n,... | work n".
        /// The rows that validation.py's materialCostFactor drive reads.</summary>
        public static string Costs(string line)
        {
            RM_MachineLineDef l = RM_MachineLines.ByKey(line?.Trim());
            if (l == null) return "REFUSED no machine line " + (line ?? "");
            var sb = new StringBuilder();
            for (int step = 1; step <= 2; step++)
                sb.Append("COST ").Append(l.key).Append(" | step ").Append(step).Append(" | materials ")
                  .Append(string.Join(",", RM_MachineLines.StepCost(l, step).Select(c => c.thingDef.defName + ":" + c.count)))
                  .Append(" | work ").Append(F(RM_MachineLines.StepWork(l, step))).Append('\n');
            return sb.ToString().TrimEnd('\n');
        }

        public static string LineLabels()
        {
            return string.Join("\n", RM_MachineLines.All.Select(l => "LABEL " + l.key + " | label " + WreckedMachinesSettings.LineLabel(l)));
        }

        /// <summary>For each level def: the MD5 of the texture file the game loads for it from this mod (the first of the path's
        /// single, south and north files that exists), else a hash of the loaded texture's name and size.</summary>
        public static string TextureIds()
        {
            ModContentPack mod = LoadedModManager.RunningModsListForReading
                .FirstOrDefault(m => m.assemblies != null && m.assemblies.loadedAssemblies.Contains(typeof(RM_WreckedMachinesProof).Assembly));
            var sb = new StringBuilder();
            foreach (RM_MachineLineDef l in RM_MachineLines.All)
                foreach (ThingDef d in new[] { l.wrecked, l.kludged, l.refurbished })
                {
                    if (d == null) continue;
                    sb.Append("TEX ").Append(d.defName).Append(" | hash ").Append(TexHash(mod, d)).Append('\n');
                }
            return sb.ToString().TrimEnd('\n');
        }

        private static string TexHash(ModContentPack mod, ThingDef d)
        {
            string path = d.graphicData?.texPath;
            if (path.NullOrEmpty()) return "none";
            if (mod?.foldersToLoadDescendingOrder != null)
                foreach (string folder in mod.foldersToLoadDescendingOrder)
                    foreach (string suffix in new[] { "", "_south", "_north" })
                    {
                        string file = Path.Combine(Path.Combine(folder, "Textures"), path + suffix + ".png");
                        if (!File.Exists(file)) continue;
                        using (MD5 md5 = MD5.Create())
                            return BitConverter.ToString(md5.ComputeHash(File.ReadAllBytes(file))).Replace("-", "").ToLowerInvariant();
                    }
            Texture tex = d.graphic?.MatSingle?.mainTexture;
            if (tex == null) return "none";
            using (MD5 md5 = MD5.Create())
                return "loaded-" + BitConverter.ToString(md5.ComputeHash(Encoding.UTF8.GetBytes(tex.name + ":" + tex.width + "x" + tex.height)))
                    .Replace("-", "").ToLowerInvariant();
        }
    }
}
