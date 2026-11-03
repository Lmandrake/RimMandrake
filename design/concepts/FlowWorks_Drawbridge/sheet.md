DRAFT, sitting 1 (2026-11-03). Scope: the drawbridge inside FlowWorks, not the whole mod. Everything outside `his words` is the Designer's proposal. No tree yet: core lines are open.

# FlowWorks drawbridge: raised look, motion, and working it

## his words
- 2026-10-22: "Drawbriges need to be looked at in game."
- 2026-10-22, by card: "Material picks win"
- 2026-10-23: "VERY weird image when the drawbridge is up here... a stiff rope sticking straight up from the drawbridge, and two ropes from its connector on the other side extending left. No bueno. Ropes should now be slack and disconnected."
- 2026-10-25, by card: "Two-leaf drawbridge, far-bank winch acceptable? → Yes, far-bank winch is fine"
- 2026-11-03: "So the drawbridges appear very broken. The fully raised drawbridge is such a thin line I can't even see it on the game. And East-West bridge when up is just a thin vertical line, very difficult to recognize at all. The north-south bridge looks as though it's down, yet it says it's up. When I clicked on a button to raise/lower it, nothing happened. This is all not the expected human experience here."
- 2026-11-03: "For the mockups, I would strongly advise that they not be allowed to go full vertical to the camera, but always show a little "still open" look to give them some dimensional awareness."
- 2026-11-03: "I prefer B actually. I like the Gate reads like the doorway that it really is, seems to fit into Rimworld better for me. East and West look GREAT on that option too. No, the winch would always be on the hinged-side and that will always be on the "friendly" side of the bank. You would never have a winch on the "enemy" side, that makes no sense. So we will need another rendering showing what that would look like if North is friendly and South is enemy. We need the Drawbridge to stay a bit "lowered" there too to ensure that it is still visible as a drawbridge and not just a vertical bar."
- 2026-11-03: "We will really need to work on the animation of it opening and shutting too so it doesn't look ridiculous."
- 2026-11-03: "It would be good to have the "cables" that guide the drawbridge still connected when it is in its raised state (to the winch side) so that it is clear what they are doing. (cables, ropes, chains, whatever they are for the particular drawbridge, of course)"
- 2026-11-03: "If it proves not possible to smoothly animate (stretching will NOT work, that would look ridiculous), then we can just render 4 to 10 "steps" and have it move through them in sequence. That would likely look pretty good. But we need to think about different bridge sizes etc."

## does
- [leaf:up_or_down] A player glancing at normal zoom can see the leaf and tell up from down, in all four directions and both materials, and the readout always agrees with the picture
- [leaf:findable_raised] A raised bridge can be found on a lived-in map at normal zoom without knowing where it is
- [leaf:friendly_bank] Hinge, winch and gate sit on the bank the player calls his, shown before he commits the drag
- [leaf:gate_is_doorway] The Hinge Gantry (option B) reads as a doorway, and a colonist visibly walks through it
- [leaf:lines_show_lifting] Raised and moving, ropes or chains in the bridge's own material run from leaf to winch side
- [leaf:click_answers] A click on raise or lower answers at once, says what happens next, and names any reason it cannot happen
- [leaf:order_gets_done] On a bridge built by colonists, a colonist comes, works it, and the leaf moves, raising and lowering
- [leaf:swing_believable] Opening and shutting looks like one rigid leaf turning on a fixed hinge, in all four directions
- [leaf:every_size_holds] Every length and width looks like the same bridge, and a wide leaf reads as one leaf
- [leaf:material_reads] Timber and steel can be told apart at normal zoom, lowered, raised and moving
- [leaf:walk] One real sitting: drag, build, raise as a raid nears, save mid-swing, reload, lower, repeat in another direction

## does not
- [leaf:no_vertical_bar] A raised leaf is never drawn straight up at the camera or as a thin bar
- [leaf:no_stretching] No leaf, plank or gate is ever stretched to fit a length or a moment of the swing
- [leaf:no_line_across_gap] No line crosses the open gap to the far bank, and none stands stiff in the air

## open
- [core] two_leaf_bank: a two-leaf bridge has one leaf hinged on the far bank. His 2026-10-25 card allows that winch; his 2026-11-03 words forbid it (the one question in the brief)

## delegated
- Raise during a raid stays an ordinary colonist job, with the wait shown clearly. Say so to undo.
- A rigid leaf looking shorter as it tips is not stretching, unless it reads so on the v3 motion page; then it goes to 4 to 10 stepped poses. Say so to undo.
- The game guesses the friendly bank as it does today (home area, then nearer the colony's buildings). New: the drag preview shows the guess and the player can flip it. Say so to undo.
- The gantry frame stands with the leaf even where the gate is off in Mod Settings or was refused; the gate fills it when present. Say so to undo.
- Motion is judged at normal speed. At 2x and 3x the bar is only no pop and no jump. Steel takes about 2 seconds a leaf today, a proposal that may be too quick to see; the motion check decides. Say so to undo.

## pruning
- up_or_down: "The north-south bridge looks as though it's down, yet it says it's up."
- findable_raised: "such a thin line I can't even see it on the game"
- friendly_bank: "You would never have a winch on the "enemy" side, that makes no sense."
- gate_is_doorway: "I like the Gate reads like the doorway that it really is"
- lines_show_lifting: "so that it is clear what they are doing"
- click_answers: "When I clicked on a button to raise/lower it, nothing happened."
- order_gets_done: "When I clicked on a button to raise/lower it, nothing happened."
- swing_believable: "so it doesn't look ridiculous"
- every_size_holds: "But we need to think about different bridge sizes etc."
- material_reads: "Material picks win"
- no_vertical_bar: "still visible as a drawbridge and not just a vertical bar"
- no_stretching: "stretching will NOT work, that would look ridiculous"
- no_line_across_gap: the Conductor's reading of "to the winch side", not his words; he can strike it
- walk: structural, one per mod, and he did not say it
