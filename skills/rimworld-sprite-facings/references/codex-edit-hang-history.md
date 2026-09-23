# Codex `edit` hang history (multi-facing generation)

Two earlier drafts of the "generate facings individually" guidance, kept in full:
the 2026-08-23 claim that the second `--image` was the cause, and the same-day
correction that it is intermittent. The distilled rule (120 s cap, retry loop,
anchor with words) is in `../SKILL.md` > "Multi-facing assets".

## The 2026-08-23 claim

🔴 **BUT TWO-IMAGE EDITS HANG ON THIS INSTALL — measured 2026-08-23.** Four
consecutive `edit` calls carrying two `--image` arguments produced **no output at
all** and were killed by their own 780 s timeout, with codex's stderr suggesting
re-authentication. The very next **single**-image edit succeeded in **79 s**, and
so had two before it, so it is neither auth nor rate limiting — it is the second
image. ⛔ **It is NOT the documented variadic-`-i` bug**: `codex_image.py:241`
already appends the `--` terminator for any non-empty image list, and that was
read and confirmed before blaming it.

✅ **The working fallback, and it is nearly as good:** edit each facing from ITS
OWN reference only, and put the approved sibling's treatment into the PROMPT as
words — *"segmented chitin plating with clean segment breaks, speckled shell,
wet translucent flesh with a bioluminescent glow inside it, deep red and rose
palette, hard black outline"*. Write that description down when the first facing
is approved; it is the anchor, and it costs one 80-second call per facing.

⚠️ Budget for it: a hung two-image call costs the FULL timeout before it fails,
so a batch of four is 52 wasted minutes. If you try the two-image form again,
give it a **120 s** timeout, not 780.

## The correction

🔴 **CODEX `edit` FAILS INTERMITTENTLY HERE, AND A FAILURE COSTS THE WHOLE
TIMEOUT.** Measured 2026-08-23 over seven calls in one sitting: **four succeeded in
79-81 s** and **three produced no output at all** and were killed by their own
timeout, with codex's stderr suggesting re-authentication.

⚠️ **CORRECTION, and it is the point of this entry.** The first three failures were
all two-image calls and this file briefly said the SECOND IMAGE was the cause. Then
a **single**-image call failed the same way. ⇒ **It is not the second image**, it is
not the documented variadic-`-i` bug either (`codex_image.py:241` already appends the
`--` terminator, which was read before blaming it) — it is **intermittent**, and the
sample that looked conclusive was four calls deep and confounded.

**How to work with it:**
- ⏱️ **Cap the timeout at 120 s, never 780.** A failure burns the entire budget before
  it reports, so a batch of four hung calls at 780 s is **52 minutes for nothing**. A
  good call returns in ~80 s; anything past 120 s is not coming.
- 🔁 **Retry rather than diagnose.** Three of seven failed and the same prompt
  succeeded on a later attempt. Wrap each facing in a retry loop instead of
  reasoning about why one died.
- ⛔ **Do not draw a conclusion about the CAUSE from a handful of calls in one
  sitting.** This entry exists because that is exactly what happened.

🔴 **AND SOME OF THOSE "HANGS" WERE THE RETRY HARNESS KILLING ITSELF.** A cleanup
line of the shape

    pgrep -f codex_image.py | xargs -r kill -9      # ⛔ NEVER

matches the **parent shell too**, because a script created by a heredoc carries its
own text — including that string — in the parent's command line. So the retry loop
SIGKILLed the job it was retrying, and the batch died with an unexplained exit 1 or
144 partway through. ✅ **`timeout` already reaps the child; no cleanup line is
needed.** If you must kill strays, match on something that cannot appear in the
parent's own argv.

✅ **Anchoring still works without the second image:** edit each facing from ITS OWN
reference and carry the approved sibling's treatment in the PROMPT as words —
*"segmented chitin plating with clean segment breaks, speckled shell, wet translucent
flesh with a bioluminescent glow inside it, deep red and rose palette, hard black
outline"*. Write that description down the moment the first facing is approved; it is
the anchor, and it survives whichever call shape you end up using.
