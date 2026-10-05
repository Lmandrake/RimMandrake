using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>
    /// The per-build style's probe verbs (AerialProbe channel; read by validation_style.py). Every placement goes through
    /// the REAL Architect designator (BuildCopyCommandUtility.FindAllowedDesignator) and its DesignateSingleCell, with the
    /// look picked by StylePicker.Pick, the same call the build button's menu makes; only the CLICK is skipped. Building
    /// uses the engine's own Blueprint.TryReplaceWithSolidThing and Frame.CompleteConstruction with a real colonist, so
    /// the blueprint -> frame -> building style hand-offs are the engine's, not ours.
    /// </summary>
    public static class StyleProbeAerial
    {
        private static string S(string s) => AerialProbe.S(s);
        private static string B(bool b) => AerialProbe.B(b);
        private static string F(float f) => AerialProbe.F(f);

        private static Thing ById(Map map, int id) => map.listerThings.AllThings.FirstOrDefault(t => t.thingIDNumber == id);

        private static IntVec3 Cell(string xz)
        {
            string[] p = xz.Split(',');
            return new IntVec3(int.Parse(p[0], CultureInfo.InvariantCulture), 0, int.Parse(p[1], CultureInfo.InvariantCulture));
        }

        private static Pawn Worker(Map map) => map.mapPawns.FreeColonistsSpawned.FirstOrDefault();

        private static string TexOf(Thing t)
        {
            try
            {
                Graphic g = t.Graphic;
                return g?.MatAt(t.Rotation)?.mainTexture?.name ?? g?.path;
            }
            catch (Exception ex) { return "ERR " + ex.GetType().Name; }
        }

        private static string StyleRow(Thing t)
        {
            return "\"id\":" + t.thingIDNumber + ",\"def\":" + S(t.def.defName) + ",\"x\":" + t.Position.x + ",\"z\":" + t.Position.z +
                   ",\"rot\":" + t.Rotation.AsInt + ",\"rawStyle\":" + S(StylePicker.RawStyle(t)?.defName) + ",\"style\":" + S(t.StyleDef?.defName) +
                   ",\"graphicPath\":" + S(t.Graphic?.path) + ",\"drawnTex\":" + S(TexOf(t));
        }

        public static string Styles(Map map, RM_MapComponent_Aerial comp)
        {
            var rows = new List<string>();
            foreach (CompAerialAnchor a in comp.Anchors.OrderBy(x => x.thingIDNumber))
            {
                var spans = new List<string>();
                foreach (SpanLink l in a.links)
                {
                    if (l.state != SpanState.Up || l.other == null || !l.other.Spawned || !AerialMath.Owns(a.thingIDNumber, l.other.thingIDNumber)) continue;
                    SpanMesh m = comp.SpanMeshFor(a, l.other);
                    spans.Add("{\"other\":" + l.other.thingIDNumber + ",\"look\":" + S(m?.look) + ",\"expectLook\":" + S(AerialMaterials.SpanLookOf(a, l.other)) +
                              ",\"spanTex\":" + S(m?.mat?.mainTexture?.name) + ",\"width\":" + F(m?.Width ?? 0f) + "}");
                }
                rows.Add("{" + StyleRow(a.parent) + ",\"look\":" + S(AerialMaterials.LookOf(a)) + ",\"topTex\":" + S(AerialMaterials.TopPathFor(a)) +
                         ",\"attachZ\":" + F(AerialMaterials.AttachZ(a)) + ",\"insulators\":" + AerialMaterials.InsulatorsFor(a).Count +
                         ",\"basePoint\":[" + F(a.BasePoint.x) + "," + F(a.BasePoint.z) + "],\"spans\":[" + string.Join(",", spans) + "]}");
            }
            // blueprints / frames / minified of our defs: the style each one carries now
            var pending = new List<string>();
            foreach (Thing t in map.listerThings.AllThings)
            {
                ThingDef target = (t.def.entityDefToBuild as ThingDef) ?? (t is MinifiedThing mt ? mt.InnerThing?.def : null);
                if (!StylePicker.IsStyled(target)) continue;
                string kind = t is Blueprint_Install ? "install" : t is Blueprint ? "blueprint" : t is Frame ? "frame" : t is MinifiedThing ? "minified" : t.GetType().Name;
                ThingStyleDef st = t is MinifiedThing m2 ? m2.InnerThing?.StyleDef : t.StyleDef;
                ThingStyleDef raw = t is MinifiedThing m3 ? StylePicker.RawStyle(m3.InnerThing) : StylePicker.RawStyle(t);
                pending.Add("{\"id\":" + t.thingIDNumber + ",\"kind\":" + S(kind) + ",\"for\":" + S(target.defName) + ",\"x\":" + t.Position.x + ",\"z\":" + t.Position.z +
                            ",\"style\":" + S(st?.defName) + ",\"rawStyle\":" + S(raw?.defName) + ",\"drawnTex\":" + S(TexOf(t)) + "}");
            }
            var picks = AerialStyles.StyledDefs.Select(dn => S(dn) + ":" + S(StylePicker.LastPicked(DefDatabase<ThingDef>.GetNamedSilentFail(dn))));
            var lookSpans = AerialStyles.Looks.Select(l => S(l) + ":{\"tex\":" + S(AerialMaterials.For(l).Span?.mainTexture?.name) + ",\"path\":" + S(AerialMaterials.For(l).SpanPath) +
                                                         ",\"width\":" + F(AerialMaterials.For(l).Width) + "}");
            return "{\"success\":true,\"cmd\":\"styles\",\"lookSpans\":{" + string.Join(",", lookSpans) + "},\"defaultLook\":" + S(StylePicker.DefaultLook) + ",\"lastPicked\":{" + string.Join(",", picks) + "}" +
                   ",\"picks\":" + StylePicker.picks + ",\"missingStyleDefs\":[" + string.Join(",", StylePicker.Missing.Select(S)) + "]" +
                   ",\"frameStyleRestored\":" + Patch_Frame_KeepStyle.restored + ",\"godMode\":" + B(DebugSettings.godMode) +
                   ",\"anchors\":[" + string.Join(",", rows) + "],\"pending\":[" + string.Join(",", pending) + "]}";
        }

        /// <summary>place:def:Look:x,z[:rot]:god|build -- pick the look exactly as the menu does, then designate one cell with
        /// the real designator, god mode on or off for that one call.</summary>
        public static string Place(Map map, string args)
        {
            string cmd = "place:" + args;
            string[] p = args.Split(':');
            if (p.Length < 4) return AerialProbe.Fail(cmd, "want def:Look:x,z[:rot]:god|build");
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(p[0]);
            string look = p[1];
            IntVec3 c = Cell(p[2]);
            int rot = p.Length >= 5 ? int.Parse(p[3], CultureInfo.InvariantCulture) : 0;
            bool god = p[p.Length - 1] == "god";
            if (!StylePicker.IsStyled(d)) return AerialProbe.Fail(cmd, "not a styled def");
            Designator_Build des = BuildCopyCommandUtility.FindAllowedDesignator(d, mustBeVisible: false);
            if (des == null) return AerialProbe.Fail(cmd, "no Architect designator for " + p[0]);
            if (look != "-") StylePicker.Pick(des, look);
            Traverse.Create(des).Field("placingRot").SetValue(new Rot4(rot));
            return Designate(map, des, c, god, cmd);
        }

        private static string Designate(Map map, Designator_Build des, IntVec3 c, bool god, string cmd)
        {
            bool was = DebugSettings.godMode;
            try
            {
                DebugSettings.godMode = god;
                AcceptanceReport ok = des.CanDesignateCell(c);
                if (!ok.Accepted) return AerialProbe.Fail(cmd, "CanDesignateCell refused: " + ok.Reason);
                string handed = des.ThingStyleDefNonPreceptSource?.defName;
                var before = new HashSet<Thing>(c.GetThingList(map));
                des.DesignateSingleCell(c);
                Thing made = c.GetThingList(map).FirstOrDefault(t => !before.Contains(t) && (t.def == des.PlacingDef || t.def.entityDefToBuild == des.PlacingDef));
                return AerialProbe.Ok(cmd, "\"godMode\":" + B(god) + ",\"designatorStyle\":" + S(handed) + (made == null ? ",\"made\":null" :
                       ",\"made\":{" + StyleRow(made) + ",\"kind\":" + S(made is Blueprint ? "blueprint" : made.def == des.PlacingDef ? "building" : made.GetType().Name) + "}"));
            }
            finally { DebugSettings.godMode = was; }
        }

        /// <summary>Every blueprint of ours -> frame -> building, by the engine's own calls and a real colonist.</summary>
        public static string FinishBuild(Map map)
        {
            Pawn w = Worker(map);
            if (w == null) return AerialProbe.Fail("finishbuild", "no free colonist on the map");
            int frames = 0, built = 0;
            var errors = new List<string>();
            foreach (Blueprint bp in map.listerThings.AllThings.OfType<Blueprint>().Where(b => StylePicker.IsStyled(b.def.entityDefToBuild as ThingDef)).ToList())
            {
                try
                {
                    if (!bp.TryReplaceWithSolidThing(w, out Thing created, out _)) { errors.Add("blueprint " + bp.thingIDNumber + " blocked"); continue; }
                    if (created is Frame) frames++; else built++;      // a Blueprint_Install yields the building itself
                }
                catch (Exception ex) { errors.Add("blueprint " + bp.thingIDNumber + ": " + ex.Message); }
            }
            foreach (Frame f in map.listerThings.AllThings.OfType<Frame>().Where(fr => StylePicker.IsStyled(fr.def.entityDefToBuild as ThingDef)).ToList())
            {
                try { f.CompleteConstruction(w); built++; }
                catch (Exception ex) { errors.Add("frame " + f.thingIDNumber + ": " + ex.Message); }
            }
            return AerialProbe.Ok("finishbuild", "\"worker\":" + S(w.LabelShort) + ",\"workerHasIdeo\":" + B(w.Ideo != null) + ",\"frames\":" + frames + ",\"built\":" + built +
                                  ",\"errors\":[" + string.Join(",", errors.Select(S)) + "]");
        }

        /// <summary>reinstall:id:x,z -- pack the building up (MinifyUtility.Uninstall, vanilla's own) and install it at x,z through
        /// an install blueprint; the caller runs finishbuild to complete it.</summary>
        public static string Reinstall(Map map, string args)
        {
            string cmd = "reinstall:" + args;
            string[] p = args.Split(':');
            Thing t = ById(map, int.Parse(p[0], CultureInfo.InvariantCulture));
            if (t == null || !t.Spawned) return AerialProbe.Fail(cmd, "no such spawned thing");
            string before = t.StyleDef?.defName;
            MinifiedThing m = t.Uninstall();
            if (m == null) return AerialProbe.Fail(cmd, "uninstall failed");
            string minStyle = m.InnerThing?.StyleDef?.defName;
            Blueprint_Install bp = GenConstruct.PlaceBlueprintForInstall(m, Cell(p[1]), map, t.Rotation, Faction.OfPlayer);
            return AerialProbe.Ok(cmd, "\"styleBefore\":" + S(before) + ",\"minifiedStyle\":" + S(minStyle) + ",\"installBlueprint\":" + (bp?.thingIDNumber ?? -1) +
                                       ",\"installStyle\":" + S(bp?.StyleDef?.defName));
        }

        /// <summary>copy:id:x,z -- the thing's own "Copy" gizmo (BuildCopyCommandUtility.BuildCopyCommand, as Building.GetGizmos
        /// makes it), clicked, then one build-mode designation at x,z. The designator is deselected after.</summary>
        public static string Copy(Map map, string args)
        {
            string cmd = "copy:" + args;
            string[] p = args.Split(':');
            Thing t = ById(map, int.Parse(p[0], CultureInfo.InvariantCulture));
            if (t == null) return AerialProbe.Fail(cmd, "no such thing");
            Command c = BuildCopyCommandUtility.BuildCopyCommand(t.def, t.Stuff, null, t.StyleDef, styleOverridden: true);
            if (!(c is Command_Action ca)) return AerialProbe.Fail(cmd, "no copy command");
            ca.action();
            Designator_Build des = BuildCopyCommandUtility.FindAllowedDesignator(t.def, mustBeVisible: false);
            if (des == null || Find.DesignatorManager.SelectedDesignator != des) return AerialProbe.Fail(cmd, "copy did not select the designator");
            Traverse.Create(des).Field("placingRot").SetValue(t.Rotation);
            string res = Designate(map, des, Cell(p[1]), false, cmd);
            Find.DesignatorManager.Deselect();
            return res;
        }
    }
}
