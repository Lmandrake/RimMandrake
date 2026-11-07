# For the owner

## "Why did I see three separate cables coming out of a doorway to a single terminal node?" (2026-11-07)

Because of a dice roll, and it was wrong. Every ordinary floor connection rolled for 1, 2 or 3 parallel cords (the Mod Setting `cordsPerConnection`, shipped at 3). Your earlier ruling on "very odd triple cords" made a machine's own lead one cord, but left conduit ends, junctions and wall stubs rolling. So a plain run out through a door to where the conduit ends could draw three cables for one line of conduit. Nothing about the door or the grid asked for it.

Fixed: the shipped setting is now 1, so one connection draws one cord everywhere. Your settings file never stored the old value, so you get the new one. Overhead lines still carry their wires, and tangles are still heaps of many wires. The slider stays in Mod Settings for a player who wants bundles. Nothing here needs an answer from you unless you want the slider removed altogether.
