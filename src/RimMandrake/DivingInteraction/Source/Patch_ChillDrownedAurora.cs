using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_FLOOR_LIGHT_1 — applies RM_MapComponent_ChillDrownedAurora's
    // computed violet-teal SkyTarget to the Chill seabed's own SkyManager.
    // See that component's file header for WHY a Harmony postfix here,
    // rather than a GameCondition registered on the seabed map itself
    // (short version: GameCondition.CanApplyOnMap refuses underground
    // unless allowUnderground=true, AND SkyTarget.LerpDarken can only ever
    // darken a map's baseline sky, never brighten it — both wrong for "the
    // floor breathes light").
    //
    // ── WHY A POSTFIX, AND WHY IT IS SAFE ──
    // Map.MapUpdate() (RimSage, Verse/Map.cs) calls
    // `skyManager.SkyManagerUpdate()` UNCONDITIONALLY, every frame, for
    // EVERY loaded map (Game.cs's own per-frame `maps[i].MapUpdate()` loop
    // — not gated to the currently-viewed map), and
    // `glowGrid.GlowGridUpdate_First()` runs immediately after it in the
    // same Map.MapUpdate() call. So: letting the ORIGINAL
    // SkyManagerUpdate() run first (untouched — every other map's weather/
    // GameCondition sky-blend, and this map's own for anything we don't
    // touch, is unaffected), then overwriting curSkyGlowInt/curSky in a
    // POSTFIX for the Chill seabed map only, guarantees the GlowGrid read
    // that follows in the very same MapUpdate() call sees OUR value, on
    // every map whether the player is currently looking at it or not
    // (needed: plant growMinGlow/growOptimalGlow checks and pawn sight read
    // GlowGrid at arbitrary times, not only while the map is on-screen).
    //
    // The ONE place this is a frame late: SkyManagerUpdate()'s own
    // `if (map == Find.CurrentMap)` block, which paints MatBases.LightOverlay
    // /shader globals from curSky BEFORE our postfix runs — so the rendered
    // tint reflects last frame's value, not this one. At 60 fps that is
    // ~16ms of staleness, imperceptible, and self-correcting every single
    // frame (we reassert our value after every original call, so "steady
    // state" is always ours).
    //
    // Mathf.Max is used for glow (never lowers whatever vanilla's own
    // weather-worker/GameCondition blend already produced for this map —
    // pure additive floor-raise, matching "never absolutely black... the
    // floor breathes light" as an ADDITION over whatever baseline exists,
    // not a replacement of it) — colour is a straight overwrite, since
    // vanilla has no opinion worth preserving about a sunless seabed's tint.
    //
    // Reflection: SkyManager's `map`/`curSkyGlowInt`/`curSky` fields are
    // private with no public setter beyond ForceSetCurSkyGlow (which only
    // covers the glow scalar, not colour) — cached FieldInfo, resolved
    // once. If a future engine update renames any of them, every lookup
    // below degrades to null and the postfix no-ops silently (no crash,
    // mechanism simply goes inert) — same risk profile as every other
    // reflection-based hook already in this codebase.
    // ════════════════════════════════════════════════════════════════════
    [HarmonyPatch(typeof(SkyManager), "SkyManagerUpdate")]
    [RimMandrake.Shared.PatchFeature("Chill drowned aurora", typeof(RM_DivingSettings), "chillDrownedAuroraEnabled")]
    public static class Patch_ChillDrownedAurora
    {
        private static readonly FieldInfo MapField = AccessTools.Field(typeof(SkyManager), "map");
        private static readonly FieldInfo CurSkyGlowField = AccessTools.Field(typeof(SkyManager), "curSkyGlowInt");
        private static readonly FieldInfo CurSkyField = AccessTools.Field(typeof(SkyManager), "curSky");

        public static void Postfix(SkyManager __instance)
        {
            if (MapField == null || CurSkyGlowField == null || CurSkyField == null)
            {
                return; // reflection target(s) missing — see class header
            }
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.chillDrownedAuroraEnabled)
            {
                return;
            }

            Map map = MapField.GetValue(__instance) as Map;
            if (!RM_ChillFireGate.IsChillSeabedMap(map))
            {
                return; // every other map, every frame: two static bool reads + one biome/pocket check, nothing else
            }

            RM_MapComponent_ChillDrownedAurora comp = map.GetComponent<RM_MapComponent_ChillDrownedAurora>();
            if (comp == null)
            {
                return;
            }

            SkyTarget ours = comp.ComputeSkyTarget();

            float existingGlow = (float)CurSkyGlowField.GetValue(__instance);
            float newGlow = Mathf.Max(existingGlow, ours.glow);
            CurSkyGlowField.SetValue(__instance, newGlow);

            SkyTarget cur = (SkyTarget)CurSkyField.GetValue(__instance);
            cur.glow = newGlow;
            cur.colors = ours.colors;
            CurSkyField.SetValue(__instance, cur);
        }
    }
}
