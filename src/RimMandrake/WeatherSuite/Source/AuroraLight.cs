using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.Shared;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.WeatherSuite
{
    // AURORA_LIGHT (2026-10-20, AURORAL_UMBRA_RENAME_BACK_TO_DARK A2 failed live: "ground stays Dark (0%)").
    //
    // WHY A GAMECONDITION ALONE CANNOT DO IT (RimSage, Verse.SkyManager.CurrentSkyTarget): every condition's SkyTarget is folded in with
    // SkyTarget.LerpDarken, i.e. glow = min(glow, condition glow) and every sky/overlay/shadow channel = min. A condition can only DARKEN.
    //
    // WHY NOT RAISE SkyManager.CurSkyGlow: that one number is also "sunlight" - SanguophageUtility.InSunlight (> 0.1 burns sanguophages),
    // CompPowerPlantSolar output, DarknessCombatUtility (> 0.35 = lit). An aurora is not sunlight.
    //
    // WHAT THIS DOES INSTEAD (two postfixes + one overlay, all inert unless a permanent aurora is registered for that map):
    //   1. SkyManager.CurrentSkyTarget postfix - recolours ONLY colors.sky / colors.overlay after the darken fold: the ordinary night is
    //      darkened (the biome is "totally dark") and the aurora's animated hue is ADDED as light. colors.sky is what MatBases.LightOverlay
    //      multiplies the whole map by, so this is what the eye sees. glow is left alone (no sunlight side effects).
    //   2. GlowGrid.GroundGlowAt postfix - outdoor, unroofed cells get max(vanilla, aurora floor). The shipped floor stays under vanilla's
    //      PsychGlow "Lit" threshold (0.3), so it reads "Dark (22%)" and keeps the darkness mood: lit, but still a dark place.
    //   3. AuroraCurtains - additive (MoteGlow) ribbons drawn just ABOVE the lighting overlay (AltitudeLayer.VisEffects, under fog of war),
    //      two layers panning against each other, tinted with the live hue. The ribbon texture is generated in code: a PLACEHOLDER until
    //      curtain art comes through the art ledger.
    // Per-tick cost: one registry refresh per permanent aurora per tick (a few multiplies). Per-call cost of the GroundGlowAt postfix when no
    // aurora map exists: one int compare. Nothing here is saved: the registry is rebuilt by the condition's own tick after every load.
    public static class AuroraLightRegistry
    {
        public sealed class Entry
        {
            public Map map;
            public GameCondition_DarkAuroraMax condition;
            public int lastTick;
            public Color hue;
            public float shimmer = 1f, nightness, groundFloor, lerp;
        }

        private static readonly List<Entry> entries = new List<Entry>();
        public static int Count => entries.Count;

        public static Entry Find(Map map)
        {
            for (int i = 0; i < entries.Count; i++)
                if (entries[i].map == map) return entries[i];
            return null;
        }

        /// <summary>Called by a PERMANENT GameCondition_DarkAuroraMax every tick for each map it affects.</summary>
        public static void Refresh(GameCondition_DarkAuroraMax cond, Map map)
        {
            Entry e = Find(map);
            if (e == null)
            {
                Prune();
                e = new Entry { map = map };
                entries.Add(e);
            }
            int ticks = Verse.Find.TickManager.TicksGame;
            float activity = Mathf.Clamp(WeatherSuiteSettings.perpetualAuroraActivity, 1, 30);
            e.condition = cond;
            e.lastTick = ticks;
            e.hue = cond.CurrentColor;
            e.shimmer = RM_WeatherKernel.Shimmer(ticks, activity, (map.uniqueID % 97) * 0.37f);
            e.nightness = RM_WeatherKernel.Nightness(GenCelestial.CurCelestialSunGlow(map));
            e.lerp = cond.SkyTargetLerpFactor(map);
            e.groundFloor = RM_WeatherKernel.GroundGlowFloor(WeatherSuiteSettings.perpetualAuroraGroundGlow, e.shimmer, e.nightness) * e.lerp;
        }

        public static void Remove(Map map)
        {
            for (int i = entries.Count - 1; i >= 0; i--)
                if (entries[i].map == map) entries.RemoveAt(i);
        }

        /// <summary>Drops entries for maps that no longer exist (a removed map, or a previous game's maps after a load).</summary>
        public static void Prune()
        {
            List<Map> maps = Verse.Find.Maps;
            for (int i = entries.Count - 1; i >= 0; i--)
            {
                Entry e = entries[i];
                if (maps == null || !maps.Contains(e.map) || e.condition == null || e.condition.Expired || !e.condition.Permanent)
                    entries.RemoveAt(i);
            }
        }

        /// <summary>The live entry for this map, or null when the aurora is off, gone, or stale.</summary>
        public static Entry Live(Map map)
        {
            if (entries.Count == 0 || map == null || !WeatherSuiteSettings.perpetualAuroraEnabled) return null;
            Entry e = Find(map);
            if (e == null || e.condition == null || e.condition.Expired) return null;
            return e;
        }
    }

    [HarmonyPatch(typeof(SkyManager), "CurrentSkyTarget")]
    [PatchFeature("Perpetual aurora light (sky colour)", typeof(WeatherSuiteSettings), nameof(WeatherSuiteSettings.perpetualAuroraEnabled))]
    internal static class Patch_SkyManager_CurrentSkyTarget
    {
        private static void Postfix(ref SkyTarget __result, Map ___map)
        {
            AuroraLightRegistry.Entry e = AuroraLightRegistry.Live(___map);
            if (e == null || e.lerp <= 0f || e.nightness <= 0f) return;
            if (___map.Biome != null && ___map.Biome.disableSkyLighting) return;
            float k = e.lerp * e.nightness;
            float dark = WeatherSuiteSettings.perpetualAuroraNightDarkness * k;
            float light = WeatherSuiteSettings.perpetualAuroraSkyLight * e.shimmer * k;
            Color b = __result.colors.sky;
            __result.colors.sky = new Color(
                RM_WeatherKernel.AuroraSkyChannel(b.r, e.hue.r, dark, light),
                RM_WeatherKernel.AuroraSkyChannel(b.g, e.hue.g, dark, light),
                RM_WeatherKernel.AuroraSkyChannel(b.b, e.hue.b, dark, light), b.a);
            // overlay (weather overlays like propane rain take this tint): half the light, same darkening
            Color o = __result.colors.overlay;
            __result.colors.overlay = new Color(
                RM_WeatherKernel.AuroraSkyChannel(o.r, e.hue.r, dark, light * 0.5f),
                RM_WeatherKernel.AuroraSkyChannel(o.g, e.hue.g, dark, light * 0.5f),
                RM_WeatherKernel.AuroraSkyChannel(o.b, e.hue.b, dark, light * 0.5f), o.a);
        }
    }

    [HarmonyPatch(typeof(GlowGrid), nameof(GlowGrid.GroundGlowAt))]
    [PatchFeature("Perpetual aurora light (ground glow)", typeof(WeatherSuiteSettings), nameof(WeatherSuiteSettings.perpetualAuroraEnabled))]
    internal static class Patch_GlowGrid_GroundGlowAt
    {
        private static void Postfix(ref float __result, IntVec3 c, bool ignoreSky, Map ___map)
        {
            if (AuroraLightRegistry.Count == 0 || ignoreSky) return;
            AuroraLightRegistry.Entry e = AuroraLightRegistry.Live(___map);
            if (e == null || __result >= e.groundFloor) return;
            if (___map.roofGrid.Roofed(c)) return;   // a roof hides the sky, exactly as vanilla's own sky term
            __result = e.groundFloor;
        }
    }

    // Moving aurora curtains: additive ribbons over the darkened map. PLACEHOLDER texture (generated below) until curtain art lands through
    // the art ledger; the drawing, tinting and panning are the mechanism and stay.
    [StaticConstructorOnStartup]
    public static class AuroraCurtains
    {
        private static readonly Material Near, Far;
        private static Vector2 panNear, panFar;
        private static readonly int RenderLayer = LayerMask.NameToLayer("GravshipExclude");

        static AuroraCurtains()
        {
            Texture2D tex = MakeRibbonTexture(256, 128);
            Near = new Material(ShaderDatabase.MoteGlow) { mainTexture = tex, name = "RM_WS_AuroraCurtainNear" };
            Far = new Material(ShaderDatabase.MoteGlow) { mainTexture = tex, name = "RM_WS_AuroraCurtainFar" };
            Near.color = Color.clear;
            Far.color = Color.clear;
        }

        // Ribbons: each column's brightness is a sum of sines in x (several folds of curtain), with a bright lower hem fading upward, the
        // hem's height wandering along x. White; the hue is the material colour.
        private static Texture2D MakeRibbonTexture(int w, int h)
        {
            var tex = new Texture2D(w, h, TextureFormat.RGBA32, true) { wrapMode = TextureWrapMode.Repeat, filterMode = FilterMode.Bilinear, name = "RM_WS_AuroraRibbons" };
            var px = new Color[w * h];
            for (int x = 0; x < w; x++)
            {
                float u = x / (float)w * Mathf.PI * 2f;
                float fold = 0.5f + 0.5f * (0.55f * Mathf.Sin(u * 3f) + 0.3f * Mathf.Sin(u * 7f + 1.3f) + 0.15f * Mathf.Sin(u * 13f + 0.4f));
                float hem = 0.25f + 0.15f * Mathf.Sin(u * 2f + 0.7f);
                for (int y = 0; y < h; y++)
                {
                    float v = y / (float)h;
                    float d = v - hem;
                    float a = d < 0f ? Mathf.Exp(-d * d * 400f) : Mathf.Exp(-d * 4f);   // sharp hem below, long fade above
                    a *= fold * fold;
                    px[y * w + x] = new Color(1f, 1f, 1f, Mathf.Clamp01(a));
                }
            }
            tex.SetPixels(px);
            tex.Apply(true, true);
            return tex;
        }

        public static void Tick(AuroraLightRegistry.Entry e)
        {
            float speed = 0.00006f * Mathf.Clamp(WeatherSuiteSettings.perpetualAuroraActivity, 1, 30) * Find.TickManager.TickRateMultiplier;
            panNear += new Vector2(1f, 0.15f) * speed;
            panFar += new Vector2(-0.6f, 0.1f) * speed * 0.7f;
            panNear.x %= 1f; panNear.y %= 1f; panFar.x %= 1f; panFar.y %= 1f;
        }

        public static void Draw(Map map, AuroraLightRegistry.Entry e)
        {
            if (!WeatherSuiteSettings.perpetualAuroraCurtains || e.nightness <= 0f || e.lerp <= 0f) return;
            float a = WeatherSuiteSettings.perpetualAuroraCurtainStrength * e.shimmer * e.nightness * e.lerp;
            if (a <= 0.001f) return;
            Color c = e.hue;
            Near.color = new Color(c.r, c.g, c.b, a);
            // the far layer drifts toward the next hue's complement-ish neighbour: a second colour in the sky, never a flat wash
            Far.color = new Color(Mathf.Clamp01(c.r * 0.6f + 0.25f), c.g * 0.8f, Mathf.Clamp01(c.b + 0.2f), a * 0.6f);
            Near.mainTextureScale = new Vector2(map.Size.x / 70f, map.Size.z / 110f);
            Far.mainTextureScale = new Vector2(map.Size.x / 130f, map.Size.z / 170f);
            Near.mainTextureOffset = panNear;
            Far.mainTextureOffset = panFar;
            float alt = AltitudeLayer.VisEffects.AltitudeFor();
            SkyOverlay.DrawWorldOverlay(map, Far, alt, RenderLayer);
            SkyOverlay.DrawWorldOverlay(map, Near, alt + 0.01f, RenderLayer);
        }
    }
}
