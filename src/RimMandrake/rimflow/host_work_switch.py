#!/usr/bin/env python3
"""host_work_switch.py - the one switch that says a machine works pipeline improvements only.

The owner, 2026-11-24: SteveDesktop works pipeline improvements only, with its own tickets first. Until 2026-11-25 that
order lived in one stop file (Archmagi's testq/fill.stop) and in the Conductor's memory. The steward aged the file into
a fault after 60 min, an Operations run wrote an expiry into it, a Conductor role run scheduled its removal, and at 12:00 PM
PST 2026-11-25 the idle filler started a DivingInteraction guard job on SteveDesktop (item
RIMMANDRAKE_VET_WORK_BOUND_FOR_STEVEDESKTOP_HE_SAW_FIREHAWK_AGAIN).

This switch is a tracked file (host_work_switch.json), so a set or a lift is a commit with its authority, on every
clone of both machines. It has no expiry: it stays until he or the Conductor lifts it.

  python3 src/RimMandrake/rimflow/host_work_switch.py show
  python3 src/RimMandrake/rimflow/host_work_switch.py set SteveDesktop --said "<his words>" [--publish]
  python3 src/RimMandrake/rimflow/host_work_switch.py lift SteveDesktop --said "<his words>" [--publish]
  python3 src/RimMandrake/rimflow/host_work_switch.py lift SteveDesktop --per-ruling \
      RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS --why "<act and reason>" [--publish]   (Conductor window only)

Readers (each refuses mod work for a switched host, and names the lift):
  testq pipeline_admit.switch_refusal(job)   submit, the fault-window rerun: a mod job (chains, rows, --full, a
                                              stage-6 checks job) for the SteveDesktop lane; a --proofs job is pipeline work
  testq fill_plan                             verdict "switched": the idle filler queues nothing for SteveDesktop
  testq steward                               SWITCHED is intentional and settled, never a fault
  work_bundle                                 a mod bundle is not sent to, or launched on, a switched host
  maturation_now                              the status page shows the switch

An unreadable switch file reads as SWITCHED for every host (could not look): nothing is admitted that cannot be shown
allowed.
"""
import argparse
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
PATH = os.path.join(HERE, "host_work_switch.json")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONDUCTOR_ACT = "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS"
HOSTS = {"stevedesktop": "SteveDesktop", "archmagi": "Archmagi"}
LIFT = 'python3 src/RimMandrake/rimflow/host_work_switch.py lift %s --said "<his words>"'
MODE = "pipeline"      # the one mode: pipeline improvements only, no mod work


class Unreadable(Exception):
    pass


def host_key(name):
    k = str(name or "").strip().lower()
    for prefix in ("stevedesktop", "archmagi"):
        if k.startswith(prefix):     # stevedesktop.b, Steve2's lock key, is the same machine
            return prefix
    if k in ("steve1", "steve2", "steve"):
        return "stevedesktop"
    if k in ("archbig", "archsmall"):
        return "archmagi"
    raise ValueError("unknown machine %r (known: %s)" % (name, ", ".join(sorted(HOSTS.values()))))


def known(name):
    """-> True when NAME is a machine (or one of its games) that this file can switch."""
    k = str(name or "").strip().lower()
    return k.startswith(("stevedesktop", "archmagi")) or k in ("steve1", "steve2", "steve", "archbig", "archsmall")


def _path(path=None):
    return path or os.environ.get("RM_HOST_SWITCH_FILE") or PATH


def _under_selftest():
    return bool(os.environ.get("RM_UNDER_SELFTEST")) or os.path.basename(sys.argv[0] or "").startswith("selftest")


