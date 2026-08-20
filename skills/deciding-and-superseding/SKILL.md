---
name: deciding-and-superseding
description: Issuing a ruling that survives contact with other agents — recording a decision so it is executable, propagating it into every file that already says otherwise, and hunting directives that outlived the ruling that created them. Use whenever you rule on scope, close or reopen an item, answer an escalation, relay an owner decision, mark something v1/v2, deprecate an approach, or change what another agent was told to do. Also use when a doc still instructs someone to do a thing that was reversed, when two files disagree about what is decided, when you are handed a menu of options and none is right, and before reporting that a decision has been "made" — because a decision that has not been propagated has not been made.
---

# Deciding and superseding

A ruling is not a thought. It is an edit to what other agents will do tomorrow.

The failure this skill exists to prevent is specific and it is the most expensive
one in a multi-agent repo: **a live instruction that outlived the ruling that
created it.** Nobody is confused, nobody argues — an agent reads a file, does what
it says, and the work is wrong because the file was right last week.

That failure has a shape worth memorising: the ruling *was* recorded, correctly,
somewhere. It just wasn't recorded everywhere. Rulings are cheap. Propagation is
the work.

## What decides whether a ruling holds

Ask this before writing anything: **when this ruling is wrong for someone, where
will they be standing?** They will be standing in a run sheet, a queue item, a
spec — not in your ruling. Write for that place.

A ruling that holds has four parts. The first is the one everyone writes and the
last is the one everyone skips.

1. **The decision**, in the imperative. Not "we should consider" — what happens now.
2. **The reason**, compressed. Reasons are what let someone apply the ruling to a
   case you did not foresee. A ruling without one gets re-litigated the first time
   reality differs slightly.
3. **What it supersedes**, named exactly — the item, the file, the phrase.
4. **What it does NOT change.** The most common way a ruling causes damage is
   over-application: you kill one thing and someone helpfully kills its neighbour.
   If a ruling has a natural blast radius, draw its edge.

Then give it a **test**. "How would someone check this was applied?" A ruling
nobody can verify is an opinion with a timestamp.

## Supersede, don't delete

When a ruling kills something, the instinct is to remove the dead text. Resist it,
and the reason is not sentiment.

Dead text leaves evidence behind. Delete the ruling but leave the evidence, and the
next reader finds the evidence, reasons from it, and reconstructs the thing you
killed — correctly, from their point of view, because nothing tells them otherwise.

The pattern that works: **strike the row, keep it visible, attach the reason.**

```
| ~~G1~~ | ⛔ DEAD — <what replaced it, and when>. <where the ruling lives> | — | <the evidence that will otherwise mislead> |
```

Two real shapes this takes:

- A gate that is no longer a gate, whose *evidence* still looks alarming. A hash
  mismatch between a repo file and a deployed file reads as a defect forever unless
  something says "this file is not shipped and the mismatch is expected."
- A criterion that lost a clause. Quietly dropping the clause is indistinguishable
  from rewriting the criterion to fit the result. Strike it in place, say why.

## Void is not failed and it is not passed

When a requirement's *reason for existing* disappears, it did not pass and it did
not fail. It is **void**, and saying so is the honest third option.

This comes up when a criterion was borrowed: item A's test included a clause that
only ever existed to feed item B, and B has since been dropped. Grading that clause
is meaningless in both directions — passing it launders, failing it punishes work
nobody should do.

Record it as struck, with the consumer that disappeared. The distinction matters
because "void" is auditable and "we decided it passed" is not.

## When the menu is wrong, reject the menu

You will be handed escalations shaped as "here are three options, I recommend B."
That framing is useful and it is not binding. Sometimes every option shares a
premise that is false, and picking one ratifies the premise.

The tell: an option makes the problem disappear without anything changing. Closing
an item as "met" when it was not met, or rewriting a pass condition after seeing the
result, both make a chart go green. Neither is a decision.

Often the right answer is **to split the thing being argued about**. A criterion
that seems half-satisfiable usually contains two independent claims wearing one
bullet: one genuinely met, one now void. Separating them beats grading the pair.

Note who is objecting and to what. An agent that raises a principle and then
recommends violating it is telling you the honest answer is not on their list.

## Propagate, or you have not decided

**This is the actual work and it is where rulings die.** A decision recorded in one
place and contradicted in four others is not a decision; it is a disagreement with
a date on it.

Standing directives cluster in predictable kinds of file. Before you call a ruling
done, sweep for the ones your repo has:

- **Run sheets and manifests** — files that tell an agent what to do next. Highest
  risk by far, because they are read for execution rather than for reference.
- **Queue and task items** — especially `spec:`/`verify:` text that names the old
  approach, and items whose `blocked` reason your ruling just dissolved.
- **Scope and burn-down files** — the state tables, where a step's status is now
  wrong.
