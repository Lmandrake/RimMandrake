# Your own patterns, reviewed

These are the habits you described and the ones visible in the repo. Most are sound;
the recommendations are adjustments, not replacements.

## §1 The 75% reboot ritual — keep the reboot, change what it does

The instinct (hand off before context degrades) is right. The current payload —
"consider moving some lessons to skill as appropriate" — is the skill-bloat pump
(RC5): the model edits long documents at peak context pressure and appends instead of
merging. Measured result: the same 52-line section three times in one skill.

**Revised ritual:**

1. At ~75%, say: *"prepare for reboot."* The window writes **two things only**:
   - a handoff note (current item, state, next step, open questions) — one screen,
     into the item or `Transient/`;
   - **one line per lesson** appended to `infrastructure/state/LESSONS_INBOX.md` —
     claim only, no essay: `sprite facings: generate individually, composite sheets
     drift — seen twice`.
2. **No skill, memory, or doctrine file is edited at reboot time. Ever.**
3. Fresh window resumes from the handoff note.

Also: reboot need has changed. This harness now summarizes and carries context across
the window boundary automatically, and Fable's effective horizon is longer than the
Opus 4.* sessions this ritual was built for. Keep the ritual for *seat handoffs you
want clean*, but you no longer need to treat 75% as a cliff — let sessions run, and
reboot at natural task boundaries instead of at a percentage.

## §2 Wake phrases — fine, and cheaper under the new topology

"Wake NAME and start your queue" / "wake and enter bench mode with me" is a good
interface. What made waking expensive was never the phrase — it was the 30–50k-token
doctrine tax behind it. With the charter (~1k tokens) plus lazy skill loading, a wake
becomes nearly free, and with two windows there are half as many of them. No change
needed on your side beyond having fewer windows to greet.

## §3 Skillbuilding: how and when to invoke it as the user

Skills are this project's best knowledge asset and its second-biggest token liability.
The discipline that keeps them assets:

**When to create a skill** — trigger it yourself when you notice any of:
- the **same lesson surfaced twice** in different sessions (once is an inbox line;
  twice is a skill);
- you just watched an agent **re-derive a procedure** you've seen derived before;
- a task needed **>3 non-obvious steps** and will recur (deploy rounds, load rounds,
  savegame surgery all earned theirs this way);
- an instrument **lied** and the workaround generalizes.

Say it explicitly — *"make this a skill"* or invoke `skill-creator` — at the moment
you notice, but have the agent write only the inbox line then; the skill itself gets
written/updated by the curation session below. A skill authored mid-task inherits the
task's tunnel vision.

**When NOT to create one:** one-off incidents (memory or inbox line), anything a hook
can enforce (hooks beat prose), anything CLAUDE.md/charter already covers in a line,
and any "lessons journal" without a procedure at its core.

**The curation session — the missing institution.** Once a week, or at each milestone
(a load round shipped, a v1 step closed), open a **fresh** window and say:
*"curation pass."* That session, and only that session:
1. drains `LESSONS_INBOX.md` into the right skills, **merging into existing sections
   rather than appending** (it has full context room to read the whole skill first);
2. deletes duplicated blocks (start with the known triplication in
   `generating-rimworld-sprites` and the 10k-word `traps.md` — its own contract says
   promote-and-prune; run the prune);
3. keeps each SKILL.md under ~2,500 words by moving depth to `references/` files that
   load only when needed — the description line does the triggering, the body should
   be procedure, not history;
4. regenerates the roster (`skills/README.md` is currently missing
   `rimworld-layout-layers`) and fixes descriptions that no longer trigger well;
5. runs on **Fable or Opus** — deciding what to delete is the hardest editorial task
   in the shop and the one place top-model spend on maintenance is justified.

This converts skill quality from a per-session gamble into a scheduled, cheap,
high-context habit — and it's the piece that makes the reboot ritual's "no skill
edits" rule sustainable.

**Memory hygiene, same principle, lighter touch:** the 76 memories are healthy, but
~5 restate CLAUDE.md/POLICY doctrine verbatim (the fan-out audit named the pairs).
The curation session may fold those in passing; memories should hold what the repo
does *not* record.

## §4 BENCH — generalize it, don't guard it

BENCH is the best process invention in the repo and the redesign's PAIR window is
just "BENCH as a permanent posture." Two refinements:

- The phrases you invented under duress — *"just do X"*, *"live dangerously"* —
  exist because the default posture was wrong. Under the charter they become the
  default, and the marked case flips: you say *"careful with this one"* when you
  want T3 treatment on something the table wouldn't catch. Opt into rigor, not out
  of it.
- *"You are checking too hard — close it and move on"* currently gets recorded as
  "closed at owner's bar," which quietly frames your judgment as the deviant case.
  Under the reversibility table it's simply the T1 default; no attribution needed.

## §5 Two numbers to watch instead of feelings

Both are free from the existing ledger, monthly or per-milestone:

1. **Median file→close wall time** — the "it takes forever" number. Should drop by an
   order of magnitude for T1 items.
2. **Process-share of commits** (fraction touching `infrastructure/|.claude/`) —
   currently 61% and rising. Healthy for this project's remaining v1 is ~30–35%.

If a fifth redesign is ever contemplated, these two numbers — not exasperation — are
what should trigger and evaluate it.
