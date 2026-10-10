# RECLAMATION_TRIGGER_REWIRE_WOKEN_COUNT — the Reclamation fires on a woken-ancients count, not a 45-day delay

## spec
Owner, 2026-10-10 story sitting card 13 (decision taken by question card): **the
Reclamation starts when enough ancients are woken** — a count; the number is owed
tuning. Card 12 (by question card): it is fully independent of the crater event,
either order. Recorded in `infrastructure/state/canon.yml` `rakata.reclamation_trigger_src`.

Built today (`design/Jawa/worldbuilding/vault_thaw_quest_family.md` §3 step 3, §4):
`RUT_WokenClaimRefused` → a 45-day chain delay → `RUT_GiveQuest_Reclamation`
(generator `src/RimUtinni/StructureInjectionsRUT/Source/VaultDungeons/gen_vault_quests.py`).
That trigger now contradicts the ruling and is owed a change: count the ancients the
player has woken and fire the Reclamation when the count reaches a tunable threshold
(a Mod Settings number, per the superb-settings rule). How "woken" is counted (casket
opens, V6 wake branch, `HistoryEventDef` records) is the build's call — read the
existing history events first.

## verify
- [ ] The 45-day chained delay no longer gates `RUT_Reclamation`; a woken-count
  threshold does, tunable in settings.
- [ ] Quicktest: waking N ancients (dev) fires the Reclamation; N−1 does not.
- [ ] `vault_thaw_quest_family.md` §0/§1/§4 updated from "as built" to the new build.
