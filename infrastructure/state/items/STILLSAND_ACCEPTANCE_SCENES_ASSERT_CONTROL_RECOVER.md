# Implement Stillsand acceptance scenes and recovery

Filed by BENCH in Designer run rm-role-designercodex-1794826273, ledger event BENCH:1794827031301434891. Parent RIMMANDRAKE_ADMIT_STILLSAND_DESIGNER_ON_CODEX_DRAFT_LEFT_UNREAD remains broader and open. This item implements the missing script contracts proposed by stage 3.

## refs

file: src/RimMandrake/Stillsand/validation.py
file: src/RimMandrake/Stillsand/northstar_site.py
file: src/RimMandrake/Stillsand/northstar_plan.py
file: src/RimMandrake/Utils/validation_core.py

## spec

Implement every planned scene_<id> function named in scenes.json in the Stillsand proof script, using the registered validation chains and shared validation_core services where correct. The exact asserted starts, actions, expectations, discriminating controls and restoration are the scene records. Every scene currently names this item as its missing entry-point/control/recovery dependency.

Implement actual read-only observation of work/jobs/reservations, item water units/booked flags, wet expiry/attraction, incident phase/draw/target/take, gale per-cell transport and boundary flux, and preservation/conversion identity/resources. Include independent visual/audio evidence where perception is the property. Exercise repeated cache lookups and absent optional service startup against real counters and source paths. Add only missing observation seams required by these contracts.

Persist scene-begin recovery before mutation. Preserve exact entry values rather than factory defaults. Snapshot and recover map/global state and settings, including held world pawns, incident queues, faith/debt/goodwill and all scene-specific state. Verify equality before scene-end. Interrupted or failed recovery remains open. Support an explicitly requested owner-review hold through scene-hold.

All listed functions are planned. Existing direct outcome/proof helpers remain component probes. Implement the normal player routes and full controls the audited chains lack. PROVE is the scene entry point/action. EXPECT is the scene expect field. LIES is its control.rules_out and cited leaf false_pass. Keep UNMEASURED distinct from FAIL and PASS, match loaded/deployed/source/list/settings identity, and maintain lossless log tap and live sentinel.

Reconcile the proposed gale measurement discrepancy as part of these new scenes. Distinguish quiet motion, conserved redistribution and externally supplied influx, with explicit conservation accounting. Preserve scope cuts and all current water consequences. Shared agricultural film integration remains later under its existing design item. The Setter binds any acceptance method in its own process.

## verify

Run the existing Stillsand offline/selftest suite plus new targeted can-fail cases for missing observations, stale fingerprints, lost/capped logs, bypassed normal actions and interrupted recovery. Each deliberately broken mechanism must fail its corresponding check. Then use an authorised later operator for targeted composed-tier normal-action scenes and their controls, with complete recovery. Verify every named entry point exists and scene contracts still validate.

## criteria

- Every planned function named below exists and implements its full scene contract, including the action/control observations that existing chains lack.
- Known positive changes appear in the observers with actual identities/ticks, and stale/missing reads and lost logs produce UNMEASURED.
- A deliberately interrupted scene restores the durable entry map/global/settings/held-pawn state, including custom settings, or leaves an explicit open recovery debt. Failed restoration cannot report successful teardown.
- Independent feature scenes pass before interaction and repeat-walk acceptance. No direct outcome helper accepts an ordinary player-action requirement.
- The proposed gale movement cases distinguish conserved motion and influx, attribute gale effects against quiet, and reject the motionless/net-delta-only and accidental-ambient false passes.
- Every present or approved inventory capability has actual exercised coverage in its assigned scene/showcase. The additional unknown giant preservation observation remains explicit.
- Actual visual/audio motion, low/high-angle sun, normal water/booked flags and real offerings retain their stated observations. A draw counter or clean log alone cannot accept them.
- soorrak_jobs live advancement uses the existing owner-attended joint-session protocol. Capability data/state reads are separate.

## entry points

- src/RimMandrake/Stillsand/validation.py::scene_existing_code_walk

- src/RimMandrake/Stillsand/validation.py::scene_observer_controls

- src/RimMandrake/Stillsand/validation.py::scene_landscape_route

- src/RimMandrake/Stillsand/validation.py::scene_harbour_secured

- src/RimMandrake/Stillsand/validation.py::scene_fortune_supply

- src/RimMandrake/Stillsand/validation.py::scene_sun_geometry

- src/RimMandrake/Stillsand/validation.py::scene_glare_cooling_mirage

- src/RimMandrake/Stillsand/validation.py::scene_buried_signs

- src/RimMandrake/Stillsand/validation.py::scene_swim_fish_thumper

- src/RimMandrake/Stillsand/validation.py::scene_giant_visit

- src/RimMandrake/Stillsand/validation.py::scene_hydration_independence

- src/RimMandrake/Stillsand/validation.py::scene_horizon_warning

- src/RimMandrake/Stillsand/validation.py::scene_gale_phases

- src/RimMandrake/Stillsand/validation.py::scene_gale_carry_return

- src/RimMandrake/Stillsand/validation.py::scene_water_cycle

- src/RimMandrake/Stillsand/validation.py::scene_pour_expiry_thumper

- src/RimMandrake/Stillsand/validation.py::scene_debt_return

- src/RimMandrake/Stillsand/validation.py::scene_cave_rows_preservation

- src/RimMandrake/Stillsand/validation.py::scene_giant_history

- src/RimMandrake/Stillsand/validation.py::scene_shade_landmarks

- src/RimMandrake/Stillsand/validation.py::scene_workshop_jobs

- src/RimMandrake/Stillsand/validation.py::scene_settings_effects

- src/RimMandrake/Stillsand/validation.py::scene_resident_ecology

- src/RimMandrake/Stillsand/validation.py::scene_soorrak_jobs

- src/RimMandrake/Stillsand/validation.py::scene_eruption_brood

- src/RimMandrake/Stillsand/validation.py::scene_campaign_encounters

- src/RimMandrake/Stillsand/validation.py::scene_salvage_fossils_scan

- src/RimMandrake/Stillsand/validation.py::scene_package_floor

- src/RimMandrake/Stillsand/validation.py::scene_walk_accept

- src/RimMandrake/Stillsand/validation.py::scene_expedition_loop

- src/RimMandrake/Stillsand/validation.py::scene_sun_work_water

- src/RimMandrake/Stillsand/validation.py::scene_gale_signs_wet

- src/RimMandrake/Stillsand/validation.py::scene_giant_death_history
