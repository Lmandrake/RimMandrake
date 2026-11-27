# Polish beside `design/specs/2026-11-19-clean-means-promises-tested/boundary.md`

- `src/RimMandrake/Utils/code_review_status.py` `code_files`: a page's `Code:` sentence cannot name a file at the repo
  root that has no extension. The bare `now` is skipped (no `/`, no extension). `./now` is kept unnormalized as
  `./now`, so `check now` reads NO PAGE although `design/specs/2026-11-27-now/boundary.md` names the wrapper. Normalize
  each kept token (`os.path.normpath`), and accept a bare token that is a file at the root. Seen 2026-11-27 by the
  fresh read of ceab7b4958.
