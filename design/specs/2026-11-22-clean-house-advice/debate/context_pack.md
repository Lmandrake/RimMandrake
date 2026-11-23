# Context pack for the skeptical debate on the clean-house advice

Written 2026-11-22, about 4:18 PM PST, for GPT. Every GPT call in this debate receives this page plus the files
listed under "Inlined files", whole. Tree: `f23afb0766`.

## What the project is (short)

RimMandrake is one person's private RimWorld 1.6 mod project (a Jawa scavenger clan on a desert world). It is also an
experimental "agent software factory": Claude agents (a "Conductor" window that the owner talks to, plus detached
helper runs launched as systemd units) design, build, test and judge the mods. GPT (through the Codex CLI) is used as
an independent second model. The owner is one human, Mandrake, who is also the only player-tester. `PURPOSE.md`
(inlined) says this in his framing.

The repository is 101 days old. It has had at least four pipeline designs in seven weeks; the current one is the
"Maturation Pipeline" (spec sections 0 to 3 inlined), in force since 2026-11-13.

## The owner's request that started the study (his words, 2026-11-22, about 3:26 PM PST)

> "INDEPENDENTLY again... I feel like there is a LOT of this in the project. Independent areas of the project that
> have re-invented the same thing a different way. I am getting nervous that we are just a creaking mass of cruft
> built up over months. Aside from a full "archive the project and re-build what we actually want, throwing away the
> rest," how might we clean house, consolidate what is redundant, deduce what common systems we REALLY need, and make
> it as deterministic as possible? I feel like I keep asking for studies like this, and they do not come back to me.
> Please advise. We need to make things more deterministic, more dependable, and less redundant. It is getting hard
> to keep fixing rather than building."

## The owner's request for this debate (his words, 2026-11-22, as the Conductor's brief gives it: about 4:25 PM PST)

> "Please take that whole study you just did and send it back to GPT with rich context for a skeptical
> re-examination. Force it to come up with alternative viewpoints and to argue each one, one agent per viewpoint.
> Then have them rebutt against the others. Finally bring it all together into a more coherent and hopefully more
> robust plan."

Note: two mods read OFF with the reason "owner 4:25 PM asked to slow the work and 4:38 PM made pipeline repairs top
priority: repair lanes may start, mod runs and biome design reads stay off". That control act (`ct_000026`) is dated
**2026-11-18**, not today (`./pipe why ExplosiveKnockback`, read 2026-11-22 about 4:25 PM PST). An earlier copy of this
page said it was from the same minute as the debate request; that was wrong. Round 0 and the first Round 1 calls saw the wrong copy.

## The study under examination

- `advice.md` (inlined whole): the study. A Fable (Claude) helper wrote it on 2026-11-22 about 4 PM PST. Each claim
  is tagged `[measured]` or `[guess ~N%]`. Its own blind spots are its section 9, "What I could not look at".
- `gpt_review.md` (inlined whole): the first GPT skeptical review of the study's draft. Section 10 of `advice.md`
  says what the study's author took from it and what not.

## Measured figures the study rests on, and how each was measured

All are from `advice.md`; the method is quoted from it. Tree `b8b9d42af8` unless named.

