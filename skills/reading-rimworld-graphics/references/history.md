# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds evidence and the old lines that are no longer true. Git holds the rest.
Each line below is a record, not a rule. Every correction below is of 2026-11-23.

## Evidence

- Vanilla questions from the Laptop, measured 2026-09-15. The question was if vanilla animals use the pawn convention
  (south faces camera, north faces away) or a top-down orientation, and if the base game is internally consistent. The
  Laptop could only reach donor mods: `SWBestiary`'s 190 three-facing sets. They are evidence about donor practice.
- The donor corpus settled the shape question. Norths cluster at 0.96–1.00 mirror symmetry, with occasional shipped
  errors such as Nuna's inverted beak.
- The 190-plant measurement (69 needed a missing rung) is of 2026-08-22. Full record:
  `infrastructure/state/evidence/TEXTURE_RESOLVER_MISSES_TWO_FORMS_1.md`.
- A single spawned pawn settled the icon question after an entire file-based analysis reached the wrong conclusion twice.

## Old lines that are no longer true

- `resources.assets` was once on "the Windows machine" only. Two Windows machines have an install now: Archmagi (ArchBig
  and ArchSmall) and SteveDesktop.
- `validate_patch.py` (2026-09-20): once a mod shipped its own `Textures/Things/` root, the checker treated `things/` as
  that mod's namespace and escalated a correct vanilla texPath to ERROR. `own_parent_exists`
  (VALIDATE_PATCH_TEXPATH_CLASSIFIER_1) now compares the whole parent folder. `vanilla_uses` (2026-10-07) accepts a path
  that a Core or DLC def uses.
- "Every entry" of the plant manifest once carried a `variant` field. The regression case has `missing` and `why`.
- The bundle ladder was once told to try side suffixes for every def. `dir_hint=True` now limits a directory class to the
  letter forms.
- "The def dump carries no `drawSize`." The dumper writes Vector2 and Color fields since DUMP_DRAWSIZE_CAPTURE_1
  (2026-08-30). Read in two captures of 2026-11-23: the field is there. The frozen `official` dump was not read.
- The code sample once saved each texture as `m_Name`, and called `m_Name` the handle to match on. The section after it
  forbids that.
- The own-mod rule once read as a rule of the whole resolver. `resolve_texture()` ranks the own mod
  first in two bundle rungs, and second in the bundle-directory rung.
- `no_loose_png` once meant only that no loose file matched. It now also means that no bundled texture matched.
