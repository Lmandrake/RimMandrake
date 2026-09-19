using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_LOUDNESS_FRONT_1: canon.yml `in_front.core_src` -- "The front
    // is reckoned at each LANDING (judgement of the past map)."
    //
    // GenStep_GravshipMarker.Generate is the same real arrival choke point
    // `RimMandrake.GravshipLanding` (src/RimMandrake/GravshipLanding/Source/
    // Patch_GenStep_GravshipMarker.cs) already patches to unfog the new map --
    // its own comment there records the gen-step order (ReserveGravshipArea
    // 600 -> Fog 1500 -> GravshipMarker 1700) and that `parms.gravship` being
    // non-null is what marks this specifically as a gravship-arrival map, not
    // any other map type. Two independent Harmony postfixes on the same
    // vanilla method from two different mods is ordinary and safe; this one
    // does not touch fog or anything GravshipLanding owns.
    //
    // Scope, honestly stated: this covers gravship arrivals only, the
    // colony's one and only "the ship lands" event in this campaign (the
    // Cradle-substrate framing in canon.yml is specifically about the
    // gravship). A base-game caravan/pod arrival at a site with no map does
    // NOT reach this gen step and is not reckoned as a landing here -- if
    // that path ever needs the same treatment, it is a separate hook, not an
    // extension of this one.
    [HarmonyPatch(typeof(GenStep_GravshipMarker), nameof(GenStep_GravshipMarker.Generate))]
    public static class Patch_GravshipLanded_ReckonFront
    {
        [HarmonyPostfix]
        public static void Postfix(GenStepParams parms)
        {
            if (!ModsConfig.OdysseyActive || parms.gravship == null) return;
            GameComponent_Ninefold.Instance?.ReckonFrontAtLanding();
        }
    }
}