| figure | value | how measured |
|---|---|---|
| Owner study requests since 2026-10-29 | 21 (22 table rows; one was the Conductor's own) | owner-ruling grep for ~20 words plus a ledger replay of 9,714 items for 25 study words; 461 items read down to the process ones |
| Studies with no ledger record that he saw them | 13 (12 of his) | ledger events (card answer, his words, an "opened for him" item). Chat in the Conductor's window is NOT in the ledger |
| Transcript check of five "no record" studies | 2 never named to him; 3 named in 1 or 2 messages | file-name search of 4.9 GB of Conductor transcripts, classed by author; the messages themselves not read |
| Commits in 30 days | 25,484: ledger/state only 63%, machinery-only 15%, design-only 13%, mod-only 7%, mod+machinery 2% | `git log --since="30 days ago" --numstat`, classed by path. "Machinery" includes `Utils`, which also holds mod and art tools |
| Machinery-only : mod-only commits | 2.3 : 1 over 30 days; 3.8 : 1 in the last week (761 vs 198) | same |
| Detached-run tokens, 30 days | ~1,771 M weighted tokens (upper bound): mod 42%, machinery 32%, unclassed 26% | 933 run records weighed by `tokens_v2`; 405 records in an old unit (upper bound), 66 with no figure; Conductor windows UNMEASURED |
| Pipeline core `rimflow` | 202 Python files, 99,617 lines; tests 291 files, 100,477 lines | file count, not tests vs tests |
| Tools `Utils` | 1,000 Python files, 344,128 lines; tests 948 files, 172,550 lines | same |
| Mod C# | 3,104 files, 717,109 lines | same |
| Hooks | 34 programs, 38 registrations | settings files |
| Units | 83 in the tree, 30 timers installed | systemd |
| Ledger | 76,558 events, 9,714 items, 1,962 open, 990 idle 14+ days | `model.read()` replay |
| Hand acts | 98 in 9 days; 71 of the first 96 were a person deciding what the tick decides | the hand-acts list |
| Standing voids | 33 in 9 days | voids file |
| Rule files | root `CLAUDE.md` 734 lines, 48 sections; standing rulings 1,807 lines; charter 264; role files 21 files, 3,908 lines | `wc -l`; the root file is inlined so you can judge it |
| Mod versions passed with a tag | 1 | git tags; the tag rule began 2026-11-13 |
| Cost of today's seven consolidation runs | 12.2 M together, 1.2 to 2.1 M each | their run records |
| Cost of the current pipeline to reach today | at least 517 M of machinery runs over nine days | run records |
| Nightly test run | red on 29 of 29 nights | nightly records |
| Load-bearing share of tools | UNMEASURED; the study guesses fewer than 150 of ~1,200 tool files are on the mod path `[guess ~50%]` | no instrument |

Today's single-source sweep (`design/specs/2026-11-22-pipeline-single-source-sweep/report.md`, inlined) is the
evidence for "the same generic service built again by each run". Six of its groups were consolidated the same day.

## The current state of the mods (from `./pipe show`, 4:15 PM PST today, inlined)

Advancing: FlowWorks (in-game acceptance), Pyrelands (in-game acceptance), GimmeSomeSlack (at the owner's walk).
Held by the owner: six biome mods and Graffiti. Off: ExplosiveKnockback, PyrelandsMechanics, ColdStorage,
WreckedMachines. One mod version has passed with a tag under the current rules.

## What the study says it could not look at (its section 9, summarised; the full text is inlined)

The Conductor's transcripts beyond five file names; whether the owner read anything; the second test machine
(SteveDesktop); the behaviour (not just names) of sibling-repository tools; which files run in a normal week; spend
inside Conductor windows; any outside tool beyond a web search (none was run); elapsed time, tokens and owner minutes
per stage move.

## Inlined files

1. `design/specs/2026-11-22-clean-house-advice/advice.md` (the study)
2. `design/specs/2026-11-22-clean-house-advice/gpt_review.md` (the first GPT review)
3. `PURPOSE.md`
4. `design/specs/2026-11-13-maturation-pipeline.md`, lines 1 to 152 (how to read it, his words, the idea in eleven
   lines, the map)
5. `CLAUDE.md` (the root rule file that every agent reads; 734 lines)
6. `design/specs/2026-11-22-pipeline-single-source-sweep/report.md` (today's sweep)
7. `design/RimMandrake/retired_eras_index_2026-11-18.md`, lines 1 to 90 (the retired pipeline eras)
8. `./pipe show` output, 2026-11-22 4:15 PM PST

## Ground rules for every answer in this debate

- Argue from this evidence. Where you go beyond it, say so and tag the claim `[guess ~N%]`.
- Never invent a figure. "UNMEASURED" is a complete answer.
- Spend is in "weighted tokens" (M = million), not dollars. The owner pays a subscription, not API prices.
- Constraints that bind every viewpoint: the owner rejected "archive the project and rebuild" as a starting frame,
  but asked for alternatives to be argued fairly; he wants the system "more deterministic, more dependable, and less
  redundant"; he must be able to keep building mods; agents do nearly all the work, and the owner keeps five acts
  (live flight tests, replacing art he kept, the pass at his walk, money, publishing outside private repos).
