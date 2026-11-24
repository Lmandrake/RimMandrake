#!/usr/bin/env python3
"""The owner's hold on mods in the Maturation Pipeline (item RIMMANDRAKE_HOLD_SIX_BIOME_MODS_ONLY_PYRELANDS_STAYS).

The owner, 2026-11-16 ~5:20 PM PST: "And stop the new biome mods work. Only Pyrelands as a biome mod right now. They are
poorly defined builds right now and the system choked at their lack of precision I think."

One list, in mod_owner_hold.json beside this file. A mod on it:
  - the Dispatch tick (maturation_dispatch._tick) launches nothing on it: no builder, judge, live driver, steward, fixer
    or holder; its row reads decision owner_hold, klass held, status HELD BY OWNER with his words, date and the lift
    command, and it counts toward no idle, paused or stalled list;
  - the Designer and DesignerCodex chain (role_launch.chain_sweep, chain_ask) asks no run for it, and a run-now already
    pending on it is refused at launch (said once, no alarm);
  - ops_watch's queues.designer stall reader skips it.
Design text written by a helper on a held mod is allowed (owner, by card 2026-11-19: "Design text is allowed, and we WILL
return to the mods... they're not going to be deprecated, don't worry."); builds, tests and live runs stay held and the
held mods are not deprecated. This file governs what the pipeline launches, nothing else.
A run already live on a held mod is allowed to finish: nothing here stops, kills or reaps anything, and its spend and
ledger rows are still recorded by the tick. Names match by the last path part, so design/concepts/Cauldron,
RimMandrake/Cauldron and Cauldron are one mod. An unreadable or malformed file raises Unreadable: a reader launches
nothing it cannot prove unheld (never a calm "no holds").

The control store (control.py) is the one writer of his hold; mod_owner_hold.json is its mirror, a read copy the store
writes (item RIMMANDRAKE_BUILD_HOLD_FILE_MIRROR_HE_SAID_COMMISSION_ALL; page
design/specs/2026-11-18-pipeline-control-surface/boundary.md). Every write below changes the store first, then rewrites
the file from the store's rows. A file row the store lacks is learned into the store, never dropped; only `lift` lifts,
with his words or as the Conductor's lift. A mirror that cannot be written raises the alarm control:owner_hold_mirror and exits 5; the store's hold
stands.

  mod_owner_hold.py show            the list, each with his words, date and lift command
  mod_owner_hold.py hold <Mod> --said "<his words>" [--date D]   hold one (then publish mod_owner_hold.json)
  mod_owner_hold.py lift <Mod> --said "<his words>"   remove one (then publish mod_owner_hold.json)
  mod_owner_hold.py lift <Mod> --per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_LIFT_HOLD_NOT_HIM_ALONE --why "<reason>"
      the Conductor's lift (owner, by card 2026-11-19: "yes... but Conductor should also be able to lift a Hold. We
      work together, don't use me as a bottleneck alone."). Only from the Conductor window (AGENT_SEAT BENCH, no
      RM_ROLE_UNIT: never a launched helper, role run, other seat or the tick). It writes a `delegated: scope` note on
      the ledger first (his daily digest reads it; no note, no lift), then lifts in the store as the Conductor's act
      (per_ruling that item, never his words); the mirror's `lifted` row says lifted_by CONDUCTOR. A lifted mod still
      does not run while its readiness list is not READY (owner 2026-11-19, No mod runs forward on a broken pipeline).
  mod_owner_hold.py mirror          rewrite the file from the store (after an alarm; pipe doctor shows drift)
  mod_owner_hold.py allow-design <Mod> --said "<his words>"   the hold stays on builds; his words on the row allow a
      design-only pass (designer_cleanse.py run refuses a held mod without them; item
      RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED). Nothing else reads the field: no build, chain or
      Dispatch launch changes.
Selftest: selftest_mod_owner_hold.py.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
PATH = os.path.join(HERE, "mod_owner_hold.json")
LIFT = 'python3 src/RimMandrake/rimflow/mod_owner_hold.py lift %s --said "<his words>"'
CONDUCTOR_LIFT = "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_LIFT_HOLD_NOT_HIM_ALONE"     # = control.CONDUCTOR_LIFT
CLI = os.path.join(HERE, "cli.py")


def conductor_window(env=None):
    """-> (ok, why): is this process the Conductor window? Seat BENCH (AGENT_SEAT, else RIMFLOW_SEAT) and no
    RM_ROLE_UNIT (every launched run, detached helper or role run, carries one). Anything else is not the Conductor."""
    import principal            # the one definition (seat BENCH, typed BENCH or CONDUCTOR; no RM_ROLE_UNIT)
    return principal.conductor_window(env)


def _digest_note(mod, why):
    """The Conductor's lift on the ledger, before it lifts: a BENCH note on CONDUCTOR_LIFT whose why starts
    `delegated: scope:`, so his daily digest (delegated_digest.py) shows it. Raises RuntimeError when it is not written."""
    import subprocess
    text = "the Conductor lifted the owner hold on %s" % key(mod)
    r = subprocess.run([sys.executable, CLI, "note", CONDUCTOR_LIFT, "--seat", "BENCH", "--text", text, "--why",
                        "delegated: scope: %s per %s: %s" % (text, CONDUCTOR_LIFT, why.strip())],
                       capture_output=True, text=True, timeout=300)  # budget: class=rimflow
    if r.returncode != 0:
        raise RuntimeError("the digest note was not written (rimflow note exit %d: %s)"
                           % (r.returncode, (r.stderr or r.stdout).strip()[-300:]))


MIRROR_ALARM = "control:owner_hold_mirror"
MIRROR_FAILED = 5      # exit codes: 0 done, 1 refused (not held, no words), 3 could not look, 5 mirror alarm


class Unreadable(Exception):
    pass


class MirrorFailed(OSError):
    """The store was written; its mirror file could not be. The store's hold binds; the alarm is raised."""


