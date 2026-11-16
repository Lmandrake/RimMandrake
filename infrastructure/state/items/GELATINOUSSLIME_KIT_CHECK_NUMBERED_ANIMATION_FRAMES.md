# Resolve numbered Dwommo animation frames in the kit-art checker

Filed by BENCH in Designer run rm-role-designercodex-1794829244.

## refs

file: src/RimMandrake/GelatinousSlime/validation.py
file: design/concepts/GelatinousSlime/record.json
file: design/concepts/GelatinousSlime/stage2_argument.md

## spec

Extend check_kit_art.py texture resolution to recognise the existing flyingAnimationFramePathPrefix numbered rotation frame convention. Preserve ordinary bare-path/rotation/directory resolution and existing authored exceptions. Confirm the declared animation frame set, resolve actual files and reject a missing required frame. This is proof-checker delivery work, not an art replacement.

## verify

First add a private numbered-prefix fixture that fails current resolution, then missing-frame and existing-path controls. Run the current kit-art checker and its targeted offline controls. Actual in-game motion and owner art review remain separate scenes.

## criteria

- The existing RM_Dwommo_Flying_ numbered frame family resolves completely.
- A missing required frame fails the checker.
- Existing ordinary path, rotation and declared exception behaviour is preserved.
- Offline path resolution supplies no runtime movement or owner art verdict.
