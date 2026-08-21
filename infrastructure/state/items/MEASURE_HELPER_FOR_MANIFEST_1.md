## spec
13 tools call `json.load`/`json.loads` on the def dump's `manifest.json`.
That file holds **532 `defCounts` entries under 517 distinct keys**, so the parse
silently keeps the last value — `AbilityDef` reads 0 where 612 defs were written.

🔴 **CORRECTED 2026-08-21, and the correction shrinks this item to almost
nothing: NOTHING in the repo reads a wrong number from the manifest today.**
The 532 entries sit under **517 distinct NAMES** — the duplicates repeat names
already present, so `json.load(...).keys()` loses no name, only the shadowed
VALUES. Proven by set comparison: the naive and duplicate-preserving key sets
are identical.

⇒ `validate_patch.py:1282` uses `set(counts.keys())` and is **correct as
written**. The audit that called it "the only live wrong answer, silently
dropping def types from validation" was wrong, and this item said so before
being checked. The other twelve call sites read `mods`/`gameVersion`/
`capturedUtc`/`modCount`, which the collided parse does not touch.

✅ **What is left, and it is worth doing but is not urgent:** a single seam so
the NEXT reader — the first one to want a defCounts VALUE — does not hit it, and
so `collision_report()` is one import away. That seam now exists at
`src/RimMandrake/Utils/dump_manifest.py`.

⛔ **And `validate_patch.py`'s USE of it is correct — do not "fix" it.** Verified
2026-08-21: its `live_types` filter deliberately skips def-type files absent from
the manifest because `defs/` accumulates, and all 19 such files are 126-243 hours
older than the manifest. Switching it to `read_manifest` gives it 532 names
instead of 517 without changing that behaviour.

The work: export `measure.dumpdb.read_manifest()` as the one supported way to
read a dump manifest, and switch the 13 call sites to it. One import, one call
each.

  `skills/rimworld-modding/scripts/validate_patch.py:1282`   ← keys only; CORRECT, do not "fix"
  `src/RimMandrake/Utils/mod_inventory.py:168`
  `src/RimMandrake/Utils/check_load.py:68`
  `src/RimMandrake/Utils/weapon_tag_audit.py:130`
  `src/RimMandrake/Utils/validate_ideoligion.py:92`
  `src/RimMandrake/Utils/validate_save_artifact.py:143`
  `src/RimMandrake/Utils/patch_provenance.py:131`
  `src/RimMandrake/Utils/harvest_log.py:399`
  `src/RimMandrake/Utils/ideology_palette.py:43`
  `src/RimMandrake/Utils/genome_matrix_build.py:597`
  `src/RimMandrake/Utils/def_diff.py:541`
  `src/RimMandrake/Utils/animal_live_diff.py:184`
  `skills/rimworld-start-prep/scripts/sync_mod_state.py:132`
  plus `observed/2026-08-13/dumps/capture_manifest.py:78,84`, which PRINTS
  `def types 517` where 532 entries were written — the one genuine, if minor,
  understatement, and it is in an archive directory.

## verify
a script that asks each of the 13 call sites for the AbilityDef count and
shows it is `[612, 18, 0]` or an explicit refusal, never a bare 0. Plus
`selftest_measure.py` still 26/26 and `validate_patch.py`'s own selftest green.

## criteria
no tool in the repo can read the dump manifest in a way that silently
discards a duplicate key.

## notes
Filed by BUILD 2026-08-21 from three audits run after the owner asked
whether the new instrument was actually adopted. It was not.
