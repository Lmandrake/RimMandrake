using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit
{
    /// <summary>
    /// Makes the conduit itself invisible (design §1-§2, §8.1) and gives it back when the master
    /// switch is off.
    ///
    /// The swap is done in C#, not as an XML texPath patch: an XML patch can only be undone by a
    /// restart, and the settings contract is "all-off degrades to vanilla, restoring correctly".
    /// So each target def's GraphicData is replaced by a copy whose texPath is a fully transparent
    /// 32x32 PNG (the same texture trick Invisible Conduit Continued uses), keeping linkType
    /// Transmitter so neighbour regeneration still works (§1: linkType None breaks it), and the
    /// original GraphicData object is kept to put back. Beauty and Flammability are NOT touched
    /// (that was Invisible Conduit's hidden gameplay change, §2).
    ///
    /// Targets: every def with building.isPowerConduit and a Transmitter link drawer, EXCEPT
    /// vanilla's own HiddenConduit, which stays the tidy invisible option and is drawn as buried.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class ConduitVisuals
    {
        public const string TransparentTexPath = "RimMandrake/MessyConduit/ConduitTransparent";

        private static readonly Dictionary<ThingDef, GraphicData> originals = new Dictionary<ThingDef, GraphicData>();
        private static readonly HashSet<ThingDef> targets = new HashSet<ThingDef>();
        public static bool Applied { get; private set; }

        static ConduitVisuals()
        {
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d.building == null || !d.building.isPowerConduit) continue;
                if (d.graphicData == null || d.graphicData.linkType != LinkDrawerType.Transmitter) continue;
                if (d == ThingDefOf.HiddenConduit) continue;
                targets.Add(d);
                originals[d] = d.graphicData;
            }
            switchDef = DefDatabase<ThingDef>.GetNamedSilentFail("PowerSwitch");
            if (switchDef?.graphicData != null) switchOrig = switchDef.graphicData;
            Apply(MessyConduitSettings.enabled);
            Log.Message("[MessyConduit] targets: " + string.Join(", ", TargetNames()) + "; invisible=" + Applied);
        }

        public static IEnumerable<string> TargetNames()
        {
            foreach (ThingDef d in targets) yield return d.defName;
        }

        public static bool IsTarget(ThingDef d) => d != null && targets.Contains(d);

        /// <summary>Hidden or untagged conduit: carries connectivity, never drawn.</summary>
        public static bool IsOtherConduit(ThingDef d) =>
            d != null && d.building != null && d.building.isPowerConduit && !targets.Contains(d);

        public static void Apply(bool invisible)
        {
            foreach (ThingDef d in targets)
            {
                GraphicData orig = originals[d];
                GraphicData use = orig;
                if (invisible)
                {
                    use = new GraphicData();
                    use.CopyFrom(orig);
                    use.texPath = TransparentTexPath;
                }
                d.graphicData = use;
                d.graphic = use.Graphic;
            }
            Applied = invisible;
            ApplySwitch(invisible);
            if (Current.ProgramState == ProgramState.Playing && Find.Maps != null)
            {
                foreach (Map map in Find.Maps)
                    foreach (Thing t in map.listerThings.AllThings)
                        if (targets.Contains(t.def) || t.def == switchDef) t.Notify_ColorChanged();
            }
        }

        // ---------------------------------------------------------------- the power switch (owner review 2026-10-04 B3)
        /// <summary>The vanilla switch's arms run to the very edge of its texture: drawn on bare ground (no conduit under it
        /// any more) a dark hairline shows round the tile edge. With the cords on, the switch draws our copy of the art
        /// held inside a 3 px fully transparent margin and clamped, so nothing can sample at the tile edge. Off restores
        /// vanilla exactly.</summary>
        public const string SwitchTexPathOurs = "RimMandrake/MessyConduit/PowerSwitch";
        private static ThingDef switchDef;
        private static GraphicData switchOrig;

        public static string SwitchTexPath() => switchDef?.graphicData?.texPath;

        private static void ApplySwitch(bool ours)
        {
            if (switchDef == null || switchOrig == null) return;
            GraphicData use = switchOrig;
            Texture2D on = ContentFinder<Texture2D>.Get(SwitchTexPathOurs, false), off = ContentFinder<Texture2D>.Get(SwitchTexPathOurs + "_Off", false);
            if (ours && on != null && off != null)
            {
                on.wrapMode = TextureWrapMode.Clamp;
                off.wrapMode = TextureWrapMode.Clamp;
                use = new GraphicData();
                use.CopyFrom(switchOrig);
                use.texPath = SwitchTexPathOurs;
                // round 3 (owner 2026-10-04: "The wires should go beneath the Power Switch"): vanilla draws the switch with
                // the Transparent shader (queue 3000, no depth write), the same queue as our cords (plugs 3001), so cords and
                // plugs painted OVER it whatever their altitude. Cutout writes depth like every other device, so the cords at
                // Conduits altitude go under it (Core.DrawStack.CordsPaintOver models the rule; SelfTest checks it).
                if (Core.DrawStack.CordsPaintOver(3000, false, 3000)) use.shaderType = ShaderTypeDefOf.Cutout;
            }
            switchDef.graphicData = use;
            switchDef.graphic = use.Graphic;
        }

        /// <summary>For the probe: the texPath each target currently renders with.</summary>
        public static Dictionary<string, string> CurrentTexPaths()
        {
            var o = new Dictionary<string, string>();
            foreach (ThingDef d in targets) o[d.defName] = d.graphicData?.texPath;
            return o;
        }

        public static int HookupWiresSuppressed;
        public static int OverlayWiresPrinted;
        public static int HookupCablesPrinted;
    }

    /// <summary>
    /// The thin machine->conduit hookup wire (CompPower.PostPrintOnto, forPowerOverlay:false) is
    /// suppressed for OUR conduit only; the machine is a node of the cord graph and gets a real cord.
    /// The power-overlay connector line (forPowerOverlay:true) is NEVER touched: Invisible Conduit's
    /// unconditional prefix erased it, which is the bug this avoids (§2, risk register row 16).
    /// </summary>
    [HarmonyPatch(typeof(PowerNetGraphics), nameof(PowerNetGraphics.PrintWirePieceConnecting))]
    public static class Patch_PrintWirePieceConnecting
    {
        public static bool Prefix(SectionLayer layer, Thing A, Thing B, bool forPowerOverlay)
        {
            if (forPowerOverlay)
            {
                ConduitVisuals.OverlayWiresPrinted++;
                return true;
            }
            if (!MessyConduitSettings.enabled || !MessyConduitSettings.hideHookupWires) return true;
            if (B != null && ConduitVisuals.IsTarget(B.def))
            {
                ConduitVisuals.HookupWiresSuppressed++;
                return false;
            }
            // B24 (owner review 2026-10-04): a hookup to anything that is not our conduit (a mast, a lamp mast, a wall
            // bracket, a power switch) was vanilla's hair-thin grey wire, invisible to him. Print it as the look's own
            // cable instead (the span cable: thick dark Industrial/Scrapper, black Modern, sleek steel Futuristic).
            if (A == null || B == null || Aerial.AerialMaterials.Span == null) return true;
            // round 2 (owner 2026-10-04): a device wired to a mast / lamp mast / bracket is a drop wire from its centroid to
            // the pole TERMINAL it is given (RM_MapComponent_Aerial.DrawLocalDrops, drawn per frame so the terminal spread
            // follows every sibling), never this straight line to the pole's graphic centre
            if (Aerial.AerialSettings.enabled && Aerial.CompAerialAnchor.Of(B) != null) { ConduitVisuals.HookupWiresSuppressed++; return false; }
            ConduitVisuals.HookupCablesPrinted++;
            PrintCable(layer, A, B);
            return false;
        }

        public static void PrintCable(SectionLayer layer, Thing A, Thing B)
        {
            // round 2 (owner 2026-10-04, station 4): end at each building's CENTROID, printed at SmallWire altitude, i.e.
            // beneath both buildings, so the art hides the ends and no misalignment can show
            Vector3 a = A.TrueCenter(), b = B.TrueCenter();
            Vector3 center = (a + b) / 2f;
            center.y = AltitudeLayer.SmallWire.AltitudeFor();
            Vector3 v = b - a;
            float len = v.MagnitudeHorizontal(), w = Mathf.Max(0.1f, Aerial.AerialMaterials.SpanWidth * 0.85f);
            float u = len / (w * 4f);
            // plane corners (-x,-z) (-x,+z) (+x,+z) (+x,-z): the strand tile's u runs ALONG the cable (plane z), v across
            var uvs = new[] { new Vector2(0f, 0f), new Vector2(u, 0f), new Vector2(u, 1f), new Vector2(0f, 1f) };
            Printer_Plane.PrintPlane(layer, center, new Vector2(w, len), Aerial.AerialMaterials.Span, v.AngleFlat(), false, uvs);
        }
    }
}
