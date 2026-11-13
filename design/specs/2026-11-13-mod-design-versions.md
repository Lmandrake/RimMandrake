# Mod Design Versions: a target that holds still long enough to pass

**Status: DRAFT for Mandrake's review, 2026-11-13. Not a ruling. Nothing here is built.**

## 1. His words (verbatim, 2026-11-13, typed to the Conductor)

> You are correct about the Designer loop. Here's the language I would like to use. Each mod now needs an official Version we are building towards. This is not a "game version" but just of that mod. It is not the "current snapshot in git hash" but rather the version of the mod's design we are aiming at. That design is, by nature, incomplete: we try, but we cannot guarantee ever that there will not be needed additions, modifications, or deletions that will occur as we build and verify it. It's simply the nature of creative work. But what CAN change is a discipline that as a person I'm having to learn, and it's showing in our process. For a given Design vision (say 1.0), some Design elements, acceptance tests, and refinements will necessarily change. If these changes are Convergent changes, meaning they bring us CLOSER to the original vision in 1.0, then they are allowed even if they force a re-build, re-validate, and re-judge cycle. Other Divergent changes may still be valuable but they actually shift the vision to something other than 1.0. This is never clear-cut, it is a judgement call by the human, and I need to put more items in this "Divergent" category. These get written up as tickets for the NEXT version and do not change today's judgement criteria. These items should not be seen as negative. They are valuable and perhaps even critical for success of the whole project. But they prevent a judge from ever declaring Pass until the Design finishes drifting... and it may never, to be honest. We need to allow our Design -> Build -> Debug -> Judge produce passes sometimes so we know the SYSTEM works too, and that's valuable in its own right, even if it means sometimes completely finishing a version of a mod you know isn't what you really need but only thought you did at first. That's the hard lesson I need to accept, and build into the system. These items MUST be carefully documented and kept protected: they are the future of the mod beyond mere Judgement pass for this version. But they must also not be allowed to change the Judgement and bars for the current version. So this is something the Designer (and Conductor itself) should always be on the lookout for and asking me. "This change is not a tweak, it's a major change or addition to the policy. Should we modify the design of the current mod definition, or should this be filed for the next version after we clear the current version?" They should freely give their advice in terms of the feasibility, effort required to build, effort required to test, and how close we are to passing the current bars. If we are having trouble passing current bars BECAUSE it needs a redesign, then that is evidence we should just do it now. If we are close to passing and can do so with minor tweaks, let's pass the current bars fully now, register that, THEN consider the next version as a new project with bars only related to those changes. Likewise, the Judge may propose moving a bar that's just cycling and failing to be met (consistently supported with weak evidence) but is otherwise unrelated to the other bars in a mod to the next version, to allow most of the current version to be accepted and fully pass, closing the loop and fairly measuring (at last!) how efficient and productive we actually are on the majority of the items. Each mod should have its own current version and status. Opening a new version to work on should be weighed by Conductor and Mandrake together as "is this more valuable than moving to the next mod and getting it to at least a first working version at all?" This means mods must now be seen as having not only their definitions file and current implementation files, but a "next version" detailed description including pre-written ticket files and acceptance tests for them as best they can. For version numbers, please suggest several common ways people define version numbers in the software industry. I'd like to adopt something well defined that has meaning.

## 2. What I take the goal to be

Three goals, in this order:
1. **The pipeline produces real passes.** A pass proves the system (Design, Build, Debug, Judge) works and gives the first honest measure of cost per finished thing.
2. **No good idea is lost.** Ideas that arrive mid-build are kept, written up and protected, without moving today's bars.
3. **His time goes to judgement calls only.** He decides "now or next version"; agents do the paperwork and bring advice.

## 3. The policy, tightened

### 3.1 A Design Version is a locked target
Each mod has one **current Design Version**. It is three things, written down and locked together:
- **The vision:** five to ten plain sentences saying what the mod is for a player at this version. This is the anchor. "Convergent" and "divergent" are measured against this text and nothing else. *(Addition: without a short written vision, nobody can say what "closer to 1.0" means.)*
- **The bars:** the acceptance criteria the Judge passes or refuses on.
- **The tests:** offline and live, per the 2026-11-13 ruling that tests are built with the item.

Lifecycle: **Drafting** (free change) → **Locked** (he says "lock it") → **Building** → **Judging** → **Passed**, or **Superseded** (replaced before passing, see 3.5). After the lock, the Judge judges only against the locked bars.

### 3.2 Every proposed change after the lock is sorted into one of four kinds
| kind | what it is | where it goes |
|---|---|---|
| **Correction** | a bar or test that is wrong, contradictory or unmeasurable | fixed in the current version by the neutral fixer (already the 2026-11-12 refusal ruling) |
| **Convergent, blocking** | without it the mod does not deliver the written vision | current version; costs a rebuild and re-judge of what it touches |
| **Convergent, polish** | closer to the vision, but the vision is delivered without it | a patch version after the pass (see 3.6) |
| **Divergent** | changes or extends the vision | the next version's file, as a ticket with its acceptance test |

