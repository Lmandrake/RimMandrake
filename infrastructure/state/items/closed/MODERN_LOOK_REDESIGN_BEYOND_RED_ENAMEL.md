---
state: proposed
needs: offline
---

# MODERN_LOOK_REDESIGN_BEYOND_RED_ENAMEL

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Whole art review of the FlowWorks Modern style: every Modern texture (pipes, hoses, pumps, sprinklers, containers, joins, couplers, cords) as real present-day products, not red enamel / primary colours (walk screenshot Steam 20261023064203_1.jpg: Modern solid pipe)

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show MODERN_LOOK_REDESIGN_BEYOND_RED_ENAMEL` history before building.

## latest ledger notes

- 2026-10-23: Pass 1 done: style guide design/RimMandrake/flowworks_modern_style_2026-10-23.md (98-texture inventory, refs, palette, Industrial=brutalist split -> INDUSTRIAL_BRUTALIST_AUDIT_POUR_THE_CONCRETE). 13 candidate textures (pipe atlas+icon, 5 joins, span, faucet, sprinkler, pump with connectors at the 0.136-cell pipe width, hose coupling+mouth) in Transient/modern_style_20261023/cand_r3, NOT installed. Art-eval runs modern_style_20261023(_r2,_r3): 0 ACCEPT; by r3 Opus calls pipe/pump/faucet/sprinkler
- 2026-10-23: In-game pass (bridge run 1 captures, art-eval run modern_style_20261023_r4_ingame, specs Transient/modern_style_20261023/specs_r4): 0 ACCEPT, nothing installed. Pump/pipe/joins ESCALATE (round cap), hose end REGEN r3 (its findings are placement/capture, not texture), faucet/sprinkler/span HOLD_INPUT (never seen in game). Before/after: Transient/modern_style_20261023/before_after_ingame_br1.png. Follow-ups MODERN_FIT_REDRAW_ROUND_FOUR_PENDING (owner) and MODERN_FITTINGS_PROBE_FAUCET_NEVER_SEEN (b
- 2026-10-29: Done when: each of the 13 candidate Modern textures is ACCEPT in the art-eval pipeline in game and installed; none reads as primary-colour enamel.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify MODERN_LOOK_REDESIGN_BEYOND_RED_ENAMEL --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=MODERN_LOOK_REDESIGN_BEYOND_RED_ENAMEL` first: another commit may already do it.
