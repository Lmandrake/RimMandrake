## spec

`art_checks.py`'s `--selftest` reads its ENTIRE corpus from
`Transient/pyrelands_art_review/art` (`REVIEW_ART`), 71 staged PNGs written
2026-09-16. `CLAUDE.md` defines `Transient/` as output a human reads once and
then bins, with a **~14-day shelf life** and the standing rule "never the only
copy of anything, and never a committed doc citing a file inside it".

So the sweep's art gate is scheduled to break on its own around 2026-09-30,
with a message that reads like a missing tool rather than a swept folder:

    FAIL  corpus missing: .../Transient/pyrelands_art_review/art (Transient has
          a ~14 day shelf life; re-staged with build_pyrelands_art_sheet.py)

The author clearly saw the risk and wrote the hint into the failure — but a test
that dies on a calendar is still a gate nobody can trust, and this suite already
had five standing failures nobody was acting on (`SELFTEST_FAILURE_TRIAGE_1`).

⚠️ **A second, subtler coupling.** `run(..., originals=True)` maps the staged
`__`-joined filenames back to the repo originals and measures THOSE, so the
staged copy is not the pixels under test — it is the **roster** of which files
get tested. That is why the 2026-09-17 art wave could invalidate five fixtures
at once while the staged folder sat unchanged: the corpus silently decides
coverage, and nothing declares it.

## verify

`art_checks.py --selftest` passes with `Transient/pyrelands_art_review/`
renamed away, and states its roster from a source that lives outside
`Transient/`.

## open

Not yet designed; three candidate shapes, none chosen:

1. **Declare the roster in-repo** — a small committed list of the mod
   `Textures/` directories under test, walked directly. Removes the staged copy
   from the loop entirely and makes new art automatically in scope. Changes what
   "the corpus" means, so the `OUTLINE_MAX_FLAGGED_FILES` cap and the 77-finding
   count would need re-measuring.
2. **Move the staged corpus out of `Transient/`** into a committed fixtures dir.
   Cheapest, but commits ~3 MB of derived thumbnails — against CLAUDE.md's
   derived-artifact rule.
3. **SKIP rather than FAIL when the corpus is absent**, the way
   `selftest_tool_metadata.py` skips on a missing DLL. Honest, and stops a
   calendar failure, but silently drops the whole art gate — the worst option if
   nobody notices the skip.

🔑 Precedent already set in this file 2026-09-18: `duplicate_facings` was
converted to a **synthetic** fixture (two copies of one sprite, plus a
one-pixel-different negative control) precisely because its corpus-derived pins
all evaporated when the art they described got fixed. The same move may fit the
other checks.
