# POLISH: work bundles (one line each, no ticket; beside `boundary.md`)

- risk: in `launch_remote`, a host bundle id equal to the held placeholder's id (the same second) lets `store_write` overwrite the live record.
- `holder_note` also counts blocked road-back items as "under a block with no end that sat idle"; the instructions it gives stay correct.
- Nothing writes `rec["sort_closed"]`, so an onboarding "done already" close reads `fixed` instead of `already_fixed`; both count as done.
- risk: `bundle_replay.py` holds every arrival, but the live lane never holds a Shape row (`list_dispatch.py:818`) or an onboarding run (`onboard_step` reads no hold), so the replay median overstates the live one (check of 2026-11-27, `large_bundles_check_2026-11-27.md`).