def load(path=None):
    """-> {host key: row}. Raises Unreadable when the file is missing or cannot be parsed. A test process that names
    no file (RM_HOST_SWITCH_FILE) reads no switch: the machine's live order is not its input."""
    if path is None and not os.environ.get("RM_HOST_SWITCH_FILE") and _under_selftest():
        return {}
    p = _path(path)
    try:
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
        rows = doc["switches"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise Unreadable("%s: %s" % (p, e))
    return {host_key(r["host"]): r for r in rows}


def switched(host, path=None):
    """-> the text of the switch on HOST (pipeline work only), or None. An unreadable file -> a text (could not look)."""
    if not known(host):
        return None     # a machine this file does not know cannot be switched (an answer, not a blind read)
    k = host_key(host)
    try:
        row = load(path).get(k)
    except Unreadable as e:
        return "the host work switch cannot be read (%s): no mod work is admitted until it reads" % e
    if not row:
        return None
    by = ("his words, %s: \"%s\"" % (row.get("date"), row.get("said")) if row.get("said") else
          "the Conductor's act, %s: %s" % (row.get("date"), row.get("why")))
    return "%s works pipeline improvements only (%s); lift: %s" % (HOSTS[k], by, LIFT % HOSTS[k])


def _authority(said, per_ruling, why, env=None):
    his = isinstance(said, str) and bool(said.strip())
    if his == bool(per_ruling):
        raise ValueError("give his words (--said) or the Conductor's act (--per-ruling %s --why \"...\"), one of them"
                         % CONDUCTOR_ACT)
    if not his:
        if (per_ruling or "").strip() != CONDUCTOR_ACT or not (isinstance(why, str) and why.strip()):
            raise ValueError("the Conductor's act cites --per-ruling %s and carries --why" % CONDUCTOR_ACT)
        import principal
        ok, who = principal.conductor_window(env)
        if not ok:
            raise ValueError("only the Conductor window acts by %s: %s" % (CONDUCTOR_ACT, who))
    return his


def _write(doc, path=None):
    p = _path(path)
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(p + ".tmp", p)


def _doc(path=None):
    try:
        with open(_path(path), encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return {"switches": [], "lifted": []}


def set_switch(host, said=None, per_ruling=None, why=None, path=None, env=None, today=None):
    """Switch HOST to pipeline work only. -> the row. Raises ValueError on a missing or wrong authority."""
    his = _authority(said, per_ruling, why, env)
    k = host_key(host)
    doc = _doc(path)
    doc.setdefault("switches", [])
    doc["switches"] = [r for r in doc["switches"] if host_key(r["host"]) != k]
    row = {"host": HOSTS[k], "mode": MODE, "date": today or datetime.date.today().isoformat()}
    row.update({"said": said.strip()} if his else {"per_ruling": CONDUCTOR_ACT, "why": why.strip()})
    doc["switches"].append(row)
    _write(doc, path)
    return row


def lift(host, said=None, per_ruling=None, why=None, path=None, env=None, today=None):
    """Lift the switch on HOST. -> the lifted row. Raises KeyError when HOST is not switched, ValueError on authority."""
    his = _authority(said, per_ruling, why, env)
    k = host_key(host)
    doc = _doc(path)
    gone = [r for r in doc.get("switches", []) if host_key(r["host"]) == k]
    if not gone:
        raise KeyError("%s is not switched" % HOSTS[k])
    doc["switches"] = [r for r in doc["switches"] if host_key(r["host"]) != k]
    done = dict(gone[0], lifted=today or datetime.date.today().isoformat())
    done.update({"lifted_said": said.strip()} if his else {"lifted_by": "CONDUCTOR", "lifted_why": why.strip()})
    doc.setdefault("lifted", []).append(done)
    _write(doc, path)
    return done


def _publish(msg):
    """Hand this process to ./publish (it has its own guards and prints PUBLISHED <sha>); never returns."""
    sys.stdout.flush()
    os.chdir(REPO)
    os.execv(os.path.join(REPO, "publish"), ["./publish", "-m", msg, os.path.relpath(PATH, REPO)])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("show")
    for verb in ("set", "lift"):
        p = sub.add_parser(verb)
        p.add_argument("host")
        p.add_argument("--said", default=None, help="his words")
        p.add_argument("--per-ruling", default=None, help="the Conductor's act: %s" % CONDUCTOR_ACT)
        p.add_argument("--why", default=None, help="the Conductor's reason (with --per-ruling)")
        p.add_argument("--date", default=None, help="the day of his words or the act (default today)")
        p.add_argument("--publish", action="store_true", help="land the switch file with ./publish")
    o = ap.parse_args(argv)
    if o.verb == "show":
        try:
            rows = load()
        except Unreadable as e:
            print("COULD NOT LOOK: %s" % e)
            return 3
        if not rows:
            print("no machine is switched: every machine takes mod work")
        for k in sorted(rows):
            print(switched(k))
        return 0
    act = set_switch if o.verb == "set" else lift
    try:
        row = act(o.host, said=o.said, per_ruling=o.per_ruling, why=o.why, today=o.date)
    except (ValueError, KeyError) as e:
        print("REFUSED: %s" % (e.args[0] if e.args else e))
        return 1
    print("%s %s: %s" % ("SWITCHED" if o.verb == "set" else "LIFTED", row["host"], json.dumps(row, ensure_ascii=False)))
    if o.publish:
        return _publish("host_work_switch: %s %s (%s)" % (o.verb, row["host"], (o.said or o.why or "").strip()[:120]))  # cut-ok: a git commit subject; the whole text is in the stored row (danger: a subject of several hundred characters buries the log view)
    print("not landed: run it again with --publish, or ./publish %s" % os.path.relpath(PATH, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
