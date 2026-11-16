# Make Cauldron metal load persist until normal advanced medical purge

Filed as stage-3 construction work from rm-role-designercodex-1794827705. Parent RIMMANDRAKE_ADMIT_CAULDRON_DESIGNER_ON_CODEX_RANKED_SECOND remains the design task. No build, live execution, deploy or restart is performed by this filing.

## Spec

Persistent positive load and a playable advanced-medicine purge, including existing saved traces. Replace natural clearance with persistence and provide normal medical treatment. Account for visible and hidden traces and the reused operation failure behavior.

Approved requirements: persistent_metal. Read design/concepts/Cauldron/tree.json and the complete named contracts in design/concepts/Cauldron/scenes.json. Source basis: OWNER:1794373071501926623, src/RimMandrake/Cauldron/Defs/HediffDefs/RM_VentMetalLoad.xml.

## Verify

Observe actual exposure, recovery, departure, reload, ordinary-care control and a completed advanced purge with ingredient use.

Scene entry points owed or consumed:

- metal_purge: src/RimMandrake/Cauldron/validation.py::scene_metal_purge
- lasting_health_work_interaction: src/RimMandrake/Cauldron/validation.py::scene_lasting_health_work_interaction
- resume_walk: src/RimMandrake/Cauldron/validation.py::scene_resume_walk

## Criteria

- The named scene starts, actions, expected observations and controls in scenes.json are executed against the identified running candidate. Required reads that cannot answer return UNMEASURED with a named cause; they never pass from source declarations or historical receipts.
- Persistent positive load and a playable advanced-medicine purge, including existing saved traces.
- Before any persistent mutation record scene-begin and the exact saved-state/settings recovery; successful and interrupted restoration compare the entry manifest, then scene-end, or use an explicit scene-hold for review.
- Changes receive their smallest meaningful offline can-fail checks before runtime acceptance. Do not run a long soak or unattended aerial-motion hunt.

## Interdependencies

FlowWorks owns transfer/process mechanics and liquid identity; EnvironmentalHazards owns shared contact/paralysis; CreatureBehaviors owns tether/track services; ExplosiveKnockback owns displacement. Preserve optional VEF and Utinni guards. Canonical composed Biomes packaging must be fingerprinted. Historical chain passes are scoped and stale, and source work cannot certify the current loaded candidate.
