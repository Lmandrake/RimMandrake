## spec
*"validate_patch.py has no selftest, and the same bug class has now shipped twice."*

🔴 **The bug class, and it really did ship twice.** RimWorld evaluates a patch xpath
against the XmlDocument, whose CHILD is `<Defs>`, so `Defs/ThingDef[...]` and
`/Defs/ThingDef[...]` mean the same thing there. lxml and ElementTree evaluate against
the `<Defs>` ROOT ELEMENT, where a leading `Defs` step means `Defs/Defs/...` and matches
nothing.

- **2026-08-21** — found in the **ElementPath** branch. 42 xpaths across this repo's own
  patches had been reporting a false 0.
- **2026-08-22** — found again in the **lxml** branch, which had never been given the same
  treatment. Every xpath using `text()`, `contains()`, `starts-with()`, `not()`, an axis
  or a union takes that branch, and **25 of the 28 operations in `BodySizeIsReal.xml` read
  as dead** when all 28 were live.

⚠️ **A false 0 is the worst output this tool can produce**, because it is indistinguishable
from a genuinely dead xpath — the one thing the validator exists to tell apart. Both fixes
were correct and neither was tested, which is what left the second free to happen.

## verify
```
python3 src/RimMandrake/Utils/selftest_validate_patch.py
```

## criteria
Reintroducing the bug makes the suite fail.

## notes
✅ **CLOSED 2026-08-22.** `src/RimMandrake/Utils/selftest_validate_patch.py`, **8/8**.

🔑 **And it was proved to catch the bug, not merely to pass.** `rebase_for_root_element`
was replaced with the identity function at RUNTIME — no file touched — and **3 of 3** of
the regression cases failed, each naming the real symptom. A regression test nobody has
seen fail is theatre.

**What it covers:** both spellings of the root step in both engines · `text()`,
`contains()`, `starts-with()`, `or`, `not()` through the lxml branch · a genuinely dead
xpath still reporting 0 (the fix must not turn every miss into a hit) · `//` still meaning
"anywhere" · the two engines AGREEING on every expression both can evaluate, which is the
strongest check available because it needs no expected number · and a guard on the routing
itself, so dropping `text()` from `UNSUPPORTED_TOKENS` cannot deliver the same false zero
by another road.

⛔ **It deliberately does NOT cover** load-set discovery, the def-file walker or report
formatting. Those need a real install; this tests `count_matches()` against documents built
in memory, runs in under a second, and can therefore be run before every commit — which is
the only property that would actually have stopped this.

⚠️ One test failed first time and the TEST was wrong, not the code: it expected three `<li>`
in a fixture holding four.
