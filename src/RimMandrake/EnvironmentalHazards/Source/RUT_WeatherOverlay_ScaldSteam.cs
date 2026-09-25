using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SCALD_MECHANICS_1 S1 build pass (scald_kit_spec.md "the boil layer —
    // boiling-lift integration + standing steam").
    //
    // The spec's own S1 text names a shared "RM_WeatherOverlay_GroundFog"
    // class, attributed to the greentide kit and described as "verified,
    // greentide". Checked this pass: no such class exists anywhere in
    // src/ (zero hits for "WeatherOverlay_GroundFog" outside kit-spec
    // markdown), and GREENTIDE_STANDALONE_MOD_1.md never mentions it either
    // — the spec's citation was to the CRIB TARGET being verified
    // (`WeatherOverlay_Fog : WeatherOverlayDualPanner`, real, decompile),
    // not to an RM_ class that has actually been built. Confirmed via the
    // real decompile of WeatherOverlay_Fog (RimWorld/WeatherOverlay_Fog.cs):
    // its Material is a `static readonly` field set in the CONSTRUCTOR body
    // (`MatLoader.LoadMat("Weather/FogOverlayWorld")`) — vanilla's own
    // overlay pattern is one hardcoded texture per subclass, not a shared
    // class with an XML-configurable texture (WeatherDef.overlayClasses is
    // a bare list of type names with no props sub-block to carry one). A
    // single shared "GroundFog" class genuinely could not serve two
    // different texture sets without either a static/global texture
    // override (fragile, load-order-dependent) or per-instance XML config
    // vanilla's own field doesn't offer. So this pass ships a Scald-scoped
    // one-off, in the same shape vanilla itself uses for each of its own
    // looks (WeatherOverlay_Fog, _Rain, _Snow, ...), rather than presuming
    // to build and name the shared generic on greentide kit's behalf.
    //
    public class RUT_WeatherOverlay_ScaldSteam : WeatherOverlayDualPanner
    {
        // MatLoader.LoadMat reads only Unity Resources/, which no mod can ship to: a mod path
        // returns null and MaterialAllocator.Create(null) throws in this type initializer,
        // killing every Update() and blacking the map. Vanilla's own fog material stands in
        // until a custom panner material exists.
        private static readonly Material SteamOverlayWorld = MatLoader.LoadMat("Weather/FogOverlayWorld");

        public RUT_WeatherOverlay_ScaldSteam()
        {
            worldOverlayMat = SteamOverlayWorld;
            // Slow, near-still drift: the sheet's own art direction is
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
