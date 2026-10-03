# FallLineArrivals — validation walk
subject: src/RimUtinni/FallLineArrivals  (packageId `mandrake.rut.falllinearrivals`)
deps: mandrake.rm.shipvermin (nest engine), mandrake.rm.biomes (kit host), mandrake.rsw.swbestiary (nest species)
list: minimal + all DLC + mandrake.rm.biomes + mandrake.rm.shipvermin + mandrake.rsw.swbestiary
status-hint: Fall Line arrivals, first pass — wreck skyfallers that are vermin nests (Band A) and the lab-rat pod (Band C). Spec: design/RimUtinni/fall_line_arrival_mechanism_spec.md.

## must be true
- Loads with no error naming this mod's defs or classes. → load_clean.no_errors_naming_this_mod
- Every def resolves: two IncidentDefs, the RUT_LabRat kind, the RUT_FallLine mutator, three wrecks and three skyfallers. → defs.all_defs_resolve
- With "Only on Fall Line maps" ON, neither event fires on a map that is not on the Fall Line. → gate.off_fall_line_refused
- With it OFF, a wreck can fall on any colony map. → gate.anywhere_allows
- "Wrecks fall" OFF stops the wreck event. → gate.wrecks_toggle_off_refuses
- A wreck falls and stands on the map as a building. → wreck_falls_and_nests.wreck_lands
- Ship-vermin come out of a fresh wreck within its burst delay. → wreck_falls_and_nests.vermin_burst_from_wreck
- "The specimen" OFF stops the pod. → specimen.lab_rat_toggle_off_refuses
- The specimen pod lands one RUT_LabRat. → specimen.lab_rat_arrives_in_pod
- On the campaign start tile the gate passes with the setting ON. → UNCOVERED: needs the canonical save, not a quicktest; whether the WorldFeature name matches is UNMEASURED until the RUT_FallLine mutator is placed (FALL_LINE_MUTATOR_PLACEMENT_1).
- No species here is in any wildAnimals table. → UNCOVERED: a def-dump census, not a bridge read (owner rule fall_line.md §8a).

## anti-guessing notes
- RULED OUT: "RSW_Cindermite" as the zhakka's defName — the port is RSW_Zhakka (SWBestiary DesertPort/RSW_DesertPortMisc_Races.xml); the stale nest roster entry VFEI2_Fuelmite spawned the donor mite.
