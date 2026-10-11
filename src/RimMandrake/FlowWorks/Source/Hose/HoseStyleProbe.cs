using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// The reel's per-build style probe verbs (HoseProbe channel; read by validation_style_hose.py). Ported at the hose port
    /// from Gimme Some Slack's StyleProbeAerial, scoped to FlowWorks' own picker (HoseLook): every placement goes through the
    /// REAL Architect designator and its DesignateSingleCell with the look picked by HoseLook.Pick (the menu's own call);
    /// building uses the engine's Blueprint.TryReplaceWithSolidThing and Frame.CompleteConstruction with a real colonist.
    ///   place:def:Look:x,z[:rot]:god|build | finishbuild | reinstall:id:x,z
    /// </summary>
    public static class HoseStyleProbe
    {
        private static string S(string s) => HoseProbe.S(s);
        private static string B(bool b) => HoseProbe.B(b);
        private static string Fail(string cmd, string why) => "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":" + S(why) + "}";
        private static string Ok(string cmd, string body) => "{\"success\":true,\"cmd\":" + S(cmd) + (body.Length > 0 ? "," + body : "") + "}";
        private static Thing ById(Map map, int id) => map.listerThings.AllThings.FirstOrDefault(t => t.thingIDNumber == id);
        private static Pawn Worker(Map map) => map.mapPawns.FreeColonistsSpawned.FirstOrDefault();

        private static IntVec3 Cell(string xz)
        {
            string[] p = xz.Split(',');
            return new IntVec3(int.Parse(p[0], CultureInfo.InvariantCulture), 0, int.Parse(p[1], CultureInfo.InvariantCulture));
        }

        private static string TexOf(Thing t)
        {
            try
            {
                Graphic g = t.Graphic;
                return g?.MatAt(t.Rotation)?.mainTexture?.name ?? g?.path;
            }
            catch (Exception ex) { return "ERR " + ex.GetType().Name; }
        }

        private static string StyleRow(Thing t) =>
            "\"id\":" + t.thingIDNumber + ",\"def\":" + S(t.def.defName) + ",\"x\":" + t.Position.x + ",\"z\":" + t.Position.z +
            ",\"rot\":" + t.Rotation.AsInt + ",\"rawStyle\":" + S(HoseLook.RawStyle(t)?.defName) + ",\"style\":" + S(t.StyleDef?.defName) +
            ",\"graphicPath\":" + S(t.Graphic?.path) + ",\"drawnTex\":" + S(TexOf(t));

        public static string Place(Map map, string args)
        {
            string cmd = "place:" + args;
            string[] p = args.Split(':');
            if (p.Length < 4) return Fail(cmd, "want def:Look:x,z[:rot]:god|build");
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(p[0]);
            string look = p[1];
            IntVec3 c = Cell(p[2]);
            int rot = p.Length >= 5 ? int.Parse(p[3], CultureInfo.InvariantCulture) : 0;
            bool god = p[p.Length - 1] == "god";
            if (!HoseLook.IsStyled(d)) return Fail(cmd, "not a styled def");
            Designator_Build des = BuildCopyCommandUtility.FindAllowedDesignator(d, mustBeVisible: false);
            if (des == null) return Fail(cmd, "no Architect designator for " + p[0]);
            if (look != "-") HoseLook.Pick(des, look);
            Traverse.Create(des).Field("placingRot").SetValue(new Rot4(rot));
            bool was = DebugSettings.godMode;
            try
            {
                DebugSettings.godMode = god;
                AcceptanceReport ok = des.CanDesignateCell(c);
                if (!ok.Accepted) return Fail(cmd, "CanDesignateCell refused: " + ok.Reason);
                string handed = des.ThingStyleDefNonPreceptSource?.defName;
                var before = new HashSet<Thing>(c.GetThingList(map));
                des.DesignateSingleCell(c);
                Thing made = c.GetThingList(map).FirstOrDefault(t => !before.Contains(t) && (t.def == des.PlacingDef || t.def.entityDefToBuild == des.PlacingDef));
                return Ok(cmd, "\"godMode\":" + B(god) + ",\"designatorStyle\":" + S(handed) + (made == null ? ",\"made\":null" :
                       ",\"made\":{" + StyleRow(made) + ",\"kind\":" + S(made is Blueprint ? "blueprint" : made.def == des.PlacingDef ? "building" : made.GetType().Name) + "}"));
            }
            finally { DebugSettings.godMode = was; }
        }

        /// <summary>Every blueprint of a styled reel -> frame -> building, by the engine's own calls and a real colonist.</summary>
        public static string FinishBuild(Map map)
        {
            Pawn w = Worker(map);
            if (w == null) return Fail("finishbuild", "no free colonist on the map");
            int frames = 0, built = 0;
            var errors = new List<string>();
            foreach (Blueprint bp in map.listerThings.AllThings.OfType<Blueprint>().Where(b => HoseLook.IsStyled(b.def.entityDefToBuild as ThingDef)).ToList())
            {
                try
                {
                    if (!bp.TryReplaceWithSolidThing(w, out Thing created, out _)) { errors.Add("blueprint " + bp.thingIDNumber + " blocked"); continue; }
                    if (created is Frame) frames++; else built++;
                }
                catch (Exception ex) { errors.Add("blueprint " + bp.thingIDNumber + ": " + ex.Message); }
            }
            foreach (Frame f in map.listerThings.AllThings.OfType<Frame>().Where(fr => HoseLook.IsStyled(fr.def.entityDefToBuild as ThingDef)).ToList())
            {
                try { f.CompleteConstruction(w); built++; }
                catch (Exception ex) { errors.Add("frame " + f.thingIDNumber + ": " + ex.Message); }
            }
            return Ok("finishbuild", "\"worker\":" + S(w.LabelShort) + ",\"workerHasIdeo\":" + B(w.Ideo != null) + ",\"frames\":" + frames + ",\"built\":" + built +
                      ",\"errors\":[" + string.Join(",", errors.Select(S)) + "]");
        }

        /// <summary>reinstall:id:x,z -- pack the reel up (vanilla Uninstall) and place an install blueprint at x,z.</summary>
        public static string Reinstall(Map map, string args)
        {
            string cmd = "reinstall:" + args;
            string[] p = args.Split(':');
            Thing t = ById(map, int.Parse(p[0], CultureInfo.InvariantCulture));
            if (t == null || !t.Spawned) return Fail(cmd, "no such spawned thing");
            string before = t.StyleDef?.defName;
            MinifiedThing m = t.Uninstall();
            if (m == null) return Fail(cmd, "uninstall failed");
            string minStyle = m.InnerThing?.StyleDef?.defName;
            Blueprint_Install bp = GenConstruct.PlaceBlueprintForInstall(m, Cell(p[1]), map, t.Rotation, Faction.OfPlayer);
            return Ok(cmd, "\"styleBefore\":" + S(before) + ",\"minifiedStyle\":" + S(minStyle) + ",\"installBlueprint\":" + (bp?.thingIDNumber ?? -1) +
                           ",\"installStyle\":" + S(bp?.StyleDef?.defName));
        }
    }
}
