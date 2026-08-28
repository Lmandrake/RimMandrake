# THRUSTER_INSTABUILD_NEVER_ACTIVE_1 — tool-built thrusters link but never contribute range

Measured 2026-08-28, 582-mod list, scratch quicktest. Three thrusters (SmallThruster x2,
LargeThruster x1; build_batch AND god-mode designator; both pad edges; exclusion zones
verified empty of foundations/things/roof; rot verified 0 via jawa/export_things): all end
LINKED (engine missingComponents clears) and NEVER ACTIVE — engine GravshipRange stays 0.
The campaign ship's hand-built thrusters on the same list give range 40. No log errors.
Suspect a mod patch (VGE re-categorizes thrusters into Platform and may patch activity/stat).

## verify
Same build sequence on the 13-mod minimal list (modlist_swap): if range appears, bisect the
mod; if not, the vanilla condition analysis in GRAVSHIP_LAUNCH_TRAVEL_1's session missed
something — instrument CompGravshipThruster.CanBeActive with a companion read tool.

## Note 2026-08-28 (BENCH): VEF patches this exact machinery
`vendor/mod_sources/VanillaExpandedFramework-main/Source/VEF/Buildings/Harmony/` transpiles
`CompAffectedByFacilities.PotentialThingsToLinkTo` / `CanPotentiallyLinkTo` (facility
"equivalence") and patches `GravshipUtility.PreLaunchConfirmation`. Start the bisect there.
