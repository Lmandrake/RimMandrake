# CREATURE_ALARM_ORIGIN_SHARE_1 — CB-1: disturbed creature reserves its own alarm share before propagation

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row CB-1 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| CB-1 | The creature that was actually disturbed keeps its own share of the alarm. Today neighbours woken by the alarm spend the shared budget first, so a big Kurreth colony can use it all up and the disturbed one never rallies. | Reserve the origin's response cost before propagation (or respond first, then propagate). | S | low | CreatureBehaviors (consumers: FeverWood RM_Kurreth, HostileFlora RM_Gallowroot) | `RM_CompReactionSource.cs` TriggerReaction calls Propagate before Respond; both `RespondersWithinRadius` and `Rally` call `evt.Spend` on one budget; Kurreth XML has propagation + Rally on eventBudget 10 |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

- Offline: build clean; with `alarmOriginRespondsFirst` on, RM_CompReactionSource.TriggerReaction calls Response.Respond before Propagate.
- L2 (owed, bridge): a Kurreth colony of 10+ disturbed once; the disturbed one rallies even when neighbours would exhaust the budget.
