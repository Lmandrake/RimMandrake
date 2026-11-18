# The discussion that triggered this review (2026-11-17, about 3:55 to 4:05 PM PST)

## What the owner was shown

The Conductor (the agent the owner talks to) summarised, from an incident note written at 12:15 PM PST, the three
gaps the coverage judge had refused Pyrelands on twice (rounds 10 and 11):

- Fire follows the wind: the test only checked one wind direction; it had to turn the wind around and show the fire
  turns with it, show fire spreads faster downwind than upwind, and show no fires exist before anything is lit.
- The burn line walks: the test had to run three game days, read each day how much of the map has burned, show that
  share stays under half, and show almost nothing burns with the feature switched off.
- One clause to delete from the design: "fire that lights inside the colony" (the owner had ruled that out 2026-11-16).

(That summary was partly stale: by 12:33 PM PST the three fixes had landed and the judge read `covered`, zero gaps.
The landed test reads "never most of the map" over four days, and its control is the reverse of the summary: with the
wind OFF the fire must FLOOD, which proves the instrument can see the difference.)

## The owner's words, verbatim (first message)

> Why are we demanding these extremely ornate fire tests? Sounds like the bar is too specific. Two wind directions,
> under half grass guarantee, almost nothing burns with the feature switched off (that won't be true!). Three game
> days. What is all of this? These don't read as bars anymore, they read as numeric requirements and pendantic ones.
> I would say Pyrelands only needs to have "significantly more abundant fire than a typical vanilla game map or other
> Baroque Biome map (estimated)". Its fire should be "driven by the wind clearly" (and this isn't just for this mod
> then, it's for all the baroque biomes, it just matters a lot in this biome). It should have clear regions "before"
> and "after" the fire so the scorchfruit have a bed to emerge in... things like that, right? Please push back, but
> who's setting the specification level the Judge is demanding here? Are the bars written to demand. this, or is the
> Judge getting peevish and demanding? I feel the need to rethink deeply here please. DON'T just believe me, push
> back, argue with me. We need judges that turn away incomplete work, but not work that isn't tuned just-so or, worse,
> forever needing more tuning because we keep asking a judge "how could it be better?"

## The owner's words, verbatim (second message, ordering this review)

> Document this precise mod's experience and multiple trial passes, document this discussion and your suggestions, as
> well as the current designer and judge prompts, and send the whole thing to GPT for deep review and its own
> recommendations first, then review of yours cross-comparison, and final specific rulings that focus on detecting and
> fixing FLAWS not endless polishing & allowing a potentially not-quite-right mod through... because we don't even know
> what not quite right even is yet anyway. [and I agree with your decision to put the wind rule as a general baroque
> biome rule for the NEXT version, not change this one]

## Standing owner rulings that bear on this (already in force)

- 2026-11-16, "A passing bar is an experience, never a tuning number": *"The mod passing bars should not specify flora
  and fauna yield rates! That would mean every time we renormalize every mod must repass its bars... drop that!"* No
  bar pins a yield rate, a stat value, any tuning number or an asset-variant count. The test: would this bar have to be
  re-passed after we renormalize numbers? Then it is not a bar.
- 2026-11-12, "A refusal carries its path to pass": *"ANY refusals must be as detailed as the evidence they are
  rejecting and include the fixes and paths towards passing that are attainable and reasonable."*
- 2026-11-02, "Use it, break it, grow": real live failures beat predictive "might be stronger" review rounds; ship,
  watch, fix.
- 2026-11-13, Design Versions: a Convergent change fixes a Problem (a defect, or an experience its user would reject as
  strange or disappointing) and stays in the current version; Polish goes on a Polish list and is NOT part of passing;
  a Divergent change goes to the next version and never moves the current bars.
- The north-star bar for the burn line was itself loosened by the owner: *"And modify the bar so that it's not so
  finicky about "the line." Sometimes poetry is simply that. I just wanted a natural grassfire feel."*

## What the Conductor measured about who sets the level

- The owner's north-star bar is loose: `pyre_burn_line_present` reads "a fresh Pyrelands map shows grass fire burning
  somewhere and moving like a natural grass fire, with a visibly scorched trail behind it." No numbers.
- The Designer expands each bar into a leaf in `tree.json` with an `experience` text that ends in "It must not read
  as ..." clauses (for the burn line: a flood that takes the whole map and its grass; a fire that does not move; a fire
  that burns once and is gone for good. For the wind: a fire that spreads the same way whatever the wind; a wind that
  carries one fire over the whole map).
- The coverage judge turns every clause, each must-not included, into a checklist part that needs a scene with a
  control that a broken mod would fail.
- The numbers (four days, "never most of the map", bearings 90 and 270) were chosen in the fixes that answered the
  judge, not in the bars.
- Stage 5 (coverage) for Pyrelands took 11 judge looks and, per the incident note, 19.2M weighted tokens against a
  4.0M advisory budget.
