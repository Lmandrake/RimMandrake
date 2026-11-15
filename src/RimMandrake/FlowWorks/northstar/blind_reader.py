#!/usr/bin/env python3
"""northstar/blind_reader.py -- LOOK_BLIND_READER, the Stage 6 look of FlowWorks 0.1.0 (test_table.json).

A reader that did not make the captures names what they show, and the answers are scored against a truth key the
reader never sees. Seven bars are decided in part by it: canal_reads_as_dug, fill_level_legible, pit_reads_as_hole,
covered_pit_springs, hose_reads_as_hose, hung_bridge_spans, and inv_looks (the look inventory: every question here).

Built Stage 3, 2026-11-14 (RIMMANDRAKE_AUTOBUILD_FLOWWORKS_SEVEN_BARS_LEFT), offline: UNRUN until Stage 6 has run the
six scenes and saved their captures. Every scene carries its foil from scenes.json (`control`): a foil question passes
only when the reader reads the foil the OTHER way, so a reader that answers from position or habit fails.

Stage 6, after the scenes (sc_dig_and_read, sc_fill_tiers, sc_pit_reads, sc_covered_pit, sc_hose_look, sc_hung_bridge):
    python3 src/RimMandrake/FlowWorks/northstar/blind_reader.py template > captures.json   # fill images, n, truth
    python3 src/RimMandrake/FlowWorks/northstar/blind_reader.py read --manifest captures.json --out result.json
    python3 src/RimMandrake/FlowWorks/northstar/blind_reader.py plan                       # the questions, no reader
Offline proof of the scorer and the blindness: selftest_blind_reader.py.

The manifest is {"questions": {<qid>: {"images": [path...], "n": <int, order questions>, "truth": <order questions'
list, label questions' list>}}}. A fixed-truth question (a choice) takes its truth from this file, never the manifest.
The truth for an order question is the staging's own geometry (e.g. plot_B's runs F0..F4), written by whoever ran it.

The reader is `claude -p` (in-game LLM transport ruling: the CLI, never an API key), run from an empty temp dir with
only the Read tool. It gets the question text, the options and the image paths; never a truth, a defName or a label.
Verdicts: PASS, FAIL, UNMEASURED (no image, no answer, an unparsable answer). A bar is PASS only when every one of its
questions is PASS.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

CANT = "cannot tell"
BARS = ("canal_reads_as_dug", "fill_level_legible", "pit_reads_as_hole", "covered_pit_springs", "hose_reads_as_hose",
        "hung_bridge_spans")
LOOK_BAR = "inv_looks"      # the look inventory: decided by every question
LIQUIDS = ["water", "salt water", "mud", "oil", "tar", "lava", "acid", "blood", CANT]


def Q(qid, bar, scene, kind, ask, options=None, truth=None, foil=False):
    return {"id": qid, "bar": bar, "scene": scene, "kind": kind, "ask": ask, "options": options, "truth": truth,
            "foil": foil}


QUESTIONS = [
    Q("dig_depth_order", "canal_reads_as_dug", "sc_dig_and_read", "order",
      "The picture shows {n} dug pads in a row, numbered 1 to {n} from left to right. List the pad numbers from "
      "shallowest to deepest, by how deep each one looks."),
    Q("dig_depth_order_foil", "canal_reads_as_dug", "sc_dig_and_read", "order",
      "The picture shows {n} dug pads in a row, numbered 1 to {n} from left to right. List the pad numbers from "
      "shallowest to deepest, by how deep each one looks.", foil=True),
    Q("dig_banks", "canal_reads_as_dug", "sc_dig_and_read", "choice",
      "Look at the ground right beside the dug pads. Is it wet or dry?", ["dry", "wet", CANT], "dry"),
    Q("fill_order", "fill_level_legible", "sc_fill_tiers", "order",
      "The picture shows {n} straight runs, numbered 1 to {n} from top to bottom. List the run numbers from least "
      "full to most full of liquid."),
    Q("fill_liquids", "fill_level_legible", "sc_fill_tiers", "label_each",
      "The picture shows {n} pools, numbered 1 to {n} from left to right. Name the liquid in each pool, in order.",
      LIQUIDS),
    Q("fill_same_foil", "fill_level_legible", "sc_fill_tiers", "choice",
      "The picture shows two runs of liquid. Do they look the same (same liquid, same fill) or different?",
      ["the same", "different", CANT], "the same", foil=True),
    Q("pit_kind", "pit_reads_as_hole", "sc_pit_reads", "choice",
      "What is the square region at the centre of the picture?",
      ["a hole dug into the ground", "a raised block or wall", "flat ground or a floor", "a pool of liquid", CANT],
      "a hole dug into the ground"),
    Q("pit_occupant", "pit_reads_as_hole", "sc_pit_reads", "choice",
      "Is there a person in the square region at the centre, and if so where?",
      ["below the ground line, inside it", "standing on top of the ground", "nobody", CANT],
      "below the ground line, inside it"),
    Q("pit_occupant_foil", "pit_reads_as_hole", "sc_pit_reads", "choice",
      "Is there a person in the square region at the centre, and if so where?",
      ["below the ground line, inside it", "standing on top of the ground", "nobody", CANT], "nobody", foil=True),
    Q("cover_falls", "covered_pit_springs", "sc_covered_pit", "choice",
      "The picture is a before|after pair. In the after half, what happened to the creature that walked onto the "
      "covered square?", ["it fell through into a hole", "it walked across", "it was never there", CANT],
      "it fell through into a hole"),
    Q("cover_falls_foil", "covered_pit_springs", "sc_covered_pit", "choice",
      "The picture is a before|after pair. In the after half, what happened to the creature that walked onto the "
      "covered square?", ["it fell through into a hole", "it walked across", "it was never there", CANT],
      "it walked across", foil=True),
    Q("hose_kind", "hose_reads_as_hose", "sc_hose_look", "choice",
      "What is the long thin line running between the machines?",
      ["a hose carrying liquid", "a power cable", "a rope", "a wall or fence", CANT], "a hose carrying liquid"),
    Q("hose_full", "hose_reads_as_hose", "sc_hose_look", "choice",
      "Is that long thin line full (rounded, carrying something) or flat (empty)?", ["full", "flat", CANT], "full"),
    Q("hose_flat_foil", "hose_reads_as_hose", "sc_hose_look", "choice",
      "Is that long thin line full (rounded, carrying something) or flat (empty)?", ["full", "flat", CANT], "flat",
      foil=True),
    Q("bridge_kind", "hung_bridge_spans", "sc_hung_bridge", "choice",
      "What crosses the channel?",
      ["a bridge hung from posts or anchors", "a solid causeway filled in", "a floor laid flat on the ground",
       "nothing", CANT], "a bridge hung from posts or anchors"),
    Q("bridge_under", "hung_bridge_spans", "sc_hung_bridge", "choice",
      "Could someone walk along the channel underneath the crossing?", ["yes", "no", CANT], "yes"),
    Q("bridge_kind_foil", "hung_bridge_spans", "sc_hung_bridge", "choice",
      "What crosses the channel?",
      ["a bridge hung from posts or anchors", "a solid causeway filled in", "a floor laid flat on the ground",
       "nothing", CANT], "nothing", foil=True),
]
BY_ID = {q["id"]: q for q in QUESTIONS}


def _norm(v):
    return v.strip().lower() if isinstance(v, str) else v


def score(q, spec, answer):
    """-> (verdict, why) for one question; spec is the manifest's entry (None when the manifest lacks it)."""
    if not spec or not spec.get("images"):
        return "UNMEASURED", "no capture in the manifest"
    missing = [p for p in spec["images"] if not os.path.exists(p)]
    if missing:
        return "UNMEASURED", "capture not on disk: %s" % missing[0]
    if answer is None:
        return "UNMEASURED", "the reader gave no answer"
    if q["kind"] == "choice":
        a = _norm(answer)
        if a not in [_norm(o) for o in q["options"]]:
            return "UNMEASURED", "answer %r is not one of the options" % (answer,)
        ok = a == _norm(q["truth"])
        return ("PASS" if ok else "FAIL"), "read %r, truth %r" % (answer, q["truth"])
    truth = spec.get("truth")
    if not isinstance(truth, list) or not truth:
        return "UNMEASURED", "the manifest gives no truth list"
    if q["kind"] == "order":
        if _norm(answer) == CANT:
            same = False
        elif isinstance(answer, list) and sorted(answer) == list(range(1, len(truth) + 1)):
            same = answer == truth
        else:
            return "UNMEASURED", "answer %r is not an order of 1..%d" % (answer, len(truth))
        # a foil passes only when the reader can NOT recover the order (scenes.json control)
        ok = (not same) if q["foil"] else same
        return ("PASS" if ok else "FAIL"), "read %r, truth %r%s" % (answer, truth, " (foil)" if q["foil"] else "")
    if q["kind"] == "label_each":
        if not isinstance(answer, list) or len(answer) != len(truth):
            return "UNMEASURED", "answer %r is not %d labels" % (answer, len(truth))
        ok = [_norm(a) for a in answer] == [_norm(t) for t in truth]
        return ("PASS" if ok else "FAIL"), "read %r, truth %r" % (answer, truth)
    return "UNMEASURED", "unknown question kind %r" % q["kind"]


