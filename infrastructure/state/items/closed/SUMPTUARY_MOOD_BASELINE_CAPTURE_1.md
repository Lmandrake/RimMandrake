# SUMPTUARY_MOOD_BASELINE_CAPTURE_1 — LP-6: Capture mood baselines from defs once, not C# copies

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row LP-6 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| LP-6 | *(hygiene)* Mood numbers for the status thoughts are copied into C# and re-stamped over the XML on every settings apply, so any XML edit or another mod's patch is silently overwritten. Read the base numbers from the defs once at startup instead. | capture baseline at load | S | low | LuminousPigment | `LuminousPigmentMod.cs` TitledMoodBase/CommonMoodBase/… duplicate `RM_SumptuaryThoughts.xml` l.25-76 |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: Mood base numbers read from ThoughtDefs at startup; settings apply scales from the captured baseline; no hardcoded duplicates.
