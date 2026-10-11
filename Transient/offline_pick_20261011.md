# Offline pick 2026-10-11 — RECLAMATION_TRIGGER_REWIRE_WOKEN_COUNT

Seat FOUNDRY. Item: the Reclamation fires on a woken-ancients count, not a 45-day delay
(owner card 13, 2026-10-10).

## Stale-default check
origin/main 15b23e414: `RUT_VaultClaimConflict` still chained `RUT_GiveQuest_Reclamation`
45 days after `woken.AllEnemiesDefeated`; no counter existed anywhere in `src/`. Not done.

## Build
- `Source/VaultDungeons/WokenAncientsKernel.cs`: pure counting rule (no Verse), so the
  selftest compiles the real file.
- `Source/VaultDungeons/GameComponent_WokenAncients.cs`: every 250 ticks reads every
  `AncientCryptosleepCasket` on every map; a casket that held living humanlike
  Ancients/AncientsHostile pawns and is now empty while standing adds them to the count.
  Destroyed-with-sleepers = LOOT, counts nothing. At threshold fires
  `RUT_GiveQuest_Reclamation` once (retries if no home map). Saved: count + fired flag.
  Dev actions: Quests → "Reclamation: add one woken ancient" / "log woken count".
- Settings: `reclamationByWokenCount` (on) + `reclamationWokenThreshold` slider 1–60,
  default 10 (PROVISIONAL; the number is owed tuning per the ruling).
- `gen_vault_quests.py`: the delay + incident are gone; the claim conflict ends Success on
  the refusal. `RUT_VaultThaw.xml` regenerated (only that hunk changed).
- `vault_thaw_quest_family.md` §0/§1/§3/§4/§7 and `canon.yml` updated to as-built.
- `validation.py` suite.toggles gains `reclamationByWokenCount`.

## Proof
`python3 src/RimMandrake/Utils/selftest_reclamation_trigger.py` — static half (XML has no
Reclamation chain, incident exists, Compile list, settings fields) + C# kernel half 15/15
(seed, eject count, count-once, loot not counted, N fires / N-1 not, once, toggle off).
`winbuild.py` builds the mod DLL clean (0 warnings). `modcheck lint` 0 FAIL.

## Outstanding
- Criterion 2 (quicktest: waking N ancients fires, N-1 does not) needs the game: use the
  dev action, or open real caskets on a V6 site map.
- The threshold number is the owner's to tune.
