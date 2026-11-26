---
state: validated
needs: offline
---

# PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

A pipe-fed faucet: a fitting on a pipe (on the liquid net) that colonists drink from and fill bottles at, taking the 'tap' name RM_LiquidTap gave up (now 'bleed well'). Thirst already counts 'taps at home' as free (RM_ThirstSettings/RM_ThirstMath Q1 'piped taps'); C7's bleed-well line beside a pipe is the natural staging spot. Background: joints study D6, Transient/pile_2026-10-22/joints_study.md, shot joints/sheet_E.jpg

Built at `31f0455f60be` (origin/main); code is in, what is owed is below.

## what is left

- A3

## latest ledger notes

- 2026-10-29: Conductor triage 2026-10-29: FAUCET_REDRAW_BORROWED_BLEED_WELL is done, so the placeholder can go. Judge and install the faucet art (§1 art), deploy, then stage a faucet on a pipe. The L4 look stays his (delegation_policy §2.1, L4 is his by definition) and rides the one FlowWorks/water look-sitting card in conductor/owner_cards_2026-10-29.md; FOUNDRY stages, then needs owner.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE` first: another commit may already do it.
