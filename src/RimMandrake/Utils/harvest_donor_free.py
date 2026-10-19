#!/usr/bin/env python3
"""harvest_donor_free.py -- ONE-page verdict on a Player.log from the donor-free list (gate §0.5.5 item 5).

    python3 src/RimMandrake/Utils/harvest_donor_free.py [--log Player.log] [--running-mods reply.json]
            [--expect-list ModsConfig.FULL.CANDIDATE_DONORS_RETIRED_2026-10-18.xml] [--against prev.json|prev.log]
            [--show exc|xref|tex|scribe|config|patch] [--json out.json] [--no-history]

Spec: design/RimMandrake/biome_sprint_kickoff_2026-10-15.md §0.5.5 item 5 -- "the donor-off Player.log has 0
exceptions and 0 cross-reference or texture misses on RM_/RSW_/RUT_". Item: DONOR_FOUR_RETIRE_JUST_GET_IT_DONE.
Read-only: the log is opened for reading and nothing else is touched (no game, bridge, ModsConfig).

ONE streaming pass over the log (tens of MB: never readlines), and in that pass:
  (a) WHICH MODS LOADED: the LAST `Initializing new game with mods:` / `Loading game from file X with mods:` block
      (Verse/Game.cs:495, SavedGameLoaderNow.cs:11 -- RunningMods, the truth, not ModsConfig which is the NEXT
      load), or `--running-mods` (a saved `jawa/running_mods` reply). Asserts no retired packageId is loaded (the
      four of DONOR_FOUR_RETIRE plus every row of infrastructure/state/facts/retired_mods.json). At the main menu
      there is no block yet: the list is UNMEASURED until a game is started/loaded or the reply file is given.
  (b) counts by class: exception EVENTS (a line opening an exception, stack frames folded into it; attributed
      ours / retired-donor / other by the line + its frames), cross-reference errors split retired-donor-def-or-
      its-rename / ours / other, config errors, texture misses (4 engine messages) split ours (a path our src XML
      names, or an RM_/RSW_/RUT_ path) / others, XML patch failures ours/others, Scribe `Could not load reference`
      lines, and the Verse.Log cap `Reached max messages limit` (after it the log is BLIND: nothing is written).
  (c) the delta against harvest_log.py's CHECKS baselines (same regexes, same pass) and against the previous run
      (history under ~/.cache/rimmandrake/harvest_donor_free/, or --against).

EXIT: 0 = the three item-5 log bars hold (0 exception events, 0 cross-ref lines naming RM_/RSW_/RUT_, 0 texture
misses on our paths). 1 = a bar fails. 2 = NOT the donor-free run (a retired packageId is loaded). 3 = the log is
blind or unidentified (message cap reached, or no mod block and no reply file) -- not a pass. Exit 0 says the LOG
holds the bars; spawns, mapgen and flight (the rest of item 5) are l1_donor_off_round.py's rows.

l1_donor_off_round.py `run --phase log` grades its L01-L04 rows through `classify()` here: one classifier, two
callers (2026-10-18; its own ad-hoc greps were retired).
"""
import argparse
import collections
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(REPO, "src")
if HERE not in sys.path:
    sys.path.insert(0, HERE)

RETIRED_FOUR = ("mlie.starwarsanimalcollection", "sarg.alphaanimals", "daria40k.alphaanimalspatchoutposts",
                "sarg.alphabiomes")
RETIRED_JSON = os.path.join(REPO, "infrastructure", "state", "facts", "retired_mods.json")
EXPECT_LIST = os.path.join(REPO, "infrastructure", "state", "modlists",
                           "ModsConfig.FULL.CANDIDATE_DONORS_RETIRED_2026-10-18.xml")
HISTORY = os.path.join(os.path.expanduser("~"), ".cache", "rimmandrake", "harvest_donor_free")

