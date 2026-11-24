// RIMMANDRAKE_LIGHT_SLACK_SWITCH_GREEN_RED_DARK_WHEN_UNPOWERED (owner 2026-11-20; his card: "Green flows, red cut"): every power switch
// on screen carries a small lamp, green when closed and powered, red when open and powered, dark (no glow) when no side has power.
// Bar switch_light_reads_state. The state rule is Core/SwitchLight (SelfTest/SwitchLightChecks.cs runs it); this file reads the live
// map into it and draws, every frame and while paused, from RM_MapComponent_CordGraph.MapComponentUpdate. Its own setting
// (switchLight) gates it, not the cords' master switch: the lamp reads on the vanilla switch art too. Nothing is cached across frames,
// so a flick or a power change shows on the next frame.
using System.Collections.Generic;
using RimMandrake.GimmeSomeSlack.Core;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack
{
    internal static class SwitchLightDraw
    {
        private static Material[] lens, halo;
        private static bool artFailed;
        private static List<ThingDef> switchDefs;
        /// <summary>One frame's net reads; emptied every frame and by GssSessionReset (it holds the last game's PowerNets).</summary>
        internal static readonly Dictionary<PowerNet, bool> liveThisFrame = new Dictionary<PowerNet, bool>();
        private static readonly bool[] sides = new bool[4];

        /// <summary>Lamps drawn last frame, by state (the probe's switchlights read reports them).</summary>
        public static int LastGreen, LastRed, LastDark;

        /// <summary>Every ThingDef whose thing is a power switch (vanilla PowerSwitch and any other mod's), found once.</summary>
        internal static List<ThingDef> SwitchDefs()
        {
            if (switchDefs != null) return switchDefs;
            switchDefs = new List<ThingDef>();
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
                if (d.thingClass != null && typeof(Building_PowerSwitch).IsAssignableFrom(d.thingClass)) switchDefs.Add(d);
            return switchDefs;
        }

        private static bool Live(PowerNet net)
        {
            if (net == null) return false;
            if (!liveThisFrame.TryGetValue(net, out bool v)) liveThisFrame[net] = v = net.HasActivePowerSource;
            return v;
        }

        /// <summary>The lamp of one switch now: closed = TransmitsPowerNow; powered = its own net live, or the net on any cardinal side
        /// cell live (Core/SwitchLight header says why those cells).</summary>
        internal static SwitchLamp LampOf(Building_PowerSwitch sw, bool settingOn, out bool closed, out bool powered)
        {
            Map map = sw.Map;
            closed = sw.TransmitsPowerNow;
            bool own = closed && Live(sw.PowerComp?.PowerNet);
            int i = 0;
            foreach (IntVec3 c in GenAdj.CellsAdjacentCardinal(sw))
            {
                if (i >= sides.Length) break;
                sides[i++] = c.InBounds(map) && Live(map.powerNetGrid.TransmittedPowerNetAt(c));
            }
            for (; i < sides.Length; i++) sides[i] = false;
            powered = SwitchLight.AnySidePowered(own, sides);
            return SwitchLight.Of(settingOn, closed, powered);
        }

        private static Material Mat(byte[] px, Shader shader)
        {
            var t = new Texture2D(SwitchLampArt.Px, SwitchLampArt.Px, TextureFormat.RGBA32, false) { filterMode = FilterMode.Bilinear, wrapMode = TextureWrapMode.Clamp, name = "GSS_SwitchLamp" };
            t.LoadRawTextureData(px);
            t.Apply(false, true);
            return MaterialPool.MatFrom(new MaterialRequest(t, shader));
        }

        /// <summary>The three lens and two halo materials, made on the first draw (the main thread).</summary>
        private static bool Art()
        {
            if (lens != null) return true;
            if (artFailed) return false;
            try
            {
                lens = new Material[3]; halo = new Material[3];
                for (int s = 0; s < 3; s++)
                {
                    lens[s] = Mat(SwitchLampArt.Lens((SwitchLamp)s), ShaderDatabase.Transparent);
                    byte[] h = SwitchLampArt.Halo((SwitchLamp)s);
                    halo[s] = h == null ? null : Mat(h, ShaderDatabase.MoteGlow);
                }
                return true;
            }
            catch (System.Exception ex)
            {
                lens = null; artFailed = true;
                Log.Error("[GimmeSomeSlack] switch lamp art could not be made; the lamps are not drawn: " + ex);
                return false;
            }
        }

        /// <summary>The switch shows the Industrial look's closed art, whose baked green LED the lamp must not contradict
        /// (Patch_PowerSwitch_Graphic draws a look only while the cords are applied; the closed art is CompFlickable.SwitchIsOn).</summary>
        private static bool CapsBakedLed(Building_PowerSwitch sw) =>
            ConduitVisuals.Applied && Aerial.ConduitStylePicker.RawLook(sw) == "Industrial" && (sw.GetComp<CompFlickable>()?.SwitchIsOn ?? true);

        private static readonly Dictionary<string, Material> unlit = new Dictionary<string, Material>();
        /// <summary>Glows put out last frame (the probe's switchlights read reports it).</summary>
        public static int LastGlowOut;

        /// <summary>The Futuristic closed switch with no power: its unlit picture over its lit one (Core/SwitchLight.GlowOut).</summary>
        private static void DrawGlowOut(Building_PowerSwitch sw, Map map, Vector3 c, bool powered)
        {
            if (!ConduitVisuals.Applied) return;
            if (!SwitchLight.GlowOut(Aerial.ConduitStylePicker.RawLook(sw), sw.GetComp<CompFlickable>()?.SwitchIsOn ?? true, powered)) return;
            int drawn = SwitchStubs.All;
            if (sw.def.size.x == 1 && sw.def.size.z == 1) drawn = map.GetComponent<RM_MapComponent_CordGraph>()?.SwitchDrawnMask(sw.Position) ?? SwitchStubs.All;
            string path = CordMaterials.StyleDir + "Futuristic/" + SwitchLight.UnlitName(drawn);
            if (!unlit.TryGetValue(path, out Material m))
            {
                Texture2D tex = SafeTex.Get(path, false);
                GraphicData gd = sw.def.graphicData;
                if (tex != null) tex.wrapMode = TextureWrapMode.Clamp;
                unlit[path] = m = tex == null || gd == null ? null : MaterialPool.MatFrom(new MaterialRequest(tex, (gd.shaderType ?? ShaderTypeDefOf.Cutout).Shader));
            }
            if (m == null) return;
            Vector2 size = sw.def.graphicData.drawSize;
            Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(new Vector3(c.x, sw.def.altitudeLayer.AltitudeFor() + Altitudes.AltInc * 0.5f, c.z), Quaternion.identity,
                new Vector3(size.x, 1f, size.y)), m, 0);
            LastGlowOut++;
        }

        /// <summary>Draw the lamp of every switch in view on the current map. Called every frame.</summary>
        internal static void Draw(Map map)
        {
            LastGreen = LastRed = LastDark = LastGlowOut = 0;
            if (Find.CurrentMap != map) return;
            if (RimWorld.Planet.WorldRendererUtility.WorldSelected || SectionLayer_RM_MessyCords.CutsceneHides) return;
            bool lamps = GimmeSomeSlackSettings.switchLight && Art();
            if (!lamps && !ConduitVisuals.Applied) return;
            liveThisFrame.Clear();
            CellRect view = Find.CameraDriver.CurrentViewRect.ExpandedBy(1);
            float yLens = AltitudeLayer.BuildingOnTop.AltitudeFor(), yHalo = yLens - Altitudes.AltInc * 0.5f;   // under the lens, so the glow rings it and never washes it out
            foreach (ThingDef d in SwitchDefs())
                foreach (Thing t in map.listerThings.ThingsOfDef(d))
                {
                    if (!(t is Building_PowerSwitch sw) || !sw.Spawned || !view.Contains(sw.Position) || map.fogGrid.IsFogged(sw.Position)) continue;
                    SwitchLamp lamp = LampOf(sw, true, out _, out bool powered);
                    Vector3 c = sw.TrueCenter();
                    DrawGlowOut(sw, map, c, powered);
                    if (!lamps) continue;
                    var pos = new Vector3(c.x + SwitchLampArt.OffX, yLens, c.z + SwitchLampArt.OffZ);
                    if (halo[(int)lamp] != null)
                        Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(new Vector3(pos.x, yHalo, pos.z), Quaternion.identity,
                            new Vector3(SwitchLampArt.HaloCells, 1f, SwitchLampArt.HaloCells)), halo[(int)lamp], 0);
                    Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(pos, Quaternion.identity, new Vector3(SwitchLampArt.LensCells, 1f, SwitchLampArt.LensCells)), lens[(int)lamp], 0);
                    if (CapsBakedLed(sw))
                        Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(new Vector3(c.x + SwitchLampArt.LedX, yLens, c.z + SwitchLampArt.LedZ), Quaternion.identity,
                            new Vector3(SwitchLampArt.LedCapCells, 1f, SwitchLampArt.LedCapCells)), lens[(int)SwitchLamp.Dark], 0);
                    if (lamp == SwitchLamp.Green) LastGreen++; else if (lamp == SwitchLamp.Red) LastRed++; else LastDark++;
                }
        }
    }
}
