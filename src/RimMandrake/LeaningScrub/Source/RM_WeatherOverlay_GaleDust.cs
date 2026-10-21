using UnityEngine;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // SCRUB_WIND_BUILD_LEAN_ON_PURPOSE part 2 — the Gale on screen (owner card 2026-10-20, biome_bars_sitting §5.2:
    // "driven dust and fuzz on screen. This needs overlay art and a weather overlay").
    //
    // Shape copied from RUT_WeatherOverlay_ScaldSteam (EnvironmentalHazards), whose header records the engine facts:
    // MatLoader.LoadMat reads Unity Resources only (never hand it a mod path: a null material throws in the type
    // initializer and blacks the map), so the overlay copies vanilla's fog material and swaps in our textures.
    //
    // 🔴 PLACEHOLDER UNTIL THE ART IS REVIEWED. The owned textures are Weather/RM_GaleDust_A and _B, queued to the artpipe
    // (infrastructure/artpipe/art_lists/scrub_gale_dust_2026-10-20.json) and NOT installed: unreviewed art never ships.
    // While they are absent this draws vanilla's fog sheet, tinted dust-brown and panned fast downwind, and says so:
    // ArtState reads "PLACEHOLDER (vanilla fog sheet)" and the proof hook reports it. When reviewed art is installed at
    // those paths it is picked up with no code change.
    //
    // The sheet streams along the map's Lean heading (RM_MapComponent_Lean.Downwind) on a leaning map, else east.
    // The overlay instance lives on the WeatherDef (one per def, shared by every map), so the direction is re-read each
    // tick from the map being ticked. VERIFY BY STATE READ: RM_GaleDustProof.ProofGale.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public class RM_WeatherOverlay_GaleDust : WeatherOverlayDualPanner
    {
        private const string VanillaFogMatPath = "Weather/FogOverlayWorld";
        public const string DustTexA = "Weather/RM_GaleDust_A";
        public const string DustTexB = "Weather/RM_GaleDust_B";
        private static readonly int MainTex = Shader.PropertyToID("_MainTex");
        private static readonly int MainTex2 = Shader.PropertyToID("_MainTex2");

        public static string ArtState = "unloaded";
        private static readonly Material DustOverlayWorld = BuildMaterial();

        // Proof state: the last tick, map and pan direction this overlay drew with. Static: one instance per def.
        public static long LastTick = -1;
        public static Vector2 LastDir = Vector2.zero;
        public static bool LastDrew;

        private Vector2 pan1 = Vector2.zero;
        private Vector2 pan2 = Vector2.zero;

        private static Material BuildMaterial()
        {
            Material vanillaFog = MatLoader.LoadMat(VanillaFogMatPath);
            if (vanillaFog == null)
            {
                ArtState = "NONE (vanilla fog material missing)";
                Log.ErrorOnce("[RM LeaningScrub] could not load vanilla material '" + VanillaFogMatPath
                    + "'; the Gale's dust overlay will not draw.", 0x6A1ED5);
                return null;
            }
            Texture2D a = ContentFinder<Texture2D>.Get(DustTexA, false);
            Texture2D b = ContentFinder<Texture2D>.Get(DustTexB, false);
            // A private copy either way: the dust tint and pan must never touch vanilla Fog's own shared material.
            Material dust = new Material(vanillaFog) { name = "RM_GaleDust" };
            if (a == null && b == null)
            {
                ArtState = "PLACEHOLDER (vanilla fog sheet)";
                return dust;
            }
            if (a != null)
            {
                dust.SetTexture(MainTex, a);
            }
            if (b != null && dust.HasProperty(MainTex2))
            {
                dust.SetTexture(MainTex2, b);
            }
            ArtState = "owned (" + (a != null ? "A" : "-") + (b != null ? "B" : "-") + ")";
            return dust;
        }

        public RM_WeatherOverlay_GaleDust()
        {
            worldOverlayMat = DustOverlayWorld;
            // Dust-brown, lighter than the plain's soil so it reads as airborne. INVENTED, the owner judges the look.
            ForcedOverlayColor = new Color(0.86f, 0.76f, 0.58f);
            // Driven: about eight times Fog's drift, well under Rain's fall. INVENTED.
            worldOverlayPanSpeed1 = 0.004f;
            worldOverlayPanSpeed2 = 0.0028f;
            worldPanDir1 = new Vector2(1f, 0f);
            worldPanDir2 = new Vector2(1f, 0f);
        }

        public override void TickOverlay(Map map, float lerpFactor)
        {
            if (worldOverlayMat == null)
            {
                return;
            }
            Vector2 dir = new Vector2(1f, 0f);
            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(map);
            if (lean != null)
            {
                dir = lean.Downwind;
            }
            // Two sheets a few degrees apart so the streaks shear instead of sliding as one. INVENTED.
            worldPanDir1 = dir;
            worldPanDir2 = new Vector2(dir.x * 0.985f - dir.y * 0.17f, dir.x * 0.17f + dir.y * 0.985f);
            LastTick = Find.TickManager.TicksGame;
            LastDir = dir;
            float rate = Find.TickManager.TickRateMultiplier;
            pan1 -= worldPanDir1 * (worldOverlayPanSpeed1 * worldOverlayMat.GetTextureScale(MainTex).x * rate);
            worldOverlayMat.SetTextureOffset(MainTex, pan1);
            if (worldOverlayMat.HasProperty(MainTex2))
            {
                pan2 -= worldPanDir2 * (worldOverlayPanSpeed2 * worldOverlayMat.GetTextureScale(MainTex2).x * rate);
                worldOverlayMat.SetTextureOffset(MainTex2, pan2);
            }
        }

        public override void DrawOverlay(Map map)
        {
            LastDrew = RM_WindCalendar.On(RM_LeaningScrubSettings.galeDustOverlayEnabled);
            if (LastDrew)
            {
                base.DrawOverlay(map);
            }
        }

        public override void Reset()
        {
            pan1 = Vector2.zero;
            pan2 = Vector2.zero;
            base.Reset();
        }
    }

    // jawa/static_call proof hook (validation.py, windlean chain). Pure state read: the Gale must be the current
    // weather (the chain locks it and waits a few ticks first). PASS when RM_Gale carries this overlay, it ticked
    // recently, drew, and streams downwind on a leaning map. The art state is always reported, never hidden.
    public static class RM_GaleDustProof
    {
        public static string ProofGale(string unused)
        {
            Map map = Find.CurrentMap;
            WeatherDef gale = DefDatabase<WeatherDef>.GetNamedSilentFail("RM_Gale");
            if (map == null || gale == null)
            {
                return "UNMEASURED no map or no RM_Gale";
            }
            bool carries = gale.overlayClasses != null && gale.overlayClasses.Contains(typeof(RM_WeatherOverlay_GaleDust));
            string weather = map.weatherManager?.curWeather?.defName ?? "none";
            long age = Find.TickManager.TicksGame - RM_WeatherOverlay_GaleDust.LastTick;
            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(map);
            string s = " weather=" + weather + " art=" + RM_WeatherOverlay_GaleDust.ArtState
                + " dir=" + RM_WeatherOverlay_GaleDust.LastDir.ToString("F2") + " tickAge=" + age
                + " drew=" + RM_WeatherOverlay_GaleDust.LastDrew + " leanMap=" + (lean != null);
            if (!carries)
            {
                return "FAIL RM_Gale does not carry RM_WeatherOverlay_GaleDust" + s;
            }
            if (weather != "RM_Gale")
            {
                return "UNMEASURED the Gale is not the current weather" + s;
            }
            if (RM_WeatherOverlay_GaleDust.LastTick < 0 || age > 600)
            {
                return "FAIL the overlay has not ticked under the Gale" + s;
            }
            if (!RM_WeatherOverlay_GaleDust.LastDrew && RM_WindCalendar.On(RM_LeaningScrubSettings.galeDustOverlayEnabled))
            {
                return "FAIL the overlay did not draw with its toggle on" + s;
            }
            if (lean != null && Vector2.Dot(RM_WeatherOverlay_GaleDust.LastDir, lean.Downwind) < 0.99f)
            {
                return "FAIL the dust does not stream downwind" + s;
            }
            return "PASS" + s;
        }
    }
}
