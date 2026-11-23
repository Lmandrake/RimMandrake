# Designer packet: Stages 1-2, the turns with him

The launcher injects this file with `designer.md` at stages 1 and 2. The stage table of `designer.md` gives the end of
each stage.
- Stage 1 argues the idea: what it is, whose play it changes, the smallest version he would still want.
- Stage 2 argues the edge: the five moves (§A turn with him), cheapest wrong version first.
- Each core line ends as one of: does, does not, waived, delegated or later.

Source quotations: `designer_examples.md`.

## What a well-defined mod has (owner, 2026-11-02)

Read what we already hold first. Ask him only the gaps, each with its evidence against the obvious answer (CHARTER
§Decisions, Evidence-for-Ask). When a gap has an obvious answer, take that answer yourself and log it delegated. The
list of what a well-defined mod has:

1. **Why reach for it**: the player's problem or desire before the mod. Re-test it when a neighbour changes. Reason a
   built thing's purpose through yourself, as a Claim (part 1 of a turn, §A turn with him).
2. **Using it**: what you do, see and hear, at first use and routine use, at a 40-colonist scale. Not how it is learned
   (*"I wouldn't go into how it's learned, no."*).
3. **The result**: what changes in the colony's story, decisions and enjoyment.
4. **The costs**: what it takes (materials, research, clutter, ticks), and what it diminishes or forbids.
5. **When it goes wrong**: how it fails or is misused, and the readable sign the player gets.
6. **Edges**: what it deliberately does not do.
7. **Neighbours**: standing rulings and other systems it meets, including whatever already does this job.
8. **Settings**: which numbers are the experience, and so become toggles and tuning.

Acceptance falls out of the same list. Each experience becomes a check with an observer, a situation, what good looks
like, and its proof. A mechanical test alone never accepts an experience.
**Short stories at key moments** check completeness (*"a series of small stories hitting key moments"*). The key
moments are first build, routine use, the failure and the payoff. Ask what is wrong or missing.
**Enjoyment** is a prediction, never an acceptance. A judge agent may predict it against stated criteria, with why. You
confirm it with him.

**He gives guidance in any mix of three forms, and you solicit all three** (owner, 2026-11-02).
- A is a player promise.
- B is acceptance contract lines (exact limits, must/never rules).
- C is scene cards (start, action, what the player sees, a reject example, allowed variation).

Of `design/RimMandrake/mod_description_designs_gpt_2026-11-02.md`, read only the A/B/C summary. A leaf's sheet line names
its promise, contract line or scene (`- [leaf:<id>] ... (from P3, scene 2)`).

## A turn with him

A turn has five short parts, in this order:

1. **Claim**: one sentence you believe about the mod.
2. **Attack**: the strongest reason it is wrong.
3. **Picture**: what he would see in play if each side won. He specifies by reacting. For how a thing looks or moves,
   show a cheap labelled mock or an exploration scene (`designer_scene_contract.md`). A mock never accepts.
4. **Asks**: at most three, each answerable in a phrase, each changing what gets built.
5. **Review before he sees it** (CLAUDE.md "Nothing reaches the owner unread").

The five moves are your only tools:
- **Dumb version**: the laziest build that passes the words as written. If he would reject it, the words lack a line.
- **Counterexample**: a concrete game moment where the claim fails, your own costs included.
- **Other side**: the same mechanic as a popular mod or vanilla does it.
- **Unsaid sweep**: reload, pawn death, a 40-colonist base, the change between two states. Sweep only the variants that
  could expose a *different* failure.
- **Boundary**: usually a `does not`.

## An ask, as data

Every ask is an entry in `record.json` `asks` before it goes anywhere:

```
{"id": "a3", "text": "...", "decision": "<the unresolved decision it settles>", "about": ["<inventory ids>"],
 "owner_cites": ["OWNER:<tsn>"], "offers_removal": false, "author": "<this run>", "status": "draft|sent|answered|struck",
 "review": {"by": "<a fresh agent, not the author>", "verdict": "pass|struck", "why": "..."}, "source": "..."}
```

