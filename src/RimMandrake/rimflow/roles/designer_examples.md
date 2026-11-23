# Designer examples: his words behind the rules

This file is loaded only on an explicit request for an example or a rationale
(`roles/designer_manifest.json` `on_request`). No stage injects this file and no program loads it: the run that gets the
request opens it. A stage packet states every rule here
(`designer_dialogue.md`, `designer_write.md`, `designer_scene_contract.md`). This file holds the quotations and worked
examples that motivated those rules. This file adds no rule of its own. A ruling quoted here keeps the scope he gave
it: a complaint about one object is not yet a universal rule.

## From his words to an acceptance line

The question each sheet answers, in his words: *"what are the human-perspective expectations we'd want to test to ensure
this passes a relentless build and validate"* (2026-11-03). What he says when he looks at the work is the raw material
for acceptance lines. All the quotes below are of that date. Each row is a candidate line for the mod that the
complaint was about. Carry a row to another mod only when the same object or behaviour is there.

| He says | What is being tested | Candidate line |
|---|---|---|
| *"such a thin line I can't even see it"*, *"not just a vertical bar"* | Seen and recognised | At play zoom in game, someone who has not read the label says what it is, in every direction and state it has |
| *"looks as though it's down, yet it says it's up"*, *"Says "needs you 5" and yet I seem to be needed in a whole bunch of places"* | Picture agrees with the words | In each state, the drawing and the inspect text say the same thing |
| *"so that it's clear what they're doing"*, *"enigmatic"* | Parts explain themselves | Each visible part he asked about: a viewer can say what it is for |
| *"stretching will NOT work, that would look ridiculous"*, *"appears to be "jumping up" in size"*, *"moving around without changing its facing"* | Motion | Through the change, the parts he named keep their size and it faces the way it moves; a still cannot pass this |
| *"When I clicked on a button to raise/lower it, nothing happened"*, *"I can't click on the tree"* | It answers him | Clicking what is drawn selects it; every order shows at once that it was taken, even while waiting for a colonist |
| *"Cartoonish and wholly not aligned with our modern art"*, *"It doesn't even look like ours"*, *"a regular-looking tree in a mushroom biome"*, *"The white is glaring."* | It belongs | Beside its neighbours, in place, a judge says it is of this world and this biome |
| *"You would never have a winch on the "enemy" side"*, *"shouldn't rot any faster than meat normally does"* | World logic | Written as the plain rule he stated, with its reject case |

Cover the zoom that he studies at as well as play zoom (*"so I can zoom in and study things"*).

