---
state: ready
needs: game-up
---

# BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Bleed well (RM_LiquidTap) and liquid drill: On/Off toggle, a visible status icon with the reason when it can't run, and a god-mode 'give this map a subsurface yield' debug action

Built at `8df1c0db13f1` (origin/main); code is in, what is owed is below.

## what is left

- A2

## latest ledger notes

- 2026-10-29: Triage 2026-10-29 (Conductor, owner asked 'do they REALLY need the owner?' OWNER.jsonl:1793249976108175484): NOT his. FlowWorks is FOUNDRY's since the v3 cutover (OWNER.jsonl:1793237487747651280). The owed A2 is an objective visual check of a bug he reported, which an agent can stage and judge: reload save e (or a quicktest with the same layout), take a zoomed capture of the named spot, have a naive Opus judge it against A2's words, and record verify at L3 with the capture as evidence. Under 'no
- 2026-11-12: Claude Whittle CLAUDE_ARCHMAGI_FWLIVE released this claim: no live item file (ledger ghost)

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY` first: another commit may already do it.