- **Design specs** — long-lived, rarely re-read, and quietly authoritative.
- **The deferred pile** — the v2/backlog file, if the ruling parks something.
- **Agent instructions** — role files and shared docs that encode the old rule.

Use the bundled script rather than remembering:

```bash
python3 scripts/stale_directives.py "mechanoids off" --root .
python3 scripts/stale_directives.py --regex "deploy.*Jawa_Patches" --root .
```

It searches directive-bearing files, groups hits by file, and flags which read as
live instructions versus historical records. It does not judge — it hands you the
list you would otherwise have to remember to build.

Run it on **the phrase someone would act on**, not on the item ID. Agents act on
"turn mechanoids off", not on "B25(c)" or "MECHANOIDS_STAY_ON_1" — a well-named item
tells you which phrase to search for, but it is still the phrase that finds the
directives.

### The unblocking sweep — the half everyone forgets

Propagation is usually thought of as chasing *forbidden* things. The other
direction pays better and is missed more often: **what did this ruling just
un-block?**

When a decision freezes an input, everything downstream that was waiting for that
input to settle is now actionable. Nobody gets a notification. The blocked items sit
there indefinitely, because their `blocked` line names a reason that quietly stopped
being true.

So after any ruling that fixes, freezes, closes or descopes something, ask: **which
items were blocked on this, and are they still blocked?** Then say so on the item,
in the words of its own stated blocker, so the next reader doesn't re-derive the old
reason and re-park it.

🔴 **You cannot run this sweep by searching for the ruling's own words, and this is
the trap that makes it fail.** A blocked item describes its blocker *in its own
vocabulary*, not in yours. Freeze "the item cherrypick" and the item that unblocks
says `weaponTags are a selection from the surviving item set and cannot be invented`
— sharing not one word with the ruling. Grep for "cherrypick" and it is invisible.

So the unblocking sweep is a **read, not a search**: open the blocked and deferred
items, read each stated reason, and ask of each one *is this still true?* That is a
handful of items and a couple of minutes, and it is the only method that works.

The same applies to work that a ruling makes **relevant again** rather than
unblocked. Cancel a plan to delete something and every task that was pointless while
it was being deleted is now live again — nothing marks those as blocked at all, so
only reading for them finds them.

Be careful to unblock honestly. If an item is now unblocked *in principle* but still
missing a spec that you owe, say exactly that rather than flipping it to ready — an
item that cannot be executed without guessing will bounce, and a bounced item costs
more than a blocked one.

## Parking a deferral so it survives

"We'll investigate later" is a decision to spend someone's future time. What that
person needs is the state of the evidence *now*, while you still have it.

Park it with: what was decided, what was measured (numbers, names, exact
identifiers), what would have to be true to revisit, and — most valuable — **which
parts are different problems**. Deferred items congeal: two unrelated causes get one
label because they were noticed the same day, and the later investigation inherits a
false unity. Split them at parking time, when you know the difference.

## Getting the identifiers right

Rulings arrive in prose and execute against exact strings. A defName with the wrong
capitalisation matches nothing, silently, and the ruling reports success.

When a decision names things — species, defs, files, mods — **verify the exact
identifiers against the artifact before recording them**, and note any that differ
from how they were said. It takes one command and it is the difference between a
ruling that lands and one that no-ops. Flag near-misses too: if a name resembles
other names that are staying, say which is which, or a later sweep by prefix will
take all of them.

## When a ruling collides with a guard

Guards exist because something went wrong once. Sooner or later a legitimate ruling
requires exactly the thing a guard refuses — a sanctioned shrink, a deliberate
override.

Do not weaken the guard. **Move its baseline, explicitly, in the same change as the
ruling that justifies it**, so it still refuses everything nobody authorised. A
guard relaxed "just this once" protects nothing afterwards, and the next person to
hit it will relax it again with less reason.

## Reporting

Report the ruling and its consequence, not your deliberation. The single most
useful sentence is usually the second-order one — what this unblocks, what it makes
unnecessary, what someone was about to do that they should now not do.

⛔ **You CANNOT announce a decision by messaging another agent, and you must not
try.** Owner's ruling, 2026-08-19: agent-to-agent `SendMessage` is OFF, and the
receiving windows are configured to **drop** peer messages without delivering them -
so the announcement costs tokens and arrives nowhere, and nothing tells you it
failed. There is no broadcast to send either: `SendMessage` names exactly one
target and there is no `@all`.

⭐ **A ruling propagates by being WRITTEN where the affected seat already reads** -
the file that says otherwise, and that seat's queue. That is the whole job of this
skill, and it always was; messaging was never the mechanism, only a shortcut that
felt like one. **If a seat is acting RIGHT NOW on a ruling you just reversed, tell
the OWNER in your reply** - he is reading you, and he is the only one with the
authority to interrupt anyone.
Detail belongs in the item where the work happens, because that is where someone
will be standing when they need it.