def key(name):
    """design/concepts/Cauldron, /abs/.../Cauldron/, RimMandrake/Cauldron, Cauldron -> Cauldron."""
    return os.path.basename(os.path.normpath(str(name or "")))


def load_file(path=None):
    """-> {mod: {"mod", "date", "said"}} from the JSON file alone (the published mirror). Raises Unreadable on a missing,
    unparsable or wrong-shaped file."""
    p = path or os.environ.get("RM_OWNER_HOLD_FILE") or PATH
    try:
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError) as e:
        raise Unreadable("%s: %s" % (p, e))
    holds = doc.get("holds") if isinstance(doc, dict) else None
    if not isinstance(holds, list):
        raise Unreadable("%s: no \"holds\" list" % p)
    out = {}
    for h in holds:
        if not (isinstance(h, dict) and isinstance(h.get("mod"), str) and h["mod"].strip()
                and isinstance(h.get("said"), str) and h["said"].strip() and isinstance(h.get("date"), str)):
            raise Unreadable("%s: a hold needs mod, said (his words) and date: %r" % (p, h))
        d = h.get("design_allowed")
        if d is not None and not (isinstance(d, dict) and isinstance(d.get("said"), str) and d["said"].strip()
                                  and isinstance(d.get("date"), str) and d["date"].strip()):
            raise Unreadable("%s: design_allowed needs said (his words) and date: %r" % (p, h))
        if key(h["mod"]) in out:
            raise Unreadable("%s: %s is held twice (rows %r and %r)" % (p, key(h["mod"]), out[key(h["mod"])], h))
        out[key(h["mod"])] = h
    return out


def load(path=None):
    """-> {mod: {"mod", "date", "said"}}: the file's holds (minus any the control store records as lifted, so a lift
    binds at once, before its mirror is published), then every mod switch in the control store (control.py: his holds
    imported with his words, and `pipe off <Mod>` rows, control=True), the moment it is written. Raises Unreadable on a
    bad file or an unreadable store: a reader launches nothing it cannot prove unheld (never a calm "no holds").
    path: read that file alone (no store)."""
    out = load_file(path)
    if path is None:
        import control as C
        try:
            lifted = C.lifted_owner()
            out = {m: h for m, h in out.items() if (m, h.get("date") or "", h.get("said") or "") not in lifted}
            for m, row in C.mod_holds().items():
                out.setdefault(key(m), row)
        except C.Unreadable as e:
            raise Unreadable("the control store: %s" % e)
    return out


