#!/usr/bin/env python3
"""conductor_acts.py — who may do an act that once needed the owner (owner 2026-11-19).

Owner, Thu 2026-11-19 ~7:40 AM PST: "I only want to preserve Flyer flights, replacing art I kept, pass at my walk,
spending money, public publishing. Everything else the Conductor should mindfully be able to do. Of course question
cards for me should get to me, but the Conductor should review them to ensure it can't just do them now and alert me
later." Full text: design/RimMandrake/standing_rulings.md §Only five acts stay his. Page:
design/specs/2026-11-19-conductor-acts/boundary.md. Item RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS.

The five KEPT acts are refused to everyone but him. Every other act a gate kept for him is open to the Conductor window
(seat BENCH, no RM_ROLE_UNIT: never a launched helper, role run, other seat or the tick), recorded as the Conductor's
act: `--per-ruling RULING --why "<the act and the reason>"`, the why tagged `delegated: conductor act: …` so the daily
digest (delegated_digest.py) lists it. Four MINDFUL acts also name what is lost if wrong and the undo:
`lost: <…>` and `undo: <…>` in the why.

  python3 src/RimMandrake/rimflow/conductor_acts.py check "<act>" --why "<why>"   exit 0 allowed, 1 refused (reason)
  python3 src/RimMandrake/rimflow/conductor_acts.py kept                          the five, one per line
Selftest: selftest_conductor_acts.py.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
CLI = os.path.join(HERE, "cli.py")

RULING = "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS"
HIS_WORDS = ("I only want to preserve Flyer flights, replacing art I kept, pass at my walk, spending money, public "
             "publishing. Everything else the Conductor should mindfully be able to do.")
KEPT = {
    "flyer flight": "a live flight test of a flyer",
    "kept art": "replacing art he kept, or releasing a keep mark",
    "walk pass": "the pass at his walk, and his judgement of gameplay, fun, theme and UI",
    "spending money": "spending money or a purchase",
    "public publishing": "publishing outside the private repos",
}
MINDFUL = {
    "owner bridge hold": "cutting his OWNER bridge hold inside 45 minutes",
    "account order": "changing the account order or the shared account's leave line",
    "work not ours": "deleting or overwriting work that is not ours",
    "loosen a bar": "loosening or removing a bar",
}
WHY_PREFIX = "delegated: conductor act: "
MIN_WORDS = 4
PART_WORDS = 3
# Self-declared and fail-safe, as the bridge's flight pattern is: a why that names a mindful act owes lost/undo.
_MINDFUL_RE = re.compile(r"\bbridge hold\b|\bhis OWNER hold\b|\baccount order\b|\bleave line\b|\bpriority order\b|"
                         r"\breset --hard\b|\boverwrit|\bdelet\w* (?:\w+ ){0,3}not ours\b|\bnot ours\b|"
                         r"\bloosen|\bremov\w* (?:a |the )?(?:locked )?bars?\b|\brelax\w* (?:a |the )?(?:threshold|bar)",
                         re.I)


def conductor_window(env=None):
    """-> (ok, why): the one definition lives in mod_owner_hold (the sibling hold-lift run's)."""
    import mod_owner_hold
    return mod_owner_hold.conductor_window(env)


def _words(text):
    return [w for w in re.split(r"\s+", str(text or "").strip()) if re.search(r"\w", w)]


def _bare(why):
    """The caller's own words, without our tag."""
    s = str(why or "").strip()
    while s.lower().startswith(WHY_PREFIX.strip().lower()):
        s = s[len(WHY_PREFIX.strip()):].strip()
    return s


def _part(why, label):
    """-> the words after `label:` up to the next `;` or label, else []."""
    m = re.search(r"\b%s:\s*(.*?)(?=;|\b(?:lost|undo):|$)" % label, why, re.I | re.S)
    return _words(m.group(1)) if m else []


def why_problem(why, mindful=False):
    """-> None when the why will do, else what is wrong with it."""
    bare = _bare(why)
    n = len(_words(bare))
    if n < MIN_WORDS:
        return ("the --why has %d word(s); a Conductor act states the act and its reason (at least %d words)"
                % (n, MIN_WORDS))
    if mindful:
        lost, undo = _part(bare, "lost"), _part(bare, "undo")
        if len(lost) < PART_WORDS or len(undo) < PART_WORDS:
            return ("a mindful act names what is lost if it is wrong and how it is undone: put `lost: <at least %d "
                    "words>` and `undo: <at least %d words>` in the --why (owner 2026-11-19: \"mindfully\")"
                    % (PART_WORDS, PART_WORDS))
    return None


def kept_refusal(act):
    """-> the refusal text when act is one of his five, else None."""
    a = str(act or "").strip().lower()
    if a in KEPT:
        return ("refused: %s stays his (owner 2026-11-19: \"%s\"); no Conductor act, --why or --per-ruling does it"
                % (KEPT[a], HIS_WORDS.split(".")[0]))
    return None


def names_mindful(why):
    return bool(_MINDFUL_RE.search(_bare(why)))


def check(act, why, env=None):
    """The gate for one act: -> (ok, text). Kept acts refuse for everyone; the rest only from the Conductor window, with
    a why that states the act and reason, and lost/undo for a mindful act."""
    k = kept_refusal(act)
    if k:
        return False, k
    ok, txt = conductor_window(env)
    if not ok:
        return False, "refused: only the Conductor window does this act under %s (%s)" % (RULING, txt)
    p = why_problem(why, mindful=str(act or "").strip().lower() in MINDFUL or names_mindful(why))
    if p:
        return False, "refused: " + p
    return True, "the Conductor's act per %s" % RULING


def cli_gate(why, env=None):
    """rimflow's check of `--per-ruling RULING` on any verb (the act is not named there): -> (ok, text)."""
    ok, txt = conductor_window(env)
    if not ok:
        return False, ("refused: --per-ruling %s is the Conductor window's alone (%s); a helper relays the Conductor's "
                       "instruction under its own seat with --why" % (RULING, txt))
    p = why_problem(why, mindful=names_mindful(why))
    if p:
        return False, "refused: " + p
    return True, "ok"


def tagged(why, act=None):
    """-> the why as the ledger stores it: `delegated: conductor act: [<act>: ]<why>` (idempotent)."""
    bare = _bare(why)
    return WHY_PREFIX + ("%s: " % act if act and not bare.lower().startswith(str(act).lower()) else "") + bare


def is_conductor_event(ev, act=None):
    """-> (ok, text): is this recorded event the Conductor's act under this ruling (and, for act, may it do that act)?"""
    if not isinstance(ev, dict):
        return False, "no event"
    if act:
        k = kept_refusal(act)
        if k:
            return False, k
    if str(ev.get("perRuling") or "") != RULING:
        return False, "the event does not cite %s" % RULING
    if ev.get("ownerSaid") or ev.get("byCard"):
        return False, "the event carries his words; a Conductor act carries the ruling"
    if str(ev.get("role_unit") or "").strip():
        return False, "the event was written by a launched run (%s), not the Conductor window" % ev["role_unit"]
    hands = str(ev.get("ranBy") or "").strip().upper()
    if hands not in ("BENCH", "CONDUCTOR"):
        return False, "the event's hands are %s, not the Conductor window's" % (hands or "unrecorded")
    why = str(ev.get("why") or "")
    if not why.startswith(WHY_PREFIX):
        return False, "the event's why is not tagged %r" % WHY_PREFIX.strip()
    p = why_problem(why, mindful=str(act or "").strip().lower() in MINDFUL)
    if p:
        return False, p
    return True, "the Conductor's act %s: %s" % (ev.get("tsn") or "", _bare(why)[:80])


def lock_problem(v, events):
    """A Design Version lock by the Conductor (VERSION.json locked_by "conductor"): None when it is the Conductor's act,
    else why not. v: VERSION.json; events: {tsn: event} of the OWNER shard (concept_tree.owner_events). The lock names
    its ledger event in conductor_event (OWNER:<tsn>), so it is a digest line; per_ruling names this ruling."""
    if not isinstance(v, dict) or str(v.get("locked_by") or "") != "conductor":
        return "the lock is not the Conductor's"
    if str(v.get("per_ruling") or "") != RULING:
        return "the Conductor's lock does not cite %s in per_ruling" % RULING
    m = re.fullmatch(r"OWNER:([0-9]+)", str(v.get("conductor_event") or ""))
    if not m:
        return "the Conductor's lock names no conductor_event OWNER:<tsn> (its ledger record)"
    ok, why = is_conductor_event((events or {}).get(m.group(1)), act="design version lock")
    return None if ok else "conductor_event %s: %s" % (v.get("conductor_event"), why)


def digest_note(item, act, text, why, run=None, env=None):
    """Write the Conductor's act on the ledger (a note on item under RULING, tagged why), so his daily digest lists it.
    For a gate that writes no ledger event of its own. Raises RuntimeError when it is not written."""
    run = run or subprocess.run
    r = run([sys.executable, CLI, "note", item, "--per-ruling", RULING, "--text", text, "--why", tagged(why, act)],
            capture_output=True, text=True, timeout=300, env=env)  # budget: class=rimflow
    if r.returncode != 0:
        raise RuntimeError("the Conductor's act was not recorded (rimflow note exit %d: %s)"
                           % (r.returncode, (r.stderr or r.stdout or "").strip()[-300:]))  # cut-ok: exception message
    return True


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("act")
    c.add_argument("--why", required=True)
    sub.add_parser("kept")
    a = ap.parse_args(argv)
    if a.cmd == "kept":
        for k, v in KEPT.items():
            print("%-18s %s" % (k, v))
        return 0
    ok, txt = check(a.act, a.why)
    print(txt)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