OURS_RE = re.compile(r"\b(RM|RSW|RUT)_")
OURS_CODE_RE = re.compile(r"RimMandrake|RimStarWars|RimUtinni|JawaBench|mandrake\.r(m|sw|ut)\.|\b(RM|RSW|RUT)_")
DONOR_CODE_RE = re.compile(r"AlphaBehavioursAndEvents|AlphaBiomes\.|AlphaAnimals|StarWarsAnimalCollection")
MODS_HEAD_RE = re.compile(r"^(Initializing new game with mods:|Loading game from file (.*) with mods:)\s*$")
MOD_ROW_RE = re.compile(r"^  - (\S+)")
EXC_RE = re.compile(r"\b\w*Exception\b")
FRAME_RE = re.compile(r"^(\s|\(Filename:|Rethrow as|--- End)|^[\w.`<>\[\],+|]+:[\w.`<>\[\]|]+ ?\(")
XREF_RE = re.compile(r"Could not resolve cross-reference(?::| to)\s.*?named (\S+?)(?=\s|$)")
SCRIBE_RE = re.compile(r"Could not load reference to \S+ named (\S+)")
CONFIG_RE = re.compile(r"^(?:Config error in|Exception in ConfigErrors\(\) of) (\S+?):")
PATCH_RE = re.compile(r"[Pp]atch operation .* failed|PatchOperation.*failed")
TEX_RES = (re.compile(r"Failed to find any textures at (\S+)"),
           re.compile(r"No textures found at (?:path )?(\S+)"),
           re.compile(r"Could not load Texture2D at '([^']*)'"),
           re.compile(r"Could not (?:find|get) texture:?\s*(\S+)"))
CAP = "Reached max messages limit"
IDENT = ("[JawaBench] ready", "Bridge token:")
FIRST_ERRORISH = re.compile(r"Exception|Could not find type named|Config error in")


# ------------------------------------------------------------------ reference data (all offline, all cheap)
def retired_packages():
    out = set(RETIRED_FOUR)
    try:
        for r in json.load(open(RETIRED_JSON, encoding="utf-8")).get("retired", []):
            if r.get("packageId"):
                out.add(r["packageId"].lower())
    except (OSError, ValueError):
        pass
    return out


def donor_names(index=None):
    """defNames the four retired donors define, from the newest def dump that still loaded them (a dump of the
    donor-free list cannot know them), or an empty set (then the split is UNMEASURED)."""
    try:
        import defindex
        if index is None:
            cap = defindex.capture_with(RETIRED_FOUR)          # a donor-free dump knows no donor names
            if cap is None:
                raise IOError("no def dump capture lists a retired donor")
            index = defindex.Index(defindex.load_raw(cap))
        return index.names_of(RETIRED_FOUR)
    except Exception as exc:                                            # noqa: BLE001
        sys.stderr.write("harvest_donor_free: no def index (%s): retired-donor split UNMEASURED\n" % exc)
        return set()


def renames_of(names):
    """The names a donor def was (or would be) ported to: the P6 rewrite's EXPLICIT table + its naming rules."""
    try:
        import save_donor_rewrite as R
        explicit = R.EXPLICIT
    except Exception:                                                   # noqa: BLE001
        explicit = {}
    out = set(explicit.values())
    for n in names:
        out.add("RSW_" + n)
        out.add("RSW_" + re.sub(r"^(sw_|SW_)", "", n))
        if n.startswith(("AA_", "AB_")):
            out.add("RM_" + n[3:])
    return out


def our_texpaths():
    """Every *Path element text in src XML (Defs and Patches): what 'a texture miss on OUR path' means."""
    rx = re.compile(r"<(\w*[Pp]ath(?:Prefix)?)>\s*([^<\s][^<]*?)\s*</\1>")
    out = set()
    for dp, dn, fn in os.walk(SRC):
        dn[:] = [d for d in dn if d not in ("Textures", "art_source", "Staged", "__pycache__", "Sounds", "Assemblies")]
        for f in fn:
            if f.endswith(".xml"):
                try:
                    for m in rx.finditer(open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()):
                        out.add(m.group(2).replace("\\", "/"))
                except OSError:
                    pass
    return out


def our_mod_names():
    import xml.etree.ElementTree as ET
    out = set()
    for tier in os.listdir(SRC):
        td = os.path.join(SRC, tier)
        if not os.path.isdir(td):
            continue
        for mod in os.listdir(td):
            ab = os.path.join(td, mod, "About", "About.xml")
            if os.path.isfile(ab):
                try:
                    n = (ET.parse(ab).getroot().findtext("name") or "").strip()
                except ET.ParseError:
                    n = ""
                if n:
                    out.add(n)
                out.add(mod)
    return out


def _baselines():
    try:
        import harvest_log
        return [(k, label, re.compile(rx), base) for k, label, rx, base, _ in harvest_log.CHECKS], harvest_log.INVENTORY
    except Exception:                                                   # noqa: BLE001
        return [], re.compile(r"^\s*\[(Source|File):")


