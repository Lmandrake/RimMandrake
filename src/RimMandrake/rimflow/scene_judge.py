#!/usr/bin/env python3
"""Judge a kept scene_trace_v1 and its receipts. The game has no part in this command."""
import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

UTILS = Path(__file__).resolve().parents[1] / "Utils"
if str(UTILS) not in sys.path:
    sys.path.insert(0, str(UTILS))

import conds as C
from live_kinds import APPARATUS, ENVIRONMENT, MOD_FAILURE, NO_LOOK, OUTCOMES, RANDOM_MISS, SUCCESS, UNRESOLVED
from scene_cond import probe_name
from scene_core import Receipt, Refused
from scene_hands import trace_fault

ROLES = ("forbidden", "opportunity", "exposure", "success", "cast_activity")
PLAN_KEYS = set(ROLES) | {"request", "claim", "version", "kind", "allowed_miss", "external"}
TAP_PROBES = {"count", "seq", "before", "after"}
EXIT = {word: code for code, word in enumerate(OUTCOMES)}
VERSION = "1"


class NoReading(Exception):
    def __init__(self, why, failure=None, missing=False):
        super().__init__(why)
        self.failure, self.missing = failure, missing


def names(value):
    return isinstance(value, list) and all(isinstance(n, str) and n for n in value)


def plan_check(plan):
    if not isinstance(plan, dict):
        raise Refused("BAD_PLAN", "contract.json must hold an object")
    extra = plan.keys() - PLAN_KEYS
    if extra:
        raise Refused("BAD_PLAN", "unknown key " + sorted(extra)[0])
    if "success" not in plan:
        raise Refused("BAD_PLAN", "declare success")
    if plan.get("kind", "A") not in ("A", "B"):
        raise Refused("BAD_PLAN", "kind must be A or B")
    if type(plan.get("allowed_miss", False)) is not bool or (plan.get("allowed_miss") and plan.get("kind") != "B"):
        raise Refused("BAD_PLAN", "allowed_miss must be a boolean and only B may allow it")
    if not names(plan.get("external", [])):
        raise Refused("BAD_PLAN", "external must list tap names")
    for key in ("claim", "version", "request"):
        if key in plan and (not isinstance(plan[key], str) or not plan[key]):
            raise Refused("BAD_PLAN", key + " must be nonempty text")


def track_name(name):
    """The kept library strips thing: and renames canonical probes on track rows, but not in open."""
    if name.startswith("{"):
        try:
            return probe_name(C.parse_json(name))
        except (ValueError, KeyError, TypeError):
            pass
    return name.removeprefix("thing:")


def observation(why, tick=None, observed=None):
    return {"condition": why, "tick": tick, "observed": observed}


