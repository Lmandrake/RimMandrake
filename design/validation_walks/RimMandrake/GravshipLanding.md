# RimMandrake: Gravship Landing Reveal — validation walk
subject: src/RimMandrake/GravshipLanding  (packageId `mandrake.rm.gravshiplanding`)
deps: `brrainz.harmony`, `Ludeon.RimWorld.Odyssey` (modDependencies)
list: standalone Harmony mod; ships no defs
status-hint: GRAVSHIP_LANDING_FIRST_SCRIPT_1 — first script drafted, never run live

Sources: `src/RimMandrake/GravshipLanding/About/About.xml` description, `Source/GravshipLandingMod.cs`, `Source/Patch_GenStep_GravshipMarker.cs`.

## must be true
- The mod ships no defs and a bogus def name reads notFound (the probe can say absent). → defs_resolve.control_probe_can_say_absent
- The one Mod Setting, `revealOutdoorsBeforeLanding` (default on), round-trips get/set/get/restore. → settings_roundtrip.revealOutdoorsBeforeLanding_round_trips
- The reveal postfix is attached to `GenStep_GravshipMarker.Generate` by `mandrake.rm.gravshiplanding`, after vanilla's marker step. → reveal_gate_armed.postfix_attached_to_gravship_marker_generate
- On a gravship-arrival map every OUTDOOR (unroofed) fogged cell is unfogged before the landing picker appears. → arrival_map_reveal.outdoor_cells_unfogged_on_arrival_map (UNMEASURED: needs a gravship arrival)
- Roofed interiors (mountains, sealed rooms, dungeons) stay fogged. → arrival_map_reveal.roofed_interiors_stay_fogged (UNMEASURED: needs a gravship arrival)
- With the setting off the map is vanilla: only the flood-fill from the reserved landing spot is unfogged. → arrival_map_reveal.toggle_off_leaves_vanilla_fog (UNMEASURED: needs a gravship arrival)
- No effect on a non-arrival map (`parms.gravship == null`) or without Odyssey. → UNCOVERED: the bridge cannot generate a map of either kind on demand; the source guard is the evidence

## the walk
1. [D] `jawa/get_defs` on a control name reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on `GravshipLandingSettings`   # settings_roundtrip
3. [D] `jawa/harmony_patches GenStep_GravshipMarker.Generate`: postfix `Postfix`, owner `mandrake.rm.gravshiplanding`   # reveal_gate_armed
4. [B] gravship-arrival map fog counts   # arrival_map_reveal (UNMEASURED until a drivable route exists)

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "the Harmony id string proves the patch attached" — PatchAll can succeed on the assembly and the target still be missing; reveal_gate_armed reads the live patch list.
RULED OUT: "the dependency-free settings round trip proves the reveal" — it proves the field; the effect needs an arrival map (UNMEASURED).
