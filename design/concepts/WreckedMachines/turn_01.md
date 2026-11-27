# Wrecked Machines, Designer turn 1 (stage 1: what is the mod)

Run `rm-role-designer-1795752087`, 2026-11-26, about 8:30 PM PST. For the Conductor to serve as question cards. The
three asks are in `record.json` (`a_root`, `a_how_found`, `a_riders`). A fresh agent that did not write this page
reviewed the asks and the page before sending (the review line is at the end).

## First: a look at the running mod is on offer

Twelve of the mod's eighteen capabilities are built. One build-over was played once, on 2026-09-01. Nothing else was
ever played.

One save on the mod's small list would show:

- the smelter at all four grades, side by side;
- the power cell and the psychic emanator at three grades each;
- a wreck with a colonist sent to study it (Research Reinvented is on the small list, so this is today's study);
- a kludged smelter half-built over a wreck.

The look measures three things that no question to you can settle:

- whether a player can tell the grades apart by eye (today the cell's three grades share one picture, and so do the
  emanator's);
- whether a grade built over the last one reads as a repair or as a build menu;
- what study at a wreck looks like in play.

None of the three asks below asks you to predict what that look would show. The question about how study should feel
is held back until after the look for that reason. The Conductor stages the look. It can be a sitting with you, or an
agent's walk that brings you a short set of zoomed captures.

## The case for and against a generic version

You asked on 2026-11-19 "whether we even bother with the generic version", and answered in the same breath: "I
suspect it's a good, strong concept save for the much larger lift in terms of art generation, but we're pretty good at
that." The Conductor called it from those words: the generic mod is the mod at 0.1.0, and the Designer still writes
the case on each side. This is that case.

**For.**

- Four of our mods already use this mod as a library, by name: Cold Storage's stasis lockers, the stasis casket and
  vault in Cuisine, the Armoury's alloy recipes, and ResearchRetag's research tabs. They sit in all three of our
  tiers. Code that all three tiers use must live in the lowest tier, and the lowest tier is the generic one. None of
  the four names this mod in its dependency list, so a change here can break them without a sign.
- Your rule of 2026-09-15: the campaign layer requires this mod, never the reverse. A mod that a stranger can install
  is the test that the rule holds.
- The idea needs no setting. The base game already has machines that nobody can build (the vanometric power cell, the
  psychic emanator) and ancient ruins to find things in. The base game has no machine that is found broken and built
  back up.
- The holy-repair layer needs a base to stand on. The base owes that layer one thing: a neutral signal when a machine
  changes grade.

**Against.**

- Art. You named it ("the much larger lift in terms of art generation") and added "but we're pretty good at that".
  A carried machine needs one picture for each grade. A big machine needs one for each grade in each
  of four facings. Today only the smelter's Wrecked and Kludged grades have a picture that no other grade uses. Each
  factory machine added later is about twelve more pictures.
- In a stranger's game the mod takes before it gives. A player who has the factory mod first meets Wrecked Machines as
  a smelter that is missing from the build menu. In the campaign nothing is taken, because the clan cannot build.
- Two designs where one might do. The generic mod gets its own bars and tests now. The holy-repair layer gets a
  second design, with its own bars and tests, after it.
- Today the mod is not generic: it does not load without the factory mod, and at least six of its labels and
  descriptions still say "the ship".

My position: the generic version is worth it, and mostly for the first reason. The ladder is already shared code,
used from all three tiers, that nobody declared.

## Claim

This is the paragraph that a builder and a blind judge would work from.

> **Wrecked Machines puts ancient machines into any RimWorld game. No colony can make one. A colony finds one, broken,
> in the place where it stopped. These machines do not fail all at once: they sag. A wrecked power cell still gives a
> faint current. The colony learns the machine by studying the machine itself. Then colonists rebuild it where it
> stands, each grade over the last. A Wrecked machine is dead or nearly dead. A Kludged machine works, badly, and looks
> bodged. A Refurbished machine does most of what it once did, and costs a scarce Ancient Component. It never equals
> the original. The reward is not a strong machine. The reward is a machine that the colony could not have by any
> other road. A big machine is repaired in place. A small one (a power cell, a psychic emanator) can be carried home
> first.**
>
> **Judged first:** a colony in an ordinary game finds one wrecked machine, studies it, kludges it and refurbishes it,
> and at every step a player sees by eye which grade it is. A tester stages this twice: once with a big machine
> repaired in place (the automated smelter), once with a machine carried home (the power cell).

The smallest version that I think you would still want: the three machine lines that exist (smelter, power cell,
emanator), a wreck that a player finds in the world, a way to come by an Ancient Component, study at the wreck, and a
picture for each grade. Turrets and more factory machines come in later versions.

## Attack

One phrase in the paragraph rests on your ruling and has a cost that I state. One word is my assumption and can be
wrong.

**"No colony can make one."** This is true of the power cell and the emanator in any game. It is true of the smelter
because this mod takes the factory mod's smelter out of the build menu: your ruling of 2026-09-16, "remove the VFE
factory, not the manual one", given the day after you ruled the mod stand-alone. A Mod Setting puts it back. The cost
is mine to state: a stranger who already has the factory mod first meets Wrecked Machines as a smelter that is missing
from the build menu. The paragraph accepts that cost. It says that in this mod's games these machines are found, never
made, and the mod's description must say so in plain words.

**"Any RimWorld game."** This word is my assumption. Today the mod does not load without the factory mod. The power
cell and the emanator need only the base game. The paragraph as written means: without the factory mod, the mod is the
carried machines only, and the big machine appears when the factory mod is present. That leaves the half you called
"excellent" (big machines repaired in place) out of a game without the factory mod. Strike "any" if the factory mod is
simply required.

## Picture

**If the paragraph is right.** A colony, a year in, finds a dome of split plate with one faint light still on. It is a
wrecked power cell, and it gives a trickle of current as it lies. Two colonists carry it home. One studies it for some
days. They kludge it: steel and components, and it now gives a fifth of what the real one gives, with patches that
show. Later they find a wrecked smelter in a ruin. It is too big to carry, so they study it and kludge it there. An
Ancient Component turns up, and the colony must choose which machine gets it. The refurbished cell gives three
quarters, for good, and still looks like a repair. No trader sells one. That is the reward.

**If the laziest build wins.** This passes the old words as written, and it is close to the mod today. The player
opens the build menu, places a "wreck" for 30 steel, and clicks the next building over it. Nothing was found. Nothing
was studied. Only the smelter's first two grades have a look of their own; the rest look the same until you click
one. It is an upgrade chain with a number on it. The paragraph
above refuses this build in three places: found, not placed; studied; told apart by eye.

## Asks (three, each answerable in a phrase)

1. **a_root.** Is the paragraph under Claim Wrecked Machines? Say "yes", or change any word. The word I doubt is
   "any" in "any RimWorld game": strike it if the factory mod is simply required. The Attack says why.

2. **a_how_found.** Picture a stranger's colony in an ordinary game, a year in. When does this mod first show itself?
   - (a) Only in the rooms of an ancient ruin, on a tile that the colony settles on or visits. The bench's note of
     your card of 2026-10-03 reads "relics are found at ancient ruin sites".
   - (b) Also now and then on an ordinary map: one wreck, half-buried, there on arrival. Every colony meets one early,
     and the ruins hold the good ones.
   - (c) Something else that you picture.

   I recommend (b). The test I judged on: does a colony that never leaves home ever see the mod? Under (a) it may
   not. What (b) costs: a wreck is less rare. The card's note does not say "only", so (b) may already be what you
   meant; that is why this is yours.

3. **a_riders.** Three finished rules sit in this mod's folder and are not about a wreck that is found and repaired:
   the alloy forge that comes early with its plasteel recipe late; the one rule for what smelting and cremation give
   back; and the water distillation machine. A stranger who installs Wrecked Machines gets the first two, and the
   third when FlowWorks is also loaded. What does 0.1.0 say about them?
   - (a) They are outside this mod's promise. The bars of 0.1.0 do not judge them. They go on working as they do
     today, and each moves to the mod it belongs to in a later version.
   - (b) They are part of what this mod is, a factory-floor mod, and each gets bars of its own in 0.1.0.
   - (c) A different answer for each; say which.

   I recommend (a). The test I judged on: the paragraph has one promise, and a tester's time goes to that promise.
   Your first-version card of 2026-11-16 ("Next version, switched off") would switch such extras off. I do not
   recommend that here. The Armoury's durasteel is made on that early forge. The salvage rule acts on every smelter
   and crematorium, so its switch changes the whole campaign. The distillation machine runs on FlowWorks' liquid code.

## What waits for turn 2

These are edges, not the idea. Each has a draft in `record.json`.

- How study at a wreck feels, and which machine a colonist may study (after the look).
- Where an Ancient Component comes from. My draft position: out of other wrecks, so that each wreck found is a choice
  between a machine and parts.
- A relic's value outside colony wealth (your card of 2026-10-03; not built).

## Review

A fresh Opus judge (agent a467e768ff82de4be, not the author) read the asks and this page against your words on the
ledger. All three asks pass. What the review changed:

- `a_root` narrowed to the one word "any". The judge's reason: your ruling of 2026-09-16 already settles "No colony
  can make one", and the other reading that the first draft offered would have undone a built capability.
- `a_how_found` option (a) no longer puts "rare, an expedition" on your card; the card's note has neither word.
- `a_riders`: "gets all three" was false (the distillation machine loads only with FlowWorks); corrected.
- This page: the case for a generic version now quotes both halves of your sentence, names the cost of two designs,
  and no longer says that you asked for the case to be written (that was the Conductor's call).
- Two claims that the judge could not confirm are gone ("three mods agreed on the salvage rule", "FlowWorks waits for
  the distillation machine"); the page now says only what the code shows.

Not checked by anyone: the text of your card of 2026-10-03. Only the bench's note of 2026-10-04 exists.
