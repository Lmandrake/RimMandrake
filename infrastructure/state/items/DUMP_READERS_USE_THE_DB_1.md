## spec
Audited 2026-08-21 after `measuring-large-artifacts` shipped. These five load a
`defs/*.json` whole where `measure` answers from `defs.sqlite`. ⚠️ **None is
broken today** — measured, `json.loads` of ThingDef.json costs 1.4 s read + 1.6 s
parse and **1.46 GB peak RSS** on a box with 33 GB free. This is cost and
fragility, not breakage, and the item should be scheduled accordingly.

  `src/RimMandrake/Utils/validate_save_artifact.py:135-205  build_index()`
      ~70 lines, and the highest value of the five. Its regex hard-codes the
      dumper's exact FIELD ORDER (`"defName":…,"defType":…,"shortHash":…`); the
      dumper changed on 2026-08-21 and any reordering silently yields an EMPTY
      index — a whole-file failure that looks like "nothing matched".
      Its `_emptyDefTypes` heuristic (`'"defs":[]' in text[:200]`) is exactly
      `coverage`, which is tri-state instead of a guess.
      🔑 Its AbilityDef-collision comment at 179-187 must MOVE with it, or the
      next reader re-derives it from scratch.
  `src/RimMandrake/Utils/gen_races_mod.py:1141-1152  verify()`
      loads EVERY defs/*.json — the only 670 MB whole-graph load left.
  `src/RimMandrake/Utils/weapon_affordability.py:171-200  load_weapons()`
  `src/RimMandrake/Utils/weapon_tag_audit.py:124-131  load_dump()`
      both hand-rebuild the tag index that `dumpdb.tag()` was written because
      of, and `tag()` returns Refused rather than 0 for a fully-cut tag — the
      "emptied by the cut: 0" bug.
  `src/RimMandrake/Utils/worldmap.py:95-113  load_hash_table()`
      19 lines, and a straight duplicate of `rimbench/savemap.py:44-63`, which
      already streams. Delete rather than port.

✅ **Already done, as the pattern to copy:** `rimflow/artifact.py:defnames_in`
(85789cf) — db first, JSON fallback when the skill or db is absent, and it
dropped 154 dead defNames as a side effect.

⛔ **Do NOT touch these — a guard that looks like a gap is usually a guard:**
  `validate_patch.py:1271-1299` live_types, and its `_dump_collisions` at
      1161-1181, which is a DELIBERATE local copy so the skill still runs on a
      machine without `measuring-large-artifacts`.
  `def_diff.py:829-838` winners — per-type ON PURPOSE ("ONE DEF TYPE AT A TIME
      is the memory contract"), and it excludes abstract/Name-only records so
      they cannot shadow a real def. A global index breaks both.
  `cherrypick_build.py:261-277` — its docstring says the IncidentDef pass needs
      a scan, not a lookup.
  `rimflow/artifact.py:judgeable()/MIN_PREFIX` — exists because the first run
      produced 1,280 phantom hits. Unmeasured by another name.
  Small readers (≤2.3 MB files): ideology_palette, genome_matrix_build,
      xenotype_check, cast_to_xml, worldmap_review, gen_races_mod:216. A
      database does not earn its keep against a 450 KB file.

## verify
each ported tool run before and after against the same dump, producing byte-identical
output, plus peak RSS and wall-clock for both. `measure` selftest still 42/42.

## criteria
no tool in the repo parses more than ~10 MB of JSON to answer a question the db
answers, and every port kept its fallback so it still runs where the skill is absent.

## notes
Filed by BUILD 2026-08-21 from the audit that followed the owner's instruction to
weave the skill in and remove what it supplants. The removals here are real but
none is urgent; the two that were URGENT (a fail-toward-success orphan bug, and
a rebuild that corrupted concurrent readers) are already fixed.
