# Artisan with judgment: seed from the 2026-11-08 Pyrelands sitting

Written by the Conductor at the end of the sitting, before its context was lost, for
`RIMMASTER_REDESIGN_ARTISAN_JUDGMENT_NOT_CHECKLIST_GRIND`. This is the evidence and a first analysis. The next
Conductor window runs the GPT rounds and writes the merged propositions.

## The owner's ask (2026-11-08 ~11:30 AM PST, verbatim)

> Before we lose this context, I want you to deeply consider how we can make our Artisan loops more like this. Do you
> see how we zoomed in on issues and resolved them, rather than just chased "evidence loops" based on "frozen
> expectations?" This is what humans are good at, and we need some of this skill to get into Artisan. Please do a DEEP
> Opus 5.5 review at high effort now to consider what we could bring to Artisan to help it be more reasoned in evolving
> items, closing items, detecting problems, resolving them in tight loops, etc. We've got to get out of the "endless
> checklists grinding against the last 20% closure" experience. You are VERY smart, much smarter than such a checklist
> expects. How can we better capture that intelligence? Then send your problem statement and thoughts and concepts (at
> least 3 with tade-offs spelled out) to GPT. First solicit its own analysis, reasoning, and plans. Then expose that same
> context withih GPT to our own analysis and see what it says. Take its results and merge them with ours here, then come
> up with some coherent propositions for an improved Artisan that doesn't burn all my tokens chasing stats that are
> likely not ideal tests or thresholds anyway. A way to "break out" of that testing paradigm with the higher level goal
> seems an important point: we're trying to get a Playable v1 right now, not determine the "ultimate perfect mod" right
> now. It also seems like we're biased towards building our own solutions rather than building off of existing game
> infrastructure (e.g. sand), open source projects, etc. We should more aggressively leverage existing work that's
> already proven whenever possible.

## The evidence: the same mod, two ways (MEASURED from today's records)

| | Artisan loop (Nov 7-8) | Live sitting (Nov 8, ~8:45 AM to 11:10 AM PST) |
|---|---|---|
| Pyrelands state | 21 of 22 bars, pass 21, 69.7M tokens, still not closed | closed on his word, every bar passed live |
| Unit of work | a pass of hours against the whole bar list | one issue at a time, fix to look in ~20-40 min |
| Bars | frozen at validation; "unseen" until re-shot | reframed (ash "too slow", "darker"), one retired ("Hard Colony"), one accepted on readings already in hand (wet roots) |

What actually happened in the sitting, each a skill the loop lacks:

1. **Differential diagnosis with a control.** "All directions south-facing" looked like broken art. He compared wild Nuna
   hens (turn fine) with penned ones (do not): the cause was our staging script's rotation lock, found in one
   observation. The agent side had spent two calls chasing graphic classes. A loop that cannot form a contrast cannot
   find this.
2. **Reframing the bar by the experience.** The ash bar said "keeps accumulating". The loop measured cells and passed it
   numerically. He said "accumulating very slowly; snow would get thicker much faster" and "darker; wet ash blackened":
   the real criterion was felt, not counted, and no bar held it.
3. **Retiring out-of-scope checks.** "I want to retire the Hard Colony bar entirely ... Of course it's hard." The loop had
   spent a pass on a 3-day colony replay, and the Conductor had made two colonist deaths a gate before DONE. Neither was
   ever a north-star bar.
4. **Sufficiency judgment.** Wet roots: paused inspect-pane readings (heat factor 24% dry vs the wet-roots line on the
   watered field) -> "Nope, that's proven." No re-staging, no time-lapse.
5. **Accepting the look over the instrument.** Firehawk and Porg flight: the stills show an "under wing", the game
   looks fine -> "Pass for Flyers". The loop's instrument (stills) disagreed with the product.
6. **Reuse over invention.** Ash had been a bespoke filth with eight sprite redraws, then a hand-built ground-cover
   layer. One question ("is there functionality their snow includes that we are losing?") found vanilla 1.6 SAND
   (depth, path cost, clear job, no heat melt), and footprints were reused from Stillsand. Same pattern twice more
   today: non-flammable stuff is a known mod category; draw order was already solved for plants in BiomesShell
   (`RM_PlantDrawOrder`) and only needed generalising.
7. **A UI finding no bar could hold.** Scorchfruit "can't be picked": wild plants need the Harvest order; no right-click
   option. A player-experience issue found by playing, not by any row.
8. **Fix cycles short enough to keep the judge's attention.** Darker/faster ash: ruling at ~9:25, built and on screen by
   ~9:45. Draw order: ruling ~10:30, PASS ~11:05.

## Diagnosis: why the loop grinds the last 20%

- **Frozen expectations.** Bars are written before play, validated, then treated as the definition of done. They encode
  guesses (thresholds, counts, which shot proves what). The apparatus audits measured 20-70% of the remaining gap as
  judging error (`D:\Luke\dev\MandrakeWorkflows\artisan\FINDINGS.md`, "Four audits").
