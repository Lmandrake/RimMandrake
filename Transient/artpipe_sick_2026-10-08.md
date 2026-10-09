# Artpipe "sick" diagnosis 2026-10-08

Measured from /mnt/d/Luke/dev/_artpipe/failed/*.manifest.json (mtime < 24 h) and the daemon log.

## Root causes
1. worker_error (22 still in failed/, daemon-wide ~9% of attempts, spread across all hours): codex gpt model emits the
   final JSON manifest (--output-schema) BEFORE calling the imagegen tool ("Tool call channel unavailable after schema
   emission", "premature manifest", "response-format constraint"). No image produced. Model flake, not a tool defect;
   codex_image.py already retries inside the attempt. Not quota (meter 58%, not grumpy).
   Action: requeue_flakes.py -> 22 worker_error + 8 master_failed requeued (20 master_failed remain: master still in failed/).
2. failed_canon (~30): mostly ONE failed line of 5-6 (pass-all gate). Genuine art misses (lothcat mouth, pekopeko tail,
   hawkbat membrane, dakkra fins up, owner "add variants" rows with a single plant). Grader consistent, no common wrong reference.
3. Sketto: legs line fails on master v2, plate v1, wing2/3 alike ("thick folds, not thin spindly legs"). The design
   (sketto_design_2026-10-08.md section 6) deliberately grades every frame on canon Must-show; only wings are canon_na on
   plates. The plate itself carries the legs and fails too, so the lock step cannot supply good legs: the defect is the art
   (legs), not the gate. Changing the gate is a canon-rule change: left alone.
4. HELD miasma_swarmling_green_v1_{east,north,south}: derive_from rot_swarmling_v2_{east,north,south}; done manifests exist,
   _artsrc PNGs missing (orphan_masters.py: no candidates). Owner's earlier note "make it sickly green" vs. later card
   deleting live Swarmling art (07ff006d0): owner decision needed (withdraw the 3 pending jobs, or supply a master).