def _rewrite(p, change):
    """Read, change and write the hold file as one step: under an exclusive lock, validated by load() first, written to
    a temp file and moved over it, so a crash or a second writer never leaves a half or stale list. The lock lives in
    the temp dir (keyed by the file's real path), not beside the file: a lock file in the tree would dirty every clone."""
    import fcntl
    import hashlib
    import tempfile
    lock = os.path.join(tempfile.gettempdir(), "mod_owner_hold.%s.lock"
                        % hashlib.sha1(os.path.realpath(p).encode()).hexdigest()[:16])
    with open(lock, "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        load(p)
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
        out = change(doc)
        fd, tmp = tempfile.mkstemp(prefix=".mod_owner_hold.", dir=os.path.dirname(os.path.abspath(p)))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            load(tmp)       # the new bytes must read as a hold list before they replace the old
            os.replace(tmp, p)
            dfd = os.open(os.path.dirname(os.path.abspath(p)), os.O_RDONLY)
            try:
                os.fsync(dfd)   # the rename itself survives a crash
            finally:
                os.close(dfd)
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
        return out


def held(name, holds=None):
    """-> the hold on `name` (any path spelling), or None. holds: load()'s mapping (read here when None)."""
    return (load() if holds is None else holds).get(key(name))


def status(h):
    """The one line every status prints for a held mod."""
    if h.get("unreadable"):
        return "CONTROL UNREADABLE: %s: nothing launches on %s until it can be read (pipe doctor)" % (h.get("said"),
                                                                                                   h["mod"])
    if h.get("control"):
        return "OFF by pipe (act %s at %s): %s (on: pipe on %s --why \"...\")" % (
            h.get("act"), h.get("at_pacific"), h.get("said"), h["mod"])
    return "HELD BY OWNER %s: \"%s\" (lift: %s)" % (h["date"], h["said"], LIFT % h["mod"])


def lift(mod, said=None, path=None, per_ruling=None, why=None):
    """Lift his hold on `mod`: in the control store (binds at once), then the file is rewritten from the store (its
    mirror). The authority is his words (`said`) or the Conductor's lift (`per_ruling` CONDUCTOR_LIFT with `why`, from
    the Conductor window, its digest note written first). -> the hold removed. Raises KeyError when neither holds it,
    ValueError when the authority is missing or not the Conductor's, RuntimeError when the digest note is not written
    (nothing lifted), MirrorFailed (alarm raised) when the store lifted it but the file could not be written.
    path: that file alone, no store and no note (a fixture)."""
    his = isinstance(said, str) and bool(said.strip())
    if his == bool(per_ruling):
        raise ValueError("a lift takes his words (--said) or the Conductor's lift (--per-ruling %s --why \"...\"), "
                         "one of them" % CONDUCTOR_LIFT)
    if not his:
        if (per_ruling or "").strip() != CONDUCTOR_LIFT or not (isinstance(why, str) and why.strip()):
            raise ValueError("the Conductor's lift cites --per-ruling %s and carries --why" % CONDUCTOR_LIFT)
        ok, who = conductor_window()
        if not ok:
            raise ValueError("only the Conductor window lifts by %s: %s" % (CONDUCTOR_LIFT, who))
    p = path or os.environ.get("RM_OWNER_HOLD_FILE") or PATH
    if path is None:
        import control as C
        f = load_file(p).get(key(mod))
        if f is None and key(mod) not in {m for m, r in C.mod_holds().items() if r.get("store")}:
            raise KeyError("%s is not held" % mod)
        if not his:
            _digest_note(mod, why)      # no note, no lift: the Conductor's lift always reaches his digest
        gone = C.lift_owner(key(mod), said if his else None, date=(f or {}).get("date"),
                            held_said=(f or {}).get("said"), per_ruling=None if his else CONDUCTOR_LIFT,
                            why=None if his else why)
        if f is None and gone is None:
            raise KeyError("%s is not held" % mod)
        _mirror_or_alarm(p, "lift %s" % key(mod))
        return f or gone

    def change(doc):
        keep = [h for h in doc["holds"] if key(h.get("mod")) != key(mod)]
        if len(keep) == len(doc["holds"]):
            raise KeyError("%s is not held" % mod)
        gone = [h for h in doc["holds"] if key(h.get("mod")) == key(mod)][0]
        doc["holds"] = keep
        doc.setdefault("lifted", []).append(dict(gone, lifted_said=said) if his else _by_conductor(gone, why))
        return gone
    return _rewrite(p, change)


def _by_conductor(row, why):
    """The mirror's `lifted` row of a Conductor lift: lifted_by CONDUCTOR, its reason and ruling; no lifted_said."""
    return dict(row, lifted_by="CONDUCTOR", lifted_why=why.strip(), per_ruling=CONDUCTOR_LIFT)


def hold(mod, said, date=None):
    """Hold `mod` with his words: the store first (binds at once), then the mirror. -> the store's row. Raises
    ValueError on empty words, MirrorFailed (alarm raised) when the file could not be written."""
    import control as C
    if not (isinstance(said, str) and said.strip()):
        raise ValueError("a hold needs his words")
    if date is not None and not (isinstance(date, str) and date.strip()):
        raise ValueError("a hold's date must be a non-blank date string")
    p = os.environ.get("RM_OWNER_HOLD_FILE") or PATH
    C.import_owner(load_file(p))        # the file's rows the store lacks are learned first, never dropped
    C.hold_owner(key(mod), said, date=date)
    _mirror_or_alarm(p, "hold %s" % key(mod))
    return C.mod_holds()[key(mod)]


def render(doc, rows, lifts):
    """-> the mirror document: the file's other keys kept, `holds` = the store's rows of his hold (the file's order
    first, then the rest by date and name), `lifted` = the file's record plus every store lift not yet in it. Pure."""
    out = dict(doc)
    order = [key(h.get("mod")) for h in doc.get("holds") or [] if isinstance(h, dict)]
    mods = [m for m in dict.fromkeys(order) if m in rows]
    mods += sorted((m for m in rows if m not in mods), key=lambda m: (rows[m].get("date") or "", m))
    holds = []
    for m in mods:
        r = {"mod": m, "date": rows[m].get("date") or "", "said": rows[m].get("said") or ""}
        if rows[m].get("design_allowed"):
            r["design_allowed"] = rows[m]["design_allowed"]
        holds.append(r)
    out["holds"] = holds
    old = {key(h.get("mod")): h for h in doc.get("holds") or [] if isinstance(h, dict)}
    lifted = [x for x in doc.get("lifted") or [] if isinstance(x, dict)]
    have = {(key(x.get("mod")), x.get("date") or "", x.get("said") or "", x.get("lifted_said") or "",
             x.get("lifted_why") if x.get("lifted_by") == "CONDUCTOR" else None) for x in lifted}
    for m, d, w, ls, cw in lifts:
        if (m, d, w, ls, cw) in have:
            continue
        was = old.get(m) if old.get(m, {}).get("said") == w else None
        base = was or {"mod": m, "date": d, "said": w}
        lifted.append(_by_conductor(base, cw) if cw is not None else dict(base, lifted_said=ls))
        have.add((m, d, w, ls, cw))
    if lifted:
        out["lifted"] = lifted
    return out


def _store_rows():
    import control as C
    return {m: r for m, r in C.mod_holds().items() if r.get("store")}, C.owner_lifts()


def mirror(path=None):
    """Rewrite the hold file from the store, under the file's lock: its rows the store lacks are learned first, so a
    mirror never drops a hold. -> the document written. Clears the mirror alarm."""
    import control as C
    p = path or os.environ.get("RM_OWNER_HOLD_FILE") or PATH

    def change(doc):
        C.import_owner(load_file(p))
        rows, lifts = _store_rows()
        new = render(doc, rows, lifts)
        doc.clear()
        doc.update(new)
        return new
    out = _rewrite(p, change)
    if _alarms_on():
        try:
            import refusal_contract as RC
            if any(a.get("subject") == MIRROR_ALARM for a in RC.open_alarms()):
                RC.clear(MIRROR_ALARM, "mod_owner_hold.json written from the store again")
        except Exception as e:      # noqa: BLE001  a stale alarm is said, never fatal to a good mirror
            print("mod_owner_hold: the mirror alarm could not be cleared: %s" % e, file=sys.stderr)
    return out


def _alarms_on():
    """Alarms reach the real alarm store only from the live control store; a test names its own RM_REFUSAL_DIR."""
    import control as C
    return C.is_live() or bool(os.environ.get("RM_REFUSAL_DIR"))


def _mirror_or_alarm(p, what):
    try:
        mirror(p)
    except Exception as e:      # noqa: BLE001  any failure to write the mirror is the alarm, never a silent lift
        why = ("%s is in the control store (binding now), but its mirror %s could not be written: %s: %s. Fix the "
               "cause, then `python3 src/RimMandrake/rimflow/mod_owner_hold.py mirror`" % (what, p, type(e).__name__,
                                                                                          e))
        if _alarms_on():
            try:
                import refusal_contract as RC
                RC.alarm(MIRROR_ALARM, why, family="control")
            except Exception as e2:     # noqa: BLE001
                why += " (and the alarm could not be raised: %s)" % e2
        raise MirrorFailed(why)


def drift(path=None):
    """-> (in_step, lines): does the hold file read exactly as the store would write it? Reads only."""
    p = path or os.environ.get("RM_OWNER_HOLD_FILE") or PATH
    try:
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
        load_file(p)
        rows, lifts = _store_rows()
    except (OSError, ValueError) as e:
        raise Unreadable("%s: %s" % (p, e))
    except Exception as e:      # noqa: BLE001  the store could not be read
        raise Unreadable("the control store: %s" % e)
    want = render(doc, rows, lifts)["holds"]
    have = doc.get("holds") or []
    if want == have:
        return True, ["owner hold mirror: in step (%d hold(s))" % len(want)]
    w, h = {x["mod"]: x for x in want}, {key(x.get("mod")): x for x in have}
    lines = ["owner hold mirror DRIFT (%s): fix with `python3 src/RimMandrake/rimflow/mod_owner_hold.py mirror`" % p]
    lines += ["  the file holds %s; the store does not (it still holds: every reader reads the file too)" % m
              for m in sorted(set(h) - set(w))]
    lines += ["  the store holds %s; the file does not" % m for m in sorted(set(w) - set(h))]
    lines += ["  %s differs between file and store" % m for m in sorted(set(w) & set(h)) if w[m] != h[m]]
    if len(lines) == 1:
        lines.append("  the rows are in another order")
    return False, lines


def design_allowed(h):
    """-> his words allowing a design-only pass on the held mod `h` (a load() row), or None."""
    d = (h or {}).get("design_allowed")
    return d if isinstance(d, dict) and isinstance(d.get("said"), str) and d["said"].strip() else None


def allow_design(mod, said, path=None, date=None):
    """Write his words allowing a design-only pass on the held `mod` onto its hold row. -> the row. Raises KeyError when
    it is not held, ValueError on empty words. The hold itself stays: every build reader is unchanged."""
    import datetime
    if not (isinstance(said, str) and said.strip()):
        raise ValueError("allow-design needs his words")
    if date is not None and not (isinstance(date, str) and date.strip()):
        raise ValueError("allow-design's date must be a non-blank date string")
    p = path or os.environ.get("RM_OWNER_HOLD_FILE") or PATH
    if path is None:        # the store first, then its mirror
        import control as C
        C.import_owner(load_file(p))
        C.allow_design_owner(key(mod), said, date or datetime.date.today().isoformat())
        _mirror_or_alarm(p, "allow-design %s" % key(mod))
        return [h for h in load_file(p).values() if key(h["mod"]) == key(mod)][0]

    def change(doc):
        rows = [h for h in doc["holds"] if key(h.get("mod")) == key(mod)]
        if not rows:
            raise KeyError("%s is not held" % mod)
        rows[0]["design_allowed"] = {"said": said.strip(), "date": date or datetime.date.today().isoformat()}
        return rows[0]
    return _rewrite(p, change)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    lp = sub.add_parser("lift")
    lp.add_argument("mod")
    lp.add_argument("--said", default=None, help="his words lifting it")
    lp.add_argument("--per-ruling", default=None, help="the Conductor's lift: %s" % CONDUCTOR_LIFT)
    lp.add_argument("--why", default=None, help="the Conductor's reason (with --per-ruling)")
    ap_ = sub.add_parser("allow-design")
    ap_.add_argument("mod")
    ap_.add_argument("--said", required=True, help="his words allowing a design-only pass")
    ap_.add_argument("--date", default=None, help="the day he said it (default today)")
    hp = sub.add_parser("hold")
    hp.add_argument("mod")
    hp.add_argument("--said", required=True, help="his words holding it")
    hp.add_argument("--date", default=None, help="the day he said it (default today)")
    sub.add_parser("mirror")
    o = ap.parse_args(argv)
    import control as C
    try:
        return _run(o)
    except MirrorFailed as e:
        print("ALARM %s: %s" % (MIRROR_ALARM, e), file=sys.stderr)
        return MIRROR_FAILED
    except (Unreadable, C.Unreadable) as e:     # could not look: nothing was decided, the cause is named
        print("COULD NOT LOOK: %s (nothing changed; pipe doctor names the fix)" % e, file=sys.stderr)
        return 3


def _run(o):
    import control as C
    pub = 'publish it: ./publish -m "owner hold: %s %s" src/RimMandrake/rimflow/mod_owner_hold.json'
    if o.cmd == "mirror":
        doc = mirror()
        print("mod_owner_hold.json written from the store (%d hold(s)); %s" % (len(doc["holds"]), pub % ("mirror",
                                                                                                         "store")))
        return 0
    if o.cmd == "hold":
        try:
            hold(o.mod, o.said, date=o.date)
        except (ValueError, C.Refused) as e:
            print(str(e), file=sys.stderr)
            return 1
        print("held %s; %s" % (key(o.mod), pub % ("hold", key(o.mod))))
        return 0
    if o.cmd == "show":
        hs = load()
        if not hs:
            print("no mod is held by the owner")
        for m, h in sorted(hs.items()):
            d = design_allowed(h)
            print("%-18s %s%s" % (m, status(h), "; design pass allowed %s: \"%s\"" % (d["date"], d["said"]) if d else ""))
        return 0
    if o.cmd == "allow-design":
        try:
            allow_design(o.mod, o.said, date=o.date)
        except (KeyError, ValueError, C.Refused) as e:
            print(str(e), file=sys.stderr)
            return 1
        print("design pass allowed on held %s; publish it: ./publish -m \"owner hold: allow design %s\" "
              "src/RimMandrake/rimflow/mod_owner_hold.json" % (key(o.mod), key(o.mod)))
        return 0
    try:
        lift(o.mod, o.said, per_ruling=o.per_ruling, why=o.why)
    except (KeyError, ValueError, RuntimeError, C.Refused) as e:
        print(str(e).strip("'\""), file=sys.stderr)
        return 1
    if o.said:
        print("lifted %s; publish it: ./publish -m \"owner hold: lift %s\" src/RimMandrake/rimflow/mod_owner_hold.json"
              % (key(o.mod), key(o.mod)))
    else:
        print("the Conductor lifted %s (his digest shows it); publish it: ./publish -m \"owner hold: Conductor lifts %s\" "
              "src/RimMandrake/rimflow/mod_owner_hold.json infrastructure/state/ledger/events/BENCH.jsonl; it still runs "
              "only when its readiness list reads READY" % (key(o.mod), key(o.mod)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
