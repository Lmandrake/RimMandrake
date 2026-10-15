# TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ

Filed by BENCH 2026-10-15 (live round 7, ratchet_pilot tier, HEAD 0207ac8fc2). Evidence:
`Transient/bench_live_20261015_r7/live/river/ext_swept_site1_1.log` and `.json`.

What happened:
- FlowWorks `extension_proof --live --site river --chains swept` ran on a `river_site.py` map (tile 60145, on the Pyrelands
  fixture's world).
- The watched wait stopped after 60 of 250 ticks with `GOVERNOR_STOP hostile_arrival: arrived: AA_Bumbledrone AA_Bumbledrone
  (animal)` (vitals seq 107).
- `returns_home` read UNMEASURED "surprise". There was no damage. The row was not counted.

Class: SITE (a threat). A hostile-classified wild animal (Alpha Animals' Bumbledrone) arrived on the map in the middle of a row.
Where it came from is UNPROVEN:
- It may have been a wander-in or a manhunter incident. `river_site.py` does not apply the shared quiet-site profile
  (`quiet_site.site_profile_receipt`: storyteller off, incident queue drained), the way GSS proof_all's P3 does.
- It may have been a map-gen animal that walked in from the edge.

## guard (to build)

- `river_site.py` applies the quiet-site profile and reads its receipt back. It sweeps non-colonists once more right before
  the extension chains run.
- Before guarding, read the `pawn_origin` row of the next such arrival (same session, before any save/load). That separates
  "incident" from "already on the map".

## verify

Run `river_site.py` then `extension_proof --live --site river` (all chains) twice. Expect no hostile_arrival stop and a quiet
receipt in the site log.
