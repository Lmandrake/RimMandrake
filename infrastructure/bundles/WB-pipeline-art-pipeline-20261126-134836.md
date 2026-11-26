# Work bundle WB-pipeline-art-pipeline-20261126-134836

System: pipeline:art-pipeline, onboarding run of its old tickets. One member.

## Done

| member | class | outcome | commit |
|---|---|---|---|
| ART_RESOLUTION_MEASURE_AT_MAX_ZOOM | not worth the touch | dropped: answered offline (`art_maxzoom_probe.py sim --check` PASS today on a full checkout: 128 px/cell art 12.2/255 off 512 at Camera+'s 456 px/cell, 5.5/255 for 256); no decision waits on the live Camera+ floor, which is read from Camera+ source. The finding moved into the sprite skill. | 28c96b476227 (skill), c18b2bd07b66 (drop) |

## What the next context needs

- `skills/generating-rimworld-sprites/SKILL.md` no longer says that no zoom shows more than 128 px/cell. It names the
  zoom per camera mod: vanilla 83, SimpleCameraSetting 114 (both live), Camera+ defaults 456 (from source, not live).
- The claim gate refused `claim` (no `## refs`, no item prose). The drop did not need a claim.

## Next, in order

Nothing. The bundle is finished.
