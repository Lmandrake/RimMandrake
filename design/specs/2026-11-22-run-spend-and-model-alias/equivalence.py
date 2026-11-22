#!/usr/bin/env python3
"""Equivalence run: the OLD readers of a run's spend unit and of a model alias against the ONE home in role_launch.

Usage: python3 design/specs/2026-11-22-run-spend-and-model-alias/equivalence.py [--recorded]
  The fixture cases always run. --recorded also reads the real stores on this machine:
  - the detached run records (D:\\ClaudeWork\\rimmandrake\\dispatcher\\detached\\*.json),
  - the role runs in the dispatcher state (state.json),
  - every committed version/run_spend.jsonl line and version/stage_record.json spend row.
It prints one line per comparison class and a final verdict line. Exit 0: every difference is classed; 1: an
unclassed difference; 2: could not look (a store unreadable).

The OLD functions are frozen copies of the code at the base commit 7580e09e4f (role_launch.run_spend and tokens_v2,
maturation.row_unit, _unit_by_time and V2_SWITCH, detached_helper.model_tier and MODEL_IDS, mod_model.pin_id,
maturation_autonomy.pilot_run_model's reverse map). They are oracles here and nowhere else.
"""
import datetime as dt
import glob
import json
import math
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "src", "RimMandrake", "rimflow"), os.path.join(ROOT, "src", "RimMandrake", "Utils")]
import role_launch as RL  # noqa: E402
import maturation as M  # noqa: E402
import mod_model as MM  # noqa: E402

DETACHED = "/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached"
STATE = "/mnt/d/ClaudeWork/rimmandrake/dispatcher/state.json"

# ---- OLD, frozen ------------------------------------------------------------------------------------------------------
OLD_V2_SWITCH = dt.datetime(2026, 11, 16, 23, 5, tzinfo=dt.timezone(dt.timedelta(hours=-8))).timestamp()


def old_unit_by_time(t):
    return "unstated" if not isinstance(t, (int, float)) else "weighted_v1" if t < OLD_V2_SWITCH else "weighted_v2"


def old_row_unit(row):
    u = row.get("token_unit")
    if isinstance(u, str) and u.strip():
        return u
    if row.get("at") is None:
        return "weighted_v1"
    t = M._instant(row.get("at"))
    return old_unit_by_time(t) if t is not None else "unstated"


def old_spend_row_unit(view):
    """The unit the OLD _spend_row stamped: the view carried no token_unit, so always by time."""
    when = view.get("end") if isinstance(view.get("end"), (int, float)) else view.get("at")
    own = view.get("token_unit") if isinstance(view.get("token_unit"), str) and view.get("token_unit") else None
    return own or old_unit_by_time(when)


def old_tokens_v2(rec):
    t = rec.get("tokens") if isinstance(rec, dict) else None
    unit = rec.get("token_unit") if isinstance(rec, dict) else None
    if unit == RL.TOKEN_UNIT:
        return (None if t is None else int(t)), ("v2" if t is not None else "unmeasured")
    mu = rec.get("model_usage") if isinstance(rec, dict) else None
    if isinstance(mu, dict) and mu:
        tot = RL._model_usage_tokens(mu)
        if tot is not None:
            return int(math.ceil(tot)), "v1_usage"
    if t is None:
        return None, "unmeasured"
    return int(math.ceil(int(t) * RL.model_weights(rec.get("model"))["input_tokens"])), "v1_bound"


def old_run_spend(r):
    if r.get("tokens") is None:
        return r.get("budget", 0)
    if r.get("token_unit") in (None, RL.TOKEN_UNIT):
        return r["tokens"]
    try:
        t, _b = old_tokens_v2(dict(r, model=r.get("model_id") or r.get("model")))
    except RL.UnknownModel:
        return r["tokens"]
    return r["tokens"] if t is None else t


OLD_MODELS = ("fable", "opus", "sonnet")
OLD_MODEL_IDS = {"fable": "claude-fable-5-2"}


def old_model_tier(model):
    if not isinstance(model, str):
        return model
    low = model.strip().lower()
    hits = [t for t in OLD_MODELS if t in low]
    return hits[0] if len(hits) == 1 else model


def old_launch(model):
    t = old_model_tier(model)
    return OLD_MODEL_IDS.get(t, t)


def old_pin_id(alias):
    if alias not in OLD_MODEL_IDS:
        raise RL.UnknownModel("not pinnable")
    return RL.resolve_model(OLD_MODEL_IDS[alias])


def old_pilot_tier(mid):
    return {v: k for k, v in OLD_MODEL_IDS.items()}.get(mid, mid)


# ---- comparison -------------------------------------------------------------------------------------------------------
def ans(f, *a):
    try:
        return f(*a)
    except RL.UnknownModel as e:
        return "UnknownModel(%s)" % str(e)[:60]


class Tally:
    def __init__(self):
        self.rows = {}

    def add(self, cls, same, why=None):
        k = (cls, "same" if same else "DIFF: " + (why or "UNCLASSED"))
        self.rows[k] = self.rows.get(k, 0) + 1

    def unclassed(self):
        return sum(n for (c, v), n in self.rows.items() if v.endswith("UNCLASSED"))

    def show(self):
        for (c, v), n in sorted(self.rows.items()):
            print("  %-34s %-90s %6d" % (c, v[:90], n))


