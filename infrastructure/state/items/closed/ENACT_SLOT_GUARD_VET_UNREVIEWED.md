# ENACT_SLOT_GUARD_VET_UNREVIEWED

This is an independent review of the ENACT_SLOT_PICK_VERIFY_MEMBERSHIP change to
`src/RimMandrake/Utils/art/enact.py` (`build_plan`, schema-2 slot loop). The author self-reviewed it and left the
file DIRTY on purpose.

What changed:
- A slot pick is refused, by name in `conflicts`, when its slot key is a lane of the snapshot but the letter is not
  that lane's. "Not that lane's" means `gof_resolved != slot` and `assign[letter] != slot`.
- The same letter is also dropped from the lane that `decision` routes it to, unless a slot of that lane picks it
  itself.
- An unknown (stale) slot key is not checked. That gap is ENACT_STALE_SLOT_KEY_MIGRATE_PATH.

Census: 0 of 385 real non-migrated slot picks would be refused (362 match graphic_of, 11 match through assign, and
12 carry a stale key that is not checked). Migrated slots (561) are skipped by enact anyway. Evidence is in
`D:\ClaudeWork\rimmandrake\vet_hotkey_guard\census2.out`.

Selftest: `selftest_enact_slot_membership.py` has 5 cases. Run against the pre-change enact, cases 1a and 1b fail:
the young-lane Y was installed at the adult path.

Questions for the reviewer:
- Is dropping the routed decision letter right when the slot record says he meant it for another slot?
- Can a by-name render appear in a known lane of the sheet without `assign` (case 5 refuses it)?