# ------------------------------------------------------------------ the one pass
def classify(path, donors=None, renames=None, our_tex=None, our_mods=None, ported_tex=None, keep=12):
    """Stream `path` once. Returns a JSON-able summary dict (see main for the fields)."""
    donors = donors or set()
    renames = renames or set()
    our_tex = our_tex or set()
    our_mods = {m for m in (our_mods or ()) if len(m) >= 4}
    ported_tex = set(ported_tex or ())
    checks, inventory = _baselines()
    s = {"log": path, "lines": 0, "ident": False, "capAt": None, "modsBlock": None, "modsSource": None,
         "firstErrorish": None,
         "exc": {"events": 0, "ours": 0, "retired": 0, "other": 0, "first": None, "sigs": collections.Counter()},
         "xref": {"lines": 0, "bar": 0, "retired": 0, "ours": 0, "other": 0, "names": collections.Counter()},
         "scribe": {"lines": 0, "retired": 0, "ours": 0, "other": 0, "names": collections.Counter()},
         "config": {"lines": 0, "ours": 0, "other": 0},
         "patch": {"lines": 0, "ours": 0, "other": 0, "retiredTarget": 0},
         "tex": {"lines": 0, "ours": 0, "other": 0, "ported": 0, "oursPaths": collections.Counter(),
                 "otherPaths": collections.Counter()},
         "baseline": collections.Counter(), "ex": collections.defaultdict(list)}
    cur = None
    block, in_block = None, False
    mod_patch_names = sorted(our_mods, key=len, reverse=True)

    def close_exc(c):
        text = c["line"] + "\n" + "\n".join(c["ctx"])
        who = "retired" if DONOR_CODE_RE.search(text) else "ours" if OURS_CODE_RE.search(text) else "other"
        e = s["exc"]
        e["events"] += 1
        e[who] += 1
        sig = re.sub(r"\d+", "N", c["line"][:140])
        e["sigs"][sig] += 1
        if e["first"] is None:
            e["first"] = {"line": c["no"], "text": c["line"][:220], "who": who}
        if len(s["ex"]["exc"]) < keep:
            s["ex"]["exc"].append("%d [%s] %s" % (c["no"], who, c["line"][:200]))

    def who_name(name, line):
        base = re.sub(r"^(Blueprint_Install_|Blueprint_|Frame_|Corpse_|Meat_)", "", name)
        if name in donors or base in donors or name in renames or base in renames:
            return "retired"
        return "ours" if OURS_RE.search(line) else "other"

    with open(path, encoding="utf-8", errors="replace") as fh:
        for no, raw in enumerate(fh, 1):
            line = raw.rstrip("\r\n")
            s["lines"] = no
            # mod block
            if in_block:
                m = MOD_ROW_RE.match(line)
                if m:
                    block["mods"].append(re.sub(r"\s*\(incompatible version\)$", "", m.group(1)).lower())
                    continue
                in_block = False
            hm = MODS_HEAD_RE.match(line)
            if hm:
                block = {"line": no, "kind": "load" if hm.group(2) else "new", "save": hm.group(2), "mods": []}
                s["modsBlock"] = block
                in_block = True
                continue
            # exception events (frames fold into the open event)
            if cur is not None:
                if FRAME_RE.match(line) and line.strip():
                    if len(cur["ctx"]) < 60:
                        cur["ctx"].append(line)
                    continue
                close_exc(cur)
                cur = None
            if not s["ident"] and any(t in line for t in IDENT):
                s["ident"] = True
            if s["capAt"] is None and CAP in line:
                s["capAt"] = no
            if not line:
                continue
            if s["firstErrorish"] is None and FIRST_ERRORISH.search(line):
                s["firstErrorish"] = {"line": no, "text": line.strip()[:220]}
            if not FRAME_RE.match(line) and EXC_RE.search(line):
                cur = {"no": no, "line": line.strip(), "ctx": []}
            if inventory.match(line):
                continue
            for k, label, rx, base in checks:
                if rx.search(line):
                    s["baseline"][k] += 1
            m = XREF_RE.search(line)
            if m:
                x = s["xref"]
                x["lines"] += 1
                w = who_name(m.group(1), line)
                x[w] += 1
                x["names"][m.group(1)] += 1
                if OURS_RE.search(line):
                    x["bar"] += 1
                    if len(s["ex"]["xref"]) < keep:
                        s["ex"]["xref"].append("%d [%s] %s" % (no, w, line[:200]))
                continue
            m = SCRIBE_RE.search(line)
            if m:
                c = s["scribe"]
                c["lines"] += 1
                c[who_name(m.group(1), line)] += 1
                c["names"][m.group(1)] += 1
                if len(s["ex"]["scribe"]) < keep:
                    s["ex"]["scribe"].append("%d %s" % (no, line[:200]))
                continue
            m = CONFIG_RE.search(line)
            if m:
                c = s["config"]
                c["lines"] += 1
                c["ours" if OURS_RE.search(m.group(1)) else "other"] += 1
                if OURS_RE.search(m.group(1)) and len(s["ex"]["config"]) < keep:
                    s["ex"]["config"].append("%d %s" % (no, line[:200]))
                continue
            if PATCH_RE.search(line):
                c = s["patch"]
                c["lines"] += 1
                ours = bool(OURS_CODE_RE.search(line)) or any(n in line for n in mod_patch_names)
                c["ours" if ours else "other"] += 1
                if donors and any(n in donors for n in re.findall(r'defName="([^"]+)"', line)):
                    c["retiredTarget"] += 1                     # a patch aimed at a retired donor's def: dead weight
                if ours and len(s["ex"]["patch"]) < keep:
                    s["ex"]["patch"].append("%d %s" % (no, line[:200]))
                continue
            for rx in TEX_RES:
                m = rx.search(line)
                if m:
                    t = s["tex"]
                    p = m.group(1).strip("'\"").replace("\\", "/")
                    t["lines"] += 1
                    ours = p in our_tex or bool(OURS_RE.search(p)) or p.startswith("StandIn/")
                    if p in ported_tex or any(q in p for q in ported_tex if q):
                        t["ported"] += 1
                    t["ours" if ours else "other"] += 1
                    t["oursPaths" if ours else "otherPaths"][p] += 1
                    if ours and len(s["ex"]["tex"]) < keep:
                        s["ex"]["tex"].append("%d %s" % (no, line[:200]))
                    break
        if cur is not None:
            close_exc(cur)
    return s


