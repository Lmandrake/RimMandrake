## spec
`infrastructure/state/preserved/BUILD.md` contains exactly one section,
`## 🔴 OWNER RULINGS, 2026-08-19`, and its body is a single line of process saying it must not
become an item. **The rulings the heading names are not in the file.**

`preserved/` is hand-written prose rescued from the queues before they became generated views,
and **nothing regenerates it** — so if `preserve()` dropped that body, the owner's 2026-08-19
rulings to BUILD may not exist anywhere on disk.

Possibly the same root as the `preserve()` archive-overwrite bug fixed 2026-08-22 (it wrote
false *"hand-written"* headers), or a second defect.

## verify
1. `git log --diff-filter=A -- infrastructure/state/preserved/BUILD.md` — did the body ever exist?
2. `git log -S "OWNER RULINGS, 2026-08-19"` across the repo: the text may survive in a
   pre-generated `queue/BUILD.md` revision.
3. Restore it if recoverable, naming in one line where it came from. If it never existed, say
   THAT in the file — an empty rescue that reads as a rescue is worse than an admitted gap.

## criteria
`preserved/BUILD.md` either carries the 2026-08-19 rulings or states plainly that they were not
captured, and names what was searched.

## Watch out
🪤 **Do not "fix" this by deleting the heading.** It is the only surviving evidence that
something was said on 2026-08-19 worth preserving; removing it destroys the lead.
