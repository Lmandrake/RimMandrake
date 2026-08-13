---
name: agent-reporting
description: How a seat reports to the owner in the terminal — the glyph-led report format, the single-spaced block held together by two trailing spaces, the 72-character no-wrap cap, 🟡 NEEDS YOU always first, notes that state findings not explanations, terse-by-default prose with rationale opt-in, numbers over adjectives, full native paths, and keeping tool output quiet by default and raw on failure. Use when reporting to the user, writing a status update, finishing a task, summarising results, answering "what did you do", or before running any command whose output hits the owner's screen.
---

# Reporting to the owner

Five seats report to one human in one terminal. **The reader is triaging, not
reading.** Three answers, fast: **does this need me · did anything break · what
changed**. Most reports bury the first under the third, because tool output
floods the screen and what survives is — the owner's words — *"a wall of
important text that's also hard to quickly parse."*

## 1. The format

```
◆ **CREATE** · <subject, 3-6 words>··
🟡 **NEEDS YOU** <the ask>··
✅ **DONE** <result, with numbers>··
⚠️ **NOTE** <the finding or outcome, a few words>··
→ `D:\Luke\dev\Rimworld\<path>`

<prose: the depth, if any. Two or three sentences.>
```

**`··` marks two literal spaces. Type spaces, not dots** — they are invisible in
a rendered file, which is why this skill draws them.
**The block is SINGLE SPACED — never a blank line between glyph lines.** It has
to land as one dense object the eye takes in at once; a blank line splits it into
separate paragraphs and the scan is gone. But Markdown joins consecutive lines
into one paragraph, so the break must be **forced: two trailing spaces on every
glyph line except the last.** **One blank line after the block**, before the
prose — and that is the only blank line.

**Do not wrap the report in a code fence.** A fence holds the shape but renders
every label literally, as asterisks. Trailing spaces keep shape, bold and emoji.

**Omit any zone that is empty. A four-line report is a good report.**

| Glyph | Zone | Holds |
|---|---|---|
| `◆` | header | **seat in bold**, then 3–6 words of subject |
| `🟡` | NEEDS YOU | the decision or blocker — **always line 2 when present** |
| `✅` | DONE | what landed, with numbers |
| `⚠️` | NOTE | a finding or an outcome — no reasoning |
| `→` | paths | full native paths in backticks, last line, no trailing spaces |

## 2. The cap: 72 characters · block surveys · prose goes deep

**A glyph line that wraps destroys the format** — it puts non-glyph text in the
glyph column, and the scan is gone. One wrapped line costs more than the three
it saved. **So the entire line, glyph and all, fits in 72 characters**, the two
trailing spaces included since they are part of the line. A cap, not a target.

**If it does not fit, it is not a shorter sentence — it is the wrong content for
that line.** Do not compress the sentence, split it: **the headline goes in the
glyph line** (the ask, the finding, the outcome), **the explanation goes in the
prose below**. `→` path lines are the one exception — a path cannot be re-cut.

**That split is the whole design, so never pre-emptively expand a glyph line to
save the owner a question.** It inverts the cost, charging every reader for depth
one reader wanted. The block carries headlines, the prose carries reasoning, and
anything else waits for the owner to ask. Asking is cheap; a broken block is not.

## 3. Terse is the default — verbosity is opt-in

Same trade as the block, applied to the prose around it.
**Do not restate or agree with the request. Acting on it is the acknowledgement.**
**Do not explain why you did what was asked** — the reasoning is interesting only
when it changes the owner's decision or when they ask for it.

**A confirmation is one line:** `Done, 8f2a11c.`

**Never pre-empt a question with a paragraph.** They will ask if they want it.

**Before** — ~40 words, agreement plus rationale nobody requested:

```
Yes, good point, I agree the block needs to stay dense for the scan to
work, so I have passed it to the running agent, which should fold it into
the edit already in flight and keep both changes in one commit.
```

**After** — six words, the owner's own version:

```
Yes. Sent to the running agent.
```

**Rationale is opt-in**: give it when the owner asks, when you are disagreeing,
when you are reporting a failure, or when a decision of theirs rests on it. Cut
it otherwise. **When they ask for discussion, analysis, options or advice, expand
freely** — the rule is about unrequested prose, not depth when depth is the ask.

## 4. 🟡 is yellow because it is an emoji

The owner asked for bold yellow. **Markdown has no colour primitive**, so in
assistant text the only thing that puts literal yellow pixels on the screen is a
yellow emoji. The marker is the emoji plus bold: 🟡 followed by **NEEDS YOU**.

**Do not reach for ANSI escapes.** `\033[33m` in assistant text renders
literally — the owner sees the escape, not a colour. ANSI belongs in a script's
own output. The seat colours in §6 are the *terminal's*; you do not emit those
either.

`❓` is dropped. **One marker, one meaning** — two glyphs for "the owner must
act" means the eye has to learn both.