class Trace:
    def __init__(self, rows):
        if any(not isinstance(r, dict) or type(r.get("n")) is not int for r in rows):
            raise NoReading("a trace row has no integer n")
        problem = trace_fault(rows)
        if problem:
            raise NoReading(problem)
        self.open, self.close = rows[0], rows[-1]
        self.end = next(r for r in rows if r["rec"] == "end")
        if self.open.get("rec") != "open" or self.open.get("schema") != "scene_trace_v1":
            raise NoReading("no scene_trace_v1 opening record")
        run = self.open.get("run")
        if not run or any(r.get("run") != run for r in rows):
            raise NoReading("rows refer to different runs")
        if any(type(r.get(k)) is not int for r in rows for k in ("seq", "tick")):
            raise NoReading("a row has no integer seq or tick")
        if any(a["seq"] >= b["seq"] or a["tick"] > b["tick"] for a, b in zip(rows, rows[1:])):
            raise NoReading("row sequence or tick went back")
        self.start, self.stop = self.open["tick"], self.end["tick"]
        if self.stop - self.start != self.end.get("executed") or self.stop - self.start > C.HARD_MAX_TICKS:
            raise NoReading("the executed tick span differs from the trace or exceeds the run limit")
        if self.close.get("paused") is not True or self.close.get("phase") != "last" or self.open.get("phase") != "first":
            raise NoReading("the first or paused closing phase could not be established")
        if self.close["tick"] != self.stop or self.close.get("tickAfter") != self.stop:
            raise NoReading("the last sample does not stand on the end tick")
        if not names(self.open.get("tracks")) or not names(self.open.get("taps", [])):
            raise NoReading("the opening list of tracks or taps could not be read")
        self.tracks = {track_name(n) for n in self.open["tracks"]}
        if len(self.tracks) != len(self.open["tracks"]):
            raise NoReading("track names in open are ambiguous")
        compiled = self.open.get("cond")
        sample = compiled.get("sample") if isinstance(compiled, dict) else None
        probes = sample.get("probes") if isinstance(sample, dict) else None
        self.sample_probes = {
            track_name(n): track_name(probe_name(p)) for n, p in probes.items()
            if track_name(n) in self.tracks and isinstance(p, dict) and isinstance(p.get("p"), str)
        } if isinstance(probes, dict) else {}
        self.taps = set(self.open.get("taps", []))
        self.first, self.last, self.changes, self.events = {}, {}, {}, {}
        self.acts, self.faults, aliases, tap_seq = {}, [], {}, {}
        for r in rows[1:-1]:
            phase, tick, rec = r.get("phase"), r["tick"], r.get("rec")
            if phase not in ("first", "end_of_tick", "last") or (
                phase == "first" and tick != self.start or phase == "last" and (tick != self.stop or r["seq"] <= self.end["seq"])
            ):
                raise NoReading("invalid phase on tick %s" % tick)
            if rec not in ("track", "tap", "link", "act", "fault") or r.get("source") == "mod_says":
                continue
            self.check_alias(r, aliases)
            if rec == "track":
                n = r.get("name")
                if not isinstance(n, str) or r.get("st") not in C.STATUSES or "v" not in r:
                    raise NoReading("track %s has no valid sample on tick %s" % (n, tick))
                n = track_name(n)
                if (phase != "last" and (tick in self.acts or r["seq"] >= self.end["seq"])) or (
                        phase == "end_of_tick" and tick <= self.start):
                    raise NoReading("track %s was sampled after an act or outside a tick" % n)
                target = self.first if phase == "first" else self.last if phase == "last" else self.changes.setdefault(tick, {})
                if n in target or n not in self.tracks:
                    raise NoReading("duplicate or undeclared sample: " + n)
                target[n] = r
            elif rec == "tap":
                entry, leave, parent = (r.get(k) for k in ("enterSeq", "exitSeq", "parentSeq"))
                name = r.get("name")
                if (not isinstance(name, str) or name not in self.taps or
                        type(entry) is not int or type(leave) is not int or not 0 <= entry < leave or
                        entry in tap_seq or leave in tap_seq or not isinstance(r.get("data"), dict) or
                        "parentSeq" not in r or parent is not None and (type(parent) is not int or not 0 <= parent < entry)):
                    raise NoReading("tap %s has no valid entry/exit record" % r.get("name"))
                tap_seq[entry], tap_seq[leave] = leave, None
                self.events.setdefault(tick, []).append(r)
            elif rec == "act":
                self.acts.setdefault(tick, []).append(r)
                if tick >= self.stop:
                    raise NoReading("act %s has no following sample" % r.get("name"))
            elif rec == "fault":
                self.faults.append(r)
        for phase, samples in (("first", self.first), ("last", self.last)):
            missing = self.tracks - samples.keys()
            if missing:
                raise NoReading("missing %s sample: %s" % (phase, ", ".join(sorted(missing))))
        for events in self.events.values():
            for r in events:
                parent = r["parentSeq"]
                if parent in tap_seq and (tap_seq[parent] is None or tap_seq[parent] <= r["exitSeq"]):
                    raise NoReading("tap %s exits outside its parent call" % r["name"])

    def sample_track(self, probe):
        if probe in self.tracks and self.sample_probes.get(probe, probe) == probe:
            return probe
        return next((name for name, recorded in self.sample_probes.items() if recorded == probe), None)

    @staticmethod
    def check_alias(row, aliases):
        if "alias" not in row and row["rec"] != "link":
            return
        alias = row.get("alias")
        if not isinstance(alias, str) or not alias:
            raise NoReading("an alias link does not name its alias")
        if row["rec"] == "link":
            old, new = row.get("old"), row.get("new")
            if not old or not new or aliases.get(alias) != old:
                raise NoReading("alias %s has an unproved link" % alias)
            aliases[alias] = new
        elif not row.get("object") or aliases.setdefault(alias, row["object"]) != row["object"]:
            raise NoReading("alias %s changed object without a link" % alias)

    def frames(self):
        values, events = dict(self.first), {}
        yield self.start, values, events
        for tick in range(self.start, self.stop + 1):
            values.update(self.changes.get(tick, {}))
            new_events = self.events.get(tick, ())
            for r in new_events:
                events.setdefault(r["name"], []).append(r)
            if tick != self.start or new_events:
                yield tick, values, events
        if any(r["st"] != values[n]["st"] or not C.same_value(r["v"], values[n]["v"]) for n, r in self.last.items()):
            yield self.stop, self.last, events


