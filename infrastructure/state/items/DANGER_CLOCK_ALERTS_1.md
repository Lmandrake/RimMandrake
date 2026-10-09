# DANGER_CLOCK_ALERTS_1 — DI-4: alerts for heated-suit low/empty and brine-encased smother clock

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row DI-4 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| DI-4 | The player can see the danger clock. Alerts show "heated suit low/empty while outside" and "colonist encased in brine: about N hours before smothering", plus a time-left line on the jacket. | Two Alert classes and an inspect-string change, read from state that already exists. | S | none | DivingInteraction | no Alert class in `DivingInteraction/Source/`; `RM_CompHeatedSuitBattery.CompInspectStringExtra` shows only charge %; `RM_BrineEncasement.GetInspectString` shows hours held, not time left |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

- Offline: build clean; Alert_HeatedSuitLow (<=20% charge, outdoors, Chill seabed) and Alert_ColonistEncased (hours left via RM_Building_BrineEncasement.SmotherHoursLeft), inspect lines on suit and jacket; toggle dangerClockAlertsEnabled.
- L2 (owed): low suit and an encased colonist both raise the alert on the Chill.
