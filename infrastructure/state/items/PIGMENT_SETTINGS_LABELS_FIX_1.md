# PIGMENT_SETTINGS_LABELS_FIX_1 — LP-4: Fix two misleading LuminousPigment settings labels

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row LP-4 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| LP-4 | Fix two misleading settings lines: the glow-tank outage slider at 0 reads "0 h before it kills" but actually means "never kills" (show "Never"); the press-gate text calls the research "hidden" though it shows locked. | label text only | S | none | LuminousPigment | `LuminousPigmentMod.cs:247,279`; `Building_GlowTank.cs:82` (0 = never); not in VERDICTS rows or items |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: Glow-tank outage slider shows Never at 0; press-gate text says locked not hidden.