class TraceCompiler(C.Compiler):
    def __init__(self, trace):
        super().__init__(self, "eval")
        self.trace = trace

    def current_map(self):
        compiled = self.trace.open.get("cond")
        return compiled.get("mapId", 0) if isinstance(compiled, dict) else 0

    def map_size(self, _map_id):
        # The value is already reduced and recorded by the hand. No map is reconstructed.
        return (2**31, 2**31)

    def refuse(self, _key):
        return None

    def probe(self, raw, at, counts):
        raw = self.obj(raw, at)
        kind = raw.get("p")
        if isinstance(kind, str) and (kind == "track" or kind in TAP_PROBES):
            p = super().probe({"p": "game.tick"}, at, counts)
            p.name, p.canonical = kind, raw
            if kind == "track":
                self.keys(raw, ("p", "name"), at)
                if not isinstance(raw.get("name"), str):
                    raise C.Refused("bad_arg", at, "track needs a name")
                p.ptype = "any"
            else:
                self.keys(raw, ("p", "taps", "where") if kind == "count" else ("p", "taps"), at)
                taps = raw.get("taps")
                allowed = names(taps) and (len(taps) >= 2 if kind == "seq" else len(taps) == (1 if kind == "count" else 2))
                if not allowed or not isinstance(raw.get("where", {}), dict):
                    raise C.Refused("bad_arg", at, kind + " needs named taps and count takes an object filter")
                p.ptype = "num" if kind == "count" else "bool"
                for name in taps:
                    self.require_tap(name)
                return p
        else:
            p = super().probe(raw, at, counts)
            if kind == "game.tick":
                return p
        name = track_name(raw["name"] if kind == "track" else probe_name(raw))
        candidates = [name] if kind == "track" else [name, track_name(probe_name(p.canonical))]
        if kind == "value.state":
            candidates.append(name.removesuffix("#state"))
        for n in candidates:
            if kind == "track":
                label = n if n in self.trace.tracks else None
            else:
                label = self.trace.sample_track(n)
            if label is not None:
                p.recorded_track = label
                p.read_status = kind == "value.state" and not n.endswith("#state")
                return p
        raise NoReading("unrecorded track " + name, missing=True)

    def require_tap(self, name):
        if name not in self.trace.taps:
            raise NoReading("unrecorded tap " + name, missing=True)

class TraceEval(C.Evaluator):
    def read_probe(self, p):
        kind = p.name
        if kind == "game.tick":
            return self.tick, "ok", ""
        if kind in TAP_PROBES:
            groups = [self.events.get(n, ()) for n in p.canonical["taps"]]
            if kind == "count":
                where = p.canonical.get("where", {})
                v = sum(all(k in r["data"] and C.same_value(r["data"][k], val) for k, val in where.items()) for r in groups[0])
            elif kind == "seq":
                prev = -1
                for group in groups:
                    prev = min((r["enterSeq"] for r in group if r["enterSeq"] > prev), default=None)
                    if prev is None:
                        break
                v = prev is not None
            else:
                first = [min((r["enterSeq"] for r in g), default=None) for g in groups]
                v = None not in first and (first[0] < first[1] if kind == "before" else first[0] > first[1])
            return v, "ok", ""
        name = p.recorded_track
        row = self.values[name]
        st, v = row["st"], row["v"]
        if p.read_status:
            return ("null" if st == "ok" and v is None else st), "ok", ""
        return (v if st == "ok" else None), st, row.get("detail", "")