**A look means using it.** When he looks, he clicks, orders and zooms (*"I just tried clicking Torres to go into the too
deep pit"*). That sitting found a creature that never turned and a staged pit that had flooded. No check caught either
defect. Sometimes he finds a defect by eye that no leaf foresaw. That defect comes back to the Designer (*"that informs
Designer strongly and should be regularly re-incorporated"*).

## What draws requirements out of him (2026-11-03)

These rules come from his sittings of 2026-11-03. Every quote in this section is his, of that date unless marked.
Evidence: `D:\ClaudeWork\rimmandrake\designer\mined_2026-11-03.md`. "Once so far" marks a rule from one instance.

**He specifies by reacting, so show before you ask.**

- With nothing to look at, he said *"Not sure how to handle that yet. Open question..."*. Shown a mock of that page, he
  said *"The English write-up you provided here is superb. There are Stuck items that seem to beg a little more"*. He
  then wrote a page of requirements.
- The first running page drew *"Much less Prose, this is intended to be a snapshot of what's running, not a narrative
  walk."*
- The first drawbridge sheet drew *"always show a little "still open" look"*.

Make a mock with skill `generating-images`, over our real art. Never ship a mock. Keep the mock in
`D:\ClaudeWork\rimmandrake\designer\` and link it from `log.md`. An exploration scene that the Conductor stages for you
never accepts a leaf. The Picture (mock or scene) passes the same pre-review as an ask: a fresh agent that is not the
author reviews it before he sees it (`designer_dialogue.md` §A turn with him, part 5). Cheapest form first:
*"We should prototype in markdowns first so I don't have you chasing design all over the place in the meantime."*
(2026-11-02). First sight changes the definition (*"it needs to be much more streamlined"*, *"Try again."*). First sight
also draws demands that nobody asked about (*"OMG we should do an audit to ensure that we need all these timers."*).

**Every picture says what it is, and a mock never accepts.**

He had to ask *"these are just renders, not actual in game art, correct?"*, *"I also have no idea what the little
build area of flooring is"* and *"is the pond supposed to be connected to the canal?"* A mock picks a direction: *"You'll
find this might not predict how they'll look in the game when connected in various ways"*.

- A status page's mock is nearly the page. A mock of a game object is not nearly the object. So his reaction to a mock
  of a game object settles less.
- Stills that an agent called good met *"This is all not the expected human experience here."* in the game.

**Walk him through the decision without being asked** (*"walk me through what precisely I'm deciding"*). Before he had
looked, he said *"I will need to review them for awhile, not yet ready to answer you"*.

**Say the assumption under each cost, as yours.** He can kill an assumption that you state.

- A line said that the winch might land on the enemy's bank. The line flagged this as our untested reasoning. It drew
  *"No, the winch would always be on the hinged-side"*.
- A stated limit of two urgent items drew *"No limits on how many can be requested"* and a design of his own.
- His test is the world's logic: *"that makes no sense"*, *"that would be strange"*, *"wouldn't the water run back into
  the pond?"*
- A ruling against one bad picture is not yet general. *"VERY weird image ... Ropes should now be slack and
  disconnected."* (2026-10-23) became *"still connected when it's in its raised state (to the winch side)"*. The change
  came minutes after the walk-through listed the ruling as settled.

**"Unproven" on the ledger may only mean unrecorded.** *"wake-on-LAN was in fact already tested successfully, not sure
why you don't know that."*; *"The power cut test was already run"*. He may have exercised a row by hand. Before you plan
around such a row, ask him in a phrase.

**Recommend, and name what you judged on** (*"Cards but also your recommendation and why."*).

- He overturns freely on design. He typed his own answers on the cards that shaped one design. So give the
  recommendation.
- In one case, option A had our recommendation, GPT and a blind reader behind it. All three judged on one test: *can
  you tell up from down*.
- He chose B because *"the Gate reads like the doorway that it really is, seems to fit into Rimworld better for me"*.
  Nobody set that test for any of the three.
- A judge answers only what it was asked (once so far).

**A reply is the start of a burst.** He keeps looking while he types: *"Oh, I now see that in the lower left..."*. Then
cables, materials, stepped motion and bridge sizes came within minutes; *"And the Titan resources shouldn't rot..."*. He
closes with a check: *"Have I provided enough guidance here?"*, *"Make sense?"*.

**Keep asks ready for when he is waiting.** *"Give me cards now while I wait thanks."* *"Any question cards while I
wait? Happy to help on any items of taste or something tricky."* A ready ask sits in `record.json` (status draft, review
pass).

**Ask the form per surface; never infer it.** A surface is one page or view that he reads, or one moment of play that
tells the player something. The form is how a reader takes the text in: a glance at a snapshot, or a
read of a write-up.

- On one day he wrote *"Much less Prose, this is intended to be a snapshot of what's running, not a narrative walk."*
  Of another page, he wrote *"The English write-up you provided here is superb."* The reader's job decides, and the
  unit is the reader's (*"Organize by Mod"*; *"Yes on the descriptions from the player point of view."*). So the
  reader's job decides the form, and the reader's unit decides how to group the text.
- In a mod, say which moments are a glance and which a read, in the player's nouns.

**Plain words, and an example for any term you coin.** *""The test never named a live state" gets a human to look baffled and ask
"what? could you give an example?""*; *"Some cryptic one: workers may not install"*.

**Ask his intent before staging, and show one feature at a time.**

- Before anyone stages a scene for him, put his intent for the scene in `log.md`, in one line. The line says what he
  wants the scene to prove, in his words if he gave them.
- He once wrote *"I'm confused how the carcass summoning scavengers and visitors relates to the coming of a new titan
  threat."* Once someone told him, he wrote the tests himself: *"So the true test might be to have the titan stomp across the
  map ... THEN force-kill it"*.
- Corpse camps and titan passage were two bundled features in one item.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
