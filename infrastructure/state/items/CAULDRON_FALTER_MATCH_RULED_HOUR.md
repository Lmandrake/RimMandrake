# Reconcile Cauldron falter with the ruled one-hour warning

Filed as stage-3 construction work from rm-role-designercodex-1794827705. Parent RIMMANDRAKE_ADMIT_CAULDRON_DESIGNER_ON_CODEX_RANKED_SECOND remains the design task. No build, live execution, deploy or restart is performed by this filing.

## Spec

About one in-game hour from the readable falter to full bloom. Reconcile the 4000-tick transition-derived falter with the nominal 2500-tick owner target. Record cue timing, bloom onset and first-dose timing independently.

Approved requirements: falter_warning. Read design/concepts/Cauldron/tree.json and the complete named contracts in design/concepts/Cauldron/scenes.json. Source basis: OWNER:1792108481222070856, src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs.

## Verify

Default-duration run with asserted start weather, onset ticks, eligible native behavior and a normal-transition control.

Scene entry points owed or consumed:

- falter_hour: src/RimMandrake/Cauldron/validation.py::scene_falter_hour

## Criteria

- The named scene starts, actions, expected observations and controls in scenes.json are executed against the identified running candidate. Required reads that cannot answer return UNMEASURED with a named cause; they never pass from source declarations or historical receipts.
- About one in-game hour from the readable falter to full bloom.
- Before any persistent mutation record scene-begin and the exact saved-state/settings recovery; successful and interrupted restoration compare the entry manifest, then scene-end, or use an explicit scene-hold for review.
- Changes receive their smallest meaningful offline can-fail checks before runtime acceptance. Do not run a long soak or unattended aerial-motion hunt.

## Interdependencies

FlowWorks owns transfer/process mechanics and liquid identity; EnvironmentalHazards owns shared contact/paralysis; CreatureBehaviors owns tether/track services; ExplosiveKnockback owns displacement. Preserve optional VEF and Utinni guards. Canonical composed Biomes packaging must be fingerprinted. Historical chain passes are scoped and stale, and source work cannot certify the current loaded candidate.