- **No permission or machinery to question a bar.** Loosening a bar is the owner's (CLAUDE.md); a loop therefore re-runs
  evidence instead of asking "is this the right test?". It also quietly drops hard work ("Braiding: do NOT start").
- **Evidence over understanding.** A pass produces shots and counts; nothing in it forms a hypothesis about WHY a bar is
  not met, or designs the one observation that would discriminate.
- **Whole-list passes.** Each pass re-reads everything, re-stages everything, and spends hours; issue-level focus is lost.
- **Build-first bias.** No step asks "what in vanilla/DLC, our 70 mods, or a proven Workshop/OSS mod already does this?"
  before writing a system.
- **No scope anchor.** "Playable v1" is not in the loop's objective; polish and v1-critical bars weigh the same.

## Concepts (at least three), with trade-offs

**A. Diagnostician pass (issue loop instead of bar loop).** Each pass opens with: what stands between this mod and a
playable v1, as a ranked list of ISSUES (not bars), each with a hypothesis and the cheapest discriminating observation
(prefer a control comparison: wild vs penned, ours vs vanilla, before vs after). Work one issue to resolution, then
re-rank. Bars become a checklist consulted at the end, not the driver.
- Buys: the sitting's shape; short cycles; finds harness bugs (the rotation lock) as fast as mod bugs.
- Costs: less systematic coverage; a weak model picks the wrong issue; needs a ranking rubric and an end-of-mod bar
  sweep so nothing silently drops.

**B. Bars as hypotheses with an intent line and a v1 class.** Every bar carries its intent ("what a player should feel"),
a class (v1-critical / polish / out-of-scope), and how it may be judged (felt, measured, either). A loop may PROPOSE
amend / retire / merge with evidence; proposals batch to the owner as one card (loosening stays his), and a polish bar
never blocks a v1 close.
- Buys: stops grinding on guessed thresholds; makes "Of course it's hard" a one-line retirement instead of a pass.
- Costs: Goodhart risk (a loop proposing to loosen what it cannot meet); owner card load; needs an independent check that
  a retire proposal is not just failure.

**C. Owner proxy judge from his own rulings.** A judge model primed with his verbatim rulings corpus (today: darker ash,
snow-like speed, "of course it's hard", flyers fine in game, reuse vanilla) predicts his verdict on a look, with a
confidence; low confidence becomes a sitting item, high confidence lets the loop move on.
- Buys: much of the sitting's judgment without his minutes; his taste stops being rediscovered.
- Costs: drift from his real taste; a confident wrong proxy is worse than a slow honest loop; must be audited against
  his live verdicts (today's sitting is a ready test set).

**D. Reuse-first gate.** Before any new system or art: a prior-art step over vanilla + DLC (decompiled source), our own
mods (`src/` search), and proven Workshop/OSS mods; record "used / adapted / rejected because". Mandatory for anything
over a small change.
- Buys: sand instead of eight redraws; less code to maintain; behaviour players already know.
- Costs: search time per item; DLC/Workshop licensing and dependency questions; a vanilla system may fight our
  design (snow melted in 50 C, sand fades) and need patches.

**E. Sitting packets: loops prepare, the owner closes.** The loop's last stage is not DONE but READY TO SIT: staged saves,
paused scenes, raids off, the 5-10 questions only he can answer, each with what the loop believes. Sittings are short and
scheduled; the loop fixes between them.
- Buys: today's closure speed, repeatably.
- Costs: his time is the bottleneck; does not scale to every mod; needs the staging discipline learned today (never
  touch his clock, never lock rotation, re-apply raid controls after every load).

**F. Churn breaker.** A bar whose evidence has been re-gathered N times (or spent X tokens) without a NEW kind of finding
stops the loop for a decision: accept on what exists, proxy-judge, or put it in the next sitting packet.
- Buys: caps the 20% grind directly; cheap to implement from existing ratchet data.
- Costs: may close things early; needs the "new kind of finding" test to be honest.

## First propositions (Conductor's, before GPT)

1. Make the loop's objective "playable v1", written into PROMPT.md, with bars classed v1 / polish (B) and a
   reuse-first step before any build (D).
2. Replace whole-list passes with the issue loop (A): one ranked issue per cycle, hypothesis plus discriminating
   observation, smallest change, look.
3. Add the churn breaker (F) to RATCHET.md: after 3 evidence rounds with no new finding, the bar goes to a decision.
4. End each mod in a sitting packet (E); build the proxy judge (C) only after it is scored against today's live verdicts.

## Next steps for the ticket (next Conductor window)

1. GPT round 1 (blind to this doc's concepts): give it the problem statement and the evidence table only; ask for its own
   analysis and plan (`python3 src/RimMandrake/Utils/gpt_consult.py`).
2. GPT round 2: give it this whole doc plus its own round-1 answer; ask it to attack ours and merge.
3. Merge into `D:\Luke\dev\MandrakeWorkflows\artisan\` (a PROPOSALS doc beside FINDINGS.md): 3-5 coherent propositions,
   each with cost, what it replaces, and how we would know in a week that it worked. Bring them to him on a card.
