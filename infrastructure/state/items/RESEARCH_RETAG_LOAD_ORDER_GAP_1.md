## spec
Found by a code-review pass (2026-09-04) while marking `src/RimUtinni/
ResearchRetag/` clean. Its own `About.xml` description says "load after
every research-adding mod" but nothing enforces that — no `forceLoadAfter`
in `About.xml`, no `LoadFolders.xml` entry pinning it late. Contrast with
`src/RimUtinni/FactionSlate/About/About.xml`, which has exactly this problem
(patches faction defs owned by other mods) and fixes it with an explicit
`forceLoadAfter` list.

`RUT_ResearchRetag.xml` carries 269 `PatchOperation`s (185 techLevel, 103
baseCost, 113 prereq lists) targeting `ResearchProjectDef`s owned by dozens
of other mods (confirmed real, live-loaded targets against the
2026-09-04T02-23-44Z def dump — e.g. `ABF_ResearchProject_Synstruct_
CoreAssistants`). Every one of those operations is a `PatchOperationConditional`/
plain `xpath` op with no `<nomatch>` reporting — CLAUDE.md's own doctrine:
"A patch that matches nothing logs nothing." If RimSort's load order ever
puts ResearchRetag BEFORE the mod that owns a targeted def, that def simply
does not exist in the XML tree yet, the patch silently no-ops, and the
retag is lost for that def with zero error anywhere.

Scope: give ResearchRetag the same protection FactionSlate already has —
either a `forceLoadAfter` list (the mods it owns targets in) or a
late-load convention already used elsewhere in this repo (check `About.xml`
`loadAfter`/`forceLoadAfter` patterns in other RUT_/RSW_/RM_ retag-style
mods first, don't invent a third convention).

## verify
- Build the target-mod list from `RUT_ResearchRetag.xml`'s own patch
  targets (extract owning mod per defName from the current live def dump,
  same method the review used) and confirm every one of those packageIds
  appears in `forceLoadAfter`.
- `validate_patch.py` still reports the same clean baseline (269/269
  1-match) after the change — this is metadata-only, not a content change.
- Regression: re-run `deploy_custom_mods.py --mod ResearchRetag` and
  confirm it stays "in sync" after deploying the `About.xml` edit.

## criteria
- ResearchRetag can no longer silently lose a retag to load order, the same
  guarantee FactionSlate already has for its own patch set.
- No change to `RUT_ResearchRetag.xml`'s actual patch content — this is a
  load-order/metadata fix only.
