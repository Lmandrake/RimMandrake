# Proposal: lists of open work that are complete together, with every drop shown to the owner

Items: `RIMMANDRAKE_CENSUS_WHERE_OPEN_THINGS_LIVE_SEVEN_LISTS_STILL_DROP` (the census) and
`RIMMANDRAKE_RESUME_CENSUS_WITH_HIS_COMPLETENESS_RULE_LEDGER_ONLY_REJECTED` (this rewrite). Written 2026-11-22. The
evidence is `census.md` and `probe_results.md` beside this page. Nothing on this page is built.

## His rule, which this proposal serves

His words, 2026-11-22 7:05 PM PST: *"As for the "one list" stuff, if you show me JUST from the ledger... I will never
know what was dropped, and thus it will be even worse than today. I would rather have three lists that are together
complete then one list that isn't."*

So completeness outranks one-ness. The owner may read several lists. Together the lists must be complete, and the
owner must be able to see that they are complete. A list built from the stores shows only what someone filed. A drop is
the thing that nobody filed. So the check must start where a need starts, not where a need ends up.

## The diagnosis in one sentence

Needs start in nine places (a run's result, a wait's date, his typed words, a handoff, a status-page note, the
Conductor's own promises, a Designer turn, an ops alarm, a question card), and nothing compares those places with the
stores, so a need that never reached a store is invisible to every list.

## The origin streams: can a program read each one today?

"A home" is a store of record that names the need and has a next act: an open ledger item, an open owed item, or a
later ledger event that acts on it. The counts are from this sitting `[measured]` unless tagged.

| origin stream | where it starts | can a program read it today? | what counts as its home | reading now | cheapest change that makes it readable |
|---|---|---|---|---|---|
| a run's result | the `DETACHED run … ended` note and its `LEFT OPEN:` or `NEXT:` lines | yes (ledger notes) | a later act on the item by anyone other than the run | 18 open items end on a run result with no later act | none needed |
| an expired wait | the `until` of a `rimflow wait` | yes (ledger) | an event on the item after the date | 21 of 37 waits past their date with no event (census) | none needed |
| his typed words | the Conductor window's transcripts on Archmagi | yes (`probe_his_words.py`, 5 s, no model) | an `--owner-said` quote, or another ledger field with his words | 138 messages in 3 days: 82 quoted, 5 echoed, 51 no home; by hand, 14 of the 51 needed a home, and 7 of those 14 are standing instructions with none `[guess ~70%]` | none for Archmagi. Words typed on SteveDesktop or in other projects: UNMEASURED; the change is to copy that machine's transcripts over Tailscale each hour |
| a card answer | `cards.jsonl` (`card_capture.py`) | yes | a `--by-card` ledger event | 23 cards asked in 3 days, all answered; not matched to `--by-card` events in this sitting (UNMEASURED) | none needed; the match is one join |
| a card he never answered | an `AskUserQuestion` call in the transcripts | yes (the transcripts) | its answer | 0 unanswered in 3 days; 1 refused by a hook | none needed |
| a handoff pointer | `` `ID` — … NEXT: `` lines in `infrastructure/state/handoffs/` | yes (regular expression) | an open item or owed item that names the id | 24 not-done pointer ids have no owed item that names them; 11 have no carrier at all (census) | none needed |
| a note on a status page | the need lines of MATURATION_NOW and FLEET_NOW | partly: the pages are files, but a line does not name its source | the item or store that the line came from | UNMEASURED | each page writes its need lines also to a small JSON file, each line with its source item or store path |
| a promise the Conductor types to him | the Conductor's own messages in the transcripts ("I will", "next I", "owed") | yes, but noisy: a program finds promise phrases, and cannot tell a real promise from a phrase | an owed item filed in the same turn | UNMEASURED | a program finds candidate sentences; a model step judges them (cost below) |
| a Designer turn that waits on him | `designer_stage.py turns` | yes | an OWNER event on its item | 0 waiting | none needed |
| an ops alarm | `ops_watch\alarms.json` | yes | the alarm's item, open | 7 alarms (6 open, 1 pending): 4 point at an item that is closed, 1 at an item not in the ledger, 2 name no item. So 0 of 7 have an open home (`alarm_home_check.py` beside this page) | none needed to read it; to give it a home, see change C5 below |

A stream that no program can read is shown on the page as UNMEASURED, with the change that would make it readable.
It is never shown as empty.

## Matching his words by meaning: what a model step would cost, and what a program alone misses

- **A program alone** (`probe_his_words.py`) lists 51 messages in 3 days as "no home", about 17 a day. By my hand
  reading, about 2 a day of those carry a ruling, an instruction or a state change that has no home. The other 15 a day
  are chat, or have a home in other words. A program alone therefore shows him every real drop of this kind, inside a
  list that is mostly chat. It also misses a home that exists in other words (5 of the 51) and calls those NO HOME.
- **A model step** (Sonnet 5.5 reads each "no home" message beside the ledger events of its window, and answers NEEDS
  NONE, HAS A HOME IN OTHER WORDS, or NEEDS A HOME) cuts the list to about 2 rows a day. Cost: about 17 calls a day at
  about 4,000 input and 150 output tokens each, or about **40,000 weighted tokens a day** `[guess ~60%]`
  (`weighted_v2`, from `MODEL_PRICES`: Sonnet 5.5 input weighs 0.5 and output 2.5). The model step can be wrong in the
  dangerous direction: it can call a real ruling "chat". So the page keeps a link to the program's full list, and the
  model never deletes a row from it.

## Three options

### Option 1. Keep the lists; add one completeness check that every list shows

A new program, `origin_check.py`, reads each origin stream in the table above. It lists every entry that has no home,
with its stream, its age, and its words or title. It writes `NO_HOME.html` (a static page in the Typora theme that
`fleet_now.py` already reads, in the warm dark-brown palette) and one line of JSON.

FLEET_NOW and MATURATION_NOW each show one banner line from that JSON: "Not filed anywhere: N (oldest: 2 d). Streams
read: 8 of 10; UNMEASURED: words typed on SteveDesktop, status-page notes." The banner links to NO_HOME.html.

Lists that the owner no longer needs to read: STATUS_BOARD (deleted: it was retired on 2026-11-19 and is still
written), and the situation brief (stopped since 2026-11-19; the banner states what the brief promised). The two "needs
you" lists both call `owner_queue.is_his`, so they cannot disagree.

- **Gain:** the smallest build that answers his rule. Every drop of a readable stream is on a page that he already has
  open, with its age. The coverage line shows him which streams are read and which are not.
- **Cost:** three lists stay three lists. NO_HOME.html is mostly chat until the model step runs (about 17 rows a day).
- **Build effort:** one Opus helper run: the program (about 350 lines), its boundary page, and the two banner lines
  `[guess ~70%]`. **Test effort:** for each stream, one planted entry with no home must appear, and one planted entry
  with a home must not; one stream made unreadable must read UNMEASURED, not 0.

### Option 2. Two pages: what is filed, and what is not filed

The owner gets two pages that are complete together:

- `OPEN_NOW.html`, built from the stores: what is going on, what needs him (ready now with minutes; waiting on us
  first), and what is next (the Conductor's owed items, the expired waits, the open hand acts, the open alarms). Each
  row names its origin stream.
- `NO_HOME.html`, from Option 1's program.

At the top of OPEN_NOW, one line ties the two pages together: "Filed: N open. Not filed: M. Streams read: 8 of 10." (N and M are the live counts.)
The NEEDS YOU block of FLEET_NOW, the Needs Mandrake and Needs Conductor blocks of MATURATION_NOW, STATUS_BOARD and the
situation brief all stop and link to OPEN_NOW. FLEET_NOW keeps the machines and runs. MATURATION_NOW keeps the mods.

- **Gain:** one place for "what needs me" and one for "what fell". The owed queue, which no page shows today, is in
  front of him with its ages.
- **Cost:** the biggest build. A new page to learn. The owed queue in front of him can feel like pressure on him for
  work that is ours.
- **Build effort:** two Opus helper runs `[guess ~65%]`. **Test effort:** Option 1's tests, plus a parity test: every
  open owed item and every row that `is_his` returns appears on OPEN_NOW once.

### Option 3. Fix the hand-overs at the source, and measure the fix with the completeness check

The check shows drops. Changes at the source stop them. Each change below has a stream in the table, so the check
proves the change worked: the stream's "no home" count goes to zero.

- **C1, run result to the Conductor:** when a run ends with a `LEFT OPEN:` note that is not a relaunch, or with a
  "NEXT: the Conductor …" line, `run_end_wake.py` files one owed item with the run as its cause.
- **C2, an expired wait:** when a wait's date passes, the owed queue shows the item as ripe and late.
- **C3, a trigger on owed items:** `rimflow file --kind owed` takes `--until <date>` or `--when <ID> done`. An item
  before its trigger is not late.
- **C4, a launch is a launch:** an owed item whose act is "launch a helper with brief X" carries the brief's path, and
  Dispatch launches it when its trigger comes, inside the account rules. 8 of the 25 owed drops in the census are such
  launches.
- **C5, an alarm keeps an open home:** when an alarm is open and its item is closed, absent or not named, `ops_watch`
  reopens or files the alarm's one fixed item. Today none of the 6 open alarms has an open item.
- **C6, his words get a home in the turn:** at the end of each Conductor turn, a hook runs the words check on that
  turn's typed messages and puts any NO HOME message in front of the Conductor before its next reply.

- **Gain:** fewer drops, not only visible drops. The owed queue drains through Dispatch for the launch kind.
- **Cost:** six changes in pipeline machinery, each with its boundary page first. More owed items are filed at first,
  because hidden needs now get a home.
- **Build effort:** three helper runs `[guess ~60%]`. **Test effort:** each change has a test that is red before the
  change and green after it; C1 also needs a planted run result that files exactly one item.

## Recommendation

**Option 1 now, with C1, C2, C3 and C5 in the same build. Then C4 and C6, and the model step, after one week of
readings.** Option 1 meets his rule with the smallest build: the lists stay several, and every page that he already
reads shows the "not filed" count and which streams are read. C1, C2, C3 and C5 are small and remove the four largest
drop sources that the census measured. C4 touches the account rules, and C6 and the model step spend tokens each day,
so a week of readings first shows whether they pay. Option 2 is the step after Option 1, if he wants one page for
"what needs me".

## What this does about the owed queue growing faster than it drains

The census measured 190 owed items filed and 142 closed since 2026-11-15, a net growth of about 6 a day; the median
close was 2.1 h. A page does not drain a queue. Three things here do:

- **Close what is done.** This sitting closed 9 owed items on evidence (7 done, 2 that no longer matter) and one more
  after its fix (the conversion list). The owed count went from 48 to 38 `[measured]`. Option 1's program can also list
  "can close" rows (an owed item whose named items are all done, or whose named file exists) each night, for the
  Conductor to close.
- **Take launches off the Conductor (C4).**
- **Make the growth visible.** The banner line shows the owed count and how many were filed and closed per day.

His decisions in this proposal: none of the five kept acts. Option 1 adds no tab; Option 2 changes what his screen
shows, so the Conductor offers it to him, with Option 1 as the default.
