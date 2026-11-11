# Frozen-contract live plan

Run the production extension_proof.py --live --chains liquid_pump, all four declared components, on registered calm_v3 (250x250, dry, >=3 standing colonists). No worldgen. Intended tier: mods__mandrake_rm_flowworks__mandrake_rm_hugethings__mandrake_rm_patches (13 ordered mods, all five DLC). No changed gameplay artifact.

PROVE unpowered: ProofPump.running=False, moved=0; sum ProofPitWater water /10000 remains 6 within 0.02 after 600 governed ticks. LIES: external source replenishment; plot D moved east of historical pond and reset first.

PROVE powered: after battery charged and 800 governed ticks, running=True, moved>=2; exact channel sum equals 6-moved within 0.02 and tank holds 10000*moved units. LIES: measuring floored fill instead of exact water, stale identity, unpowered fixture.

PROVE disabled: liquidPumpEnabled=False read/set; after 600 ticks running=False and moved unchanged. LIES: unpowered pump; powered positive control precedes it.

PROVE pour: ProofTank result starts TANK mode=Dump effective=Dump before ProofPump ;pour. Read exact channel sum before/after 600 ticks; increase >0.02 required. LIES: tank modes off, missing tank, mismatched effective mode, unrelated source inflow. Explicitly require tankModesEnabled=True, retain raw mode/volume/tick calls, compare with the unpowered control and source staging.

Result fields: chains[name=liquid_pump].components[].name/verdict/detail/evidence[{call,result}], situational.{gate,seen_hits,validity}, env.{running,running_sha256,assembly_sha256}; all_green is scoped to this selected chain only. No full-suite acceptance.

Before launch require cold preflight GREEN; after Steam launch require live preflight GREEN and investigate every exception/config error. Expected FlowWorks DLL SHA256 1c92c54ebdffb03aefa05c92512b37d2ce63a67ea18f5b8c3b903ef146bfd8a2; type_probe must confirm loaded MVID matches file. Bad load signatures: Caught exception while loading play data; Recovered from incompatible or corrupted mods errors; Config error in; missing RimMandrake type. All are investigated rather than ignored.

Snapshot every registry mod static and debug flag before suite writes. Use a unique save_site baseline (new file and no prior-slot stat changes), reload it before measuring full-map Rect fingerprint and difficulty reference. Finally reload baseline, compare full map terrain/underterrain/roof/depth/exact liquid/thing identity-position-HP fingerprint, restore exact pre-scene static/debug values and difficulty; verify equality. Preserve all raw failures. Three nonpass runs require independent pilot diagnosis.

Stop using supported live_session.stop_game, stamp DOWN, release immediately, verify both lease and host lock FREE before offline broaden/judge. Keep full logs private, publish only token-free findings and hashes.
