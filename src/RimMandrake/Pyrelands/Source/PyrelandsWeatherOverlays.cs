using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// Falling weather that can be seen on this biome's ground. Vanilla's rain and snow overlays are light streaks and flakes that
    /// vanish on dark ash under a dim sky: on map w at noon (2026-11-08) vanilla Rain, black rain on WeatherOverlay_Rain and ash fall
    /// on WeatherOverlay_SnowHard all captured with no drop or flake at 47 px a cell, so black rain read only as a darker hour.
    /// These draw their own alpha-blended textures (weather_overlay_gen.py) in two layers that pan at different speeds, so a dark
    /// drop reads dark on bright grass and a pale flake pale on dark ash. The material colour is the sky's overlay alpha only
    /// (ForcedOverlayColor white): the texture carries the colour, and the alpha fades it in and out with the weather transition.
    /// </summary>
    public abstract class WeatherOverlay_RM_Layered : SkyOverlay
    {
        private static readonly int MainTex = Shader.PropertyToID("_MainTex");
        private static readonly int RenderLayer = LayerMask.NameToLayer("GravshipExclude");   // where vanilla weather draws

        private Material near, far;
        private Vector2 panNear, panFar;
        private Color color = Color.clear;
        private int draws, ticks;
        private string texState = "not looked up";

        private static readonly System.Collections.Generic.List<WeatherOverlay_RM_Layered> live = new System.Collections.Generic.List<WeatherOverlay_RM_Layered>();

        /// <summary>For the bridge (jawa/static_call): each live overlay's material, colour, texture and how often it drew and ticked.</summary>
        public static string Diag()
        {
            var sb = new System.Text.StringBuilder();
            foreach (var o in live)
                sb.AppendFormat("{0}: tex={1} mat={2} shader={3} color={4} draws={5} ticks={6} pan={7}; ", o.GetType().Name, o.texState,
                    o.near != null, o.near != null && o.near.shader != null ? o.near.shader.name : "-", o.color, o.draws, o.ticks, o.panNear);
            return sb.Length == 0 ? "no overlay constructed" : sb.ToString();
        }

        protected abstract string TexPath { get; }
        protected abstract Vector2 DirNear { get; }
        protected abstract Vector2 DirFar { get; }
        protected abstract float SpeedNear { get; }
        protected abstract float SpeedFar { get; }
        /// <summary>The far layer's texture scale: above 1 draws it smaller and denser, which reads as further away.</summary>
        protected virtual float FarScale => 1.6f;
        /// <summary>The far layer's alpha against the near one.</summary>
        protected virtual float FarAlpha => 0.6f;

        protected WeatherOverlay_RM_Layered()
        {
            ForcedOverlayColor = Color.white;
            live.Add(this);
        }

        private bool EnsureMaterials()
        {
            if (near != null) return true;
            if (!UnityData.IsInMainThread) return false;
            var tex = ContentFinder<Texture2D>.Get(TexPath, false);
            texState = tex == null ? "missing" : tex.width + "x" + tex.height;
            if (tex == null) return false;
            tex.wrapMode = TextureWrapMode.Repeat;
            near = new Material(ShaderDatabase.Transparent) { mainTexture = tex, name = "RM_" + TexPath + "_near" };
            far = new Material(ShaderDatabase.Transparent) { mainTexture = tex, name = "RM_" + TexPath + "_far" };
            far.SetTextureScale(MainTex, new Vector2(FarScale, FarScale));
            ApplyColor();
            return true;
        }

        private void ApplyColor()
        {
            if (near == null) return;
            near.color = color;
            far.color = new Color(color.r, color.g, color.b, color.a * FarAlpha);
        }

        public override void TickOverlay(Map map, float lerpFactor)
        {
            ticks++;
            if (near == null) return;
            float rate = Find.TickManager.TickRateMultiplier;
            panNear -= DirNear.normalized * (SpeedNear * rate);
            panFar -= DirFar.normalized * (SpeedFar * FarScale * rate);
            panNear.x %= 1f; panNear.y %= 1f; panFar.x %= 1f; panFar.y %= 1f;
            near.SetTextureOffset(MainTex, panNear);
            far.SetTextureOffset(MainTex, panFar);
        }

        public override void DrawOverlay(Map map)
        {
            draws++;
            if (!EnsureMaterials()) return;
            if (color.a <= 0.001f) return;
            DrawWorldOverlay(map, far, RenderLayer);
            DrawWorldOverlay(map, near, RenderLayer);
        }

        public override void SetOverlayColor(Color c)
        {
            color = c;
            ApplyColor();
        }

        public override void Reset()
        {
            panNear = panFar = Vector2.zero;
        }
    }

    /// <summary>Black rain: thin sooty streaks falling down and a little left, as fast as vanilla rain (0.015 and 0.022).</summary>
    public class WeatherOverlay_RM_BlackRain : WeatherOverlay_RM_Layered
    {
        protected override string TexPath => "Weather/RM_FE_BlackRainStreaks";
        protected override Vector2 DirNear => new Vector2(-0.25f, -1f);
        protected override Vector2 DirFar => new Vector2(-0.24f, -1f);
        protected override float SpeedNear => 0.022f;
        protected override float SpeedFar => 0.015f;
    }

    /// <summary>Ash fall: soft grey flakes drifting down slowly and sideways on the wind, the near layer faster than the far
    /// (snow-gentle speeds, not SnowHard's, which read as brown rain).</summary>
    public class WeatherOverlay_RM_AshFall : WeatherOverlay_RM_Layered
    {
        protected override string TexPath => "Weather/RM_FE_AshFlakes";
        protected override Vector2 DirNear => new Vector2(-0.55f, -1f);
        protected override Vector2 DirFar => new Vector2(-0.4f, -1f);
        protected override float SpeedNear => 0.0035f;
        protected override float SpeedFar => 0.0022f;
        protected override float FarAlpha => 0.75f;
    }
}