def fixtures(T):
    fable_v1 = {"tokens": 1000, "model": "claude-fable-5-2", "at": "2026-11-15T10:00:00Z"}
    a, b = old_run_spend(dict(fable_v1)), RL.run_spend(dict(fable_v1))
    T.add("fixture: unstamped Fable run_spend", a == b,
          "old was wrong: old run_spend %s counted an unstamped (weighted_v1) Fable figure as v2; new %s = tokens_v2" % (a, b))
    unk = {"tokens": 10, "token_unit": "weighted_v1", "model": "claude-nonesuch-9-9", "budget": 777}
    a, b = old_run_spend(dict(unk)), RL.run_spend(dict(unk))
    T.add("fixture: unknown model run_spend", a == b,
          "old was wrong: old %s took a figure it could not weigh as it stood; new %s counts its budget" % (a, b))
    for m in ("claude-fable-5-2", "Opus", "us.anthropic.claude-opus-5-5-v1:0", "claude-haiku-5-5", "haiku", "x", None,
              "fable-opus"):
        T.add("fixture: tier", old_model_tier(m) == RL.tier(m))


def recorded(T):
    try:
        st = json.load(open(STATE))
    except (OSError, ValueError) as e:
        print("could not look: %s: %s" % (STATE, e))
        return 2
    if not os.path.isdir(DETACHED):
        print("could not look: %s is not a folder" % DETACHED)
        return 2
    recs, bad = [], 0
    for f in glob.glob(os.path.join(DETACHED, "*.json")):
        try:
            r = json.load(open(f))
        except (OSError, ValueError):
            bad += 1
            continue
        if isinstance(r, dict) and r.get("unit") and r.get("item"):
            recs.append(r)
    by_unit = {r["unit"]: r for r in recs}
    import maturation_now as MN
    for r in recs:
        a, b = ans(old_run_spend, dict(r)), ans(RL.run_spend, dict(r))
        why = None
        if a != b and not r.get("token_unit") and isinstance(r.get("tokens"), int):
            try:
                RL.tokens_v2(dict(r))
                why = ("old was wrong: an unstamped (weighted_v1) %s figure taken as v2; new converts it "
                       "(tokens_v2)" % RL.tier(r.get("model")))
            except RL.UnknownModel:
                why = ("old was wrong: an unstamped (weighted_v1) %s figure taken as v2; its alias names no variable "
                       "here, so new counts it UNMEASURED (its budget)" % RL.tier(r.get("model")))
        T.add("detached record: run_spend", a == b, why)
        a, b = ans(old_tokens_v2, dict(r)), ans(RL.tokens_v2, dict(r))
        T.add("detached record: tokens_v2", a == b)
        if r.get("status") == "finished":
            view = MN.run_view(r, r.get("ended") or 0, spend=lambda rec: (None, None, None))
            a, b = old_spend_row_unit(view), M._spend_row(view, ["designer"])["token_unit"]
            T.add("detached record: run row unit", a == b)
        t = r.get("model")
        T.add("detached record: tier", old_model_tier(t) == RL.tier(t))
        a, b = ans(old_launch, t), ans(RL.launch_model, t)
        T.add("detached record: --model argument", a == b)
    runs = [x for rs in (st.get("roles") or {}).values() for x in (rs.get("runs") or [])]
    for r in runs:
        T.add("role run: run_spend", ans(old_run_spend, dict(r)) == ans(RL.run_spend, dict(r)))
    files = subprocess.run(["git", "-C", ROOT, "ls-files", "*version/run_spend.jsonl", "*version/stage_record.json"],
                           capture_output=True, text=True).stdout.split()
    nrows = 0
    for f in files:
        p = os.path.join(ROOT, f)
        if f.endswith(".jsonl"):
            rows = [json.loads(x) for x in open(p) if x.strip()]
        else:
            rows = json.load(open(p)).get("spend") or []
        for x in rows:
            nrows += 1
            a, b = old_row_unit(x), M.row_unit(x)
            why = None
            if a != b:
                d = by_unit.get(x.get("unit"))
                why = ("old was wrong" if d is not None and RL.stored_unit(d) == b else "UNCLASSED")
            T.add("committed row: unit", a == b, why)
            run = by_unit.get(x.get("unit"))
            if run is not None and not x.get("kind") == "estimate":
                T.add("committed row: unit = its run record's", M.row_unit(x) == RL.stored_unit(run),
                      "row stamp differs from its run record")
    for alias in ("fable", "opus", "sonnet", "haiku"):
        a, b = ans(old_pin_id, alias), ans(MM.pin_id, alias)
        if str(a).startswith("UnknownModel") and str(b).startswith("UnknownModel"):
            a = b = "refused"
        why = None
        if a != b and alias in ("opus", "sonnet"):
            why = "new: %s is pinnable; its id is read from its variable (%s)" % (alias, b)
        T.add("pin_id(%s)" % alias, a == b, why)
    print("inputs: %d detached records (%d json files did not parse: not records), %d role runs, %d committed rows "
          "in %d files" % (len(recs), bad, len(runs), nrows, len(files)))
    return 0


def main(argv):
    T = Tally()
    fixtures(T)
    rc = recorded(T) if "--recorded" in argv else 0
    T.show()
    if rc:
        print("EQUIVALENCE UNMEASURED: a store could not be read")
        return rc
    n = T.unclassed()
    print("EQUIVALENCE %s: %d unclassed difference(s)" % ("OK" if n == 0 else "FAIL", n))
    return 0 if n == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