## 5. A NOTE states the finding, not the reasoning

The NOTE line holds **the thing itself** — the finding, or the key outcome, in a
few words. Why it is true and what it might mean: prose, below the block.

**Before** — 30 words, wraps twice, finding buried mid-sentence:

```
⚠️ **NOTE** the validator flagged the armor patch because the def it targets is not present in any currently subscribed mod, which probably means it was unsubscribed
```

**After** — 7 words, the finding first, the reasoning moved below the block:

```
⚠️ **NOTE** armor patch targets a def nothing defines

Probably an unsubscribe. Not verified against the workshop folder.
```

## 6. Rules

**The 🟡 line is always first after the header, always marked.** If nothing needs
them, say `(nothing needs you)` explicitly. **Absence must be informative, not
ambiguous** — neither line present forces the owner to re-read the whole thing to
learn whether they are on the hook, which is the cost this format removes.

**Glyph first character, always.** Prose beginning `I've completed the…` is
unscannable however good it is — the eye must parse the sentence to learn the
category. A glyph column answers that before reading.

**Numbers, not adjectives.** `1,578 → 154` beats "significantly reduced", and is
shorter. Adjectives make the reader ask "how much?"

**Paths are full, plain and native — `D:\Luke\dev\Rimworld\CLAUDE.md`.** Standing
project rule: never a bare filename, `scatter.py` turns a one-second action into a
hunt. **No `file:///`, no `%20`.** That form existed only to be clickable, and
nothing here is — terminal hyperlinks (OSC 8) and markdown links are both inert,
and a double-click only copies. It bought nothing and cost line width.

**Wrap every Windows path in backticks.** An unbackticked `\` can be eaten as a
markdown escape, silently deleting a separator from the path you just gave.

**Opening is a separate act — `./src/RimMandrake/Utils/show.sh <path>`** launches Explorer with
the file selected. "Show me" is a request to *run* that, not to reprint the path.

**Do not narrate progress.** Report at completion, not at each step.

**This is not seat-to-seat messaging.** Peer messages are
`skills/agent-messaging/SKILL.md`, ten-line ceiling. A peer does not need 🟡 —
if it does not need them, it is a file, not a message.

**The seat prefix is fixed** so the owner can filter five windows visually. Seats
also carry terminal colours — BRIDGE cyan · OPS amber · CREATE green · VISION
violet · PROJECT slate — which work at a glance, where the prefix survives
scrolling, copying and piping. Carry both.

## 7. Tool output — quiet by default, raw on failure

**Anything a command prints competes with the report for the same attention.**
Default every command to its quiet form.

| Offender | Quiet form |
|---|---|
| `git commit` | `git commit --quiet <pathspec> -F -` |
| `git push` | `git push 2>&1 \| tail -2` |
| `git diff` / `git status` | `--stat` / `--short` — never a full diff |
| proving a file exists | `ls -l <path>` — **never `cat`** |
| build / test / install | `\| tail -n 20` |
| any loop over many files | count the result, print the count |

**On failure, show the raw output** — that is when the flood is the fastest thing
to diagnose from. Quiet is a default for the success path, not a rule for errors.

## 8. Before and after

**Before** — everything true, nothing findable:

```
I've finished going through the patch files as requested. The validator
flagged a significant number of issues initially, mostly duplicated xpath
targets, and after cleaning those up the count came down substantially. I
also noticed JawaArmor.xml references a def I couldn't find in the mod set
— probably an unsubscribe, but not really my area.
```

**After** — same content, block then prose:

```
◆ **CREATE** · patch validation sweep··
🟡 **NEEDS YOU** delete JawaArmor.xml, or resubscribe its mod?··
✅ **DONE** 41 patches validated · 1,578 → 154 warnings · 8f2a11c··
⚠️ **NOTE** armor patch targets a def nothing defines··
→ `D:\Luke\dev\Rimworld\Jawa_Patches\Patches\JawaArmor.xml`

Warnings were near-all duplicated xpath targets. The dead def is likely
from an unsubscribe; not verified, and not my area to delete.
```

The question moved from sentence four to line two, numbers replaced "a
significant number", the reason left the block, and no glyph line wraps.

## 9. Before you send

1. **Is every glyph line ≤ 72 characters, glyph included?** Count them.
2. **Two trailing spaces on every glyph line but the last** — no blank lines
   inside the block, and the block is not inside a code fence.
3. Is 🟡 line 2 — or is `(nothing needs you)` there instead?
4. Does every line in the block start with a glyph?
5. Does each ⚠️ state a finding, with the reasoning moved to the prose?
6. **Is any prose here unrequested** — agreement, restatement, why you did it?
7. Are the numbers numbers, not adjectives, and every path full, native and
   backticked — no `file:///`, no `%20`?
8. Did any command print more than ~20 lines the owner did not need?
9. Have you dropped every zone that was empty?
