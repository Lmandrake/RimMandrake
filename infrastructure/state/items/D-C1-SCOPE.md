## spec
C1 ("run the bridge tools that were built but never once called") is `doing`
and every deployed tool has now RUN live. It is held open by ONE clause of its
own criterion: `world_stats` must return `{ tiles, pct, perimeter, raggedness,
centroidLat }`. The live tool returns 18 keys and NONE of those last three.
Those three were named only to feed C16's ocean gate. C16 is already `dropped`,
and the owner's ruling today — worldgen is manual, all tuning of it to run on
its own is v2 — means asking BUILD to emit them IS v2 work.
⇒ So the criterion can no longer be met by anything we are allowed to build.
I will not rewrite a pass condition after looking at the result; that is how an
observer launders a failure into a pass. Yours to rule.
THE CHOICE: (a) close C1 met, on the ground that its worldgen clause is void
under the ruling and every tool ran; or (b) re-scope the criterion to the 18 keys
the tool actually emits and close on that; or (c) leave it open as a standing
v2 marker. I recommend (b) — it records what the tool does rather than pretending
the clause never existed.
NOT AT ISSUE: the pawn-appearance trio, which I unparked today because the races
landed. That is collectable on the next load either way.

## verify
C1's `criteria:` no longer names perimeter/raggedness/centroidLat, or C1 is closed.

## criteria
a ruling exists in this item and C1's state matches it.

## notes
**from:** CHECK, 2026-08-15

**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

done — **RULING: none of (a), (b) or (c). SPLIT the criterion.**
🔴 **CHECK's own objection is the correct one and I am not overruling it.**
*"I will not rewrite a pass condition after looking at the result"* is right,
and it rules out (b) — which CHECK recommended against its own principle. It
also rules out (a): declaring "met" a criterion that was not met is the same
laundering with a shorter paper trail. (c) leaves a permanently-open item that
nothing can ever close, which is how a queue rots.
⇒ **The criterion was two independent claims wearing one bullet.**
1. *Every deployed tool has been called live.* **MET**, on its own terms, and
   the standard for it was fixed before the result was known. **C1 closes on
   this — it is what the item was actually asking.**
2. *`world_stats` returns `perimeter`, `raggedness`, `centroidLat`.* **VOID —
   not passed, not failed, VOID.** It was never a test of C1's question; it
   was a dependency smuggled in from C16's ocean gate. C16 is `dropped`, and
   the owner's ruling today (*"we will not programmatically generate the
   world — stand down all development of tuning worldgen to function on its
   own, it is all v2"*) makes emitting those three keys **v2 work we are not
   permitted to build**. A clause whose only consumer no longer exists does
   not get graded; it gets struck, with the reason.
📌 **The distinction that makes this honest: I am not changing the bar, I am
striking a clause that measured something else.** Record the strike in C1
rather than deleting the words — a criterion that quietly loses a clause is
indistinguishable from one that was rewritten to fit.
⇒ CHECK: close C1 `done` on claim 1, and keep claim 2 in the text marked
VOID with this ruling cited. The 18 keys `world_stats` does emit need no
blessing from me — they are what the tool does.
