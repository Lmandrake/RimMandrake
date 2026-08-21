# REFMATCH_THRESHOLDS_CALIBRATE_1 — the globes were approved, so refmatch can be built

> 🔴 **STOP — 2026-08-21, BUILD. This item's premise collides with a named owner ruling
> it does not cite: `canon.yml > ORTHO_GLOBE_MAP_ACCEPTED_1`, ruled by the owner
> 2026-08-20 and committed at `977aa75`:** *"Let's go with the globe map you made for v1.
> Map accepted."* ⇒ *"`REFERENCE_MATCH_HARNESS_1` (refmatch.py, the five defect screens)
> is MOOT for v1 … ⛔ Do not build it for v1."*
>
> The quote below — *"Yes, I like your new globes. Well done."* — is 92 minutes LATER and
> is the WEAKER of the two, as this item's own spec says: approval of the RENDERING, not
> a finding about the world. **Liking a rendering does not reverse "do not build it."**
> ⇒ **`refmatch.py` was NOT written.** Blocked on the owner; one sentence settles it.
> Evidence: `infrastructure/state/observed/build/REFMATCH_THRESHOLDS_CALIBRATE_1_offline.txt`

## spec

🔴 **OWNER, 2026-08-21: "Yes, I like your new globes. Well done."** He looked at
`TRANSIENT_refmatch_globes.html` — Ash'karr as three orthographic globes (day face,
terminator, night cap) beside the two tidal-lock reference photographs, all at the same
size.

**That look was the gate.** `CANON_RULINGS_OWED_OWNER_1` recorded that *"`refmatch.py`
cannot be built until you have looked, because its five defect thresholds are calibrated
against those photographs, not chosen."* ⇒ **The block is lifted. Build it.**

🔑 **"I like them" is approval of the RENDERING, and that is what it is worth.** It says
the orthographic view is the right instrument and the current world reads acceptably
through it. ⛔ It is **not** a ruling that the world has zero defects, and it must not be
quoted as one — the whole point of `refmatch.py` is to find defects the eye passes over.
The five thresholds are still calibrated against the photographs, not against his
approval.

⚠️ **The globe view is now the binding one.** Every earlier view was equirectangular,
which is why compass-circle artefacts survived so long — they are invisible in the
projection everyone was looking at. Any future "does the map look right" check renders
globes, per `CLAUDE.md`'s *iterate by LOOKING* rule and
`design/Jawa/worldbuilding/the_one_map.md`.

⛔ **This is not a generator and must not become one.** Per the owner's 2026-08-18 ruling
there is ONE map. `refmatch.py` MEASURES the one world against reference photographs and
reports. It does not propose alternatives, sweep parameters, or expose a knob that could
roll a second planet.

## verify

- `refmatch.py` runs against the current world and reports all five defect classes with a
  number each, not a verdict.
- Each threshold cites the reference photograph and the measurement behind it. A threshold
  with no citation is not calibrated, it is chosen — and that is the failure mode this
  item exists to avoid.
- Re-running on an unchanged world reproduces the same numbers exactly.
- It contains no code path that emits an alternative planet.

## criteria

Five thresholds, each traceable to a photograph, measuring the one map — built now that
the instrument has been approved.
