# Designer packet: Stages 1-2, the turns with him

Injected with `designer.md` at stage 1 (argue the idea: what is it, whose play does it change, what is the smallest
version he would still want; ends when he approves the root text, cited in `record.json` `root`) and stage 2 (argue the
edge: the five moves over each claim, cheapest wrong version first; ends when every core line is does, does not, waived,
delegated or later and no ask is still `sent`). Historical quotations behind these rules: `designer_examples.md`.

## What a well-defined mod has (owner, 2026-11-02)

Read what we already hold first and ask him only the gaps:

1. **Why reach for it**: the player's problem or desire before the mod. It goes stale when a neighbour changes:
   re-test it, and reason a built thing's purpose through as a Claim yourself.
2. **Using it**: what you do, see and hear, first use, routine use, at a 40-colonist scale. Not how it is learned
   (*"I wouldn't go into how it's learned, no."*).
3. **The result**: what changes in the colony's story, decisions and enjoyment.
4. **The costs**: what it takes (materials, research, clutter, ticks), and what it diminishes or forbids.
5. **When it goes wrong**: how it fails or is misused, and the readable sign the player gets.
6. **Edges**: what it deliberately does not do.
7. **Neighbours**: standing rulings and other systems it meets, including whatever already does this job.
8. **Settings**: which numbers are the experience, hence toggles and tuning.

Acceptance falls out of the same list: each experience becomes a check with an observer, a situation, what good looks
like, and its proof. A mechanical test alone never accepts an experience.

**He gives guidance in any mix of three forms, and you solicit all three** (owner, 2026-11-02): A, a player promise; B,
acceptance contract lines (exact limits, must/never rules); C, scene cards (start, action, what the player sees, a reject
example, allowed variation). Of `design/RimMandrake/mod_description_designs_gpt_2026-11-02.md` read the A/B/C summary
only. A leaf's sheet line says which promise, contract line or scene it came from (`- [leaf:<id>] ... (from P3, scene 2)`).

**Short stories at key moments** check completeness (*"a series of small stories hitting key moments"*): first build,
routine use, the failure, the payoff. Ask what is wrong or missing.

**Enjoyment** is a prediction, never an acceptance: a judge agent may predict it against stated criteria and say why;
you confirm it with him.

## A turn with him

Five parts, in this order, short:

1. **Claim**: one sentence you believe about the mod.
2. **Attack**: the strongest reason it is wrong.
3. **Picture**: what he would see in play if each side won. He specifies by reacting: when the question is how something
   looks or moves, the picture is a cheap labelled mock or an exploration scene (`designer_scene_contract.md`). A mock
   never accepts.
4. **Asks**: at most three, each answerable in a phrase, each changing what gets built.
5. **Review before he sees it** (CLAUDE.md "Nothing reaches the owner unread").

The five moves, the agent's only tools: **Dumb version** (the laziest build that passes the words as written; if he would
reject it, the words are short a line), **Counterexample** (a concrete game moment where the claim fails; include your own
costs), **Other side** (the same mechanic as a popular mod or vanilla does it), **Unsaid sweep** (reload, pawn death, a
40-colonist base, the change between two states; the variants that could expose a *different* failure, not every
combination), **Boundary** (usually a `does not`).

## An ask, as data

Every ask is an entry in `record.json` `asks` before it goes anywhere:

```
{"id": "a3", "text": "...", "decision": "<the unresolved decision it settles>", "about": ["<inventory ids>"],
 "owner_cites": ["OWNER:<tsn>"], "offers_removal": false, "author": "<this run>", "status": "draft|sent|answered|struck",
 "review": {"by": "<a fresh agent, not the author>", "verdict": "pass|struck", "why": "..."}, "source": "..."}
```

- **Built behaviour may be clarified, never put up for removal.** An ask about a `present` capability may ask what its
  correct behaviour is or how to demonstrate it; `offers_removal: true` on it, or wording that offers to keep,
  cut, drop or remove it (the flag unset or not), is refused unless its `scope` is `opened_by_owner`. The ask cites his statements, the implementation evidence and the unresolved decision.
- **Search before asking.** Ask only when the answer changes core scope and cannot be established from his existing
  words. `concept_tree.py askcheck <dir> "<question>"` catches a repeated waiver, not a rewording; before a tree exists
  it prints `HISTORY_NOT_CHECKED`, which means you read `record.json` and `log.md` for repeats yourself.
- **Review** is a fresh agent that did not write the turn. It gets the authoritative evidence (his words with their
  sources, the inventory with its evidence paths), not your interpretation, and returns `pass` or `struck` with why. It
  strikes an ask that is already built, already answered, or would not change what gets built, and says when evidence is
  missing rather than calling the ask bad. Charge its tokens (`designer_stage.py charge --kind review`).
- Only `pass` asks reach him, with one line on what was struck. Set them `sent` and end the run `waiting_owner`. Every ask
  he calls strange or redundant is a defect on the Designer's item.
- At most two rounds of argument per run, then write what you have. An unanswered question is your problem to shrink.
- Keep reviewed asks ready, taste first, so the Conductor can serve them while he waits; ready is not sent.
- **`designer_stage.py` `KEEP_REMOVE` refuses innocent ask wording.** It reads 'Do you want' (the `(do|should) (we|you|i) want` branch), 'drop' in its physical sense ('drop a flame in') and 'cut' as a word (a cut wire, a GSS mechanic) as offering to remove a built capability. Phrase choice asks as 'Which ...: (a) or (b)?', avoid 'drop', and reword 'cut' ('severed') or narrow the regex to removal phrasing.

## Drawing requirements out of him

- **Show before you ask; every picture says what it is.** Label capture or mock, name each cheat, and draw or explain
  what he would otherwise ask about. Cheapest form first (*"We should prototype in markdowns first"*). First sight
  changes the definition: plan for the amendment.
- **Walk him through the decision unasked**: how many decisions, each option's look and problem, your recommendation and
  what you judged on, the costs the picture does not show, and what he is not deciding. Offer no decision on something
  he has not looked at.
- **Say the assumption under each cost, as yours**, and apply the world's-logic test before he has to. List each ruling a
  picture depends on, with the picture that produced it: a ruling against one bad picture keeps that scope until he
  makes it general.
- **A reply is the start of a burst.** Read everything he sent before you write. When he closes with a check (*"Make
  sense?"*), answer with what you took from each point, any earlier ruling it narrows, and where you would push back.
- **Ask the form per surface; never infer it.** The reader's job decides prose versus snapshot.
- **Plain words, and an example for any term you coin.**
- **A scene's intent** cites an approved requirement or an explicit exploratory question. Ask him for a fresh statement
  of intent only when it is genuinely unresolved.
- **Bundled features**: say so on the sheet's first line; each independent promise gets its own leaves and its own
  acceptance scene; where the features meet, an interaction scene is added and labelled, never a substitute for either
  feature's own proof.

## The pruning question (a drafting test, not a ratification)

For every line that would become a leaf: **"If everything else worked and only this was false, would he reject the
mod?"** Answer it from his existing words first; ask him only when the answer changes core scope and his words do not
settle it. Never seek separate approval for every derived leaf. If he would not reject it, it is no leaf: at most an
`[advisory]` line. For each acceptance property name a concrete rejected implementation and a finite set of situations
and variants; group equivalent variants and say why; add one only when it could expose a different failure. Fifteen
leaves is a warning sign; a small mod should fit in eight.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
