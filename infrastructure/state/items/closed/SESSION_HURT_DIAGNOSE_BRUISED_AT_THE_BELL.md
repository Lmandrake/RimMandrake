---
state: built
needs: bridge
---

# SESSION_HURT_DIAGNOSE_BRUISED_AT_THE_BELL

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks live_session B3: colonists Elisa/Godders hurt mid-script (Bruise = FlowWorks Blunt fall damage, ToxicBuildup = toxic pit fill?) so GovernorStop voided climb_proof, sprinkler_live, liquid_checks L2/L4/L6; find the source (drafted colonists left on cells later scripts dig?) and fence colonists off the B3 sites

Built at `61131dde14fb` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-10-26: SteveDesktop sweep J20261026T004751Z-6e5292 still non-PASS on chain 'pit_fill_effects' (row in D:\ClaudeWork\rimmandrake\fw_sweep_triage\nonpass.tsv); re-run that chain after the fix.
- 2026-10-28: testq J20261028T222611Z-7fc22a.a1 paused the SteveDesktop lane; finding STEVE_LANE_SYNC_REFUSED_7FC22A
- 2026-10-28: testq J20261028T222611Z-7fc22a.a1 on SteveDesktop: REFUSED/SYNC, no verdict recorded (runner pull failed: hint: Diverging branches can't be fast-forwarded, you need to either: hint: hint: 	git merge --no-ff hint: hint: or: hint: hint: 	git rebase)

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify SESSION_HURT_DIAGNOSE_BRUISED_AT_THE_BELL --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=SESSION_HURT_DIAGNOSE_BRUISED_AT_THE_BELL` first: another commit may already do it.
