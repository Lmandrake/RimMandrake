# Three quick measurements: his card answers, where tickets are born, and factory work against game work

Item: `RIMMANDRAKE_TRY_NIGHT_HYPOTHESES_ON_RUNNING_FACTORY_BETTER`. Bears on hypotheses
`RIMMANDRAKE_SEND_CARDS_AS_NOTICES_WITH_UNDO_OVERRULED_OFTEN` and
`RIMMANDRAKE_BUDGET_FACTORY_SHARE_TICKETS_BORN_IN_RUNS` in `00-hypotheses.md`.

**What these are, said plainly.** Unlike the first two experiments, no for-and-against line was written to a file
before these three counts were run. I held a guess for each and give it below as recalled, which is weaker
evidence of a prediction than a file with an earlier timestamp. Treat these as measurements, not as tests.
All three were inline reads (2026-11-19, about 12:54 AM PST); nothing was written anywhere but the scratch folder.

## His card answers

- **Guess held before the count:** he picks the recommended option at least 9 times in 10, so a card could act at
  once and offer an undo.
- **Source:** the card store, `D:\ClaudeWork\rimmandrake\cards\cards.jsonl`: 127 cards, 303 questions, answered
  2026-11-15 to 2026-11-19 [measured]. A sanity reading that the instrument can see: 82 questions carry no
  recommended option and were set aside, so the "recommended" test is not matching everything.

| of the 221 questions that carried a recommended option | questions | share |
|---|---|---|
| he picked the recommended option, no words of his own | 127 | 57% |
| he picked it and added his own words | 8 | 4% |
| he picked another option | 38 | 17% |
| he answered in his own words, picking no option | 48 | 22% |

[measured.] Across all 303 questions he wrote words of his own on 85 (28%).

- **Result: the guess was wrong.** He departs from the recommendation about 4 times in 10. A card is doing real
  work. The useful reading is the opposite of my hypothesis: 48 answers in his own words mean that, about 1 time
  in 5, none of the offered options was the answer.
- **Not measured:** how long work waited on each card (the store holds the answer time, not the asking time);
  whether the departures cluster on one kind of question.

## Where tickets are born

- **Guess held before the count:** more tickets are filed than ended on most days.
- **Source:** every `file`, `close`, `drop` and `supersede` event in `infrastructure/state/ledger/events/*.jsonl`
  with a time on or after 2026-11-12 12:00 AM PST. No such event lacked a time [measured: 0].

| day (Pacific) | filed | filed from inside a run | closed | dropped or superseded | filed per ended |
|---|---|---|---|---|---|
| 11-12 | 141 | 64 | 34 | 8 | 3.36 |
| 11-13 | 78 | 51 | 25 | 40 | 1.20 |
| 11-14 | 55 | 26 | 25 | 10 | 1.57 |
| 11-15 | 421 | 321 | 262 | 148 | 1.03 |
| 11-16 | 221 | 162 | 181 | 37 | 1.01 |
| 11-17 | 137 | 47 | 120 | 5 | 1.10 |
| 11-18 | 256 | 198 | 365 | 175 | 0.47 |

[measured.] Week: 1,309 filed, 869 of them (66%) from inside a run; 1,435 ended; net down 126. "Filed from inside
a run" means the event carries a `role_unit`.

- **Result: the guess held on six days of seven**, and the one day that broke it was the hand-ordered sweep of 377
  old tickets. Without that day the week is 1,053 filed against 895 ended.
- **Not measured:** which of the filed tickets are about the factory and which about the game. The `kind` field
  (task 595, bug 260, fix 225, build 61, owed 60, art 19, system 18, polish 18) does not say.

## Factory work against game work, by detached-helper spend

- **Guess held before the count:** over 70% of helper spend goes to the factory's own machinery.
- **Source:** the 81 items that detached helpers ran on in the window, each run's own spend from its transcript
  (so resumed sessions are counted once), 309.1 million weighted tokens in all [measured]. I labelled each item
  "game" or "factory" by its name [mine, ~85% per item]. Game: the five biome second-reader items, the five
  Utinni-lens rewrites, the four sea designs and the retired combined sea design, the pilot biome revision, the
  owner-words harvest off a concept, the trimmed-readings check, the tenancy-row cleanse, and three Graffiti or
  tribute items.

| | items | weighted tokens | share |
|---|---|---|---|
| game (all of it design reading and writing; none of it mod code) | 22 | 129.8 million | 42% |
| factory (pipeline code, tests, tools, records, reviews) | 59 | 179.3 million | 58% |

- **Result: the guess was too high.** 58%, not over 70%. Two limits matter more than the number: this is one day,
  and mod builds run inside the Maturation Pipeline, whose runs are not detached helpers and are not in this count.
