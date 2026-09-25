using UnityEngine;
using Verse;

namespace RimMandrake.Greentide
{
    // GREENTIDE_MECHANICS_2 spike pass (greentide_kit_spec.md M4, "the Roil
    // — standing ground-fog weather").
    //
    // The spec's own M4 text names a class "RM_WeatherOverlay_GroundFog"
    // marked *(verified, greentide)* as if a shared, reusable overlay class
    // already existed for any biome's ground-hugging fog look. Checked this
    // pass: no such class exists anywhere in the repo, and
    // SCALD_MECHANICS_1's own spike pass (2026-09-13, this same repo) hit
    // the identical assumption and resolved it in full against the real
    // decompile of vanilla's own crib target
    // (RimWorld/WeatherOverlay_Fog.cs): its Material is a `static readonly`
    // field assigned in the CONSTRUCTOR body
    // (`MatLoader.LoadMat("Weather/FogOverlayWorld")`), and
    // WeatherDef.overlayClasses is a bare list of type names with no props
    // sub-block — vanilla's own pattern is one hardcoded-texture subclass
    // per look, never a shared class taking an XML-configurable texture. A
    // single "RM_WeatherOverlay_GroundFog" genuinely cannot serve both the
    // Scald's steam sky and the Greentide's ground fog with two different
    // looks. Re-verified directly this pass (not just cited from Scald's
    // finding): WeatherOverlay_Fog.cs read in full again, same shape
    // confirmed.
    //
    // So this ships the Greentide's own one-off, in the same shape
    // RUT_WeatherOverlay_ScaldSteam.cs (EnvironmentalHazards) already
    // established for its sibling kit, but in Greentide's OWN standalone
    // mod (src/RimMandrake/Greentide/Source/, mandrake.rm.greentide) rather
    // than the shared EnvironmentalHazards assembly — matching the real
    // precedent GREENTIDE_STANDALONE_MOD_1 already set for every other
    // Greentide-specific class (RM_MapComponent_TerrainMire etc. all live
    // here, not in EnvironmentalHazards, despite the spec's stale "lives in
    // the ruled kit's home" line predating the owner's later
    // own-RimMandrake-tier-mod ruling). RM_-prefixed, not RUT_-prefixed: per
    // NAMING_SCHEME_PLAN.md, RM_ is correct for a class shipping inside
    // Greentide's own RimMandrake-tier mod, not the RUT_-tier UtinniPatches.
    //
    // Panner values authored bottom-heavy per the sheet's "hides the floor,
    // canopy stands clear" art direction (worldPanDir tuned slow and
    // near-still, a standing roil rather than wind-driven weather) —
    // INVENTED, same honesty posture as Scald's own M4/S1 overlay: v1 ships
    // the *visual* ground-hug only (WeatherDef.accuracyMultiplier/
    // moveSpeedMultiplier are the mechanical half, both native WeatherDef
    // fields per the spec's own *(verified)* citation, XML-only, not this
    // class's concern). True per-layer occlusion (floor hidden, canopy
    // clear as an actual visibility mechanic) has no verified vanilla hook
    // — the spec's own M4 text already named this ❓/deferred and this pass
    // does not reopen it.
    public class RM_WeatherOverlay_GreentideRoil : WeatherOverlayDualPanner
    {
        // MatLoader.LoadMat reads only Unity Resources/, which no mod can ship to: a mod path
        // returns null and MaterialAllocator.Create(null) throws in this type initializer,
        // killing every Update() and blacking the map. Vanilla's own fog material stands in
        // until a custom panner material exists.
        private static readonly Material RoilOverlayWorld = MatLoader.LoadMat("Weather/FogOverlayWorld");

        public RM_WeatherOverlay_GreentideRoil()
        {
            worldOverlayMat = RoilOverlayWorld;
            // Slower than vanilla Fog's 0.0004-0.0005: a standing waist-deep
            // roil, not weather blowing through. INVENTED.
            worldOverlayPanSpeed1 = 0.00018f;
            worldOverlayPanSpeed2 = 0.00012f;
            worldPanDir1 = new Vector2(0.4f, 1f);
            worldPanDir2 = new Vector2(-0.35f, 0.85f);
        }
    }
}
