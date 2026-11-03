# Judge record: Rawshade design (delegated design call, delegation_policy.md §4)

Judge: GPT via `src/RimMandrake/Utils/gpt_consult.py` (not the maker), given the doc, the three render-C images and the quoted rulings. Prompts and earlier doc versions: `D:\ClaudeWork\rimmandrake\relentless\SCALDHIDE_R1_DESIGN_NEW_CREATURE\`.

| round | NAME | DESCRIPTION | BEHAVIOUR | NUMBERS | what changed after |
|---|---|---|---|---|---|
| 1 | KEEP | KEEP | REDO | KEEP | the per-species nine-cell shade became a generic canopy in the Burn's own overhead test; a readable sign was specified for each kind of prey and for its own death |
| 2 | KEEP | KEEP | UNSURE | KEEP | footprint specified (Chebyshev r = round(0.45 × drawSize), from the measured dome width); shelter only while standing; one `Exposed` for both dive and damage |
| 3 | KEEP | KEEP | KEEP | KEEP | none |

## Final verdict (round 3, verbatim)

- **NAME — KEEP.** “Rawshade” is a plain-English grotesque description that fits the naming register.
- **DESCRIPTION — KEEP.** Matches the images: a headless, folded flesh dome, blackened upper crust, scalloped hanging rim and four slender stilt legs. The shelter trap is invented behaviour, compatible with the anatomy.
- **BEHAVIOUR — KEEP.** The revision resolves round 2’s questions: square footprint, Chebyshev distance, explicit cell coverage, no shelter while moving, and shared `Exposed` coverage for diving and damage. The fifth-input count is now correct. Armour supplies the Burn exemption; dissolution with visible slime satisfies the death and readable-sign constraints. The generic Burn canopy does not introduce creature-specific Direct Sun geometry.
- **NUMBERS — KEEP.** Provisional values support the intended role. The listed small prey fit the 0.7 limit; a 1.0 adult person exceeds it. Zero products and slime-producing dissolution fit the bans.

**Internal consistency:** No clear factual contradiction in the supplied doc. The stated drawSize range produces radius 1 and therefore a 3 × 3 footprint. This is an explicit, coarse square approximation of the dome; it should not be read as an exact silhouette measurement.