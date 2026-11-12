---
state: built
needs: game-up
---

# REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Redrawn reel (south facing, Scrapper): the laid hose's coupler draws BENEATH the reel's drawn open outlet pipe — nonsensical layering; the hose must visibly mate onto the outlet (screenshot Steam 20261023063953_1.jpg)

Built at `f2a0d6cdf884` (origin/main); code is in, what is owed is below.

## what is left

- A2

## latest ledger notes

- 2026-10-29: Triage 2026-10-29 (Conductor, owner asked 'do they REALLY need the owner?' OWNER.jsonl:1793249976108175484): NOT his. FlowWorks is FOUNDRY's since the v3 cutover (OWNER.jsonl:1793237487747651280). The owed A2 is an objective visual check of a bug he reported, which an agent can stage and judge: reload save e (or a quicktest with the same layout), take a zoomed capture of the named spot, have a naive Opus judge it against A2's words, and record verify at L3 with the capture as evidence. Under 'no

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH` first: another commit may already do it.
