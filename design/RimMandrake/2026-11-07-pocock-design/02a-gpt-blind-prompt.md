# Blind prompt sent to the second model (pass 2, step 1), 2026-11-07

You are advising a solo game-mod developer ("the owner") whose code is written almost entirely by AI agents. Answer from
the facts below; you have not seen anyone else's answer. Be concrete and opinionated.

## The project

A large RimWorld 1.6 modding project: 80 mod folders with an About.xml, in C# (Harmony patches, map components) and XML, plus a large Python
tooling layer: a ledger/ticket system and agent pipeline (`rimflow/`, 394 code files, 164k lines), utilities (`Utils/`,
1,807 files, 495k lines), and the biggest mod, FlowWorks (911 files, 277k lines). About 6,900 commits touched `src/` in
the last month (2026-10-07 to 2026-11-07), nearly all by agents. Every mod has a "functional script" (a live proof run
through a bridge into the running game) and offline selftests; some selftests use planted mutations to prove they can go
red. File reviews go to a second model (Codex) and a file is "clean" only when a full review finds nothing. Geometry is
solved offline in Python first, sweeping the whole space, before any C#; the game is used only for the final look.

## The owner's standing rulings that bind any answer

- **Agents decide nearly everything** (2026-10-22): technical, scope, design detail and art calls are delegated; only a
  short list needs him (acceptance bars he wrote, irreversible acts on others' work, replacing art he kept, changing his
  rulings, paid or outward acts, some live tests).
- **"Use it, break it, grow"** (2026-11-02): real live failures beat predictive "might be stronger" review rounds. Do
  not propose review ceremonies.
- **The builder writes its own verification** (2026-08-26), accepted for speed.
- **Acceptance bars are his.** Agents may add regression checks and new bars; loosening one is his.
- **He specifies by reacting**: show him something before asking him to decide.
- His minutes are the scarcest resource.

## What prompted this

He watched Matt Pocock's talk "Software Fundamentals Matter More Than Ever" and read Pocock's skills (mattpocock/skills).
The argument: agents accelerate code entropy, so the human should own module and interface design (the "grey box": you
design the interface and the tests at it; the agent owns the implementation). The skills' main ideas:

- **Deep modules** (Ousterhout): much behaviour behind a small interface. A **seam** is where behaviour can vary without
  editing there. **Deletion test**: imagine deleting a module; if complexity vanishes it was a pass-through, if it
  reappears across callers it earned its keep. **One adapter means a hypothetical seam; two means a real one.** An
  interface includes invariants, ordering and error modes, not just types.
- **TDD at pre-agreed seams**: before any test, the human confirms which seams are tested. Anti-patterns:
  implementation-coupled tests, **tautological** tests (expected value recomputed the way the code computes it), and
  horizontal slicing (all tests first).
- **Grilling**: interview the human in rounds until the design tree is resolved; facts are the agent's job, decisions
  the human's. Some questions are "ungrillable": build a throwaway prototype and react to it.
- **Domain glossary** (`GLOSSARY.md` with banned synonyms) and ADRs for hard-to-reverse, surprising, real trade-offs.
- **Architecture survey**: find hot spots from commit history, apply the deletion test, report deepening candidates.

He is weighing whether to become more involved in interface and module design himself.

## Facts measured today

**Hot spots, last month** (commits touching the file; commits whose subject reads as a fix; lines now):

| file | commits | fix | lines |
|---|---|---|---|
| rimflow/relentless.py (the agent pipeline; currently STOPPED pending a redesign sitting with the owner) | 248 | 32 | 8,494 |
| Utils/ops_watch.py (operations alarms) | 174 | 21 | 5,704 |
| FlowWorks SelfTest/Program.cs | 161 | 18 | 2,335 |
| FlowWorks validation.py (the mod's functional script) | 130 | 13 | 1,883 |
| rimflow/dispatcher.py (role scheduler) | 91 | 22 | 2,447 |
| FlowWorks RM_MapComponent_Excavation.cs | 89 | 11 | 4,103 |
| FlowWorks northstar/validation_v2.py | 84 | 11 | 5,156 |
| rimflow/seat_restart.py | 71 | 16 | 3,648 |
| rimflow/concept_tree.py (a design-tree linter) | 22 | 11 | 931 |

- Of 516 fix commits from 10-07 to 11-01, about 53% name a review round ("fix the fifth review pass"); from 11-02 (the
  "use it, break it" ruling) to 11-07, fix commits fell from 11% to 6% of all commits, and 35% of them name a review.
- `concept_tree.py`: 14 review rounds in about two hours on 11-01 hardened its Markdown input parsing against ever more
  exotic input (CommonMark fences, NFKC, zero-width characters); the hunt ended when the accepted input was narrowed
  ("sheet is plain bullets", "bracket allow-list").
- A month-old subsystem, `Utils/arena`, took 247 commits (55 fix) in 7 days and was then deleted when its trial ended.
- About 50 of 1,537 selftest files assert on source text (they read a `.py`/`.cs` file and check a string), rather than
  behaviour.

**The loops ("Artisan").** Three autonomous loops of fresh agent passes, each working one mod from where it stands to
something it would show the owner, with the owner's statement of the experience frozen and everything else (code, tests,
proofs) the agent's to change. A blind judge reads its done claim; then the owner looks. Zero acceptances so far. The
owner worries they write "nonsense code as they iteratively grope forward". What their branches show:

- **Graffiti**: its pure "kernel" (`RM_GraffitiKernel.cs`) grew from 21 to 62 static functions; one-line boolean gates
  doubled from 6 to 12 (e.g. `ThoughtActive(bool settingOn, bool onMap, bool spawned, bool markFound) => a && b && c && d`,
  one caller passing a literal `true` for the last). Older selftests of those gates are tautological
  (`Check(ThoughtActive(a,b,c,d) == (a && b && c && d))`), written before the loop by earlier builders; the loop's own new
  checks are mostly literal or behavioural invariants ("a psychopath mourns nobody", vertices stay inside the face).
- **GSS (cables)**: the same scene helpers (`line`, `perimeter`) are copied into four new scripts with drifting
  signatures. Its proof rows read the mod's own state through a probe, with explicit negative controls.
- **Pyrelands**: the loop rewrote its proof script heavily (lines added+deleted are 10x the net change); it dropped some
  rows ("canonical-save rows dropped") and tightened others (a row had passed while the heater heated nothing).
- Across all three: code churn is low (gross/net lines about 1.0 to 1.5 on most files), public interfaces mostly grow and
  rarely change (a few removed signatures), and code referenced nowhere is rare (about 5 of 660 declared names).
- The judge reads screenshots and claims, never the code.

## The two questions

1. Where would a **trial** of each idea above pay in this codebase? Propose a few small, bounded trials: the module, the
   idea, what the trial does, what result would say "it helps" and what would say "it doesn't", and the cost in agent
   time and in the owner's minutes. Rank by value per minute of his time.
2. Could these ideas keep the loops from writing poor code pass after pass? Give two or three genuinely different
   options, the cost each adds per pass, and how each fits "use it, break it". Say which you would pick.

Finally: if he takes the "more involved in interfaces" option, what should he actually do each week, and how many
minutes would it cost him? Say what you would advise.
