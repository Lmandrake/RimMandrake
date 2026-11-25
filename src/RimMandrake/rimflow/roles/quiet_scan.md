# The standing scan of quiet files: you read code files one at a time

You are one run of the standing scan that the owner ordered by card on 2026-11-19. A program picks each file: a code file that
no commit changed for 7 days or more, mod content first. You read that file whole and you end it. You are offline: use no
game and no bridge.

Do not claim, start, wait on or close the ledger item named in the footer. That item is closed, and a detached run
needs an item to run on. Write no
`LEFT OPEN:` note. The footer's lines about claim, close and the item do not apply to you. Its rules about the clone,
`./publish`, and foreground commands do apply.

## Read first

- `src/RimMandrake/rimflow/roles/code_review.md`: the review method. That file says what a Problem is and who fixes a Problem.
  Work by that file.
- `design/RimMandrake/standing_rulings.md` §Code is clean when its promises are tested: only when that file leaves a question.
- `~/dev/MandrakeWorkflows/skills/mutate-your-checker/SKILL.md`: when you write a test.
- `skills/clone-landing-commits/SKILL.md`: before your first landing.

Most files that you read have no page of promises (`code_review_status.py check <path>` reads NO PAGE). For those files a
finding is a Problem only when it is measured, or predicted with a concrete case (this input, this wrong result), to cause a
failure in ordinary operation: a wrong result in the game, an exception, a feature that does not work, a tool that reports a
false answer. Do not write a page.

## The loop

1. `python3 src/RimMandrake/rimflow/quiet_scan.py next`
   - `READ <path>`: do steps 2 to 5 on that file, then run it again.
   - `YIELD <why>` or `DONE <why>`: stop. Write your summary and end.
2. Check that the file is reachable: a def, class, patch or script that something loads, calls, names or documents. When
   nothing reaches it, end the file with step 5, `noted`, and say what you searched.
3. Read the whole file, and what it calls where the question needs it. Never guess a defName, field or engine behaviour: read
   it. A file with no Problem is the usual case (about 0 or 1 bug per file was measured). Do not look for a Problem
   until you find one.
4. A Problem: fix it here, now. Write an offline test first, see it FAIL, fix the code, see it PASS. Run the mod's other offline
   tests that read the changed file. A C# change is built with `python3 src/RimMandrake/Utils/winbuild.py <Mod>`, and the DLL
   travels with its `.srchash`. Land with `./publish` and explicit paths.
   - Then start one fresh reader: the Agent tool, `subagent_type: "rm-fixer"`, `model: "sonnet"`,
     `run_in_background: false`, with the reader's text below and nothing else. No second reread follows.
   - Never fix a stricter test, a tuning number or a rare failure. Each of those is one line on `polish.md` beside the
     page, when the file has a page. When the file has no page, drop it.
   - A style point in a file that your fix changed, you do now, before the fresh reader (`CLAUDE.md` §Touching code has a
     cost, the polish rule). A style point in any other file is one line on `polish.md` beside its page.
   - A bar (a sentence about what the player sees or can do, in a mod's `## north star` section or its
     `version/locked_bars.json`) is never yours to change.
   - When the fix needs one of his five acts, is unknown after a real attempt, or needs a game while `python3
     src/RimMandrake/rimflow/game_lock.py query all` shows none free, file one ticket that names what you tried and the
     failure with its concrete case (`rimflow file`, the line in the footer), and end the file `noted`
     with the ticket's id. Search the ledger for the failure first.
5. End the file with exactly one of these. A refusal names its repair: do the repair and run the command again.
   - No Problem found, or a Problem was fixed and the fresh reader found none:
     `python3 src/RimMandrake/Utils/code_review_status.py mark-clean <path>`, then
     `./publish -m "quiet scan: <path> read clean" infrastructure/state/code_review/$AGENT_SEAT.jsonl`, then
     `python3 src/RimMandrake/rimflow/quiet_scan.py end <path> --outcome clean`.
     When the fresh reader read it last, add `--reviewer-seat $AGENT_SEAT --reviewer-agent <its name>` to `mark-clean`.
   - The fresh reader also found and fixed a Problem, so the file is FLAGGED. Publish the fix and
     `infrastructure/state/code_review/flags/$AGENT_SEAT.jsonl`, then `quiet_scan.py end <path> --outcome flagged`.
   - Anything else: `quiet_scan.py end <path> --outcome noted --reason "<why>"`.

## The fresh reader's text (fill in the path)

> Read `src/RimMandrake/rimflow/roles/code_review.md`. You are its one fresh reader of `<path>` in this clone. Read the whole
> file, its page if it has one, and its tests. Do not read its git history or any earlier finding. When you find no
> Problem, reply `NO PROBLEM` and stop. A file with no page has a Problem only where a concrete case (this input, this wrong
> result) causes a failure in ordinary operation. When you find a Problem, write a test, see it FAIL, fix the code, see it PASS,
> then run `python3 src/RimMandrake/Utils/code_review_status.py flag <path> --why "<what was found and fixed>"`. Do not
> publish. Reply `PROBLEM FIXED`, the failure, and the paths that you changed. Use no game and no bridge.

## The level that is enough, and when to stop

One whole read per file, one fix round, one fresh reader. A file that ends is never read again by you. Stop when `next` says so.

End with a summary of at most 5 lines: each file, its outcome, and what was fixed.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation.
