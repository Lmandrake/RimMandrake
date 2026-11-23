---
state: built
needs: game-up
---

# REEL_LINK_FIX_IGNORES_THE_OBVIOUS_PORT

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Walk save e: reel-to-reel hose connected from the left reel's NORTH connector to the right reel's WEST side, over its handle, ignoring its obvious hose connector; east reel to central reel refused 'no room to attach' though the central reel has an open port on its right. Screenshot /mnt/c/Program Files (x86)/Steam/userdata/40784075/760/remote/294100/screenshots/20261023063407_1.jpg

Built at `89e2ed65196a` (origin/main); code is in, what is owed is below.

## what is left

- A2

## latest ledger notes

- 2026-10-29: Triage 2026-10-29 (Conductor, owner asked 'do they REALLY need the owner?' OWNER.jsonl:1793249976108175484): NOT his. FlowWorks is FOUNDRY's since the v3 cutover (OWNER.jsonl:1793237487747651280). The owed A2 is an objective visual check of a bug he reported, which an agent can stage and judge: reload save e (or a quicktest with the same layout), take a zoomed capture of the named spot, have a naive Opus judge it against A2's words, and record verify at L3 with the capture as evidence. Under 'no

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify REEL_LINK_FIX_IGNORES_THE_OBVIOUS_PORT --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=REEL_LINK_FIX_IGNORES_THE_OBVIOUS_PORT` first: another commit may already do it.
