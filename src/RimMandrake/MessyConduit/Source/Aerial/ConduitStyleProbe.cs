using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using HarmonyLib;
using RimMandrake.MessyConduit.Core;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>
    /// Stage-2 probe verbs (AerialProbe channel; read by validation_style.py S9/S10). Placement goes through the REAL Architect
    /// designator with the key picked by ConduitStylePicker.Pick (the menu option's own call); only the click is skipped.
    ///   cstyles[:x,z,w,h]            every run member in the rect (stored style, look, colour, run id / area), every cord piece
    ///                                owned in the rect (material index, look, strand texture, legacy flag and whether a legacy
    ///                                piece chose the SAME Material objects as the pre-stage-2 default-look set), and the
    ///                                textures the rect's RM_MessyCords section meshes actually hold
    ///   cplace:def:key:x,z:god|build | cline:def:key:x0,z0:x1,z1:god|build | cfinishbuild | cprocess | cclearpicks
    ///   crestyle:x,z:key             the gizmo's own call | cdeconstruct:x,z   a member destroyed as by deconstruction
    /// </summary>
    public static class ConduitStyleProbe
    {
        private static string S(string s) => AerialProbe.S(s);
        private static string B(bool b) => AerialProbe.B(b);

        private static IntVec3 Cell(string xz)
        {
            string[] p = xz.Split(',');
            return new IntVec3(int.Parse(p[0], CultureInfo.InvariantCulture), 0, int.Parse(p[1], CultureInfo.InvariantCulture));
        }

        public static string Run(Map map, string cmd)
        {
            RM_MapComponent_ConduitRuns runs = map.GetComponent<RM_MapComponent_ConduitRuns>();
            if (cmd == "cprocess") { int n = runs.PendingCount; runs.ProcessPending(); return AerialProbe.Ok(cmd, "\"processed\":" + n); }
            if (cmd == "cclearpicks") { ConduitStylePicker.ClearPicks(); return AerialProbe.Ok(cmd, ""); }
            if (cmd == "cfinishbuild") return FinishBuild(map);
            if (cmd == "cstyles" || cmd.StartsWith("cstyles:")) return Styles(map, runs, cmd);
            if (cmd.StartsWith("cplace:")) return Place(map, cmd);
            if (cmd.StartsWith("cline:")) return Line(map, cmd);
            if (cmd.StartsWith("crestyle:"))
            {
                string[] p = cmd.Substring(9).Split(':');
                Thing t = Cell(p[0]).GetThingList(map).FirstOrDefault(x => ConduitStylePicker.IsMember(x.def));
                if (t == null) return AerialProbe.Fail(cmd, "no run member there");
                int n = runs.RestyleRun(t, p[1], false);
                return AerialProbe.Ok(cmd, "\"changed\":" + n + ",\"message\":" + S(runs.lastMessage));
            }
            if (cmd.StartsWith("cdeconstruct:"))
            {
                Thing t = Cell(cmd.Substring(13)).GetThingList(map).FirstOrDefault(x => ConduitStylePicker.IsMember(x.def));
                if (t == null) return AerialProbe.Fail(cmd, "no run member there");
                t.Destroy(DestroyMode.Deconstruct);
                return AerialProbe.Ok(cmd, "\"destroyed\":" + S(t.def.defName));
            }
            return null;
        }

        private static string Place(Map map, string cmd)
        {
            string[] p = cmd.Substring(7).Split(':');
            if (p.Length < 4) return AerialProbe.Fail(cmd, "want def:key:x,z:god|build");
            return PlaceOne(map, p[0], p[1], Cell(p[2]), p[3] == "god", cmd);
        }

        private static string Line(Map map, string cmd)
        {
            string[] p = cmd.Substring(6).Split(':');
            if (p.Length < 5) return AerialProbe.Fail(cmd, "want def:key:x0,z0:x1,z1:god|build");
            IntVec3 a = Cell(p[2]), b = Cell(p[3]);
            var res = new List<string>();
            int dx = Math.Sign(b.x - a.x), dz = Math.Sign(b.z - a.z), n = Math.Max(Math.Abs(b.x - a.x), Math.Abs(b.z - a.z));
            for (int i = 0; i <= n; i++) res.Add(PlaceOne(map, p[0], p[1], new IntVec3(a.x + dx * i, 0, a.z + dz * i), p[4] == "god", cmd));
            bool ok = res.All(r => r.StartsWith("{\"success\":true"));
            return (ok ? AerialProbe.Ok(cmd, "\"cells\":" + res.Count) : AerialProbe.Fail(cmd, "some cells failed")).TrimEnd('}') + ",\"each\":[" + string.Join(",", res) + "]}";
        }

        private static string PlaceOne(Map map, string defName, string key, IntVec3 c, bool god, string cmd)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (!ConduitStylePicker.IsOurs(d)) return AerialProbe.Fail(cmd, "not a stage-2 styled def: " + defName);
            Designator_Build des = BuildCopyCommandUtility.FindAllowedDesignator(d, mustBeVisible: false);
            if (des == null) return AerialProbe.Fail(cmd, "no Architect designator for " + defName);
            if (key != "-" && !ConduitStylePicker.Pick(des, key)) return AerialProbe.Fail(cmd, "not a menu key: " + key);
            bool was = DebugSettings.godMode;
            try
            {
                DebugSettings.godMode = god;
                AcceptanceReport ok = des.CanDesignateCell(c);
                if (!ok.Accepted) return AerialProbe.Fail(cmd, "CanDesignateCell refused at " + c + ": " + ok.Reason);
                var before = new HashSet<Thing>(c.GetThingList(map));
                des.DesignateSingleCell(c);
                Thing made = c.GetThingList(map).FirstOrDefault(t => !before.Contains(t) && (t.def == d || t.def.entityDefToBuild == d));
                return AerialProbe.Ok(cmd, "\"x\":" + c.x + ",\"z\":" + c.z + ",\"made\":" + S(made == null ? null : made is Blueprint ? "blueprint" : made.def == d ? "building" : made.GetType().Name) +
                                            ",\"rawStyle\":" + S(StylePicker.RawStyle(made)?.defName));
            }
            finally { DebugSettings.godMode = was; }
        }

        private static string FinishBuild(Map map)
        {
            Pawn w = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (w == null) return AerialProbe.Fail("cfinishbuild", "no free colonist on the map");
            int built = 0;
            var errors = new List<string>();
            foreach (Blueprint bp in map.listerThings.AllThings.OfType<Blueprint>().Where(b => ConduitStylePicker.IsOurs(b.def.entityDefToBuild as ThingDef)).ToList())
            {
                try { if (!bp.TryReplaceWithSolidThing(w, out _, out _)) errors.Add("blueprint " + bp.thingIDNumber + " blocked"); }
                catch (Exception ex) { errors.Add("blueprint " + bp.thingIDNumber + ": " + ex.Message); }
            }
            foreach (Frame f in map.listerThings.AllThings.OfType<Frame>().Where(fr => ConduitStylePicker.IsOurs(fr.def.entityDefToBuild as ThingDef)).ToList())
            {
                try { f.CompleteConstruction(w); built++; }
                catch (Exception ex) { errors.Add("frame " + f.thingIDNumber + ": " + ex.Message); }
            }
            return AerialProbe.Ok("cfinishbuild", "\"workerHasIdeo\":" + B(w.Ideo != null) + ",\"built\":" + built + ",\"errors\":[" + string.Join(",", errors.Select(S)) + "]");
        }

        private static string TexName(Material m) => m == null ? null : m.mainTexture == null ? "<none>" : m.mainTexture.name;

        private static string Styles(Map map, RM_MapComponent_ConduitRuns runs, string cmd)
        {
            CellRect rect = CellRect.WholeMap(map);
            if (cmd.StartsWith("cstyles:"))
            {
                int[] r = cmd.Substring(8).Split(',').Select(x => int.Parse(x, CultureInfo.InvariantCulture)).ToArray();
                rect = new CellRect(r[0], r[1], r[2], r[3]).ClipInsideMap(map);
            }
            runs.ProcessPending();
            RM_MapComponent_CordGraph cg = map.GetComponent<RM_MapComponent_CordGraph>();
            cg.Rebuild();
            // ---- members and their runs
            var members = new List<Thing>();
            foreach (ThingDef d in ConduitStylePicker.MemberDefs)
                foreach (Thing t in map.listerThings.ThingsOfDef(d)) if (rect.Contains(t.Position)) members.Add(t);
            members.Sort((a, b) => a.thingIDNumber.CompareTo(b.thingIDNumber));
            var runOf = new Dictionary<Thing, int>();
            var runArea = new Dictionary<int, int>();
            foreach (Thing t in members)
            {
                if (runOf.ContainsKey(t)) continue;
                List<Thing> run = runs.RunOf(t);
                int id = run[0].thingIDNumber;
                ConduitStyles.Run info = RM_MapComponent_ConduitRuns.Info(run);
                runArea[id] = info.Area;
                foreach (Thing m in run) runOf[m] = id;
            }
            var rows = members.Select(t =>
            {
                string look = ConduitStylePicker.LookOf(StylePicker.RawStyle(t), out string colour);
                string drawn = null;
                if (t is Building_PowerSwitch) { try { drawn = TexName(t.Graphic?.MatSingle); } catch (Exception ex) { drawn = "ERR " + ex.GetType().Name; } }
                return "{\"id\":" + t.thingIDNumber + ",\"def\":" + S(t.def.defName) + ",\"x\":" + t.Position.x + ",\"z\":" + t.Position.z +
                       ",\"rawStyle\":" + S(StylePicker.RawStyle(t)?.defName) + ",\"look\":" + S(look) + ",\"colour\":" + S(colour) +
                       ",\"run\":" + runOf[t] + ",\"runArea\":" + runArea[runOf[t]] + (drawn != null ? ",\"drawnTex\":" + S(drawn) : "") + "}";
            }).ToList();
            // ---- pieces owned in the rect
            var pieces = new List<string>();
            int legacy = 0, legacySame = 0;
            foreach (LaidPiece p in cg.Pieces)
            {
                if (!rect.Contains(new IntVec3(p.Owner.X, 0, p.Owner.Z))) continue;
                int g = cg.MatIndexOf(p), v = cg.VariantOf(p);
                ConduitStyles.FromGlobal(g, out string look, out int variant);
                bool leg = cg.IsLegacy(p);
                bool same = true;
                if (leg)
                {
                    legacy++;
                    same = CordMaterials.StrandG(g) == CordMaterials.StrandFor(v) && CordMaterials.StrandFaceG(g) == CordMaterials.StrandFaceFor(v) &&
                           CordMaterials.StrandLodG(g) == CordMaterials.StrandLodFor(v);
                    foreach (DecalKind k in Enum.GetValues(typeof(DecalKind))) same &= CordMaterials.DecalG(k, g) == CordMaterials.Decal(k, v);
                    if (same) legacySame++;
                }
                var decals = p.Decals.Select(d => TexName(CordMaterials.DecalG(d.Kind, g))).Where(n => n != null).Distinct();
                pieces.Add("{\"key\":" + S(p.Key) + ",\"owner\":[" + p.Owner.X + "," + p.Owner.Z + "],\"strands\":" + p.Strands.Count + ",\"g\":" + g + ",\"look\":" + S(look) +
                           ",\"variant\":" + variant + ",\"legacy\":" + B(leg) + (leg ? ",\"legacySameMaterials\":" + B(same) : "") +
                           ",\"strandTex\":" + S(TexName(CordMaterials.StrandG(g))) + ",\"decalTex\":[" + string.Join(",", decals.Select(S)) + "]}");
            }
            // ---- what the section meshes in the rect hold
            var printed = new Dictionary<string, int>();
            var sections = Traverse.Create(map.mapDrawer).Field("sections").GetValue<Section[,]>();
            if (sections != null)
                foreach (Section sec in sections)
                {
                    if (sec == null || !sec.CellRect.Overlaps(rect)) continue;
                    foreach (SectionLayer l in Traverse.Create(sec).Field("layers").GetValue<List<SectionLayer>>())
                    {
                        if (!(l is SectionLayer_RM_MessyCords)) continue;
                        foreach (LayerSubMesh m in l.subMeshes.Where(m => m.finalized && m.verts.Count > 0))
                        {
                            string n = TexName(m.material) + (CordMaterials.IsLod(m.material) ? "(lod)" : "");
                            printed[n] = printed.TryGetValue(n, out int c) ? c + m.verts.Count : m.verts.Count;
                        }
                    }
                }
            // ---- every look's strand textures (what a run of that look may print)
            var lookStrands = AerialStyles.Looks.Select(look =>
                S(look) + ":[" + string.Join(",", Enumerable.Range(0, ConduitStyles.VariantsOf(look)).Select(v => S(TexName(CordMaterials.StrandG(ConduitStyles.Global(look, v)))))) + "]");
            return AerialProbe.Ok(cmd, "\"defaultLook\":" + S(StylePicker.DefaultLook) + ",\"defaultKey\":" + S(ConduitStylePicker.DefaultKey(DefDatabase<ThingDef>.GetNamedSilentFail("PowerConduit"))) +
                ",\"missingStyleDefs\":[" + string.Join(",", ConduitStylePicker.Missing.Select(S)) + "],\"notStylable\":[" + string.Join(",", ConduitStylePicker.NotStylable.Select(S)) + "]" +
                ",\"globalMissing\":[" + string.Join(",", CordMaterials.GlobalMissing.Select(S)) + "],\"lookStrands\":{" + string.Join(",", lookStrands) + "}" +
                ",\"counters\":{\"processed\":" + runs.processed + ",\"adopted\":" + runs.adopted + ",\"bridges\":" + runs.bridges + ",\"linkBridges\":" + runs.linkBridges +
                ",\"repainted\":" + runs.repainted + ",\"materialised\":" + runs.materialised + ",\"restyles\":" + runs.restyles + ",\"pending\":" + runs.PendingCount + "}" +
                ",\"lastMessage\":" + S(runs.lastMessage) + ",\"switchPaths\":{" + string.Join(",", ConduitStylePicker.SwitchPaths.Select(kv => S(kv.Key) + ":" + S(kv.Value))) + "}" +
                ",\"members\":[" + string.Join(",", rows) + "],\"pieces\":[" + string.Join(",", pieces) + "],\"legacyPieces\":" + legacy + ",\"legacySameMaterials\":" + legacySame +
                ",\"printedTex\":{" + string.Join(",", printed.OrderBy(kv => kv.Key).Select(kv => S(kv.Key) + ":" + kv.Value)) + "}");
        }
    }
}
