# CATHEDRAL_MISSION_BOON_OFFERS_1 — Deniably-sourced Assailant missions + Heat-gated gravtech boons

Source: `infrastructure/state/items/CATHEDRAL_MISSION_BOON_OFFERS_1.md` (arc §3 bullet 3,
`design/Jawa/cathedral_concealment_arc_spec.md`). Criteria copied; no new scope.

Done when each line below is shown true:

- **Offer appears only at the correct stage.** Assailant mission offers appear at TOLERATED (stage 1)
  and above, never at WARY; gravtech boons only at VOUCHED (stage 2). Evidence: a selftest that drives
  the shadow blackboard's stage machine (`src/RimMandrake/Utils/gm_blackboard_shadow.py`) through
  WARY → TOLERATED → VOUCHED and reads the offer set at each poll.
- **Never attributed to the Cathedral before stage 3.** Every quest-giver / letter string for the
  missions and boons passes item 3's linter (`src/RimMandrake/RustCathedral/cathedral_arc_lint.py
  --xml <file> --stage N` or `--text`) at the stage it can appear in. Evidence: the lint run on the
  shipped def file(s), exit 0, plus a planted attributed line the linter refuses.
- **Boon availability flips with a shadow-mode Heat change.** At VOUCHED, a boon is offered when
  Imperial Heat is low and withheld when Heat is high ("when the Empire is looking, it does not act").
  Evidence: selftest rows showing one boon open at low Heat and closed after a Heat rise, same stage.
- **The dark flip closes both.** A go-dark flip (§6.1) closes missions and boons. Evidence: selftest
  row on the poll the go-dark fires.
- **Every beat completes Oracle-absent.** Fallback (prescribed) text ships for every mission and boon
  offer and the offer path needs no LLM. Evidence: the defs/text file and a run with the Oracle absent.
- **K2 anti-laundering: completing missions scrubs zero Heat.** Evidence: selftest row, Heat before and
  after N mission completions identical (Regard rises, Heat does not move).
- **Regard feedback observed in shadow logs.** A completed mission feeds Regard (item 1 input).
  Evidence: a shadow-log record showing the mission-completion Regard gain.
- **≥1 Assailant mission shape + the boon-offer gate live end to end on a quicktest.** LIVE step, not
  this offline lane: after the offline part lands, the item is noted, set needs=bridge and handed to
  BENCH for a live loop. Offline evidence owed here: the defs and C#/bridge-letter path built and
  validated on disk (`validate_patch.py`, winbuild if C#), and the exact live run recipe written.
