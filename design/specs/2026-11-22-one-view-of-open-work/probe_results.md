# Probe: which of his typed messages have a home in the ledger (2026-11-19 7:00 PM to 2026-11-22 7:00 PM PST)

Item: `RIMMANDRAKE_RESUME_CENSUS_WITH_HIS_COMPLETENESS_RULE_LEDGER_ONLY_REJECTED`. Run 2026-11-22 about 7:20 PM PST.
The program is `probe_his_words.py` beside this page. It makes no model call and runs in about 5 s.

```
python3 design/specs/2026-11-22-one-view-of-open-work/probe_his_words.py \
    --since 2026-11-20T03:00:00Z --until 2026-11-23T03:00:00Z --rows /tmp/probe_rows.json
```

## What the program reads, and how it decides

- **His messages:** every message typed into the Conductor window on Archmagi, from the window's transcripts
  (`~/.claude/projects/-home-mandrake-rm-bench/*.jsonl`). The program skips machine text: task notifications, wake and
  seat-restart prompts, and steward prompts. Card answers are tool results, so they are not counted here.
- **The homes:** every ledger event from one hour before the message to 72 hours after it.
  - QUOTED: an `--owner-said` field holds the message's words, or holds a quote of 5 or more words that lies inside
    the message.
  - ECHOED: some other ledger field (a note, a reason, a title, a card label) shares 8 words in a row with the message,
    or a quarter of its 5-word runs.
  - NO HOME: neither.
- **The controls (run in the same sitting):** a planted message of nonsense words read NO HOME. A planted copy of a
  real `--owner-said` quote read QUOTED. The first version of the matcher missed partial quotes (for example "They all
  look excellent to me", quoted from a longer message). I fixed the matcher before taking the reading below.

## The reading `[measured]`

| | QUOTED | ECHOED | NO HOME |
|---|---|---|---|
| under 8 words | 7 | 1 | 25 |
| 8 to 30 words | 24 | 1 | 16 |
| over 30 words | 51 | 3 | 10 |
| **all 138 messages** | **82** | **5** | **51** |

## The 51 messages with no home, read by hand

I read each of the 51 once. Each class is my judgement, so each row is `[guess ~70%]`.

- **32 need no home.** They are chat or acts that the session finished: "question cards?", "goodbye", "Sure, let's do
  it", the GPT sign-in he asked for, "I'm going afk. Goodnight."
- **5 have a home outside the quotes.** The ledger or a spec carries the same point in other words:
  - "We can run two games you know..." became his ruling of 2026-11-20 8:24 PM PST on two live games.
  - "Please, no 'let's check again' tasks" is in the title of an owed item.
  - "Not used at all" (SteveDesktop sound) is in a note.
  - The game names question became `design/specs/2026-11-22-game-names/`.
  - "In game look first" is in the carry item of 2026-11-22.
- **7 are standing instructions, rulings or state changes with no home that I could find:**
  - 2026-11-20 6:09 AM: *"Just please make sure it's as ready for my look as possible... nothing so stale that no
    matter what I say you just respond "oh yeah that's old""*
  - 2026-11-20 11:43 AM: *"A rare error once a day or so isn't too bad."* (the SteveDesktop lane)
  - 2026-11-20 6:31 PM: *"I'm really worried tickets don't capture everything needed to really understand the effect
    that but is having on the pipeline and how fixes would play out. You have that view right now. Will the fixer?"*
  - 2026-11-21 2:45 PM: *"Unfortunately I can no longer do the walk, I am about to go phone only. So that is released for now."* (no ledger event near that time records the walk's release)
  - 2026-11-21 1:11 AM: *"Beware. Asking for fable gets you 5.1. That full model name was importsnt if not handled
    correctly."*
  - 2026-11-21 5:44 PM: *"Override. Let it get to 1% before emergency cutover happens."*
  - 2026-11-22 1:06 PM: *"The image was captured at very low res, you should zoom in more or not compress before
    showing me."*
- **7 are questions or one-time orders that the session may have answered.** Examples: *"I am distressed that
  judging events are still being used to slowly improve testing definitions rather than game content"* (2026-11-20
  3:56 AM), *"Agreed. Remove it now."* (6:21 AM), *"I want to know the answer about 0.1%."* (5:21 AM).

## What the probe cannot see

- Messages that he typed anywhere else: on SteveDesktop, in a window of another project, or in a chat outside Claude
  Code. On Archmagi, only the Conductor window's transcripts hold messages in this window of time.
- Whether a message that has no home needs one. The program cannot tell "ok" from a ruling. A short ruling ("Thin
  outline") and a short reply ("Sure") look the same to it.
- Paraphrase. Five of the 51 had a home in other words, and the program called them NO HOME.
- Homes outside the ledger: specs, rule files, mod folders, memory. A home there is real, but the program does not
  read it.
