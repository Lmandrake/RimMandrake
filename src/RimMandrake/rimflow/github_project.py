#!/usr/bin/env python3
"""github_project.py — sync the mirrored GitHub issues onto a GitHub Projects v2
board, as a DURABLE, idempotent projection (never a one-off click-through).

QUEUE_GITHUB_MIRROR_1's third sibling: github_mirror.py pushes rimflow items to
GitHub Issues one-way; board_viz.py renders them as a local HTML board;
this script pushes the SAME derived state (board_viz.build_tickets(), which
reuses infer_effort/infer_importance unchanged) onto a real Projects v2 board
owned by Lmandrake, titled "RimMaster Tickets", so the same picture is visible
inside GitHub itself — filterable, sortable, no local file to open.

Ledger stays the truth. This writes GitHub only, never the ledger. Deleting the
project loses nothing that isn't already in events.jsonl + the mirror map.

State lives beside the mirror map, committed:
    infrastructure/state/ledger/github_project_state.json
holding the project number/node-id and every custom field's id + option ids,
so a re-run never re-creates the project or a field — it looks them up once,
then only ever adds/edits items. `gh project item-add` is itself idempotent
per URL (returns the existing item, never a duplicate), so the item loop below
does too.

Fields:
  Importance (low/medium/high/critical), Effort (S/M/L/XL),
  Needs (offline/deploy/game-up/bridge/harvest/owner),
  Seat (BENCH/FOUNDRY — the two LIVE windows; legacy-seat items leave this
  field unset rather than inventing an option nobody asked for),
  Kind (task/build — the two the owner named; the ledger actually carries 11
  kind values, and the other 9 leave this field unset for the same reason).
  Status is GitHub's own built-in field: proposed/ready -> Todo,
  doing -> In Progress, done/dropped/superseded -> Done.

Default is DRY RUN: prints the plan, touches nothing. --apply executes via
`gh` (CLI verbs) and `gh api graphql` (per-item field batch — the CLI has no
single verb for "set five fields on one item", so one graphql mutation per
item aliases all its field writes into one call).

Invoke after `github_mirror.py --apply`, so the map it reads is current:
    python3 src/RimMandrake/rimflow/github_project.py --apply
or via `github_mirror.py --apply --with-project`, which chains this in.
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import model
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from board_viz import build_tickets, GH_REPO  # noqa: E402  (reuses the ONE derivation)

OWNER = "Lmandrake"
TITLE = "RimMaster Tickets"
STATE_PATH = os.path.join(model.LEDGER, "github_project_state.json")

# name -> ordered options. Order is cosmetic (GitHub shows them in creation
# order); values must match what board_viz/model actually emit.
CUSTOM_FIELDS = {
    "Importance": ["low", "medium", "high", "critical"],
    "Effort": ["S", "M", "L", "XL"],
    "Needs": ["offline", "deploy", "game-up", "bridge", "harvest", "owner"],
    "Seat": ["BENCH", "FOUNDRY"],
    "Kind": ["task", "build"],
}

STATUS_MAP = {
    "proposed": "Todo", "ready": "Todo", "doing": "In Progress",
    "done": "Done", "dropped": "Done", "superseded": "Done",
}


def gh_json(args):
    r = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("gh %s\nFAILED: %s" % (" ".join(args), r.stderr.strip()))
    return json.loads(r.stdout)


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {}


def save_state(st):
    with open(STATE_PATH, "w") as f:
        json.dump(st, f, indent=1, sort_keys=True)


def ensure_project(st, apply_, plan):
    """Find-or-create ONE project titled TITLE on OWNER. Never re-creates."""
    if st.get("number") and st.get("id"):
        return st["number"], st["id"], st.get("url")

    listing = gh_json(["project", "list", "--owner", OWNER, "--format", "json", "-L", "100"])
    for p in listing["projects"]:
        if p["title"] == TITLE:
            plan.append("(found existing project #%d %r — reusing, not creating)"
                        % (p["number"], TITLE))
            return p["number"], p["id"], p["url"]

    plan.append('gh project create --owner %s --title "%s"' % (OWNER, TITLE))
    if not apply_:
        return None, None, None
    created = gh_json(["project", "create", "--owner", OWNER, "--title", TITLE,
                       "--format", "json"])
    return created["number"], created["id"], created["url"]


def ensure_fields(number, apply_, plan):
    """-> {field_name: {"id": fid, "options": {optname: optid}}}, including Status."""
    fields = {}
    if number is None:  # dry run, project doesn't exist yet
        return fields
    have = gh_json(["project", "field-list", str(number), "--owner", OWNER,
                    "--format", "json", "-L", "50"])["fields"]
    by_name = {f["name"]: f for f in have}

    if "Status" in by_name:
        fields["Status"] = {
            "id": by_name["Status"]["id"],
            "options": {o["name"]: o["id"] for o in by_name["Status"].get("options", [])},
        }

    for name, opts in CUSTOM_FIELDS.items():
        if name in by_name:
            f = by_name[name]
            fields[name] = {"id": f["id"],
                            "options": {o["name"]: o["id"] for o in f.get("options", [])}}
            continue
        plan.append('gh project field-create %d --name "%s" --data-type SINGLE_SELECT '
                    '--single-select-options "%s"' % (number, name, ",".join(opts)))
        if not apply_:
            continue
        created = gh_json(["project", "field-create", str(number), "--owner", OWNER,
                           "--name", name, "--data-type", "SINGLE_SELECT",
                           "--single-select-options", ",".join(opts), "--format", "json"])
        fields[name] = {"id": created["id"],
                        "options": {o["name"]: o["id"] for o in created["options"]}}
    return fields


def item_add(project_number, issue_number, apply_, plan):
    url = "https://github.com/%s/issues/%d" % (GH_REPO, issue_number)
    plan.append("gh project item-add %d --url %s" % (project_number, url))
    if not apply_:
        return None
    r = gh_json(["project", "item-add", str(project_number), "--owner", OWNER,
                "--url", url, "--format", "json"])
    return r["id"]


def set_fields(project_id, item_id, sets, apply_, plan):
    """sets: [(field_id, option_id, label-for-the-plan)]. One graphql call, N aliases —
    the CLI has no verb for 'edit several fields on one item' in a single round trip."""
    if not sets:
        return
    plan.append("gh api graphql (set %s)" % ", ".join(s[2] for s in sets))
    if not apply_:
        return
    parts = []
    for i, (field_id, option_id, _label) in enumerate(sets):
        parts.append(
            'f%d: updateProjectV2ItemFieldValue(input: {projectId: "%s", itemId: "%s", '
            'fieldId: "%s", value: {singleSelectOptionId: "%s"}}) '
            '{ projectV2Item { id } }' % (i, project_id, item_id, field_id, option_id))
    query = "mutation { " + " ".join(parts) + " }"
    r = subprocess.run(["gh", "api", "graphql", "-f", "query=" + query],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("gh api graphql FAILED for item %s: %s" % (item_id, r.stderr.strip()))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true",
                    help="execute via gh (default: dry run, print the plan)")
    args = ap.parse_args()

    plan = []
    st = load_state()
    number, project_id, url = ensure_project(st, args.apply, plan)
    fields = ensure_fields(number, args.apply, plan)

    if args.apply:
        if number is None:
            sys.exit("project create did not report a number — aborting before state write")
        st.update({"number": number, "id": project_id, "url": url})
        save_state(st)

    tickets = build_tickets()  # only MIRRORED items — same source as board_labels.py

    added, edited = 0, 0
    for t in tickets:
        if not t["issue"]:
            continue
        item_id = item_add(number, t["issue"], args.apply, plan)
        added += 1

        sets = []
        if "Importance" in fields and t["importance"] in fields["Importance"]["options"]:
            sets.append((fields["Importance"]["id"],
                        fields["Importance"]["options"][t["importance"]],
                        "Importance=%s" % t["importance"]))
        if "Effort" in fields and t["effort"] in fields["Effort"]["options"]:
            sets.append((fields["Effort"]["id"], fields["Effort"]["options"][t["effort"]],
                        "Effort=%s" % t["effort"]))
        if "Needs" in fields and t["needs"] in fields["Needs"]["options"]:
            sets.append((fields["Needs"]["id"], fields["Needs"]["options"][t["needs"]],
                        "Needs=%s" % t["needs"]))
        if "Seat" in fields and t["owner"] in fields["Seat"]["options"]:
            sets.append((fields["Seat"]["id"], fields["Seat"]["options"][t["owner"]],
                        "Seat=%s" % t["owner"]))
        if "Kind" in fields and t["kind"] in fields["Kind"]["options"]:
            sets.append((fields["Kind"]["id"], fields["Kind"]["options"][t["kind"]],
                        "Kind=%s" % t["kind"]))
        status = STATUS_MAP.get(t["state"])
        if "Status" in fields and status in fields["Status"]["options"]:
            sets.append((fields["Status"]["id"], fields["Status"]["options"][status],
                        "Status=%s" % status))

        if sets:
            set_fields(project_id, item_id, sets, args.apply, plan)
            edited += 1

    mode = "APPLIED" if args.apply else "DRY RUN — nothing touched"
    print("%s: project #%s %s" % (mode, number, url or "(not yet created)"))
    print("  %d mirrored ticket(s), %d item-add(s) planned, %d field-set batch(es)"
         % (len(tickets), added, edited))
    if not args.apply:
        for line in plan[:20]:
            print("  " + line)
        if len(plan) > 20:
            print("  ... and %d more" % (len(plan) - 20))


if __name__ == "__main__":
    main()
