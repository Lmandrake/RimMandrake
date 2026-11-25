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

The reader is `claude -p` (in-game LLM transport ruling: the CLI, never an API key), sandboxed by claude_reader: Read
only, on picture copies under neutral names. It gets neutral question ids (Q1 ...), question text, shuffled options and
those copies; never a truth, a question id, a foil mark, a defName, a label or a repo path (leaks() refuses the prompt).
Verdicts: PASS, FAIL, UNMEASURED (no image, no answer, an unparsable answer). A bar is PASS only when every one of its
questions is PASS.
"""
import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "rimflow"))  # rimflow/effort.py, appended: shadows nothing
import effort as EF  # noqa: E402  the one effort table (RIMMANDRAKE_PASS_EFFORT_ON_EVERY_LAUNCH_STEVEDESKTOP_RAN_MEDIUM)

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
    Q("fill_differ", "fill_level_legible", "sc_fill_tiers", "choice",
      "The picture shows two runs of liquid. Do they look the same (same liquid, same fill) or different?",
      ["the same", "different", CANT], "different"),
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


def _ints(v, n):
    """v is exactly a permutation of the integers 1..n (no bools, no strings)."""
    return (isinstance(v, list) and len(v) == n and all(type(x) is int for x in v)
            and sorted(v) == list(range(1, n + 1)))


def _rho(a, b):
    """Spearman rank correlation of two orders of 1..n."""
    n = len(a)
    if n < 2:
        return 1.0
    ra, rb = {x: i for i, x in enumerate(a)}, {x: i for i, x in enumerate(b)}
    return 1 - 6.0 * sum((ra[x] - rb[x]) ** 2 for x in a) / (n * (n * n - 1))


DENY = ("/home", "/mnt", "/tmp", "/root")   # the reader may Read none of these (claude_reader)
PICS_ROOT = "/var/tmp"                       # where the picture copies live: outside every DENY root
KEEP_IN = ("/home/", "/mnt/")                # the manifest and the result file must live under one of these


FOIL_RHO = 0.5   # an order foil passes on "cannot tell" or a reading below this agreement: the order is no longer read


def images_of(spec):
    """-> the entry's image list, or None when the entry or its images are malformed."""
    if not isinstance(spec, dict):
        return None
    im = spec.get("images")
    return im if isinstance(im, list) and im and all(isinstance(p, str) and p for p in im) else None


def score(q, spec, answer):
    """-> (verdict, why) for one question; spec is the manifest's entry (None when the manifest lacks it)."""
    if images_of(spec) is None:
        return "UNMEASURED", "no capture (or a malformed entry) in the manifest"
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
        if not _ints(truth, len(truth)):
            return "UNMEASURED", "the manifest truth %r is not an order of the integers 1..%d" % (truth, len(truth))
        if _norm(answer) == CANT:
            same, rho = False, None
        elif _ints(answer, len(truth)):
            same, rho = answer == truth, _rho(answer, truth)
        else:
            return "UNMEASURED", "answer %r is not an order of 1..%d" % (answer, len(truth))
        # a foil passes only when the reader can NOT recover the order (scenes.json control): "cannot tell", or an
        # order agreeing with the truth below FOIL_RHO; a near-miss is still a reading
        ok = (rho is None or rho < FOIL_RHO) if q["foil"] else same
        return ("PASS" if ok else "FAIL"), "read %r, truth %r%s" % (answer, truth, " (foil)" if q["foil"] else "")
    if q["kind"] == "label_each":
        if not all(isinstance(t, str) for t in truth):
            return "UNMEASURED", "the manifest truth %r is not a list of labels" % (truth,)
        if not isinstance(answer, list) or len(answer) != len(truth) or not all(isinstance(a, str) for a in answer):
            return "UNMEASURED", "answer %r is not %d labels" % (answer, len(truth))
        ok = [_norm(a) for a in answer] == [_norm(t) for t in truth]
        return ("PASS" if ok else "FAIL"), "read %r, truth %r" % (answer, truth)
    return "UNMEASURED", "unknown question kind %r" % q["kind"]


