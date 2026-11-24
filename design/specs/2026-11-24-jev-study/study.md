# Jev, a very cheap typed-judgment model: where could it help RimMandrake?

Study of 2026-11-24 for the item `RIMMANDRAKE_STUDY_JEV_CHEAP_JUDGMENT_MODEL_ASKED_ONCE_BEFORE_FABLE`. One Fable
Designer run. Nothing was built and no live machinery changed. The trial that this study recommends is in
`trial.md` beside this file. Every figure is marked `[measured]` (by this run, today, unless a date is given),
`[published]` (a vendor's or an author's claim that this run did not check) or `[guess ~N%]`.

**What Jev is.** Jev is a hosted model of the company TypeSafe AI. Jev writes no text. A program sends Jev a
`state` (any JSON) and a map of typed questions. Jev answers each question with a pick from a closed set, a
probability of yes, or a place on a scale, and gives a probability with each answer.

## The answer in five lines

1. **The interface does what the vendor says.** One call takes 129 to 141 ms `[measured]`, the time does not grow
   from 1 question to 15 `[measured]`, and one call costs about 8 weighted tokens `[measured, ≈ from dollars]`.
2. **On our own records, Jev's judgment is weak.** Jev was at chance on mixed tickets, fair on defect tickets and
   poor on review findings. Its stated probability did not match how often it was right `[measured]`.
3. **A word count trained on our own labels beat Jev on both sets** `[measured]`. The cause is not the model: the
   fact that decides our "quick" calls is usually not in the text that the call would read.
4. **At build time the honest answer is "little here today".** One small trial is worth its cost: a peek at what
   each live run is doing. `trial.md` holds its pass line.
5. **At play time, a call to Jev breaks the in-game law** (a hosted key). The route that needs no ruling is to
   compile the judgments at build time and ship them as data. A true play-time call would want a local model,
   and a new ruling from the owner.

## What was measured

Model `jev-1.14.0`, through the provider `~/dev/Dispatch/providers/jev`, about 450 calls. All questions were
written before the first run and were not tuned afterwards. Scripts, question text and every answer are in
`evidence/` beside this file.

| measurement | reading |
|---|---|
| Latency, one call at a time, 12 calls each | 1 question 129 ms, 5 questions 133 ms, 15 questions 141 ms (median) `[measured]` |
| Latency, 6 calls at once, 293 calls | median 141 ms, slowest 1167 ms `[measured]` |
| Size of a call | 452 input tokens for 1 question, 790 for 5, 1754 for 15 `[measured]` |
| Price | $0.042 per million input tokens, output free `[published, vendor's models page read today]` |
| Price in weighted tokens | 1 Jev token ≈ 0.0105 weighted token (Opus 5.5 input = 1); a 5-question call ≈ 8 `[measured ≈]` |
| Spend of this whole study | about 370,000 Jev tokens ≈ 3,900 weighted tokens `[measured ≈]` |
| Same request sent 10 times | the same pick 10 of 10, but its probability moved between 0.83 and 0.88 `[measured]` |
| Image input (new since the first study) | one 140 KB picture: 165 to 196 ms, 3045 tokens; one 6.7 MB capture refused ("Invalid image dimensions") `[measured, 2 pictures]` |

Jev is not in `MODEL_PRICES`, so each weighted figure for Jev is converted from the dollar price and marked `≈`.

### Labelled set 1: is a ticket worth the touch?

The labels come from the ledger. Label "dropped": the 105 tickets that the Conductor or the owner dropped with the
reason "not worth the touch" (2026-11-21 to 2026-11-24). Label "fixed": tickets closed with a commit since
2026-11-21. Jev saw only what the filer wrote: the title and the filing reason. Jev answered five questions: a
verdict (fix it, or not worth the touch) and four plain facts (a failure was seen; the problem is only predicted;
ordinary use reaches it; the change is wording only).

| set | Jev's verdict | separation (AUC; 0.5 is chance, 1.0 is perfect) | Jev says p ≥ 0.9: how often right | word-count floor (AUC) |
|---|---|---|---|---|
| all kinds, 105 dropped and 105 fixed | right on 44% | 0.47 | 43% of 74 | 0.94 |
| defect tickets only (kinds bug and fix), 29 dropped and 102 fixed | right on 77% | 0.71 | 86% of 63 | 0.77 |
| 105 dropped (all kinds) and 102 fixed defects | right on 61%; kept 94 of 102 fixed; caught 33 of 105 dropped | 0.76 | 73% of 75 | 0.89 |

All rows `[measured]`. The word-count floor is a naive Bayes count of words, trained on our labels and scored on
tickets that it did not train on.

