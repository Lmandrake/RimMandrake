using System;
using System.Collections.Generic;
using System.Globalization;
using RimMandrake.Shared.StylePicker;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// STYLE_READBACK_PROBE_ANY_BUILT_THING: a read-only style reader for ANY building, blueprint or frame on a cell, so a
    /// faucet, sprinkler head or pipe pole's StyleDef and drawn texture can be measured (list_things and inspect_string omit
    /// style; HoseStyleProbe's place: verb refuses non-reel defs). Two doors onto the same row:
    ///   jawa/static_call type=RimMandrake.FlowWorks.Hose.StyleReadback method=StyleRow args="x,z"
    ///   HoseProbe request "stylerow:x,z"
    /// Both answer {"success":true,"cmd":"stylerow:x,z","rows":[{id,def,x,z,rot,rawStyle,style,look,graphicPath,drawnTex,kind}]}.
    /// SpawnStyled is the live proof's staging door: it spawns a def with a given ThingStyleDef (style set before spawn,
    /// as GenConstruct does for a styled build), so the reader has a known answer to read back.
    /// </summary>
    public static class StyleReadback
    {
        private static string S(string s) => HoseProbe.S(s);
        private static string Fail(string cmd, string why) => "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":" + S(why) + "}";

        /// <summary>"x,z" -> the cell, or null when the text is not two integers.</summary>
        internal static IntVec3? ParseCell(string xz)
        {
            string[] p = (xz ?? "").Split(',');
            if (p.Length != 2) return null;
            if (!int.TryParse(p[0].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int x)) return null;
            if (!int.TryParse(p[1].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int z)) return null;
            return new IntVec3(x, 0, z);
        }

        /// <summary>The material texture the thing draws at its rotation (falls back to the graphic's path).</summary>
        internal static string TexOf(Thing t)
        {
            try
            {
                Graphic g = t.Graphic;
                return g?.MatAt(t.Rotation)?.mainTexture?.name ?? g?.path;
            }
            catch (Exception ex) { return "ERR " + ex.GetType().Name; }
        }

        /// <summary>The look word of a "&lt;def&gt;_&lt;Look&gt;" style def name (null when unstyled).</summary>
        internal static string LookOfStyleName(string styleDefName)
        {
            if (string.IsNullOrEmpty(styleDefName)) return null;
            int us = styleDefName.LastIndexOf('_');
            return us > 0 && us < styleDefName.Length - 1 ? styleDefName.Substring(us + 1) : null;
        }

        /// <summary>One thing's style fields (no braces): what is stored, what the engine reports, what is drawn.</summary>
        public static string Row(Thing t)
        {
            string style = t.StyleDef?.defName;
            return "\"id\":" + t.thingIDNumber + ",\"def\":" + S(t.def.defName) + ",\"x\":" + t.Position.x + ",\"z\":" + t.Position.z +
                   ",\"rot\":" + t.Rotation.AsInt + ",\"rawStyle\":" + S(StylePickerCore.RawStyle(t)?.defName) + ",\"style\":" + S(style) +
                   ",\"look\":" + S(LookOfStyleName(style)) + ",\"graphicPath\":" + S(t.Graphic?.path) + ",\"drawnTex\":" + S(TexOf(t));
        }

        private static string KindOf(Thing t) =>
            t is Blueprint ? "blueprint" : t is Frame ? "frame" : t is Building ? "building" : t.GetType().Name;

        /// <summary>A thing the reader reports: anything built or being built (never a pawn, plant, filth or item).</summary>
        internal static bool IsBuilt(Thing t) =>
            t is Building || t is Blueprint || t is Frame || t.def.category == ThingCategory.Building;

        /// <summary>static_call surface: "x,z" -> every building/blueprint/frame on that cell of the current map, any def.</summary>
        public static string StyleRow(string arg)
        {
            string cmd = "stylerow:" + arg;
            Map map = Find.CurrentMap;
            if (map == null) return Fail(cmd, "no current map");
            return StyleRowOn(map, arg);
        }

        public static string StyleRowOn(Map map, string arg)
        {
            string cmd = "stylerow:" + arg;
            IntVec3? c = ParseCell(arg);
            if (c == null) return Fail(cmd, "want x,z");
            if (!c.Value.InBounds(map)) return Fail(cmd, "out of bounds");
            var rows = new List<string>();
            foreach (Thing t in c.Value.GetThingList(map))
            {
                if (IsBuilt(t)) rows.Add("{" + Row(t) + ",\"kind\":" + S(KindOf(t)) + "}");
            }
            return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"rows\":[" + string.Join(",", rows) + "]}";
        }

        /// <summary>static_call staging surface: "def,style|-,x,z[,rot]" -> spawn one def at the cell (default stuff) with that
        /// ThingStyleDef (or none for "-"), player faction, and answer the reader's row for the cell.</summary>
        public static string SpawnStyled(string arg)
        {
            string cmd = "spawnstyled:" + arg;
            Map map = Find.CurrentMap;
            if (map == null) return Fail(cmd, "no current map");
            string[] p = (arg ?? "").Split(',');
            if (p.Length < 4) return Fail(cmd, "want def,style|-,x,z[,rot]");
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(p[0].Trim());
            if (d == null) return Fail(cmd, "no ThingDef " + p[0]);
            ThingStyleDef sd = null;
            if (p[1].Trim() != "-")
            {
                sd = DefDatabase<ThingStyleDef>.GetNamedSilentFail(p[1].Trim());
                if (sd == null) return Fail(cmd, "no ThingStyleDef " + p[1]);
            }
            IntVec3? c = ParseCell(p[2] + "," + p[3]);
            if (c == null || !c.Value.InBounds(map)) return Fail(cmd, "bad cell");
            int rot = p.Length >= 5 && int.TryParse(p[4].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int r) && r >= 0 && r < 4 ? r : 0;
            Thing t = ThingMaker.MakeThing(d, d.MadeFromStuff ? GenStuff.DefaultStuffFor(d) : null);
            if (sd != null) t.StyleDef = sd;
            if (t.def.CanHaveFaction) t.SetFactionDirect(Faction.OfPlayer);
            GenSpawn.Spawn(t, c.Value, map, new Rot4(rot));
            return StyleRowOn(map, c.Value.x + "," + c.Value.z);
        }
    }
}
