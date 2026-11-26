# Workshop Pipeline: the onboarding run of one home's old tickets

`list_dispatch.py` launches this brief on one home (one part of the pipeline, one machine) that holds old tickets: open
tickets with no outcome check, no routed part and no shaped split. A mod's road-back bundle sends its old tickets
through the same steps. `work_bundle.onboard_brief` fills the text below the marker. Page:
`design/specs/2026-11-24-work-bundles/boundary.md` §Onboarding old tickets by home. The owner, 2026-11-25: "MANY of the
tickets from before a certain date will not include a custom check already prepared. Propose the right way to onboard
those tickets and process them into appropriate work bundles, if we have to write tests then so be it, and start work
on them. We HAVE to have a route like this."

<!-- BRIEF -->
This brief is the role {role}. You are the worker of onboarding run {bid}: all the old tickets of one home, {system}, in one run. Most of them were
filed before the Shape stage went live, so they have no outcome check. Many are done already, dead, or not worth the
touch. You sort them first, then you write the checks of the ones that stay, then you fix them.

The bundle id is {bid}. Its state file is {sf}: read it first if it exists (a restart), and write it after each step and
each group. Your first ticket is `{lead}`: claim it before anything else
(`python3 src/RimMandrake/rimflow/cli.py claim {lead} --seat BENCH --why "work bundle {bid}" --publish`).
Cite "work bundle {bid}" in the --why of every ledger act. Write your step for the page after each step:
`python3 src/RimMandrake/rimflow/work_bundle.py step {bid} "<step A, B or C, and the count done>"`.

The members ({n}):
{rows}

Why this run: {why}

Old work is filtered before any process takes it (CLAUDE.md §Old work is filtered before any process takes it). The
older the ticket, the more proof it needs. Read each ticket against the code of now. Run its test on the current build.
A stale or wrong ticket is dropped with its reason; you do not do its work. A ticket filed before the Maturation Pipeline
(2026-11-13) is worked only after its check is seen red today.

Step A, the reality sort, before you write any check. Read every member against the code of now: its prose, the files
and items it names, `git log` of those files since its filing. Give each member ONE class and act on it at once:
- done already: close it with the commit that did the work
  (`cli.py close <ID> --sha <that commit> --evidence "<what shows it>" --seat BENCH --why "work bundle {bid}: done already" --publish`);
  a commit that is only ledger events is refused by --sha: then use `--no-code "done already by <sha>: <what>"`.
- dead or stale (its target is gone, or a later ruling replaced it): drop it with the reason
  (`cli.py drop <ID> --reason "stale: <the target that is gone, or the ruling>" --seat BENCH --publish`).
- duplicate: supersede it (`cli.py supersede <ID> --by <the live twin> --seat BENCH --publish`).
- not worth the touch (test 1 of CLAUDE.md §Touching code has a cost): drop it with
  `--reason "not worth the touch: <why>"`.
- needs the owner, the Conductor or a judge: write its route with `rimflow shape` (below, a part with a route), then go on.
  A route is only for one of the owner's five acts, a choice between goals or a looser bar, or a taste call. Do not
  route a repair that our standing rules already allow: keep it.
- keep: it goes to step B.
Write one PROGRESS note on {lead} when step A ends: the count of each class, and the ids of the kept members.

Step B, group and write the checks. Group the kept members by cause or by the files that the fix changes. For each kept
member, write its outcome check with `rimflow shape`:
  python3 src/RimMandrake/rimflow/cli.py shape <ID> --parts '<json list>' --size small --seat BENCH --why "work bundle {bid}: step B" --publish
A part is {"name": "...", "effect": "cmd:<command> | path-has:<repo path>::<text> | path-lacks:<repo path>::<text>",
"fooled_by": "<what would pass this check and leave the need unmet>", "route": null}, or a part with "effect": null and
"route": {"who": "owner|conductor|judge|review", "ask": "<what is asked>", "resumes": "<what resumes the ticket>"}.
Each check tests the NEED, not the paper, and is seen to fail on the current build before the fix (the write refuses a
check that is never seen failing; a refusal names the part and the repair: repair it and write again). A member for
which no check is possible gets the line `Acceptance test: none, <reason>` in a note, and a route.

Step C, the work. Follow the role src/RimMandrake/rimflow/roles/builder.md, setting Work Bundle, from its step 3, group by
group: fix test first, see the check hold, run the tests that the change touches, `./publish`, close each member with
its commit, write a PROGRESS note, then run `python3 src/RimMandrake/rimflow/work_bundle.py context`. On SAVE AND RESTART,
finish the group in hand, write the state file (what is done, what the next context needs, what is next), publish it,
and end. The pipeline restarts a fresh run of you from that file.

Every member ends with one outcome: closed (fixed or done already), dropped, superseded, routed, a dated wait, or a note
that starts `REFUSED BY BUNDLE:` with its reason (the role's section "A refusal has a reason"). A full context, a long
run or a spend stop is never a reason.

{fixer}

{polish}
Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never
his quotation. Do not start a helper or a subagent of your own, and do not run a command in the background.
