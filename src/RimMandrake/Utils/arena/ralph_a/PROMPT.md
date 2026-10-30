# ralph_a build pass

You are one fresh BUILD pass of the `ralph_a` loop. You have no memory of earlier passes; everything you need is in
this prompt and in the repository you are standing in (the arm clone, branch `ralph/wip`).

Do exactly one thing: make the frozen task below true, with a test that proves it, and commit it on `ralph/wip`.

Rules (POLICY.md beside this file holds the full list; these are the ones a pass breaks most):
- Read the code you change before you change it. Never guess a defName, field or namespace.
- Every behaviour you add has a selftest that goes RED when the behaviour is removed. Run only the tests for what
  you changed: `python3 src/RimMandrake/Utils/run_selftests.py --only <tests>`.
- Commit explicit paths only (`git add <path>`), one commit or a few, on `ralph/wip`. Never push, never merge, never
  touch `main`: the loop publishes, and only after its gate AND a separate tester pass agree.
- No placeholders (TODO, FIXME, `pass  # later`, stub returns). The gate rejects them.
- Do not start the game, a live seat, a systemd unit or another model. A task that needs a live look is handed to
  the live lane by the loop after you finish; you only build and test offline.
- If a section `LAST FAILURE` or `TESTER VERDICT` follows, it is why the previous pass of this task was not
  published. Fix that first. A tester finding is a defect until your test shows it is not.

When you are done, stop. Do not summarise the diff; the loop reads git, not your words.
