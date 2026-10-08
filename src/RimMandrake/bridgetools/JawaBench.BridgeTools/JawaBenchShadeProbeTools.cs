// JawaBenchShadeProbeTools.cs - SOLAR_MIRRORS_BUILD_1 (design §6.2, RM_ShadeProbe).
//
// Read-only. One call reports the shade grid, the mirror light layer, the mirror
// field solver and per-cell light/shade/roof state, all by reflection so the file
// loads with CreatureBehaviors or SolarMirrors absent. Any member that cannot be
// found is listed under missingMembers - never thrown, never silently omitted.
//
// THREAD AFFINITY: reads MapComponent / ThingComp state - main thread only.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // Reads a public property OR field; records the miss and returns null when absent.
        private static object ProbeMember(object obj, string label, string name, List<string> missing)
        {
            if (obj == null) return null;
            const BindingFlags f = BindingFlags.Public | BindingFlags.Instance;
            Type t = obj.GetType();
            try
            {
                PropertyInfo p = t.GetProperty(name, f);
                if (p != null && p.GetIndexParameters().Length == 0) return p.GetValue(obj, null);
                FieldInfo fi = t.GetField(name, f);
                if (fi != null) return fi.GetValue(obj);
            }
            catch (Exception e)
            {
                missing.Add(label + "." + name + " (threw " + e.GetType().Name + ")");
                return null;
            }
            missing.Add(label + "." + name);
            return null;
        }

        private static float? ProbeFloatAt(object comp, string label, string method, IntVec3 c, List<string> missing, HashSet<string> reported)
        {
            if (comp == null) return null;
            MethodInfo m = comp.GetType().GetMethod(method, BindingFlags.Public | BindingFlags.Instance, null, new[] { typeof(IntVec3) }, null);
            if (m == null)
            {
                if (reported.Add(label + "." + method)) missing.Add(label + "." + method + "(IntVec3)");
                return null;
            }
            try { return Convert.ToSingle(m.Invoke(comp, new object[] { c })); }
            catch (Exception e)
            {
                if (reported.Add(label + "." + method)) missing.Add(label + "." + method + " (threw " + e.GetType().Name + ")");
                return null;
            }
        }

        private static List<string> ProbeDistinct(List<string> items)
        {
            var seen = new HashSet<string>();
            var o = new List<string>();
            foreach (string s in items) if (seen.Add(s)) o.Add(s);
            return o;
        }

        private static string ProbeCell(object v)
        {
            if (v is IntVec3 c) return c.IsValid ? c.x + "," + c.z : null;
            return v?.ToString();
        }

        [Tool(
            "jawa/shade_probe",
            Description = "READ-ONLY. One-call probe of the shade and mirror-light stack by reflection: " +
                "RM_MapComponent_ShadeGrid (CreatureBehaviors), RM_MapComponent_MirrorLight and " +
                "RM_MapComponent_MirrorField (SolarMirrors). Reports present flags, shade grid version and " +
                "patch count, per requested cell shade/exposure/gridLight/mirrorLight/groundGlow/roofed, every " +
                "mirror (target, aim, last fired/relayed/delivered, efficiency, source, blocker, dust, seized, " +
                "ancient, detent), every light receiver, mirror-layer totals and the field solver state. Cells " +
                "are 'x,z;x,z;...' (max 200); out-of-bounds cells report inBounds=false; unparseable tokens go " +
                "under badTokens. Mirrors are capped at 200 with a truncated flag. Any member that cannot be " +
                "found by reflection is listed under missingMembers (the source may not have it yet) - a null " +
                "value alongside a missingMembers entry means UNMEASURED, not zero.",
            ResultDescription = "success, present{shadeGrid,mirrorLight,mirrorField}, gridVersion, patchCount, " +
                "cells[{x,z,inBounds,shade,exposure,gridLight,mirrorLight,groundGlow,roofed}], mirrors[], " +
                "mirrorsTruncated, receivers[], mirrorLight{}, field{}, badTokens, missingMembers, ticksGame.")]
        public static async Task<object> ShadeProbe(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cells as 'x,z;x,z;...' (max 200). Empty reads only the map-level values.")] string cells = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null)
                {
                    return (object)new { success = true, present = false, reason = "no current map", ticksGame = TicksGameSafe() };
                }

                var missing = new List<string>();
                var reported = new HashSet<string>();

                Type gridType = FindTypeByFullName("RimMandrake.CreatureBehaviors.RM_MapComponent_ShadeGrid");
                Type lightType = FindTypeByFullName("RimMandrake.SolarMirrors.RM_MapComponent_MirrorLight");
                Type fieldType = FindTypeByFullName("RimMandrake.SolarMirrors.RM_MapComponent_MirrorField");
                object grid = gridType != null ? map.GetComponent(gridType) : null;
                object light = lightType != null ? map.GetComponent(lightType) : null;
                object field = fieldType != null ? map.GetComponent(fieldType) : null;

                var present = new { shadeGrid = grid != null, mirrorLight = light != null, mirrorField = field != null };
                if (gridType == null) missing.Add("type RimMandrake.CreatureBehaviors.RM_MapComponent_ShadeGrid");
                else if (grid == null) missing.Add("map component RM_MapComponent_ShadeGrid");
                if (lightType == null) missing.Add("type RimMandrake.SolarMirrors.RM_MapComponent_MirrorLight");
                else if (light == null) missing.Add("map component RM_MapComponent_MirrorLight");
                if (fieldType == null) missing.Add("type RimMandrake.SolarMirrors.RM_MapComponent_MirrorField");
                else if (field == null) missing.Add("map component RM_MapComponent_MirrorField");

                // Grid version and patch count.
                object gridVersion = ProbeMember(grid, "ShadeGrid", "GridVersion", missing);
                int? patchCount = null;
                if (grid != null)
                {
                    object graph = ProbeMember(grid, "ShadeGrid", "PatchGraph", missing);
                    if (graph != null)
                    {
                        object pc = ProbeMember(graph, "PatchGraph", "PatchCount", missing);
                        if (pc is int n) patchCount = n;
                        else
                        {
                            object list = ProbeMember(graph, "PatchGraph", "patches", missing);
                            if (list is ICollection col) patchCount = col.Count;
                        }
                    }
                }

                // Cells.
                var badTokens = new List<string>();
                var cellList = new List<object>();
                if (!string.IsNullOrWhiteSpace(cells))
                {
                    string[] tokens = cells.Split(new[] { ';' }, StringSplitOptions.RemoveEmptyEntries);
                    if (tokens.Length > 200)
                    {
                        return Fail($"Too many cells: {tokens.Length} > 200. Split the call.");
                    }
                    foreach (string raw in tokens)
                    {
                        string[] xz = raw.Trim().Split(',');
                        if (xz.Length != 2 || !int.TryParse(xz[0].Trim(), out int x) || !int.TryParse(xz[1].Trim(), out int z))
                        {
                            badTokens.Add(raw);
                            continue;
                        }
                        var c = new IntVec3(x, 0, z);
                        if (!c.InBounds(map))
                        {
                            cellList.Add(new { x, z, inBounds = false });
                            continue;
                        }
                        float? glow = null;
                        try { glow = map.glowGrid.GroundGlowAt(c, false, false); }
                        catch (Exception e) { if (reported.Add("glow")) missing.Add("glowGrid.GroundGlowAt (threw " + e.GetType().Name + ")"); }
                        cellList.Add(new
                        {
                            x,
                            z,
                            inBounds = true,
                            shade = ProbeFloatAt(grid, "ShadeGrid", "ShadeAt", c, missing, reported),
                            exposure = ProbeFloatAt(grid, "ShadeGrid", "ExposureAt", c, missing, reported),
                            gridLight = ProbeFloatAt(grid, "ShadeGrid", "LightAt", c, missing, reported),
                            mirrorLight = ProbeFloatAt(light, "MirrorLight", "LightAt", c, missing, reported),
                            groundGlow = glow,
                            roofed = map.roofGrid.Roofed(c)
                        });
                    }
                }

                // Mirrors.
                var mirrors = new List<object>();
                bool truncated = false;
                object mirrorsObj = ProbeMember(light, "MirrorLight", "Mirrors", missing);
                if (mirrorsObj is IEnumerable mEnum)
                {
                    foreach (object m in mEnum)
                    {
                        if (mirrors.Count >= 200) { truncated = true; break; }
                        ThingWithComps parent = (m as ThingComp)?.parent;
                        mirrors.Add(new
                        {
                            def = parent?.def?.defName,
                            pos = parent != null ? parent.Position.x + "," + parent.Position.z : null,
                            target = ProbeCell(ProbeMember(m, "Mirror", "Target", missing)),
                            hasAim = ProbeMember(m, "Mirror", "HasAim", missing),
                            hasPending = ProbeMember(m, "Mirror", "HasPending", missing),
                            lastFired = ProbeMember(m, "Mirror", "lastFired", missing),
                            lastRelayed = ProbeMember(m, "Mirror", "lastRelayed", missing),
                            lastDelivered = ProbeMember(m, "Mirror", "lastDelivered", missing),
                            lastEfficiency = ProbeMember(m, "Mirror", "lastEfficiency", missing),
                            lastSource = ProbeMember(m, "Mirror", "lastSource", missing)?.ToString(),
                            lastBlocker = ProbeMember(m, "Mirror", "lastBlocker", missing)?.ToString(),
                            dust = ProbeMember(m, "Mirror", "Dust", missing),
                            seized = ProbeMember(m, "Mirror", "Seized", missing),
                            isAncient = ProbeMember(m, "Mirror", "IsAncient", missing),
                            detentIndex = ProbeMember(m, "Mirror", "DetentIndex", missing)
                        });
                    }
                }

                // Receivers.
                var receivers = new List<object>();
                object recvObj = ProbeMember(light, "MirrorLight", "Receivers", missing);
                if (recvObj is IEnumerable rEnum)
                {
                    foreach (object r in rEnum)
                    {
                        if (receivers.Count >= 200) break;
                        ThingWithComps parent = (r as ThingComp)?.parent;
                        receivers.Add(new
                        {
                            def = parent?.def?.defName,
                            pos = parent != null ? parent.Position.x + "," + parent.Position.z : null,
                            lit = ProbeMember(r, "Receiver", "Lit", missing),
                            lastLight = ProbeMember(r, "Receiver", "LastLight", missing)
                        });
                    }
                }

                object lightSummary = light == null ? null : new
                {
                    mirrorCount = ProbeMember(light, "MirrorLight", "MirrorCount", missing),
                    anyLight = ProbeMember(light, "MirrorLight", "AnyLight", missing),
                    passCount = ProbeMember(light, "MirrorLight", "PassCount", missing),
                    lastChangeHash = ProbeMember(light, "MirrorLight", "LastChangeHash", missing)
                };

                object fieldSummary = field == null ? null : new
                {
                    hasField = ProbeMember(field, "MirrorField", "HasField", missing),
                    latched = ProbeMember(field, "MirrorField", "Latched", missing),
                    currentlySolved = ProbeMember(field, "MirrorField", "CurrentlySolved", missing),
                    solverReport = ProbeMember(field, "MirrorField", "SolverReport", missing)?.ToString(),
                    solutionCount = ProbeMember(field, "MirrorField", "SolutionCount", missing),
                    minReAims = ProbeMember(field, "MirrorField", "MinReAims", missing),
                    configurations = ProbeMember(field, "MirrorField", "Configurations", missing)
                };

                return (object)new
                {
                    success = true,
                    present,
                    gridVersion,
                    patchCount,
                    cells = cellList,
                    mirrors,
                    mirrorsTruncated = truncated,
                    receivers,
                    mirrorLight = lightSummary,
                    field = fieldSummary,
                    badTokens,
                    // one entry per missing member, not one per mirror/receiver that lacked it
                    missingMembers = ProbeDistinct(missing),
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