def readings(plan, trace):
    trees = {}
    for role in ROLES:
        if role not in plan:
            continue
        c = TraceCompiler(trace)
        try:
            compiled = c.compile_spec({"tree": plan[role]})
        except C.Refused as e:
            raise Refused("BAD_CONDITION", "%s %s: %s" % (role, e.at, e.detail)) from e
        trees[role] = compiled.tree, TraceEval(c)
    for name in plan.get("external", []):
        TraceCompiler(trace).require_tap(name)
    first, hits, misses, final, unread = {}, {}, {}, {}, {}
    for i, (tick, values, events) in enumerate(trace.frames()):
        for role, (tree, ev) in trees.items():
            if role in unread:
                continue
            ev.tick, ev.values, ev.events = tick, values, events
            value, _, _, records = ev.evaluate(tree, tick)
            seen = observation(role, tick, records)
            if value is None or any(r["status"] == "ignored" for r in records):
                unread[role] = seen         # a forbidden effect still decides the run (MOD FAILURE in any run)
                continue
            final[role] = seen
            if i == 0:
                first[role] = value
            if value and (i or role != "exposure"):
                hits.setdefault(role, seen)
            elif not value:
                misses.setdefault(role, seen)
    if unread and "forbidden" not in hits:
        role, seen = next(iter(unread.items()))
        raise NoReading("unreadable condition " + role, seen)
    return first, hits, misses, final


def apparatus(trace):
    if trace.faults:
        r = trace.faults[0]
        return observation(r.get("what", "fault"), r["tick"], r.get("detail"))
    expected = trace.open.get("acts")
    left = trace.close.get("actsNotDone")
    if not isinstance(expected, list) or not names(left):
        raise NoReading("the call did not record which acts ran")
    done = {}
    for tick, acts in trace.acts.items():
        for act in acts:
            if not isinstance(act.get("name"), str) or type(act.get("ok")) is not bool or act["name"] in done:
                raise NoReading("invalid act record on tick " + str(tick))
            done[act["name"]] = tick - trace.start
            if not act["ok"] and act.get("delivery") != "giver_refused":
                return observation(act["name"], tick, act.get("detail"))
    for act in expected:
        if not isinstance(act, dict) or not isinstance(act.get("name"), str) or type(act.get("at")) is not int:
            raise NoReading("invalid act in the opening call")
        if done.get(act["name"]) != act["at"]:
            return observation(act["name"], trace.start + act["at"], "act was not delivered on the requested tick")
    if left:
        return observation("acts not done", trace.stop, left)
    if trace.end.get("state") == "aborted" and isinstance(trace.end.get("why"), str) and trace.end["why"].startswith("act '"):
        return observation("act at start", trace.stop, trace.end["why"])
    return None


def spoiled_by(plan, trace, miss, cast_activity):
    if "cast_activity" not in plan:
        return None
    act_tick = min(trace.acts, default=trace.start)
    for tick, events in trace.events.items():
        if tick > miss["tick"] or cast_activity and cast_activity["tick"] <= tick:
            continue
        for r in events:
            if r["name"] in plan.get("external", []) and (
                    tick < act_tick or tick == miss["tick"] and r["data"].get("entered_station") is True):
                return r
    return None


@dataclass
class Verdict:
    outcome: str
    row: int
    first_failed: dict
    evidence: dict
    counts_for_bar: bool
    receipt: dict


def no_reading(error, receipt=None):
    receipt = receipt or Receipt("scene.judge", None, None, None)
    receipt.could_not_look.append(str(error))
    return Verdict(NO_LOOK, 3, error.failure or observation(str(error)), {"missing": error.missing}, False, receipt.as_dict())


