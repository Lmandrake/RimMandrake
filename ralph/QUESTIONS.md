# For the owner

## "Why did I see three separate cables coming out of a doorway to a single terminal node?" (2026-11-07)

Because of a dice roll, and it was wrong. Every ordinary floor connection rolled for 1, 2 or 3 parallel cords (the Mod Setting `cordsPerConnection`, shipped at 3). Your earlier ruling on "very odd triple cords" made a machine's own lead one cord, but left conduit ends, junctions and wall stubs rolling. So a plain run out through a door to where the conduit ends could draw three cables for one line of conduit. Nothing about the door or the grid asked for it.

Fixed: the shipped setting is now 1, so one connection draws one cord everywhere. Your settings file never stored the old value, so you get the new one. Overhead lines still carry their wires, and tangles are still heaps of many wires. The slider stays in Mod Settings for a player who wants bundles. Nothing here needs an answer from you unless you want the slider removed altogether.

**Second cause, found 2026-11-07 (pass 5).** Modern power strips could still look like several cables going to one place. When a strip sat right beside a machine, its sockets faced that machine. The cord passing through to the next node then had to run along the machine's edge to reach a socket, so from above it looked like a second cord going into the machine. The machine now takes the strip's own single lead, and the sockets face open floor. This is a change to how strips sit in a look you approved. Seen working beside the batteries in the Modern look; other spots and looks not yet checked. Before and after shots still owed.

**Third cause, found 2026-11-07 (pass 6), the biggest one.** Batteries and generators carry power themselves, and the mod drew a separate cord to every conduit cell touching them. A conduit run alongside a solar panel drew seven cords and a row of power strips into that one panel. The staged test site never ran conduit along a machine, so nobody saw it until I built a colony on a generated map. Now each run gets one cord. A battery joining two separate runs keeps one cord per run, and a conduit end beside the building still plugs in, so it doesn't spark. Seen fixed at the solar panels and batteries in the Modern look (`p6N_Modern_yard`, against `p6L_Modern_yard` before). Other looks not yet checked.

## Cords in tall grass look dashed: keep this? (2026-11-07, pass 6)

On a real map the grass draws over the cords, so a thin cord through grass shows as broken dashes (`p6N_Modern_cutspan`, `p6L_Modern_house` bottom right). It reads as a cord lying down in the grass, but a player could take a dashed stretch for a break. Drawing cords above the grass would fix that, but they would look laid on top of the plants, and it changes a look you approved. I recommend keeping it as it is, and I have left it unchanged. Tell me if you want it the other way.
