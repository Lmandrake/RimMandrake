# Flyer gate progress 2026-10-09
- started: reading item/doc
- Found A (flyer_plate_from_master.py) and C (lock wing rule) ALREADY committed (56568324e, cb451164f). Remaining work = floor + east re-run + queue.
- (a) S/N floor set 0.38 -> 0.25 (measured after A+C: S 0.279, N 0.260; 0.28 would fail N, so 0.25 keeps margin). Decision taken by question card 2026-10-09 06:12.
- East re-run (plate v2 east; master_v2/wing2_v1/wing3_v1): share old rule 0.238 -> rule C 0.344; locked frames DIFFER (hashes changed). Still fails east floor 0.45 and 6px margin; master v2 cover 0.563 < 0.92 so the gate rejects it anyway. East was never passing; its filed (failed) output changed but is not installable.
- (b) Hawkbat east master OK'd (decision taken by question card). Filed S/N masters hawkbat_fly_master_v1_{south,north} (derive_from east master; rows: Transient/hawkbat_kinrath_redraw_2026-10-09/hawkbat_stage1_master_sn.json). Art generation, runs in artpipe daemon. Plates/wing poses (stage 2) wait for S/N masters; NOTE study says Hawkbat membranes cover the torso, so plate-removal may not suit it - decide after S/N masters land.
- Sketto south wing2 regen filed: sketto_fly_wing2_v2_south (derive_from sketto_fly_master_v3_south, head-locked prompt); row: Transient/sketto_pilot_2026-10-08/stage2_south_wing2_v2.json.