def classify(plan, rows, receipts, *, accepted=True):
    """Pure classification of the script's checker, one kept call and its receipt facts."""
    plan_check(plan)
    run_receipt = next((r for r in receipts if isinstance(r.get("entry"), dict) and r["entry"].get("name") == "s.run"), {})
    game, build, commit = (run_receipt.get(k) for k in ("game", "build", "commit"))
    receipt = Receipt("scene.judge", run_receipt.get("entry", {}).get("request"), game, build, commit)
    stamps = [s for r in receipts if names(r.get("stamps")) for s in r["stamps"]]
    receipt.stamps = sorted(set(stamps))

    def verdict(word, row, failed=None, **evidence):
        counts = word == SUCCESS and accepted and not stamps and isinstance(commit, str) and bool(re.fullmatch(r"[0-9a-f]{40,64}", commit))
        return Verdict(word, row, failed, evidence, counts, receipt.as_dict())

    try:
        trace = Trace(rows)
        if (not isinstance(build, dict) or not build.get("list") or not build.get("version") or
                any(r.get("build") != build for r in receipts)):
            raise NoReading("the receipts do not establish one loaded build")
        if (not isinstance(game, dict) or not game.get("session") or not game.get("name") or
                any(not isinstance(r.get("game"), dict) or any(r["game"].get(k) != game[k] for k in ("name", "session"))
                    for r in receipts) or (game.get("tick_before"), game.get("tick_after")) != (trace.start, trace.stop)):
            raise NoReading("the receipt does not identify the trace's game, session and tick span")
        if any(not names(r.get("stamps")) or r.get("commit") != commit for r in receipts):
            raise NoReading("the receipt stamps or commit could not be established")
        fault = apparatus(trace)
        first, hits, misses, final = readings(plan, trace)
        evidence = {"trace": "held", "build": "held", "exposure": "exposure" in hits}
        if "forbidden" in hits:
            return verdict(MOD_FAILURE, 1, hits["forbidden"], **evidence)
        if first.get("success") is True:
            fault = observation("success already true at first sample", trace.start, hits["success"]["observed"])
        if fault:
            return verdict(APPARATUS, 2, fault, **evidence)
        state = trace.end.get("state")
        if state not in ("hit", "done") or trace.end.get("complete") is not True:
            raise NoReading("run ended %s" % state, observation("run end", trace.stop, trace.end.get("unknown") or trace.end.get("why")))
        if "opportunity" in misses:
            miss = misses["opportunity"]
            spoiler = spoiled_by(plan, trace, miss, hits.get("cast_activity"))
            if spoiler:
                return verdict(ENVIRONMENT, 4, miss, spoiler=spoiler, **evidence)
            return verdict(UNRESOLVED, 5, miss, **evidence)
        if "exposure" not in hits:
            return verdict(UNRESOLVED, 9, final.get("exposure", observation("exposure was not declared")), **evidence)
        success = final["success"]
        if success["observed"][0]["v"] is True:
            return verdict(SUCCESS, 6, **evidence)
        if plan.get("kind", "A") == "A":
            return verdict(MOD_FAILURE, 8, success, **evidence)
        if plan.get("allowed_miss"):
            return verdict(RANDOM_MISS, 7, success, **evidence)
        return verdict(UNRESOLVED, 9, success, **evidence)
    except NoReading as e:
        return no_reading(e, receipt)


def _load(path, lines=False):
    text = path.read_text(encoding="utf-8")
    if lines:
        rows = [C.parse_json(line) for line in text.splitlines() if line.strip()]
        if any(not isinstance(r, dict) for r in rows):
            raise ValueError("a row in " + path.name + " is not an object")
        return rows
    return C.parse_json(text)


def judge(run_dir, rejudge=False):
    """Classify the call selected by contract.json and keep the verdict in this run folder."""
    try:
        return _judge(run_dir, rejudge)
    except NoReading as e:
        return no_reading(e)
    except (OSError, ValueError) as e:
        return no_reading(NoReading(str(e)))


