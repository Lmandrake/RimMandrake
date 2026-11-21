# RIMMANDRAKE_TRACE_PYRE_FIREHAWK_TURNS_MANHUNTER_IN_BURN_WALK

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20). Class unknown.

## spec

On the visit-2 site (quiet storyteller, incident queue cleared by gate B), during `burn_line_burned_share` (chain
burn_line, evidence design/concepts/Pyrelands/version/in_game/visit_2/evidence/pv2_burn_line.json), the governor stopped
jawa/safe_advance after 1320 of 2000 ticks: "hostile_arrival: turned hostile: RM_FireHawk (Manhunter)". The rest of the
chain read UNMEASURED. Vanilla turns a wild animal manhunter when a colonist harms it (revenge) or by an incident; the
site's colonists fight fire in the burn, and fire-hawks fly into it. Which one happened is unread.

## verify

The next burn_line run records the hawk's last damage source (or the letter/incident) when it turns hostile.

## criteria

- The cause is named: vanilla revenge (then a SITE matter: colonists must not fight fire beside hawks in this row), an
  incident (SITE: the quiet profile leaked), or a mod path (MOD).

## Acceptance test

Live only, none offline: the event is rare. Red: seen once, 2026-11-20. Green: the cause named on this item.

## refs

file: src/RimMandrake/Pyrelands/validation.py
def: ThingDef/RM_FireHawk
