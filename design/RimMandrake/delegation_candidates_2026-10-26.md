# Delegation candidates: the classes to consider after art geometric correction (2026-10-26)

*BENCH helper, offline analysis. Asked for because of the owner's words on 2026-10-26: "asking me to review everything isn't
very fire and forget … Could you make this determination yourself right now?" That request produced the first delegated
class (`delegation_policy.md` §2.3, second exception). A decision class can be delegated when (1) a check MEASURES the
defect or outcome, (2) the change is small and REVERSIBLE, and (3) a NON-MAKER judge confirms it. This document is a
proposal. Nothing in it is in force until he answers the cards in §3.*

## 1. Method and caveats

- **Source of record.** Every AskUserQuestion card in the top-level BENCH and FOUNDRY transcripts from 2026-10-05 to
  2026-10-27 01:46Z. I re-extracted them with their full option lists, because the friction census cut card text at
  300 characters and so loses the "(Recommended)" mark.
  - 816 card calls holding 2,123 questions.
  - 1,600 were answered. 521 were blocked by a hook or errored.
  - Typed owner messages come from the census's `owner_classified.jsonl` (1,638 messages), counted by keyword.
  - Scripts and data: `D:\ClaudeWork\rimmandrake\orch_record\delegation\`. The scripts are `extract_cards.py`,
    `flatten.py`, `classify.py` with `rules_v3.txt`, and `tally.py`. The outputs are `tally.txt`, `questions_cls.json`,
    and the member lists `c1.txt` (sheet marks) and `c2.txt` (cleanup, next, game, rule-apply).
- **Classifier.** Ordered keyword rules; the first matching rule wins. On 135 hand-labelled questions (two random
  samples, 90 + 45) it agreed with my labels about 82% of the time. The 45-question sample was partly used to tune
  the rules, so 79% on the 90-question sample is the honest figure. Class sizes are therefore ±20%. The top-5 subsets
  below were read by hand, row by row, and do not rely on the classifier.
- **Agreement (strict).** His answer counts as agreeing only when it was the option marked "(Recommended)", alone or
  with a note. A typed "(1), plus a nuance" counts as disagreeing, so the true agreement rate is somewhat higher.
- **Predictability.** For the top 5 I also measured how often a single written rule would have produced his answer.
  This is the figure that matters for delegation, and it differs a lot from strict agreement: agents often
  recommended caution, and he overruled them in the direction the rule would have taken anyway.
- **Owner-time proxy.** 30 s per answered question (about 20 s to read, 10 s to pick), plus his typed text at 3
  characters per second, divided by 3 weeks. Typed driving messages count 0.3 to 0.5 min each. This measures his
  attention, not card latency: the median latency was 35 to 150 s per question. **Minutes saved per week = minutes per
  week the class costs × predictability.**
- **The policy already cut card volume.** Before `delegation_policy.md` (2026-10-22 23Z) he answered about 76
  questions a day; after it, 207 in 4.1 days, about 50 a day. Agreement after the policy stayed near 55%.

## 2. Ranked table

Columns (1), (2) and (3) are the three delegation properties: measured by a check, reversible, confirmed by a
non-maker judge. ✓ means it holds now, ◐ means it holds partly, ✗ means it does not hold. Classes are ranked by
minutes saved per week.

| # | class (what reaches him) | answered, 3 wk (after policy) | strict agree | rule predicts him | min/wk it costs → saved | (1) | (2) | (3) | §2 line touched | what blocks it |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Work order and helper count**: "which next", "how many helpers", "rule now or later"; plus typed session driving | 29 (4) cards; about 235 typed go-ahead or keep-going messages | 81% | 81% | ~18 → **~14** | ✓ ledger and queue | ✓ | n/a (scope) | none; already delegated by §1 `scope` | Habit only: seats still card it, and nothing stops a delegated-class card |
| 2 | **Carry out his own sheet marks**: a newer pick over his older keep; his ✕ on kept or live art | 23 (3) cards; 35 typed "enact my sheet" | 39% | **83%** (19/23) | ~13 → **~11** | ✓ the marks are data in `*.decisions.json` | ◐ only if ✕ retires to the archive instead of `purge` | ✓ none needed: the mark is his | §2.2 (`art.py purge` takes `--owner-said` only), §2.3 (kept art) | `art.py` refuses kept art even when the newer mark is his; no retire-with-revert path for ✕ |
| 3 | **Restart, deploy, take the bridge when free** (never flyers) | 16 (1) cards; about 139 typed restart or bridge messages | 54% | 69% (11/16) | ~16 of ~27 → **~11** | ◐ bridge lock yes; "is he in a live sitting?" no | ✓ a restart is reversible | n/a | §2.6 (`./bridge` is his) | No presence signal: every "no" he gave was "we're live, the game is NOT down" or "I pre-check first" |
| 4 | **Delete our own unreferenced leftovers**: old saves, scratch clones, orphan `mandrake.*` mod folders, settings or textures nothing reads, dead patches | 21 hand-read (3); 42 typed delete or cleanup messages | 56% | **86%** (18/21 chose delete, remove or archive) | ~12 → **~10** | ◐ reference check exists for art and patches, not for saves and folders | ✓ if archived or bundled first | ◐ a reaper's report | none when it is ours (§2.2 covers work not ours) | No single "unreferenced and pushed" checker; the agent default leans "keep"; the 10-18 reaper covers clones only |
| 5 | **Apply a ruling to its twin**: campaign copy, sister biome, all ages and sexes | 9 (1) | 86% | 89% (8/9) | ~1.8 → **~1.6** | ✓ a twin map or defName pair | ✓ git | ◐ | none; §2.4 says applying a ruling to a case it does not name is delegated | Habit only |
| 6 | Accept a reviewed design proposal | 49 (7) | 60% | — | 13.6 → ~8 | ✗ | ✓ | ✓ | §2.4 when it changes a ruling | His free answers add the nuance that becomes the rule; he is the design source |
| 7 | Art picks and install-after-judge (ARTPICK) | 168 (29) | 60% | — | 38.4 → ~23 | ◐ art-eval | ✓ | ✓ | §2.3 | Already §1 `art`. 29 cards after the policy is a leak, but 50% agreement after the policy means he still overrides half |
| 8 | Process and tooling choices (PROCESS) | 197 (58) | 58% | — | 47.1 → ~27 | ✗ | ✓ | ◐ | none (§1 `technical`) | Already delegated; 58 cards in 4 days. Low agreement: his answers carry new requirements |
| 9 | Names a player reads | 61 (11) | 69% | — | 12.6 → ~9 | ✗ | ✓ | ✓ | §1 `design` | He renames freely ("only our names everywhere, always") |
| 10 | Numbers and sizes | 74 (12) | 41% | — | 20.6 → ~8 | ◐ size rule | ✓ | ✓ | §1 `design` | Low agreement; he also rules the method ("with GPT, not a simple algorithm") |
| 11 | Mod list: retire or keep a donor mod | 51 (4) | 48% | — | 14.7 | ✗ | ✗ retirement cascades | — | §2.2 | His play taste; often irreversible in a save |
| 12 | Canon fixes, where a stat departs from canon | 24 (0) | 48% | — | 5.2 | ✓ canon entry | ✓ | ✓ | §2.4 (deliberate departures from canon) | He keeps non-canon for play (Nikto, Herglic, Gamorrean, "Keep all") |
| 13 | Conflict between two of his design rulings | 24 (5) | 45% | — | 6.4 | — | — | — | §2.4 | It is his ruling to reconcile, by definition |
| 14 | Design bulk (mechanics, roster, feel) | 796 (57) | 60% | — | 203 | ✗ | ✓ | ◐ | §1 `design` | Where his taste is the product; 40% disagreement |
| 15 | North-star bars | 9 (1) | 71% | — | 2.1 | — | — | — | §2.1 | Reserved; never proposed |

Rows 6 to 15 are all the other classes. Rows 7, 8 and 14 are already delegated by §1, yet 144 of the 207 cards asked
after the policy fell in them. At 50 to 60% strict agreement, his answers show that those cards mostly carried real
choices. The waste is the share he answers "(Recommended)" without comment, not the class as a whole.

## 3. Top 5 as ready-to-ask cards

Each card is written to be sent as-is through AskUserQuestion with no previews. The time line goes immediately above
it, read from `date` when the card is asked. They are text-only, so none needs a "ready for a question card?" pause.

### Card 1: Stop asking him which work comes next

**Question:** "Agents still ask you which job comes next or how many helpers to run: 29 cards in 3 weeks, and you
picked the recommended choice 81% of the time. You also typed about 235 'go ahead' or 'keep going' replies. Your
10-22 policy already lets agents decide ordering on their own. May a check refuse any card whose only question is
ordering or helper count, so the agent decides, logs it as delegated, and lists it in your daily digest?"

- **Refuse ordering cards (Recommended):** The data shows these are your agreement, not your judgement; about 14 min a
  week back. You lose the cheap chance to steer; you steer by saying so at any time, and you see the order in the
  digest after the fact.
- **Ordering cards only at your first sitting:** Keeps one daily steering moment (one card, about 1 min a day). Costs
  a stall until you sit, and agents may save questions up for it.
- **Leave as is:** You keep seeing everything. Costs about 14 min a week and the "go ahead" replies.

### Card 2: Carry out your own sheet marks without asking again

**Question:** "When your newer sheet pick conflicts with an older keep, or you click ✕ on a picture you once kept or
that is in the game, agents ask you again. That happened 23 times in 3 weeks. 19 times your answer was the rule
'newest mark wins, ✕ acts now', while the agents' recommendation (usually 'wait' or 'keep') matched you only 39% of
the time. The art store's guard refuses both acts without your typed words. May newest-mark-wins become a delegated
class? ✕ would move the picture to the art archive (one-command restore) instead of purging it, and each act would be
listed in your digest."

- **Yes, newest mark wins, ✕ archives (Recommended):** Your marks already are your decision; about 11 min a week back,
  plus the 35 typed "enact my sheet" nudges. A slip is restored with one command. Build cost: a `retire` path in
  `art.py` and a guard exception tied to your mark's timestamp.
- **Yes, but ✕ on live art waits until its replacement is installed:** Never ships a hole in the game. Costs the
  delay you rejected 5 out of 5 times after 10-09 ("Delete now").
- **Only newest-mark-wins; ✕ still asks:** Removes the conflict cards, which are the safer half. Keeps about half the
  cards.
- **No, keep asking:** Your typed words stay on every act on kept art. Costs about 11 min a week.

### Card 3: Restart the game when it is free and you are not playing

**Question:** "On 10-17 you said 'As long as bridge is available (set up a watcher to check) it can be yours', but
the bridge command is still reserved to you. Since then, restart and bridge handoffs cost about 139 typed messages
and 16 cards in 3 weeks. Every time you said no, it was because you were live ('the game is NOT down', 'I pre-check
alone first'). May a seat take the free bridge, deploy and restart on its own when a watcher shows no other seat holds
it and you have not touched the game for 20 minutes? Never for flyer flight."

- **Yes, free bridge and 20 minutes idle (Recommended):** Matches your 10-17 words and covers every "no" you gave;
  about 11 min a week back. Build cost: an idle-input probe and a watcher. Risk: closing a game you were only watching;
  a restart costs about 1 to 25 minutes, and nothing is lost.
- **Yes, but only overnight or when you say 'I'm away':** No chance of interrupting you. Daytime handoffs stay manual.
- **Only on the small test mod list:** The full list (about 25 min to load) stays yours. Fewer surprises; about half
  the saving.
- **No:** The bridge stays yours. Costs about 16 min a week of handoff messages.

### Card 4: Delete our own unused leftovers on a check

**Question:** "Cleanup cards (old dev saves, scratch clones, orphan mandrake mod folders, settings or pictures nothing
reads, patches aimed at retired mods) reached you 21 times in 3 weeks, plus 42 typed cleanup messages. In 18 of 21
you chose delete or archive, often more than we proposed ('Delete all 116', 'Delete the intermediates', 'No residual
trash'). May agents delete our own leftovers when a check proves nothing reads them and everything is pushed, after
archiving or bundling them, and list each in your digest?"

- **Yes, archive then delete, listed in the digest (Recommended):** Matches 86% of your answers; about 10 min a week
  back. A bundle or archive makes any slip recoverable. Build cost: one reference-and-pushed checker covering saves,
  folders, settings and patches.
- **Yes, but archive only, and you empty the archive monthly:** Nothing is ever truly gone without you. Disk fills
  until you empty it (we have had 87 to 373 GB piles).
- **Only the kinds already ruled (clones, saves):** Narrow and safe. Mod folders and dead settings keep asking.
- **No:** Every deletion asks you.

### Card 5: Apply your rulings to their twins without asking

**Question:** "When you cut a creature from a biome, agents sometimes ask whether the same cut applies to that
biome's campaign copy or sister version. That happened 9 times in 3 weeks, and you said yes 8 times (for example
'Yes, both' for the Abyss and Leaning Scrub twins). Your policy already lets agents apply a ruling to a case it does
not name. May agents apply each ruling to its twins automatically, note it on the item, and list it in your digest?"

- **Yes, apply to twins, listed in the digest (Recommended):** 8 of 9 answers were yes, and the policy already allows
  it; a small saving (about 2 min a week), but it removes a whole kind of card. A wrong twin is reverted from git.
- **Yes, but only for cuts, not additions:** Your one "no" was about porting creatures, which is an addition. Safer.
  It keeps the rare addition cards.
- **No:** Twins ask you each time.

## 4. Classes that must stay his

These classes fail a property or touch a reserved line, so no card is proposed for them.

- **North-star bars:** §2.1.
- **Conflicts between his own rulings, and canon departures:** §2.4. Agreement is 45 to 48%, and he chooses play over
  canon.
- **Mod-list retirement:** §2.2. It is not reversible in a save, and agreement is 48%.
- **Design bulk, names, numbers and design proposals:** already §1-delegated as a policy, but agreement is 41 to 69%.
  His free answers carry new requirements, so the cards there are mostly real.
- **Purge from the art store:** stays `--owner-said`. Card 2 deliberately proposes archiving, not purging.

**Owed after this document:** answers to cards 1 to 5. If card 2 is answered yes, `art.py retire` must be built. If
card 3 is answered yes, an idle-input probe must be built.