def _judge(run_dir, rejudge):
    folder = Path(run_dir)
    contract = folder / "contract.json"
    if not contract.is_file():
        raise Refused("NO_CONTRACT", "no " + str(contract))
    try:
        plan = _load(contract)
    except (OSError, ValueError) as e:
        raise Refused("BAD_PLAN", str(e)) from e
    plan_check(plan)
    files = sorted(folder.glob("trace_*.jsonl"))
    request = plan.get("request")
    if request:
        files = [f for f in files if f.stem == "trace_" + request]
    if not files:
        raise Refused("NO_TRACE", "no kept trace for %s" % (request or folder))
    if len(files) != 1:
        raise Refused("BAD_PLAN", "choose request from " + ", ".join(f.stem[6:] for f in files))
    path, = files
    request = path.stem[6:]
    first_path = folder / "verdict.json"
    previous = _load(first_path) if first_path.exists() else None
    if rejudge and previous is None:
        raise Refused("NO_VERDICT", "judge the kept run before rejudging it")
    receipt_path, run_path = folder / "receipts.jsonl", folder / "run.json"
    try:
        kept = hashlib.sha256()
        for f in (path, receipt_path, run_path):
            kept.update(hashlib.sha256(f.read_bytes()).digest())
        evidence_hash = kept.hexdigest()
        rows, receipts, run = _load(path, lines=True), _load(receipt_path, lines=True), _load(run_path)
    except (OSError, ValueError) as e:
        raise NoReading("could not read the kept trace, run metadata or receipts: " + str(e)) from e
    if previous is not None and (previous["request"], previous["evidence_hash"]) != (request, evidence_hash):
        raise Refused("EVIDENCE_CHANGED", "the kept call or receipt changed since the first judgement")
    checker_hash = hashlib.sha256(C.canon(plan).encode("utf-8")).hexdigest()
    if previous is not None and not rejudge:
        if checker_hash != previous["checker_hash"]:
            raise Refused("CONTRACT_MISMATCH", "the checker changed; use --rejudge")
        return Verdict(**{k: previous[k] for k in Verdict.__dataclass_fields__})

    # an entry may carry more than its name and request (the s.run entry names its mode since 0aaaaf3de7)
    matching = [r for r in receipts if isinstance(r.get("entry"), dict) and r["entry"].get("name") == "s.run"
                and r["entry"].get("request") == request]
    if not matching or not isinstance(run, dict) or any(
        not isinstance(r.get("game"), dict) or r["game"].get("session") != run.get("session") or
        r["game"].get("name") != run.get("game") for r in matching
    ):
        raise NoReading("no receipt matches request " + request + " and the kept session")
    accepted = run.get("mode") == "accept" and run.get("commit") == matching[0].get("commit")
    result = classify(plan, rows, matching + [r for r in receipts if r not in matching], accepted=accepted)
    if rejudge and result.evidence.get("missing"):
        return result
    old_plan = previous["checker_plan"] if previous else plan
    changes = sorted(k for k in plan.keys() | old_plan.keys() if plan.get(k) != old_plan.get(k))
    record = dict(asdict(result), request=request, evidence_hash=evidence_hash, checker_hash=checker_hash,
                  checker=plan.get("version", VERSION), judge_version=VERSION, checker_plan=plan,
                  changed=checker_hash != (previous or {}).get("checker_hash", checker_hash), changes=changes)
    line = json.dumps(record, sort_keys=True) + "\n"
    if rejudge:
        with (folder / "verdict_history.jsonl").open("a", encoding="utf-8") as f:
            f.write(line)
    else:
        with tempfile.TemporaryDirectory(dir=folder) as d:
            temp = Path(d) / first_path.name
            temp.write_text(line, encoding="utf-8")
            try:
                os.link(temp, first_path)
            except FileExistsError:
                return _judge(run_dir, rejudge)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dir")
    ap.add_argument("--rejudge", action="store_true")
    args = ap.parse_args(argv)
    try:
        result = judge(args.run_dir, args.rejudge)
    except Refused as e:
        print("REFUSED %s" % e)
        return 7
    print(json.dumps(asdict(result), sort_keys=True))
    return EXIT[result.outcome]


if __name__ == "__main__":
    sys.exit(main())
