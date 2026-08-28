# Transient/ — output that exists to be looked at, then thrown away

Everything in this directory is **untracked, short-lived, and for a human**. It is
where a contact sheet, a review page, a before/after render, a one-off census or a
draft analysis goes while it is being discussed — and then it goes in the bin.

🔴 **This directory is gitignored. Nothing here survives a fresh clone.** That is
deliberate: a file that must survive is, by definition, not transient, and belongs
somewhere it will be found.

## What goes here

Exactly three purposes:

| | |
|---|---|
| **show the owner something** | a render, a contact sheet, a diff image, a chart, an HTML page he is meant to open and look at |
| **confirm a finding** | the evidence behind a claim, kept only until the claim is settled or written down properly |
| **get a decision** | a review sheet or option set he picks from |

If the file does not serve one of those three, it does not belong here.

## What does NOT go here

- ⛔ **Machine cache, logs, samples, temp files.** Those go to **`/tmp`** — never
  into the repo at all. Nobody looks at them; they exist for a program, not a
  person. If a script needs a working directory, it uses `/tmp`, and if the output
  turns out to be worth keeping, it gets copied out deliberately.
- ⛔ **Anything another file references as its evidence.** The moment a tracked
  document points at an artifact, that artifact has stopped being transient — move
  it beside the document and commit it, or the document acquires a dead link the
  first time this directory is cleaned.
- ⛔ **The only copy of anything.** No work product lives here. If losing it would
  cost real work, it is in the wrong place.

## Shelf life

**Assume 14 days.** Anything here may be deleted by anyone, at any time, without
being read — that is what "transient" means and it is the whole contract.

```
python3 src/RimMandrake/rimflow/cli.py sweep --transient
```

⚠️ **`sweep` LISTS. It never deletes.** A heuristic deciding which of someone's
working files are stale is a heuristic destroying work. It prints age and last
commit; a human does the deleting.

## Naming

Files keep whatever name says what they are. The old root-level `TRANSIENT_` prefix
is no longer needed — the directory carries that meaning now — but the files moved
here on 2026-08-27 kept their prefix, because dozens of them cross-reference each
other by name and a rename would have broken every link.

## History

Before 2026-08-27 this content lived as `TRANSIENT_*` files at the repo root, and
the earlier convention (specced in `Transient/TRANSIENT_upgrade_plan.md`) had them
**committed and swept** rather than ignored. The owner reversed that on 2026-08-27:
transient output is **not tracked**. The root-level naming rule in
`.claude/hooks/queue_lint.py` now routes scratch here instead.
