# ART_MARKS_BUILD_NEWEST_WINS_ARCHIVE

Owner card 2026-10-26 19:06 PDT: "May 'newest mark wins' become a delegated rule, with X moving the picture to the
art archive (one-command restore) instead of deleting it, and each act listed in your digest?" -> "Newest mark wins,
X archives (Recommended)". Recorded: canon.yml `art_marks_newest_wins_delegated`; delegation_policy.md §2.3 (third
exception). Evidence: design/RimMandrake/delegation_candidates_2026-10-26.md §3 card 2 (23 re-ask cards / 3 weeks).

## Build
- `art.py retire <sha>`: moves the picture to the art archive (bytes kept, append-only `retire` event), one-command
  restore (`art.py restore <sha>`). Never a purge; purge stays `--owner-said` only.
- Ingest/enact: his ✕ on a kept or live picture -> retire (acts now, live art included); a newer mark of his over an
  older keep -> the newer mark wins. Guard exception tied to the timestamp of HIS mark (the sheet decision's ts must
  be newer than the keep it overrides; agent marks never qualify). No re-asking card.
- Every act logged `--why "delegated: art marks"` and appears in the daily digest (§5).
- Then re-curate skills/rimworld-review-sheets (art_requirements 11, lifecycle enact line) to the built verbs.
## Verify
Selftest: ✕ on a kept live picture retires it and restore brings the bytes back byte-identical; an older mark never
beats a newer keep; an agent mark never takes the exception; digest lists both acts.
