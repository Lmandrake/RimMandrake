# ART_SHEET_REDESIGN_FRESH_OR_REFUSE

**Owner, 2026-10-12 (verbatim):** "We need to deeply reconsider how the art sheets are handled. Even in this reduced
setting of the Experiment, it's failing. I'm not sure what to do about it yet, but it needs some kind of hook or
ensurance that it's not serving stale information. By construction, by design, by hashes, by hooks, I'm not sure. But it
must be improved in freshness guarantee. File this for post-Wednesday. I don't want to spent tokens on it right now, but
it's a very high priority for Wednesday night."

**When:** Wednesday 2026-10-14 night, after the 16:00 PDT account reset. Spend no tokens on it before then.

**Triggering incident (2026-10-12):** the GSS owner-walk art sheet of 2026-10-11 (built 3c5e33d5c7, 14:56 PDT) showed
the pre-v3 power-tap clamp as "what the game shows now": the image was a 2026-10-03 render keyed on the pre-rename
texPath `RimMandrake/MessyConduit/Aerial/TapClamp` plus a 2026-10-04 def dump. The owner's v3 pick C was installed
3 h after the build (737b796e6f), so the sheet served a superseded, already-ruled row. Its header also reported
"4 decided" while 3 of the 4 were agent prefills. The sheet passed the existing scaled_review_gate stamp anyway — the
gate checks the sheet's form, not the freshness of its images. A same-day point fix to the generator (BENCH subagent,
2026-10-12) is not this redesign.

**Design space to weigh (not decided):** a content hash of every displayed image's source (texture on disk, def
texPath, def-dump fingerprint) stamped into the sheet; refuse to serve when any hash no longer matches (serve_gated.py
checks on every page load); a hook on `art install` that invalidates or rebuilds every sheet citing that def; rows
already ruled leave the to-decide set automatically; "decided" counts only owner provenance, never prefill.
