# BOUNDARY: the Workshop Pipeline's Shape stage (list_shape.py), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/list_shape.py` (all of it), the Shape run's brief `src/RimMandrake/rimflow/roles/list_shape.md`,
the `shape` verb in `src/RimMandrake/rimflow/model.py` (`VERBS["shape"]`, its `_apply` branch, `Item.shape`,
`Item.shape_named`), `rimflow shape` in `src/RimMandrake/rimflow/cli.py` (`cmd_shape`), and the Shape lines of
`src/RimMandrake/rimflow/list_dispatch.py` (`gather`, `decide`, `execute`) and `list_dispatch.json` (`shape_*`).
Item: `RIMMANDRAKE_BUILD_SHAPE_STAGE_CHECK_TESTS_THE_NEED_NOT_PAPER`, step 4 of
`design/specs/2026-11-22-coordination-every-agent-must-use/plan.md` (§Shape). Why: on 2026-11-23 about 70 of 1,527 open
items carried an outcome check, so the lane could see only those; Shape is what gives the rest a check.
Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_list_shape.py`. The plan's acceptance script
(`src/RimMandrake/rimflow/acceptance/step4_shape_accept.py`) checks the exit rule.

## How it works, in one paragraph

An open item with no outcome check and no route is due for Shape when it is named (`rimflow shape <ID> --enter`), or
when it was filed after Shape went live (`shape_from`) and is older than `shape_grace_h`. The lane
(`list_dispatch.py`) launches one Shape run on a due item, through every gate a Work run passes. The run applies the
worth-the-touch test, splits the item into parts, and writes them with `rimflow shape <ID> --parts ... --size ...`.
Each part has an outcome check with its "what would pass this check and leave the need unmet" line (`fooled_by`), or a
route (who, what is asked, what resumes the item). The write derives the item's one outcome check from the parts. Then
the item is in the lane's ordinary Ready, Work and Verify stages.

## How the lane decides "small"

The lane does not guess size from an item's text: before Shape nothing on an item can be counted that says how big it
is. Every Shape run is launched as a **Shape-and-Work run**: by default the run that shapes the item also does the
work, in the same run, with its context (the owner's input of 2026-11-23: "a single agent take an item through the non
mod pipeline"). The run itself records the size on the `shape` event. `small` (the default): it works on. `large`: it
stops after Shape, and the lane then gives the item its own Work runs (up to `max_runs_per_item`), not counting the
Shape run. The brief says when a run records `large`: the parts need more than one run's work, or need different
skills or models, or the run needs help. Asking for help (a `LEFT OPEN:` note, a route) is the other way to split.

## ACCEPTS (the only inputs this is built for)

- **an-open-item-with-no-check-and-no-route.** A ledger item that is not done, dropped or superseded, with no
  `Item.effect` and no routed part. Only these are due for Shape.
- **a-split-as-json.** `rimflow shape --parts` takes a JSON list of parts (or `@<path>` to a file of one).
  A part is `{"name", "effect" or null, "fooled_by" or null, "route" or null, "holds_why" optional}`; a route is
  `{"who": judge|owner|conductor|review, "ask", "resumes"}`.
- **a-check-in-the-step-1-forms.** Each part's check is a `list_effect` check (`path-has:`, `path-lacks:`, `cmd:`).

## DOES NOT SURVIVE (not promised)

- **a-check-that-tests-the-paper.** Whether a check tests the need is a judgement. The program counts only that a check
  exists and has its `fooled_by` line; a weak check (no line) is marked for the page and the weekly audit, never
  stopped. The weekly audit (plan step 5) reads what Shape runs wrote.
- **a-route-that-is-answered.** Nothing reads a route's answer. The party that answers re-shapes the item (`rimflow
  shape` again, the route replaced by a check, or dropped); until then the item's check fails and the lane reads it
  as routed or failing.
- **a-second-shape-after-a-dated-wait.** A lane item with a check whose dated wait passed gets its second look as a Work
  run, not as a Shape run (`design/specs/2026-11-23-list-dispatch/boundary.md`, a-passed-wait-gets-one-second-look). An
  old item that nobody named reads `reshape`.
- **the-fresh-reader-of-pipeline-code.** A Shape-and-Work run that changes pipeline code owes one fresh reader (CLAUDE.md
  §Code is clean). The lane does not launch that reader.
- **old-items-unnamed.** An item filed before `shape_from` never enters Shape by itself (plan: no hand migration of
  old items). It enters when someone names it.

## PROMISES (each one is owed a test of the same name)

- **an-item-filed-with-its-check-never-enters-shape.** `needs_shape_run` is False for an item with an outcome check,
  and the lane decides on it as before (never `shape`).
- **a-routed-item-needs-no-shape-run.** An item with a full route needs no Shape run; the lane reads it `routed`, with
  who holds it, what is asked and what resumes it, and launches nothing. This holds also when the item has a failing
  check beside the routed part: no Work run is launched until the party that answers re-shapes it.
- **shaped-means-every-part-has-a-check-or-a-full-route.** `shaped(parts)["shaped"]` is True only when there is at least
  one part and each part has an outcome check a program can read, or a route with a known `who` and a non-empty `ask`
  and `resumes`. Every other part is named in `unshaped`.
- **weak-is-a-mark-never-a-stop.** A part with a check and no `fooled_by` line is named in `weak`; `shaped` stays True.
  The `rimflow shape` write prints the weak parts and writes the event.
- **the-shape-write-refuses-an-unshaped-split-and-names-the-repair.** `rimflow shape --parts` with an unshaped part, an
  unreadable list, or a check that the step-1 gate refuses writes nothing and exits non-zero. Its message names each
  part and the repair, so the same run repairs it and writes again.
- **each-check-part-is-seen-failing.** Each part's check passes the step-1 gate (`list_effect.attach_gate`): seen
  failing now or at filing, or a `holds_why` beside it. A vacuous check is refused.
- **the-item-check-covers-every-part.** The write gives the item one outcome check: the part's own check when the item
  has one part and it has a check; else `cmd:python3 src/RimMandrake/rimflow/list_shape.py holds <ID>`, which exits 0
  only when every part's check holds. A routed part never holds, so a routed part keeps the item open. An item whose
  parts are all routed gets no check.
- **holds-keeps-fails-apart-from-could-not-look.** `list_shape.py holds <ID>` exits 0 when every part holds, 1 when one
  fails or is routed, 2 when a part's check is unmeasured and none fails, or when the ledger or the item's parts
  cannot be read. It never exits 0 on an item with no parts.
- **the-ledger-carries-the-shape.** A `shape` event replays into `Item.shape` (parts, size, when, who) and sets
  `Item.effect` to the derived check (None when all parts are routed). `--enter` replays into `Item.shape_named`. No
  stage keeps a store of its own.
- **old-items-enter-only-when-named.** An open item with no check and no route is due for Shape only when it is named,
  or it was filed at or after `shape_from` and is at least `shape_grace_h` old. Each reading says why in words.
- **a-naming-can-be-taken-off.** `rimflow shape <ID> --leave` takes the naming off an item: the item is due again only by
  its age, or when someone names it again. It keeps the item's split and check. On an item that is not named it writes
  nothing and says so. Why: on 2026-11-23 the old-ticket sort named 80 old items, and the owner stopped the sort.
- **the-lane-launches-a-shape-run-through-every-gate.** A due item reads `shape` and is launched as one detached run
  with the Shape brief, kind `shape`, model opus. The lane's gates (disabled, pause, `pipe off`, the owner's mod hold,
  a claim, a wait, the account, the chain rule, the slots, the clone pool) stop it as they stop a Work run.
- **a-shape-run-that-left-neither-check-nor-route-is-stopped.** When a Shape run ended and the item still has no check
  and no route, the item reads `stopped`, with its Needs Conductor line once. The line says that the item has neither. No second Shape run is launched by
  itself.
- **a-large-shape-run-is-not-a-work-run.** When the Shape run recorded `large`, it is not counted against
  `max_runs_per_item`, and its end without a `LEFT OPEN:` note does not stop the item: the lane launches the first Work
  run. A `small` Shape run counts as Work run 1.
- **a-due-item-enters-shape-when-its-adoption-cannot-happen.** A due item whose `## verify` acceptance script was refused
  as its check, or is too heavy to adopt, reads `shape`. A script that can be adopted is adopted first. An item that is
  not due reads `adopt_refused` or `adopt_too_heavy`.
- **a-passed-wait-never-keeps-a-due-item-out-of-shape.** A due item with no check whose dated wait passed reads `shape`
  (the plan's second look). A Shape run that left only a wait buys no second Shape run: the item reads `stopped`.
- **a-reshape-by-another-party-starts-the-run-count-again.** When a party that is no run of this item writes its split
  (the answer to a route, or the hand shape that a stop asks for), the runs launched before that split are not counted:
  Work run 1 launches. A split that a run of this item writes starts nothing again.
- **status-lists-every-item-due-for-shape.** `list_shape.py status` with no ids lists each open item that is shaped, named
  or due, by age too.
- **the-shape-brief-asks-for-the-need.** The brief names the item, the worth-the-touch test, the four routes, the
  `fooled_by` line, the size rule, and the `rimflow shape` command.
- **each-limit-names-its-danger.** `shape_grace_h` and `shape_from` in `list_dispatch.json` each have a `_<name>_doc`
  that names the danger it guards.

Later lists beside this page: `polish.md`.
