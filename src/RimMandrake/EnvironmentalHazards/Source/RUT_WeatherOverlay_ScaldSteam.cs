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
    // ── The look: copy vanilla's fog material, swap its textures, tint it ─
    // Three engine facts settle the route, all MEASURED against the 1.6
    // decompile:
    //
    //  1. `MatLoader.LoadMat(path)` is `Resources.Load("Materials/" + path)`
    //     — Unity Resources ONLY. No mod folder is ever searched. Handing it
    //     a mod path returns null, and building a Material from null throws
    //     inside this type initializer, which blacks the whole map. 🔴 Never
    //     call it with anything but a vanilla path.
    //  2. Copying a Material carries its shader and every property with it,
    //     so a copy of the fog material already pans correctly; only the
    //     textures need replacing. ⚠️ `MaterialAllocator.Create(Material)`,
    //     which the spec's draft snippet used, is `internal static` to
    //     Assembly-CSharp and is NOT callable from a mod assembly — it would
    //     not compile. `new Material(src)` is what that method does anyway
    //     (plus leak bookkeeping the tracker only uses for a warning), so
    //     that is what this uses.
    //  3. `SkyOverlay.ForcedOverlayColor` is honoured by SkyManager — a
    //     forced colour replaces the sky's own overlay colour for that
    //     overlay. Anomaly's WeatherOverlay_BloodFog tints exactly this way.
    //
    // ── Graceful by construction ─────────────────────────────────────────
    // With the two mod textures absent, `ContentFinder.Get(..., false)`
    // returns null, nothing is swapped, and this class is EXACTLY the
    // previous shipped look (vanilla fog, borrowed). So the art can land
    // later without another code change and nothing is broken meanwhile.
    // That matters because the textures are real art content, queued to the
    // artpipe as scaldsteam_overlay_a/_b, not written here.
    //
    // ⚠️ UNMEASURED, to settle on the first live run (both harmless either
    // way, which is why they are guarded rather than assumed): whether
    // vanilla's fog material declares `_MainTex2` at all, and whether
    // ForcedOverlayColor on a WORLD overlay reads as a tint rather than a
    // wash at the shipped alpha.
    [StaticConstructorOnStartup]
    public class RUT_WeatherOverlay_ScaldSteam : WeatherOverlayDualPanner
    {
        private const string VanillaFogMatPath = "Weather/FogOverlayWorld";
        private const string SteamTexA = "Weather/RM_ScaldSteam_A";
        private const string SteamTexB = "Weather/RM_ScaldSteam_B";

        private static readonly Material SteamOverlayWorld = BuildMaterial();

        private static Material BuildMaterial()
        {
            Material vanillaFog = MatLoader.LoadMat(VanillaFogMatPath);
            if (vanillaFog == null)
            {
                // Should be impossible (vanilla path), but a null here would
                // otherwise throw in the type initializer and black the map.
                Log.ErrorOnce(
                    "[RM EnvironmentalHazards] could not load vanilla material '" + VanillaFogMatPath
                    + "'; the Scald's steam overlay will not draw.", 0x5CA1D0);
                return null;
            }

            Texture2D a = ContentFinder<Texture2D>.Get(SteamTexA, false);
            Texture2D b = ContentFinder<Texture2D>.Get(SteamTexB, false);
            if (a == null && b == null)
            {
                return vanillaFog; // no owned art yet — vanilla fog, unchanged, no copy allocated
            }

            Material steam = new Material(vanillaFog);
            if (a != null)
            {
                steam.SetTexture("_MainTex", a);
            }
            if (b != null && steam.HasProperty("_MainTex2"))
            {
                steam.SetTexture("_MainTex2", b);
            }
            return steam;
        }

        public RUT_WeatherOverlay_ScaldSteam()
        {
            worldOverlayMat = SteamOverlayWorld;

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
