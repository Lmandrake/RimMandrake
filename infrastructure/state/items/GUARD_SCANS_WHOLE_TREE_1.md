# GUARD_SCANS_WHOLE_TREE_1 — one seat's dirty item blocks every other seat's commit

Sibling of `LEDGER_CANNOT_BE_COMMITTED_1`. Same file, same shape: a guard whose scope is
wider than the thing it means to protect.

## spec

`.claude/hooks/queue_lint.py:245` builds the ownership check as

```python
mine = [p for p in changed(root, [p for p in paths if ITEMS in p])]
```

`paths` comes from a regex over the commit COMMAND TEXT. When the command names no item
file that list is empty — and `changed()` (line 193) runs
`git diff HEAD --name-only --` with an empty pathspec, which lists the **entire working
tree**. The check then walks every dirty item in the repo, not the ones being committed.

⇒ **Any seat's in-progress edit to any item refuses every other seat's unrelated commit.**
Measured 2026-08-21: CHECK was mid-edit on `ashkarr-map-quality-second-pass-8c31f7`, and a
REP commit of four agent files plus `package_skill.py` was refused for "editing 1 item(s)
owned by another seat" — an item that appeared in neither the pathspec nor the diff. Four
seats share one working tree, so this fires whenever anyone is mid-item.

⚠️ **A second consequence, and it is the one that bites the workflow.** `rimflow file
--for <SEAT>` prints *"items/<ID>.md still needs ## spec and ## verify and ## criteria"* —
so the FILER is told to write the spec. The first commit of that file succeeds only
because `git diff HEAD` does not list untracked files. Every subsequent correction to it
is refused, because the item now belongs to the seat it was filed for. **You may create a
spec for another seat and never fix a typo in it.**

Workaround in use: name any item you DO own in the pathspec so the filter is non-empty.
That is a hole in the guard, not a fix, and it should stop working when this is done.

## verify

- A commit naming no item file is not refused because of an unrelated dirty item.
- A commit that DOES name another seat's item is still refused.
- The seat that filed an item can amend its `items/<ID>.md` until the owning seat claims
  it (or: filing writes the spec, so it needs no amendment — either resolution is fine,
  but one of them must be true).
- `.claude/hooks/selftest_queue_lint.py` passes, with a case for the empty-pathspec branch.

## criteria

The guard refuses exactly the commits that change another seat's work, and no others.
