# SCAR_MARK_MUTUAL_EXCLUSION_1 — SC-1: Warscar and Scarlands marks mutually exclusive per pawn

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row SC-1 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| SC-1 | One scar per pawn, both ways: a pawn already carrying the Warscar mark should not also pick up the campaign's Scarlands mark (today only the Warscar side refuses the other). | the RUT mark's lock (EnvironmentalWeatherExtension.hediffToApply path) skips pawns carrying a `RM_WarscarMarkFamily`-tagged hediff — a small skip-tag field in EnvironmentalHazards, or tag-check in the lock | S–M | low | Scarlands, EnvironmentalHazards, UtinniPatches | `RM_WarscarMark.CarriesOtherMark` (one-way); closed WARSCAR_MARK_TRADE_BUILD_1 says "⚠️ One-directional: the frozen twin's lock does not yet skip RM_WarscarMark"; no live item mentions it |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.