def dump_of_this_run(log_path):
    """At the main menu there is no mod block. If `log_path` is the LIVE Player.log, the newest def-dump capture whose
    manifest was written after Player-prev.log's mtime (Unity rotates the log at launch and keeps that mtime: the
    previous run's last write) was written by THIS run, and its `mods` are what loaded. Else None."""
    try:
        from game_paths import CAPTURES, PLAYER_LOG, PREV_LOG
        if os.path.abspath(log_path) != os.path.abspath(PLAYER_LOG) or not os.path.isfile(PREV_LOG):
            return None
        caps = sorted(c for c in os.listdir(CAPTURES) if os.path.isfile(os.path.join(CAPTURES, c, "manifest.json")))
        if not caps:
            return None
        mp = os.path.join(CAPTURES, caps[-1], "manifest.json")
        if os.path.getmtime(mp) <= os.path.getmtime(PREV_LOG):
            return None
        man = json.load(open(mp, encoding="utf-8-sig"))
        return [m.get("packageId", "").lower() for m in man.get("mods", [])], "def dump %s (written by this run)" % caps[-1]
    except (OSError, ValueError, ImportError):
        return None


def loaded_mods(s, running_mods=None, log_path=None):
    """(list of packageIds or None, source label). Order: reply file, the log's last mod block, this run's dump."""
    if running_mods:
        rm = json.load(open(running_mods, encoding="utf-8-sig"))
        rm = rm.get("result", rm) if isinstance(rm, dict) else rm
        ids = [str(x).lower() for x in (rm.get("packageIds") or rm.get("mods") or []) if isinstance(x, str)] or \
              [str(m.get("packageId", "")).lower() for m in (rm.get("mods") or []) if isinstance(m, dict)]
        return ids, "reply file %s" % os.path.basename(running_mods)
    b = s.get("modsBlock")
    if b and b["mods"]:
        return b["mods"], "log line %d (%s)" % (b["line"], "loaded save " + b["save"] if b["save"] else "new game")
    got = dump_of_this_run(log_path) if log_path else None
    return got if got else (None, None)


def bars(s):
    return {"exceptions": s["exc"]["events"], "xrefOurs": s["xref"]["bar"], "texOurs": s["tex"]["ours"]}


