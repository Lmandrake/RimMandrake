# SCRUB_PROVE_VINE_FORMS_AND_CRAFT

## spec

Implement economy_observer first; every vine-group sc_* scene assigned this item in scenes.json covers generated islands, independent capped creep/ExplosiveGrowth exclusions, actual common hazards, Dripping, Twitcher, Hollow, Crown, six/four forms and smother/fuel economy. Reuse existing forms/four_forms/islands/dripping/lash/smother/patches chains and kernels as support. Required additions include natural onset/traffic rather than direct sweeps, exact 1.5 boundary, Sleeper shared controls, young/smothered states, saved state graphics, pollution cap, autonomous Lure ingestion, Hoard identities/gear and full timing/settings migration matrix. Premium fuel compares actual rates/duration/work/energy, mixed-credit reload and capacity saturation. Crown flight portions are owner-attended. Track exact bystander IDs before cleanup, including same-form flora, pools, fruit and fires.

Design source: design/concepts/LeaningScrub/plan.md and build_items_03.md; exact per-scene contracts in scenes.json. Stage3 author rm-role-designercodex-1794799806, BENCH. This is a child proof-contract package; it does not replace or close the broader Designer intake item.

Owned entries:
- sc_island_land: src/RimMandrake/LeaningScrub/validation.py::scene_island_land
- sc_creep: src/RimMandrake/LeaningScrub/validation.py::scene_creep
- sc_vine_contact: src/RimMandrake/LeaningScrub/validation.py::scene_vine_contact
- sc_dripping: src/RimMandrake/LeaningScrub/validation.py::scene_dripping
- sc_twitcher: src/RimMandrake/LeaningScrub/validation.py::scene_twitcher
- sc_hollow: src/RimMandrake/LeaningScrub/validation.py::scene_hollow
- sc_crown: src/RimMandrake/LeaningScrub/validation.py::scene_crown
- sc_rearing: src/RimMandrake/LeaningScrub/validation.py::scene_rearing
- sc_walking: src/RimMandrake/LeaningScrub/validation.py::scene_walking
- sc_hoard: src/RimMandrake/LeaningScrub/validation.py::scene_hoard
- sc_quench: src/RimMandrake/LeaningScrub/validation.py::scene_quench
- sc_sworn: src/RimMandrake/LeaningScrub/validation.py::scene_sworn
- sc_shedding: src/RimMandrake/LeaningScrub/validation.py::scene_shedding
- sc_strangler: src/RimMandrake/LeaningScrub/validation.py::scene_strangler
- sc_weeper: src/RimMandrake/LeaningScrub/validation.py::scene_weeper
- sc_sleeper: src/RimMandrake/LeaningScrub/validation.py::scene_sleeper
- sc_lure: src/RimMandrake/LeaningScrub/validation.py::scene_lure
- sc_smother_claim: src/RimMandrake/LeaningScrub/validation.py::scene_smother_claim
- sc_cane_fuel: src/RimMandrake/LeaningScrub/validation.py::scene_cane_fuel
- sc_economy_observer: src/RimMandrake/LeaningScrub/validation.py::scene_economy_observer

## criteria

Implement every named owned scene as a real script entry, reusing validation_core/rimdrive and production kernels. Before any mutation, capture exact original save/settings/world and call scene-begin. Assert scene-specific starting state, execute normal engine scheduling/jobs wherever promised, emit a separate result for each finite variant, run its discriminating negative control, then verify full restoration/scene-end or explicit owner_review scene-hold. A helper's direct effect never accepts a natural trigger. Same-def bystander IDs must survive. Missing preconditions/log observability/tool/list/owner for flight yield UNMEASURED, never PASS. Implement injected failures for starts/control/restoration and an exception during staging; demonstrate offline that they refuse false passes and leave recovery open. No actual bridge/restart/deploy is authorized by filing.

Each item requires an offline fake-driver/contract test of start refusal, specific control failure, exact settings restoration and interrupted journal handling. It also requires later targeted actual engine evidence for its live leaves, on the declared supported list, plus owner-attended portions where required. Implementing an entry is not closing its live proof obligation. Every outstanding Stage 0 chain/auxiliary audit is mapped in `audit_disposition_03.json`; legacy helpers are never certified merely by being wrapped.


- Every owned entry exists with its asserted start, action, expected positive, distinct negative control, full recovery and correct hold.
- Offline tests deliberately break start, control, accounting or restoration and refuse false PASS.
- No live acceptance is claimed from fake-driver tests, source presence, direct helper calls or unavailable preconditions. Live evidence is later required at each declared tier.
- Product/dependency gaps remain named, including existing authorized migration; do not mark completed merely because a proof wrapper was added.

## verify

Run targeted offline contract/selftests first. Later authorized bridge driver runs the named scene entries with source/assembly/list identities and exact recovery journal; owner present for every actual-flight arm. Read scenes.json for PROVE/EXPECT/LIES and finite variants. No bridge/restart/deploy action is authorized by this filing.