def prompt_for(qs, manifest):
    """The reader's whole prompt: question text, options, image paths. No truth, no defName, no label."""
    L = ["You are shown pictures from a video game. Answer only from what you SEE in the pictures.",
         "Read each picture with the Read tool; read no other file. Answer every question.",
         'Reply with ONE JSON object, nothing after it: {"<question id>": <answer>, ...}.',
         'A choice answer is one option, copied exactly. An order answer is a list of numbers. If you cannot tell, '
         'answer "%s".' % CANT, ""]
    for q in qs:
        spec = manifest.get(q["id"]) or {}
        n = spec.get("n") or len(spec.get("truth") or []) or "N"
        L.append("Question %s: %s" % (q["id"], q["ask"].format(n=n)))
        for p in spec.get("images") or []:
            L.append("  picture: %s" % p)
        if q["kind"] == "choice":
            L.append("  options: " + " | ".join(q["options"]))
        elif q["kind"] == "label_each":
            L.append("  answer a list of %s labels, each one of: %s" % (n, " | ".join(q["options"])))
        else:
            L.append("  answer a list of the numbers 1..%s in your order, or \"%s\"" % (n, CANT))
        L.append("")
    return "\n".join(L)


def leaks(prompt, manifest):
    """-> truth values (manifest truths beyond option words) that appear in the prompt: must be empty."""
    out = []
    for qid, spec in manifest.items():
        t = (spec or {}).get("truth")
        if isinstance(t, list) and len(t) > 1 and all(isinstance(x, int) for x in t):
            if re.search(r"\[\s*%s\s*\]" % r"\s*,\s*".join(str(x) for x in t), prompt):
                out.append(qid)
        for k in ("label", "defName", "depths", "fills"):
            v = (spec or {}).get(k)
            if v and str(v) in prompt:
                out.append("%s.%s" % (qid, k))
    return out