def _plain(s):
    o = json.loads(json.dumps(s, default=lambda x: dict(x) if isinstance(x, collections.Counter) else str(x)))
    for k in ("xref", "scribe"):
        o[k]["names"] = dict(collections.Counter(s[k]["names"]).most_common(200))
    o["exc"]["sigs"] = dict(collections.Counter(s["exc"]["sigs"]).most_common(100))
    return o


def fingerprint(path):
    st = os.stat(path)
    return "%s|%d|%d" % (os.path.basename(path), st.st_size, int(st.st_mtime))


def history_prev(fp, hist_dir=HISTORY):
    best = None
    if os.path.isdir(hist_dir):
        for f in sorted(os.listdir(hist_dir)):
            if f.endswith(".json"):
                try:
                    j = json.load(open(os.path.join(hist_dir, f), encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                if j.get("fingerprint") != fp:
                    best = j
    return best


def history_save(o, hist_dir=HISTORY):
    os.makedirs(hist_dir, exist_ok=True)
    name = hashlib.sha1(o["fingerprint"].encode()).hexdigest()[:12]
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for f in os.listdir(hist_dir):                       # one file per fingerprint: re-runs replace, not pile up
        if f.endswith(name + ".json"):
            os.remove(os.path.join(hist_dir, f))
    json.dump(o, open(os.path.join(hist_dir, "%s_%s.json" % (stamp, name)), "w", encoding="utf-8"))


def _d(now, prev):
    if prev is None:
        return ""
    d = now - prev
    return "  (prev %d, %+d)" % (prev, d) if d else "  (= prev)"


def report(s, mods, src, retired, expect, prev, out=print):
    b = bars(s)
    P = (prev or {})
    pb = P.get("bars", {})
    out("DONOR-FREE HARVEST  %s  %d lines%s" % (s["log"], s["lines"],
                                                "" if s["ident"] else "  [no JawaBench/Bridge-token line: NOT IDENTIFIED]"))
    if s["capAt"]:
        out("  BLIND from line %d: '%s' -- Verse.Log stopped writing; every count below is a FLOOR" % (s["capAt"], CAP))
    if mods is None:
        out("  (a) mods loaded: UNMEASURED -- no 'with mods:' block yet (main menu?) and no def dump from this run; "
            "start/load a game or pass --running-mods <jawa/running_mods reply>")
    else:
        bad = sorted(set(mods) & retired)
        line = "  (a) mods loaded: %d from %s; retired packageIds loaded: %s" % (len(mods), src, bad or "none")
        out(line)
        if expect:
            miss, extra = sorted(set(expect) - set(mods)), sorted(set(mods) - set(expect))
            out("      vs expected list (%d): missing %d %s  extra %d %s" % (len(expect), len(miss), miss[:6],
                                                                         len(extra), extra[:6]))
    e, x, t = s["exc"], s["xref"], s["tex"]
    out("  (b) BARS (§0.5.5 #5)       now   ")
    out("      exception events       %5d%s   ours %d / retired-donor %d / other %d" % (
        e["events"], _d(e["events"], pb.get("exceptions")), e["ours"], e["retired"], e["other"]))
    if e["first"]:
        out("        first: line %d [%s] %s" % (e["first"]["line"], e["first"]["who"], e["first"]["text"][:150]))
    out("      xref naming RM_/RSW_/RUT_ %4d%s   (all xref %d: retired-donor-or-rename %d / ours %d / other %d)" % (
        x["bar"], _d(x["bar"], pb.get("xrefOurs")), x["lines"], x["retired"], x["ours"], x["other"]))
    out("      texture misses, ours   %5d%s   (%d distinct; others %d lines, %d distinct; on ported subjects %d)" % (
        t["ours"], _d(t["ours"], pb.get("texOurs")), len(t["oursPaths"]), t["other"], len(t["otherPaths"]),
        t["ported"]))
    out("      also: config errors %d (ours %d) | patch failures %d (ours %d, aimed at a retired def %d) | Scribe 'Could not load reference' %d "
        "(retired %d, ours %d)" % (s["config"]["lines"], s["config"]["ours"], s["patch"]["lines"], s["patch"]["ours"], s["patch"]["retiredTarget"],
                                   s["scribe"]["lines"], s["scribe"]["retired"], s["scribe"]["ours"]))
    checks, _ = _baselines()
    bl = []
    for k, label, rx, base in checks:
        n = s["baseline"].get(k, 0)
        tag = "RED" if n > base else "better" if n < base else "ok"
        if tag != "ok":
            bl.append("%s %d vs %d %s" % (k, n, base, tag))
    out("  (c) harvest_log baselines: %s" % ("; ".join(bl) if bl else "all %d at baseline" % len(checks)))
    if prev:
        new_sigs = [k for k in s["exc"]["sigs"] if k not in (P.get("exc", {}).get("sigs") or {})]
        new_tex = [k for k in t["oursPaths"] if k not in (P.get("tex", {}).get("oursPaths") or {})]
        out("      vs previous run %s: %d new exception signature(s), %d new texture path(s) of ours" % (
            P.get("fingerprint"), len(new_sigs), len(new_tex)))
        for k in new_sigs[:3]:
            out("        + %s" % k[:150])
    else:
        out("      vs previous run: none recorded")
    for k in ("xref", "tex", "exc"):
        for ln in s["ex"].get(k, [])[:3]:
            out("      e.g. %-4s %s" % (k, ln[:170]))


def verdict(s, mods, retired):
    if mods is not None and set(mods) & retired:
        return 2, "NOT THE DONOR-FREE RUN: %s loaded" % sorted(set(mods) & retired)
    if s["capAt"] or mods is None:
        return 3, "UNMEASURED: %s" % ("log hit the message cap" if s["capAt"] else "loaded mod list unknown")
    b = bars(s)
    failed = [k for k, v in b.items() if v]
    if failed:
        return 1, "FAIL: " + ", ".join("%s %d" % (k, b[k]) for k in failed)
    return 0, "PASS: 0 exception events, 0 xref on RM_/RSW_/RUT_, 0 texture misses on ours (log bars only)"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--log")
    ap.add_argument("--running-mods")
    ap.add_argument("--expect-list", default=EXPECT_LIST)
    ap.add_argument("--against", help="previous summary .json, or another Player.log to classify and diff")
    ap.add_argument("--show", choices=("exc", "xref", "tex", "scribe", "config", "patch"))
    ap.add_argument("--json")
    ap.add_argument("--no-history", action="store_true")
    ap.add_argument("--no-index", action="store_true", help="skip the def index (retired-donor split UNMEASURED)")
    a = ap.parse_args(argv)
    path = a.log
    if not path:
        from game_paths import PLAYER_LOG
        path = PLAYER_LOG
    if not os.path.isfile(path):
        print("log not found: %s" % path)
        return 3
    donors = set() if a.no_index else donor_names()
    ref = dict(donors=donors, renames=renames_of(donors), our_tex=our_texpaths(), our_mods=our_mod_names())
    s = classify(path, keep=10_000 if a.show else 12, **ref)
    if a.show:
        for ln in s["ex"].get(a.show, []):
            print(ln)
        return 0
    retired = retired_packages()
    mods, src = loaded_mods(s, a.running_mods, path)
    expect = None
    if a.expect_list and os.path.isfile(a.expect_list):
        import defindex
        expect = defindex.modlist_packages(a.expect_list)
    prev = None
    if a.against:
        if a.against.endswith(".json"):
            prev = json.load(open(a.against, encoding="utf-8"))
        else:
            ps = classify(a.against, **ref)
            prev = _plain(ps)
            prev["bars"] = bars(ps)
            prev["fingerprint"] = fingerprint(a.against)
    o = _plain(s)
    o["bars"] = bars(s)
    o["fingerprint"] = fingerprint(path)
    o["mods"] = {"count": None if mods is None else len(mods), "source": src,
                 "retiredLoaded": sorted(set(mods or ()) & retired)}
    o["donorNamesKnown"] = len(donors)
    if prev is None and not a.no_history:
        prev = history_prev(o["fingerprint"])
    report(s, mods, src, retired, expect, prev)
    code, why = verdict(s, mods, retired)
    o["verdict"] = {"exit": code, "why": why}
    if not donors:
        print("  NOTE retired-donor split UNMEASURED (no def index); bars are unaffected")
    print("VERDICT exit %d: %s" % (code, why))
    if a.json:
        json.dump(o, open(a.json, "w", encoding="utf-8"), indent=1)
    if not a.no_history:
        history_save(o)
    return code


if __name__ == "__main__":
    sys.exit(main())
