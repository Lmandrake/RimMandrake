# Preserve active Cauldron combustion on reload and contain sealed boundaries

Filed as stage-3 construction work from rm-role-designercodex-1794827705. Parent RIMMANDRAKE_ADMIT_CAULDRON_DESIGNER_ON_CODEX_RANKED_SECOND remains the design task. No build, live execution, deploy or restart is performed by this filing.

## Spec

Connected combustion over water with contained propagation and actual goods displacement. Provide flame-front save continuity and validate sealed diagonal containment as well as straight barriers. Match the installed candidate to repeated combined live scenes after the offline chain fix.

Approved requirements: connected_gas, explosive_displacement. Read design/concepts/Cauldron/tree.json and the complete named contracts in design/concepts/Cauldron/scenes.json. Source basis: src/RimMandrake/Cauldron/Source/RM_VentGas.cs, src/RimMandrake/Cauldron/Source/Kernel/RM_VentGasKernel.cs, src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackCompat.cs.

## Verify

Single-spark ground/water lanes, a maintained gas gap, straight/diagonal sealed controls, mid-chain reload, smoke/instigator readback and identified goods displacement.

Scene entry points owed or consumed:

- gas_transport: src/RimMandrake/Cauldron/validation.py::scene_gas_transport
- gas_chain: src/RimMandrake/Cauldron/validation.py::scene_gas_chain
- gas_displacement: src/RimMandrake/Cauldron/validation.py::scene_gas_displacement
- gas_warden_interaction: src/RimMandrake/Cauldron/validation.py::scene_gas_warden_interaction

## Criteria

- The named scene starts, actions, expected observations and controls in scenes.json are executed against the identified running candidate. Required reads that cannot answer return UNMEASURED with a named cause; they never pass from source declarations or historical receipts.
- Connected combustion over water with contained propagation and actual goods displacement.
- Before any persistent mutation record scene-begin and the exact saved-state/settings recovery; successful and interrupted restoration compare the entry manifest, then scene-end, or use an explicit scene-hold for review.
- Changes receive their smallest meaningful offline can-fail checks before runtime acceptance. Do not run a long soak or unattended aerial-motion hunt.

## Interdependencies

FlowWorks owns transfer/process mechanics and liquid identity; EnvironmentalHazards owns shared contact/paralysis; CreatureBehaviors owns tether/track services; ExplosiveKnockback owns displacement. Preserve optional VEF and Utinni guards. Canonical composed Biomes packaging must be fingerprinted. Historical chain passes are scoped and stale, and source work cannot certify the current loaded candidate.

Retain RIMMANDRAKE_FIND_WHY_GAS_CHAIN_STOPS_FIVE_OF_SEVENTEEN as the earlier intermittent-chain history; this item adds the explicit active-front save and straight/diagonal containment obligations. It neither supersedes nor closes that item.
