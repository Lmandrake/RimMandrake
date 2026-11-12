---
state: validated
needs: bridge
---

# WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Build the four approved water art candidates (option A each): canal/lake one colour, very shallow under 25 cm, wall band, darker 5 m/10 m lake tints

Built at `c5bbf3239fe8` (origin/main); code is in, what is owed is below.

## what is left

- A4

## latest ledger notes

- 2026-10-22: Triage, nothing built. (1) Sheet letter A in all four rows is the 'render rm_waterthin' 2026-10-16 column (the installed 0.5 m art), not a mock; the mocks were unlettered reference_textures, so 'option A' does not name a candidate except canal row's mock label 'A: tint'. (2) VERY_SHALLOW: already built, RM_WaterVeryShallow = VS2_faint_veil (md5 match), 1ef4a3282. (3) CANAL_LAKE: P14 one freshwater ladder (ce36444ba, 2026-10-18, after the 10-17 shots) puts dug canal water on the same base-layer t
- 2026-10-29: Conductor triage 2026-10-29: he approved option A for all four candidates; built at c5bbf3239fe8 (L1). Owed: deploy, then stage frames beside the mocks deep_T2_navy and wall_1_shadow_band so the look is one glance. The L4 look stays his (delegation_policy §2.1, L4 is his by definition) and rides the one FlowWorks/water look-sitting card in conductor/owner_cards_2026-10-29.md; FOUNDRY stages, then needs owner.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED` first: another commit may already do it.