def prompt_for(asked, rng=None):
    """The reader's whole prompt. asked: [(neutral id, question, n, [picture aliases])]. Only neutral ids (Q1, Q2 ...),
    question text, options (shuffled when rng is given) and picture aliases: no truth, question id, foil mark, defName,
    label or repo path. -> (prompt, the option order shown per neutral id)."""
    L = ["You are shown pictures from a video game. Answer only from what you SEE in the pictures.",
         "Read each picture with the Read tool; read no other file. Answer every question.",
         'Reply with ONE JSON object, nothing after it: {"Q1": <answer>, "Q2": <answer>, ...}.',
         'A choice answer is one option, copied exactly. An order answer is a list of numbers. If you cannot tell, '
         'answer "%s".' % CANT, ""]
    shown = {}
    for nid, q, n, pics in asked:
        L.append("%s: %s" % (nid, q["ask"].format(n=n)))
        for p in pics:
            L.append("  picture: %s" % p)
        opts = list(q["options"] or [])
        if rng is not None:
            rng.shuffle(opts)
        shown[nid] = opts
        if q["kind"] == "choice":
            L.append("  options: " + " | ".join(opts))
        elif q["kind"] == "label_each":
            L.append("  answer a list of %s labels, each one of: %s" % (n, " | ".join(opts)))
        else:
            L.append('  answer a list of the numbers 1..%s in your order, or "%s"' % (n, CANT))
        L.append("")
    return "\n".join(L), shown


def leaks(prompt, manifest):
    """-> what of the truth key, the question ids or the repo appears in the prompt: must be empty."""
    out = [q["id"] for q in QUESTIONS if q["id"] in prompt]
    out += [w for w in ("foil", "control", "truth", "/home/", "/mnt/", "northstar", "FlowWorks") if w in prompt]
    for qid, spec in manifest.items():
        if not isinstance(spec, dict):
            continue
        t = spec.get("truth")
        q = BY_ID.get(qid) or {}
        # a label truth made only of option words is in every prompt by design; an order truth is a run of numbers
        if (isinstance(t, list) and len(t) > 1 and all(isinstance(x, (str, int)) for x in t)
                and not set(map(_norm, t)) <= set(map(_norm, q.get("options") or []))):
            if re.search(r"\s*,\s*".join(re.escape(str(x)) for x in t), prompt):
                out.append(qid + ".truth")
        for k in ("label", "defName", "depths", "fills"):
            v = spec.get(k)
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