- **No threshold makes Jev a safe screen.** In the first set, among 25 tickets that Jev called "not worth the
  touch" at 0.9 or more, 23 were really fixed `[measured]`.
- **A small model fitted on Jev's five answers did not help**: AUC 0.76, and at its best point it caught 20 of 105
  drops while it flagged 5 of 102 fixed tickets `[measured]`. The fit did repair the probability: tickets that it
  gave 0.6 to 0.8 were fixed 73% of the time.
- **Why Jev fails here.** The question "was a failure seen?" ran backwards on the first set: the dropped tickets
  report seen failures more often than the fixed ones do. The Conductor's drop reasons name facts that the ticket
  does not hold: "Relentless is retired", "never reproduced since 2026-11-16", "the throwing frame is a
  third-party mod". No reader of the ticket alone can know these facts.
- **Limits of this set.** "Fixed" means that someone did the work, not that the work was worth it. The fixed
  tickets are newer than many dropped ones, and the word-count floor may read the age of a ticket from its
  vocabulary. The floor's lead is real but smaller than it looks `[guess ~70%]`.

### Labelled set 2: is a review finding significant, or polish?

Label "polish": 45 lines from the `polish.md` lists. Label "significant": 58 tickets that came from a review and
were then fixed. Lines that held the words "significant", "polish" or "nit" were left out.

Jev was right on 53%, AUC 0.61. When Jev said 0.9 or more it was right 71% of the time (38 cases). The word-count
floor reached AUC 0.94 `[measured]`. Polish lines and tickets differ in style (a polish line often starts with a
file path), and the floor can read that style, so this set flatters the floor.

### What could not be measured, and what would settle it

- **Class of a failed check (mod wrong, check wrong, scene wrong).** The ledger holds 163 triaged findings
  `[measured]`, but 77 say only "the row passes in a later run" and most others say "tracked in <item>". Three
  clean classes are not recorded. To settle it: 40 failed rows classed by hand from run records.
- **The seven outcomes of a live run.** The ledger holds 8 runs with an outcome word, all of them COULD NOT LOOK
  `[measured]`. There is no set to test on.
- **Accuracy on pictures, and duplicates.** Not run. Two pictures show only that the call works.

## What the first study proposed, and what happened to it

The first study is `design/RimMandrake/Jev_Opportunities.md` (2026-09-28: a scan of 40 places, then a GPT review
that cut most of them).

- **It proposed** five text-against-text checks (a live item that cites a closed item; a line that asserts a
  number or only quotes it; a visual brief against its source; a stated reason for a species in two biomes; a
  duplicate screen at filing), one new category (classify once at build time and keep the result as reviewable
  data), and a first experiment of two parts. It withdrew every play-time use until the owner ruled on the
  transport.
- **None of the five checks was built, and the first experiment did not run** `[measured: no commit and no ledger
  item names them]`.
- **One different thing was built**: a shadow-mode Jev caller in the test runner
  (`src/RimMandrake/Utils/modcheck/jev_triage.py` and `jev_questions.py`, commit `8741c95450`, 2026-10-01). It
  routes failed components and acts on nothing, because each of its thresholds is unset.
- **That caller was never calibrated.** Archmagi had no key on that day. The key arrived on 2026-10-10 (item
  `JEV_KEY_ARCHMAGI_1`, closed). The shadow log that was to set the thresholds does not exist in this clone or in
  the bench clone `[measured]`. On 2026-11-05 a scoring of 29 fast-testing ideas put "Jev small judgments" at
  rank 22 (`design/RimMandrake/fast_testing_2026-11-05/scored.md`).

The first study's main finding still holds, and today's numbers support it: a cheap judge does not help where
an input is missing.

## Build time: the opportunities, ranked by value against cost

"Saving" compares one Jev call with what does the job today. The ratings are the Designer's own.

