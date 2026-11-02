DRAFT, sitting 2 (2026-11-02). Round 1 is answered and recorded. Round 2 is open. Everything outside `his words` and `waived` is the Designer's proposal.
Built today (mod_completion 2026-11-01): 31 inventory entries, 14 work at L2+, 4 broken, 13 unverified. Full inventory: `log.md`, sitting 2.

# Gimme Some Slack

## his words
- 2026-10-02: "I almost want to make it weirder like snakey, ropey loose conduit on the floor."
- 2026-10-02: "It's just about cords roughly connecting to/from where they belong. … it's really the nodal map of sources, destinations, places where they go into walls, places where they emerge, and then corners that they must traverse."
- 2026-10-02: "I'm not going for taught cables. Quite the opposite. Everything is a too-long extension cord."
- 2026-10-02: "Yes, conduit that suddenly ends has a "node" at its terminal point that must be reached by a "broken" cord lying on the ground. Sparking if live, dead if not."
- 2026-10-02: "ideally a huge tangle of nasty wires and power strips all swirled together terribly"
- 2026-10-02: "Yes, I want it to have much larger excursions that avoid unwalkable areas or even pile up against them."
- 2026-10-02: "I'd like the powerlines included, swaying in the wind, etc. … Movement/animation is not appropriate for Northstar, unfortunately."
- 2026-10-04: "A single build menu should allow the player to select between these four art styles for the poles, hose reels, hoses, and cables somehow. … a single connected run of conduit no matter how large would be a single art style."
- 2026-10-10: "it allows GimmeSomeSlack to be entirely about cables and conduits and electricity."
- 2026-10-10: "If caught, steady goodwill drain (like living too close to a settlement)"
- 2026-10-16: "you show one cable going all the way. But then you draw a second cable that acts disconnected as well."
- 2026-10-22: "Their own switch."
- 2026-10-23: "the electrical plug is shown going into a pipe slot. Weird. It should favor diagonal approaches sliding underneath, to avoid confusion."
- 2026-10-26: "find out if gimme some slack also has the same problemmatic delay with large numbers of wires and connectors."
- 2026-11-02: "Yes, I want both poles and floor coords. No, I would not reject it, but there's no reason not to do this. It's just art and that's easy. No, I don't much care about savegame continuity, though I'd be very surprised if we needed to store things in the savegame that acted that way. Those were very strange questions given we already have these capabilities."
- 2026-11-02: "The power strips (modern style art) or connectors (other art styles) should appear whenever there are three or four way junctions of conduit. They should appear to host many of the other lines plugging into the power strips and connectors, as the means to join the many cables."
- 2026-11-02: "Cables should look messy and only loosely follow the conduit in the floor. It should not repeat patterns but appear like real messy cables strewn across the floor."
- 2026-11-02: "The experience should be to make the space filled with realistically sprawling, over length extension cables just like happens in real life. Cables should pile against the wall, resist tight turns, and tend toward gently curving tangles and coils."
- 2026-11-02: "The point is to make the game look more realistic and support the experience of scavengers, sloppy junkers, and trailer trash."
- 2026-11-02: "The four kinds of art are intended to support different game styles. One for junkyard kludge vibe, one for deep industrial // Star Wars, one for modern day obnoxious multi colored extension cables and normal power strips, and futuristic cyberpunk style"

## does
- [leaf:conduit_invisible] An observer sees no vanilla conduit pipe. Only cords show where power goes
- [leaf:cords_slack] A cord between two nodes lies in broad loops, much longer than the straight line, and piles against walls rather than crossing them
- [leaf:wall_face] Where conduit goes into a wall, the cord ends at the wall's face
- [leaf:tangle] A dense block of conduit reads as one heap of wires and power strips
- [leaf:break_ends] At a cut, the live end looks different from the dead end at normal zoom
- [leaf:span_overhead] An overhead span between masts is drawn above the pawns and buildings under it
- [leaf:span_downed] When a mast falls or a span is cut, the span lies on the ground
- [leaf:cut_cost] Cutting or building one wire in a large base causes no visible stall (built; the slice bar is still partly failing)
- [leaf:walk] Reload a save made mid-way, cut and repair a line again, then build a second grid: the cords stay true throughout
- [floor:mod_settings] Master switch off restores vanilla conduit without a restart
- [advisory] Four styles, one look per connected run: built, and the walk's two style bars stay ("No, I would not reject it, but there's no reason not to do this")
- [advisory] Power-tap theft with a goodwill drain, the wire-down alert, re-stringing a span, and pipe poles with their own switch: all built, none barred (delegated)

## does not
- [leaf:no_hose] Draws nothing for a hose or pipe. Hoses belong to FlowWorks ("entirely about cables and conduits and electricity")
- [leaf:no_taut] No cord is pulled taut and straight between two nodes
- [leaf:no_impassable] No cord is drawn across a wall, rock or other impassable cell
- [floor:multiplayer] No multiplayer support
- [waived:w1] No promise that a save loads clean after the mod is removed
- [advisory] Sway and spark motion: seen on the review map, never a bar ("Movement/animation is not appropriate for Northstar")

## waived
- w1, 2026-11-02: "I don't much care about savegame continuity" (OWNER:1793590546413059482)

## open
- [core] cords_tell_truth: no cord across a cut, no second phantom cable, no plug into a pipe slot. Is a false drawing a reason to reject, or a bug class? (round 2, ask 1). The phantom cable from 10-16 was never verified fixed
- Gravship: after landing, do the cords keep their old look or get laid fresh? (round 2, ask 2). Built as a switch; latest proof row broken. Core only if he says so

## delegated
- Theft, wire-down alert, re-stringing, pipe-pole switches are [advisory], not leaves. His ask-1 answer names "poles and floor coords" only. Say so to undo.
- The style bars stay in the walk as they are. Only he loosens a bar, and his words do not ask for it.

## pruning
- conduit_invisible: "little drawn wires decoratively put over otherwise-invisible-conduits"
- cords_slack: "Everything is a too-long extension cord."
- wall_face: "we just say "it's in there" and show where it comes out/goes in"
- tangle: "a huge tangle of nasty wires and power strips"
- break_ends: "Sparking if live, dead if not."
- span_overhead, span_downed: "Yes, I want both poles and floor coords." (2026-11-02, answering "would you reject it without them")
- cut_cost: his 2026-10-26 words. The number comes from the floor
- no_hose: his 2026-10-10 words
- no_taut: "I'm not going for taught cables."
- no_impassable: "much larger excursions that avoid unwalkable areas or even pile up against them"
- walk: the walk leaf every mod has
- styles: no leaf. "No, I would not reject it" (2026-11-02)
