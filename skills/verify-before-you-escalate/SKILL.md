---
name: verify-before-you-escalate
description: Run the one command that settles a written claim before acting on it, escalating it, or raising an alarm about it. Use when a doc, README, queue item, comment or teammate asserts something checkable — a count, a date, a staleness, a version, a flag, a path, a "this is broken" or "this is out of date" — and especially when that assertion is about to cost someone a slow resource, a rebuild, a restart, a rollback, or a message to another agent. Also use when a file's age or timestamp is your evidence, when two docs disagree about a number, when you are about to say something "gates" or "blocks" something else, and when a documented command errors — because the doc may simply be wrong.
---

# Verify before you escalate

Written claims decay. The doc was true when someone wrote it, the world moved, and
nobody re-ran the check. Then someone reads it, believes it, and spends real
resources on it.

The move is small: **before escalating on a claim, run the command that settles
it.** Seconds against a round trip through other agents, or a slow rebuild, or a
restart nobody needed.

Escalating on an unverified claim is worse than staying quiet, because an alarm
travels. It gets relayed, written into other docs, and acted on by people further
from the evidence than you were. A wrong alarm can outlive the thing it was wrong
about.

## The asymmetry that makes this always worth it

Verification is nearly free and its failure mode is a wasted second. Escalation is
expensive and its failure mode is other agents doing wrong work confidently.

So the bar is not "am I fairly sure?" It is: **is there a command that would settle
this, and have I run it?** If a command exists and you have not run it, you do not
have a finding — you have a hypothesis with a citation.

This does not mean verify everything. Claims you are about to *act* on cheaply and
reversibly are fine to act on. The trigger is when a claim is about to become an
alarm, a blocker, a scope call, or a claim on a scarce resource.

## The archetypes

Most bad claims are one of a few shapes. Recognising the shape tells you the command.

### Age is not freshness

A timestamp answers "when did this filesystem entry last change", which is not the
same question as "does this content describe the current world."

The classic trap: **a directory's mtime does not move when the files inside it are
overwritten in place.** No entries created, none deleted, so the directory looks
frozen while its contents are current. Read a folder date as staleness and you
invent a crisis.

Prefer, in order:

1. **A fingerprint or manifest the producer wrote** — a `capturedUtc`, a build ID, a
   recorded input set. This states what the artifact *is*, not when a file moved.
2. **A content check** — does the artifact contain the thing that was added
   recently, or lack the thing that was removed?
3. **A timestamp**, last, and only on the specific file you care about.

If a tool already answers the staleness question by comparing input sets rather
than clocks, that tool's verdict beats any timestamp you can read yourself.

### A number in prose is not a measurement

Counts get written once and copied forever. When two files disagree, neither is
evidence — go to the thing being counted and count it.

Then do the reconciling step, because it is the one that produces knowledge:
**diff the old set against the new one and attribute every difference.** "It is 575
now, not 585" is a correction. "It is 585 − 11 + 1 = 575, and here is the commit for
each" is a finding, and it also surfaces the changes nobody recorded — which is
usually the actual problem.

### A documented command is not a command

Flags get renamed, tools get rewritten, docs do not follow. Before reporting that a
documented command failed, check the tool's own interface: `--help`, the argument
parser, the source.

Watch for the dangerous recovery: a documented flag errors, someone reads the error
as "nothing to do", and skips straight to the destructive form of the command. When
you find a wrong command in a doc, **fix every copy of it**, because the reason it
is wrong in one place is that it was copied from another.

### "This is broken" is usually "this is unmeasured"

Absence of evidence arrives disguised as evidence of absence, especially when the
check itself is silently incapable — a validator that scans the wrong format, a
grep for a string the system never emits, a patch matcher that returns true when it
matches nothing.

Before reporting a defect, ask whether the check could have detected the healthy
case. If it could not, the finding is "we have no route to measure this", which is
a different and often more valuable thing to report.

## Choosing the settling command

Ask: **what would be different if the claim were false?** Then observe that thing
directly, as close to the source as you can get.

Cheap and decisive beats thorough. One `--help`, one count, one field out of a
manifest. If settling a claim looks like it needs a big investigation, you have
probably not found the decisive observation yet.

Prefer the artifact over any description of it, the producer's own record over your
inference, and the running system over the file on disk when they can differ.

## Bounding it

Do not run the analysis functions of a tool that also writes. When you need to
measure with a destructive tool, call the parts that compute and never the entry
point that commits — and say which you did, so nobody has to wonder whether your
measurement changed the thing measured.

Check your own harness before you trust a dramatic result. If a measurement
contradicts a teammate's, suspect your invocation first: an argument passed in the
wrong shape can produce a confident, catastrophic-looking number. A disagreement
with someone else's measurement is a reason to re-read your own command, not a
reason to escalate faster.

## Finish the job: correct the source

**A verification is not done when you know the answer. It is done when the wrong
claim is no longer written down.**

This is the step that gets skipped, and skipping it is what makes the same claim cost
somebody else the same trip next week. Recommending a fix is not fixing it. If you
have just proved a doc wrong and you can edit that doc, edit it — then say you did.

Two things that make the correction worth more than the fix itself:

- **Fix every copy.** A wrong claim is rarely alone; it is wrong in one place because
  it was copied from another. Search for it before you consider it corrected — the
  same flag, the same count, the same date, wherever it was propagated.
- **Record the trap, not just the correction.** "The date was wrong" helps nobody.
  "The folder mtime does not move because the dump overwrites the files in place —
  read the manifest's `capturedUtc`" stops the next person making the same inference.

Leave the check behind where you can: a claim that carries the command which proves
it does not decay the same way a bare number does.

## Reporting it

**When the claim was wrong**, say what is true, and say that you corrected the source.

**When the claim was right**, say so plainly and give the measurement, which turns a
citation into a fact with a number attached.

**When you were the one who raised a false alarm**, correct it in the same voice you
raised it in and keep it brief. What matters is the doc being right afterwards. Note
which method held up — often something in the system was giving the correct answer
the whole time, and pointing at it is more useful than any apology.

Leave behind the check itself where you can. A claim that carries the command that
proves it does not decay the same way.
