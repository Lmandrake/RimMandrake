#!/usr/bin/env python3
"""list_shape.py: the List Pipeline's Shape stage. An item with no outcome check gets parts, each with a check that tests
the need (and its "what would pass this check and leave the need unmet?" line), or a route. No model, no tokens.

Item RIMMANDRAKE_BUILD_SHAPE_STAGE_CHECK_TESTS_THE_NEED_NOT_PAPER, step 4 of
design/specs/2026-11-22-coordination-every-agent-must-use/plan.md (§Shape). Page design/specs/2026-11-23-list-shape/
boundary.md; selftest selftest_list_shape.py; acceptance acceptance/step4_shape_accept.py. Why: on 2026-11-23 about 70 of
1,527 open items carried an outcome check, so the lane (list_dispatch.py) could see only those.

    python3 src/RimMandrake/rimflow/list_shape.py holds ID          exit 0 every part's check holds; 1 one fails or is
                                                                    routed; 2 could not look (no parts, a blind check)
    python3 src/RimMandrake/rimflow/list_shape.py status [ID...]    the Shape facts of open items: due, shaped, weak, routed

The write is `rimflow shape <ID> --parts '<json list>' [--size small|large]` (cli.cmd_shape, which calls
`write_fields`), and `rimflow shape <ID> --enter` names an old item for Shape (`--leave` takes it off). The lane launches the Shape run
(list_dispatch.decide: `shape`), with the brief roles/list_shape.md filled by `brief_text`.
A part: {"name", "effect": check or None, "fooled_by": str or None, "route": None or {"who", "ask", "resumes"},
"holds_why": optional}. The checks are list_effect's forms.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ITEM = "RIMMANDRAKE_BUILD_SHAPE_STAGE_CHECK_TESTS_THE_NEED_NOT_PAPER"
ROUTES = ("judge", "owner", "conductor", "review")
SIZES = ("small", "large")
BRIEF = os.path.join(HERE, "roles", "list_shape.md")
HOLDS_CMD = "cmd:python3 src/RimMandrake/rimflow/list_shape.py holds %s"
CLOSED = ("done", "dropped", "superseded")


def _text(v):
    return v.strip() if isinstance(v, str) and v.strip() else None


def route_ok(r):
    """-> True when r is a hand-over: a known `who`, and a non-empty `ask` and `resumes`."""
    return (isinstance(r, dict) and r.get("who") in ROUTES and bool(_text(r.get("ask")))
            and bool(_text(r.get("resumes"))))


def _check_ok(text):
    import list_effect as LE
    return bool(_text(text)) and LE.parse(text)["kind"] != "unreadable"


def _name(p, i):
    return str((p.get("name") if isinstance(p, dict) else None) or "part %d" % (i + 1))


def shaped(parts):
    """-> {"shaped", "unshaped", "weak"}. A part is shaped when it has a check a program can read, or a full route.
    "weak" names each check part with no fooled_by line: a mark for the page and the audit, never a stop."""
    unshaped, weak = [], []
    for i, p in enumerate(parts or []):
        n = _name(p, i)
        if not isinstance(p, dict):
            unshaped.append(n)
            continue
        if _check_ok(p.get("effect")):
            if not _text(p.get("fooled_by")):
                weak.append(n)
        elif not route_ok(p.get("route")):
            unshaped.append(n)
    return {"shaped": bool(parts) and not unshaped, "unshaped": unshaped, "weak": weak}


def needs_shape_run(item):
    """item = {"effect", "route", "parts"} -> True when the item has no check, no route and no shaped split."""
    item = item or {}
    if _text(item.get("effect")) or route_ok(item.get("route")):
        return False
    return not shaped(item.get("parts"))["shaped"]


def first_route(parts):
    for p in parts or []:
        if isinstance(p, dict) and not _check_ok(p.get("effect")) and route_ok(p.get("route")):
            return p["route"]
    return None


def item_check(iid, parts):
    """-> the item's one outcome check: a lone check part's own check; the holds command when there is more than one
    part; None when no part has a check."""
    checks = [p["effect"].strip() for p in parts or [] if isinstance(p, dict) and _check_ok(p.get("effect"))]
    if not checks:
        return None
    if len(parts) == 1:
        return checks[0]
    return HOLDS_CMD % iid


def due(item, cfg, now):
    """item = {"effect", "route", "parts", "named": epoch or None, "filed": epoch or None} -> (bool, why).
    Due for a Shape run: no check, no route, no shaped split, and named, or filed at or after shape_from and at least
    shape_grace_h old (an old item enters only when someone names it: plan §What the plan does not do)."""
    item = item or {}
    if not needs_shape_run(item):
        if _text(item.get("effect")):
            return False, "it carries an outcome check"
        if route_ok(item.get("route")):
            return False, "it is routed to %s" % item["route"]["who"]
        return False, "it is shaped already"
    if item.get("named"):
        return True, "named for Shape at %s" % _pac(item["named"])
    frm = (cfg or {}).get("shape_from")
    filed = item.get("filed")
    if not frm:
        return False, "it was never named for Shape, and no shape_from is set, so no item enters by itself"
    frm = _epoch(frm)
    if filed is None or filed < frm:
        return False, "filed before Shape went live (%s) and never named (`rimflow shape <ID> --enter`)" % _pac(frm)
    grace = float((cfg or {}).get("shape_grace_h", 24)) * 3600
    if now - filed < grace:
        return False, "filed %.1f h ago; its filer gets %g h to close or claim it first" % (
            (now - filed) / 3600, grace / 3600)
    return True, "filed %.1f h ago with no check and no route" % ((now - filed) / 3600)


def _epoch(v):
    if isinstance(v, (int, float)):
        return float(v)
    import model as LM
    return LM.epoch(v)


def _pac(t):
    import datetime as dt
    pac = dt.timezone(dt.timedelta(hours=-8), "PST")
    return dt.datetime.fromtimestamp(t, pac).strftime("%Y-%m-%d %I:%M %p %Z").replace(" 0", " ")


def facts(item):
    """model.Item -> {"effect", "route", "parts", "size", "weak", "named", "filed", "shape_at", "shape_unit"}: the Shape
    facts the lane and the stage view read. The route is the first part that is routed and has no check. shape_at and
    shape_unit: when the last split was written, and by which unit (None: a window)."""
    sh = getattr(item, "shape", None) or {}
    parts = sh.get("parts")
    named = getattr(item, "shape_named", None)
    import model as LM
    created = getattr(item, "created_at", None)
    return {"effect": getattr(item, "effect", None), "route": first_route(parts), "parts": parts,
            "size": sh.get("size"), "weak": shaped(parts)["weak"] if parts else [],
            "named": _epoch(named) if named else None, "filed": LM.epoch(created) if created else None,
            "shape_at": LM.epoch(sh["at"]) if sh.get("at") else None, "shape_unit": sh.get("unit")}


# ---- the write (cli.cmd_shape) -------------------------------------------------------------------------------------

REPAIR = ("each part needs an outcome check (path-has:<repo path>::<text>, path-lacks:<repo path>::<text> or "
          "cmd:<command>) with its fooled_by line, or a route {\"who\": one of %s, \"ask\": \"<what is asked>\", "
          "\"resumes\": \"<what resumes the item>\"}" % "|".join(ROUTES))


def read_parts(text):
    """`--parts` text (a JSON list, or {"parts": [...]}, or @<path>) -> (parts, None) or (None, why)."""
    t = (text or "").strip()
    if t.startswith("@"):
        try:
            with open(t[1:], encoding="utf-8") as f:
                t = f.read()
        except OSError as e:
            return None, "the parts file cannot be read: %s" % e
    try:
        v = json.loads(t)
    except ValueError as e:
        return None, "the parts are not JSON (%s); give a JSON list of parts" % e
    if isinstance(v, dict) and isinstance(v.get("parts"), list):
        v = v["parts"]
    if not isinstance(v, list):
        return None, "the parts are not a JSON list"
    return v, None


def write_fields(iid, parts, size, gate):
    """-> (fields for the `shape` event, notes) or (None, refusal). gate(check, holds_why) -> (seen, refusal) is
    list_effect.attach_gate bound to the item. Nothing is written on a refusal; the refusal names each part and the
    repair, so the same run repairs it and writes again."""
    size = size or "small"
    if size not in SIZES:
        return None, "the size %r is not one of %s" % (size, ", ".join(SIZES))
    s = shaped(parts)
    if not s["shaped"]:
        if not parts:
            return None, "no parts: an empty split is not a split. Repair: %s." % REPAIR
        return None, "not shaped: %s. Repair: %s." % (", ".join(s["unshaped"]), REPAIR)
    names = [_name(p, i) for i, p in enumerate(parts)]
    if len(set(names)) != len(names):
        return None, "two parts share a name (%s); give each part its own name" % ", ".join(names)
    out, refusals = [], []
    for n, p in zip(names, parts):
        q = {"name": n, "effect": None, "fooled_by": _text(p.get("fooled_by")), "route": None}
        if _check_ok(p.get("effect")):
            q["effect"] = p["effect"].strip()
            seen, refusal = gate(q["effect"], _text(p.get("holds_why")))
            if refusal:
                refusals.append("part %s: %s" % (n, refusal))
                continue
            q["seen"] = seen
            if _text(p.get("holds_why")):
                q["holds_why"] = p["holds_why"].strip()
        else:
            r = p["route"]
            q["route"] = {"who": r["who"], "ask": r["ask"].strip(), "resumes": r["resumes"].strip()}
        out.append(q)
    if refusals:
        return None, "the step-1 gate refused a part's check:\n" + "\n".join(refusals)
    ev = {"parts": out, "size": size}
    check = item_check(iid, out)
    if check:
        ev["check"] = check
        ev["seen"] = (out[0]["seen"] if check == out[0].get("effect") else
                      {"verdict": "fails", "why": "each check part passed the step-1 gate at shape"})
    notes = []
    if s["weak"]:
        notes.append("weak (no 'what would pass this check and leave the need unmet' line; marked for the page and "
                     "the weekly audit, not stopped): %s" % ", ".join(s["weak"]))
    return ev, notes


# ---- the item check -------------------------------------------------------------------------------------------------

def holds_parts(parts, root, run=None):
    """-> (code, lines): 0 every part holds; 1 one fails or is routed; 2 none fails and one could not be looked at, or
    no parts. A routed part never holds: it keeps the item open until it is re-shaped."""
    if not parts:
        return 2, ["the item has no parts to check"]
    if run is None:
        import list_effect as LE
        run = LE.run
    fails = blind = 0
    lines = []
    for i, p in enumerate(parts):
        n = _name(p, i)
        if not isinstance(p, dict):
            blind += 1
            lines.append("%s: unreadable part" % n)
        elif _check_ok(p.get("effect")):
            v, out = run(p["effect"], root)
            fails += v == "fails"
            blind += v not in ("holds", "fails")
            lines.append("%s: %s (%s) %s" % (n, v, p["effect"], " ".join(str(out or "").split())[:200]))  # cut-ok: terminal display
        elif route_ok(p.get("route")):
            fails += 1
            r = p["route"]
            lines.append("%s: routed to %s (%s); resumes on %s" % (n, r["who"], r["ask"], r["resumes"]))
        else:
            blind += 1
            lines.append("%s: neither a check nor a route" % n)
    return (1 if fails else 2 if blind else 0), lines


def holds_main(iid):
    try:
        import list_effect as LE
        w = LE._world()
        it = w.items.get(iid)
    except Exception as e:  # noqa: BLE001 - could not look is never a verdict
        print("UNMEASURED: the ledger could not be read (%s: %s)" % (type(e).__name__, e))
        return 2
    if it is None:
        print("UNMEASURED: %s has never been filed" % iid)
        return 2
    code, lines = holds_parts((it.shape or {}).get("parts"), LE.check_root())
    for ln in lines:
        print(ln)
    print({0: "HOLDS", 1: "FAILS", 2: "UNMEASURED"}[code] + ": %s" % iid)
    return code


# ---- the Shape run's brief ------------------------------------------------------------------------------------------

def brief_text(iid, it, row):
    with open(BRIEF, encoding="utf-8") as f:
        text = f.read()
    text = text.split("<!-- BRIEF -->", 1)[-1]
    return (text.replace("{item}", iid).replace("{title}", str((it or {}).get("title") or "-"))
            .replace("{why_due}", str((it or {}).get("shape_why") or (row or {}).get("why") or "-"))
            .replace("{routes}", ", ".join(ROUTES)).strip() + "\n")


# ---- status ---------------------------------------------------------------------------------------------------------

def status_main(ids):
    import list_effect as LE
    try:
        import list_dispatch as LD
        cfg = LD.load_cfg()
    except Exception:  # noqa: BLE001 - no cfg: due() reads "no shape_from"
        cfg = {}
    w = LE._world()
    now = time.time()
    picked = ids or [i for i, x in w.items.items() if x.state not in CLOSED and (
        x.shape or x.shape_named or due(facts(x), cfg, now)[0])]
    counts = {}
    for iid in picked:
        x = w.items.get(iid)
        if x is None:
            print("%-64s never filed" % iid)
            continue
        f = facts(x)
        d, why = due(f, cfg, now)
        s = shaped(f["parts"]) if f["parts"] else None
        kind = ("closed" if x.state in CLOSED else "due" if d else "routed" if f["route"] and not f["effect"]
                else "shaped" if s and s["shaped"] else "checked" if f["effect"] else "not due")
        counts[kind] = counts.get(kind, 0) + 1
        print("%-64s %-8s %s" % (iid, kind, why))
        for p in f["parts"] or []:
            tag = "check" if p.get("effect") else "route"
            print("    %-24s %s %s%s" % (p["name"], tag, p.get("effect") or json.dumps(p.get("route")),
                                         "" if not p.get("effect") or p.get("fooled_by") else "   [weak]"))
            if p.get("fooled_by"):
                print("    %-24s fooled by: %s" % ("", p["fooled_by"]))
        if f["effect"]:
            print("    item check: %s  (size %s)" % (f["effect"], f["size"] or "-"))
    print("list_shape status: %d item(s); %s" % (len(picked), ", ".join("%s %d" % kv for kv in sorted(counts.items()))))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("holds")
    h.add_argument("id")
    s = sub.add_parser("status")
    s.add_argument("ids", nargs="*")
    o = ap.parse_args(argv)
    if o.cmd == "holds":
        return holds_main(o.id)
    return status_main(o.ids)


if __name__ == "__main__":
    sys.exit(main())