| # | opportunity | evidence | saving | cost of a wrong answer, and what catches it | how to test it | novelty / real gain |
|---|---|---|---|---|---|---|
| 1 | **Peek at a live run**: name what each run is doing now (reads, builds, tests, drives a game, waits, repeats a failed act) from the last events of its transcript | The owner asked for this on 2026-11-24. Nothing does it today. The answer is in the text that Jev reads. | About 30 weighted tokens a look, against about 10,000 for a Sonnet reader of the same tail `[guess ~50%]` | A wrong word on a status page. The raw last line stands beside it. It must never feed a stop or a void. | `trial.md`: 80 labelled windows; Jev against a plain rule on tool names | low / small but real. The plain rule may do as well `[guess ~55%]` |
| 2 | **Inhabited reaction table, compiled at build time** (see the play-time section) | 294 authored characters `[measured 2026-09-28]`; today's sample gave sensible, different picks for five characters `[measured, 5 cases]` | Small: about 37,000 weighted tokens for the whole table against about 400,000 on Opus `[guess ~40%]`. The value is the table, not the model. | A character acts out of character. A judge agent reads a sample; the table is data that anyone can edit. | A blind judge compares 40 cells filled by Jev with 40 filled by Opus | medium / medium, when Inhabited is in the pipeline |
| 3 | **Screen a capture before an image judge reads it** (black frame, menu, wrong subject) | Image input is new. The vendor calls it prototype grade `[published]`. Two pictures tried. | About 32 weighted tokens a picture against a few thousand for an Opus look `[guess ~50%]`; it saves only on bad frames, and their rate is unknown | A good frame is taken again, or a bad frame passes and the Opus judge catches it | 40 captures labelled usable, black or menu | medium / unknown |
| 4 | Ticket triage: worth the touch | Set 1 above: AUC 0.47 to 0.76 | none | A real fault is dropped. Nothing catches it. | done today: it fails | low / none |
| 5 | Review finding: significant or polish | Set 2 above: AUC 0.61 | none | A significant finding is lost on a polish list | done today: it fails | low / none |
| 6 | Ticket triage: already fixed (the brief: a Codex lane closed 13 of 28 so today) | The answer is in the code, not in the ticket | none | A ticket closes with its fault alive | not a Jev job; keep the Codex lane | none |
| 7 | Class of a failed check; the seven outcomes of a run | No clean labels. The cause is in the game state. | unknown | A mod is sent back for a fault of the check | first make 40 labels by hand | low / small `[guess ~80%]` |
| 8 | Duplicates at filing; routing of a new item; an unclear brief sentence | 28 of 1030 drops name a duplicate or a successor `[measured, crude word match]` | small | A ticket is wrongly merged | not worth a test now | low / small |

Rows 4 to 8 fail test 1 of "Touching code has a cost": nobody would care about the fix that they offer.

**A plain result that costs nothing to use:** for ticket triage, a word count trained on our own closed tickets
separated the sets better than Jev did. If a pre-screen of tickets is ever wanted, test that floor first, on
tickets split by filing date.

## Play time: Inhabited and the mods

**What a typed judgment in 130 ms could do.** Inhabited gives each place a cast of named people, each with a role
and traits (`design/Jawa/bridge/INHABITED_DESIGN.md`). Three uses fit the interface:

- **A choice among authored acts.** A gravship lands near the refinery: does this person keep working, watch,
  greet and trade, hide, fetch the guards, or leave? In today's sample the gruff foreman fetched the guards
  (p 0.87), the greedy trader went to trade (0.53), the timid drudge hid (0.73), and the bored guard watched
  (0.70) `[measured, 5 cases]`.
- **A stance on a scale** (hostile to friendly), from the same state.
- **Which authored line to say.** A Choice takes up to 255 options `[published]`, so Jev can pick one line from a
  character's own pool to fit the moment.

**The conflict, stated plainly.** The standing ruling of 2026-09-05 says: in-game LLM access is the Claude Code
CLI (`claude -p` as a subprocess), never an HTTP call with a hosted API key
(`design/RimMandrake/standing_rulings.md` §In-game LLM access). A play-time call to Jev is exactly an HTTP call
with a hosted key. This study does not design round that ruling. For Jev to be called in play, the owner would
have to change the ruling to allow a second transport. That ruling is his. Three of his five acts follow from
it: a money spend (our key, or a relay that we run), publication (a mod that calls out), and his walk.

**What a play-time call would need, whatever model answers:**

- **Network and an account.** Each player needs a TypeSafe key, or we run and pay for a relay. Every DLC is
  assumed; a TypeSafe account cannot be.
- **Privacy.** Colony state leaves the player's machine. Third-party pages say that the vendor's default
  retention is vague and that zero retention is for enterprise customers only `[published, not checked on the
  vendor's own pages]`.
- **Offline.** Law 2 of `design/RimMandrake/llm_ingame_wiring_spec.md` already rules this: the game is whole
  with the model absent. Each call needs a prescribed fallback.
- **Determinism for tests and saves.** The same request did not return the same probability twice `[measured]`.
  So the game must store each decision in the save, apply it at most once, and never ask again on a reload. A
  kind A live test cannot depend on a live call: tests must run with the fallback or with a recorded answer.
- **Law 1 (text or menu authority).** A typed pick is a menu pick, so the shape fits. C# must still check that
  the picked act is legal at that moment.
- **A readable sign.** No pawn does a thing without a sign that the player can read. A picked line is its own
  sign. A picked act needs a bubble or a letter that says why ("Orra saw the guns and ran for the guards").

**The route that needs no ruling: decide at build time, ship data.** Ask the model once, at build time, for each
character and each class of event (a ship lands, strangers come armed, strangers come to trade, a crewmate is
shot, the larder is empty). Store the answers as a reaction table in the mod's XML. In play, C# reads the table.

