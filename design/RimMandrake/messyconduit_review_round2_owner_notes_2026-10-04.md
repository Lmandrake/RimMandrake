# MessyConduit (Gimme Some Slack) — owner review notes, round 2, 2026-10-04

Typed by the owner while walking `human_review.py` stations (verbatim; station numbers are the review map's).
Ledger item: `MESSYCONDUIT_REVIEW_ROUND1_1` (new findings file as B28 onward).

> We need some tests that make the hose solve a complex path (like a spiral through a simple
> maze with two options, then "build" a wall to block the obvious solution so we can see if it
> changes to go the other way... or what happens). Screenshot of station 16 still shows the
> crappy hose reel disconnected from the pipe. Gonna need to make sure the Hose Reel can also
> connect to standard static piping and other pipe-friendly buildings (like tanks). BTW, to be
> clear, these should be "universal pipes" that can carry any liquid of any kind (see universal
> tank). What logic is even used on if you use one, two, or three cables to connect to the power
> poles BTW? Would be VERY cool to have different local buildings connect to each of the three
> terminals (or share one as needed) if more than one local connection is made (so three lights
> on the ground would each wire to a different terminal on the power pole) but that might be too
> hard. We need the extra camera zoom mod to be in ALL DEBUG SETS for testing so I can really
> zoom in and study what's going on, BTW, make that policy change right now for Rimworld
> Debugging and Northstar. [DONE 6940d65a3] Screenshot taken on station 4 showing connectors not properly meeting the lightbulbs. Can we have them just go to the centroid of a building and be beneath them on
> the drawstack so that we don't have to worry about this problem? Screenshot taken station 6
> showing improvement in the wall holes having perspective on which wall they are mounted, but
> still needs alignment work: they "hang off" the wall inappropriately. Graphic for power tap is
> ugly and confusing: make it VERY clear that it's grabbed onto the other power tap. Currently
> it looks like a brown lump next to a disconnected sparking power conduit, not clear. Showing
> it BITING into the line with sparks occasionally shooting out of it would be better. Wall
> mounts look much better (screenshot station 9) but some are shown as leaning INTO the wall
> rather than out from the wall, needs fix. The north/south wall mounts seem to mount in the center of the wall rather than at their edge (both north and south), while the east/west ones
> mount soundly inside the wall entirely (as though they attach to the outer wall and then lean
> into the wall). No visible connector between battern and power pole either. Please increase the
> diversity of connected devices clustered around power poles both at distance and next to them
> to show the range of possibilities. Please include an image of power poles carrying power
> over an otherwise well populated room filled with electric devices and messy cables between
> them. Please show power cables carrying wires through a large region of heavy
> mountain-ceiling-rock with fog of war on around it. Give some thought to other potentially
> challenging configurations we might want to examine to reveal bugs visible to the human eye.
> Offer a description of the mod's current function and the tests we're running to GPT and ask
> it where high-value tests could be added that would reveal new interesting questions. Also
> evaluate how we should extend our tests and the human sheet to cover the fact that we're switching to user-selectable art.

Workstreams (2026-10-04): AERIAL (centroid connectors under buildings, power-tap clamp art, wall-mount lean/offset,
batten–pole connector, terminal-assignment logic), HOSE (reel joins universal pipes/tanks, reel art, maze/spiral/blocked-wall
path tests), SHEET (new stations in `human_review.py`), CONSULT (GPT test review + user-selectable-art test plan).

## Decisions taken by question card, 2026-10-04 3:46 PM PDT (card clicks, not typed words)

1. **Blocked hose:** reroute within its length; if none exists, retract to the reel with a visible alert. Never a ghost hose; also enforce length on re-plan.
2. **Universal pipe:** wait for FlowWorks. Reel connection stays generic (any pipe-like building sharing an edge); test against tanks.
3. **Modern cord colour:** store colour on each cord piece; a merge keeps the larger run's colour (save migration owed).
4. **Pole terminals:** spread devices across the three terminals, share only when full (as built).
