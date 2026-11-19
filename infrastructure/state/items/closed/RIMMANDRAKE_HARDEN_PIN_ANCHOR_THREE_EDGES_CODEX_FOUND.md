## spec
designer_stage.input_changes / close_run / repin (e881b97715). Codex reported (D:\ClaudeWork\rimmandrake\conductor\remote_landings_20261118\codex\e881b97715.review.md): (1) the
anchor is HEAD at close, before land_state commits the accepted bytes, and the window starts at the FIRST occurrence of
the pinned hash at or after it, so B->A->C landed after the anchor lets B escape; the docstring promises UNMEASURED for
"an anchor that does not carry the pinned hash" but the code only refuses when the hash is in no commit of the window
(confirmed here by reading designer_stage.py ~2240-2290, not run); (2) a shallow clone where the anchor resolves but
`git log anchor..HEAD` is cut returns a partial list; (3) a failed rev-parse at close writes no pinned_at, i.e. a new
pin that behaves as a legacy one. (4, pre-existing) a failed blob read hashes as absence. Likelihood is low (land_state
commits right after close); the docstring overclaim is real.

## verify
Acceptance test: none yet, the reproductions are Codex's in-memory ones; the builder writes one failing case per edge in selftest_designer_repin.py first and watches each fail.

## criteria
- Each edge returns UNMEASURED (None, why), never a shorter list; the docstring says what the code does.
