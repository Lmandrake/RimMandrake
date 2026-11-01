using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SCALD_MECHANICS_1 S1 build pass (scald_kit_spec.md "the boil layer —
    // boiling-lift integration + standing steam"), rebuilt for
    // SCALD_STEAM_WEATHER_DESIGN_1 §3.1 step 6 on 2026-09-26.
    //
    // The spec's own S1 text names a shared "RM_WeatherOverlay_GroundFog"
    // class, attributed to the greentide kit and described as "verified,
    // greentide". Checked: no such class exists anywhere in src/, and
    // GREENTIDE_STANDALONE_MOD_1.md never mentions it either — the spec's
    // citation was to the CRIB TARGET being verified
    // (`WeatherOverlay_Fog : WeatherOverlayDualPanner`, real, decompile),
    // not to an RM_ class that has actually been built. Vanilla's own
    // overlay pattern is one hardcoded material per subclass
    // (WeatherOverlay_Fog, _Rain, _Snow ...), and WeatherDef.overlayClasses
    // is a bare list of type names with no props block to carry a texture,
    // so a shared generic could not serve two biomes' art anyway. This is
    // a Scald-scoped one-off, in vanilla's own shape.
    //
    // ── The look: vanilla fog as the haze, our own two cloud layers on top ─
    // Swapping our textures into a copy of the fog material showed nothing
    // (measured live: same camera, steam against clear, no cloud shape, only a
    // tint). So the fog material stays vanilla, and the clouds are two plain
    // Transparent materials this class pans and draws itself.
    //
    // ⚠️ MatLoader.LoadMat reads Unity Resources only: never hand it a mod path.
    // MeshPool.wholeMapPlane maps one UV to 10 map cells, so a texture needs a
    // scale well under 1 or a billow is two cells wide.
    // SkyOverlay.ForcedOverlayColor is honoured by SkyManager, which sets its
    // alpha to the weather's lerp factor, so the clouds fade with the weather.
    //
    // With the textures absent this is plain vanilla fog and nothing breaks.
    [StaticConstructorOnStartup]
    public class RUT_WeatherOverlay_ScaldSteam : WeatherOverlayDualPanner
    {
        private const string VanillaFogMatPath = "Weather/FogOverlayWorld";
        private const string SteamTexA = "Weather/RM_ScaldSteam_A";
        private const string SteamTexB = "Weather/RM_ScaldSteam_B";

        // INVENTED, judged live: a tile spans 70 and 50 cells; billows at 0.5 opacity, streaks at 0.4.
        private const float ScaleA = 0.143f;
        private const float ScaleB = 0.2f;
        private const float OpacityA = 0.5f;
        private const float OpacityB = 0.4f;

        private static readonly Material FogMat = MatLoader.LoadMat(VanillaFogMatPath);
        private static readonly Material CloudA = BuildCloud(SteamTexA, ScaleA);
        private static readonly Material CloudB = BuildCloud(SteamTexB, ScaleB);

        private Vector2 panA;
        private Vector2 panB;

        private static Material BuildCloud(string path, float scale)
        {
            Texture2D tex = ContentFinder<Texture2D>.Get(path, false);
            if (tex == null)
            {
                return null;
            }
            Material m = new Material(ShaderDatabase.Transparent) { mainTexture = tex };
            m.mainTextureScale = new Vector2(scale, scale);
            m.color = Color.clear;
            return m;
        }

        public override void TickOverlay(Map map, float lerpFactor)
        {
            base.TickOverlay(map, lerpFactor);
            float rate = Find.TickManager.TickRateMultiplier;
            if (CloudA != null)
            {
                panA -= worldPanDir1 * (worldOverlayPanSpeed1 * ScaleA * rate);
                CloudA.mainTextureOffset = panA;
            }
            if (CloudB != null)
            {
                panB -= worldPanDir2 * (worldOverlayPanSpeed2 * ScaleB * rate);
                CloudB.mainTextureOffset = panB;
            }
        }

        public override void DrawOverlay(Map map)
        {
            base.DrawOverlay(map);
            if (CloudA != null)
            {
                DrawWorldOverlay(map, CloudA);
            }
            if (CloudB != null)
            {
                DrawWorldOverlay(map, CloudB);
            }
        }

        public override void SetOverlayColor(Color color)
        {
            base.SetOverlayColor(color);
            if (CloudA != null)
            {
                CloudA.color = new Color(color.r, color.g, color.b, color.a * OpacityA);
            }
            if (CloudB != null)
            {
                CloudB.color = new Color(color.r, color.g, color.b, color.a * OpacityB);
            }
        }

        public RUT_WeatherOverlay_ScaldSteam()
        {
            worldOverlayMat = FogMat;

            // Sheet §9: "cyan glow under white steam". White, with the
            // water's own cyan bleeding up through it — never a grey blind.
            // INVENTED value, from the spec's own §3.1 draft.
            ForcedOverlayColor = new Color(0.88f, 0.97f, 0.97f);

            // Slow, near-still drift: the sheet's art direction is
            // "perpetual roil" but S1's steam sky is standing breath, not
            // wind-driven fog — deliberately slower than Fog's own
            // 0.0004-0.0005 pan speed. INVENTED.
            worldOverlayPanSpeed1 = 0.0002f;
            worldOverlayPanSpeed2 = 0.00015f;
            worldPanDir1 = new Vector2(0.6f, 1f);
            worldPanDir2 = new Vector2(-0.5f, 0.9f);
        }
    }
}