*(Change to his text, and the most important one.)* He wrote that convergent changes are allowed even when they force a re-judge. The measured Explosive Knockback loop was made almost entirely of convergent changes: twelve refusals, every gap a small scene edit, none a new idea. So "convergent is always allowed" does not end the loop. The split into blocking and polish does: only a convergent change the vision cannot do without re-opens the current version.

### 3.3 The Judge after the lock
- The first judge round lists every unmet locked bar. Later rounds check that list. *(From the census: a judge free to add a new small gap each round never says yes.)*
- Something new the Judge notices is a **proposal**, sorted by 3.2. It is never a refusal by itself.
- **Bar deferral** (his idea): when one bar keeps failing on weak evidence and no other bar depends on it, the Judge proposes moving it to the next version. Proposed trigger: three judge rounds unmet with the same weak-evidence reason. The pass record then reads "passed, N bars deferred", so the measure stays honest.

### 3.4 Who decides, and what they bring him
The call is his. The Designer, the Conductor and the Judge watch for it and ask in his sentence: *"This change is not a tweak, it's a major change or addition. Modify the current version, or file it for the next version after we clear this one?"* Every such question carries four facts: feasibility, build effort, test effort, and how far the current version is from passing (bars met of bars total, last judge round).

*(Addition, to save his time.)* An asymmetric default: **filing something to the next version never needs him**, because it changes no current bar and loses nothing. **Only bringing a change INTO a locked version needs him.** He sees the filed list in the daily digest and can pull anything forward.

### 3.5 "It needs a redesign" is a new version, not an edit
His rule: if the current bars cannot be passed because the design is wrong, redesign now. Proposed form: the current version is marked **Superseded, not passed**, with the reason, and the redesign opens as the next number. The failed attempt stays on the record with its cost. That keeps the pass statistics true and stops a redesign from hiding inside an edit.

### 3.6 Version numbers (options in section 4; this section assumes the recommended one)
`MAJOR.MINOR.PATCH`, meaning for a mod's design:
- **MAJOR**: the vision changed (a redesign, or a release line).
- **MINOR**: divergent additions inside the same vision: the "next version" work.
- **PATCH**: convergent polish and corrections after a pass. No new bars of a new kind.
- **Judge rounds show as `-rc.N`** (release candidate N): `0.1.0-rc.3` is the third judge round on 0.1.0. A high N is a visible loop alarm with no extra tooling.
- First working versions are `0.x`. `1.0.0` is reserved for the version he would ship to players.

### 3.7 What every mod now carries
Per mod, beside its definition and its code:
- `VERSION` record: current version, state, bars met of total, judge round, cost so far.
- The locked vision, bars and tests of the current version.
- **The next-version file**: each deferred or divergent item as a pre-written ticket with its acceptance test (or `Acceptance test: none, <reason>`), who proposed it, when, and why it was not taken now. **Protected:** append-only for agents; removing an entry is his call.
- **The pass record** of each passed version: date, git hash, bars, evidence, deferred bars, total cost, judge rounds. A passed version's tests become regression tests for every later version.

### 3.8 Opening a new version is a portfolio decision
After a pass the mod rests. Opening its next version is decided by him and the Conductor together against one question: *is this worth more than getting the next mod to its first working version?* The Conductor brings one table: every mod, its version, state, and the size of its next-version file.

### 3.9 What gets measured, at last
Per passed version: cost, judge rounds, days, bars deferred. Across mods: passes per week and cost per pass. A version with five or more judge rounds, or over its budget, parks and comes to him with the remaining list (the cap that Explosive Knockback's 4M budget failed to enforce).

## 4. Version numbering: the common schemes
| scheme | example | what the number means | fit here |
|---|---|---|---|
| **Semantic Versioning** | 1.4.2 | MAJOR breaking, MINOR additions, PATCH fixes; a published standard (semver.org) | best: maps onto vision / divergent / convergent |
| **Calendar Versioning** | 2026.11 | when it was released | weak: says when, not what kind of change |
| **Maturity stages** | alpha, beta, RC, 1.0 | how finished it is | useful as a suffix (rc.N), too coarse alone |
| **Sequential revisions** | v1, v2, v3 | only order | simplest; cannot tell polish from redesign |
| **Zero-based SemVer** | 0.3.0 then 1.0.0 | 0.x means not yet promised to users | fits a game not yet released |

**DECIDED by the owner, 2026-11-13: "Semantic Versioning it is."** With the zero-based convention and `-rc.N` for judge rounds. Recorded in `design/RimMandrake/standing_rulings.md` and `LEXICON.md`.

## 5. Open questions for him
1. ~~The numbering scheme.~~ Decided: Semantic Versioning.
2. The asymmetric default (file to next version without asking; only promotion into a locked version asks).
3. Convergent changes: split into blocking and polish, or keep all convergent changes in the current version as he wrote.
4. Who approves a Judge's bar deferral.
5. How the five existing concepts enter: lock each as 0.1.0 at today's bars and sort today's open gaps by 3.2, or redraw their visions first.