- Size: 294 characters × about 20 classes of event ≈ 5,900 calls ≈ 3.5 million Jev tokens ≈ 37,000 weighted
  tokens `[guess ~60%]`.
- The game then needs no network, no account and no key. It is deterministic, and the table can be read,
  judged and edited.
- The cost: the judgment sees a class of event, never the live colony. For "wasn't that guy working a refinery
  a while ago?", a class of event is enough `[guess ~60%]`.
- Any model can fill the table. Jev's edge over an Opus pass is a small one-time cost.

**If a true play-time judgment is wanted later**, a local model fits the present law better than Jev does: a
sidecar process with no key and no network, the same shape as `claude -p`. The ruling of 2026-09-05 struck the
"local Ollama fallback" by name, so this also needs the owner's word.

## Others like it

All but the first row are `[published]`, taken from the survey in
`~/dev/Dispatch/docs/research/2026-11-05-decision-models/FINDINGS.md` and one web search today. This run did not
check them again.

| option | what it is | good at | cost |
|---|---|---|---|
| **Word count or embedding + logistic regression** | a classic model trained on our own labels | our own repeated calls, once about 100 labels exist; it beat Jev twice today `[measured]` | free, local, about 1 ms; needs labels and a retrain when our vocabulary moves |
| **Zero-shot encoders** (GLiClass; DeBERTa-v3 and ModernBERT "zeroshot" models) | 150 to 450 MB, MIT or Apache licence, ONNX builds for CPU | closed-set picks with no labels and no account; the realistic play-time class | free; tens to hundreds of ms on CPU; the probability must be fitted on our own data |
| **GLiNER2.5-Decide** (Fastino) | Apache 2.0 encoder; labels given at call time | single-label picks; a fitted temperature took its calibration error from 0.160 to 0.028 | free; about 300 ms on CPU, 25 ms on a GPU |
| **Kev** | Apache 2.0, 0.8 to 9 billion parameters; serves Jev's own request shape on the local machine | a drop-in if TypeSafe goes away; more world knowledge than an encoder | free; 149 ms for 5 questions on an Apple M5; wants a GPU |
| **Clef-flash** (Cloudflare) and **pplx-decider** (Perplexity) | hosted like Jev, and the weights are open | a second vendor with the same shape | $0.02 to $0.04 per million tokens |
| **Laya** | open, 421 million parameters, Jev's request shape, about 10 ms | nothing of ours: on 20 labelled items it answered "keep" to all 20 `[measured 2026-11-05, on a Mac]` | free |

One independent paper (arXiv 2609.37647; abstract only, read on 2026-11-05) scored Jev on 37 public sets: 95 to
99% on easy sets, and weak on "fine-grained or noisy labels and rubric-based judgments" `[published]`. Our two
sets are of that weak kind.

## The risks

- **The vendor changes or goes away.** `jev-latest` moved from 1.13 to 1.14 on 2026-10-14 `[published]`; this
  study's calls were answered by 1.14 `[measured]`. A threshold belongs to one model version: pin the version.
  Open models with the same request shape exist, so the request code is not the lock-in. The questions and the
  thresholds are.
- **Calibration that drifts, or was never there.** On our records the stated probability was not safe to act on
  `[measured]`. Fit it on our own labels, check it again after each model change, and never rank by confidence
  (already measured in `~/.claude/skills/consult-jev/SKILL.md`).
- **A cheap wrong answer that nobody checks.** A call that costs 8 weighted tokens tempts us to ask everywhere.
  Each use needs a named catcher. No Jev answer may drop a ticket, void a run or pass a bar.
- **Data that leaves the machine.** Build-time text is our own, in private repos; the risk is small. Play-time
  state belongs to a player; see the play-time section.
- **Text that argues for itself** can move an answer `[published]`, and agents with a stake write our tickets.

## Sources

- Vendor documents, fetched today: `https://docs.typesafe.ai/llms-full.txt` (models, images, model jaggedness,
  changelog).
- The provider and its findings: `~/dev/Dispatch/providers/jev/` (`docs/FINDINGS.md`).
- The survey of the class: `~/dev/Dispatch/docs/research/2026-11-05-decision-models/`.
- Our records: the ledger (`infrastructure/state/ledger/events/`), the `polish.md` lists, the first study.
- Pages on retention and hosting, found by web search today and not checked against the vendor:
  `https://www.eesel.ai/blog/typesafe-jev-pricing`,
  `https://jwatte.com/blog/typesafe-jev-system-one-sovereign-ai-stack/`.
- GLiClass: `https://github.com/Knowledgator/GLiClass`.
