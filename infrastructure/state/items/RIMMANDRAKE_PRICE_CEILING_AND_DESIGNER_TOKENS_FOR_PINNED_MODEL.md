## spec
Found 2026-11-19 by RIMMANDRAKE_PIN_MOD_MODEL_FABLE_EVERY_STAGE_ROLES_OPUS, which scales a pinned mod's per-run caps by
the price ratio (Fable 5.2 over Opus 5.5 = 2, `mod_model.cap_scale`). Two limits that are also priced for Opus were
left unscaled on purpose, because neither is a per-run cap:
1. `stage_ceiling_usd` (maturation_dispatch.json, $100 per mod per stage; a ceiling, so the Conductor's act). The tick
   reserves each launch's cap against it before launch. A pinned WreckedMachines build reserves $30, not $15, so the
   ceiling admits 3 build runs where an Opus mod gets 6 [measured from the code: reserve = the run's cap].
2. The Designer's weighted-token task budget (designer_stage, advisory; role_launch's over-budget alarm). weighted_v2
   weighs a Fable token at 2x an Opus token (MODEL_PRICES), so the budget and its alarm fire at half the work.

## question for the Conductor
Scale either limit for a pinned mod (the per-run caps' idea), or keep them as they are for the Fable experiment? Until
ruled, both stay as shipped.

## criteria
The Conductor's ruling on each of the two limits is recorded on this item; if either scales, a pinned mod's limit is the shipped one times mod_model.cap_scale, with its test.

## verify
Acceptance test: none, both are ceilings the Conductor rules on (his `stage_ceiling_usd` releases, the Designer's
budget); a test is written with the change if he scales either.
