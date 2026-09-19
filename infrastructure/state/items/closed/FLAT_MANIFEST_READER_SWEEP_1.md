# FLAT_MANIFEST_READER_SWEEP_1 — audited the 10 named candidates: zero silent readers remain

Filed 2026-08-29T12:56:58Z. Spec named 10 files a grep hit for "manifest": `artifact.py`,
`apparel_tag_audit.py`, `animal_live_diff.py`, `cast_to_xml.py`, `check_refs.py`,
`def_inventory.py`, `check_load.py`, `def_diff.py`, `extract_bundle_textures.py`,
`dump_projection.py`. Ask: for each, does it resolve the manifest itself or via a helper,
does it fail loud or silently degrade; fix silent ones; prefer one shared resolver.

## Audited all 10. None are silent. Most are already the fix.

| file | resolution | verdict |
|---|---|---|
| `apparel_tag_audit.py` | `game_paths.DEF_DUMP` (the shared, already-correct newest-capture resolver) | clean |
| `check_load.py` | `game_paths.DEF_DUMP`, plus its own staleness check vs ModsConfig.xml mtime | clean |
| `dump_projection.py` | `sqlite_path()` explicitly walks UP out of `captures/<id>` to find `defs.sqlite` at the DefDump root — the most robust of any resolver here, and the one this item's own spec implicitly wants everyone using | clean — this IS the reference implementation |
| `cast_to_xml.py` | its own `_resolve_dump()`: tries the path directly, then `<path>/defs`, then newest `captures/*/defs` by reverse-sorted name, prints which capture+modCount it picked, `die()`s loud if none resolve | clean, independently correct |
| `animal_live_diff.py` | requires explicit `--live` (no default), `sys.exit()`s loud if `animals.json` is absent | clean — no silent path to have |
| `def_diff.py` | requires explicit `--live` (no default), `sys.exit()`s loud if `defs/` is absent | clean — same shape |
| `artifact.py` | `sha_of`/`defnames_in` take a caller-supplied `path`, no default, no auto-guess at all | clean — not this bug's shape |
| `def_inventory.py` | this is the offline dump **writer**, not a reader of an existing DefDump capture | not applicable |
| `check_refs.py` | its "manifest.json" hit is a doc-reference-checker's list of generic filenames to exclude from broken-link reporting — nothing to do with DefDump | not applicable, grep false-positive |
| `extract_bundle_textures.py` | its "manifest.json" is `observed/inventory/bundle_textures/manifest.json`, its OWN unrelated texture-cache manifest | not applicable, grep false-positive |

## The one real historical instance was already fixed, same day, before this item existed

`sync_mod_state.py` (`skills/rimworld-start-prep/scripts/`) is the file that actually broke —
named in the item's own spec as the trigger. Fixed in `801bd127` (2026-08-29T05:56:25-07:00):
tries the flat path, then every `captures/<id>/manifest.json`, sorts by mtime, `die()`s if
neither exists. This item was filed **~7 hours later** (12:56:58Z same day) off a grep that
did not check whether its hits were already fixed — the same pattern as
`AUTHORED_FACTION_RAID_SPAWNS_NOTHING_1` and the bills/storage half of
`PLACER_IDENTITY_REPLAY_1` earlier this session: a grep or a claim from before a fix, re-filed
without a re-check.

`validate_patch.py` is named in `cast_to_xml.py`'s own docstring as the sibling SILENT case
(`DUMP_LAYOUT_BROKE_TOOLS_1`) — also already fixed (its own `--live` resolver at
`skills/rimworld-modding/scripts/validate_patch.py:1393` walks `captures/<id>` and prints which
one it picked).

## "Prefer one shared resolver" — noted, not executed

There are now genuinely **four independent implementations** of "find the current capture":
`game_paths.DEF_DUMP` (simplest, a module constant), `dump_projection.sqlite_path()` (most
robust, walks any of 4 path shapes), `cast_to_xml._resolve_dump()`, and
`sync_mod_state.py`'s inline version. All four are currently correct and independently
verified. Consolidating them was NOT done here: every one works, a refactor changes working
code for zero behavior difference, and this item's ask was "fix silent ones" — there were
none. Flagging the duplication as a real but low-priority follow-up, not fixing it unasked.

## criteria
- [x] Every one of the 10 named files checked: does it resolve itself or via a helper, loud
      or silent.
- [x] Silent readers fixed — none existed; the two that ever were (`sync_mod_state.py`,
      `validate_patch.py`) were already fixed same-day before this item was filed.
- [x] "Prefer one shared resolver" — recorded as a real, low-priority duplication (4
      independent correct implementations), not executed as an unrequested refactor.
