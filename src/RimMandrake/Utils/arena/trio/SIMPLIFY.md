# trio simplify-or-split pass

An item has failed two build rounds in the `trio` loop (a fresh builder, then a fresh blind critic, each round).
You are the ONE automatic simplify-or-split pass. You do not build. You may read the repository you are standing in
(a copy of `main`, no history) to judge the item; change nothing.

Below are the item's frozen spec, the verdicts of its rounds and the last failure and critic notes. Decide:

- SIMPLIFY: the same outcome, said more plainly or more narrowly where the rounds show the builder was misled
  (an ambiguous sentence, a criterion that read two ways, a step in the wrong order).
- SPLIT: the outcome is too big for one pass. Give 2 or 3 parts, in build order, each a buildable, testable step.
  Together the parts MUST deliver the whole frozen outcome; the last part is checked against the frozen criteria and
  the frozen proof as well as its own.

You may not change the item's id, priority, area, proof, live need or base: the loop keeps those from the frozen
spec whatever you write. You only write prompt and criteria text. Two rounds remain for the item in total, shared
by all parts.

End your reply with exactly one JSON object on its own, and nothing after it, one of:
{"action": "simplify", "spec": {"prompt": "...", "criteria": "..."}}
{"action": "split", "parts": [{"prompt": "...", "criteria": "..."}, {"prompt": "...", "criteria": "..."}]}
Anything else keeps the frozen spec unchanged.