def claude_reader(prompt, pics_dir, model="opus", timeout=900):
    """One fresh `claude -p` reader, cwd an empty dir under PICS_ROOT holding only the picture copies. Its tool set is
    Read alone (--tools), no MCP, dontAsk (anything not allowed is refused), and a Read of /home, /mnt, /tmp or /root is
    denied outright (deny beats the user settings' bare Read allow), so this repo's answer key, the manifest and any
    result file (main refuses either outside /home or /mnt) are out of its reach. User settings still load: they carry
    the environment the CLI's account comes from. Rules use //path, the absolute form. -> its stdout."""
    cmd = [os.path.expanduser("~/.local/bin/claude"), "-p", prompt, "--model", model, "--tools", "Read", "--strict-mcp-config",
           "--permission-mode", "dontAsk", "--allowedTools", "Read(/%s/**)" % pics_dir,
           "--disallowedTools", *["Read(%s%s/**)" % (sl, d) for d in DENY for sl in ("/", "//")],
           "--no-session-persistence", "--output-format", "text"] + EF.effort_args(model)
    r = subprocess.run(cmd, cwd=pics_dir, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError("claude -p rc %d: %s" % (r.returncode, (r.stderr or r.stdout)[-400:]))
    return r.stdout


def run(manifest, reader, seed=None):
    """-> the result: per question verdicts, per bar verdicts. reader(prompt, pics_dir) -> reply text.
    The pictures are copied to a fresh temp dir under neutral names; questions and options are shuffled by `seed`."""
    if not isinstance(manifest, dict):
        raise SystemExit("REFUSED: the manifest's questions are not an object")
    for spec in manifest.values():
        if images_of(spec):
            spec["images"] = [_native(p) for p in spec["images"]]
    seed = seed if seed is not None else int.from_bytes(os.urandom(4), "big")
    rng = random.Random(seed)
    asked_q = [q for q in QUESTIONS if images_of(manifest.get(q["id"])) and
               all(os.path.exists(p) for p in manifest[q["id"]]["images"])]
    rng.shuffle(asked_q)
    reply, answers, nid_of = None, None, {}
    # under PICS_ROOT, never $TMPDIR: a seat TMPDIR lies under /home, which claude_reader denies the reader
    with tempfile.TemporaryDirectory(prefix="blind_reader_", dir=PICS_ROOT) as pics_dir:
        alias, asked = {}, []
        for i, q in enumerate(asked_q, 1):
            spec = manifest[q["id"]]
            pics = []
            for p in spec["images"]:
                if p not in alias:
                    alias[p] = os.path.join(pics_dir, "picture_%02d%s" % (len(alias) + 1, os.path.splitext(p)[1]))
                    shutil.copyfile(p, alias[p])
                pics.append(alias[p])
            n = spec.get("n") or len(spec.get("truth") or []) or "N"
            nid_of[q["id"]] = "Q%d" % i
            asked.append(("Q%d" % i, q, n, pics))
        prompt, _ = prompt_for(asked, rng)
        leaked = leaks(prompt, manifest)
        if leaked:
            raise SystemExit("REFUSED: the prompt carries %s" % ", ".join(leaked))
        if asked:
            reply = reader(prompt, pics_dir)
            answers = parse_reply(reply)
    rows = []
    for q in QUESTIONS:
        a = answers.get(nid_of[q["id"]]) if isinstance(answers, dict) and q["id"] in nid_of else None
        v, why = score(q, manifest.get(q["id"]), a)
        rows.append({"id": q["id"], "asked_as": nid_of.get(q["id"]), "bar": q["bar"], "scene": q["scene"],
                     "foil": q["foil"], "verdict": v, "why": why})
    bars = {}
    for b in BARS + (LOOK_BAR,):
        vs = [r["verdict"] for r in rows if b == LOOK_BAR or r["bar"] == b]
        bars[b] = "FAIL" if "FAIL" in vs else ("PASS" if vs and all(v == "PASS" for v in vs) else "UNMEASURED")
    return {"test": "LOOK_BLIND_READER", "seed": seed, "rows": rows, "bars": bars,
            "reply_tail": (reply or "")[-2000:], "parsed": isinstance(answers, dict)}


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
    rd.add_argument("--seed", type=int, default=None)
    a = ap.parse_args(argv)
    if a.cmd == "template":
        print(json.dumps(template(), indent=1))
        return 0
    if a.cmd == "plan":
        print(prompt_for([("Q%d" % i, q, "N", ["picture_NN.png"]) for i, q in enumerate(QUESTIONS, 1)])[0])
        return 0
    for f in (a.manifest, a.out):
        if not os.path.realpath(f).startswith(KEEP_IN):
            raise SystemExit("REFUSED: %s is outside %s, where the reader could Read the truth" % (f, " or ".join(KEEP_IN)))
    man = json.load(open(a.manifest)).get("questions") or {}
    res = run(man, lambda p, d: claude_reader(p, d, model=a.model), seed=a.seed)
    json.dump(res, open(a.out, "w"), indent=1)
    for b, v in res["bars"].items():
        print("%-22s %s" % (b, v))
    return 0 if all(v == "PASS" for v in res["bars"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
