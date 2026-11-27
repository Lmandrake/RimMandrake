# Offline simulations: what we have, and where one would pay (census, 2026-11-26)

For Mandrake. Item `RIMMANDRAKE_CENSUS_SIMULATIONS_ASK_AT_DESIGN_FIRE_HAS_ONE`; your card of 2026-11-26, 6:15 PM PST:
"Census now, plus a design rule". The rows, files and faults are in `evidence.md` beside this page
(`D:\Luke\dev\RimMandrake\design\specs\2026-11-26-simulation-census\evidence.md`). Nothing is built and no ticket is
filed. You pick.

**Words.** An offline simulation runs the logic of a mod or a tool with no live game and no live machine, over many
cases. "Real code" means that the simulation runs the shipped code against a fake clock, machine or game. "Copy" means
that a second copy of the logic runs. A copy can drift from the shipped code.

**The Conductor's reading, not your words** (it decided the classes): a simulation pays where the logic is a state
machine or physics with many cases and the live test is slow. A simulation does not pay for art, for a def with no
logic, or for a thing that one cheap live look decides. Prefer real code. A copy needs a check against live readings.

## The count: 24 rows

| class | mods | pipeline | all |
|---|---|---|---|
| HAS ONE | 13 | 3 | 16 |
| WOULD BENEFIT | 1 (a guess) | 6 | 7 |
| WOULD NOT | 1 | 0 | 1 |

## What exists `[measured: files read 2026-11-26]`

- **Thirteen mods** run their shipped Verse-free decision code (the kernels) under a seeded dotnet fuzz. Real code.
- **Explosive Knockback** also asks the game's own sight-line code on a hand-built map: 0 of 999,162 lines differ
  from its model. Real game code.
- **Pyrelands** has a whole-map burn model (`pyre_burn_sim.py`). It is a copy, fitted to your two-week walk saves.
- **Gimme Some Slack** lays a dumped live colony's cords with the production builder (`LabWorld.cs`). Real code.
- **The account plan** has a sweep: the real pass, one simulated week, 378 regimes. On 2026-11-25 it found 5 kinds of
  wrong switch before any of them happened live. A replay runs the real rule over 14 days of recorded readings.
- **The Conductor window restart** runs the real Dispatcher tick over real child processes on a simulated clock.
- **The six process models** (`src/RimMandrake/Utils/sim/`) compare architectures. They are copies of the process.
  They model the retired builder seat and the 2026-10 era, not today's pipeline.

## Where a simulation would pay most `[measured hours, 2026-11-12 to 2026-11-26]`

Each row names the faults that a simulation of the real code would have shown before they cost live or stuck hours.
Hours that overlap are added, so each total is an upper bound `[guess ~70% that the order holds]`.

| rank | what | hours | faults that a simulation would have shown |
|---|---|---|---|
| 1 | SteveDesktop test lane | about 64 | a pause with no end held work 49 h; Steve2 repeated one refusal 47 times in 11 h; the account gate refused every launch 3.6 h |
| 2 | Ticket lane (`list_dispatch.py`) | about 57 | a block on a finished ticket stopped a chain 16 h; 4 tickets at the chain limit have no next step (31 to 39 h); the load line held the lane 2.2 h |
| 3 | Maturation Pipeline tick | about 53 | a mod that rests after its pass keeps its open tickets (Gimme Some Slack 45 h); refused loads counted as visit failures spent 6 visit chains, feed quiet 6 h; a deploy given to a steward that may not stop the game waited 2 h |
| 4 | The publish door and clone levels | about 22 | refused closes that say only "nothing to publish" (up to 15 h); a twin ledger commit held 3 h while every landing said level; the tick's clone stuck 2.5 h, 39 min and 30 min on files that no landing carried |
| 5 | Work bundles | about 10 | no lane run reached SteveDesktop for 10 h after bundles began; the launcher made one-ticket bundles |

Also WOULD BENEFIT, ranked last: the game locks (a dead holder's OWNER lock refused every take; stale mod-list swap
markers; hours UNMEASURED), and the Deep Desert Tribes mod (a guess: it sleeps, so it had no faults).

**The form that fits ranks 1 to 5** `[guess ~60%]`: the account sweep's form. Run the real tick or lane code every
step of a simulated day, with stand-ins only for what touches the world (games, ssh, the meter, git). Then check, on
every step, that no ticket, job or mod stays in a state that nothing ends. Four of the five rows lost their hours to
such a state.

**The gap beside HAS ONE.** A kernel fuzz does not run the code that calls the kernel. A measured trial on 2026-11-07
caught 0 of 31 planted faults in callers and 21 of 21 in kernels. The game-code probe of 2026-11-25 shows that some
callers can now run offline.

## The rule, from now (in `CLAUDE.md`, `standing_rulings.md` and `designer.md`)

Each design of a new mod, each scope proposal page of a next version, and each boundary page of new pipeline machinery
that is a state machine answers in writing: "offline simulation: yes or no, and why". A yes names what the simulation
covers and its form. It moves no current bar.

## What I could not look at

Codex runs. Hours that nobody recorded (the feed that ran dry on 2026-11-25, SteveDesktop idle while the ticket lane
had work). Live faults inside each mod that a caller simulation would have caught: I did not class them mod by mod.
