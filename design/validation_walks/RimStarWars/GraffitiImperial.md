# RimStarWars: Imperial Graffiti — validation walk
subject: src/RimStarWars/GraffitiImperial  (packageId `mandrake.rsw.graffitiimperial`)
deps: `mandrake.rm.graffiti` (hard, the framework); loadAfter Royalty (the `Empire` FactionDef the gate names)
list: minimal tier plus the Graffiti framework and Royalty
status-hint: GRAFFITI_IMPERIAL_FIRST_SCRIPT_1 — content-only addon (one ThingDef, no C#, no settings class); first script drafted, never run live

Sources: `src/RimStarWars/GraffitiImperial/About/About.xml` description, `Defs/ThingDefs_GraffitiImperial.xml`, the framework's `Defs/ThingDefs_Graffiti.xml` (sibling `RM_Graffiti_Stencil_Crown`) and `Source/ModExtension_Graffiti.cs`.

## must be true
- The one def (`RSW_Graffiti_Stencil_ImperialCog`) loads and resolves; a bogus name reads notFound. → defs_resolve.every_shipped_def_resolves
- The mod has no Mod Settings of its own; the framework's `paintingEnabled` is the effective master gate and is readable. → settings_roundtrip.no_settings_class_of_its_own, settings_roundtrip.framework_master_gate_is_readable
- Its framework extension reads category Taunt, form Stencil and the Empire hostility gate, live. → framework_wiring.extension_reads_taunt_stencil_empire_live
- The Empire gate stays in lockstep with the franchise-free Crown mark (wave-76 defect: it once shipped ungated). → framework_wiring.gate_in_lockstep_with_the_crown
- The gate's FactionDef (`Empire`, Royalty) exists, so the gate does not open on a no-match. → framework_wiring.empire_faction_def_resolves
- A placed mark exists as one thing with Beauty -5 and Cleanliness -3 ("does not fade"). → mark_state.mark_spawned_is_found_with_ruled_beauty_and_cleanliness (probe control: mark_state.empty_rect_reads_zero_probe_can_say_absent)
- The spree can pick the cog from the weighted pool. → mechanics_unmeasured.spree_pool_can_pick_the_cog (UNMEASURED: random pick, needs a sampling method)
- An Empire-allied painter never paints it, an Empire-hostile one can. → mechanics_unmeasured.imperial_painter_never_paints_it_hostile_painter_can (UNMEASURED: no verb sets faction relations)
- The designator and raid-exit tagging offer it. → mechanics_unmeasured.designator_and_raid_exit_offer_it (UNMEASURED: UI and a raid)
- The art resolves with no magenta. → mechanics_unmeasured.texture_binds_and_renders (UNMEASURED: visual; art queued, not generated)
- The art reads as asemic Aurebesh, not English. → UNCOVERED: visual judgment, the owner's (fork F5)

## the walk
1. [D] `jawa/get_defs ThingDef/RSW_Graffiti_Stencil_ImperialCog`: `foundCount` 1; a bogus def reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field get paintingEnabled` on `RimMandrake.Graffiti.RM_GraffitiSettings`   # settings_roundtrip
3. [D] `jawa/get_defs fields modExtensions deep` on the cog and the Crown; `FactionDef/Empire`   # framework_wiring
4. [B] `jawa/spawn_batch` the mark on prepared concrete at the live map centre; `jawa/list_things`, `jawa/thing_stats Beauty,Cleanliness`; an empty rect as control   # mark_state
X. [S] (human pass) the stencil, once generated, reads as a crossed-out Imperial cog with an Aurebesh-styled tag; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "this mod needs a settings round trip" — there is no Source/ folder and no settings class; static_checks fails if one appears, so a future C# addition forces the chain to be written.
RULED OUT: "an Empire-less tier is a defect" — the gate is null-safe and opens on no match by design (GraffitiPool.HostilityGateAllows); the check that the FactionDef resolves is a tier-composition check, not a mod verdict.