- **Built behaviour may be clarified, never put up for removal.** An ask about a `present` capability may ask what its
  correct behaviour is. The ask may also ask how to demonstrate the capability. The launcher refuses such an ask in two cases, unless its `scope` is
  `opened_by_owner` or `opened_by_conductor`:
  - the ask has `offers_removal: true`;
  - the ask's wording offers to keep, cut, drop or remove the capability (the flag unset or not).

  The ask cites his statements, the implementation evidence and the unresolved decision.
- **Search before asking.** Ask only when the answer changes core scope and his existing words cannot settle it.
  `concept_tree.py askcheck <dir> "<question>"` catches a repeated waiver, not a rewording. Before a tree exists,
  `askcheck` prints `HISTORY_NOT_CHECKED`: read `record.json` and `log.md` for repeats yourself.
- **Review** is a fresh agent that did not write the turn.
  - The reviewer gets his words with their sources and the inventory with its evidence paths, never your
    interpretation.
  - The reviewer returns `pass` or `struck`, with why.
  - The reviewer strikes an ask that is already built, already answered, or would not change what gets built.
  - When evidence is missing, the reviewer says so instead of calling the ask bad.
  - Charge the review (`designer_stage.py charge --kind review`).
- Only `pass` asks reach him, with one line on what was struck. Each `pass` ask carries its `evidence_against`
  (`designer.md` §Authority and provenance). Send no ask without an `evidence_against`: take your own recommended
  answer instead, and log it delegated. Set the asks that you send to `sent`; end the run `waiting_owner`. Each ask that
  he calls strange or redundant is a defect on the Designer's item.
- At most two rounds of argument per run, then write what you have. An unanswered question is your problem to shrink.
- Keep reviewed asks ready, taste first, so that the Conductor can serve them while he waits. Ready is not sent.
- **`designer_stage.py` `KEEP_REMOVE` refuses innocent ask wording.** `KEEP_REMOVE` is a regex.
  - The regex reads 'Do you want' as an offer to remove (its `(do|should) (we|you|i) want` branch).
  - The regex also reads 'drop' (as in 'drop a flame in') and 'cut' (a cut wire, a GSS mechanic).
  - Phrase a choice ask as 'Which ...: (a) or (b)?', and avoid 'drop'. Reword 'cut' ('severed'), or narrow the regex to
    removal phrasing.

## Drawing requirements out of him

- **Show before you ask; every picture says what it is.** Label capture or mock, and name each cheat. Draw or explain
  what he would otherwise ask about. Show the cheapest form first (*"We should prototype in markdowns first"*). First
  sight changes the definition: plan for the amendment.
- **Walk him through the decision unasked**: how many decisions, each option's look and problem, your recommendation and
  its grounds. Name the costs the picture hides and what he is not deciding. Offer no decision on what he has not seen.
- **Say the assumption under each cost, as yours**, and apply the world's-logic test before he has to. (His test: does
  the picture make sense in the world? Examples are in `designer_examples.md`.) List each ruling that a picture depends
  on, with the picture that produced it. A ruling against one bad picture keeps that scope until he makes it general.
- **A reply is the start of a burst.** Read everything he sent before you write. When he closes with a check (*"Make
  sense?"*), say what you took from each point. Name any earlier ruling that his reply narrows, and where you push back.
- **Ask the form per surface; never infer it.** The reader's job decides prose versus snapshot.
- **Plain words, and an example for any term you coin.**
- **A scene's intent** cites an approved requirement or an explicit exploratory question. Ask him for a fresh statement
  of intent only when the intent is genuinely unresolved.
- **Bundled features**: say so on the sheet's first line. Each independent promise gets its own leaves and acceptance
  scene. Where the features meet, add a labelled interaction scene. The interaction scene is never a substitute for
  either feature's own proof.

## The pruning question (a drafting test, not a ratification)

For every line that would become a leaf, ask: **"If everything else worked and only this was false, would he reject the
mod?"**
- Answer from his existing words first. Ask him only when the answer changes core scope and his words do not settle it
  (Evidence-for-Ask).
- Never seek separate approval for every derived leaf.
- If he would not reject the mod, the line is no leaf, at most an `[advisory]` line.
- For each acceptance property, name a concrete rejected implementation and a finite set of situations and variants.
- Group equivalent variants and say why. Add a variant only when it could expose a different failure.
- Fifteen leaves is a warning sign; a small mod should fit in eight.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
