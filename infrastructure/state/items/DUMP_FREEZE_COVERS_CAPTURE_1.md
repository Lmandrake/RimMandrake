## spec
🔴 **The frozen official dump has already been replaced, and nothing announced it.**

`infrastructure/state/dumps/REGISTRY.jsonl` freezes `OFFICIAL-2026-08-20` at
`capturedUtc 2026-08-20T15:08:30Z`. The dump on disk is `2026-08-21T08:20:20Z`.
⚠️ Both are **578 mods**, which is why it went unnoticed — the mod count was the
only quantity the frozen branch compared, and it had not moved.

✅ Detection shipped 2026-08-21: `refresh.py` compares the registry's
`capturedUtc` against the manifest's and reports **`REPLACED`** on the board.

⛔ **Resolving it is the owner's, and an agent must not re-freeze to clear the
warning** — that is exactly how a design target moves without anyone deciding.

The three options, written out in `infrastructure/state/queue/HUMAN.md`:
  (a) re-freeze to the 08-21 capture (new entry, new id)
  (b) restore the 08-20 capture, if it was chosen for a reason not visible here
  (c) drop `frozen: true` until the mod list stops moving

🔑 Context for the choice: the 08-21 capture is what everything on 2026-08-21 was
measured against, and it is the one that exposed the 824-def collision loss. It is
better evidence than the 08-20 one, not worse.

⚠️ **Already settled and needing no decision:** the freeze covers the CAPTURE only
(`manifest.json`, `defs/**`, `animals.json`). `defs.sqlite` is derived, deterministic
and rebuilt in ~60 s, so it sits inside the frozen path and outside the freeze.
Full ruling at the top of `infrastructure/state/dumps/README.md`.

## verify
`python3 src/RimMandrake/Utils/refresh.py` shows `DefDump/ (live)` as something
other than `REPLACED`, and `python3 src/RimMandrake/Utils/selftest_frozen_dumps.py`
stays green.

## criteria
the registry's frozen entry and the capture on disk describe the same capture, by
the owner's deliberate choice rather than by an agent clearing a warning.

## notes
Filed by BUILD 2026-08-21 after the owner asked which representation of a dump is
frozen. The ruling is implemented; only the pre-existing mismatch is open, and it
is the owner's by the registry's own rule that only he re-freezes.
