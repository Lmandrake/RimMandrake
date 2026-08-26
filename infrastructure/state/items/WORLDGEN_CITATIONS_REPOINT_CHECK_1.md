# WORLDGEN_CITATIONS_REPOINT_CHECK_1 — done 2026-08-26, seat CHECK

Both CHECK-owned citations from the 2026-08-23 archive split were traced and repointed.
⚠️ **The split is no longer the whole story:** both archive files were **deleted whole** at
`892beac2` (2026-08-26), so repointing at the archive PATH — which is what the item's spec
told me to do — would have produced a second dead citation. Every repoint below names the
git rev instead.

| citation | cited target | verdict | repointed to |
|---|---|---|---|
| `items/C17.md` §spec | `WORLDGEN_FACTION_CHECKLIST.md` Sections 1–3 + R1/R2/R4/R5, "21 untick / 6 keep" | **GONE** — split at `c4455458`, archive deleted at `892beac2` | `git show 892beac2^:infrastructure/state/archive/WORLDGEN_FACTION_CHECKLIST_ARCHIVE.md`, plus the correction that the 21 unticks are moot and KEEP is **4**, not 6 |
| `items/MUTATORS_LANDMARKS_INTO_PAINT_1.md` §verify | `WORLDPAINT_REHEARSAL.md` §6, strings 6b/7/7b/8 | **GONE** — same two commits | `git show 892beac2^:infrastructure/state/archive/WORLDPAINT_REHEARSAL_ARCHIVE.md` §6 |

Cited by section, never by line number — the trap the spec named, and the one that broke
`load_session.py`.

## And the reverse direction, which the spec did not ask for

Both live files' headers still said **"Nothing was deleted."** That was true on 2026-08-23
and false from `892beac2` onward, so a reader arriving at either header was being told the
moved sections were safe in a file that no longer exists. One correction line added to the
top blockquote of **both** `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md` and
`infrastructure/state/WORLDPAINT_REHEARSAL.md`.

## Not mine, still open

`D-CRIT` and `D10` carry the identical unrepointed citation and are **DECIDE's** — named in
`c4455458`'s own commit message. Already filed as `WORLDGEN_CITATIONS_REPOINT_DECIDE_1` — left alone, not re-filed.
