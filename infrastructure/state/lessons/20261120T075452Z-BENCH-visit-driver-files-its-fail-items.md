A visit's FAIL item that is not caused_by the steward run never reaches a fixer: a visit driver files its FAIL items caused_by its own DRIVE item, and a visit row's 'filed' can name an OLDER item, but the maturation tick launches fixers only on items caused_by the steward run (maturation_autonomy._road_back_ids finds items only by caused_by), so the next visit would launch without it. The steward takes each over with 'rimflow file <NEW> --caused-by <steward item> --replaces <driver item or old item>'.

Sightings:
- 2026-11-19: five GimmeSomeSlack visit-2 driver items (RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_ACCEPTANCE_VISIT_TWO) were still open and never re-parented.
- FlowWorks visit 5, GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO: a visit row whose 'filed' names an OLDER item (not filed caused-by the driver's or a steward's item) is invisible to the road back. The steward files a successor caused-by its own item with --replaces <old>.