def parse_reply(text):
    """-> the last JSON object in the reader's reply, or None."""
    text, dec = text or "", json.JSONDecoder()
    for i in reversed([m.start() for m in re.finditer(r"\{", text)]):
        try:
            obj, _ = dec.raw_decode(text, i)
        except ValueError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def _native(p):
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", p)
    return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/")) if m and os.name != "nt" else p


def claude_reader(prompt, image_dirs, model="opus", timeout=900):
    """One fresh `claude -p` reader in an empty temp dir, Read only. -> its stdout."""
    with tempfile.TemporaryDirectory(prefix="blind_reader_") as d:
        cmd = ["claude", "-p", prompt, "--model", model, "--allowedTools", "Read", "--output-format", "text"]
        for x in sorted(set(image_dirs)):
            cmd += ["--add-dir", x]
        r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            raise RuntimeError("claude -p rc %d: %s" % (r.returncode, (r.stderr or r.stdout)[-400:]))
        return r.stdout


def run(manifest, reader):
    """-> the result: per question verdicts, per bar verdicts. reader(prompt, image_dirs) -> reply text."""
    for spec in manifest.values():
        if spec and spec.get("images"):
            spec["images"] = [_native(p) for p in spec["images"]]
    asked = [q for q in QUESTIONS if (manifest.get(q["id"]) or {}).get("images")]
    prompt = prompt_for(asked, manifest)
    leaked = leaks(prompt, manifest)
    if leaked:
        raise SystemExit("REFUSED: the prompt carries truth for %s" % ", ".join(leaked))
    reply, answers = None, None
    if asked:
        dirs = [os.path.dirname(os.path.abspath(p)) for q in asked for p in manifest[q["id"]]["images"]]
        reply = reader(prompt, dirs)
        answers = parse_reply(reply)
    rows = []
    for q in QUESTIONS:
        a = (answers or {}).get(q["id"]) if isinstance(answers, dict) else None
        v, why = score(q, manifest.get(q["id"]), a)
        rows.append({"id": q["id"], "bar": q["bar"], "scene": q["scene"], "foil": q["foil"], "verdict": v, "why": why})
    bars = {}
    for b in BARS + (LOOK_BAR,):
        vs = [r["verdict"] for r in rows if b == LOOK_BAR or r["bar"] == b]
        bars[b] = "FAIL" if "FAIL" in vs else ("PASS" if vs and all(v == "PASS" for v in vs) else "UNMEASURED")
    return {"test": "LOOK_BLIND_READER", "rows": rows, "bars": bars, "reply_tail": (reply or "")[-2000:],
            "parsed": isinstance(answers, dict)}


def template():
    out = {}
    for q in QUESTIONS:
        e = {"scene": q["scene"], "foil": q["foil"], "images": []}
        if q["kind"] in ("order", "label_each"):
            e.update({"n": None, "truth": None})
        out[q["id"]] = e
    return {"questions": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("template")
    sub.add_parser("plan")
    rd = sub.add_parser("read")
    rd.add_argument("--manifest", required=True)
    rd.add_argument("--out", required=True)
    rd.add_argument("--model", default="opus")
    a = ap.parse_args(argv)
    if a.cmd == "template":
        print(json.dumps(template(), indent=1))
        return 0
    if a.cmd == "plan":
        print(prompt_for(QUESTIONS, {}))
        return 0
    man = json.load(open(a.manifest)).get("questions") or {}
    res = run(man, lambda p, d: claude_reader(p, d, model=a.model))
    json.dump(res, open(a.out, "w"), indent=1)
    for b, v in res["bars"].items():
        print("%-22s %s" % (b, v))
    return 0 if all(v == "PASS" for v in res["bars"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
